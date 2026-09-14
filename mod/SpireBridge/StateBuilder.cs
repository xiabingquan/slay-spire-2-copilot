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
using MegaCrit.Sts2.Core.Events;
using MegaCrit.Sts2.Core.Localization;
using MegaCrit.Sts2.Core.Map;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.MonsterMoves.Intents;
using MegaCrit.Sts2.Core.MonsterMoves.MonsterMoveStateMachine;
using MegaCrit.Sts2.Core.Nodes;
using MegaCrit.Sts2.Core.Nodes.Cards.Holders;
using MegaCrit.Sts2.Core.Nodes.Events;
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
using MegaCrit.Sts2.Core.Nodes.Screens.TreasureRoomRelic;
using MegaCrit.Sts2.Core.Runs;

namespace MimoSpire.Bridge;

// Builds the protocol state snapshot from live game objects. Runs only on the
// game main thread; never holds game references between calls. Field access to
// a few private screen members fails soft to index-only option lists.
public static class StateBuilder
{
    private static readonly FieldInfo? CardRewardOptionsField =
        typeof(NCardRewardSelectionScreen).GetField("_options", BindingFlags.Instance | BindingFlags.NonPublic);

    private static readonly FieldInfo? RelicChoiceField =
        typeof(NChooseARelicSelection).GetField("_relics", BindingFlags.Instance | BindingFlags.NonPublic);

    public static Dictionary<string, object?> Build()
    {
        RunState? runState = SafeRunState();
        CombatState? combat = SafeCombatState();
        Player? player = null;
        if (runState != null)
        {
            player = LocalContext.GetMe(runState.Players);
        }
        player ??= combat != null ? LocalContext.GetMe(combat) : null;

        string screen = DetectScreen(combat, out string screenType, out Node? screenNode);
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

    private static string DetectScreen(CombatState? combat, out string screenType, out Node? screenNode)
    {
        screenNode = null;
        screenType = "none";
        try
        {
            if (combat != null && CombatManager.Instance.IsInProgress)
            {
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
                NMainMenu => "menu",
                NCombatRoom => "combat",
                _ => "other",
            };
        }
        catch (Exception)
        {
            return "other";
        }
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
            ["map_coord"] = runState.CurrentMapCoord is { } coord ? CoordDto(coord) : null,
        };
        try
        {
            run["visited_coords"] = runState.VisitedMapCoords.Select(CoordDto).ToList();
        }
        catch (Exception)
        {
            run["visited_coords"] = new List<object?>();
        }
        run["available_map_points"] = AvailableMapPoints(runState);
        return run;
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
            ["relics"] = player.Relics.Select(r => new Dictionary<string, object?>
            {
                ["id"] = r.Id.Entry,
                ["name"] = ModelName(r),
            }).ToList(),
            ["potions"] = player.PotionSlots.Select((PotionModel? p, int i) => p == null
                ? null
                : new Dictionary<string, object?>
                {
                    ["index"] = i,
                    ["id"] = p.Id.Entry,
                    ["name"] = ModelName(p),
                    ["target_type"] = p.TargetType.ToString(),
                }).ToList(),
        };
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
        // Deck lives on the run player state; PlayerCombatState piles are combat-only.
        PropertyInfo? prop = player.GetType().GetProperty("Deck") ?? player.GetType().GetProperty("MasterDeck");
        if (prop?.GetValue(player) is IEnumerable<CardModel> deck)
        {
            return deck.Select((CardModel c, int i) => new Dictionary<string, object?>
            {
                ["index"] = i,
                ["id"] = c.Id.Entry,
                ["name"] = ModelName(c),
            }).ToList();
        }
        return new List<Dictionary<string, object?>>();
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
        }
        return new Dictionary<string, object?>
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
        if (creature.Monster is { } monster)
        {
            dto["move_id"] = SafeMoveId(monster);
            dto["intents"] = BuildIntents(monster, creature);
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
                var dto = new Dictionary<string, object?>
                {
                    ["type"] = intent.IntentType.ToString(),
                    ["class"] = intent.GetType().Name,
                };
                try
                {
                    dto["label"] = ResolveLoc(intent.GetIntentLabel(Array.Empty<Creature>(), owner));
                }
                catch (Exception)
                {
                    // intent label unavailable for this intent type
                }
                // Damage/hit counts live on undocumented intent subclasses; probe
                // common member names so state stays useful across game patches.
                foreach (string member in new[] { "Damage", "damage", "Hits", "hits", "HitCount", "Times" })
                {
                    MemberInfo? hit = intent.GetType().GetMember(member, BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic).FirstOrDefault();
                    object? value = hit switch
                    {
                        PropertyInfo p => p.GetValue(intent),
                        FieldInfo f => f.GetValue(intent),
                        _ => null,
                    };
                    if (value != null && (member is "Damage" or "damage" or "Hits" or "hits" or "HitCount" or "Times"))
                    {
                        dto[member is "Damage" or "damage" ? "damage" : "hits"] = value is decimal d ? (int)d : value;
                    }
                }
                intents.Add(dto);
            }
        }
        catch (Exception)
        {
            // intent enumeration failed; move state may be transitioning
        }
        return intents;
    }

    private static Dictionary<string, object?> PowerDto(PowerModel power)
    {
        var dto = new Dictionary<string, object?>
        {
            ["id"] = power.Id.Entry,
            ["name"] = ModelName(power),
        };
        foreach (string member in new[] { "Amount", "Stacks", "StackCount" })
        {
            if (power.GetType().GetProperty(member)?.GetValue(power) is { } v)
            {
                dto["amount"] = v is decimal d ? (int)d : v;
                break;
            }
        }
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
    // LocManager.SmartFormat via GetFormattedText.
    internal static string ResolveLoc(LocString loc)
    {
        try
        {
            string text = loc.GetFormattedText();
            if (!string.IsNullOrWhiteSpace(text))
            {
                return text;
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
                return raw;
            }
        }
        catch (Exception)
        {
            // raw table entry missing
        }
        return $"{loc.LocTable}:{loc.LocEntryKey}";
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
                "rewards" => RewardButtonOptions(screenNode),
                "event" => EventOptions(screenNode),
                "treasure" => TreasureOptions(screenNode),
                "rest" => RestOptions(screenNode),
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
        return options;
    }

    private static Dictionary<string, object?> CardResultOption(object result, int index)
    {
        var option = new Dictionary<string, object?>
        {
            ["kind"] = "card",
            ["index"] = index,
            ["id"] = ProbeModelId(result),
            ["name"] = ProbeModelId(result) ?? $"option_{index}",
        };
        return option;
    }

    private static string? ProbeModelId(object container)
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

    private static List<Dictionary<string, object?>> CardHolderOptions(Node? screenNode)
    {
        var options = new List<Dictionary<string, object?>>();
        if (screenNode == null)
        {
            return options;
        }
        List<NCardHolder> holders = UiHelper.FindAll<NCardHolder>(screenNode);
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
        List<NRewardButton> buttons = UiHelper.FindAll<NRewardButton>(screenNode);
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
            options.Add(new Dictionary<string, object?>
            {
                ["kind"] = "event_option",
                ["index"] = i,
                ["id"] = option.TextKey,
                ["name"] = ResolveLoc(option.Title),
                ["is_proceed"] = option.IsProceed,
            });
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
            case "card_reward":
            case "card_choice":
            case "deck_select":
            case "relic_choice":
            case "rewards":
            case "event":
            case "rest":
            {
                List<Dictionary<string, object?>> options =
                    ((BuildScreenDetail(screen, screenNode, runState, player)["options"] as List<Dictionary<string, object?>>)
                     ?? new List<Dictionary<string, object?>>());
                foreach (Dictionary<string, object?> option in options)
                {
                    string action = screen switch
                    {
                        "rest" => option["name"]?.ToString()?.ToLowerInvariant().Contains("smith") == true ? "smith" : "rest",
                        "event" => "choose",
                        "rewards" => "choose",
                        _ => "choose",
                    };
                    actions.Add(new Dictionary<string, object?>
                    {
                        ["action"] = action,
                        ["args"] = new Dictionary<string, object?> { ["index"] = option["index"] },
                    });
                }
                if (screen is "card_reward" or "card_choice" or "deck_select")
                {
                    actions.Add(new Dictionary<string, object?> { ["action"] = "skip", ["args"] = new Dictionary<string, object?>() });
                }
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
        string raw = string.Join("|",
            state["screen"]?.ToString() ?? "",
            state["screen_type"]?.ToString() ?? "",
            (state["combat"] as Dictionary<string, object?>)?["round"]?.ToString() ?? "",
            (state["combat"] as Dictionary<string, object?>)?["turn_phase"]?.ToString() ?? "",
            (state["run"] as Dictionary<string, object?>)?["total_floor"]?.ToString() ?? "",
            (state["run"] as Dictionary<string, object?>)?["act_floor"]?.ToString() ?? "",
            (state["run"] as Dictionary<string, object?>)?["gold"]?.ToString() ?? "",
            (state["run"] as Dictionary<string, object?>)?["room_type"]?.ToString() ?? "",
            (state["player"] as Dictionary<string, object?>)?["hp"]?.ToString() ?? "",
            ((state["combat"] as Dictionary<string, object?>)?["piles"] as Dictionary<string, object?>)?["hand"]?.ToString() ?? "",
            ((state["run"] as Dictionary<string, object?>)?["available_map_points"] as List<Dictionary<string, object?>>)?.Count.ToString() ?? "",
            ((state["screen_detail"] as Dictionary<string, object?>)?["options"] as List<Dictionary<string, object?>>)?.Count.ToString() ?? "");
        ulong hash = 14695981039346656037;
        foreach (char c in raw)
        {
            hash = (hash ^ c) * 1099511628211;
        }
        return hash.ToString("x16");
    }
}
