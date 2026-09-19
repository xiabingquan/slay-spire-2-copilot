using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Text.Json;
using System.Threading.Tasks;
using Godot;
using MegaCrit.Sts2.Core.AutoSlay.Helpers;
using MegaCrit.Sts2.Core.Combat;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Context;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Merchant;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Entities.RestSite;
using MegaCrit.Sts2.Core.GameActions;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Map;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Powers;
using MegaCrit.Sts2.Core.Nodes;
using MegaCrit.Sts2.Core.Nodes.Cards.Holders;
using MegaCrit.Sts2.Core.Nodes.Combat;
using MegaCrit.Sts2.Core.Nodes.CommonUi;
using MegaCrit.Sts2.Core.Nodes.Events;
using MegaCrit.Sts2.Core.Nodes.Events.Custom.CrystalSphere;
using MegaCrit.Sts2.Core.Nodes.GodotExtensions;
using MegaCrit.Sts2.Core.Nodes.Relics;
using MegaCrit.Sts2.Core.Nodes.RestSite;
using MegaCrit.Sts2.Core.Nodes.Rewards;
using MegaCrit.Sts2.Core.Nodes.Rooms;
using MegaCrit.Sts2.Core.Nodes.Screens;
using MegaCrit.Sts2.Core.Nodes.Screens.CardSelection;
using MegaCrit.Sts2.Core.Nodes.Screens.CharacterSelect;
using MegaCrit.Sts2.Core.Nodes.Screens.GameOverScreen;
using MegaCrit.Sts2.Core.Nodes.Screens.MainMenu;
using MegaCrit.Sts2.Core.Nodes.Screens.Map;
using MegaCrit.Sts2.Core.Nodes.Screens.Overlays;
using MegaCrit.Sts2.Core.Nodes.Screens.ScreenContext;
using MegaCrit.Sts2.Core.Nodes.Screens.Shops;
using MegaCrit.Sts2.Core.Nodes.Screens.Timeline;
using MegaCrit.Sts2.Core.Nodes.Screens.TreasureRoomRelic;
using MegaCrit.Sts2.Core.Runs;
using MegaCrit.Sts2.Core.Saves;
using MegaCrit.Sts2.Core.Timeline;
using MegaCrit.Sts2.Core.Timeline.Epochs;


namespace SpireCopilot.Bridge;

// Run-lifecycle action executors: start_run (menu automation + ascension
// parity), continue_run, abandon_run, and the game-over teardown chain.
public static class RunLifecycle
{
    // start_run args: character (optional substring match), seed (optional),
    // ascension (optional int >= 0). Ascension is fail-loud: when the key is
    // present it must be a valid level the profile already unlocked for that
    // character (CharacterStats.MaxAscension, earned by wins) — otherwise
    // ok=false before any UI work. Omitting the key keeps profile-preferred.
    internal static (bool, string) StartRun(JsonElement args)
    {
        string? character = ActionExecutor.GetString(args, "character");
        string? seed = ActionExecutor.GetString(args, "seed");
        int? ascension = null;
        if (args.TryGetProperty("ascension", out _))
        {
            if (string.IsNullOrEmpty(character))
            {
                return (false, "start_run: ascension requires an explicit character arg (fail-loud)");
            }
            if (!ActionExecutor.TryGetInt(args, "ascension", out int want) || want < 0)
            {
                return (false, "start_run: invalid ascension value (need integer >= 0); fail-loud, not silently ignored");
            }
            try
            {
                ProgressState? progress = SaveManager.Instance?.Progress;
                if (progress == null)
                {
                    return (false, "start_run: progress save not loaded; cannot validate ascension (fail-loud)");
                }
                CharacterStats? stats = FindCharacterStats(progress, character);
                if (stats == null)
                {
                    return (false, $"start_run: no character_stats entry matching '{character}'; cannot validate ascension (fail-loud)");
                }
                if (want > stats.MaxAscension)
                {
                    return (false, $"start_run: ascension {want} exceeds unlocked max_ascension={stats.MaxAscension} for {stats.Id} (fail-loud; levels unlock via wins)");
                }
                ascension = want;
            }
            catch (Exception e)
            {
                return (false, $"start_run: ascension validation failed: {e.Message} (fail-loud)");
            }
        }
        ActionExecutor.Fire(() => StartRunSequence(character, seed, ascension), "start run");
        return (true, $"submitted start_run (character={character ?? "random"}, seed={seed ?? "random"}, ascension={(ascension?.ToString() ?? "profile-preferred")})");
    }

    // Match profile CharacterStats by ModelId entry/id substring — same
    // matching rule as the character-select button lookup.
    private static CharacterStats? FindCharacterStats(ProgressState progress, string character)
    {
        return progress.CharacterStats.Values.FirstOrDefault(s =>
            s != null && (
                (s.Id?.Entry?.Contains(character, StringComparison.OrdinalIgnoreCase) ?? false)
                || (s.Id?.ToString()?.Contains(character, StringComparison.OrdinalIgnoreCase) ?? false)));
    }

    // Mirrors the game's own AutoSlay menu path (AutoSlayer.PlayMainMenuAsync).
    // Takeover-safe: clears game-over screens first so start_run works from any
    // game state (startup, mid-run, or ended).
    private static async Task StartRunSequence(string? character, string? seed, int? ascension)
    {
        Node root = ((SceneTree)Engine.GetMainLoop()).Root;
        if (ActiveScreenContext.Instance.GetCurrentScreen() is NGameOverScreen ended)
        {
            BridgeMod.LogInfo("start_run: clearing game-over screen first");
            await ClearGameOverScreen(ended);
            await WaitHelper.Until(
                () => NGame.Instance?.MainMenu is { } m && m.IsVisibleInTree(),
                default, TimeSpan.FromSeconds(20), "main menu after game over");
        }
        if (!string.IsNullOrEmpty(seed))
        {
            if (NGame.Instance != null)
            {
                NGame.Instance.DebugSeedOverride = seed;
            }
        }
        try
        {
            SpeedHooks.Apply("start_run");
        }
        catch (Exception e)
        {
            BridgeMod.LogErr($"prefs tweak failed: {e}");
        }
        TimelineUnlock.EnsureNeowEpochRevealed();
        Control mainMenu = await WaitHelper.ForNode<Control>(root, "/root/Game/RootSceneContainer/MainMenu", default, TimeSpan.FromSeconds(30));
        // Simulate the normal play loop's Timeline visits: earned-but-unrevealed
        // Epochs are revealed through the game's own inspect/unlock UI so
        // QueueUnlocks side effects (character unlocks, timeline expansions,
        // pending unlock flags) fire exactly as they do for manual play.
        await TimelineUnlock.VisitTimelineAndReveal(mainMenu);
        // Boon-room guarantee fallback: if Neow still is not Revealed after the
        // native Timeline flow (UI drift, unexpected slot state), force it the
        // old way so Act-start boon rooms never silently vanish.
        TimelineUnlock.FallbackRevealNeowForBoonRoom();
        NButton? abandon = mainMenu.GetNodeOrNull<NButton>("MainMenuTextButtons/AbandonRunButton");
        if (abandon is { Visible: true })
        {
            await UiHelper.Click(abandon);
            await WaitHelper.Until(() => NModalContainer.Instance?.OpenModal != null, default, TimeSpan.FromSeconds(5), "abandon modal");
            if (NModalContainer.Instance?.OpenModal is Node modal)
            {
                NButton? yes = modal.GetNodeOrNull<NButton>("VerticalPopup/YesButton");
                if (yes != null)
                {
                    await UiHelper.Click(yes);
                }
                await WaitHelper.Until(() => NModalContainer.Instance.OpenModal == null, default, TimeSpan.FromSeconds(5), "abandon modal close");
            }
        }
        NButton? singleplayer = mainMenu.GetNodeOrNull<NButton>("MainMenuTextButtons/SingleplayerButton");
        if (singleplayer != null)
        {
            await UiHelper.Click(singleplayer);
        }
        Control? charSelect = null;
        await WaitHelper.Until(() =>
        {
            charSelect = mainMenu.GetNodeOrNull<Control>("Submenus/CharacterSelectScreen");
            NButton? standard = mainMenu.GetNodeOrNull<NButton>("Submenus/SingleplayerSubmenu/StandardButton");
            if (charSelect?.Visible == true)
            {
                return true;
            }
            return standard is { Visible: true };
        }, default, TimeSpan.FromSeconds(10), "character select visible");
        if (mainMenu.GetNodeOrNull<Control>("Submenus/CharacterSelectScreen") is not { Visible: true } visibleSelect)
        {
            NButton? standard = mainMenu.GetNodeOrNull<NButton>("Submenus/SingleplayerSubmenu/StandardButton");
            if (standard != null)
            {
                await UiHelper.Click(standard);
                await WaitHelper.Until(() => mainMenu.GetNodeOrNull<Control>("Submenus/CharacterSelectScreen")?.Visible == true,
                    default, TimeSpan.FromSeconds(10), "character select after standard");
            }
        }
        Control selectScreen = mainMenu.GetNode<Control>("Submenus/CharacterSelectScreen");
        Node buttonContainer = selectScreen.GetNode("CharSelectButtons/ButtonContainer");
        List<NCharacterSelectButton> characterButtons = UiHelper.FindAll<NCharacterSelectButton>(buttonContainer);
        // Refresh lock state from save progress (same as the game's AutoSlay
        // path) — UnlockIfPossible only unlocks characters the save already
        // earned; it never grants unearned unlocks.
        foreach (NCharacterSelectButton b in characterButtons)
        {
            try { b.UnlockIfPossible(); } catch { /* refresh best-effort */ }
        }
        foreach (NCharacterSelectButton b in characterButtons)
        {
            string entry = "";
            try { entry = b.Character?.Id.Entry ?? ""; } catch { }
            BridgeMod.LogInfo($"start_run: roster name={b.Name} locked={b.IsLocked} char_entry={entry}");
        }
        NCharacterSelectButton? chosen = null;
        if (!string.IsNullOrEmpty(character))
        {
            // Match Character.Id.Entry first (stable id), then button Name.
            chosen = characterButtons.FirstOrDefault(b =>
                !b.IsLocked && SafeCharEntry(b).Contains(character, StringComparison.OrdinalIgnoreCase));
            chosen ??= characterButtons.FirstOrDefault(b =>
                !b.IsLocked && b.Name.ToString().Contains(character, StringComparison.OrdinalIgnoreCase));
        }
        chosen ??= characterButtons.FirstOrDefault(b => !b.IsLocked);
        if (chosen == null)
        {
            BridgeMod.LogErr("start_run: no unlocked character button found");
            return;
        }
        // Profile PreferredAscension must be written BEFORE Select(): the game's
        // own character-select handler reads it when the character changes.
        if (ascension is int wantPre)
        {
            WriteProfilePreferredAscension(SafeCharEntry(chosen), wantPre);
        }
        chosen.Select();
        await Task.Delay(200, default);
        if (ascension is int wantAsc)
        {
            ApplyAscensionOnSelectScreen(selectScreen, chosen, wantAsc);
        }
        NButton confirm = await WaitHelper.ForNode<NButton>(selectScreen, "ConfirmButton", default, TimeSpan.FromSeconds(10));
        await UiHelper.Click(confirm);
        BridgeMod.LogInfo($"start_run: embarked as {chosen.Name} char_entry={SafeCharEntry(chosen)} (seed={seed ?? "random"}, ascension={ascension?.ToString() ?? "profile-preferred"})");
    }

    // Ascension parity: only levels the profile already unlocked for this
    // character (CharacterStats.MaxAscension — written by the game's own win
    // handling) are ever applied; nothing unearned is granted. Preferred level
    // is written to the profile first (before Select, so the game's own
    // character-change path can read it), then applied through the public UI
    // setters on NAscensionPanel and StartRunLobby.SyncAscensionChange, with a
    // reflection fallback to the game's private singleplayer path. RunState.
    // AscensionLevel in state is the authority for post-embark verification.
    private static int WriteProfilePreferredAscension(string charEntry, int want)
    {
        int max = -1;
        try
        {
            ProgressState? progress = SaveManager.Instance?.Progress;
            CharacterStats? stats = progress == null ? null : FindCharacterStats(progress, charEntry);
            if (stats != null)
            {
                max = stats.MaxAscension;
                stats.PreferredAscension = want;
                SaveManager.Instance!.SaveProgressFile();
                BridgeMod.LogInfo($"start_run: profile PreferredAscension={want} for {stats.Id} (max={max})");
            }
            else
            {
                BridgeMod.LogErr($"start_run: no character_stats for '{charEntry}' when writing preferred ascension");
            }
        }
        catch (Exception e)
        {
            BridgeMod.LogErr($"start_run: profile preferred-ascension write failed: {e.Message}");
        }
        return max;
    }

    private static void ApplyAscensionOnSelectScreen(Control selectScreen, NCharacterSelectButton chosen, int want)
    {
        string charEntry = SafeCharEntry(chosen);
        int max = WriteProfilePreferredAscension(charEntry, want);
        try
        {
            NAscensionPanel? panel = UiHelper.FindAll<NAscensionPanel>(selectScreen).FirstOrDefault();
            if (panel != null)
            {
                if (max >= 0)
                {
                    panel.SetMaxAscension(max);
                }
                panel.SetAscensionLevel(want);
                BridgeMod.LogInfo($"start_run: NAscensionPanel.SetAscensionLevel({want}) -> panel.Ascension={panel.Ascension} (max={max})");
            }
            else
            {
                BridgeMod.LogErr("start_run: NAscensionPanel not found on character select — using lobby path only");
            }
        }
        catch (Exception e)
        {
            BridgeMod.LogErr($"start_run: NAscensionPanel apply failed: {e.Message}");
        }
        try
        {
            if (selectScreen is NCharacterSelectScreen ncss && ncss.Lobby is { } lobby)
            {
                lobby.SyncAscensionChange(want); // public API
                if (lobby.Ascension != want)
                {
                    // Game's own singleplayer path: reads profile PreferredAscension.
                    MethodInfo? setAfter = lobby.GetType().GetMethod(
                        "SetSingleplayerAscensionAfterCharacterChanged",
                        BindingFlags.Instance | BindingFlags.NonPublic);
                    if (setAfter != null && chosen.Character?.Id is { } cid)
                    {
                        setAfter.Invoke(lobby, new object[] { cid });
                    }
                }
                if (lobby.Ascension != want)
                {
                    PropertyInfo? prop = lobby.GetType().GetProperty("Ascension");
                    prop?.SetMethod?.Invoke(lobby, new object[] { want });
                }
                BridgeMod.LogInfo($"start_run: lobby ascension readback={lobby.Ascension} (wanted={want}, lobby.MaxAscension={lobby.MaxAscension})");
                if (lobby.Ascension != want)
                {
                    BridgeMod.LogErr($"start_run: FAILED to set lobby ascension to {want}; run may embark at {lobby.Ascension}");
                }
            }
            else
            {
                BridgeMod.LogErr("start_run: StartRunLobby not reachable on character select");
            }
        }
        catch (Exception e)
        {
            BridgeMod.LogErr($"start_run: lobby ascension apply failed: {e.Message}");
        }
    }

    private static string SafeCharEntry(NCharacterSelectButton b)
    {
        try { return b.Character?.Id.Entry ?? ""; }
        catch { return ""; }
    }

    internal static (bool, string) ContinueRun()
    {
        if (NGame.Instance?.MainMenu is not { } mainMenu || !mainMenu.IsVisibleInTree())
        {
            return (false, "not at main menu");
        }
        List<NButton> buttons = UiHelper.FindAll<NButton>(mainMenu);
        NButton? continueBtn = buttons.FirstOrDefault(b =>
            b.Visible && b.Name.ToString().Contains("Continue", StringComparison.OrdinalIgnoreCase));
        if (continueBtn == null)
        {
            return (false, "no continue-run button found on main menu");
        }
        NButton target = continueBtn;
        ActionExecutor.Fire(() => UiHelper.Click(target), "continue run");
        return (true, "submitted continue_run");
    }

    internal static (bool, string) AbandonRun()
    {
        ActionExecutor.Fire(AbandonRunSequence, "abandon run");
        return (true, "submitted abandon_run");
    }

    private static async Task AbandonRunSequence()
    {
        Node root = ((SceneTree)Engine.GetMainLoop()).Root;
        NButton options = await WaitHelper.ForNode<NButton>(root, "/root/Game/RootSceneContainer/Run/GlobalUi/TopBar/RightAlignedStuff/Options", default, TimeSpan.FromSeconds(10));
        await UiHelper.Click(options);
        NButton abandon = await WaitHelper.ForNode<NButton>(root, "/root/Game/RootSceneContainer/Run/GlobalUi/CapstoneScreenContainer/OptionsScreen/AbandonRunButton", default, TimeSpan.FromSeconds(10));
        await UiHelper.Click(abandon);
        NButton confirm = await WaitHelper.ForNode<NButton>(root, "/root/Game/RootSceneContainer/Run/GlobalUi/OverlayScreensContainer/GameOverScreen/UI/ProceedButton", default, TimeSpan.FromSeconds(15));
        await UiHelper.Click(confirm);
        BridgeMod.LogInfo("abandon_run complete");
    }

    // Drives NGameOverScreen back to the main menu using the game's own
    // summary flow: Continue button, then Return-To-Main-Menu button. Both are
    // polled until enabled — takeover must work from any game state.
    // Game-over summary: Continue button, then Return-To-Main-Menu. Nodes can
    // be disposed mid-poll while another path (start_run's own game-over clear)
    // tears the screen down — every node touch is IsInstanceValid-guarded and
    // re-found per step; a disposed Continue means "teardown in progress, skip"
    // (live crash 2026-09-17 run-7: Cannot access a disposed object
    // NGameOverContinueButton — proceed chain threw, state looked frozen).
    internal static async Task ClearGameOverScreen(NGameOverScreen screen)
    {
        for (int i = 0; i < 24; i++)
        {
            if (!GodotObject.IsInstanceValid(screen))
            {
                BridgeMod.LogInfo("game_over chain: screen disposed during teardown — nothing to clear");
                return;
            }
            NGameOverContinueButton? cont = UiHelper.FindFirst<NGameOverContinueButton>(screen);
            if (cont == null)
            {
                break; // continue button gone — screen already advancing
            }
            if (!GodotObject.IsInstanceValid(cont))
            {
                await Task.Delay(250, default);
                continue;
            }
            if (cont.IsEnabled)
            {
                BridgeMod.LogInfo("game_over chain: continue enabled=True");
                if (GodotObject.IsInstanceValid(cont))
                {
                    await UiHelper.Click(cont);
                }
                break;
            }
            await Task.Delay(500, default);
        }
        NReturnToMainMenuButton? menuBtn = null;
        for (int i = 0; i < 24; i++)
        {
            if (!GodotObject.IsInstanceValid(screen))
            {
                BridgeMod.LogInfo("game_over chain: screen disposed before return-to-menu — ok");
                return;
            }
            menuBtn = UiHelper.FindFirst<NReturnToMainMenuButton>(screen);
            if (menuBtn != null && GodotObject.IsInstanceValid(menuBtn) && menuBtn.Visible && menuBtn.IsEnabled)
            {
                break;
            }
            menuBtn = null;
            await Task.Delay(500, default);
        }
        if (menuBtn != null && GodotObject.IsInstanceValid(menuBtn))
        {
            BridgeMod.LogInfo("game_over chain: clicking return to main menu");
            await UiHelper.Click(menuBtn);
        }
        else
        {
            BridgeMod.LogInfo("game_over chain: return-to-menu button never appeared (likely already cleared)");
        }
    }
}
