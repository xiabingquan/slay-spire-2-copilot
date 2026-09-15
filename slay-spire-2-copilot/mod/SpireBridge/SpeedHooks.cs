using System;
using System.Linq;
using System.Reflection;
using MegaCrit.Sts2.Core.Saves;
using MegaCrit.Sts2.Core.Settings;

namespace SpireCopilot.Bridge;

// Game-side speed levers for the bridge decision loop. Applied whenever the
// client talks to us (hello/start_run) so animations never dominate run time.
// Research notes (docs/research/game-api-findings.md) recommend FastMode=Instant
// + FTUE off while the bridge is connected; NonInteractiveMode short-circuits
// the remaining Cmd.Wait / combat pause gates AutoSlay also relies on.
public static class SpeedHooks
{
    private static bool _loggedSignature;

    public static void Apply(string reason)
    {
        try
        {
            SaveManager? saves = SaveManager.Instance;
            if (saves?.PrefsSave == null)
            {
                BridgeMod.LogInfo($"speed hooks deferred ({reason}): SaveManager not ready");
                return;
            }
            saves.PrefsSave.FastMode = FastModeType.Instant;
            saves.SetFtuesEnabled(false);
            bool nim = ApplyNonInteractive();
            BridgeMod.LogInfo(
                $"speed hooks applied ({reason}): fast_mode={saves.PrefsSave.FastMode} ftue_off=true nim={nim}");
        }
        catch (Exception e)
        {
            BridgeMod.LogErr($"speed hooks failed ({reason}): {e}");
        }
    }

    public static void ApplyIfNeeded(string reason)
    {
        try
        {
            SaveManager? saves = SaveManager.Instance;
            if (saves?.PrefsSave != null && saves.PrefsSave.FastMode == FastModeType.Instant && NimActive() == true)
            {
                return;
            }
        }
        catch (Exception)
        {
            // fall through to Apply
        }
        Apply(reason);
    }

    public static bool NimActive()
    {
        try
        {
            Type? nim = FindNonInteractiveMode();
            if (nim == null)
            {
                return false;
            }
            const BindingFlags F = BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Static;
            PropertyInfo? prop = nim.GetProperty("IsActive", F);
            if (prop != null && prop.PropertyType == typeof(bool))
            {
                return (bool)(prop.GetValue(null) ?? false);
            }
            FieldInfo? field = nim.GetField("IsActive", F);
            return field != null && field.FieldType == typeof(bool) && (bool)(field.GetValue(null) ?? false);
        }
        catch (Exception)
        {
            return false;
        }
    }

    public static string Status()
    {
        try
        {
            SaveManager? saves = SaveManager.Instance;
            string fast = saves?.PrefsSave?.FastMode.ToString() ?? "unavailable";
            return $"fast_mode={fast} nim={NimActive()}";
        }
        catch (Exception e)
        {
            return $"speed_status_error={e.Message}";
        }
    }

    private static bool ApplyNonInteractive()
    {
        Type? nim = FindNonInteractiveMode();
        if (nim == null)
        {
            BridgeMod.LogErr("speed hooks: NonInteractiveMode type not found in sts2 assembly");
            return false;
        }
        const BindingFlags F = BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Static;
        if (!_loggedSignature)
        {
            string members = string.Join(", ",
                nim.GetMembers(F).Select(m => $"{m.MemberType}:{m.Name}"));
            BridgeMod.LogInfo($"speed hooks: NonInteractiveMode members [{members}]");
            _loggedSignature = true;
        }
        Type funcBool = typeof(Func<bool>);
        foreach (string name in new[] { "AutoSlayerCheck", "BridgeCheck", "OverrideCheck", "Check" })
        {
            PropertyInfo? prop = nim.GetProperty(name, F);
            if (prop != null && prop.CanWrite && prop.PropertyType == funcBool)
            {
                prop.SetValue(null, (Func<bool>)(() => true));
                BridgeMod.LogInfo($"speed hooks: NonInteractiveMode.{name} => true");
                return NimActive() || prop.GetValue(null) != null;
            }
            FieldInfo? field = nim.GetField(name, F);
            if (field != null && field.FieldType == funcBool)
            {
                field.SetValue(null, (Func<bool>)(() => true));
                BridgeMod.LogInfo($"speed hooks: NonInteractiveMode.{name} => true");
                return NimActive() || field.GetValue(null) != null;
            }
        }
        // Last resort: any writable static bool that gates IsActive.
        foreach (FieldInfo field in nim.GetFields(F).Where(f => f.FieldType == typeof(bool) && !f.IsInitOnly))
        {
            if (field.Name.Contains("Active", StringComparison.OrdinalIgnoreCase)
                || field.Name.Contains("Enabled", StringComparison.OrdinalIgnoreCase))
            {
                field.SetValue(null, true);
                BridgeMod.LogInfo($"speed hooks: NonInteractiveMode.{field.Name} = true");
            }
        }
        return NimActive();
    }

    private static Type? FindNonInteractiveMode()
    {
        Assembly asm = typeof(SaveManager).Assembly;
        return asm.GetTypes().FirstOrDefault(t => t.Name == "NonInteractiveMode");
    }
}
