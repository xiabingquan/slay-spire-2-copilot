# Powers

Static combat buff/debuff reference; ids as they appear in state.

- VULNERABLE_POWER: target takes +50% attack damage; also amplifies incoming
  damage when on the player.
- WEAK_POWER: target deals ~25% less attack damage.
- FRAIL_POWER: reduces block gained; with CHAINS_OF_BINDING observed zeroing
  block entirely.
- SLIPPERY_POWER (e.g. 墨宝): first incoming hit greatly reduced (Strike 6 ->
  1); charges consumed per hit — later hits deal full damage.
- STRENGTH_POWER / RITUAL_POWER (enemy): per-turn strength growth — kill first.
- DEMON_FORM_POWER (player): +strength per turn; core engine.
- CONFUSED_POWER (FAKE_SNECKO_EYE): hand costs randomized each draw; exploit
  0-cost cards.
- PLATING_POWER (GORGET): start-of-combat flat block.
- THORNS_POWER (BRONZE_SCALES): reflect damage when attacked.
- FLAME_BARRIER_POWER: temporary thorns + block.
- DUPPLICATION_POWER (DUPLICATOR potion): temporary card-duplication state.
- INFESTED_POWER (异蛙寄生虫 elite): on death spawns multiple adds (4x ~17-21hp)
  — save AOE for the spawn wave.
- MINION_POWER: boss flag — spawns replacement minion on death.
- STOCK_POWER: robot-assembly flag — each death spawns next robot variant.
- RAMPART_POWER: living-shield ally block regeneration.
- RINGING_POWER (仪式兽 boss): on player, hand cards flip can_play=false —
  card-play lockout.
- SLOW_POWER (旧日雕像 elite): alternating slow (empty-intent) turns and heavy
  charged hits + strength growth; fortify before heavy turns.
- TERRITORIAL / SOAR / BURROWED_POWER: elite/boss defensive stances; burrowed
  pairs with big charged intents that cancel if block broken in time.
- SHRINK_POWER (缩小甲虫): reduces player attack damage until the enemy dies.
- CHAINS_OF_BINDING_POWER: queen-boss debuff; suspected block suppression.
- ClarityPower vs DrawCardsNextTurnPower: both draw next turn(s); Clarity
  spans the next N turns, DrawCardsNextTurn the next turn only.
- Inert marker powers exist (e.g. FanOfKnives checked by Shiv targeting) —
  presence alone can change card behavior.
