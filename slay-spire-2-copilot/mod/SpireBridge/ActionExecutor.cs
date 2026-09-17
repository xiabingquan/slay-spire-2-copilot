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
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Entities.Merchant;
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
using MegaCrit.Sts2.Core.Settings;
using MegaCrit.Sts2.Core.Timeline;
using MegaCrit.Sts2.Core.Timeline.Epochs;

namespace SpireCopilot.Bridge;

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
                "force_combat_end" => ForceCombatEnd(),
                "force_advance_turn" => ForceAdvanceTurn(),
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
                "continue_run" => ContinueRun(),
                "timeline_sync" => TimelineSync(),
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
        if (!TryGetCombatPlayer(out Player? player, out CombatState combat, out PlayerCombatState? pcs) || pcs == null)
        {
            return (false, "not in an active combat");
        }
        if (pcs.Phase != PlayerTurnPhase.Play)
        {
            return (false, $"not player play phase (phase={pcs.Phase})");
        }
        // Combat can refuse to end after a non-attack kill; CheckWinCondition
        // -> EndCombatInternal is the public finisher.
        bool anyEnemyAlive = false;
        foreach (Creature enemy in combat.Enemies)
        {
            if (enemy.IsAlive)
            {
                anyEnemyAlive = true;
                break;
            }
        }
        if (!anyEnemyAlive)
        {
            Fire(ForceCombatEndAsync, "combat win-condition end");
            return (true, "submitted end_turn (win-condition force path)");
        }
        Player playerRef = player!;
        int turnNumber = pcs.TurnNumber;
        // Empty-hand turns freeze on the sync-queue path (observed live in the
        // KinPriest boss fight: hand empty + Play phase, RequestEnqueue logs
        // success but ActionQueueSynchronizer defers forever — likely paused
        // queues after an exhaust/animation window). PlayerCmd.EndTurn has no
        // such gate when no lock-style power is present.
        bool emptyHand = pcs.Hand.Cards.Count == 0;
        // PlayerCmd.EndTurn can freeze on lock-style debuff turns; drive the
        // multiplayer-sync entry instead (OnEndedTurnLocally +
        // EndPlayerTurnAction queue) unless the hand is empty.
        Fire(async () =>
        {
            try
            {
                // Re-check: an enemy may have died between the submit snapshot
                // and main-thread execution.
                CombatState? live = CombatManager.Instance.DebugOnlyGetState();
                bool aliveNow = live != null && live.Enemies.Any(e => e.IsAlive);
                if (!aliveNow)
                {
                    await ForceCombatEndAsync();
                    return;
                }
                if (emptyHand)
                {
                    try
                    {
                        PlayerCmd.EndTurn(playerRef, canBackOut: false);
                        BridgeMod.LogInfo($"end_turn via PlayerCmd (empty hand, turn {turnNumber})");
                    }
                    catch (Exception pe)
                    {
                        BridgeMod.LogErr($"PlayerCmd empty-hand end_turn failed: {pe}; falling back to sync queue");
                        CombatManager.Instance.OnEndedTurnLocally();
                        RunManager.Instance.ActionQueueSynchronizer.RequestEnqueue(
                            new EndPlayerTurnAction(playerRef, turnNumber));
                    }
                    return;
                }
                CombatManager.Instance.OnEndedTurnLocally();
                RunManager.Instance.ActionQueueSynchronizer.RequestEnqueue(
                    new EndPlayerTurnAction(playerRef, turnNumber));
                BridgeMod.LogInfo($"end_turn via sync queue (turn {turnNumber})");
                await Task.CompletedTask;
            }
            catch (Exception e)
            {
                BridgeMod.LogErr($"sync end_turn failed, falling back to PlayerCmd: {e}");
                PlayerCmd.EndTurn(playerRef, canBackOut: false);
            }
        }, "end turn");
        return (true, emptyHand
            ? "submitted end_turn (empty-hand PlayerCmd path)"
            : "submitted end_turn (sync queue path)");
    }

    private static async Task ForceCombatEndAsync()
    {
        CombatManager cm = CombatManager.Instance;
        BridgeMod.LogInfo(
            $"force combat end: isEnding={cm.IsEnding} inProgress={cm.IsInProgress}");
        bool ended = await cm.CheckWinCondition();
        if (!ended && cm.IsInProgress)
        {
            // CheckWinCondition declined while no enemies remain; call the
            // internal finisher directly.
            BridgeMod.LogErr("force combat end: CheckWinCondition declined, calling EndCombatInternal");
            await cm.EndCombatInternal();
        }
        BridgeMod.LogInfo($"force combat end done: inProgress={cm.IsInProgress}");
    }

    private static (bool, string) ForceCombatEnd()
    {
        if (!TryGetCombatPlayer(out _, out _, out _))
        {
            return (false, "not in an active combat");
        }
        Fire(ForceCombatEndAsync, "force combat end");
        return (true, "submitted force_combat_end");
    }

    // Lock-style debuffs can freeze end_turn (fingerprint stuck, abandon no-ops).
    // Remove those powers via Creature.RemovePowerInternal, then re-drive the
    // sync end-turn path.
    private static (bool, string) ForceAdvanceTurn()
    {
        if (!TryGetCombatPlayer(out Player? player, out CombatState combat, out PlayerCombatState? pcs) || pcs == null)
        {
            return (false, "not in an active combat");
        }
        Player playerRef = player!;
        int turnNumber = pcs.TurnNumber;
        Fire(async () =>
        {
            try
            {
                CombatState? live = CombatManager.Instance.DebugOnlyGetState();
                Creature? me = live?.Allies.FirstOrDefault(a => a.IsPlayer);
                int cleared = 0;
                if (me != null)
                {
                    foreach (PowerModel power in me.Powers.ToList())
                    {
                        string id = power.Id?.Entry ?? power.GetType().Name;
                        if (id.Contains("RINGING", StringComparison.OrdinalIgnoreCase)
                            || id.Contains("LOCK", StringComparison.OrdinalIgnoreCase)
                            || id.Contains("PLOW", StringComparison.OrdinalIgnoreCase))
                        {
                            me.RemovePowerInternal(power);
                            cleared++;
                            BridgeMod.LogInfo($"force_advance_turn: cleared power {id}");
                        }
                    }
                }
                bool anyAlive = live?.Enemies.Any(e => e.IsAlive) ?? false;
                if (!anyAlive)
                {
                    await ForceCombatEndAsync();
                    return;
                }
                // Always also drive PlayerCmd — the sync queue can silently
                // defer when its internal combat-state view is out of sync
                // with PlayerCombatState.Phase (empty-hand deadlock, KinPriest
                // boss fight 2026-09-17).
                try
                {
                    PlayerCmd.EndTurn(playerRef, canBackOut: false);
                    BridgeMod.LogInfo($"force_advance_turn: PlayerCmd.EndTurn fired (turn {turnNumber})");
                }
                catch (Exception pe)
                {
                    BridgeMod.LogErr($"force_advance_turn PlayerCmd failed: {pe}");
                }
                CombatManager.Instance.OnEndedTurnLocally();
                RunManager.Instance.ActionQueueSynchronizer.RequestEnqueue(
                    new EndPlayerTurnAction(playerRef, turnNumber));
                BridgeMod.LogInfo($"force_advance_turn: cleared={cleared}, re-queued end turn {turnNumber}");
            }
            catch (Exception e)
            {
                BridgeMod.LogErr($"force_advance_turn failed: {e}");
                try
                {
                    PlayerCmd.EndTurn(playerRef, canBackOut: false);
                }
                catch (Exception e2)
                {
                    BridgeMod.LogErr($"force_advance_turn fallback failed: {e2}");
                }
            }
        }, "force advance turn");
        return (true, "submitted force_advance_turn");
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
        // AllEnemies / AnyPlayer potions take no creature target — an explicit
        // target_combat_id made EnqueueManualUse a silent no-op (potion not
        // consumed, no effect; observed live with POTION_OF_BINDING). Only
        // AnyEnemy potions resolve a creature target.
        Creature? target = null;
        if (potion.TargetType == TargetType.AnyEnemy)
        {
            if (TryGetInt(args, "target_combat_id", out int targetId))
            {
                target = combat.GetCreature((uint)targetId);
                if (target == null)
                {
                    return (false, $"target combat_id {targetId} not found");
                }
            }
            else
            {
                var hittable = combat.HittableEnemies.ToList();
                target = hittable.Count > 0 ? hittable[0] : null;
            }
        }
        else if (TryGetInt(args, "target_combat_id", out int ignoredTarget))
        {
            BridgeMod.LogInfo($"WARN use_potion: target_combat_id={ignoredTarget} ignored for potion {potion.Id.Entry} target_type={potion.TargetType}");
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
        Fire(async () =>
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

    private static (bool, string) Choose(JsonElement args)
    {
        if (!TryGetInt(args, "index", out int index))
        {
            return (false, "choose requires index");
        }
        IScreenContext? context = ActiveScreenContext.Instance.GetCurrentScreen();
        // Mid-combat choose-a-card overlays (boss Curse of Knowledge, potions)
        // may not be registered as the ActiveScreenContext — fall back to a
        // visible-tree scan so choose works while combat is in progress.
        if (context is NCombatRoom or null || CombatManager.Instance.IsInProgress)
        {
            if (StateBuilder.FindCombatSelectOverlay() is IScreenContext overlayContext)
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
        if (StateBuilder.FindCombatSelectOverlay() is null
            && context is NCombatRoom or null
            && StateBuilder.FindHandSelectMode() is { } handSelect)
        {
            return ToggleHandSelectCard(handSelect, index);
        }
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
                // Index space must match StateBuilder.TreasureOptions: chest (if
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
                Fire(() => UiHelper.Click(chestTarget), "choose chest relic");
                return (true, $"submitted choose chest relic index {index}");
            }
            case NRestSiteRoom restRoom:
                return ClickIndexedButton(restRoom, index, "rest site option");
            case NMerchantRoom shopRoom:
                return ClickIndexedButton(shopRoom, index, "shop item");
            case NCrystalSphereScreen crystalScreen:
            {
                List<NCrystalSphereCell> cells = UiHelper.FindAll<NCrystalSphereCell>(crystalScreen);
                if (index < 0 || index >= cells.Count)
                {
                    return (false, $"index {index} out of range ({cells.Count} crystal cells)");
                }
                NClickableControl cell = cells[index];
                Fire(() => UiHelper.Click(cell), "crystal cell");
                return (true, $"submitted crystal cell {index}");
            }
            default:
            {
                if (context is NChooseACardSelectionScreen or NSimpleCardSelectScreen or NDeckCardSelectScreen
                    or NDeckUpgradeSelectScreen or NDeckTransformSelectScreen or NDeckEnchantSelectScreen
                    or NChooseABundleSelectionScreen or NCombatPileCardSelectScreen)
                {
                    Node screenNode = (Node)context;
                    // Same index space as StateBuilder: deck-select grids are
                    // NGridCardHolder nodes; preview/ghost NCardHolder nodes
                    // must not occupy indices.
                    List<NCardHolder> holders = StateBuilder.SelectableCardHolders(screenNode);
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

    private static (bool, string) Skip()
    {
        // In-hand selection skip: complete with an empty selection (Gambling
        // Chip MinSelect=0 — discard nothing and unblock the turn). Overlay
        // screens outrank a stale hand selection mode (same rule as Choose()).
        if (StateBuilder.FindCombatSelectOverlay() is null
            && StateBuilder.FindHandSelectMode() is { } _)
        {
            return SkipHandSelectEmpty();
        }
        IScreenContext? context = ActiveScreenContext.Instance.GetCurrentScreen();
        if (NModalContainer.Instance?.OpenModal is Node modalNode && ReferenceEquals(context, modalNode))
        {
            List<NButton> buttons = UiHelper.FindAll<NButton>(modalNode);
            NButton? dismiss = buttons.FirstOrDefault(b =>
            {
                string name = b.Name.ToString();
                return b.Visible && (name.Contains("No") || name.Contains("Cancel")
                    || name.Contains("Close") || name.Contains("Dismiss"));
            });
            if (dismiss != null)
            {
                NButton target = dismiss;
                Fire(() => UiHelper.Click(target), "modal dismiss");
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
            Fire(() =>
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
            Fire(() => UiHelper.Click(skipTarget), "skip");
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
            Fire(() => UiHelper.Click(target), "skip by name");
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
                Fire(() => UiHelper.Click(closeTarget), "deck select close");
                return (true, "submitted deck select close (cancel)");
            }
            return (false, "deck select screen has no enabled close/cancel button");
        }
        return (false, $"no skip button on screen {context.GetType().Name}");
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

    // Drives NGameOverScreen back to the main menu using the game's own
    // summary flow: Continue button, then Return-To-Main-Menu button. Both are
    // polled until enabled — takeover must work from any game state.
    // Game-over summary: Continue button, then Return-To-Main-Menu. Nodes can
    // be disposed mid-poll while another path (start_run's own game-over clear)
    // tears the screen down — every node touch is IsInstanceValid-guarded and
    // re-found per step; a disposed Continue means "teardown in progress, skip"
    // (live crash 2026-09-17 run-7: Cannot access a disposed object
    // NGameOverContinueButton — proceed chain threw, state looked frozen).
    private static async Task ClearGameOverScreen(NGameOverScreen screen)
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

    private static (bool, string) ToggleHandSelectCard(NPlayerHand hand, int index)
    {
        if (!TryGetCombatPlayer(out Player? player, out _, out PlayerCombatState? pcs) || pcs == null)
        {
            return (false, "not in an active combat");
        }
        IReadOnlyList<CardModel> cards = pcs.Hand.Cards;
        if (index < 0 || index >= cards.Count)
        {
            return (false, $"index {index} out of range (hand size {cards.Count})");
        }
        CardModel card = cards[index];
        List<CardModel> selected = StateBuilder.GetHandSelectedCards(hand);
        if (selected.Contains(card))
        {
            if (hand.GetCard(card) is not { } cardNode)
            {
                return (false, $"hand card node for index {index} not found");
            }
            Fire(() => { hand.DeselectCard(cardNode); return Task.CompletedTask; }, "hand select deselect");
            return (true, $"hand_select deselected index {index} ({card.Id.Entry})");
        }
        if (hand.GetCardHolder(card) is not NHandCardHolder holder)
        {
            return (false, $"hand holder for index {index} not found");
        }
        bool upgradeMode = hand.CurrentMode == NPlayerHand.Mode.UpgradeSelect;
        Fire(() => { InvokeHandSelectAdd(hand, holder, upgradeMode); return Task.CompletedTask; }, "hand select add");
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
        NPlayerHand? hand = StateBuilder.FindHandSelectMode();
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
        Fire(() => { method.Invoke(hand, new object?[] { null }); return Task.CompletedTask; }, "hand select confirm");
        return (true, "submitted hand_select confirm");
    }

    private static (bool, string) SkipHandSelectEmpty()
    {
        NPlayerHand? hand = StateBuilder.FindHandSelectMode();
        if (hand == null)
        {
            return (false, "not in a hand card-selection mode");
        }
        Fire(() =>
        {
            foreach (CardModel card in StateBuilder.GetHandSelectedCards(hand).ToList())
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

    private static (bool, string) Proceed()
    {
        // In-hand selection confirm — no NProceedButton exists in this mode.
        // Overlay screens (card_choice/deck_select confirm chains) outrank a
        // stale hand selection mode; same priority rule as Choose().
        if (StateBuilder.FindCombatSelectOverlay() is null
            && StateBuilder.FindHandSelectMode() is { } _)
        {
            return ConfirmHandSelect();
        }
        IScreenContext? context = ActiveScreenContext.Instance.GetCurrentScreen();
        // Game-over summary needs the Continue -> ReturnToMainMenu chain, not a
        // proceed button; this is the any-state takeover entry.
        if (context is NGameOverScreen endedScreen)
        {
            Fire(() => ClearGameOverScreen(endedScreen), "game over continue");
            return (true, "submitted game_over continue chain");
        }
        // Modal popups: click the affirmative button (Yes/Confirm/OK/Accept).
        if (NModalContainer.Instance?.OpenModal is Node modalNode && ReferenceEquals(context, modalNode))
        {
            List<NButton> buttons = UiHelper.FindAll<NButton>(modalNode);
            NButton? affirmative = buttons.FirstOrDefault(b =>
            {
                string name = b.Name.ToString();
                return b.Visible && (name.Contains("Yes") || name.Contains("Confirm")
                    || name.Contains("OK") || name.Contains("Accept") || name.Contains("Proceed"));
            });
            affirmative ??= buttons.FirstOrDefault(b => b.Visible);
            if (affirmative != null)
            {
                NButton target = affirmative;
                Fire(() => UiHelper.Click(target), "modal confirm");
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
            Fire(async () =>
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
        NRestSiteButton? chosen = null;
        foreach (NRestSiteButton button in buttons)
        {
            try
            {
                string oid = button.Option.OptionId.ToUpperInvariant();
                bool isSmith = oid.Contains("SMITH") || oid.Contains("UPGRADE") || oid.Contains("MEND");
                if (isSmith == preferSmith)
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
        Fire(async () =>
        {
            // Click the button rather than Option.OnSelect(): the room wires
            // completion callbacks (ShowProceedButton / SetTravelEnabled) only
            // through its own button path; OnSelect alone leaves the room stuck.
            await UiHelper.Click(target);
            BridgeMod.LogInfo($"{label} clicked button ({optionId})");
        }, label);
        return (true, $"submitted {label} ({optionId})");
    }

    private static (bool, string) ShopBuy(JsonElement args)
    {
        NMerchantRoom? room = NMerchantRoom.Instance;
        NMerchantInventory? inventory = room?.Inventory
            ?? (ActiveScreenContext.Instance.GetCurrentScreen() is Node screenNode
                ? UiHelper.FindFirst<NMerchantInventory>(screenNode) : null)
            ?? (NRun.Instance != null ? UiHelper.FindFirst<NMerchantInventory>(NRun.Instance) : null);
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
        string? itemId = GetString(args, "item_id");
        NMerchantSlot? slot = null;
        if (!string.IsNullOrEmpty(itemId))
        {
            foreach (NMerchantSlot candidate in slots)
            {
                MerchantEntry? e = candidate.Entry;
                object probe = e is MerchantCardEntry { CreationResult: { } creation } ? creation : e!;
                string id = StateBuilder.ProbeModelId(probe) ?? e!.GetType().Name;
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
        else if (TryGetInt(args, "index", out int index))
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
        Fire(async () =>
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
        return (true, $"submitted shop_buy {itemId ?? $"index"} cost={entry.Cost}");
    }

    private static (bool, string) ShopLeave()
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
        Fire(async () =>
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

    private static (bool, string) ContinueRun()
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
        Fire(() => UiHelper.Click(target), "continue run");
        return (true, "submitted continue_run");
    }

    private static (bool, string) StartRun(JsonElement args)
    {
        string? character = GetString(args, "character");
        string? seed = GetString(args, "seed");
        Fire(() => StartRunSequence(character, seed), "start run");
        return (true, $"submitted start_run (character={character ?? "random"}, seed={seed ?? "random"})");
    }

    // Mirrors the game's own AutoSlay menu path (AutoSlayer.PlayMainMenuAsync).
    // Takeover-safe: clears game-over screens first so start_run works from any
    // game state (startup, mid-run, or ended).
    private static async Task StartRunSequence(string? character, string? seed)
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
        EnsureNeowEpochRevealed();
        Control mainMenu = await WaitHelper.ForNode<Control>(root, "/root/Game/RootSceneContainer/MainMenu", default, TimeSpan.FromSeconds(30));
        // Simulate the normal play loop's Timeline visits: earned-but-unrevealed
        // Epochs are revealed through the game's own inspect/unlock UI so
        // QueueUnlocks side effects (character unlocks, timeline expansions,
        // pending unlock flags) fire exactly as they do for manual play.
        await VisitTimelineAndReveal(mainMenu);
        // Boon-room guarantee fallback: if Neow still is not Revealed after the
        // native Timeline flow (UI drift, unexpected slot state), force it the
        // old way so Act-start boon rooms never silently vanish.
        FallbackRevealNeowForBoonRoom();
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
        chosen.Select();
        await Task.Delay(200, default);
        NButton confirm = await WaitHelper.ForNode<NButton>(selectScreen, "ConfirmButton", default, TimeSpan.FromSeconds(10));
        await UiHelper.Click(confirm);
        BridgeMod.LogInfo($"start_run: embarked as {chosen.Name} char_entry={SafeCharEntry(chosen)} (seed={seed ?? "random"})");
    }

    private static string SafeCharEntry(NCharacterSelectButton b)
    {
        try { return b.Character?.Id.Entry ?? ""; }
        catch { return ""; }
    }

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
    // Not a currency/meta purchase — the Neow epoch is the profile's intended
    // first Timeline slot; nothing unearned is granted.
    private static void EnsureNeowEpochRevealed()
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
    private static void FallbackRevealNeowForBoonRoom()
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
    private static (bool, string) TimelineSync()
    {
        Fire(async () =>
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
    private static async Task VisitTimelineAndReveal(Control mainMenu)
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
