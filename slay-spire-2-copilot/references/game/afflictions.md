# Afflictions and statuses

Card-bound debuffs and status cards as they appear in deck/combat.

## Verified

- BYRDONIS_EGG (status card, Sapphire Seed / nest events): unplayable (-1
  cost), dead draw — remove via shop; HATCH rest option appears while in deck.
- SLIMED-type status cards: enemy-inflicted; some playable for minor effect.
- DECAY / WOUND: enemy/event statuses; playable for chip or SECOND_WIND fuel;
  shop-removal targets.
- RINGING (affliction): effect lives in RINGING_POWER — hand cards flip to
  can_play=false while on the player (observed in a boss fight).

## Reported

- BYRDONIS_EGG: HATCH interaction beyond the rest-option presence is pending
  re-test.

## Mechanics

- Most card-bound afflictions are pointers to their Power logic (e.g. Bound ->
  ChainsOfBindingPower, Ringing -> RingingPower) — read the power entry for the
  actual effect.
