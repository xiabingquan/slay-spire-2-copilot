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

// Builds the protocol state snapshot from live game objects. Runs only on the
// game main thread; never holds game references between calls. Field access to
// a few private screen members fails soft to index-only option lists.
// Concern split: ScreenDetect (screen resolution), RunDto (run/player/map),
// CombatDto (creatures/intents/move graphs), ScreenOptions (per-screen option
// index spaces), AvailableActions (legal action list), ChooseVerify
// (card-reward press verification) — this class orchestrates and fingerprints.
public static class StateBuilder
{
    public static Dictionary<string, object?> Build()
    {
        InfoCompleteness.BeginBuild();
        RunState? runState = SafeRunState();
        CombatState? combat = SafeCombatState();
        Player? player = null;
        if (runState != null)
        {
            player = LocalContext.GetMe(runState.Players);
        }
        player ??= combat != null ? LocalContext.GetMe(combat) : null;

        string screen = ScreenDetect.DetectScreen(combat, out string screenType, out Node? screenNode);

        // Information contract: screens that imply run/combat state must have
        // the object backing them — a null here is unverified information, not
        // an empty world. 'other' is exempt: DetectScreen returns it when
        // ActiveScreenContext is null (boot/loading transient) or the context
        // is unclassified — neither implies a run, so a null RunState there is
        // the same empty world the player sees, not an information gap.
        // (Live: 2026-09-19 boot race flagged menu as 'other' + RunState
        // unreadable and hard-stopped a clean main menu via exit 78.)
        if (runState == null && screen is not ("menu" or "hello" or "error" or "other"))
        {
            InfoCompleteness.FlagDuringBuild($"screen '{screen}' active but RunState unreadable");
        }
        if (combat == null && screen == "combat")
        {
            InfoCompleteness.FlagDuringBuild("screen 'combat' active but CombatState unreadable");
        }

        Dictionary<string, object?> detail = ScreenOptions.BuildScreenDetail(screen, screenNode, runState, player);
        List<Dictionary<string, object?>> options =
            detail["options"] as List<Dictionary<string, object?>> ?? new List<Dictionary<string, object?>>();

        var state = new Dictionary<string, object?>
        {
            ["screen"] = screen,
            ["screen_type"] = screenType,
            ["run"] = RunDto.BuildRun(runState),
            ["player"] = RunDto.BuildPlayer(player, runState),
            ["combat"] = combat != null ? CombatDto.BuildCombat(combat, player) : null,
            ["screen_detail"] = detail,
        };
        // available_actions derives from the SAME option index spaces
        // screen_detail just published — one probe pass per Build, indices
        // guaranteed to agree between the two lists.
        state["available_actions"] = AvailableActions.Build(screen, combat, player, runState, options);

        // Card-reward choose verification: resolve pending press against the
        // live deck delta (see InfoCompleteness.cs). Runs before fingerprint.
        ChooseVerify.Attach(state, screen, player, runState);

        // Completeness envelope — client hard-stops + Feishu on info_complete:false.
        List<string> missing = InfoCompleteness.DrainForState();
        state["info_complete"] = missing.Count == 0;
        state["missing_info"] = missing;
        state["notify_user"] = missing.Count > 0;

        state["fingerprint"] = Fingerprint(state);
        return state;
    }

    private static RunState? SafeRunState()
    {
        try
        {
            return RunManager.Instance.DebugOnlyGetState();
        }
        catch (Exception)
        {
            return null;
        }
    }

    private static CombatState? SafeCombatState()
    {
        try
        {
            return CombatManager.Instance.DebugOnlyGetState();
        }
        catch (Exception)
        {
            return null;
        }
    }

    private static string Fingerprint(Dictionary<string, object?> state)
    {
        // Content hash over volatile decision inputs. Nested collections are
        // JSON-serialized; List.ToString() yields only the type name.
        var parts = new System.Text.StringBuilder();
        void Add(object? value)
        {
            parts.Append(value switch
            {
                null => "",
                string s => s,
                System.Collections.IEnumerable e and not string =>
                    System.Text.Json.JsonSerializer.Serialize(e),
                _ => value.ToString(),
            });
            parts.Append('|');
        }

        Add(state.GetValueOrDefault("screen"));
        Add(state.GetValueOrDefault("screen_type"));
        if (state.GetValueOrDefault("combat") is Dictionary<string, object?> combat)
        {
            Add(combat.GetValueOrDefault("round"));
            Add(combat.GetValueOrDefault("current_side"));
            Add(combat.GetValueOrDefault("turn_phase"));
            Add(combat.GetValueOrDefault("turn_number"));
            Add(combat.GetValueOrDefault("energy"));
            Add(combat.GetValueOrDefault("max_energy"));
            Add(combat.GetValueOrDefault("creatures"));
            Add(combat.GetValueOrDefault("piles"));
        }
        else
        {
            Add("");
        }
        if (state.GetValueOrDefault("run") is Dictionary<string, object?> run)
        {
            Add(run.GetValueOrDefault("total_floor"));
            Add(run.GetValueOrDefault("act_floor"));
            Add(run.GetValueOrDefault("gold"));
            Add(run.GetValueOrDefault("room_type"));
            Add(run.GetValueOrDefault("is_game_over"));
            Add(run.GetValueOrDefault("map_coord"));
            Add(run.GetValueOrDefault("available_map_points"));
        }
        else
        {
            Add("");
        }
        if (state.GetValueOrDefault("player") is Dictionary<string, object?> player)
        {
            Add(player.GetValueOrDefault("hp"));
            Add(player.GetValueOrDefault("max_hp"));
            Add(player.GetValueOrDefault("block"));
            Add(player.GetValueOrDefault("gold"));
            Add(player.GetValueOrDefault("potions"));
            Add(player.GetValueOrDefault("relics"));
            Add((player.GetValueOrDefault("deck") as List<Dictionary<string, object?>>)?.Count);
        }
        else
        {
            Add("");
        }
        Add(state.GetValueOrDefault("screen_detail"));
        Add(state.GetValueOrDefault("available_actions"));

        string raw = parts.ToString();
        ulong hash = 14695981039346656037;
        foreach (char c in raw)
        {
            hash = (hash ^ c) * 1099511628211;
        }
        return hash.ToString("x16");
    }
}
