using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using Godot;
using MegaCrit.Sts2.Core.AutoSlay.Helpers;
using MegaCrit.Sts2.Core.Combat;
using MegaCrit.Sts2.Core.Context;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Merchant;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Events;
using MegaCrit.Sts2.Core.Localization;
using MegaCrit.Sts2.Core.Map;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.MonsterMoves.Intents;
using MegaCrit.Sts2.Core.MonsterMoves.MonsterMoveStateMachine;
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
using MegaCrit.Sts2.Core.Nodes.Screens.TreasureRoomRelic;
using MegaCrit.Sts2.Core.Runs;


namespace SpireCopilot.Bridge;

// Combat-scoped state DTOs: creatures, powers, hand/piles, intents, and the
// full monster move-state-machine graph. Reflection probes here are read-only
// — never call rng-consuming RollMove/GetNextState paths.
public static class CombatDto
{
    // RandomBranchState.GetStateWeight(StateWeight, Creature) — private static;
    // applies UseOnlyOnce/CannotRepeat/CanRepeatXTimes/cooldown gating against
    // StateLog. Read-only evaluation; NEVER call rng-consuming RollMove/
    // GetNextState paths (they would desync live monster AI rolls).
    // decomp: MegaCrit.Sts2.Core.MonsterMoves.MonsterMoveStateMachine/RandomBranchState.cs:130
    private static readonly MethodInfo? BranchGetStateWeightMethod =
        typeof(MegaCrit.Sts2.Core.MonsterMoves.MonsterMoveStateMachine.RandomBranchState)
            .GetMethod("GetStateWeight", BindingFlags.Static | BindingFlags.NonPublic);

    // ConditionalBranchState.States — private List<ConditionalBranch>;
    // ConditionalBranch is a private nested struct with public readonly id and
    // public float Evaluate().
    private static readonly FieldInfo? ConditionalBranchStatesField =
        typeof(MegaCrit.Sts2.Core.MonsterMoves.MonsterMoveStateMachine.ConditionalBranchState)
            .GetField("States", BindingFlags.Instance | BindingFlags.NonPublic);

    // AbstractIntent.GetIntentDescription(IEnumerable<Creature>, Creature) —
    // protected virtual; SmartFormat loc resolution can throw, so each call is
    // wrapped and a failure omits the field.
    private static readonly Dictionary<Type, MethodInfo?> IntentDescriptionMethods = new();

    private static MethodInfo? GetIntentDescriptionMethod(Type intentType)
    {
        if (IntentDescriptionMethods.TryGetValue(intentType, out MethodInfo? cached))
        {
            return cached;
        }
        MethodInfo? method = null;
        try
        {
            method = intentType.GetMethod(
                "GetIntentDescription",
                BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic,
                binder: null,
                types: new[] { typeof(IEnumerable<Creature>), typeof(Creature) },
                modifiers: null);
        }
        catch (Exception)
        {
            method = null;
        }
        IntentDescriptionMethods[intentType] = method;
        return method;
    }

    internal static Dictionary<string, object?>? BuildCombat(CombatState combat, Player? player)
    {
        PlayerCombatState? pcs = player?.PlayerCombatState;
        var creatures = new List<Dictionary<string, object?>>();
        foreach (Creature creature in combat.Allies.Concat(combat.Enemies))
        {
            creatures.Add(CreatureDto(creature));
        }
        var piles = new Dictionary<string, object?>();
        if (pcs != null)
        {
            var hand = new List<Dictionary<string, object?>>();
            IReadOnlyList<CardModel> cards = pcs.Hand.Cards;
            for (int i = 0; i < cards.Count; i++)
            {
                hand.Add(CardDto(cards[i], i, player));
            }
            piles["hand"] = hand;
            piles["draw_count"] = pcs.DrawPile.Cards.Count;
            piles["discard_count"] = pcs.DiscardPile.Cards.Count;
            piles["exhaust_count"] = pcs.ExhaustPile.Cards.Count;
            // Id-only pile arrays — full card semantics via lookup; "+" marks
            // upgraded copies. ~400B per pile, not CardDto.
            try { piles["draw_card_ids"] = CardPileIdList(pcs.DrawPile); } catch (Exception) { /* omit */ }
            try { piles["discard_card_ids"] = CardPileIdList(pcs.DiscardPile); } catch (Exception) { /* omit */ }
            try { piles["exhaust_card_ids"] = CardPileIdList(pcs.ExhaustPile); } catch (Exception) { /* omit */ }
            try
            {
                piles["play_count"] = pcs.PlayPile.Cards.Count;
                piles["play_card_ids"] = CardPileIdList(pcs.PlayPile);
            }
            catch (Exception) { /* omit */ }
        }
        var dto = new Dictionary<string, object?>
        {
            ["round"] = combat.RoundNumber,
            ["current_side"] = combat.CurrentSide.ToString(),
            ["turn_phase"] = pcs?.Phase.ToString() ?? "None",
            ["turn_number"] = pcs?.TurnNumber,
            ["energy"] = pcs?.Energy,
            ["max_energy"] = SafeMaxEnergy(pcs),
            ["creatures"] = creatures,
            ["piles"] = piles,
        };
        try
        {
            if (combat.Encounter is { } encounter)
            {
                dto["encounter_id"] = encounter.Id.Entry;
                dto["should_give_rewards"] = encounter.ShouldGiveRewards;
                dto["min_gold_reward"] = encounter.MinGoldReward;
                dto["max_gold_reward"] = encounter.MaxGoldReward;
            }
        }
        catch (Exception) { /* encounter unavailable */ }
        try
        {
            dto["hittable_enemy_combat_ids"] = combat.HittableEnemies.Select(c => c.CombatId).ToList();
        }
        catch (Exception) { /* omit */ }
        try
        {
            dto["escaped_creature_combat_ids"] = combat.EscapedCreatures.Select(c => c.CombatId).ToList();
        }
        catch (Exception) { /* omit */ }
        // Combat history — last 10 entries, excluded from fingerprint inputs.
        try
        {
            var all = CombatManager.Instance.History.Entries.ToList();
            List<Dictionary<string, object?>> history = all
                .Skip(Math.Max(0, all.Count - 10))
                .Select(e =>
                {
                    var h = new Dictionary<string, object?> { ["kind"] = e.GetType().Name };
                    try { h["text"] = e.HumanReadableString; } catch (Exception) { /* omit text */ }
                    return h;
                })
                .ToList();
            dto["history"] = history;
        }
        catch (Exception) { /* history unavailable */ }
        return dto;
    }

    private static List<string> CardPileIdList(CardPile? pile)
    {
        var ids = new List<string>();
        if (pile == null)
        {
            return ids;
        }
        foreach (CardModel card in pile.Cards)
        {
            try
            {
                bool upgraded = GameProbe.ProbeBool(card, "IsUpgraded", "Upgraded") is true;
                ids.Add(upgraded ? card.Id.Entry + "+" : card.Id.Entry);
            }
            catch (Exception)
            {
                try { ids.Add(card.Id.Entry); } catch (Exception) { /* skip card */ }
            }
        }
        return ids;
    }

    private static object? SafeMaxEnergy(PlayerCombatState? pcs)
    {
        try
        {
            return pcs?.MaxEnergy;
        }
        catch (Exception)
        {
            return null;
        }
    }

    private static Dictionary<string, object?> CreatureDto(Creature creature)
    {
        var dto = new Dictionary<string, object?>
        {
            ["combat_id"] = creature.CombatId,
            ["side"] = creature.Side.ToString(),
            ["is_player"] = creature.IsPlayer,
            ["name"] = creature.Name,
            ["hp"] = creature.CurrentHp,
            ["max_hp"] = creature.MaxHp,
            ["block"] = creature.Block,
            ["is_alive"] = creature.IsAlive,
            ["is_hittable"] = SafeIsHittable(creature),
            ["powers"] = creature.Powers.Select(PowerDto).ToList(),
        };
        try { dto["model_id"] = creature.ModelId.Entry; } catch (Exception) { /* omit */ }
        try { dto["slot_name"] = creature.SlotName; } catch (Exception) { /* omit */ }
        try { dto["is_primary_enemy"] = creature.IsPrimaryEnemy; } catch (Exception) { /* omit */ }
        try { dto["is_secondary_enemy"] = creature.IsSecondaryEnemy; } catch (Exception) { /* omit */ }
        try { dto["is_stunned"] = creature.IsStunned; } catch (Exception) { /* omit */ }
        if (creature.Monster is { } monster)
        {
            dto["move_id"] = SafeMoveId(monster);
            dto["intents"] = BuildIntents(monster, creature);
            if (creature.IsAlive)
            {
                try
                {
                    Dictionary<string, object?>? graph = MoveGraphDto(monster, creature);
                    if (graph != null)
                    {
                        dto["move_graph"] = graph;
                    }
                }
                catch (Exception)
                {
                    // move graph unavailable — state build must not fail
                }
            }
        }
        return dto;
    }

    private static object? SafeIsHittable(Creature creature)
    {
        try
        {
            return creature.IsHittable;
        }
        catch (Exception)
        {
            return null;
        }
    }

    internal static string? SafeMoveId(MonsterModel monster)
    {
        try
        {
            return monster.NextMove?.Id;
        }
        catch (Exception)
        {
            return null;
        }
    }

    // Loc tables leak raw keys like "intents:FORMAT_EMPTY" for buff/debuff
    // intents — replace those segments with the intent type so the client can
    // act on them without a --json dive.
    private static string CleanIntentLabel(string? label, AbstractIntent intent)
    {
        string fallback = intent.IntentType.ToString();
        if (string.IsNullOrEmpty(label))
        {
            return fallback;
        }
        if (!label.Contains("FORMAT_EMPTY") && !label.Contains("intents:"))
        {
            return label;
        }
        string cleaned = label.Replace("intents:FORMAT_EMPTY", fallback).Replace("FORMAT_EMPTY", fallback);
        return string.IsNullOrWhiteSpace(cleaned) ? fallback : cleaned.Trim(';', ' ');
    }

    // Typed intent DTO. Member names verified against decomp
    // (/tmp/sts2-decomp/MegaCrit.Sts2.Core.MonsterMoves.Intents/*):
    // AttackIntent.DamageCalc (Func<decimal>?), .Repeats (virtual int),
    // GetSingleDamage/.GetTotalDamage (public, run the live damage hooks),
    // StatusIntent.CardCount (public int),
    // AbstractIntent.GetIntentDescription (protected virtual — cached reflection).
    private static Dictionary<string, object?> IntentDto(AbstractIntent intent, Creature owner)
    {
        var dto = new Dictionary<string, object?>
        {
            ["type"] = intent.IntentType.ToString(),
            ["class"] = intent.GetType().Name,
        };
        try
        {
            dto["label"] = CleanIntentLabel(GameProbe.ResolveLoc(intent.GetIntentLabel(Array.Empty<Creature>(), owner)), intent);
        }
        catch (Exception)
        {
            dto["label"] = intent.IntentType.ToString();
        }
        if (intent is AttackIntent attack)
        {
            try { dto["damage"] = attack.GetSingleDamage(Array.Empty<Creature>(), owner); } catch (Exception) { /* omit */ }
            try { dto["total_damage"] = attack.GetTotalDamage(Array.Empty<Creature>(), owner); } catch (Exception) { /* omit */ }
            try { dto["hits"] = attack.Repeats; } catch (Exception) { /* omit */ }
            try
            {
                if (attack.DamageCalc?.Invoke() is { } baseDmg)
                {
                    dto["base_damage"] = (int)baseDmg;
                }
            }
            catch (Exception) { /* omit */ }
        }
        if (intent is StatusIntent status)
        {
            try { dto["card_count"] = status.CardCount; } catch (Exception) { /* omit */ }
        }
        try
        {
            MethodInfo? descMethod = GetIntentDescriptionMethod(intent.GetType());
            if (descMethod != null
                && descMethod.Invoke(intent, new object[] { Array.Empty<Creature>(), owner }) is MegaCrit.Sts2.Core.Localization.LocString loc)
            {
                string? text = GameProbe.ResolveLoc(loc);
                if (!string.IsNullOrWhiteSpace(text))
                {
                    dto["description"] = GameProbe.StripBbcode(text);
                }
            }
        }
        catch (Exception)
        {
            // description loc can fail on incomplete SmartFormat vars — omit
        }
        return dto;
    }

    private static List<Dictionary<string, object?>> BuildIntents(MonsterModel monster, Creature owner)
    {
        var intents = new List<Dictionary<string, object?>>();
        try
        {
            MoveState? move = monster.NextMove;
            if (move?.Intents == null)
            {
                return intents;
            }
            foreach (AbstractIntent intent in move.Intents)
            {
                try
                {
                    intents.Add(IntentDto(intent, owner));
                }
                catch (Exception)
                {
                    // single intent failure must not drop the whole list
                }
            }
        }
        catch (Exception)
        {
            // intent enumeration failed; move state may be transitioning
        }
        return intents;
    }

    // Full move-state-machine graph per alive monster: every move with its
    // intents, linear follow-ups, branch weights, and the performed-move log.
    // Read-only — never calls RollMove/GetNextState with live RNG.
    private static Dictionary<string, object?>? MoveGraphDto(MonsterModel monster, Creature owner)
    {
        MonsterMoveStateMachine? machine = monster.MoveStateMachine;
        if (machine == null)
        {
            // No fallback: the player can always read the enemy's move cycle
            // in-game — an unreadable state machine is incomplete information.
            InfoCompleteness.FlagDuringBuild(
                $"monster '{monster.Id.Entry}': move_graph unavailable (MoveStateMachine unreadable)");
            return null;
        }
        var graph = new Dictionary<string, object?>
        {
            ["current_move_id"] = SafeMoveId(monster),
        };
        try
        {
            List<string> log = machine.StateLog
                .Select(s => s.Id)
                .Where(id => !string.IsNullOrEmpty(id))
                .ToList();
            if (log.Count > 12)
            {
                log = log.Skip(log.Count - 12).ToList();
            }
            graph["state_log"] = log;
        }
        catch (Exception)
        {
            graph["state_log"] = new List<string>();
        }
        var states = new List<Dictionary<string, object?>>();
        string? currentId = SafeMoveId(monster);
        try
        {
            foreach (MonsterState state in machine.States.Values)
            {
                try
                {
                    states.Add(StateDto(state, owner, currentId));
                }
                catch (Exception e)
                {
                    // Per-state failure: keep the stub AND flag it — a stub
                    // without data is uncertainty, not information.
                    InfoCompleteness.FlagDuringBuild(
                        $"monster '{monster.Id.Entry}' move '{state.Id}': state serialization failed ({e.GetType().Name})");
                    try
                    {
                        states.Add(new Dictionary<string, object?> { ["id"] = state.Id, ["kind"] = "other", ["incomplete"] = true });
                    }
                    catch (Exception) { /* omit */ }
                }
            }
        }
        catch (Exception e)
        {
            InfoCompleteness.FlagDuringBuild(
                $"monster '{monster.Id.Entry}': move_graph states enumeration failed ({e.GetType().Name})");
        }
        graph["states"] = states;
        return graph;
    }

    private static Dictionary<string, object?> StateDto(MonsterState state, Creature owner, string? currentId)
    {
        if (state is MoveState move)
        {
            bool isCurrent = move.Id == currentId;
            var dto = new Dictionary<string, object?>
            {
                ["id"] = move.Id,
                ["kind"] = "move",
                ["is_current"] = isCurrent,
            };
            try { dto["must_perform_once"] = move.MustPerformOnceBeforeTransitioning; } catch (Exception) { /* omit */ }
            try
            {
                string? followUp = null;
                try { followUp = move.FollowUpState?.Id; } catch (Exception) { /* fall through */ }
                followUp ??= move.FollowUpStateId;
                if (!string.IsNullOrEmpty(followUp))
                {
                    dto["follow_up_id"] = followUp;
                }
            }
            catch (Exception) { /* omit */ }
            try
            {
                if (move.Intents != null)
                {
                    var intents = new List<Dictionary<string, object?>>();
                    foreach (AbstractIntent intent in move.Intents)
                    {
                        try
                        {
                            Dictionary<string, object?> idto = IntentDto(intent, owner);
                            // Payload budget: non-current moves keep the math
                            // (damage/hits/base/total) but drop prose fields.
                            if (!isCurrent)
                            {
                                idto.Remove("description");
                                idto.Remove("label");
                            }
                            intents.Add(idto);
                        }
                        catch (Exception) { /* omit one */ }
                    }
                    dto["intents"] = intents;
                }
            }
            catch (Exception) { /* omit */ }
            return dto;
        }
        if (state is RandomBranchState branch)
        {
            var dto = new Dictionary<string, object?>
            {
                ["id"] = branch.Id,
                ["kind"] = "random_branch",
            };
            var branches = new List<Dictionary<string, object?>>();
            try
            {
                foreach (RandomBranchState.StateWeight sw in branch.States)
                {
                    var b = new Dictionary<string, object?>
                    {
                        ["state_id"] = sw.stateId,
                        ["cooldown"] = sw.cooldown,
                        ["repeat_type"] = sw.repeatType.ToString(),
                        ["max_times"] = sw.maxTimes,
                    };
                    try
                    {
                        if (sw.weightLambda?.Invoke() is { } w)
                        {
                            b["weight"] = w;
                        }
                    }
                    catch (Exception) { /* weight lambda unavailable */ }
                    try
                    {
                        if (BranchGetStateWeightMethod != null
                            && BranchGetStateWeightMethod.Invoke(null, new object[] { sw, owner }) is float ew)
                        {
                            b["effective_weight"] = ew;
                        }
                    }
                    catch (Exception)
                    {
                        // gate evaluation unavailable — fall back to raw weight
                        if (!b.ContainsKey("weight"))
                        {
                            try { b["effective_weight"] = sw.GetWeight(); } catch (Exception) { /* omit */ }
                        }
                    }
                    branches.Add(b);
                }
            }
            catch (Exception) { /* branch list unavailable */ }
            dto["branches"] = branches;
            return dto;
        }
        if (state is ConditionalBranchState conditional)
        {
            var dto = new Dictionary<string, object?>
            {
                ["id"] = conditional.Id,
                ["kind"] = "conditional_branch",
            };
            var branches = new List<Dictionary<string, object?>>();
            static void CollectBranchElements(System.Collections.IEnumerable raw, List<Dictionary<string, object?>> branches)
            {
                foreach (object? element in raw)
                {
                    if (element == null)
                    {
                        continue;
                    }
                    Type elementType = element.GetType();
                    var b = new Dictionary<string, object?>();
                    try
                    {
                        FieldInfo? idField = elementType.GetField("id", BindingFlags.Instance | BindingFlags.Public)
                            ?? elementType.GetField("Id", BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic);
                        if (idField?.GetValue(element) is string bid)
                        {
                            b["state_id"] = bid;
                        }
                    }
                    catch (Exception) { /* omit */ }
                    try
                    {
                        MethodInfo? evaluate = elementType.GetMethod("Evaluate", BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic);
                        if (evaluate?.Invoke(element, null) is float score)
                        {
                            b["condition_met"] = score > 0f;
                        }
                    }
                    catch (Exception) { /* omit rather than guess */ }
                    if (b.Count > 0)
                    {
                        branches.Add(b);
                    }
                }
            }
            try
            {
                if (ConditionalBranchStatesField?.GetValue(conditional) is System.Collections.IEnumerable raw)
                {
                    CollectBranchElements(raw, branches);
                }
            }
            catch (Exception e)
            {
                InfoCompleteness.FlagDuringBuild(
                    $"monster move '{conditional.Id}': conditional branch reflection failed ({e.GetType().Name})");
            }
            // Fallback scan: some ConditionalBranchState instances (observed on
            // Bowlbug-class POST_HEADBUTT / SNORE_NEXT) read empty from the
            // declared States field. Walk instance fields up the inheritance
            // chain for any IEnumerable whose elements expose an id + Evaluate
            // pair before concluding the table is unavailable.
            if (branches.Count == 0)
            {
                try
                {
                    for (Type? t = conditional.GetType(); t != null && t != typeof(object); t = t.BaseType)
                    {
                        foreach (FieldInfo fi in t.GetFields(BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.DeclaredOnly))
                        {
                            object? val;
                            try { val = fi.GetValue(conditional); } catch (Exception) { continue; }
                            if (val is not System.Collections.IEnumerable scanRaw || val is string)
                            {
                                continue;
                            }
                            var collected = new List<Dictionary<string, object?>>();
                            try { CollectBranchElements(scanRaw, collected); } catch (Exception) { continue; }
                            if (collected.Count > 0)
                            {
                                branches.AddRange(collected);
                                dto["branch_source"] = $"fallback_field:{fi.Name}";
                                break;
                            }
                        }
                        if (branches.Count > 0)
                        {
                            break;
                        }
                    }
                }
                catch (Exception) { /* fallback scan is best-effort */ }
            }
            if (branches.Count == 0)
            {
                // Predictive branch tables are planning aids, not per-turn
                // authority — the live move id + intent bits (always present
                // in the monster dto) are what combat decisions run on.
                // An empty table after both reflection passes is annotated,
                // not hard-stopped; missing CURRENT move/intent still stops.
                dto["branch_table"] = "reflection_empty";
            }
            dto["branches"] = branches;
            dto["incomplete"] = false;
            return dto;
        }
        return new Dictionary<string, object?>
        {
            ["id"] = state.Id,
            ["kind"] = "other",
            ["incomplete"] = true,
        };
    }

    private static Dictionary<string, object?> PowerDto(PowerModel power)
    {
        var dto = new Dictionary<string, object?>
        {
            ["id"] = power.Id.Entry,
            ["name"] = GameProbe.ModelName(power),
        };
        try { dto["amount"] = power.Amount; } catch (Exception) { /* omit */ }
        try { dto["type"] = power.Type.ToString(); } catch (Exception) { /* omit */ }
        try { dto["stack_type"] = power.StackType.ToString(); } catch (Exception) { /* omit */ }
        try { dto["is_visible"] = power.IsVisible; } catch (Exception) { /* omit */ }
        try
        {
            if (power.Applier is { } applier)
            {
                dto["applier_combat_id"] = applier.CombatId;
                dto["applier_name"] = applier.Name;
            }
        }
        catch (Exception) { /* omit */ }
        return dto;
    }

    internal static Dictionary<string, object?> CardDto(CardModel card, int index, Player? player)
    {
        bool canPlay = false;
        string? reason = null;
        try
        {
            canPlay = card.CanPlay();
        }
        catch (Exception)
        {
            // CanPlay consults hooks that may throw mid-transition
        }
        if (!canPlay && player?.PlayerCombatState != null)
        {
            try
            {
                player.PlayerCombatState.HasEnoughResourcesFor(card, out UnplayableReason r);
                if (r != UnplayableReason.None)
                {
                    reason = r.ToString();
                }
            }
            catch (Exception)
            {
                // cost evaluation unavailable
            }
        }
        object? cost = null;
        try
        {
            cost = card.EnergyCost.GetWithModifiers(CostModifiers.All);
        }
        catch (Exception)
        {
            // cost modifiers not resolvable outside combat
        }
        return new Dictionary<string, object?>
        {
            ["index"] = index,
            ["id"] = card.Id.Entry,
            ["name"] = GameProbe.ModelName(card),
            ["cost"] = cost,
            ["target_type"] = card.TargetType.ToString(),
            ["can_play"] = canPlay,
            ["unplayable_reason"] = reason,
            ["upgraded"] = GameProbe.ProbeBool(card, "IsUpgraded", "Upgraded"),
        };
    }
}
