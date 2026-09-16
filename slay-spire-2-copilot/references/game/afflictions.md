# Afflictions and statuses

Card-bound debuffs and status cards. Sources: gamerblurb status-card list,
local xml affliction classes, spire-codex, play on v0.107.1.

## Card-bound afflictions (logic hosts)

- BOUND: logic lives in CHAINS_OF_BINDING_POWER — block suppression (queen-boss debuff).
- ENTANGLED: logic lives in TANGLED_POWER.
- GALVANIZED: logic lives in GALVANIC_POWER.
- HEXED: logic lives in HEX_POWER.
- RINGING: logic lives in RINGING_POWER — hand cards flip can_play=false (card-play lockout).
- SMOG: logic lives in SMOGGY_POWER.
- TAINTED: logic lives in TAINTED_POWER.

## Status cards

- BECKON: playable, no extra cost; lose 6 HP if still in hand at end of turn.
- BURN: unplayable; deal 2 damage to you if in hand at end of turn.
- DAZED: unplayable; Ethereal — vanishes if unplayed at end of turn.
- DEBRIS: playable, 1 energy; Exhausts when played.
- DISINTEGRATION: playable; deal 6 damage to you at end of turn.
- FRANTIC_ESCAPE: playable, 1 energy; raises Sandpit by 1; costs 1 more each time used.
- INFECTION: unplayable; deal 3 damage to you if in hand at end of turn.
- MIND_ROT: playable; reduce your card draw by 1 each turn.
- SLIMED: playable, 1 energy; draw 1 card; Exhausts.
- SLOTH: playable; limits you to at most 3 cards played per turn.
- SOOT: unplayable; clogs hand/deck (Biiig Hug relic adds these on shuffle).
- TOXIC: playable, 1 energy; deal 5 damage if in hand at end of turn, then Exhausts.
- VOID: unplayable; Ethereal; drawing it costs Colorless Energy (TURBO discard fodder).
- WASTE_AWAY: playable; grant 1 less Colorless Energy per turn.
- WOUND: unplayable; clogs hand/deck — SECOND_WIND fuel.
- BYRDONIS_EGG: unplayable (-1 cost) dead draw from nest/Sapphire Seed events;
  HATCH rest option appears while in deck; remove via shop.

## Status-synergy cards (payoffs)

- COMPACT (Defect): hand Status cards become Fuel + Block.
- FLAK_CANNON: exhaust all Status cards, dealing damage per card removed.
- ITERATION: extra draw the first time you draw a Status card each turn.
- ROCKET_PUNCH: becomes free when a Status card is created.
- SMOKESTACK: damages all enemies whenever a Status card is created.
- TRASH_TO_TREASURE: channels a random Orb on Status card creation.
