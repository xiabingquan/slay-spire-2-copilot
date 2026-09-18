using System.Collections.Generic;

namespace SpireCopilot.Bridge;

// Information-completeness contract (user directive 2026-09-19):
//   every field the server returns must equal what a player can read in-game;
//   zero uncertainty, zero fallbacks; if information is incomplete the client
//   hard-stops and notifies the user via Feishu instead of playing through it.
//
// Two flag scopes, both game-thread only:
//   RequestFlags — raised while executing an action (e.g. choose refused
//                  because the option id could not be resolved). They survive
//                  into the StateBuilder.Build() that follows the action, get
//                  reported once on that state payload, then clear.
//   BuildFlags   — raised while assembling state (reflection misses, empty
//                  branch tables, unresolved option ids). Cleared at the start
//                  of every Build and re-detected fresh each time, so a
//                  persistent structural gap re-flags on every state read.
public static class InfoCompleteness
{
    private static readonly List<string> RequestFlags = new();
    private static readonly List<string> BuildFlags = new();

    // Called at the top of StateBuilder.Build(). Does NOT clear RequestFlags —
    // those belong to the action that just executed and must appear on the
    // state payload returned with that action's result.
    public static void BeginBuild() => BuildFlags.Clear();

    public static void FlagDuringAction(string what)
    {
        if (!RequestFlags.Contains(what))
        {
            RequestFlags.Add(what);
        }
        BridgeMod.LogErr($"info-incomplete (action): {what}");
    }

    public static void FlagDuringBuild(string what)
    {
        if (!BuildFlags.Contains(what))
        {
            BuildFlags.Add(what);
        }
        BridgeMod.LogErr($"info-incomplete (build): {what}");
    }

    // Merged snapshot for the state payload; request flags are consumed after
    // this call so they are reported exactly once.
    public static List<string> DrainForState()
    {
        var merged = new List<string>(RequestFlags);
        foreach (string f in BuildFlags)
        {
            if (!merged.Contains(f))
            {
                merged.Add(f);
            }
        }
        RequestFlags.Clear();
        return merged;
    }
}

// Card-reward choose verification. Run-44 live (2026-09-19) showed the printed
// reward option order diverging from the card actually applied to the deck
// (PARSE -> BLADE_DANCE+, PHOTON_CUT -> WHIRLWIND, …). A press without a
// verified outcome is not information — the next Build resolves this pending
// record against the deck delta; anything other than a clean one-card delta
// raises an incomplete-info flag (client stops + Feishu, never guesses).
public sealed class CardRewardVerifyPending
{
    public CardRewardVerifyPending(int index, string requestedId, List<string> deckBefore)
    {
        Index = index;
        RequestedId = requestedId;
        DeckBefore = deckBefore;
    }

    public int Index { get; }
    public string RequestedId { get; }
    public List<string> DeckBefore { get; }
    public int BuildsOnScreen { get; set; }
}
