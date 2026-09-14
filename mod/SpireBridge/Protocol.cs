using System.Text.Json;

namespace MimoSpire.Bridge;

// Wire protocol v1 envelopes (see docs/protocol.md). State payloads are
// dictionary trees built on the game main thread by StateBuilder.
public static class Protocol
{
    public static readonly JsonSerializerOptions JsonOptions = new()
    {
        PropertyNamingPolicy = JsonNamingPolicy.SnakeCaseLower,
    };

    private static string Emit(object payload) => JsonSerializer.Serialize(payload, JsonOptions);

    public static string HelloOk(string gameVersion, long assemblyHash, string modVersion) => Emit(new
    {
        type = "hello_ok",
        protocol_version = BridgeMod.ProtocolVersion,
        game_version = gameVersion,
        assembly_hash = assemblyHash,
        mod_version = modVersion,
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
        object payload = state == null
            ? new { type = "act_result", ok, action, message }
            : new { type = "act_result", ok, action, message, state };
        return Emit(payload);
    }

    public static string Error(string message, string? detail) => detail == null
        ? Emit(new { type = "error", message })
        : Emit(new { type = "error", message, detail });
}
