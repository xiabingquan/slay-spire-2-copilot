# Run postmortem — 2026-09-15 Ironclad Act1 boss defeat

- Result: defeat, floor 16 Act 1 boss 同族神官 (190hp) + 2x 同族信徒 minions
- Character: IRONCLAD (DEFECT rotation target still locked on this profile)
- Logs: logs/run-20260915-234721.log (main), logs/run-20260916-000047.log (post-SL boss replay)
- Wall clock: ~23:47 start_run -> 00:02 game_over ≈ 15min (within 30min budget,
  including two mod rebuild/restarts for framework fixes + one SL reload)
- Framework profile (instrumented): act cadence p50 ~3s, after-end_turn gap p50=1s,
  settle p50~800ms, bridge rtt p50=8ms — historical runs were 30s+/act and 200s
  after end_turn

## What this run validated (framework)

1. FastMode=Instant + NonInteractiveMode hooks: doctor shows `speed=fast_mode=Instant
   nim=True`; animation waits no longer dominate.
2. Fingerprint content-hash fix: settle/play waits track hand/hp/powers; no more
   false stalls on mid-turn plays.
3. Combat-end win-condition force path: HAVOC kills no longer freeze combat;
   `end_turn (win-condition force path)` -> rewards in 655ms.
4. SL mechanism (user request): `spirectl sl` = stop/launch/continue_run,
   total 17.7s (stop 1.4s, launch 6.5s, settle 0.5s). Boss reload restored
   46hp + potions from room-entry save with seed-identical opening hand/intents.

## Run shape

- Floors 1-13 smooth: slime packs, shops (card removal + PERFECTED_STRIKE),
  rest sites (UPPERCUT then BLUDGEON upgrades), treasure (WAR_PAINT),
  events (BRAIN_LEECH HEADBUTT, JUNGLE_MAZE gold), elite-free path to boss.
- Floor 14 4-slime pack: first clear stalled on combat-end (pre-fix); SL replay
  used foreknowledge (headbutt 9hp slime instead of leaking 3hp) and finished
  cleaner at 16hp entering rest.
- Boss: MINION_POWER believers (58/59hp) + priest 190hp. First attempt died R5
  to 27 incoming vs 13hp. SL replay reached R6 at 3hp — FYSH_OIL revealed as
  STRENGTH+DEXTERITY buff, CURE_ALL as draw+energy potion — but all-attack hand
  could not block priest 10-dmg hits. Death at boss 101hp.

## What killed the run

Boss DPS race lost: deck had burst (BLUDGEON/UPPERCUT) but not enough block
consistency against 27-dmg turns once FRAIL/WEAK stacked. Minions were ignored
too long — 59hp STR minion contributed 7-9/turn for six rounds.

## Lessons

- SL is a first-class tool: reload on lethal-incoming hands; replay with known
  intents/draw order. Timing 17.7s is cheap insurance vs run loss.
- CURE_ALL = draw cards + bonus energy (not a heal). FYSH_OIL = +STR +DEX.
  Both are combat-tempo potions — spend them on the burst/defend turn, not panic.
- Boss with MINION_POWER adds: either kill adds to cut incoming, or bring
  reliable block every turn. Burst-only decks fold at ~R5-R6 when debuffs stack.
- Card-reward skip still broken server-side (named button not Skip/Pass);
  workaround = pick a card. Fix pending: dump screen node names on reward screens.

## Next framework targets

1. Card-reward skip button discovery (inspect node tree on NCardRewardSelectionScreen).
2. continue_run room-load race: launch/SL should wait for room screen, not just menu.
3. shop_leave async race: settle returns before leave lands (~0.5s late).
4. Keep profiling every run; target ≤30min full-run wall clock including SLs.
