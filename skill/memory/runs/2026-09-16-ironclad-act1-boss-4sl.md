# Run postmortem — 2026-09-16 Ironclad Act1 boss 仪式兽

- Result: run ended frozen at floor 16 boss (仪式兽 57/252 remaining, player 6/87
  RINGING-locked; end_turn + abandon_run both no-op — combat thread stuck)
- Character: IRONCLAD (DEFECT/NECROBINDER/REGENT/SILENT still locked on profile)
- Logs: logs/run-20260916-001641.log + SL fragments; final profile fragment
  logs/run-20260916-004040.log
- Best line (4th SL attempt): R15 boss 57/252 at 6hp — farthest progress.
  R16 RINGING + intent 21 vs max block 7 = lethal even without the freeze.
- Framework profile (final fragment): rtt p50=7ms, settle p50=822ms,
  after-end_turn p50=1s, cadence 3.6s/act — latency budget healthy.
- SL: 17–18.6s reload, seed-identical hands/intents; used for stall recovery
  and foreknowledge (quality, not speed).

## Boss pattern (仪式兽 252hp, PLOW + STR scaling)

- Intent: R1 empty, then 18,20,22… +2/turn; empty-intent turns every ~3 rounds
  (damage windows). RINGING_POWER locks hand after first play on some turns
  (~R9/R12/R13/R16 this attempt) — lessons tactic: one card then end_turn.
- WHIRLWIND+ ~24 dmg/turn; FLAME_BARRIER 24 block; TORIC_TOUGHNESS 5 block +
  residual power; TRUE_GRIT ~7 block but exhausts next card.
- PLOW/RINGING end_turn freezes: fingerprint stuck; abandon also no-ops.
  Recovery = SL (room-entry reload). Recurred multiple times → run-ender.

## What killed the run

1. RINGING/PLOW end_turn freeze (game-side; no server force-advance yet).
2. Block package too thin for 252hp STR-scaling boss: even the best line only
   reached 57hp by R16 while player sat at 6hp with no heal left.

## Lessons / framework TODO

- Implement `force_advance_turn` in SpireBridge: clear RINGING-like locks via
  reflection, re-enqueue EndPlayerTurnAction, CheckWinCondition fallback.
- COLORLESS_POTION / POWER_POTION: no visible bridge-state effect — verify.
- Deck: 2×ARMAMENTS + WHIRLWIND + FLAME carried floors 1–15 well; boss needs
  either more burst (Bludgeon-class) or heal/relic sustain.

## Next

Postmortem committed; framework force_advance_turn queued; next run starts
immediately per continuous-play mandate.
