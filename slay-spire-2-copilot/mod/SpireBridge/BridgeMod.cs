using System;
using System.Text.Json;
using Godot;
using MegaCrit.Sts2.Core.Debug;
using MegaCrit.Sts2.Core.Logging;

namespace SpireCopilot.Bridge;

// Mod entry point. The game calls Init via ModInitializerAttribute on this
// class during bootstrap; we register our Godot node types, attach the
// main-thread dispatcher, and start the localhost TCP server.
[MegaCrit.Sts2.Core.Modding.ModInitializer("Init")]
public static class BridgeMod
{
    public const string ModId = "spire-copilot-bridge";
    public const string ModVersion = "0.4.2";
    public const int ProtocolVersion = 1;
    public const int DefaultPort = 17612;

    private static TcpServer? _server;

    // Information-completeness contract: pending card-reward choose
    // verification (set by ActionExecutor, resolved by StateBuilder).
    // See InfoCompleteness.cs — no fallbacks; unverified = incomplete.
    public static CardRewardVerifyPending? CardRewardVerifyPending;

    public static void Init()
    {
        try
        {
            LogInfo($"initializing (mod {ModVersion}, protocol {ProtocolVersion})");
            Godot.Bridge.ScriptManagerBridge.LookupScriptsInAssembly(typeof(BridgeMod).Assembly);
            if (Engine.GetMainLoop() is SceneTree tree && tree.Root != null)
            {
                tree.Root.CallDeferred("add_child", new GameDispatcher());
            }
            else
            {
                LogErr("scene tree unavailable at init; dispatcher not attached");
            }
            int port = DefaultPort;
            string envPort = OS.GetEnvironment("SPIREBRIDGE_PORT");
            if (int.TryParse(envPort, out int parsed) && parsed is > 0 and < 65536)
            {
                port = parsed;
            }
            _server = new TcpServer(port);
            _server.Start();
            LogInfo("init complete");
        }
        catch (Exception e)
        {
            LogErr($"init failed: {e}");
        }
    }

    // Runs on the game main thread via GameDispatcher for every request.
    internal static string HandleRequest(string line)
    {
        try
        {
            using JsonDocument doc = JsonDocument.Parse(line);
            if (!doc.RootElement.TryGetProperty("type", out JsonElement typeProp))
            {
                return Protocol.Error("missing type field", null);
            }
            string? type = typeProp.GetString();
            switch (type)
            {
                case "hello":
                    SpeedHooks.ApplyIfNeeded("hello");
                    return Protocol.HelloOk(GetGameVersion(), GetAssemblyHash(), ModVersion, SpeedHooks.Status());
                case "ping":
                    return Protocol.Pong();
                case "state":
                    return Protocol.State(StateBuilder.Build());
                case "act":
                {
                    if (!doc.RootElement.TryGetProperty("action", out JsonElement actionProp))
                    {
                        return Protocol.Error("missing action field", null);
                    }
                    string action = actionProp.GetString() ?? "";
                    bool hasArgs = doc.RootElement.TryGetProperty("args", out JsonElement args);
                    (bool ok, string message, var state) = ActionExecutor.Execute(action, hasArgs ? args : default);
                    return Protocol.ActResult(ok, action, message, state);
                }
                default:
                    return Protocol.Error("unknown request type", type);
            }
        }
        catch (JsonException e)
        {
            return Protocol.Error("invalid json", e.Message);
        }
        catch (Exception e)
        {
            LogErr($"request handler failed: {e}");
            return Protocol.Error("handler exception", e.Message);
        }
    }

    internal static string GetGameVersion()
    {
        try
        {
            return ReleaseInfoManager.Instance.ReleaseInfo?.Version ?? "unknown";
        }
        catch (Exception)
        {
            return "unknown";
        }
    }

    internal static long GetAssemblyHash()
    {
        try
        {
            return ReleaseInfoManager.Instance.ReleaseInfo?.MainAssemblyHash ?? 0;
        }
        catch (Exception)
        {
            return 0;
        }
    }

    internal static void LogInfo(string message) => Log.Info($"[{ModId}] {message}");

    internal static void LogErr(string message) => Log.Error($"[{ModId}] {message}");
}
