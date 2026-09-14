# Relics

Extracted from game sts2.xml (3 types). One entry per type.

- DeprecatedRelic: Represents a relic that has been removed from the game. Mostly used for the run history.
- UndyingSigil: This relic doesn't actually _do_ anything; Doom checks for its existence and makes enemy Doom trigger at the start of the enemy's turn instead of the end of the enemy's turn (so enemies die before they can attack).
- VakuuCardSelector: Card selector used by Vakuu (via WhisperingEarring) during auto-play. Selects cards in row-major order (top-left to bottom-right).

## Known / observed (seeded during play)

- BURNING_BLOOD (Ironclad starter): heal 6 HP at end of combat. Verified live 2026-09-14.
- VAJRA: seen in shop (154g). STS1 effect: +1 Strength at combat start. STS2 unverified.
- PANTOGRAPH: seen in shop (236g). STS1 effect: full heal entering boss combat. STS2 unverified.
- LEES_WAFFLE: seen in shop (229g). STS1 effect: heal on pickup / interactable. STS2 unverified.
- GORGET: chest relic floor 9. STS1 effect: start combat with 3 Block. STS2 unverified — observe next fights.
- VAJRA: elite drop floor 11 (shop had it at 154g). STS1: +1 Strength at combat start. Pending live verify.
- ODDLY_SMOOTH_STONE: chest relic floor 24 act 2. STS1: +1 Dexterity at combat start. Verify in next combat block values.
- Hatch rest-site option (孵化): appears only while BYRDONIS_EGG-type card is in deck
  (observed floor 8 with egg present, absent floor 25 after egg removal). Interaction
  unverified — re-test when a future egg event occurs.
- LOST_WISP: gained from LOST_WISP event "claim" option floor 27 act 2. Effect pending observation.
- FAKE_SNECKO_EYE: bought from NFakeMerchant event (54g). Fake relic — effects/trap pending observation.
- WONGOS_MYSTERY_TICKET: Wongos event mystery box (300g) floor 28 act 2. Function pending observation — possible later redemption.
- VENERABLE_TEA_SET / REGAL_PILLOW / NUNCHAKU: owl judge (floor 34 act 3) relic
  drops. STS1 refs: tea set+pillow boost rest-site recovery; nunchaku grants
  energy on attack counts. STS2 effects pending observation.
- BAG_OF_PREPARATION: chest relic floor 38 act 3. STS1: draw +2 on first turn of combat.
- HAPPY_FLOWER: shop relic act 3 (175g). STS1: +1 energy every 3rd turn.
- ORNAMENTAL_FAN: elite drop floor 41. STS1: +1 dex per 3 attacks.
- STRIKE_DUMMY: elite relic floor 43 act3. STS1: +1 strength at combat start.
- JUNGLE_MAZE_ADVENTURE event (run2 f4): solo quest traded 18hp for +147 gold
  instantly (80->62, 7->154). Join-forces alternative unobserved.
- LASTING_CANDY: run2 elite drop. Rest heals observed +24 at 53hp (53->77) —
  likely rest-boost relic like tea set; verify scaling on later rests.
- SPARKLING_ROUGE / CHANDELIER: run2 chest drops floor 9; effects pending combat
  observation.
- TUNING_FORK: run2 elite drop floor 13. Effect pending observation.
- BLESSING_OF_THE_FORGE: run2 elite potion drop. Effect pending first use.
- Run2 combat-start package confirmed again: STRENGTH+DEXTERITY powers + energy
  6/3 — attributions between SPARKLING_ROUGE/CHANDELIER/TUNING_FORK still open.
- THE_LANTERN_KEY event branches (run1/2 observed): RETURN_THE_KEY grants ~+100
  gold instantly no combat; KEEP_THE_KEY starts knight fight for key card.
  Choose RETURN at low hp, KEEP when healthy.
- AMETHYST_AUBERGINE: chest relic run2 f24. Effect pending combat observation.
