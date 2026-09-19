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

// available_actions: per-screen legal action list derived from the same
// option index spaces that screen_detail publishes.
public static class AvailableActions
{
    internal static List<Dictionary<string, object?>> Build(
        string screen, CombatState? combat, Player? player, RunState? runState,
        List<Dictionary<string, object?>> screenOptions)
    {
        var actions = new List<Dictionary<string, object?>>();
        switch (screen)
        {
            case "combat":
            {
                PlayerCombatState? pcs = player?.PlayerCombatState;
                if (pcs?.Phase == PlayerTurnPhase.Play)
                {
                    for (int i = 0; i < pcs.Hand.Cards.Count; i++)
                    {
                        actions.Add(new Dictionary<string, object?>
                        {
                            ["action"] = "play",
                            ["args"] = new Dictionary<string, object?> { ["card_index"] = i },
                        });
                    }
                    actions.Add(new Dictionary<string, object?> { ["action"] = "end_turn", ["args"] = new Dictionary<string, object?>() });
                }
                if (player != null && player.Potions.Any())
                {
                    for (int i = 0; i < player.PotionSlots.Count; i++)
                    {
                        if (player.PotionSlots[i] != null)
                        {
                            actions.Add(new Dictionary<string, object?>
                            {
                                ["action"] = "use_potion",
                                ["args"] = new Dictionary<string, object?> { ["potion_index"] = i },
                            });
                        }
                    }
                }
                break;
            }
            case "map":
                if (runState != null)
                {
                    foreach (Dictionary<string, object?> point in RunDto.AvailableMapPoints(runState))
                    {
                        actions.Add(new Dictionary<string, object?>
                        {
                            ["action"] = "map_select",
                            ["args"] = new Dictionary<string, object?>
                            {
                                ["row"] = point["row"],
                                ["col"] = point["col"],
                            },
                        });
                    }
                }
                break;
            case "hand_select":
            {
                // choose toggles a hand card in/out of the live selection;
                // proceed confirms the current selection; skip completes with
                // an empty selection (legal when select_min=0, e.g. Gambling
                // Chip discarding nothing).
                foreach (Dictionary<string, object?> option in screenOptions)
                {
                    actions.Add(new Dictionary<string, object?>
                    {
                        ["action"] = "choose",
                        ["args"] = new Dictionary<string, object?> { ["index"] = option["index"] },
                    });
                }
                actions.Add(new Dictionary<string, object?> { ["action"] = "proceed", ["args"] = new Dictionary<string, object?>() });
                actions.Add(new Dictionary<string, object?> { ["action"] = "skip", ["args"] = new Dictionary<string, object?>() });
                break;
            }
            case "card_reward":
            case "card_choice":
            case "deck_select":
            case "relic_choice":
            case "rewards":
            case "event":
            {
                foreach (Dictionary<string, object?> option in screenOptions)
                {
                    actions.Add(new Dictionary<string, object?>
                    {
                        ["action"] = "choose",
                        ["args"] = new Dictionary<string, object?> { ["index"] = option["index"] },
                    });
                }
                if (screen is "card_reward" or "card_choice" or "deck_select")
                {
                    actions.Add(new Dictionary<string, object?> { ["action"] = "skip", ["args"] = new Dictionary<string, object?>() });
                }
                // "rewards" included: after all reward buttons are claimed the
                // screen exposes no choose options, and proceed (NProceedButton)
                // is the only way forward — without it the actions list showed
                // abandon_run only (live gap 2026-09-17).
                if (screen is "card_choice" or "deck_select" or "relic_choice" or "rewards")
                {
                    actions.Add(new Dictionary<string, object?> { ["action"] = "proceed", ["args"] = new Dictionary<string, object?>() });
                }
                break;
            }
            case "rest":
            {
                foreach (Dictionary<string, object?> option in screenOptions)
                {
                    string oid = option["id"]?.ToString()?.ToUpperInvariant() ?? "";
                    string action = GameProbe.RestOptionIsSmith(oid) ? "smith" : "rest";
                    actions.Add(new Dictionary<string, object?>
                    {
                        ["action"] = action,
                        ["args"] = new Dictionary<string, object?> { ["index"] = option["index"] },
                    });
                }
                // After HEAL/SMITH is chosen the rest-site buttons are consumed
                // and RestOptions comes back empty — without a proceed entry the
                // actions list degraded to abandon_run only and the agent could
                // not see that room-leave was legal (live gap 2026-09-17, run
                // floor 8 deadlock). Proceed() resolves the room's proceed
                // button tree-wide, so listing it always is safe: pre-choice it
                // simply fails with "proceed button is not enabled yet".
                actions.Add(new Dictionary<string, object?>
                {
                    ["action"] = "proceed",
                    ["args"] = new Dictionary<string, object?>(),
                });
                break;
            }
            case "treasure":
                actions.Add(new Dictionary<string, object?> { ["action"] = "treasure_open", ["args"] = new Dictionary<string, object?>() });
                foreach (Dictionary<string, object?> option in screenOptions)
                {
                    if (option["kind"]?.ToString() == "relic")
                    {
                        actions.Add(new Dictionary<string, object?>
                        {
                            ["action"] = "choose",
                            ["args"] = new Dictionary<string, object?> { ["index"] = option["index"] },
                        });
                    }
                }
                actions.Add(new Dictionary<string, object?> { ["action"] = "proceed", ["args"] = new Dictionary<string, object?>() });
                break;
            case "shop":
            {
                foreach (Dictionary<string, object?> option in screenOptions)
                {
                    if (option["stocked"] is true)
                    {
                        actions.Add(new Dictionary<string, object?>
                        {
                            ["action"] = "shop_buy",
                            ["args"] = new Dictionary<string, object?> { ["index"] = option["index"] },
                        });
                    }
                }
                actions.Add(new Dictionary<string, object?> { ["action"] = "shop_leave", ["args"] = new Dictionary<string, object?>() });
                break;
            }
            case "modal":
                actions.Add(new Dictionary<string, object?> { ["action"] = "proceed", ["args"] = new Dictionary<string, object?>() });
                actions.Add(new Dictionary<string, object?> { ["action"] = "skip", ["args"] = new Dictionary<string, object?>() });
                break;
            case "crystal_sphere":
            {
                foreach (Dictionary<string, object?> option in screenOptions)
                {
                    actions.Add(new Dictionary<string, object?>
                    {
                        ["action"] = "choose",
                        ["args"] = new Dictionary<string, object?> { ["index"] = option["index"] },
                    });
                }
                actions.Add(new Dictionary<string, object?> { ["action"] = "proceed", ["args"] = new Dictionary<string, object?>() });
                break;
            }
            case "menu":
                actions.Add(new Dictionary<string, object?> { ["action"] = "start_run", ["args"] = new Dictionary<string, object?>() });
                actions.Add(new Dictionary<string, object?> { ["action"] = "continue_run", ["args"] = new Dictionary<string, object?>() });
                break;
            case "game_over":
                actions.Add(new Dictionary<string, object?> { ["action"] = "proceed", ["args"] = new Dictionary<string, object?>() });
                actions.Add(new Dictionary<string, object?> { ["action"] = "start_run", ["args"] = new Dictionary<string, object?>() });
                break;
        }
        if (runState != null && RunManager.Instance.IsInProgress && screen != "combat")
        {
            actions.Add(new Dictionary<string, object?> { ["action"] = "abandon_run", ["args"] = new Dictionary<string, object?>() });
        }
        return actions;
    }
}
