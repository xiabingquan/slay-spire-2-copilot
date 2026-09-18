using System;
using System.Linq;
using System.Reflection;
using MegaCrit.Sts2.Core.Saves;
using MegaCrit.Sts2.Core.Settings;

namespace SpireCopilot.Bridge;

// Game-side speed levers for the bridge decision loop. Applied on hello and
// start_run: FTUE off + NonInteractiveMode short-circuits remaining Cmd.Wait
// and combat-pause gates. FastMode is forced to a NON-Instant value:
// FastMode=Instant wedges PunchOff-class event cinematics — PunchEachOther's
// particle spawns stay null under Instant and the async loop spins forever
// (run-37, floor 7 PunchOff hard-wedge, reproduced on relaunch). Prefs may
// already hold Instant from earlier sessions, so overwrite explicitly.
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
            string fastBefore = saves.PrefsSave.FastMode.ToString();
            saves.PrefsSave.FastMode = PickNonInstantFastMode();
            saves.SetFtuesEnabled(false);
            // NIM must stay OFF: PunchOff.PunchEachOther's particle spawns are
            // gated on animation waits that NonInteractiveMode short-circuits —
            // with nim=true the cinematic null-loops even at FastMode=Fast
            // (run-37 live test: fast_mode=Fast->Fast nim=true still wedged).
            bool nim = ApplyNonInteractiveOff();
            BridgeMod.LogInfo(
                $"speed hooks applied ({reason}): fast_mode={fastBefore}->{saves.PrefsSave.FastMode} ftue_off=true nim_off={nim}");
        }
        catch (Exception e)
        {
            BridgeMod.LogErr($"speed hooks failed ({reason}): {e}");
        }
    }

    // Prefer Fast, then Normal, then any non-Instant enum member. Never Instant:
    // event cinematics (PunchOff.PunchEachOther) infinite-loop on null particles.
    private static FastModeType PickNonInstantFastMode()
    {
        foreach (string name in new[] { "Fast", "Normal", "Default", "Slow" })
        {
            try
            {
                FastModeType parsed = (FastModeType)Enum.Parse(typeof(FastModeType), name);
                if (parsed.ToString() != "Instant")
                {
                    return parsed;
                }
            }
            catch (Exception)
            {
                // name not in this build's enum — try the next candidate
            }
        }
        foreach (FastModeType value in Enum.GetValues(typeof(FastModeType)))
        {
            if (value.ToString() != "Instant")
            {
                return value;
            }
        }
        // Only reachable if the enum is Instant-only; leave whatever is set.
        return FastModeType.Instant;
    }

    public static void ApplyIfNeeded(string reason)
    {
        try
        {
            SaveManager? saves = SaveManager.Instance;
            if (saves?.PrefsSave != null
                && saves.PrefsSave.FastMode.ToString() != "Instant"
                && NimActive() == false)
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

    private static bool ApplyNonInteractiveOff()
    {
        Type? nim = FindNonInteractiveMode();
        if (nim == null)
        {
            // Type missing = NIM cannot be active; treat as off.
            return true;
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
                prop.SetValue(null, (Func<bool>)(() => false));
                BridgeMod.LogInfo($"speed hooks: NonInteractiveMode.{name} => false");
                break;
            }
            FieldInfo? field = nim.GetField(name, F);
            if (field != null && field.FieldType == funcBool)
            {
                field.SetValue(null, (Func<bool>)(() => false));
                BridgeMod.LogInfo($"speed hooks: NonInteractiveMode.{name} => false");
                break;
            }
        }
        // Belt-and-braces: force any Active/Enabled static bool false too.
        foreach (FieldInfo field in nim.GetFields(F).Where(f => f.FieldType == typeof(bool) && !f.IsInitOnly))
        {
            if (field.Name.Contains("Active", StringComparison.OrdinalIgnoreCase)
                || field.Name.Contains("Enabled", StringComparison.OrdinalIgnoreCase))
            {
                try
                {
                    field.SetValue(null, false);
                    BridgeMod.LogInfo($"speed hooks: NonInteractiveMode.{field.Name} = false");
                }
                catch (Exception)
                {
                    // backing field may reject direct set; the delegate above is primary
                }
            }
        }
        return NimActive() == false;
    }

    private static Type? FindNonInteractiveMode()
    {
        Assembly asm = typeof(SaveManager).Assembly;
        return asm.GetTypes().FirstOrDefault(t => t.Name == "NonInteractiveMode");
    }
}
