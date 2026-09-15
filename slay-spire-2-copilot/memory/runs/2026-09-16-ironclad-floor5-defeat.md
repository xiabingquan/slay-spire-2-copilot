# Run postmortem — 2026-09-16 Ironclad floor 5 defeat

- Result: defeat floor 5 Act 1, 毛绒伏地虫 (worm 19/56 remaining, STR-stacked)
- Character: IRONCLAD (DEFECT/NECROBINDER rotation targets still locked)
- Logs: logs/run-20260915-030647.log (active pointer; SL rotates fragments)
- Wall clock: ~00:00 start_run -> ~00:35 game_over ≈ 35min including 2 SL
  reloads (~18s each) + quality decision time on dangerous turns
- Priority (user directive): floors/score > stable play > framework latency.
  No suicides to hit clocks; SL used to retry a losing fight, not to speed.

## Play quality notes

- Floors 1-4 clean at good HP (56/80 entering floor 5) after SHRUG/RAGE picks
  and a transform event (RAMPAGE; event cost 9hp).
- Floor 5 pack (shrink beetle 40 + STR worm 56) is a deck-check: SHRINK cuts
  output, worm scales to 18-25 dmg/turn. Two SL retries with full foreknowledge
  (same seed hands/intents) both died around R9-R10 — once at 10hp vs 27hp worm,
  once at 3hp vs 27hp worm. Best line found: kill beetle by R5, max-block worm
  turns (rage+shrug+2defend ≈ 18-21), race on empty-intent turns.
- POWER_POTION use showed no visible buff in bridge state (verify what it grants).
- Card-reward skip still broken server-side — forced into mediocre picks
  (PILLAGE/HAVOC line) instead of skip.

## Framework metrics this run

- Bridge rtt/settle stayed ~1-8ms / ~800ms; end_turn → play p50 ~0.7s.
- SL reload 17.6-18.5s end-to-end — first-class recovery/info tool.
- One combat freeze (~fingerprint stuck mid-fight pre-SL); SL cleared it.
- Remaining tooling gaps: card_reward skip node discovery; continue_run
  room-load wait; shop_leave async settle; POWER_POTION effect visibility.

## Lesson

- Weak defensive packages fold to STR-scaling multi-enemy floors even with
  correct targeting — prioritize block/relic/heal picks before Act1 mid-boss
  packs when the deck is still strike-heavy.
