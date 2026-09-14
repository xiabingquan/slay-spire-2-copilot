using System;
using System.Collections.Generic;
using System.Linq;
using System.Text.Json;
using System.Threading.Tasks;
using Godot;
using MegaCrit.Sts2.Core.AutoSlay.Helpers;
using MegaCrit.Sts2.Core.Combat;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Context;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Map;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Nodes;
using MegaCrit.Sts2.Core.Nodes.Cards.Holders;
using MegaCrit.Sts2.Core.Nodes.CommonUi;
using MegaCrit.Sts2.Core.Nodes.Events;
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
using MegaCrit.Sts2.Core.Nodes.Screens.TreasureRoomRelic;
using MegaCrit.Sts2.Core.Runs;
using MegaCrit.Sts2.Core.Saves;
using MegaCrit.Sts2.Core.Settings;

namespace MimoSpire.Bridge;

// Dispatches protocol actions on the game main thread. Long-running game
// sequences (card play animations, menu automation) are started fire-and-
// forget; completion is observed by the client polling state fingerprints.
public static class ActionExecutor
{
    public static (bool Ok, string Message, Dictionary<string, object?>? State) Execute(string action, JsonElement args)
    {
        try
        {
            (bool ok, string message) = action switch
            {
                "play" => Play(args),
                "end_turn" => EndTurn(),
                "use_potion" => UsePotion(args),
                "map_select" => MapSelect(args),
                "choose" => Choose(args),
                "skip" => Skip(),
                "treasure_open" => TreasureOpen(),
                "proceed" => Proceed(),
                "rest" => RestSiteOption(preferSmith: false),
                "smith" => RestSiteOption(preferSmith: true),
                "shop_buy" => ShopBuy(args),
                "shop_leave" => ShopLeave(),
                "start_run" => StartRun(args),
                "abandon_run" => AbandonRun(),
                _ => (false, $"unknown action '{action}'"),
            };
            return (ok, message, StateBuilder.Build());
        }
        catch (Exception e)
        {
            BridgeMod.LogErr($"action '{action}' failed: {e}");
            return (false, e.Message, SafeState());
        }
    }

    private static Dictionary<string, object?>? SafeState()
    {
        try
        {
            return StateBuilder.Build();
        }
        catch (Exception)
        {
            return null;
        }
    }

    private static (bool, string) Play(JsonElement args)
    {
        if (!TryGetInt(args, "card_index", out int cardIndex))
        {
            return (false, "play requires card_index");
        }
        if (!TryGetCombatPlayer(out Player? player, out CombatState combat, out PlayerCombatState? pcs) || pcs == null)
        {
            return (false, "not in an active combat play phase");
        }
        if (pcs.Phase != PlayerTurnPhase.Play)
        {
            return (false, $"not player play phase (phase={pcs.Phase})");
        }
        IReadOnlyList<CardModel> hand = pcs.Hand.Cards;
        if (cardIndex < 0 || cardIndex >= hand.Count)
        {
            return (false, $"card_index {cardIndex} out of range (hand size {hand.Count})");
        }
        CardModel card = hand[cardIndex];
        Creature? target = null;
        if (TryGetInt(args, "target_combat_id", out int targetId))
        {
            target = combat.GetCreature((uint)targetId);
            if (target == null)
            {
                return (false, $"target combat_id {targetId} not found");
            }
        }
        else if (card.TargetType == TargetType.AnyEnemy)
        {
            var hittable = combat.HittableEnemies.ToList();
            if (hittable.Count == 0)
            {
                return (false, "card requires a target but no hittable enemies");
            }
            target = hittable[0];
        }
        CardModel cardRef = card;
        Creature? targetRef = target;
        Fire(async () => await CardCmd.AutoPlay(new BlockingPlayerChoiceContext(), cardRef, targetRef), "play card");
        return (true, $"submitted play {card.Id.Entry} -> {(target?.Name ?? "none")}");
    }

    private static (bool, string) EndTurn()
    {
        if (!TryGetCombatPlayer(out Player? player, out _, out PlayerCombatState? pcs) || pcs == null)
        {
            return (false, "not in an active combat");
        }
        if (pcs.Phase != PlayerTurnPhase.Play)
        {
            return (false, $"not player play phase (phase={pcs.Phase})");
        }
        Player playerRef = player!;
        Fire(() => { PlayerCmd.EndTurn(playerRef, canBackOut: false); return Task.CompletedTask; }, "end turn");
        return (true, "submitted end_turn");
    }

    private static (bool, string) UsePotion(JsonElement args)
    {
        if (!TryGetInt(args, "potion_index", out int potionIndex))
        {
            return (false, "use_potion requires potion_index");
        }
        if (!TryGetCombatPlayer(out Player? player, out CombatState combat, out _))
        {
            return (false, "not in an active combat");
        }
        Player playerRef = player!;
        if (potionIndex < 0 || potionIndex >= playerRef.PotionSlots.Count || playerRef.PotionSlots[potionIndex] == null)
        {
            return (false, $"potion_index {potionIndex} is empty or out of range");
        }
        PotionModel potion = playerRef.PotionSlots[potionIndex]!;
        Creature? target = null;
        if (TryGetInt(args, "target_combat_id", out int targetId))
        {
            target = combat.GetCreature((uint)targetId);
            if (target == null)
            {
                return (false, $"target combat_id {targetId} not found");
            }
        }
        else if (potion.TargetType == TargetType.AnyEnemy)
        {
            var hittable = combat.HittableEnemies.ToList();
            target = hittable.Count > 0 ? hittable[0] : null;
        }
        Creature? targetRef = target;
        Fire(() => { potion.EnqueueManualUse(targetRef); return Task.CompletedTask; }, "use potion");
        return (true, $"submitted use_potion {potion.Id.Entry}");
    }

    private static (bool, string) MapSelect(JsonElement args)
    {
        if (!TryGetInt(args, "row", out int row) || !TryGetInt(args, "col", out int col))
        {
            return (false, "map_select requires row and col");
        }
        RunState? runState = RunManager.Instance.DebugOnlyGetState();
        if (runState == null)
        {
            return (false, "no active run");
        }
        if (NMapScreen.Instance is not { } mapScreen || !mapScreen.IsOpen)
        {
            return (false, "map screen is not open");
        }
        List<NMapPoint> points = UiHelper.FindAll<NMapPoint>(mapScreen);
        NMapPoint? targetPoint = points.FirstOrDefault(p => p.Point.coord.row == row && p.Point.coord.col == col);
        if (targetPoint == null)
        {
            return (false, $"no map point node at ({row},{col})");
        }
        if (!targetPoint.IsEnabled)
        {
            return (false, $"map point ({row},{col}) is not selectable yet");
        }
        NClickableControl clickTarget = targetPoint;
        Fire(() => UiHelper.Click(clickTarget), "map select");
        return (true, $"submitted map_select ({row},{col})");
    }

    private static (bool, string) Choose(JsonElement args)
    {
        if (!TryGetInt(args, "index", out int index))
        {
            return (false, "choose requires index");
        }
        IScreenContext? context = ActiveScreenContext.Instance.GetCurrentScreen();
        switch (context)
        {
            case NCardRewardSelectionScreen cardReward:
            {
                List<NCardHolder> holders = UiHelper.FindAll<NCardHolder>(cardReward);
                if (index < 0 || index >= holders.Count)
                {
                    return (false, $"index {index} out of range ({holders.Count} card options)");
                }
                NCardHolder holder = holders[index];
                Fire(() => { holder.EmitSignal(NCardHolder.SignalName.Pressed, holder); return Task.CompletedTask; }, "choose card reward");
                return (true, $"submitted choose card reward index {index}");
            }
            case NChooseARelicSelection relicScreen:
            {
                List<NRelicBasicHolder> holders = UiHelper.FindAll<NRelicBasicHolder>(relicScreen);
                if (index < 0 || index >= holders.Count)
                {
                    return (false, $"index {index} out of range ({holders.Count} relic options)");
                }
                NClickableControl relicTarget = holders[index];
                Fire(() => UiHelper.Click(relicTarget), "choose relic");
                return (true, $"submitted choose relic index {index}");
            }
            case NEventRoom eventRoom:
            {
                List<NEventOptionButton> buttons = UiHelper.FindAll<NEventOptionButton>(eventRoom)
                    .Where(b => b.Option is { IsLocked: false })
                    .ToList();
                if (index < 0 || index >= buttons.Count)
                {
                    return (false, $"index {index} out of range ({buttons.Count} event options)");
                }
                NEventOptionButton optionButton = buttons[index];
                Fire(() => UiHelper.Click(optionButton), "choose event option");
                return (true, $"submitted choose event option index {index}");
            }
            case NRewardsScreen rewardsScreen:
            {
                List<NRewardButton> buttons = UiHelper.FindAll<NRewardButton>(rewardsScreen);
                if (index < 0 || index >= buttons.Count)
                {
                    return (false, $"index {index} out of range ({buttons.Count} reward buttons)");
                }
                NClickableControl rewardTarget = buttons[index];
                Fire(() => UiHelper.Click(rewardTarget), "choose reward");
                return (true, $"submitted choose reward index {index}");
            }
            case NTreasureRoom treasureRoom:
            {
                List<NTreasureRoomRelicHolder> holders = UiHelper.FindAll<NTreasureRoomRelicHolder>(treasureRoom)
                    .Where(h => h.IsEnabled && h.Visible)
                    .ToList();
                if (index < 0 || index >= holders.Count)
                {
                    return (false, $"index {index} out of range ({holders.Count} chest relics)");
                }
                NClickableControl chestTarget = holders[index];
                Fire(() => UiHelper.Click(chestTarget), "choose chest relic");
                return (true, $"submitted choose chest relic index {index}");
            }
            case NRestSiteRoom restRoom:
                return ClickIndexedButton(restRoom, index, "rest site option");
            case NMerchantRoom shopRoom:
                return ClickIndexedButton(shopRoom, index, "shop item");
            default:
            {
                if (context is NChooseACardSelectionScreen or NSimpleCardSelectScreen or NDeckCardSelectScreen
                    or NDeckUpgradeSelectScreen or NDeckTransformSelectScreen or NDeckEnchantSelectScreen
                    or NChooseABundleSelectionScreen)
                {
                    Node screenNode = (Node)context;
                    List<NCardHolder> holders = UiHelper.FindAll<NCardHolder>(screenNode);
                    if (index < 0 || index >= holders.Count)
                    {
                        return (false, $"index {index} out of range ({holders.Count} cards)");
                    }
                    NCardHolder holder = holders[index];
                    Fire(() => { holder.EmitSignal(NCardHolder.SignalName.Pressed, holder); return Task.CompletedTask; }, "choose card");
                    return (true, $"submitted choose card index {index}");
                }
                return (false, $"choose not supported on screen {context?.GetType().Name ?? "null"}");
            }
        }
    }

    private static (bool, string) ClickIndexedButton(Node screenNode, int index, string label)
    {
        List<NClickableControl> buttons = UiHelper.FindAll<NRestSiteButton>(screenNode).Cast<NClickableControl>().ToList();
        if (buttons.Count == 0)
        {
            buttons = UiHelper.FindAll<NRewardButton>(screenNode).Cast<NClickableControl>().ToList();
        }
        if (index < 0 || index >= buttons.Count)
        {
            return (false, $"index {index} out of range ({buttons.Count} {label} buttons)");
        }
        NClickableControl target = buttons[index];
        Fire(() => UiHelper.Click(target), label);
        return (true, $"submitted {label} index {index}");
    }

    private static (bool, string) Skip()
    {
        IScreenContext? context = ActiveScreenContext.Instance.GetCurrentScreen();
        if (context is not Node screenNode)
        {
            return (false, "no active screen to skip");
        }
        NChoiceSelectionSkipButton? skipButton = UiHelper.FindFirst<NChoiceSelectionSkipButton>(screenNode);
        if (skipButton == null)
        {
            return (false, $"no skip button on screen {context.GetType().Name}");
        }
        NClickableControl skipTarget = skipButton;
        Fire(() => UiHelper.Click(skipTarget), "skip");
        return (true, "submitted skip");
    }

    private static (bool, string) TreasureOpen()
    {
        if (ActiveScreenContext.Instance.GetCurrentScreen() is not NTreasureRoom room)
        {
            return (false, "not in a treasure room");
        }
        Node? chest = room.GetNodeOrNull("Chest");
        if (chest is not NClickableControl clickable)
        {
            return (false, "chest node not found or already opened");
        }
        Fire(() => UiHelper.Click(clickable), "open chest");
        return (true, "submitted treasure_open");
    }

    private static (bool, string) Proceed()
    {
        IScreenContext? context = ActiveScreenContext.Instance.GetCurrentScreen();
        NProceedButton? proceed = context switch
        {
            IRoomWithProceedButton roomButton => roomButton.ProceedButton,
            NRewardsScreen rewards => UiHelper.FindFirst<NProceedButton>(rewards),
            NGameOverScreen gameOver => UiHelper.FindFirst<NProceedButton>(gameOver),
            Node node => UiHelper.FindFirst<NProceedButton>(node),
            _ => null,
        };
        proceed ??= UiHelper.FindFirst<NProceedButton>(((SceneTree)Engine.GetMainLoop()).Root);
        if (proceed == null)
        {
            return (false, $"no proceed button on screen {context?.GetType().Name ?? "null"}");
        }
        if (!proceed.IsEnabled)
        {
            return (false, "proceed button is not enabled yet");
        }
        NProceedButton proceedRef = proceed;
        Fire(() => UiHelper.Click(proceedRef), "proceed");
        return (true, "submitted proceed");
    }

    private static (bool, string) RestSiteOption(bool preferSmith)
    {
        if (ActiveScreenContext.Instance.GetCurrentScreen() is not NRestSiteRoom room)
        {
            return (false, "not in a rest site room");
        }
        List<NRestSiteButton> buttons = UiHelper.FindAll<NRestSiteButton>(room);
        if (buttons.Count == 0)
        {
            return (false, "no rest site option buttons found");
        }
        NRestSiteButton? chosen = buttons.FirstOrDefault(b =>
            b.Name.ToString().Contains(preferSmith ? "Smith" : "Rest", StringComparison.OrdinalIgnoreCase));
        chosen ??= preferSmith && buttons.Count > 1 ? buttons[1] : buttons[0];
        NClickableControl target = chosen;
        string label = preferSmith ? "smith" : "rest";
        Fire(() => UiHelper.Click(target), label);
        return (true, $"submitted {label} ({chosen.Name})");
    }

    private static (bool, string) ShopBuy(JsonElement args)
    {
        if (!TryGetInt(args, "index", out int index))
        {
            return (false, "shop_buy requires index");
        }
        return ClickIndexedButton((Node?)ActiveScreenContext.Instance.GetCurrentScreen() ?? new Node(), index, "shop buy");
    }

    private static (bool, string) ShopLeave()
    {
        return Proceed();
    }

    private static (bool, string) StartRun(JsonElement args)
    {
        string? character = GetString(args, "character");
        string? seed = GetString(args, "seed");
        Fire(() => StartRunSequence(character, seed), "start run");
        return (true, $"submitted start_run (character={character ?? "random"}, seed={seed ?? "random"})");
    }

    // Mirrors the game's own AutoSlay menu path (AutoSlayer.PlayMainMenuAsync).
    private static async Task StartRunSequence(string? character, string? seed)
    {
        Node root = ((SceneTree)Engine.GetMainLoop()).Root;
        if (!string.IsNullOrEmpty(seed))
        {
            if (NGame.Instance != null)
            {
                NGame.Instance.DebugSeedOverride = seed;
            }
        }
        try
        {
            SaveManager.Instance.SetFtuesEnabled(false);
            SaveManager.Instance.PrefsSave.FastMode = FastModeType.Fast;
        }
        catch (Exception e)
        {
            BridgeMod.LogErr($"prefs tweak failed: {e}");
        }
        Control mainMenu = await WaitHelper.ForNode<Control>(root, "/root/Game/RootSceneContainer/MainMenu", default, TimeSpan.FromSeconds(30));
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
        NCharacterSelectButton? chosen = null;
        if (!string.IsNullOrEmpty(character))
        {
            chosen = characterButtons.FirstOrDefault(b =>
                !b.IsLocked && b.Name.ToString().Contains(character, StringComparison.OrdinalIgnoreCase));
            chosen ??= characterButtons.FirstOrDefault(b =>
                !b.IsLocked && b.Character?.Id.Entry.Contains(character, StringComparison.OrdinalIgnoreCase) == true);
        }
        chosen ??= characterButtons.FirstOrDefault(b => !b.IsLocked);
        if (chosen == null)
        {
            BridgeMod.LogErr("start_run: no unlocked character button found");
            return;
        }
        chosen.Select();
        await Task.Delay(200, default);
        NButton confirm = await WaitHelper.ForNode<NButton>(selectScreen, "ConfirmButton", default, TimeSpan.FromSeconds(10));
        await UiHelper.Click(confirm);
        BridgeMod.LogInfo($"start_run: embarked as {chosen.Name} (seed={seed ?? "random"})");
    }

    private static (bool, string) AbandonRun()
    {
        Fire(AbandonRunSequence, "abandon run");
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

    private static bool TryGetCombatPlayer(out Player? player, out CombatState combat, out PlayerCombatState? pcs)
    {
        player = null;
        combat = null!;
        pcs = null;
        try
        {
            if (!CombatManager.Instance.IsInProgress)
            {
                return false;
            }
            CombatState? state = CombatManager.Instance.DebugOnlyGetState();
            if (state == null)
            {
                return false;
            }
            combat = state;
            player = LocalContext.GetMe(state);
            pcs = player?.PlayerCombatState;
            return player != null;
        }
        catch (Exception)
        {
            return false;
        }
    }

    private static void Fire(Func<Task> work, string label)
    {
        work().ContinueWith(task =>
        {
            if (task.IsFaulted)
            {
                BridgeMod.LogErr($"{label} failed: {task.Exception}");
            }
        }, TaskScheduler.Default);
    }

    private static bool TryGetInt(JsonElement args, string name, out int value)
    {
        value = 0;
        if (args.ValueKind != JsonValueKind.Object)
        {
            return false;
        }
        if (!args.TryGetProperty(name, out JsonElement prop))
        {
            return false;
        }
        if (prop.ValueKind == JsonValueKind.Number && prop.TryGetInt32(out value))
        {
            return true;
        }
        if (prop.ValueKind == JsonValueKind.String && int.TryParse(prop.GetString(), out value))
        {
            return true;
        }
        return false;
    }

    private static string? GetString(JsonElement args, string name)
    {
        if (args.ValueKind != JsonValueKind.Object || !args.TryGetProperty(name, out JsonElement prop))
        {
            return null;
        }
        return prop.ValueKind == JsonValueKind.String ? prop.GetString() : null;
    }
}
