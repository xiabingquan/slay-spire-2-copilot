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

// Combat-phase action executors: card play (fail-loud targeting gates), end
// turn (sync-queue / empty-hand paths), forced combat end/advance, potions.
public static class CombatActions
{
    internal static (bool, string) Play(JsonElement args)
    {
        if (!ActionExecutor.TryGetInt(args, "card_index", out int cardIndex))
        {
            return (false, "play requires card_index");
        }
        if (!ActionExecutor.TryGetCombatPlayer(out Player? player, out CombatState combat, out PlayerCombatState? pcs) || pcs == null)
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
        // Parity gate (user report 2026-09-17, run-12): CardCmd.AutoPlay builds
        // ResourceInfo { EnergySpent = 0 } and calls OnPlayWrapper(isAutoPlay:
        // true) — it never runs CanPlay or SpendResources, so every bridge play
        // was FREE energy/stars (observed live: 5-6 one-cost cards per turn at
        // a displayed 3/3). The game's honest player path is PlayCardAction
        // (CanPlay -> SpendResources -> OnPlayWrapper isAutoPlay:false); the
        // mod now enqueues that action and pre-checks CanPlay so the client
        // gets a real rejection instead of a silent free play.
        if (!card.CanPlay(out UnplayableReason unplayableReason, out AbstractModel? preventer))
        {
            return (false, $"card not playable ({unplayableReason}"
                + (preventer != null ? $" via {preventer.GetType().Name}" : "") + ")");
        }
        Creature? target = null;
        // Targeting is strict: never fall back to hittable[0]. An explicit but
        // unparseable target must error out loud, and AnyEnemy/AnyAlly plays
        // must carry target_combat_id — silent mis-targeting hid a whole run's
        // worth of wrong hits behind `target:"id1"` strings that TryGetInt
        // never parsed.
        if (args.TryGetProperty("target", out JsonElement rawTarget))
        {
            return (false, $"unsupported target arg {rawTarget.GetRawText()} — "
                + "pass target_combat_id=<int> from state combat ids");
        }
        if (ActionExecutor.TryGetInt(args, "target_combat_id", out int targetId))
        {
            // Live-observed 2026-09-17 (A1 run-14): Self/Skill cards passed a
            // creature target enqueue PlayCardAction that the game silently
            // no-ops (card stays in hand, energy/HP unchanged) — Defend and
            // Bloodletting plays were lost mid-boss-fight this way. Fail loud
            // instead: only AnyEnemy/AnyAlly/AnyPlayer consume an explicit
            // target; Self/AllEnemies/RandomEnemy/etc. must omit the arg.
            if (card.TargetType is not (TargetType.AnyEnemy or TargetType.AnyAlly or TargetType.AnyPlayer))
            {
                return (false, $"card {card.Id.Entry} target_type={card.TargetType} — "
                    + "omit target_combat_id (only AnyEnemy/AnyAlly/AnyPlayer take an explicit "
                    + "target; passing one to self/aoe/random cards no-ops in PlayCardAction)");
            }
            target = combat.GetCreature((uint)targetId);
            if (target == null)
            {
                return (false, $"target_combat_id {targetId} not found in combat");
            }
            // Faction gate (live-observed 2026-09-17 A1 run-18): the TargetType
            // enum gate alone still let Self/AllEnemies-class cards through on
            // some builds (DEFEND/THUNDERCLAP plays returned ok=true, echoed
            // "-> enemy name", and silently no-op'd — energy and block both
            // unchanged). The game's PlayCardAction drops a mismatched faction
            // target without resolving the card. Fail loud on faction too:
            // enemy-targeted cards must resolve to a non-ally; player/ally-
            // targeted cards must resolve to an ally (the player).
            bool targetIsAlly = combat.Allies != null
                && combat.Allies.Any(a => a != null && a.CombatId == target.CombatId);
            if (card.TargetType == TargetType.AnyEnemy && targetIsAlly)
            {
                return (false, $"card {card.Id.Entry} target_type=AnyEnemy — "
                    + $"target_combat_id {targetId} resolves to an ally; pick an enemy id");
            }
            if (card.TargetType is (TargetType.AnyAlly or TargetType.AnyPlayer) && !targetIsAlly)
            {
                return (false, $"card {card.Id.Entry} target_type={card.TargetType} — "
                    + $"target_combat_id {targetId} resolves to an enemy; self/ally cards "
                    + "must omit the arg or target an ally id (mismatch silently no-ops)");
            }
        }
        else if (card.TargetType is TargetType.AnyEnemy or TargetType.AnyAlly or TargetType.AnyPlayer)
        {
            return (false, $"card {card.Id.Entry} needs a target — pass "
                + "target_combat_id=<int> (no auto-target fallback)");
        }
        CardModel cardRef = card;
        Creature? targetRef = target;
        ActionExecutor.Fire(() =>
        {
            RunManager.Instance.ActionQueueSynchronizer.RequestEnqueue(
                new PlayCardAction(cardRef, targetRef));
            return Task.CompletedTask;
        }, "play card (PlayCardAction)");
        return (true, $"submitted play {card.Id.Entry} -> {(target?.Name ?? "none")} (energy-checked)");
    }

    internal static (bool, string) EndTurn()
    {
        if (!ActionExecutor.TryGetCombatPlayer(out Player? player, out CombatState combat, out PlayerCombatState? pcs) || pcs == null)
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
            ActionExecutor.Fire(ForceCombatEndAsync, "combat win-condition end");
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
        ActionExecutor.Fire(async () =>
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

    internal static async Task ForceCombatEndAsync()
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

    internal static (bool, string) ForceCombatEnd()
    {
        if (!ActionExecutor.TryGetCombatPlayer(out _, out _, out _))
        {
            return (false, "not in an active combat");
        }
        ActionExecutor.Fire(ForceCombatEndAsync, "force combat end");
        return (true, "submitted force_combat_end");
    }

    // Lock-style debuffs can freeze end_turn (fingerprint stuck, abandon no-ops).
    // Remove those powers via Creature.RemovePowerInternal, then re-drive the
    // sync end-turn path.
    internal static (bool, string) ForceAdvanceTurn()
    {
        if (!ActionExecutor.TryGetCombatPlayer(out Player? player, out CombatState combat, out PlayerCombatState? pcs) || pcs == null)
        {
            return (false, "not in an active combat");
        }
        Player playerRef = player!;
        int turnNumber = pcs.TurnNumber;
        ActionExecutor.Fire(async () =>
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

    internal static (bool, string) UsePotion(JsonElement args)
    {
        if (!ActionExecutor.TryGetInt(args, "potion_index", out int potionIndex))
        {
            return (false, "use_potion requires potion_index");
        }
        if (!ActionExecutor.TryGetCombatPlayer(out Player? player, out CombatState combat, out _))
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
            if (ActionExecutor.TryGetInt(args, "target_combat_id", out int targetId))
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
        else if (ActionExecutor.TryGetInt(args, "target_combat_id", out int ignoredTarget))
        {
            BridgeMod.LogInfo($"WARN use_potion: target_combat_id={ignoredTarget} ignored for potion {potion.Id.Entry} target_type={potion.TargetType}");
        }
        Creature? targetRef = target;
        ActionExecutor.Fire(() => { potion.EnqueueManualUse(targetRef); return Task.CompletedTask; }, "use potion");
        return (true, $"submitted use_potion {potion.Id.Entry}");
    }
}
