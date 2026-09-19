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

// Card-reward choose verification: resolve the pending press against the live
// deck delta so an unverified reward pick surfaces as incomplete info instead
// of silently trusting the printed option order.
public static class ChooseVerify
{
    internal static List<string> DeckTupleSnapshot(Player? player, RunState? runState)
    {
        var tuples = new List<string>();
        if (player == null || runState == null)
        {
            InfoCompleteness.FlagDuringAction("deck snapshot unavailable (player/runState null) — choose verification impossible");
            return tuples;
        }
        foreach (Dictionary<string, object?> row in RunDto.SafeDeck(player, runState))
        {
            string id = row.TryGetValue("id", out object? v) ? v?.ToString() ?? "?" : "?";
            bool upgraded = row.TryGetValue("upgraded", out object? u) && u is true;
            tuples.Add(upgraded ? id + "+" : id);
        }
        return tuples;
    }

    internal static void Attach(
        Dictionary<string, object?> state, string screen, Player? player, RunState? runState)
    {
        if (BridgeMod.CardRewardVerifyPending is not { } pending)
        {
            return;
        }
        List<string> deckNow = DeckTupleSnapshot(player, runState);
        if (screen == "card_reward")
        {
            pending.BuildsOnScreen++;
            state["last_choose_verification"] = new Dictionary<string, object?>
            {
                ["requested_index"] = pending.Index,
                ["requested_option_id"] = pending.RequestedId,
                ["verify"] = "pending",
                ["builds_on_screen"] = pending.BuildsOnScreen,
            };
            return;
        }
        // Screen moved on: the press must now be explainable by a clean deck delta.
        var gained = deckNow.Except(pending.DeckBefore).ToList();
        var lost = pending.DeckBefore.Except(deckNow).ToList();
        var resolved = new Dictionary<string, object?>
        {
            ["requested_index"] = pending.Index,
            ["requested_option_id"] = pending.RequestedId,
            ["deck_delta_gained"] = gained,
            ["deck_delta_lost"] = lost,
        };
        if (gained.Count == 1 && lost.Count == 0)
        {
            resolved["verify"] = "applied";
            resolved["applied"] = gained[0];
            resolved["applied_matches_request"] =
                gained[0].StartsWith(pending.RequestedId, StringComparison.Ordinal);
        }
        else if (gained.Count == 1 && lost.Count == 1 && gained[0].StartsWith(lost[0].TrimEnd('+'), StringComparison.Ordinal))
        {
            // same-card upgrade path (e.g. PERFECTED_STRIKE -> PERFECTED_STRIKE+)
            resolved["verify"] = "applied_upgrade";
            resolved["applied"] = gained[0];
            resolved["applied_matches_request"] =
                gained[0].StartsWith(pending.RequestedId, StringComparison.Ordinal);
        }
        else
        {
            resolved["verify"] = "unresolved";
            resolved["applied"] = null;
            InfoCompleteness.FlagDuringBuild(
                $"card_reward choose verification unresolved: index={pending.Index} requested={pending.RequestedId} " +
                $"gained=[{string.Join(",", gained)}] lost=[{string.Join(",", lost)}] — applied card unverified");
        }
        state["last_choose_verification"] = resolved;
        BridgeMod.CardRewardVerifyPending = null;
    }
}
