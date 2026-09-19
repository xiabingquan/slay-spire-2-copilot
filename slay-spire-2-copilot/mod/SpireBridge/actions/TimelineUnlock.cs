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

// Timeline unlock pipeline: Neow epoch obtain/reveal plus the earned
// character-epoch grant + native Timeline UI drain that mirrors manual play's
// QueueUnlocks side effects. Parity rule: never grant unearned unlocks.
public static class TimelineUnlock
{
    // Act 1's run-start boon room (Neow / 先古移民 family) only spawns when the
    // profile has revealed NeowEpoch: RunManager.SetStartedWithNeowFlag() copies
    // UnlockState.IsEpochRevealed<NeowEpoch>() into ExtraFields.StartedWithNeow,
    // and GenerateMap() re-types the Act-1 StartingMapPoint to Monster when the
    // flag is false — no boon room, no relic offer (live miss 2026-09-17, user
    // confirmed every act start has a boon). Manual play reveals the epoch by
    // opening the Timeline screen (auto-ObtainEpoch) and clicking the Neow slot
    // (RevealEpoch); automated runs never visit Timeline. Mirror that one-time
    // progression step here, before embark, so run creation snapshots a
    // revealed NeowEpoch. Not a currency/meta purchase — the Neow epoch is the
    // profile's intended first Timeline slot.
    // Parity-first Neow handling: place NEOW_EPOCH at ObtainedNoSlot when
    // missing — the exact state the game itself writes when the Timeline
    // screen first opens (NTimelineScreen auto-Obtain path). The subsequent
    // VisitTimelineAndReveal clicks the slot through native UI so
    // NeowEpoch.QueueUnlocks runs for real (Silent1 grant + expansions).
    internal static void EnsureNeowEpochRevealed()
    {
        try
        {
            SaveManager? saves = SaveManager.Instance;
            if (saves == null)
            {
                BridgeMod.LogInfo("start_run: Neow epoch obtain deferred (SaveManager not ready)");
                return;
            }
            string neowId = EpochModel.GetId<NeowEpoch>();
            if (saves.IsEpochRevealed<NeowEpoch>())
            {
                return;
            }
            SerializableEpoch? e = saves.Progress?.Epochs.FirstOrDefault(x => x.Id == neowId);
            if (e != null && e.State >= EpochState.ObtainedNoSlot)
            {
                return; // already obtained — Timeline visit will reveal it natively
            }
            saves.ObtainEpochOverride(neowId, EpochState.ObtainedNoSlot);
            try
            {
                foreach (EpochModel exp in EpochModel.Get(neowId).GetTimelineExpansion())
                {
                    saves.UnlockSlot(exp.Id);
                }
            }
            catch { /* expansion best-effort */ }
            saves.SaveProgressFile();
            BridgeMod.LogInfo($"start_run: Neow {neowId} -> ObtainedNoSlot (Timeline visit will reveal)");
        }
        catch (Exception e)
        {
            BridgeMod.LogErr($"start_run: Neow epoch obtain failed: {e.Message}");
        }
    }

    // Boon-room guarantee: hard-reveal Neow ONLY as a fallback after the
    // native Timeline flow, when it still is not Revealed (UI drift / unexpected
    // slot state). Preserves the run-3 lesson — act-start boon rooms must never
    // silently vanish — without skipping QueueUnlocks on the happy path.
    internal static void FallbackRevealNeowForBoonRoom()
    {
        try
        {
            SaveManager? saves = SaveManager.Instance;
            if (saves == null || saves.IsEpochRevealed<NeowEpoch>())
            {
                return;
            }
            string neowId = EpochModel.GetId<NeowEpoch>();
            saves.ObtainEpochOverride(neowId, EpochState.Revealed);
            saves.SaveProgressFile();
            BridgeMod.LogInfo($"start_run: FALLBACK hard-revealed {neowId} — boon room will spawn; Timeline flow did not complete natively");
        }
        catch (Exception e)
        {
            BridgeMod.LogErr($"start_run: Neow fallback reveal failed: {e.Message}");
        }
    }

    // timeline_sync: run the Timeline reveal drain from the main menu WITHOUT
    // starting a run — verification hook for the unlock pipeline.
    internal static (bool, string) TimelineSync()
    {
        ActionExecutor.Fire(async () =>
        {
            Node root = ((SceneTree)Engine.GetMainLoop()).Root;
            Control mainMenu = await WaitHelper.ForNode<Control>(root, "/root/Game/RootSceneContainer/MainMenu", default, TimeSpan.FromSeconds(30));
            await VisitTimelineAndReveal(mainMenu);
        }, "timeline sync");
        return (true, "submitted timeline_sync");
    }

    /// <summary>
    /// Mirrors the normal play loop's Timeline visits: place every EARNED
    /// character-epoch into ObtainedNoSlot (the exact state the game's own
    /// QueueUnlocks writes), then walk the Timeline UI clicking Obtained slots
    /// so reveal/unlock side effects fire through the game's native flow.
    /// Pure UI simulation alone is not enough for already-broken saves where an
    /// epoch was force-marked Revealed without running QueueUnlocks — that is
    /// why the repair step exists. Idempotent; safe to call every start_run.
    /// </summary>
    internal static async Task VisitTimelineAndReveal(Control mainMenu)
    {
        try
        {
            GrantEarnedCharacterEpochs();
            NButton? timelineBtn = mainMenu.GetNodeOrNull<NButton>("MainMenuTextButtons/TimelineButton");
            if (timelineBtn is not { Visible: true })
            {
                BridgeMod.LogErr("timeline: MainMenuTextButtons/TimelineButton not found/visible");
                return;
            }
            await UiHelper.Click(timelineBtn);
            Node? timeline = null;
            await WaitHelper.Until(() =>
            {
                timeline = UiHelper.FindFirst<NTimelineScreen>(mainMenu)
                    ?? (ActiveScreenContext.Instance.GetCurrentScreen() as NTimelineScreen);
                return timeline != null;
            }, default, TimeSpan.FromSeconds(10), "timeline screen visible");
            if (timeline == null)
            {
                BridgeMod.LogErr("timeline: screen did not open");
                return;
            }
            for (int round = 0; round < 24; round++)
            {
                List<NEpochSlot> slots = UiHelper.FindAll<NEpochSlot>(timeline);
                NEpochSlot? target = null;
                foreach (NEpochSlot s in slots)
                {
                    try
                    {
                        if (s.State == EpochSlotState.Obtained && s.Visible && s.IsEnabled)
                        {
                            target = s;
                            break;
                        }
                    }
                    catch { /* disposed slot */ }
                }
                if (target == null)
                {
                    BridgeMod.LogInfo($"timeline: drain complete (round {round}, slots={slots.Count}, none Obtained)");
                    break;
                }
                string epochId = "";
                try { epochId = target.model?.Id ?? "?"; } catch { }
                BridgeMod.LogInfo($"timeline: revealing {epochId} (round {round})");
                await UiHelper.Click(target);
                await Task.Delay(1500, default); // unlock-animation budget
                // Click through inspect/unlock screens until Timeline slots are
                // the topmost interactive layer again.
                for (int inner = 0; inner < 6; inner++)
                {
                    Node ctx = ActiveScreenContext.Instance.GetCurrentScreen() as Node ?? timeline;
                    if (ctx == timeline)
                    {
                        List<NEpochSlot> now = UiHelper.FindAll<NEpochSlot>(timeline);
                        bool inspectOpen = UiHelper.FindFirst<NEpochInspectScreen>(timeline) is { } ins
                            && ins.Visible;
                        if (!inspectOpen && now.Count > 0)
                        {
                            break;
                        }
                    }
                    NButton? click = null;
                    List<NButton> btns = UiHelper.FindAll<NButton>(ctx);
                    foreach (NButton b in btns)
                    {
                        if (!b.Visible) continue;
                        string n = b.Name.ToString();
                        if (n.Contains("Close", StringComparison.OrdinalIgnoreCase)
                            || n.Contains("Confirm", StringComparison.OrdinalIgnoreCase)
                            || n.Contains("Continue", StringComparison.OrdinalIgnoreCase))
                        {
                            click = b;
                            break;
                        }
                    }
                    click ??= btns.FirstOrDefault(b => b.Visible && b.IsEnabled);
                    if (click == null) break;
                    await UiHelper.Click(click);
                    await Task.Delay(800, default);
                }
            }
            // Back to main menu.
            NButton? back = UiHelper.FindAll<NButton>(timeline)
                .FirstOrDefault(b => b.Visible && b.Name.ToString().Contains("Back", StringComparison.OrdinalIgnoreCase));
            if (back != null)
            {
                await UiHelper.Click(back);
                await Task.Delay(600, default);
            }
            BridgeMod.LogInfo("timeline: visit finished");
        }
        catch (Exception e)
        {
            BridgeMod.LogErr($"timeline visit failed: {e}");
        }
    }

    /// <summary>
    /// Repair/chain step: place earned character epochs into ObtainedNoSlot so
    /// the Timeline drain can reveal them through native UI.
    /// Earn rules mirror decomp design intent: Silent1 — any completed run
    /// (also granted as NeowEpoch.QueueUnlocks side effect); Regent1 — a
    /// completed run as Silent; Necrobinder1 — as Regent; Defect1 — as
    /// Necrobinder (CharacterModel.UnlocksAfterRunAs chain).
    /// </summary>
    private static void GrantEarnedCharacterEpochs()
    {
        try
        {
            SaveManager saves = SaveManager.Instance;
            if (saves?.Progress == null) return;
            ProgressState p = saves.Progress;
            bool AnyRun()
            {
                try
                {
                    return p.FloorsClimbed > 0
                        || p.CharacterStats.Values.Any(c => c != null && (c.TotalWins + c.TotalLosses) > 0);
                }
                catch { return false; }
            }
            bool RunsAs(string entry)
            {
                try
                {
                    return p.CharacterStats.Any(kv =>
                    {
                        if (kv.Value == null) return false;
                        if ((kv.Value.TotalWins + kv.Value.TotalLosses) <= 0) return false;
                        string key = kv.Key.ToString() ?? "";
                        string id = kv.Value.Id?.ToString() ?? "";
                        string ent = "";
                        try { ent = kv.Value.Id?.Entry ?? ""; } catch { }
                        return key.Contains(entry, StringComparison.OrdinalIgnoreCase)
                            || id.Contains(entry, StringComparison.OrdinalIgnoreCase)
                            || ent.Contains(entry, StringComparison.OrdinalIgnoreCase);
                    });
                }
                catch { return false; }
            }
            void GrantIfEarned(string epochId, bool earned)
            {
                if (!earned || string.IsNullOrEmpty(epochId)) return;
                SerializableEpoch? e = p.Epochs.FirstOrDefault(x => x.Id == epochId);
                if (e != null && e.State >= EpochState.Obtained) return; // Obtained/Revealed: nothing to do
                if (e != null && e.State == EpochState.Revealed) return;
                saves.ObtainEpochOverride(epochId, EpochState.ObtainedNoSlot);
                try
                {
                    // UnlockSlot on the epoch itself promotes ObtainedNoSlot ->
                    // Obtained (ProgressState.UnlockSlot) — the state the Timeline
                    // UI renders as a clickable slot; without this the slot does
                    // not exist visually and the drain finds nothing to click.
                    saves.UnlockSlot(epochId);
                    foreach (EpochModel exp in EpochModel.Get(epochId).GetTimelineExpansion())
                    {
                        saves.UnlockSlot(exp.Id);
                    }
                }
                catch { /* expansion best-effort */ }
                saves.SaveProgressFile();
                BridgeMod.LogInfo($"timeline repair: {epochId} -> ObtainedNoSlot+slot (earned; awaiting Timeline reveal)");
            }
            GrantIfEarned(EpochModel.GetId<Silent1Epoch>(), AnyRun());
            GrantIfEarned(EpochModel.GetId<Regent1Epoch>(), RunsAs("SILENT"));
            GrantIfEarned(EpochModel.GetId<Necrobinder1Epoch>(), RunsAs("REGENT"));
            GrantIfEarned(EpochModel.GetId<Defect1Epoch>(), RunsAs("NECROBINDER"));
        }
        catch (Exception e)
        {
            BridgeMod.LogErr($"character epoch grant failed: {e}");
        }
    }
}
