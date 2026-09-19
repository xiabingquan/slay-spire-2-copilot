using System.Text.Json;

namespace SpireCopilot.Bridge;

// Wire protocol v1 envelopes (see references/bridge/protocol.md). State payloads are
// dictionary trees built on the game main thread by StateBuilder.
public static class Protocol
{
    public static readonly JsonSerializerOptions JsonOptions = new()
    {
        PropertyNamingPolicy = JsonNamingPolicy.SnakeCaseLower,
    };

    private static string Emit(object payload) => JsonSerializer.Serialize(payload, JsonOptions);

    public static string HelloOk(string gameVersion, long assemblyHash, string modVersion, string speedStatus) => Emit(new
    {
        type = "hello_ok",
        protocol_version = BridgeMod.ProtocolVersion,
        game_version = gameVersion,
        assembly_hash = assemblyHash,
        mod_version = modVersion,
        speed = speedStatus,
    });

    public static string Pong() => Emit(new { type = "pong" });

    public static string State(System.Collections.Generic.Dictionary<string, object?> state)
    {
        state["type"] = "state";
        state["protocol_version"] = BridgeMod.ProtocolVersion;
        state["game_version"] = BridgeMod.GetGameVersion();
        state["assembly_hash"] = BridgeMod.GetAssemblyHash();
        state["mod_version"] = BridgeMod.ModVersion;
        return Emit(state);
    }

    public static string ActResult(bool ok, string action, string message,
        System.Collections.Generic.Dictionary<string, object?>? state)
    {
        // Information-completeness envelope: surfaced top-level so the client
        // gate sees it without digging into state. info-incomplete failures
        // always carry notify_user=true — the client hard-stops and pings
        // Feishu (user directive 2026-09-19: no fallbacks, no uncertainty).
        bool notify = false;
        var missing = new System.Collections.Generic.List<string>();
        if (state != null)
        {
            if (state.TryGetValue("notify_user", out object? nu) && nu is bool b && b)
            {
                notify = true;
            }
            if (state.TryGetValue("missing_info", out object? mi) && mi is System.Collections.Generic.List<string> ml)
            {
                missing = ml;
            }
        }
        if (!ok && message.StartsWith("info incomplete", System.StringComparison.Ordinal))
        {
            notify = true;
            if (missing.Count == 0)
            {
                missing.Add(message);
            }
        }
        object payload = state == null
            ? new { type = "act_result", ok, action, message, notify_user = notify, missing_info = missing }
            : new { type = "act_result", ok, action, message, notify_user = notify, missing_info = missing, state };
        return Emit(payload);
    }

    // Injects game-thread timing into an already-emitted JSON object so the
    // client profiler can separate bridge RTT from queue wait + handler work.
    public static string InjectServerMs(string payload, long serverMs, long queueMs)
    {
        if (string.IsNullOrEmpty(payload) || !payload.EndsWith("}"))
        {
            return payload;
        }
        return payload.Substring(0, payload.Length - 1)
            + ",\"server_ms\":" + serverMs
            + ",\"queue_ms\":" + queueMs + "}";
    }

    public static string Error(string message, string? detail) => detail == null
        ? Emit(new { type = "error", message })
        : Emit(new { type = "error", message, detail });
}
