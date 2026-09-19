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

// Shared reflection probes and localization text helpers used by both the
// state DTO builders and the action executors.
public static class GameProbe
{
    internal static object? ProbeBool(object target, params string[] names)
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

    internal static string ModelName(AbstractModel model)
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

    internal static string StripBbcode(string text)
    {
        return System.Text.RegularExpressions.Regex.Replace(text, @"\[/?[^\]]+\]", "");
    }

    // Rest-site option classification shared by available_actions and the
    // rest/smith executors; callers pass the raw OptionId string.
    internal static bool RestOptionIsSmith(string optionId)
    {
        string oid = (optionId ?? "").ToUpperInvariant();
        return oid.Contains("SMITH") || oid.Contains("UPGRADE") || oid.Contains("MEND");
    }

    // Assign dto[key] = getter() and omit the key when the getter throws
    // (reflection miss on private game members) — the pervasive probe pattern.
    internal static void Set(Dictionary<string, object?> dto, string key, Func<object?> getter)
    {
        try
        {
            dto[key] = getter();
        }
        catch (Exception)
        {
            // omit: member not exposed on this build
        }
    }
}
