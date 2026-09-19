using System;
using System.Collections.Generic;
using System.Text.Json;
using System.Threading.Tasks;
using MegaCrit.Sts2.Core.Combat;
using MegaCrit.Sts2.Core.Context;
using MegaCrit.Sts2.Core.Entities.Players;

namespace SpireCopilot.Bridge;

// Dispatches protocol actions on the game main thread. Long-running game
// sequences (card play animations, menu automation) are started fire-and-
// forget; completion is observed by the client polling state fingerprints.
// Executors by concern: CombatActions (play/end_turn/force/potions),
// ScreenActions (choose/skip/proceed/map/shop/rest), RunLifecycle
// (start/continue/abandon + game-over chain), TimelineUnlock (epoch drain).
public static class ActionExecutor
{
    public static (bool Ok, string Message, Dictionary<string, object?>? State) Execute(string action, JsonElement args)
    {
        try
        {
            (bool ok, string message) = action switch
            {
                "play" => CombatActions.Play(args),
                "end_turn" => CombatActions.EndTurn(),
                "force_combat_end" => CombatActions.ForceCombatEnd(),
                "force_advance_turn" => CombatActions.ForceAdvanceTurn(),
                "use_potion" => CombatActions.UsePotion(args),
                "map_select" => ScreenActions.MapSelect(args),
                "choose" => ScreenActions.Choose(args),
                "skip" => ScreenActions.Skip(),
                "treasure_open" => ScreenActions.TreasureOpen(),
                "proceed" => ScreenActions.Proceed(),
                "rest" => ScreenActions.RestSiteOption(preferSmith: false),
                "smith" => ScreenActions.RestSiteOption(preferSmith: true),
                "shop_buy" => ScreenActions.ShopBuy(args),
                "shop_leave" => ScreenActions.ShopLeave(),
                "start_run" => RunLifecycle.StartRun(args),
                "continue_run" => RunLifecycle.ContinueRun(),
                "timeline_sync" => TimelineUnlock.TimelineSync(),
                "abandon_run" => RunLifecycle.AbandonRun(),
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

    internal static Dictionary<string, object?>? SafeState()
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

    internal static bool TryGetCombatPlayer(out Player? player, out CombatState combat, out PlayerCombatState? pcs)
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

    internal static void Fire(Func<Task> work, string label)
    {
        work().ContinueWith(task =>
        {
            if (task.IsFaulted)
            {
                BridgeMod.LogErr($"{label} failed: {task.Exception}");
            }
        }, TaskScheduler.Default);
    }

    internal static bool TryGetInt(JsonElement args, string name, out int value)
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

    internal static string? GetString(JsonElement args, string name)
    {
        if (args.ValueKind != JsonValueKind.Object || !args.TryGetProperty(name, out JsonElement prop))
        {
            return null;
        }
        return prop.ValueKind == JsonValueKind.String ? prop.GetString() : null;
    }
}
