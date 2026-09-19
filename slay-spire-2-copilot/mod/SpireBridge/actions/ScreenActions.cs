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

// Screen-navigation action executors: choose/skip/proceed, map select,
// treasure/rest/shop, and in-hand card-selection toggles.
public static class ScreenActions
{
    internal static (bool, string) MapSelect(JsonElement args)
    {
        if (!ActionExecutor.TryGetInt(args, "row", out int row) || !ActionExecutor.TryGetInt(args, "col", out int col))
        {
            return (false, "map_select requires row and col");
        }
        if (RunManager.Instance.DebugOnlyGetState() == null)
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
            return (false, $"no map point node at ({row},{col}) among {points.Count} nodes");
        }
        NMapPoint pointRef = targetPoint;
        ActionExecutor.Fire(async () =>
        {
            // Map points stay disabled until NMapScreen.IsTravelEnabled is set;
            // our menu automation path never triggers the game's enabler, so set
            // it here (honors Hook.ShouldProceedToNextMapPoint) and fall back to
            // debug travel, then select through the game's own entry point that
            // enqueues VoteForMapCoordAction.
            NMapScreen? screen = NMapScreen.Instance;
            if (screen == null)
            {
                BridgeMod.LogErr("map_select: NMapScreen.Instance is null");
                return;
            }
            if (!screen.IsTravelEnabled)
            {
                try
                {
                    screen.SetTravelEnabled(true);
                }
                catch (Exception e)
                {
                    BridgeMod.LogErr($"map_select: SetTravelEnabled failed: {e}");
                }
                BridgeMod.LogInfo($"map_select: SetTravelEnabled(true) -> IsTravelEnabled={screen.IsTravelEnabled}");
            }
            if (!screen.IsTravelEnabled)
            {
                try
                {
                    screen.SetDebugTravelEnabled(true);
                    BridgeMod.LogInfo("map_select: debug travel enabled (hook declined normal travel)");
                }
                catch (Exception e)
                {
                    BridgeMod.LogErr($"map_select: SetDebugTravelEnabled failed: {e}");
                }
            }
            await Task.Delay(150, default);
            try
            {
                screen.OnMapPointSelectedLocally(pointRef);
                BridgeMod.LogInfo($"map_select ({row},{col}): vote enqueued via OnMapPointSelectedLocally");
            }
            catch (Exception e)
            {
                BridgeMod.LogErr($"map_select: OnMapPointSelectedLocally failed: {e}; falling back to ForceClick");
                await UiHelper.Click(pointRef);
            }
        }, "map select");
        return (true, $"submitted map_select ({row},{col})");
    }

    internal static (bool, string) Choose(JsonElement args)
    {
        if (!ActionExecutor.TryGetInt(args, "index", out int index))
        {
            return (false, "choose requires index");
        }
        IScreenContext? context = ActiveScreenContext.Instance.GetCurrentScreen();
        // Mid-combat choose-a-card overlays (boss Curse of Knowledge, potions)
        // may not be registered as the ActiveScreenContext — fall back to a
        // visible-tree scan so choose works while combat is in progress.
        if (context is NCombatRoom or null || CombatManager.Instance.IsInProgress)
        {
            if (ScreenDetect.FindCombatSelectOverlay() is IScreenContext overlayContext)
            {
                context = overlayContext;
            }
        }
        // In-hand selection (Gambling Chip, Armaments upgrade-select, …) has no
        // overlay screen node — route choose to the hand toggle only when no
        // overlay screen is live. Overlay screens (NCombatPileCardSelectScreen
        // Stratagem picks etc.) take priority: a stale NPlayerHand selection
        // mode must not hijack their indices (live: Act-3 boss 2026-09-17,
        // choose on card_choice failed with "index 8 out of range (hand size 4)").
        if (ScreenDetect.FindCombatSelectOverlay() is null
            && context is NCombatRoom or null
            && ScreenDetect.FindHandSelectMode() is { } handSelect)
        {
            return ToggleHandSelectCard(handSelect, index);
        }
        switch (context)
        {
            case NCardRewardSelectionScreen cardReward:
            {
                // Printed index space = screen._options (ScreenOptions.CardRewardOptions).
                // UI holder order diverged from _options live (run-51: printed [2]=FEED,
                // unfiltered FindAll<NCardHolder>[2] pressed MANGLE) — same ghost/preview
                // pollution class as run-12 THE_GAMBIT→PROLONG on grid screens, which
                // SelectableCardHolders fixed for card_choice but NOT for card_reward.
                // Root fix: resolve by card id, never by raw holder index — probe
                // _options[index] for the requested id, then press the holder that
                // actually carries that id. Unresolvable / no-match = fail-loud refuse
                // (no fallback, no guess). 2026-09-19 user contract.
                string? requestedId = null;
                int optionCount = 0;
                try
                {
                    if (ScreenOptions.CardRewardOptionsField?.GetValue(cardReward) is System.Collections.IEnumerable raw)
                    {
                        int i = 0;
                        foreach (object? opt in raw)
                        {
                            optionCount++;
                            if (i == index && opt != null)
                            {
                                requestedId = GameProbe.ProbeModelId(opt);
                            }
                            i++;
                        }
                    }
                }
                catch (Exception e)
                {
                    BridgeMod.LogErr($"card_reward requested-id probe failed: {e}");
                }
                if (index < 0 || (optionCount > 0 && index >= optionCount))
                {
                    return (false, $"index {index} out of range ({optionCount} card options)");
                }
                if (string.IsNullOrEmpty(requestedId))
                {
                    InfoCompleteness.FlagDuringAction(
                        $"card_reward choose refused: option {index} id unresolvable at press time (player reads the card on screen)");
                    return (false,
                        $"info incomplete: card_reward option {index} id unresolvable — choose refused (no fallback; client must stop + notify)");
                }
                // Candidate holders: grid-filtered first (reward layouts that use
                // NGridCardHolder), else all NCardHolder. Press by id match only.
                List<NCardHolder> candidates = UiHelper.FindAll<NGridCardHolder>(cardReward).Cast<NCardHolder>().ToList();
                if (candidates.Count == 0)
                {
                    candidates = UiHelper.FindAll<NCardHolder>(cardReward);
                }
                NCardHolder? target = null;
                var resolvedIds = new List<string>();
                foreach (NCardHolder h in candidates)
                {
                    string? hid = GameProbe.ProbeModelId(h);
                    if (!string.IsNullOrEmpty(hid))
                    {
                        resolvedIds.Add(hid);
                        if (target is null && hid.StartsWith(requestedId, StringComparison.Ordinal))
                        {
                            target = h;
                        }
                    }
                }
                if (target is null)
                {
                    if (resolvedIds.Count == 0)
                    {
                        InfoCompleteness.FlagDuringAction(
                            $"card_reward choose refused: holder ids unresolvable (requested {requestedId} at printed index {index})");
                        return (false,
                            $"info incomplete: card_reward holder ids unresolvable — choose refused (requested_id={requestedId}; no fallback)");
                    }
                    InfoCompleteness.FlagDuringAction(
                        $"card_reward choose refused: requested_id={requestedId} not present on any holder (holder ids: {string.Join(",", resolvedIds)}) — printed/UI mapping divergence");
                    return (false,
                        $"card_reward mapping divergence: requested_id={requestedId} not on any holder [holder_ids={string.Join(",", resolvedIds)}] — choose refused (no fallback; re-read state and choose by printed id)");
                }
                RunState? verifyRun = null;
                Player? verifyPlayer = null;
                try
                {
                    verifyRun = RunManager.Instance.DebugOnlyGetState();
                    if (verifyRun != null)
                    {
                        verifyPlayer = LocalContext.GetMe(verifyRun.Players);
                    }
                }
                catch (Exception e)
                {
                    BridgeMod.LogErr($"card_reward deck snapshot failed: {e}");
                }
                List<string> deckBefore = ChooseVerify.DeckTupleSnapshot(verifyPlayer, verifyRun);
                BridgeMod.CardRewardVerifyPending =
                    new CardRewardVerifyPending(index, requestedId, deckBefore);
                NCardHolder pressTarget = target;
                ActionExecutor.Fire(() => { pressTarget.EmitSignal(NCardHolder.SignalName.Pressed, pressTarget); return Task.CompletedTask; }, "choose card reward");
                return (true,
                    $"submitted choose card reward index {index} (requested_id={requestedId}; pressed holder by id match; applied-card verification pending next state)");
            }
            case NChooseARelicSelection relicScreen:
                return ClickAt<NRelicBasicHolder>(relicScreen, index, "choose relic", "relic options");
            case NEventRoom eventRoom:
                return ClickAt<NEventOptionButton>(eventRoom, index, "choose event option", "event options",
                    b => b.Option is { IsLocked: false });
            case NRewardsScreen rewardsScreen:
                return ClickAt<NRewardButton>(rewardsScreen, index, "choose reward", "reward buttons");
            case NTreasureRoom treasureRoom:
            {
                // Index space must match ScreenOptions.TreasureOptions: chest (if
                // present) occupies index 0, enabled relic holders follow.
                List<NTreasureRoomRelicHolder> holders = UiHelper.FindAll<NTreasureRoomRelicHolder>(treasureRoom)
                    .Where(h => h.IsEnabled && h.Visible)
                    .ToList();
                bool chestListed = treasureRoom.GetNodeOrNull("Chest") != null;
                int relicIndex = chestListed ? index - 1 : index;
                if (relicIndex < 0)
                {
                    return (false, "index 0 is the chest; use treasure_open for it");
                }
                if (relicIndex >= holders.Count)
                {
                    return (false, $"index {index} out of range ({holders.Count} chest relics)");
                }
                NClickableControl chestTarget = holders[relicIndex];
                ActionExecutor.Fire(() => UiHelper.Click(chestTarget), "choose chest relic");
                return (true, $"submitted choose chest relic index {index}");
            }
            case NRestSiteRoom restRoom:
                return ClickIndexedButton(restRoom, index, "rest site option");
            case NMerchantRoom shopRoom:
                return ClickIndexedButton(shopRoom, index, "shop item");
            case NCrystalSphereScreen crystalScreen:
                return ClickAt<NCrystalSphereCell>(crystalScreen, index, "crystal cell", "crystal cells");
            default:
            {
                if (context is NChooseACardSelectionScreen or NSimpleCardSelectScreen or NDeckCardSelectScreen
                    or NDeckUpgradeSelectScreen or NDeckTransformSelectScreen or NDeckEnchantSelectScreen
                    or NChooseABundleSelectionScreen or NCombatPileCardSelectScreen)
                {
                    Node screenNode = (Node)context;
                    // Same index space as ScreenOptions: deck-select grids are
                    // NGridCardHolder nodes; preview/ghost NCardHolder nodes
                    // must not occupy indices.
                    List<NCardHolder> holders = ScreenOptions.SelectableCardHolders(screenNode);
                    if (index < 0 || index >= holders.Count)
                    {
                        return (false, $"index {index} out of range ({holders.Count} cards)");
                    }
                    NCardHolder holder = holders[index];
                    // NCardGridSelectionScreen subclasses (deck_select screens
                    // and NCombatPileCardSelectScreen) route clicks through
                    // NCardGrid.HolderPressed, which the grid re-emits only for
                    // holders it allocated AND connected — EmitSignal(Pressed)
                    // on a found holder never reaches OnCardClicked when the
                    // connection is missing/pooled (live 2026-09-17 run-12:
                    // PaelsTooth 5-card storage and Neow's Fury recovery picks
                    // silently registered nothing; MinSelect==MaxSelect screens
                    // then deadlock because Confirm stays disabled).
                    // NChooseACardSelectionScreen / NChooseABundleSelectionScreen
                    // connect holder.Pressed directly and stay on the signal
                    // path; grid-backed screens invoke OnCardClicked via
                    // reflection, same pattern as InvokeHandSelectAdd.
                    if (context is NChooseACardSelectionScreen or NChooseABundleSelectionScreen)
                    {
                        ActionExecutor.Fire(() => { holder.EmitSignal(NCardHolder.SignalName.Pressed, holder); return Task.CompletedTask; }, "choose card (holder signal)");
                        return (true, $"submitted choose card index {index}");
                    }
                    IScreenContext screenCtx = context;
                    CardModel cardModel = holder.CardModel;
                    ActionExecutor.Fire(() =>
                    {
                        MethodInfo? onClicked = screenCtx.GetType().GetMethod(
                            "OnCardClicked",
                            BindingFlags.NonPublic | BindingFlags.Instance,
                            null,
                            new[] { typeof(CardModel) },
                            null);
                        onClicked ??= typeof(NCardGridSelectionScreen).GetMethod(
                            "OnCardClicked",
                            BindingFlags.NonPublic | BindingFlags.Instance,
                            null,
                            new[] { typeof(CardModel) },
                            null);
                        if (onClicked != null)
                        {
                            onClicked.Invoke(screenCtx, new object[] { cardModel });
                        }
                        else
                        {
                            holder.EmitSignal(NCardHolder.SignalName.Pressed, holder);
                        }
                        return Task.CompletedTask;
                    }, "choose card (OnCardClicked)");
                    return (true, $"submitted choose card index {index} via OnCardClicked");
                }
                return (false, $"choose not supported on screen {context?.GetType().Name ?? "null"}");
            }
        }
    }

    // Shared chooser for screens whose option index space equals a plain
    // FindAll<T> list: bounds-check, click, report — messages stay identical
    // to the per-screen cases they replace.
    private static (bool, string) ClickAt<T>(Node scope, int index, string actionLabel, string boundsLabel, Func<T, bool>? filter = null)
        where T : NClickableControl
    {
        List<T> items = UiHelper.FindAll<T>(scope);
        if (filter != null)
        {
            items = items.Where(filter).ToList();
        }
        if (index < 0 || index >= items.Count)
        {
            return (false, $"index {index} out of range ({items.Count} {boundsLabel})");
        }
        T target = items[index];
        ActionExecutor.Fire(() => UiHelper.Click(target), actionLabel);
        return (true, $"submitted {actionLabel} index {index}");
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
        ActionExecutor.Fire(() => UiHelper.Click(target), label);
        return (true, $"submitted {label} index {index}");
    }

    // Locate the right confirm button on any card-selection screen. Preview
    // confirmations live inside container subtrees whose % unique-names do not
    // resolve from the screen root, so walk all confirm buttons and prefer the
    // enabled one under a preview-named parent.
    private static NConfirmButton? FindSelectionConfirm(Node screen)
    {
        List<NConfirmButton> all = UiHelper.FindAll<NConfirmButton>(screen);
        NConfirmButton? enabledPreview = null;
        NConfirmButton? enabledAny = null;
        NConfirmButton? namedConfirm = null;
        NConfirmButton? anyVisible = null;
        foreach (NConfirmButton button in all)
        {
            if (!button.Visible)
            {
                continue;
            }
            anyVisible ??= button;
            string parentName = button.GetParent()?.Name.ToString() ?? "";
            bool previewish = parentName.Contains("review", StringComparison.OrdinalIgnoreCase)
                || button.Name.ToString().Contains("review", StringComparison.OrdinalIgnoreCase);
            if (button.IsEnabled)
            {
                if (previewish)
                {
                    enabledPreview ??= button;
                }
                enabledAny ??= button;
            }
            if (button.Name.ToString().Contains("Confirm", StringComparison.OrdinalIgnoreCase))
            {
                namedConfirm ??= button;
            }
        }
        NConfirmButton? pick = enabledPreview ?? enabledAny ?? namedConfirm ?? anyVisible ?? all.FirstOrDefault();
        if (pick != null)
        {
            BridgeMod.LogInfo($"FindSelectionConfirm pick={pick.Name}/{pick.GetParent()?.Name} "
                + $"enabled={pick.IsEnabled} candidates={all.Count}");
        }
        return pick;
    }

    // First visible modal button whose name contains any of the keywords.
    private static NButton? FindModalButton(Node modalNode, params string[] keywords)
    {
        List<NButton> buttons = UiHelper.FindAll<NButton>(modalNode);
        return buttons.FirstOrDefault(b =>
        {
            if (!b.Visible)
            {
                return false;
            }
            string name = b.Name.ToString();
            return keywords.Any(k => name.Contains(k));
        });
    }

    internal static (bool, string) Skip()
    {
        // In-hand selection skip: complete with an empty selection (Gambling
        // Chip MinSelect=0 — discard nothing and unblock the turn). Overlay
        // screens outrank a stale hand selection mode (same rule as Choose()).
        if (ScreenDetect.FindCombatSelectOverlay() is null
            && ScreenDetect.FindHandSelectMode() is { } _)
        {
            return SkipHandSelectEmpty();
        }
        IScreenContext? context = ActiveScreenContext.Instance.GetCurrentScreen();
        if (NModalContainer.Instance?.OpenModal is Node modalNode && ReferenceEquals(context, modalNode))
        {
            NButton? dismiss = FindModalButton(modalNode, "No", "Cancel", "Close", "Dismiss");
            if (dismiss != null)
            {
                NButton target = dismiss;
                ActionExecutor.Fire(() => UiHelper.Click(target), "modal dismiss");
                return (true, $"submitted modal dismiss ({target.Name})");
            }
            return (false, "no dismiss button on modal");
        }
        if (context is not Node screenNode)
        {
            return (false, "no active screen to skip");
        }
        // STS2 card rewards have NO skip button at all: the scene node
        // NChoiceSelectionSkipButton (child "SkipButton") belongs to the
        // RELIC selection screen, not NCardRewardSelectionScreen. The game's
        // skip semantic for cards is a null choice — CardReward treats
        // OptionSelected()==null as endSelection with no card obtained, and
        // the screen's _ExitTree sets that null result. Remove the overlay
        // the same way the game's own post-choice cleanup does
        // (NOverlayStack.Remove) so the null choice resolves legally.
        if (context is NCardRewardSelectionScreen rewardScreen)
        {
            ActionExecutor.Fire(() =>
            {
                NOverlayStack.Instance?.Remove(rewardScreen);
                return Task.CompletedTask;
            }, "card reward skip via overlay removal");
            return (true, "submitted card-reward skip (overlay remove -> null choice)");
        }
        NChoiceSelectionSkipButton? skipButton = UiHelper.FindFirst<NChoiceSelectionSkipButton>(screenNode);
        // Live gap 2026-09-17 (Act-3 run, 3rd occurrence): on
        // NCardRewardSelectionScreen the skip control is documented as an
        // NChoiceSelectionSkipButton ("like the choose 1 of 3 card reward
        // screen") but is not found inside the screen node's own subtree —
        // likely lives in a shared overlay/GlobalUi container. Walk outward
        // (parent, then scene-tree root) before giving up so the advertised
        // skip action is actually executable.
        if (skipButton == null && screenNode.GetParent() is Node screenParent)
        {
            skipButton = UiHelper.FindFirst<NChoiceSelectionSkipButton>(screenParent);
        }
        if (skipButton == null)
        {
            skipButton = UiHelper.FindFirst<NChoiceSelectionSkipButton>(
                ((SceneTree)Engine.GetMainLoop()).Root);
        }
        if (skipButton != null && skipButton.Visible)
        {
            NClickableControl skipTarget = skipButton;
            ActionExecutor.Fire(() => UiHelper.Click(skipTarget), "skip");
            return (true, "submitted skip");
        }
        // Card-reward screens expose skip as a plain button, not
        // NChoiceSelectionSkipButton — state still advertises the action.
        List<NButton> screenButtons = UiHelper.FindAll<NButton>(screenNode);
        NButton? namedSkip = screenButtons.FirstOrDefault(b =>
        {
            if (!b.Visible)
            {
                return false;
            }
            string name = b.Name.ToString();
            return name.Contains("Skip", StringComparison.OrdinalIgnoreCase)
                || name.Contains("Pass", StringComparison.OrdinalIgnoreCase)
                || name.Contains("跳过");
        });
        if (namedSkip != null)
        {
            NButton target = namedSkip;
            ActionExecutor.Fire(() => UiHelper.Click(target), "skip by name");
            return (true, $"submitted skip ({target.Name})");
        }
        // Deck-select screens cancel through %Close (completes with an empty
        // selection when prefs.Cancelable) — no skip button exists there.
        if (context is NDeckCardSelectScreen or NDeckUpgradeSelectScreen
            or NDeckTransformSelectScreen or NDeckEnchantSelectScreen)
        {
            NBackButton? close = screenNode.GetNodeOrNull<NBackButton>("%Close");
            if (close != null && close.Visible && close.IsEnabled)
            {
                NBackButton closeTarget = close;
                ActionExecutor.Fire(() => UiHelper.Click(closeTarget), "deck select close");
                return (true, "submitted deck select close (cancel)");
            }
            return (false, "deck select screen has no enabled close/cancel button");
        }
        return (false, $"no skip button on screen {context.GetType().Name}");
    }

    internal static (bool, string) TreasureOpen()
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
        ActionExecutor.Fire(() => UiHelper.Click(clickable), "open chest");
        return (true, "submitted treasure_open");
    }

    internal static (bool, string) Proceed()
    {
        // In-hand selection confirm — no NProceedButton exists in this mode.
        // Overlay screens (card_choice/deck_select confirm chains) outrank a
        // stale hand selection mode; same priority rule as Choose().
        if (ScreenDetect.FindCombatSelectOverlay() is null
            && ScreenDetect.FindHandSelectMode() is { } _)
        {
            return ConfirmHandSelect();
        }
        IScreenContext? context = ActiveScreenContext.Instance.GetCurrentScreen();
        // Game-over summary needs the Continue -> ReturnToMainMenu chain, not a
        // proceed button; this is the any-state takeover entry.
        if (context is MegaCrit.Sts2.Core.Nodes.Screens.GameOverScreen.NGameOverScreen endedScreen)
        {
            ActionExecutor.Fire(() => RunLifecycle.ClearGameOverScreen(endedScreen), "game over continue");
            return (true, "submitted game_over continue chain");
        }
        // Modal popups: click the affirmative button (Yes/Confirm/OK/Accept).
        if (NModalContainer.Instance?.OpenModal is Node modalNode && ReferenceEquals(context, modalNode))
        {
            List<NButton> buttons = UiHelper.FindAll<NButton>(modalNode);
            NButton? affirmative = FindModalButton(modalNode, "Yes", "Confirm", "OK", "Accept", "Proceed");
            affirmative ??= buttons.FirstOrDefault(b => b.Visible);
            if (affirmative != null)
            {
                NButton target = affirmative;
                ActionExecutor.Fire(() => UiHelper.Click(target), "modal confirm");
                return (true, $"submitted modal confirm ({target.Name})");
            }
            return (false, "no button found on modal");
        }
        // Card-selection screens confirm through NConfirmButton with varying
        // naming per subclass (%Confirm / "Confirm" / preview-container Confirm).
        if (context is NSimpleCardSelectScreen
            or NChooseACardSelectionScreen
            or NChooseABundleSelectionScreen
            or NDeckCardSelectScreen
            or NDeckUpgradeSelectScreen
            or NDeckTransformSelectScreen
            or NDeckEnchantSelectScreen
            or NCombatPileCardSelectScreen)
        {
            Node node = (Node)context;
            // Two-phase confirm chain: main Confirm reveals a preview; the
            // preview's own Confirm finalizes. Click whichever is actionable
            // now, then retry the other after a beat so a single proceed can
            // complete screens that require both steps.
            ActionExecutor.Fire(async () =>
            {
                for (int attempt = 0; attempt < 3; attempt++)
                {
                    NConfirmButton? confirm = FindSelectionConfirm(node);
                    if (confirm == null)
                    {
                        return;
                    }
                    BridgeMod.LogInfo($"confirm chain attempt {attempt + 1} -> {confirm.Name} visible={confirm.Visible} enabled={confirm.IsEnabled}");
                    await UiHelper.Click(confirm);
                    await Task.Delay(500, default);
                    if (!GodotObject.IsInstanceValid(node) || (node is Control control && !control.IsVisibleInTree()))
                    {
                        return; // screen closed: selection finalized
                    }
                }
            }, "confirm card selection");
            return (true, "submitted confirm (chain)");
        }
        NProceedButton? proceed = context switch
        {
            IRoomWithProceedButton roomButton => roomButton.ProceedButton,
            NRewardsScreen rewards => UiHelper.FindFirst<NProceedButton>(rewards),
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
        ActionExecutor.Fire(() => UiHelper.Click(proceedRef), "proceed");
        return (true, "submitted proceed");
    }

    internal static (bool, string) RestSiteOption(bool preferSmith)
    {
        if (ActiveScreenContext.Instance.GetCurrentScreen() is not NRestSiteRoom room)
        {
            return (false, "not in a rest site room");
        }
        List<NRestSiteButton> buttons = UiHelper.FindAll<NRestSiteButton>(room);
        NRestSiteButton? chosen = null;
        foreach (NRestSiteButton button in buttons)
        {
            try
            {
                string oid = button.Option.OptionId;
                if (GameProbe.RestOptionIsSmith(oid) == preferSmith)
                {
                    chosen = button;
                    break;
                }
            }
            catch (Exception)
            {
                // option not bound on this button
            }
        }
        chosen ??= buttons.FirstOrDefault();
        if (chosen == null)
        {
            return (false, "no rest site buttons found");
        }
        NRestSiteButton target = chosen;
        string label = preferSmith ? "smith" : "rest";
        string optionId;
        try
        {
            optionId = target.Option.OptionId;
        }
        catch (Exception)
        {
            optionId = target.Name.ToString();
        }
        ActionExecutor.Fire(async () =>
        {
            // Click the button rather than Option.OnSelect(): the room wires
            // completion callbacks (ShowProceedButton / SetTravelEnabled) only
            // through its own button path; OnSelect alone leaves the room stuck.
            await UiHelper.Click(target);
            BridgeMod.LogInfo($"{label} clicked button ({optionId})");
        }, label);
        return (true, $"submitted {label} ({optionId})");
    }

    internal static (bool, string) ShopBuy(JsonElement args)
    {
        NMerchantRoom? room = NMerchantRoom.Instance;
        Node? scope = ActiveScreenContext.Instance.GetCurrentScreen() as Node;
        NMerchantInventory? inventory = ScreenOptions.FindMerchantInventory(room, scope);
        if (inventory == null)
        {
            return (false, "no merchant inventory active");
        }
        if (room?.Inventory is { IsOpen: false })
        {
            room.OpenInventory();
        }
        List<NMerchantSlot> slots = (inventory.GetAllSlots()?.ToList() ?? new List<NMerchantSlot>())
            .Where(s => s.Entry != null)
            .ToList();
        string? itemId = ActionExecutor.GetString(args, "item_id");
        NMerchantSlot? slot = null;
        if (!string.IsNullOrEmpty(itemId))
        {
            foreach (NMerchantSlot candidate in slots)
            {
                MerchantEntry? e = candidate.Entry;
                object probe = e is MerchantCardEntry { CreationResult: { } creation } ? creation : e!;
                string id = GameProbe.ProbeModelId(probe) ?? e!.GetType().Name;
                if (id == itemId)
                {
                    slot = candidate;
                    break;
                }
            }
            if (slot == null)
            {
                return (false, $"item_id '{itemId}' not found in shop inventory");
            }
        }
        else if (ActionExecutor.TryGetInt(args, "index", out int index))
        {
            if (index < 0 || index >= slots.Count)
            {
                return (false, $"shop_buy index {index} out of range ({slots.Count} items)");
            }
            slot = slots[index];
        }
        else
        {
            return (false, "shop_buy requires index or item_id");
        }
        MerchantEntry entry = slot.Entry!;
        if (!entry.IsStocked)
        {
            return (false, "item is out of stock");
        }
        if (!entry.EnoughGold)
        {
            return (false, $"not enough gold for cost {entry.Cost}");
        }
        MerchantEntry entryRef = entry;
        NMerchantRoom? roomRef = room;
        NMerchantInventory inventoryRef = inventory;
        ActionExecutor.Fire(async () =>
        {
            try
            {
                NMerchantSlot? slotNode = (roomRef != null ? UiHelper.FindAll<NMerchantSlot>(roomRef) : UiHelper.FindAll<NMerchantSlot>(inventoryRef))
                    .FirstOrDefault(s => ReferenceEquals(s.Entry, entryRef));
                if (slotNode?.Hitbox is { } hitbox)
                {
                    await UiHelper.Click(hitbox);
                    await Task.Delay(300, default);
                }
                bool purchased = await entryRef.OnTryPurchaseWrapper(inventoryRef.Inventory, false);
                BridgeMod.LogInfo($"shop buy wrapper entry={entryRef.GetType().Name} -> {purchased}");
                if (!purchased && slotNode?.Hitbox is { } retryHitbox)
                {
                    await UiHelper.Click(retryHitbox);
                    BridgeMod.LogInfo($"shop buy hitbox fallback slot={slotNode.Name}");
                }
            }
            catch (Exception e)
            {
                BridgeMod.LogErr($"shop buy failed entry={entryRef.GetType().Name}: {e}");
            }
        }, "shop buy");
        return (true, $"submitted shop_buy {itemId ?? "index"} cost={entry.Cost}");
    }

    internal static (bool, string) ShopLeave()
    {
        NMerchantRoom? room = NMerchantRoom.Instance;
        IScreenContext? context = ActiveScreenContext.Instance.GetCurrentScreen();
        if (room == null && context is not Node)
        {
            return Proceed();
        }
        Node? scope = (Node?)room ?? (Node?)context;
        NMerchantRoom? roomRef = room;
        Node scopeRef = scope!;
        ActionExecutor.Fire(async () =>
        {
            NMerchantInventory? inv = roomRef?.Inventory
                ?? UiHelper.FindFirst<NMerchantInventory>(scopeRef);
            if (inv is { IsOpen: true })
            {
                NBackButton? back = UiHelper.FindFirst<NBackButton>(inv)
                    ?? UiHelper.FindFirst<NBackButton>(scopeRef);
                if (back != null)
                {
                    await UiHelper.Click(back);
                    await Task.Delay(400, default);
                }
            }
            NProceedButton? proceed = roomRef?.ProceedButton
                ?? UiHelper.FindFirst<NProceedButton>(scopeRef);
            if (proceed != null)
            {
                await UiHelper.Click(proceed);
            }
        }, "shop leave");
        return (true, "submitted shop_leave");
    }

    private static (bool, string) ToggleHandSelectCard(NPlayerHand hand, int index)
    {
        if (!ActionExecutor.TryGetCombatPlayer(out Player? player, out _, out PlayerCombatState? pcs) || pcs == null)
        {
            return (false, "not in an active combat");
        }
        IReadOnlyList<CardModel> cards = pcs.Hand.Cards;
        if (index < 0 || index >= cards.Count)
        {
            return (false, $"index {index} out of range (hand size {cards.Count})");
        }
        CardModel card = cards[index];
        List<CardModel> selected = ScreenDetect.GetHandSelectedCards(hand);
        if (selected.Contains(card))
        {
            if (hand.GetCard(card) is not { } cardNode)
            {
                return (false, $"hand card node for index {index} not found");
            }
            ActionExecutor.Fire(() => { hand.DeselectCard(cardNode); return Task.CompletedTask; }, "hand select deselect");
            return (true, $"hand_select deselected index {index} ({card.Id.Entry})");
        }
        if (hand.GetCardHolder(card) is not NHandCardHolder holder)
        {
            return (false, $"hand holder for index {index} not found");
        }
        bool upgradeMode = hand.CurrentMode == NPlayerHand.Mode.UpgradeSelect;
        ActionExecutor.Fire(() => { InvokeHandSelectAdd(hand, holder, upgradeMode); return Task.CompletedTask; }, "hand select add");
        return (true, $"hand_select selected index {index} ({card.Id.Entry})");
    }

    // SelectCardInSimpleMode / SelectCardInUpgradeMode are private; the game
    // invokes them through Godot method binds on holder click — reflection is
    // the headless equivalent.
    private static void InvokeHandSelectAdd(NPlayerHand hand, NHandCardHolder holder, bool upgradeMode)
    {
        MethodInfo? method = typeof(NPlayerHand).GetMethod(
            upgradeMode ? "SelectCardInUpgradeMode" : "SelectCardInSimpleMode",
            BindingFlags.NonPublic | BindingFlags.Instance);
        method?.Invoke(hand, new object[] { holder });
    }

    private static (bool, string) ConfirmHandSelect()
    {
        NPlayerHand? hand = ScreenDetect.FindHandSelectMode();
        if (hand == null)
        {
            return (false, "not in a hand card-selection mode");
        }
        MethodInfo? method = typeof(NPlayerHand).GetMethod(
            "OnSelectModeConfirmButtonPressed", BindingFlags.NonPublic | BindingFlags.Instance);
        if (method == null)
        {
            return (false, "hand select confirm method not found");
        }
        // OnSelectModeConfirmButtonPressed SetResults the live _selectionCompletionSource
        // with the current _selectedCards — confirm and (after deselecting all)
        // empty-complete share this path.
        ActionExecutor.Fire(() => { method.Invoke(hand, new object?[] { null }); return Task.CompletedTask; }, "hand select confirm");
        return (true, "submitted hand_select confirm");
    }

    private static (bool, string) SkipHandSelectEmpty()
    {
        NPlayerHand? hand = ScreenDetect.FindHandSelectMode();
        if (hand == null)
        {
            return (false, "not in a hand card-selection mode");
        }
        ActionExecutor.Fire(() =>
        {
            foreach (CardModel card in ScreenDetect.GetHandSelectedCards(hand).ToList())
            {
                if (hand.GetCard(card) is { } cardNode && GodotObject.IsInstanceValid(cardNode))
                {
                    hand.DeselectCard(cardNode);
                }
            }
            typeof(NPlayerHand)
                .GetMethod("OnSelectModeConfirmButtonPressed", BindingFlags.NonPublic | BindingFlags.Instance)
                ?.Invoke(hand, new object?[] { null });
            return Task.CompletedTask;
        }, "hand select skip empty");
        return (true, "submitted hand_select skip (empty selection)");
    }
}
