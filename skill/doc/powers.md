# Powers (buffs/debuffs applied in combat)

Extracted from game sts2.xml (14 types). One entry per type.

- AccelerantPower: This power doesn't actually do anything on its own. Instead, the Poison power checks for this power and re-triggers itself if it's there.
- BackAttackLeftPower: This is just a marker power for <see cref="T:MegaCrit.Sts2.Core.Models.Powers.SurroundedPower"/> to check for.
- BackAttackRightPower: This is just a marker power for <see cref="T:MegaCrit.Sts2.Core.Models.Powers.SurroundedPower"/> to check for.
- ClarityPower: Draw an extra card at the beginning of your next N turns. This is distinct from <see cref="T:MegaCrit.Sts2.Core.Models.Powers.DrawCardsNextTurnPower"/> due to its stacking behavior.
- DrawCardsNextTurnPower: Draw an extra N cards at the beginning of your next turn. This is distinct from <see cref="T:MegaCrit.Sts2.Core.Models.Powers.ClarityPower"/> due to its stacking behavior.
- EscapeArtistPower: Just a visual timer for when <see cref="T:MegaCrit.Sts2.Core.Models.Monsters.ThievingHopper"/> will escape.
- FanOfKnivesPower: This power doesn't actually do anything on its own. Instead, the <see cref="T:MegaCrit.Sts2.Core.Models.Cards.Shiv"/> card checks for its existence and modifies its targeting.
- MockPhaseObserverPower: Test-only power that records <see cref="P:MegaCrit.Sts2.Core.Entities.Players.PlayerCombatState.Phase"/> at the moment each turn lifecycle hook fires. Tests should call <see cref="M:MegaCrit.Sts2.Core.Models.Powers.Mocks.MockPhaseObserverPower.ResetObservations"/> before each scenario and read <see cref="P:MegaCrit.Sts2.Core.Models.Powers.Mocks.MockPhaseObserverPower.Observations"/> after.
- ParryPower: This power doesn't actually do anything on its own. Instead, the <see cref="T:MegaCrit.Sts2.Core.Models.Cards.SovereignBlade"/> card checks for its existence and modifies its block.
- SeekingEdgePower: This power doesn't actually do anything on its own. Instead, Sovereign blade cards checks for this power and and changes its behavior based off of that
- TemporaryDexterityPower: This class represents a buff/debuff that gives/takes dexterity. We never instantiate this directly. See <see cref="T:MegaCrit.Sts2.Core.Models.Powers.TemporaryStrengthPower"/> for context around how this is used.
- TemporaryFocusPower: This class represents a buff/debuff that gives/takes focus. We never instantiate this directly. See <see cref="T:MegaCrit.Sts2.Core.Models.Powers.TemporaryStrengthPower"/> for context around how this is used.
- TemporaryStrengthPower: This class represents a buff/debuff that gives/takes strength. This class is never instantiated directly. Instead, it is subclassed and those classes represent the buff/debuff. Every model that grants a temporary strength power creates an associated power that subclasses this. For example, FlexPotion has FlexPotionPower which grants strength and then takes it away at the end of the turn. This used to be called Strength Down (or Restore Strength for negative strength) and be its own power. We switched to this model so make the UX more clear for players; both Strength and Temporary Strength are a buff.
- TheHuntPower: This power acts as a visual indicator to the player that the Hunt card was successful. The actual behavior lives in <see cref="T:MegaCrit.Sts2.Core.Models.Cards.TheHunt"/> .

## Known / observed (seeded during play)

- SLIPPERY_POWER (enemy, e.g. 墨宝): incoming attack damage greatly reduced (Strike 6 -> 1 observed);
  the charge appears consumed/removed after taking a hit — subsequent hits deal full damage. Verified live.
- VULNERABLE_POWER: target takes +50% attack damage for the duration (Strike 6 -> 9 vs vulnerable 墨宝). Verified live.
- PlatingPower / RegenPower: game-internal self-buffs used by AutoSlay smoke bot (huge flat block / regen per turn).

## Observed in Act 3 boss/elite runs (2026-09-15)

- WEAK_POWER: target deals ~25% less attack damage; intent display drops after application.
- VULNERABLE_POWER: target takes +50% attack damage; also amplifies incoming damage when on the player.
- FRAIL_POWER: reduces block gained; stacked with CHAINS_OF_BINDING observed zeroing block
  entirely in boss rounds despite DEFEND/SECOND_WIND plays (verify exact formula later).
- CHAINS_OF_BINDING_POWER: queen-boss debuff; suspected block-suppression component.
- MINION_POWER: boss flag; spawns replacement minion on death (factory/queen fights).
- STOCK_POWER: robot-assembly flag; each death spawned next robot variant until fight end.
- RITUAL_POWER / STRENGTH_POWER on enemies: per-turn strength growth — kill priority target.
- RAMPART_POWER: living-shield ally block-regeneration source.
- SLIPPERY_POWER: first-hit damage massively reduced; charges consumed per hit (potions strip too).
- TERRITORIAL_POWER / SOAR_POWER / BURROWED_POWER: elite/boss defensive stances; burrowed
  pairs with big charged intents that cancel if block broken in time.
- DEMON_FORM_POWER: player power — +strength per turn (upgraded); core engine.
- CONFUSED_POWER (from FAKE_SNECKO_EYE): hand costs randomized each draw — exploit 0-cost
  high cards; beware expensive basics.
- PLATING_POWER (GORGET): start-of-combat flat block; observed absorbing early hits.
- THORNS_POWER (BRONZE_SCALES): reflect damage on being attacked.
- FLAME_BARRIER_POWER: temporary thorns+block from FLAME_BARRIER card.
- DUPPLICATION_POWER (DUPLICATOR potion): temporary card-duplication state; redraw found
  lethal BASH at 2hp once.
- INFESTED_POWER (异蛙寄生虫 elite, run2 f7): on death spawns multiple 扭动虫
  adds (4x ~17-21hp observed). Save AOE (THUNDERCLAP/BREAKTHROUGH/WHIRLWIND)
  for the spawn wave instead of blowing it on the parent.
