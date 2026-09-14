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
