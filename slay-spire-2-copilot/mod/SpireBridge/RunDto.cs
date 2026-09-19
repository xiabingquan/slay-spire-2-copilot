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

// Run-scoped state DTOs: run progress, act map graph, player snapshot, deck.
public static class RunDto
{
    internal static Dictionary<string, object?>? BuildRun(RunState? runState)
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

    internal static Dictionary<string, object?>? BuildPlayer(Player? player, RunState? runState)
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
                    ["name"] = GameProbe.ModelName(r),
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
                    ["name"] = GameProbe.ModelName(p),
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
            System.Reflection.PropertyInfo? gold = player.GetType().GetProperty("Gold");
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

    internal static List<Dictionary<string, object?>> SafeDeck(Player player, RunState runState)
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
                ["name"] = GameProbe.ModelName(c),
                ["upgraded"] = GameProbe.ProbeBool(c, "IsUpgraded", "Upgraded"),
            }).ToList();
        }
        catch (Exception e)
        {
            InfoCompleteness.FlagDuringBuild($"player deck unreadable ({e.GetType().Name}) — player can open the deck in-game");
            return new List<Dictionary<string, object?>>();
        }
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
            System.Reflection.PropertyInfo? prop = me?.GetType().GetProperty("Gold");
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

    internal static List<Dictionary<string, object?>> AvailableMapPoints(RunState runState)
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
}
