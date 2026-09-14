# Iteration changelog

Newest entries at the bottom. One line per change: date, nature, cause, fix.

- 2026-09-14 [feature] initial SpireBridge mod v0.1.0, spirectl v0, skill memory
  seeded. Mod built against game v0.107.1 (sts2.dll); CardCmd.AutoPlay path used
  because TryManualPlay does not exist on this game build.
- 2026-09-14 [fix] handshake BOM crash: C# StreamWriter(Encoding.UTF8) emitted a
  UTF-8 BOM that json.loads rejected. spirectl strips BOM per line; mod uses
  UTF8Encoding(false).
- 2026-09-14 [fix] map points stuck disabled after automated run start: nothing
  in the menu-automation path calls NMapScreen.SetTravelEnabled(true), and
  OnRelease/ForceClick no-op unless IsTravelable. map_select now sets travel
  (falling back to debug travel when Hook.ShouldProceedToNextMapPoint declines)
  and selects via NMapScreen.OnMapPointSelectedLocally (enqueues
  VoteForMapCoordAction). First map selection targets min-row points like AutoSlay.
- 2026-09-14 [feature] continue_run action for resuming saved runs from the menu.
- 2026-09-14 [fix] Steam launch race: direct .app open without a fully booted
  Steam client triggers "Steam init failed". spirectl launch now waits for
  steam_osx + Steam Helper/steamwebhelper processes and only uses
  steam://rungameid URLs.
- 2026-09-14 [fix] doctor false-OK during mod warm-up: bridge answers
  {"type":"error","message":"dispatcher not ready"} before GameDispatcher._Ready;
  doctor and launch now require type==hello_ok.
- 2026-09-14 [fix] LocString labels rendered as table metadata in state options
  and intents: resolve via LocString.GetFormattedText()/GetRawText() instead of
  ToString(); Godot node names serialized as objects -> Name.ToString().
- 2026-09-14 [fix] fingerprint blind to event option-page transitions: include
  act_floor, gold, and screen_detail option count in the hash input.
- 2026-09-14 [docs] acceptance session recorded (skill/memory/runs/
  2026-09-14-acceptance-session.md): two combat victories, reward and event
  decisions, map routing all verified through spirectl; energy display bug and
  untested treasure path logged as open gaps.
