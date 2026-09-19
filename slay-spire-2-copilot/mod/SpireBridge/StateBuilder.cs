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
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Entities.Merchant;
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
public static class StateBuilder
{
    internal static readonly FieldInfo? CardRewardOptionsField =
        typeof(NCardRewardSelectionScreen).GetField("_options", BindingFlags.Instance | BindingFlags.NonPublic);

    private static readonly FieldInfo? RelicChoiceField =
        typeof(NChooseARelicSelection).GetField("_relics", BindingFlags.Instance | BindingFlags.NonPublic);

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

        string screen = DetectScreen(combat, out string screenType, out Node? screenNode);

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

        var state = new Dictionary<string, object?>
        {
            ["screen"] = screen,
            ["screen_type"] = screenType,
            ["run"] = BuildRun(runState),
            ["player"] = BuildPlayer(player, runState),
            ["combat"] = combat != null ? BuildCombat(combat, player) : null,
            ["screen_detail"] = BuildScreenDetail(screen, screenNode, runState, player),
        };
        state["available_actions"] = BuildAvailableActions(screen, combat, player, runState, screenNode);

        // Card-reward choose verification: resolve pending press against the
        // live deck delta (see InfoCompleteness.cs). Runs before fingerprint.
        AttachChooseVerification(state, screen, player, runState);

        // Completeness envelope — client hard-stops + Feishu on info_complete:false.
        List<string> missing = InfoCompleteness.DrainForState();
        state["info_complete"] = missing.Count == 0;
        state["missing_info"] = missing;
        state["notify_user"] = missing.Count > 0;

        state["fingerprint"] = Fingerprint(state);
        return state;
    }

    internal static List<string> DeckTupleSnapshot(Player? player, RunState? runState)
    {
        var tuples = new List<string>();
        if (player == null || runState == null)
        {
            InfoCompleteness.FlagDuringAction("deck snapshot unavailable (player/runState null) — choose verification impossible");
            return tuples;
        }
        foreach (Dictionary<string, object?> row in SafeDeck(player, runState))
        {
            string id = row.TryGetValue("id", out object? v) ? v?.ToString() ?? "?" : "?";
            bool upgraded = row.TryGetValue("upgraded", out object? u) && u is true;
            tuples.Add(upgraded ? id + "+" : id);
        }
        return tuples;
    }

    private static void AttachChooseVerification(
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

    // Mid-combat selection overlays (NChooseACardSelectionScreen & kin) open
    // while CombatManager.IsInProgress stays true — boss Curse of Knowledge
    // (Knowledge Demon), Skill/Colorless/Attack/Power potions. DetectScreen's
    // combat short-circuit used to hide them and deadlock the fight
    // (live: Act 2 Knowledge Demon boss, 2026-09-17).
    public static Node? FindCombatSelectOverlay()
    {
        try
        {
            Node root = ((SceneTree)Engine.GetMainLoop()).Root;
            // NCardGridSelectionScreen covers NCombatPileCardSelectScreen
            // (Stratagem-style in-combat chosen draws via CardSelectCmd.
            // FromCombatPile) and the deck-select family — without it the
            // choice overlay was invisible, PlayerChoiceContext never
            // resolved, and combat froze in PlayerTurnPhase.Start/End
            // (live: Act-1 Byrdonis elite with StratagemPower, 2026-09-17).
            if (UiHelper.FindFirst<NCardGridSelectionScreen>(root) is { } g && g.IsVisibleInTree())
            {
                return g;
            }
            if (UiHelper.FindFirst<NChooseACardSelectionScreen>(root) is { } a && a.IsVisibleInTree())
            {
                return a;
            }
            if (UiHelper.FindFirst<NChooseABundleSelectionScreen>(root) is { } b && b.IsVisibleInTree())
            {
                return b;
            }
            if (UiHelper.FindFirst<NSimpleCardSelectScreen>(root) is { } c && c.IsVisibleInTree())
            {
                return c;
            }
            if (UiHelper.FindFirst<NDeckCardSelectScreen>(root) is { } d && d.IsVisibleInTree())
            {
                return d;
            }
        }
        catch { /* tree not ready */ }
        return null;
    }

    // In-hand selection mode (NPlayerHand.CurrentMode SimpleSelect/UpgradeSelect):
    // CardSelectCmd.FromHand* resolves its PlayerChoiceContext through the hand UI
    // itself, not through an overlay screen node — FindCombatSelectOverlay cannot
    // see it. Public surface: IsInCardSelection; private fields _selectedCards /
    // _prefs carry the live selection.
    public static NPlayerHand? FindHandSelectMode()
    {
        try
        {
            NPlayerHand? hand = NCombatRoom.Instance?.Ui?.Hand;
            if (hand != null && hand.IsInCardSelection)
            {
                return hand;
            }
        }
        catch { /* combat room not ready */ }
        return null;
    }

    private static readonly FieldInfo? HandSelectedCardsField =
        typeof(NPlayerHand).GetField("_selectedCards", BindingFlags.NonPublic | BindingFlags.Instance);

    private static readonly FieldInfo? HandPrefsField =
        typeof(NPlayerHand).GetField("_prefs", BindingFlags.NonPublic | BindingFlags.Instance);

    public static List<CardModel> GetHandSelectedCards(NPlayerHand hand)
    {
        try
        {
            return HandSelectedCardsField?.GetValue(hand) as List<CardModel> ?? new List<CardModel>();
        }
        catch
        {
            return new List<CardModel>();
        }
    }

    internal static (int Min, int Max) GetHandSelectBounds(NPlayerHand hand)
    {
        try
        {
            object? prefs = HandPrefsField?.GetValue(hand);
            if (prefs != null)
            {
                int min = prefs.GetType().GetProperty("MinSelect")?.GetValue(prefs) is int mn ? mn : 0;
                int max = prefs.GetType().GetProperty("MaxSelect")?.GetValue(prefs) is int mx ? mx : 0;
                return (min, max);
            }
        }
        catch { /* reflection failed; report unconstrained */ }
        return (0, 0);
    }

    internal static List<Dictionary<string, object?>> HandSelectOptions(Player? player, Node? screenNode)
    {
        var options = new List<Dictionary<string, object?>>();
        if (screenNode is not NPlayerHand hand || player?.PlayerCombatState is not { } pcs)
        {
            return options;
        }
        List<CardModel> selected = GetHandSelectedCards(hand);
        (int min, int max) = GetHandSelectBounds(hand);
        IReadOnlyList<CardModel> cards = pcs.Hand.Cards;
        for (int i = 0; i < cards.Count; i++)
        {
            Dictionary<string, object?> dto = CardDto(cards[i], i, player);
            dto["kind"] = "hand_card";
            dto["selected"] = selected.Contains(cards[i]);
            dto["select_min"] = min;
            dto["select_max"] = max;
            options.Add(dto);
        }
        return options;
    }

    private static string DetectScreen(CombatState? combat, out string screenType, out Node? screenNode)
    {
        screenNode = null;
        screenType = "none";
        try
        {
            if (combat != null && CombatManager.Instance.IsInProgress)
            {
                if (FindCombatSelectOverlay() is { } overlayNode)
                {
                    screenNode = overlayNode;
                    screenType = overlayNode.GetType().Name;
                    return overlayNode switch
                    {
                        NDeckCardSelectScreen => "deck_select",
                        _ => "card_choice",
                    };
                }
                // CardSelectCmd.FromHand* choices (Gambling Chip discard,
                // Armaments upgrade-select, …) run inside NPlayerHand itself —
                // no overlay screen node exists. Surface them as hand_select
                // or the PlayerChoiceContext never resolves and combat freezes
                // in PlayerTurnPhase.Start (live: Act-2 Ovicopter + GamblingChip,
                // 2026-09-17).
                if (FindHandSelectMode() is { } handNode)
                {
                    screenNode = handNode;
                    screenType = "NPlayerHand";
                    return "hand_select";
                }
                screenType = "NCombatRoom";
                return "combat";
            }
            if (NGame.Instance?.MainMenu is { } mainMenu && mainMenu.IsVisibleInTree() && NRun.Instance == null)
            {
                screenNode = mainMenu;
                screenType = mainMenu.GetType().Name;
                return "menu";
            }
            IScreenContext? current = ActiveScreenContext.Instance.GetCurrentScreen();
            if (current == null)
            {
                return "other";
            }
            if (NModalContainer.Instance?.OpenModal is Node modalNode && ReferenceEquals(current, modalNode))
            {
                screenNode = modalNode;
                screenType = modalNode.GetType().Name;
                return "modal";
            }
            screenNode = current as Node;
            screenType = current.GetType().Name;
            return current switch
            {
                NMapScreen => "map",
                NRewardsScreen => "rewards",
                NCardRewardSelectionScreen => "card_reward",
                NChooseARelicSelection => "relic_choice",
                NChooseACardSelectionScreen => "card_choice",
                NChooseABundleSelectionScreen => "card_choice",
                NSimpleCardSelectScreen => "card_choice",
                NDeckCardSelectScreen => "deck_select",
                NDeckUpgradeSelectScreen => "deck_select",
                NDeckTransformSelectScreen => "deck_select",
                NDeckEnchantSelectScreen => "deck_select",
                NGameOverScreen => "game_over",
                NEventRoom => "event",
                NTreasureRoom => "treasure",
                NRestSiteRoom => "rest",
                NMerchantRoom => "shop",
                NMerchantInventory => "shop",
                NCrystalSphereScreen => "crystal_sphere",
                NMainMenu => "menu",
                NCombatRoom => "combat",
                _ => DefaultScreenFor(current, screenNode),
            };
        }
        catch (Exception)
        {
            return "other";
        }
    }

    // Event-embedded merchant UIs (e.g. NFakeMerchant) expose the same
    // NMerchantInventory slot system; route them through the shop pipeline.
    private static string DefaultScreenFor(IScreenContext current, Node? screenNode)
    {
        if (screenNode == null)
        {
            return "other";
        }
        string typeName = current.GetType().Name;
        if (typeName.Contains("Merchant", StringComparison.OrdinalIgnoreCase)
            || UiHelper.FindFirst<NMerchantInventory>(screenNode) != null)
        {
            return "shop";
        }
        return "other";
    }

    private static Dictionary<string, object?>? BuildRun(RunState? runState)
    {
        if (runState == null)
        {
            return null;
        }
        var run = new Dictionary<string, object?>
        {
            ["active"] = RunManager.Instance.IsInProgress && !RunManager.Instance.IsAbandoned,
            ["act_index"] = runState.CurrentActIndex,
            ["act_floor"] = runState.ActFloor,
            ["total_floor"] = runState.TotalFloor,
            ["room_type"] = runState.CurrentRoom?.RoomType.ToString() ?? "Unassigned",
            ["is_game_over"] = runState.IsGameOver,
            ["gold"] = SafeGold(runState),
            ["ascension"] = runState.AscensionLevel,
            ["map_coord"] = runState.CurrentMapCoord is { } coord ? CoordDto(coord) : null,
        };
        try { run["seed"] = runState.Rng.StringSeed; } catch (Exception) { /* omit */ }
        try { run["game_mode"] = runState.GameMode.ToString(); } catch (Exception) { /* omit */ }
        try
        {
            run["modifiers"] = runState.Modifiers
                .Select(m => m.Id.Entry)
                .Where(e => !string.IsNullOrEmpty(e))
                .ToList();
        }
        catch (Exception) { run["modifiers"] = new List<string>(); }
        try
        {
            run["visited_coords"] = runState.VisitedMapCoords.Select(CoordDto).ToList();
        }
        catch (Exception)
        {
            run["visited_coords"] = new List<object?>();
        }
        run["available_map_points"] = AvailableMapPoints(runState);
        run["map"] = FullMapDto(runState);
        run["act_start_room"] = ActStartRoom(runState, run["available_map_points"]);
        return run;
    }

    // Act-start boon rooms (Ancient/Neow-family, e.g. 先古移民 with HP
    // restore) sit on the map's lowest row. The game transitions straight to
    // the row-1 map after act bosses, and available_map_points never lists
    // the start room — agents skipped the boon (live miss 2026-09-17). This
    // surfaces the start room explicitly AND re-injects it into the
    // selectable list while unvisited, so map_select can target it first.
    private static object? ActStartRoom(RunState runState, object? availablePoints)
    {
        try
        {
            ActMap? map = runState.Map;
            if (map == null)
            {
                return null;
            }
            List<MapPoint> all = map.GetAllMapPoints().ToList();
            // Act-start points can live outside the grid enumeration
            // (same class of gap as boss points) — without StartingMapPoint
            // the min-row scan lands on row 1 and misses the boon room.
            try
            {
                if (map.StartingMapPoint is { } sp
                    && !all.Any(p => p.coord.row == sp.coord.row && p.coord.col == sp.coord.col))
                {
                    all.Add(sp);
                }
            }
            catch { /* StartingMapPoint unavailable */ }
            if (all.Count == 0)
            {
                return null;
            }
            int minRow = all.Min(p => p.coord.row);
            MapPoint start = all.First(p => p.coord.row == minRow);
            bool visited = false;
            try
            {
                visited = runState.VisitedMapCoords.Any(c => c.row == start.coord.row && c.col == start.coord.col);
            }
            catch { /* visited list unavailable */ }
            var dto = new Dictionary<string, object?>
            {
                ["row"] = start.coord.row,
                ["col"] = start.coord.col,
                ["point_type"] = start.PointType.ToString(),
                ["visited"] = visited,
                // String match on PointType — enum members vary by build;
                // Ancient covers Neow-family boon rooms (先古移民 etc.).
                ["is_boon_room"] = start.PointType.ToString() is "Ancient" or "Unknown"
                    or "Event" or "Neow" or "NeowBoon",
            };
            // Re-inject unvisited boon-room starts into the selectable list.
            if (!visited && dto["is_boon_room"] is true && availablePoints is List<Dictionary<string, object?>> list)
            {
                bool already = list.Any(p => (p.GetValueOrDefault("row") as int?) == start.coord.row
                    && (p.GetValueOrDefault("col") as int?) == start.coord.col);
                if (!already)
                {
                    list.Insert(0, new Dictionary<string, object?>
                    {
                        ["row"] = start.coord.row,
                        ["col"] = start.coord.col,
                        ["point_type"] = start.PointType.ToString(),
                        ["act_start_boon"] = true,
                    });
                }
            }
            return dto;
        }
        catch (Exception e)
        {
            return new Dictionary<string, object?> { ["error"] = e.Message };
        }
    }

    // Full act map for route planning: every point with its room type plus
    // forward connectivity (children coords). available_map_points only lists
    // the current selectable row — without the rest of the graph the AI
    // cannot weigh elite/rest/shop/boss paths ahead.
    private static object? FullMapDto(RunState runState)
    {
        try
        {
            ActMap? map = runState.Map;
            if (map == null)
            {
                return null;
            }
            var byRow = new SortedDictionary<int, List<Dictionary<string, object?>>>();
            void AddPoint(MapPoint p)
            {
                var children = new List<object?>();
                try
                {
                    foreach (MapPoint c in p.Children)
                    {
                        children.Add(CoordDto(c.coord));
                    }
                }
                catch { /* children unavailable */ }
                if (!byRow.TryGetValue(p.coord.row, out List<Dictionary<string, object?>>? list))
                {
                    list = new List<Dictionary<string, object?>>();
                    byRow[p.coord.row] = list;
                }
                list.Add(new Dictionary<string, object?>
                {
                    ["row"] = p.coord.row,
                    ["col"] = p.coord.col,
                    ["point_type"] = p.PointType.ToString(),
                    ["children"] = children,
                });
            }
            foreach (MapPoint p in map.GetAllMapPoints())
            {
                AddPoint(p);
            }
            // Boss / start points can live outside the grid enumeration.
            try { if (map.BossMapPoint is { } boss) AddPoint(boss); } catch { }
            try { if (map.StartingMapPoint is { } start) AddPoint(start); } catch { }
            var rows = new List<object?>();
            foreach (KeyValuePair<int, List<Dictionary<string, object?>>> kv in byRow)
            {
                rows.Add(new Dictionary<string, object?>
                {
                    ["row"] = kv.Key,
                    ["points"] = kv.Value,
                });
            }
            return new Dictionary<string, object?> { ["rows"] = rows };
        }
        catch (Exception e)
        {
            return new Dictionary<string, object?> { ["error"] = e.Message };
        }
    }

    private static object? SafeGold(RunState runState)
    {
        try
        {
            Player? me = LocalContext.GetMe(runState.Players);
            PropertyInfo? prop = me?.GetType().GetProperty("Gold");
            return prop?.GetValue(me);
        }
        catch (Exception)
        {
            return null;
        }
    }

    private static Dictionary<string, object?> CoordDto(MapCoord coord) => new()
    {
        ["row"] = coord.row,
        ["col"] = coord.col,
    };

    private static List<Dictionary<string, object?>> AvailableMapPoints(RunState runState)
    {
        var points = new List<Dictionary<string, object?>>();
        try
        {
            ActMap map = runState.Map;
            IEnumerable<MapPoint> candidates;
            if (runState.VisitedMapCoords.Count == 0)
            {
                // First selection of a run targets the lowest-row points on the
                // map (the floor-0/1 entrance), mirroring the game's AutoSlay.
                List<MapPoint> all = map.GetAllMapPoints().ToList();
                int minRow = all.Count > 0 ? all.Min(p => p.coord.row) : 0;
                candidates = all.Where(p => p.coord.row == minRow);
            }
            else
            {
                candidates = runState.CurrentMapPoint?.Children
                    ?? map.startMapPoints.Cast<MapPoint>();
            }
            foreach (MapPoint point in candidates)
            {
                points.Add(new Dictionary<string, object?>
                {
                    ["row"] = point.coord.row,
                    ["col"] = point.coord.col,
                    ["point_type"] = point.PointType.ToString(),
                });
            }
        }
        catch (Exception)
        {
            // map graph unavailable (menu / between acts)
        }
        return points;
    }

    private static Dictionary<string, object?>? BuildPlayer(Player? player, RunState? runState)
    {
        if (player == null)
        {
            return null;
        }
        Creature creature = player.Creature;
        var dto = new Dictionary<string, object?>
        {
            ["hp"] = creature.CurrentHp,
            ["max_hp"] = creature.MaxHp,
            ["block"] = creature.Block,
            ["relics"] = player.Relics.Select(r =>
            {
                var relic = new Dictionary<string, object?>
                {
                    ["id"] = r.Id.Entry,
                    ["name"] = ModelName(r),
                };
                try { relic["stack_count"] = r.StackCount; } catch (Exception) { /* omit */ }
                try { relic["is_used_up"] = r.IsUsedUp; } catch (Exception) { /* omit */ }
                try
                {
                    if (r.ShowCounter)
                    {
                        relic["counter"] = r.DisplayAmount;
                    }
                }
                catch (Exception) { /* omit */ }
                return relic;
            }).ToList(),
            ["potions"] = player.PotionSlots.Select((PotionModel? p, int i) =>
            {
                if (p == null)
                {
                    return null;
                }
                var potion = new Dictionary<string, object?>
                {
                    ["index"] = i,
                    ["id"] = p.Id.Entry,
                    ["name"] = ModelName(p),
                    ["target_type"] = p.TargetType.ToString(),
                };
                try { potion["rarity"] = p.Rarity.ToString(); } catch (Exception) { /* omit */ }
                try { potion["usage"] = p.Usage.ToString(); } catch (Exception) { /* omit */ }
                return potion;
            }).ToList(),
        };
        try
        {
            // Character + ascension verification fields (long-term policy):
            // character id entry (e.g. "IRONCLAD") and the profile's unlocked
            // max ascension snapshot taken at run start.
            if (player.Character?.Id is { } charId)
            {
                dto["character"] = charId.Entry;
                dto["character_id"] = charId.ToString();
            }
            dto["ascension_max_at_start"] = player.MaxAscensionWhenRunStarted;
        }
        catch (Exception)
        {
            // character/ascension not exposed on this build
        }
        try
        {
            PropertyInfo? gold = player.GetType().GetProperty("Gold");
            if (gold?.GetValue(player) is { } g)
            {
                dto["gold"] = g;
            }
        }
        catch (Exception)
        {
            // gold not exposed on this build
        }
        if (runState != null)
        {
            try
            {
                dto["deck"] = SafeDeck(player, runState);
            }
            catch (Exception)
            {
                dto["deck"] = new List<object?>();
            }
        }
        return dto;
    }

    private static List<Dictionary<string, object?>> SafeDeck(Player player, RunState runState)
    {
        // Player.Deck is a CardPile; iterate its Cards collection.
        try
        {
            CardPile? pile = player.Deck;
            if (pile == null)
            {
                return new List<Dictionary<string, object?>>();
            }
            return pile.Cards.Select((CardModel c, int i) => new Dictionary<string, object?>
            {
                ["index"] = i,
                ["id"] = c.Id.Entry,
                ["name"] = ModelName(c),
                ["upgraded"] = ProbeBool(c, "IsUpgraded", "Upgraded"),
            }).ToList();
        }
        catch (Exception e)
        {
            InfoCompleteness.FlagDuringBuild($"player deck unreadable ({e.GetType().Name}) — player can open the deck in-game");
            return new List<Dictionary<string, object?>>();
        }
    }

    private static Dictionary<string, object?>? BuildCombat(CombatState combat, Player? player)
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
                bool upgraded = ProbeBool(card, "IsUpgraded", "Upgraded") is true;
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

    private static string? SafeMoveId(MonsterModel monster)
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
    // .GetSingleDamage/.GetTotalDamage (public, run the live damage hooks),
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
            dto["label"] = CleanIntentLabel(ResolveLoc(intent.GetIntentLabel(Array.Empty<Creature>(), owner)), intent);
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
                string? text = ResolveLoc(loc);
                if (!string.IsNullOrWhiteSpace(text))
                {
                    dto["description"] = StripBbcode(text);
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
            ["name"] = ModelName(power),
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

    private static Dictionary<string, object?> CardDto(CardModel card, int index, Player? player)
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
            ["name"] = ModelName(card),
            ["cost"] = cost,
            ["target_type"] = card.TargetType.ToString(),
            ["can_play"] = canPlay,
            ["unplayable_reason"] = reason,
            ["upgraded"] = ProbeBool(card, "IsUpgraded", "Upgraded"),
        };
    }

    private static object? ProbeBool(object target, params string[] names)
    {
        foreach (string name in names)
        {
            if (target.GetType().GetProperty(name)?.GetValue(target) is bool b)
            {
                return b;
            }
        }
        return null;
    }

    private static string ModelName(AbstractModel model)
    {
        try
        {
            if (model.GetType().GetProperty("Title")?.GetValue(model) is LocString loc)
            {
                return ResolveLoc(loc);
            }
        }
        catch (Exception)
        {
            // localization lookup failed; fall back to id
        }
        return model.Id.Entry;
    }

    // LocString.ToString() dumps table metadata; resolution goes through
    // LocManager.SmartFormat via GetFormattedText. BBCode styling tags are
    // stripped so agent-facing text stays clean.
    internal static string ResolveLoc(LocString loc)
    {
        try
        {
            string text = loc.GetFormattedText();
            if (!string.IsNullOrWhiteSpace(text))
            {
                return StripBbcode(text);
            }
        }
        catch (Exception)
        {
            // SmartFormat may fail on incomplete variables
        }
        try
        {
            string raw = loc.GetRawText();
            if (!string.IsNullOrWhiteSpace(raw))
            {
                return StripBbcode(raw);
            }
        }
        catch (Exception)
        {
            // raw table entry missing
        }
        return $"{loc.LocTable}:{loc.LocEntryKey}";
    }

    private static string StripBbcode(string text)
    {
        return System.Text.RegularExpressions.Regex.Replace(text, @"\[/?[^\]]+\]", "");
    }

    private static Dictionary<string, object?> BuildScreenDetail(
        string screen, Node? screenNode, RunState? runState, Player? player)
    {
        var detail = new Dictionary<string, object?>
        {
            ["options"] = new List<Dictionary<string, object?>>(),
        };
        try
        {
            List<Dictionary<string, object?>> options = screen switch
            {
                "map" => MapOptions(runState),
                "card_reward" => CardRewardOptions(screenNode),
                "relic_choice" => RelicChoiceOptions(screenNode),
                "card_choice" or "deck_select" => CardHolderOptions(screenNode),
                "hand_select" => HandSelectOptions(player, screenNode),
                "rewards" => RewardButtonOptions(screenNode),
                "event" => EventOptions(screenNode),
                "treasure" => TreasureOptions(screenNode),
                "rest" => RestOptions(screenNode),
                "shop" => ShopOptions(screenNode),
                "modal" => ModalOptions(screenNode),
                "crystal_sphere" => CrystalOptions(screenNode),
                _ => new List<Dictionary<string, object?>>(),
            };
            detail["options"] = options;
        }
        catch (Exception e)
        {
            detail["error"] = e.Message;
        }
        return detail;
    }

    private static List<Dictionary<string, object?>> MapOptions(RunState? runState)
    {
        var options = new List<Dictionary<string, object?>>();
        if (runState == null)
        {
            return options;
        }
        var uiPoints = new Dictionary<(int Row, int Col), NMapPoint>();
        try
        {
            if (NMapScreen.Instance is { } mapScreen)
            {
                foreach (NMapPoint node in UiHelper.FindAll<NMapPoint>(mapScreen))
                {
                    uiPoints[(node.Point.coord.row, node.Point.coord.col)] = node;
                }
            }
        }
        catch (Exception)
        {
            // UI map nodes unavailable; options still come from run state
        }
        List<Dictionary<string, object?>> statePoints = AvailableMapPoints(runState);
        for (int i = 0; i < statePoints.Count; i++)
        {
            Dictionary<string, object?> d = statePoints[i];
            int row = (int)d["row"]!;
            int col = (int)d["col"]!;
            var option = new Dictionary<string, object?>
            {
                ["kind"] = "map_point",
                ["index"] = i,
                ["id"] = $"{row},{col}",
                ["name"] = d["point_type"]?.ToString() ?? "unknown",
                ["detail"] = d,
            };
            if (uiPoints.TryGetValue((row, col), out NMapPoint? node))
            {
                option["enabled"] = node.IsEnabled;
                option["visible"] = node.Visible;
                option["point_state"] = node.State.ToString();
            }
            options.Add(option);
        }
        if (NMapScreen.Instance is { } screen)
        {
            if (options.Count > 0)
            {
                options[0]["travel_enabled"] = screen.IsTravelEnabled;
                options[0]["is_traveling"] = screen.IsTraveling;
            }
        }
        return options;
    }

    private static List<Dictionary<string, object?>> CardRewardOptions(Node? screenNode)
    {
        var options = new List<Dictionary<string, object?>>();
        if (screenNode is not NCardRewardSelectionScreen screen)
        {
            return options;
        }
        if (CardRewardOptionsField?.GetValue(screen) is IEnumerable<object> cards)
        {
            int i = 0;
            foreach (object result in cards)
            {
                options.Add(CardResultOption(result, i));
                i++;
            }
        }
        if (options.Count == 0)
        {
            // The player sees three card rewards on screen — an empty list from
            // reflection is a miss, not an empty reward.
            InfoCompleteness.FlagDuringBuild(
                "card_reward screen active but options list unreadable (reflection miss — player sees the card options in-game)");
        }
        return options;
    }

    private static Dictionary<string, object?> CardResultOption(object result, int index)
    {
        string? id = ProbeModelId(result);
        var option = new Dictionary<string, object?>
        {
            ["kind"] = "card",
            ["index"] = index,
            ["id"] = id,
        };
        if (string.IsNullOrEmpty(id))
        {
            // NO FALLBACK: no invented option_N names. The id the player can
            // read on the card face is unreadable to us — that is incomplete.
            option["name"] = null;
            option["incomplete"] = true;
            InfoCompleteness.FlagDuringBuild(
                $"card_reward option {index}: card id unresolved (reflection miss — player reads the card name on screen)");
        }
        else
        {
            option["name"] = id;
        }
        return option;
    }

    internal static string? ProbeModelId(object container)
    {
        foreach (string member in new[] { "Card", "card", "Model", "CardModel" })
        {
            object? value = container.GetType().GetProperty(member)?.GetValue(container)
                ?? container.GetType().GetField(member)?.GetValue(container);
            if (value is AbstractModel model)
            {
                return model.Id.Entry;
            }
            if (value != null)
            {
                PropertyInfo? id = value.GetType().GetProperty("Id") ?? value.GetType().GetProperty("CardId");
                if (id?.GetValue(value) is ModelId modelId)
                {
                    return modelId.Entry;
                }
                if (id?.GetValue(value) is string s)
                {
                    return s;
                }
            }
        }
        return null;
    }

    private static List<Dictionary<string, object?>> RelicChoiceOptions(Node? screenNode)
    {
        var options = new List<Dictionary<string, object?>>();
        if (screenNode is not NChooseARelicSelection screen)
        {
            return options;
        }
        IReadOnlyList<RelicModel>? relics = RelicChoiceField?.GetValue(screen) as IReadOnlyList<RelicModel>;
        if (relics == null)
        {
            return options;
        }
        for (int i = 0; i < relics.Count; i++)
        {
            RelicModel relic = relics[i];
            options.Add(new Dictionary<string, object?>
            {
                ["kind"] = "relic",
                ["index"] = i,
                ["id"] = relic.Id.Entry,
                ["name"] = ModelName(relic),
            });
        }
        return options;
    }

    // Index space for card-selection screens. Deck-select grids route clicks
    // through NGridCardHolder (game AutoSlay DeckCardSelectScreenHandler does
    // the same); FindAll<NCardHolder> also returns preview/ghost holders, whose
    // indices never map to grid clicks — choose then Presses a dead node.
    internal static List<NCardHolder> SelectableCardHolders(Node screenNode)
    {
        if (screenNode is NDeckCardSelectScreen or NDeckUpgradeSelectScreen
            or NDeckTransformSelectScreen or NDeckEnchantSelectScreen
            or NCombatPileCardSelectScreen
            or NChooseACardSelectionScreen or NChooseABundleSelectionScreen)
        {
            // NChooseACardSelectionScreen also clicks NGridCardHolder nodes
            // (decomp: nGridCardHolder.Pressed -> SelectHolder); unfiltered
            // FindAll<NCardHolder> put preview/ghost holders in the index
            // space and choose(2) silently picked the wrong card live
            // (run-12: THE_GAMBIT pick landed on PROLONG).
            return UiHelper.FindAll<NGridCardHolder>(screenNode).Cast<NCardHolder>().ToList();
        }
        return UiHelper.FindAll<NCardHolder>(screenNode);
    }

    private static List<Dictionary<string, object?>> CardHolderOptions(Node? screenNode)
    {
        var options = new List<Dictionary<string, object?>>();
        if (screenNode == null)
        {
            return options;
        }
        List<NCardHolder> holders = SelectableCardHolders(screenNode);
        for (int i = 0; i < holders.Count; i++)
        {
            options.Add(new Dictionary<string, object?>
            {
                ["kind"] = "card",
                ["index"] = i,
                ["id"] = ProbeModelId(holders[i]),
                ["name"] = ProbeModelId(holders[i]) ?? $"card_{i}",
            });
        }
        return options;
    }

    private static List<Dictionary<string, object?>> RewardButtonOptions(Node? screenNode)
    {
        var options = new List<Dictionary<string, object?>>();
        if (screenNode == null)
        {
            return options;
        }
        List<NRewardButton> buttons = UiHelper.FindAll<NRewardButton>(screenNode)
            .Where(b => b.Visible && b.IsEnabled)
            .ToList();
        for (int i = 0; i < buttons.Count; i++)
        {
            options.Add(new Dictionary<string, object?>
            {
                ["kind"] = "reward",
                ["index"] = i,
                ["id"] = buttons[i].Name.ToString(),
                ["name"] = buttons[i].Name.ToString(),
            });
        }
        return options;
    }

    private static List<Dictionary<string, object?>> EventOptions(Node? screenNode)
    {
        var options = new List<Dictionary<string, object?>>();
        if (screenNode == null)
        {
            return options;
        }
        List<NEventOptionButton> buttons = UiHelper.FindAll<NEventOptionButton>(screenNode)
            .Where(b => b.Option is { IsLocked: false })
            .ToList();
        for (int i = 0; i < buttons.Count; i++)
        {
            EventOption option = buttons[i].Option;
            var dto = new Dictionary<string, object?>
            {
                ["kind"] = "event_option",
                ["index"] = i,
                ["id"] = option.TextKey,
                ["name"] = ResolveLoc(option.Title),
                ["is_proceed"] = option.IsProceed,
            };
            try
            {
                string? description = ResolveLoc(option.Description);
                if (!string.IsNullOrWhiteSpace(description))
                {
                    dto["description"] = StripBbcode(description);
                }
            }
            catch (Exception) { /* omit */ }
            try
            {
                // Live textKey shape: "NEOW.pages.INITIAL.options.NEOWS_TALISMAN"
                // — event id is the segment before ".pages.".
                string textKey = option.TextKey ?? "";
                int pages = textKey.IndexOf(".pages.", StringComparison.Ordinal);
                if (pages > 0)
                {
                    dto["event_id"] = textKey[..pages];
                }
                else if (!string.IsNullOrEmpty(textKey))
                {
                    dto["event_id"] = textKey.Split('.')[0];
                }
            }
            catch (Exception) { /* omit */ }
            try
            {
                if (option.Relic is { } relic)
                {
                    dto["relic_id"] = relic.Id.Entry;
                }
            }
            catch (Exception) { /* omit */ }
            options.Add(dto);
        }
        return options;
    }

    private static List<Dictionary<string, object?>> TreasureOptions(Node? screenNode)
    {
        var options = new List<Dictionary<string, object?>>();
        if (screenNode is not NTreasureRoom room)
        {
            return options;
        }
        Node? chest = room.GetNodeOrNull("Chest");
        if (chest != null)
        {
            options.Add(new Dictionary<string, object?>
            {
                ["kind"] = "button",
                ["index"] = options.Count,
                ["id"] = "chest",
                ["name"] = "Open chest",
            });
        }
        List<NTreasureRoomRelicHolder> holders = UiHelper.FindAll<NTreasureRoomRelicHolder>(room);
        foreach (NTreasureRoomRelicHolder holder in holders.Where(h => h.IsEnabled && h.Visible))
        {
            options.Add(new Dictionary<string, object?>
            {
                ["kind"] = "relic",
                ["index"] = options.Count,
                ["id"] = holder.Name.ToString(),
                ["name"] = holder.Name.ToString(),
            });
        }
        return options;
    }

    private static List<Dictionary<string, object?>> RestOptions(Node? screenNode)
    {
        var options = new List<Dictionary<string, object?>>();
        if (screenNode == null)
        {
            return options;
        }
        List<NRestSiteButton> buttons = UiHelper.FindAll<NRestSiteButton>(screenNode);
        for (int i = 0; i < buttons.Count; i++)
        {
            var option = new Dictionary<string, object?>
            {
                ["kind"] = "button",
                ["index"] = i,
                ["id"] = buttons[i].Name.ToString(),
                ["name"] = buttons[i].Name.ToString(),
            };
            try
            {
                // Button.Option throws if unset; resolve id/title when available.
                MegaCrit.Sts2.Core.Entities.RestSite.RestSiteOption restOption = buttons[i].Option;
                option["id"] = restOption.OptionId;
                option["name"] = ResolveLoc(restOption.Title);
                option["enabled"] = restOption.IsEnabled;
            }
            catch (Exception)
            {
                // option not bound yet
            }
            options.Add(option);
        }
        return options;
    }

    private static List<Dictionary<string, object?>> ShopOptions(Node? screenNode)
    {
        var options = new List<Dictionary<string, object?>>();
        NMerchantRoom? room = screenNode as NMerchantRoom ?? NMerchantRoom.Instance;
        NMerchantInventory? inventory = room?.Inventory
            ?? (screenNode != null ? UiHelper.FindFirst<NMerchantInventory>(screenNode) : null)
            ?? (NRun.Instance != null ? UiHelper.FindFirst<NMerchantInventory>(NRun.Instance) : null);
        if (inventory == null)
        {
            return options;
        }
        try
        {
            // Slots live in the inventory UI; open it so the client sees the goods.
            if (room?.Inventory is { IsOpen: false })
            {
                room.OpenInventory();
            }
            List<NMerchantSlot> slots = inventory.GetAllSlots()?.ToList() ?? new List<NMerchantSlot>();
            int index = 0;
            foreach (NMerchantSlot slot in slots)
            {
                MerchantEntry? entry = slot.Entry;
                if (entry == null)
                {
                    continue;
                }
                // Card goods wrap the model in CreationResult; probe that first.
                object probeTarget = entry is MerchantCardEntry { CreationResult: { } creation }
                    ? creation : entry;
                string id = ProbeModelId(probeTarget) ?? entry.GetType().Name;
                options.Add(new Dictionary<string, object?>
                {
                    ["kind"] = slot is NMerchantCardRemoval ? "card_removal" : "shop_item",
                    ["index"] = index,
                    ["id"] = id,
                    ["name"] = id,
                    ["cost"] = entry.Cost,
                    ["affordable"] = entry.EnoughGold,
                    ["stocked"] = entry.IsStocked,
                });
                index++;
            }
        }
        catch (Exception e)
        {
            options.Add(new Dictionary<string, object?> { ["kind"] = "error", ["id"] = e.Message });
        }
        return options;
    }

    private static List<Dictionary<string, object?>> ModalOptions(Node? screenNode)
    {
        var options = new List<Dictionary<string, object?>>();
        if (screenNode == null)
        {
            return options;
        }
        List<NButton> buttons = UiHelper.FindAll<NButton>(screenNode);
        for (int i = 0; i < buttons.Count; i++)
        {
            options.Add(new Dictionary<string, object?>
            {
                ["kind"] = "button",
                ["index"] = i,
                ["id"] = buttons[i].Name.ToString(),
                ["name"] = buttons[i].Name.ToString(),
            });
        }
        return options;
    }

    private static List<Dictionary<string, object?>> CrystalOptions(Node? screenNode)
    {
        var options = new List<Dictionary<string, object?>>();
        if (screenNode == null)
        {
            return options;
        }
        List<NCrystalSphereCell> cells = UiHelper.FindAll<NCrystalSphereCell>(screenNode);
        for (int i = 0; i < cells.Count; i++)
        {
            options.Add(new Dictionary<string, object?>
            {
                ["kind"] = "crystal_cell",
                ["index"] = i,
                ["id"] = cells[i].Name.ToString(),
                ["name"] = cells[i].Name.ToString(),
                ["visible"] = cells[i].Visible,
            });
        }
        return options;
    }

    private static List<Dictionary<string, object?>> BuildAvailableActions(
        string screen, CombatState? combat, Player? player, RunState? runState, Node? screenNode)
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
                    foreach (Dictionary<string, object?> point in AvailableMapPoints(runState))
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
                foreach (Dictionary<string, object?> option in HandSelectOptions(player, screenNode))
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
                List<Dictionary<string, object?>> options =
                    ((BuildScreenDetail(screen, screenNode, runState, player)["options"] as List<Dictionary<string, object?>>)
                     ?? new List<Dictionary<string, object?>>());
                foreach (Dictionary<string, object?> option in options)
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
                foreach (Dictionary<string, object?> option in RestOptions(screenNode))
                {
                    string oid = option["id"]?.ToString()?.ToUpperInvariant() ?? "";
                    string action = oid.Contains("SMITH") || oid.Contains("UPGRADE") || oid.Contains("MEND")
                        ? "smith" : "rest";
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
                foreach (Dictionary<string, object?> option in TreasureOptions(screenNode))
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
                foreach (Dictionary<string, object?> option in ShopOptions(screenNode))
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
                foreach (Dictionary<string, object?> option in CrystalOptions(screenNode))
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
