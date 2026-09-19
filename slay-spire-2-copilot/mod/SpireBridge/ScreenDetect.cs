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

// Screen detection: which UI surface is live (combat overlays, hand-select
// mode, map/rewards/shop screens) plus the hand-selection reflection probes.
public static class ScreenDetect
{
    private static readonly FieldInfo? HandSelectedCardsField =
        typeof(NPlayerHand).GetField("_selectedCards", BindingFlags.NonPublic | BindingFlags.Instance);

    private static readonly FieldInfo? HandPrefsField =
        typeof(NPlayerHand).GetField("_prefs", BindingFlags.NonPublic | BindingFlags.Instance);

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
            Dictionary<string, object?> dto = CombatDto.CardDto(cards[i], i, player);
            dto["kind"] = "hand_card";
            dto["selected"] = selected.Contains(cards[i]);
            dto["select_min"] = min;
            dto["select_max"] = max;
            options.Add(dto);
        }
        return options;
    }

    internal static string DetectScreen(CombatState? combat, out string screenType, out Node? screenNode)
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
}
