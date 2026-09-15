# 2026-09-15 run2 — Ironclad, Act 2 elite defeat (game over, notified)

Result: DEFEATED floor 26 act 2 elite 感染棱柱 (Infected Prism, VITAL_SPARK_POWER)
round 4 — 3hp vs 8 incoming, no block card in final hand. Detailed JSON log:
logs/ (run-20260915-*.log, the active pointer file at time of death).

## Run trajectory

- Act 1: boss 仪式兽 (Ritual Beast, 252hp) killed on replay4 round 8 — RINGING
  one-hit tactic + step-discipline + sync-queue end_turn after 3 stall-replays
- Act 2 floors 18-25: 9hp bowl-bug survival clear (IMPERVIOUS anchor), LOST_WISP
  event re-claim, lantern-key RETURN branch (+100g), brain-leech HEADBUTT pick,
  shop haul (TEA_SET/WEAK_POTION/DECAY-removal), tunnel-bug 14hp survival
  (burrow-cancel validated), rest heal 15->39, chest AMETHYST_AUBERGINE
- Act 2 elite f26: Infected Prism 161hp — VITAL_SPARK mitigated damage/blocked
  per-turn; no IMPERVIOUS in dying hand; 3hp vs 8 = death

## Final loadout

- 8 relics: BURNING_BLOOD, LASTING_CANDY, SPARKLING_ROUGE, CHANDELIER,
  TUNING_FORK, LOST_WISP, VENERABLE_TEA_SET, AMETHYST_AUBERGINE
- Engine: PYRE (energy) + IMPERVIOUS + BODY_SLAM x2 + HEADBUTT + RAMPAGE +
  THUNDERCLAP x2 + upgraded POMMEL/BASH-era core; potions unused at death
  (GAMBLERS_BREW/ENERGY_POTION — energy potion never fired in final turn)

## Lessons (postmortem summary)

- VITAL_SPARK elite: block-regen + damage mitigation — needs sustained AOE/attrition
  plan and block cards each turn; treat as long-fight check, not burst target.
- At critical hp with no block in hand, potions are the last lever — ENERGY_POTION
  could have enabled extra plays; GAMBLERS_BREW remained untested-effect even at death.
- Run2 life-extension toolkit (IMPERVIOUS/BODY_SLAM/tea-set rests) carried the run
  20+ floors past its first near-death — tools work; the edge cases (RINGING hands,
  block-less draws) remain the killers.

## Server status at run end

All screens encountered this run supported live: combat/map/rewards/card rewards/
events (wisp/lantern-key/brain-leech/jungle-maze/chaos-transform)/shop (item_id
buys+removal)/treasure/rest(heal+smith)/selection screens/deck-select confirms.
Sync end_turn path and any-state takeover chain both live-validated.
