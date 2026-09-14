# Playing lessons

Short, generalizable, actionable. Add only after a run end or a mid-run
breakthrough; remove entries that prove wrong.

## Combat

- Read intents before playing: if incoming damage exceeds HP+block, prioritize
  block or kill the attacker this turn.
- Hand indices are volatile: re-read state after every act; never reuse an index
  from a previous snapshot.
- The game's can_play flag is authoritative — trust it over manual energy math
  (the bridge energy field has lagged behind real energy).
- Multi-enemy fights: killing a low-HP attacker this turn beats spreading damage,
  even when a bigger enemy has scarier stats.
- Status-only enemy intents (no damage) are free turns to set up powers/block.

## Rewards and deck

- Skip is a valid choice; a deck that stays consistent beats one stuffed with
  situational rares.
- Starter deck saturated on strikes: prefer block/utility picks (BLOOD_WALL paid
  off immediately in the next fight).
- Strength engines (INFLAME) scale every future strike — high priority for Ironclad.

## Map and events

- Frontier options may be the only path; Unknown (?) rooms resolved to events or
  combat — both handled fine by the loop.
- Event options with unreadable text: decide on option keys + STS event archetypes
  (TAKE-type options grant relics/cards, often with a deck cost).
- Treasure rooms are map-luck; don't stall a run hunting one.

## Tooling

- After any act, if wait times out, re-read state directly — fingerprint changes
  can lag option-page transitions.
