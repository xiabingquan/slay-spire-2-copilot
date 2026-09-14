# Iteration changelog

Newest entries at the bottom. One line per change: date, nature, cause, fix.

- 2026-09-14 [feature] initial SpireBridge mod v0.1.0, spirectl v0, skill memory
  seeded. Mod built against game v0.107.1 (sts2.dll); CardCmd.AutoPlay path used
  because TryManualPlay does not exist on this game build.
- 2026-09-14 [fix] handshake BOM crash: C# StreamWriter(Encoding.UTF8) emitted a
  UTF-8 BOM that json.loads rejected. spirectl strips BOM per line; mod uses
  UTF8Encoding(false). Mod fix takes effect on next game launch.
