# Powers

Combat buffs/debuffs as they appear in state (power ids). Verified effects
first; reported claims marked.

## Verified

- VULNERABLE_POWER: target takes +50% attack damage (Strike 6 -> 9); also
  amplifies incoming damage when on the player.
- WEAK_POWER: target deals ~25% less attack damage; intent display drops after
  application.
- FRAIL_POWER: reduces block gained; stacked with CHAINS_OF_BINDING observed
  zeroing block entirely (exact formula unverified).
- SLIPPERY_POWER (e.g. 墨宝): first-hit incoming attack damage greatly reduced
  (Strike 6 -> 1); charges consumed per hit (potions strip too) — subsequent
  hits deal full damage.
- STRENGTH_POWER / RITUAL_POWER on enemies: per-turn strength growth — kill
  priority target.
- DEMON_FORM_POWER (player): +strength per turn (upgraded); core engine.
- CONFUSED_POWER (from FAKE_SNECKO_EYE): hand costs randomized each draw —
  exploit 0-cost cards; beware expensive basics.
- PLATING_POWER (GORGET): start-of-combat flat block; observed absorbing early hits.
- THORNS_POWER (BRONZE_SCALES): reflect damage on being attacked.
- FLAME_BARRIER_POWER: temporary thorns + block from the FLAME_BARRIER card.
- DUPPLICATION_POWER (DUPLICATOR potion): temporary card-duplication state.
- INFESTED_POWER (异蛙寄生虫 elite): on death spawns multiple adds (4x ~17-21hp
  observed) — save AOE for the spawn wave, not the parent.
- MINION_POWER: boss flag; spawns replacement minion on death (factory/queen fights).
- STOCK_POWER: robot-assembly flag; each death spawns next robot variant until
  fight end.
- RAMPART_POWER: living-shield ally block-regeneration source.
- RINGING_POWER (仪式兽 boss debuff): on player, remaining hand cards flipped
  to can_play=false — card-play lockout suspected; duration/counterplay
  unverified.
- SLOW_POWER (旧日雕像 elite): alternating cadence — empty-intent slow turns
  then 23-dmg charged hits + strength growth; fortify before heavy turns.
- TERRITORIAL_POWER / SOAR_POWER / BURROWED_POWER: elite/boss defensive
  stances; burrowed pairs with big charged intents that cancel if block broken
  in time.
- SHRINK_POWER (缩小甲虫): reduces player attack damage until the enemy dies
  (observed).

## Reported

- CHAINS_OF_BINDING_POWER: queen-boss debuff; suspected block-suppression
  component.

## Mechanics

- ClarityPower vs DrawCardsNextTurnPower: both draw extra cards next turn(s);
  stacking behavior differs — Clarity spans the next N turns,
  DrawCardsNextTurn applies to the next turn only.
- Several powers are inert markers consulted by other cards (e.g. FanOfKnives
  checked by Shiv targeting) — presence alone can change card behavior.
