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
