# Afflictions and statuses

Card-bound afflictions, status cards, and curses. Every entry verified against
decompiled classes: afflictions in `MegaCrit.Sts2.Core.Models.Afflictions.*`,
cards in `MegaCrit.Sts2.Core.Models.Cards.*`, logic hosts in
`MegaCrit.Sts2.Core.Models.Powers.*`. "Ethereal" = vanishes if still in hand
at end of turn. "Unplayable" = cannot be played.

## Card-afflictions (attached to deck cards; logic lives in the host power)

- BOUND: host = CHAINS_OF_BINDING_POWER — afflicted cards are drawn up to the
  power's Amount per turn; only 1 Bound card may be played per turn; all
  Bound clears at end of your turn.
- ENTANGLED: host = TANGLED_POWER — Attack cards get Entangled; Entangled
  cards cost +Amount Energy; clears at end of your turn.
- GALVANIZED: host = GALVANIC_POWER (stackable) — Power cards get Galvanized
  (Amount); playing a Galvanized card deals Amount unpowered damage to its
  owner.
- HEXED: host = HEX_POWER — Hexed cards gain Ethereal keyword while the power
  exists; clears when the applier dies or the power is removed.
- RINGING: host = RINGING_POWER — a Ringing card is unplayable once any card
  has been played this turn; clears at end of your turn.
- SMOG: host = SMOGGY_POWER — Skill cards get Smog after you play a Skill;
  Smog cards are unplayable while the power exists; clears at end of your
  turn.
- TAINTED (stackable, Skill cards only): host = TAINTED_POWER — attacks
  against the power owner deal +Amount damage; the power itself is removed at
  end of Enemy side turn. (VitalSparkPower afflicts player Skill cards with
  Tainted and applies TaintedPower when a Tainted card is played.)

## Status cards

- SLIMED (Status): cost 1; on play draw 1 card, Exhausts.
- DAZED (Status): unplayable, Ethereal — vanishes if unplayed at end of turn.
  (PersonalHivePower injects Dazed cards into the attacker's draw pile.)
- WOUND (Status): unplayable; pure deck clog. **Run-35 live reconfirm (Vantom boss)**: 3 Wounds in hand through end of turn dealt ZERO HP damage — no Infection-class EOT tax; archive "pure deck clog" claim holds live.
- TOXIC (Status): cost 1, Exhausts; if still in hand at end of turn, deals 5
  unpowered damage to its owner (DamageVar 5).
- DISINTEGRATION (Status, KnowledgeDemon choice): cost -1, not generated in
  combat; when chosen, applies DISINTEGRATION_POWER 6 — lose 6 HP at end of
  your turn (unpowered), persistent while the power lasts.
- MIND_ROT (Status, KnowledgeDemon choice): cost -1; when chosen, applies
  MIND_ROT_POWER 1 — draw 1 fewer card per turn.
- SLOTH (Status, KnowledgeDemon choice): cost -1; when chosen, applies
  SLOTH_POWER 3 — play at most 3 cards per turn (counter resets at your turn
  start; display shows cards played this turn).
- WASTE_AWAY (Status, KnowledgeDemon choice): cost -1; when chosen, applies
  WASTE_AWAY_POWER 1 — max Energy reduced by 1.

## Curse cards

- ASCENDERS_BANE: unplayable, Ethereal, Eternal — cannot be removed normally.
- CURSE_OF_THE_BELL: unplayable, Eternal.
- CLUMSY: unplayable, Ethereal.
- INJURY: unplayable.
- DECAY: unplayable; if still in hand at end of turn, deals 2 unpowered
  damage to its owner (DamageVar 2).
- DOUBT: unplayable; if still in hand at end of turn, applies 1 WEAK_POWER to
  its owner (first application skips its next duration tick).
- REGRET: unplayable; at end of turn, if in hand, deals unblockable unpowered
  damage to owner equal to the number of cards in hand (counted at turn end).
- NORMALITY: unplayable; while it is in your hand, after you have played 3
  cards this turn you can play no more cards (limit 3 plays/turn).

## Status-synergy payoffs (cards that read Status cards)

- COMPACT (Defect): hand Status cards become Fuel + Block (card text).
- FLAK_CANNON: exhausts all Status cards, dealing damage per card removed.
- ITERATION: ITERATION_POWER — extra draw the first time you draw a Status
  card each turn.
- ROCKET_PUNCH: becomes free when a Status card is created.
- SMOKESTACK: SMOKESTACK_POWER — damages all enemies when a Status card is
  created.
- TRASH_TO_TREASURE: TRASH_TO_TREASURE_POWER — channels a random Orb when a
  Status card is created.

## Related powers (cross-reference powers.md)

- Chains/Ringing/Tangled/Galvanic/Hex/Smoggy/Tainted host powers, plus
  DISINTEGRATION_POWER, MIND_ROT_POWER, SLOTH_POWER, WASTE_AWAY_POWER,
  NO_DRAW_POWER, NO_ENERGY_GAIN_POWER — see powers.md for stack/hook details.
