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

// Per-screen option extractors for screen_detail.options — the index spaces
// that available_actions and the choose executors must agree on.
public static class ScreenOptions
{
    internal static readonly FieldInfo? CardRewardOptionsField =
        typeof(NCardRewardSelectionScreen).GetField("_options", BindingFlags.Instance | BindingFlags.NonPublic);

    private static readonly FieldInfo? RelicChoiceField =
        typeof(NChooseARelicSelection).GetField("_relics", BindingFlags.Instance | BindingFlags.NonPublic);

    internal static Dictionary<string, object?> BuildScreenDetail(
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
                "hand_select" => ScreenDetect.HandSelectOptions(player, screenNode),
                "rewards" => RewardButtonOptions(player, screenNode),
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

    // Merchant inventory resolution shared by ShopOptions (state) and ShopBuy
    // (action): the room's own inventory, else a node scan of the given scope,
    // else a run-wide scan (event-embedded merchants).
    internal static NMerchantInventory? FindMerchantInventory(NMerchantRoom? room, Node? scope)
    {
        return room?.Inventory
            ?? (scope != null ? UiHelper.FindFirst<NMerchantInventory>(scope) : null)
            ?? (NRun.Instance != null ? UiHelper.FindFirst<NMerchantInventory>(NRun.Instance) : null);
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
        List<Dictionary<string, object?>> statePoints = RunDto.AvailableMapPoints(runState);
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
        string? id = GameProbe.ProbeModelId(result);
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
                ["name"] = GameProbe.ModelName(relic),
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
                ["id"] = GameProbe.ProbeModelId(holders[i]),
                ["name"] = GameProbe.ProbeModelId(holders[i]) ?? $"card_{i}",
            });
        }
        return options;
    }

    // Reward model probe (proposal 3): resolve the underlying reward object
    // via reflection (Reward / PotionReward members) instead of trusting raw
    // node names like @Control@30026. Potion rewards with full potion slots
    // are unclaimable — surface that as claimable:false, and choose fail-louds.
    internal static (string? RewardKind, string? ResolvedId, bool Claimable, string? Reason)
        ProbeReward(NRewardButton button, Player? player)
    {
        object? reward = null;
        try
        {
            Type bt = button.GetType();
            reward = bt.GetProperty("PotionReward")?.GetValue(button);
            reward ??= bt.GetProperty("Reward")?.GetValue(button);
        }
        catch (Exception)
        {
            // reflection miss: fall back to node-name identity
        }
        string? kind = reward?.GetType().Name;
        string? resolved = reward != null ? GameProbe.ProbeModelId(reward) : null;
        bool potionReward = (kind ?? "").Contains("Potion", StringComparison.OrdinalIgnoreCase);
        if (potionReward && player != null)
        {
            var slots = player.PotionSlots;
            bool anySlot = slots != null && slots.Count > 0;
            bool full = anySlot;
            if (anySlot)
            {
                foreach (var s in slots)
                {
                    if (s == null)
                    {
                        full = false;
                        break;
                    }
                }
            }
            if (full)
            {
                return (kind, resolved, false, "potion slots full");
            }
        }
        return (kind, resolved, true, null);
    }

    private static List<Dictionary<string, object?>> RewardButtonOptions(Player? player, Node? screenNode)
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
            (string? kind, string? resolved, bool claimable, string? reason) = ProbeReward(buttons[i], player);
            string nodeName = buttons[i].Name.ToString();
            var dto = new Dictionary<string, object?>
            {
                ["kind"] = "reward",
                ["index"] = i,
                ["id"] = resolved ?? nodeName,
                ["name"] = resolved ?? nodeName,
            };
            if (kind != null)
            {
                dto["reward_kind"] = kind;
            }
            if (!claimable)
            {
                dto["claimable"] = false;
                dto["reason"] = reason;
            }
            options.Add(dto);
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
                ["name"] = GameProbe.ResolveLoc(option.Title),
                ["is_proceed"] = option.IsProceed,
            };
            try
            {
                string? description = GameProbe.ResolveLoc(option.Description);
                if (!string.IsNullOrWhiteSpace(description))
                {
                    dto["description"] = GameProbe.StripBbcode(description);
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
                option["name"] = GameProbe.ResolveLoc(restOption.Title);
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
        NMerchantInventory? inventory = FindMerchantInventory(room, screenNode);
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
                string id = GameProbe.ProbeModelId(probeTarget) ?? entry.GetType().Name;
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
}
