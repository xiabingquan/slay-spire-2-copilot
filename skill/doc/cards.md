# Cards knowledge (observed play)

Extracted from live runs 2026-09-14/15 (Ironclad). Costs/values observed under
normal and CONFUSED states; can_play flag in state is always authoritative.

## Starter / basic

- STRIKE_IRONCLAD: 1-cost attack, ~6 dmg + strength. Enchant/upgrade scales.
- DEFEND_IRONCLAD: 1-cost, ~5 block + dexterity.
- BASH: 2-cost, ~8-10 dmg + 2x VULNERABLE (upgraded ~10+). Core vuln applier.

## Ironclad core (observed)

- BLOOD_WALL: 2-cost self — ~16 block at 2hp cost; also chips nearby enemies
  (~8 dmg observed once). Never play below ~5hp (hp cost kills).
- SHRUG_IT_OFF: 1-cost, 8 block + draw 1.
- DISMANTLE: 1-cost attack ~1 dmg + strips one enemy power/charge
  (SLIPPERY charges, RAMPART-style buffs — value is the strip).
- THUNDERCLAP: 1-cost AOE, ~4+str all enemies + 1x VULNERABLE each; also
  stripped enemy block fully in observed fights.
- UPPERCUT (upgraded): 2-cost, ~8-21 dmg + WEAK + VULNERABLE — best 2-debuff card.
- BLUDGEON: 3-cost, 32+str single target; ~35-49 observed; enchanted variant
  reached 49 under vuln. Boss/elite killer.
- WHIRLWIND (upgraded): X-cost AOE multi-hit; with str stacking observed
  27/33/49/80/81 total — scales brutally with DEMON_FORM + energy relics.
- PERFECTED_STRIKE (upgraded): dmg + bonus per STRIKE in deck; 19-32 observed
  with 4-5 strikes deck.
- SWORD_BOOMERANG (upgraded): multi-hit random targets, str-scaling; cleaned
  multi-enemy packs and stripped block.
- DEMON_FORM (upgraded): 3-cost power, +strength each turn for multiple turns;
  engine card — play turn 1-2 whenever drawn.
- JUGGERNAUT: power — deals damage when gaining block; pairs with block cards.
- IRON_WAVE: dmg + block hybrid (~10 dmg + ~5-8 block).
- SECOND_WIND: exhaust cards from hand -> block per exhausted card; converted
  status junk into 30+ block in boss fight.
- ARMAMENTS: 5 block + upgrades a hand card for the combat.
- BATTLE_TRANCE: draw 3, no draws after this turn.
- FLAME_BARRIER: block + FLAME_BARRIER_POWER (temporary thorns); absorbed and
  reflected in elite fights.
- TWIN_STRIKE: 2-hit attack; str per hit.
- BLOODLETTING / OFFERING: hp-cost energy/draw cards — dangerous below 20hp.

## Event / status cards

- BYRDONIS_EGG: unplayable (-1 cost) status from nest events; HATCH rest option
  appears while in deck. Remove via shop.
- DECAY / WOUND / SLIMED: enemy/event statuses; some playable for chip; prime
  SECOND_WIND fuel or shop-removal targets.
- SPOILS_MAP: map-theft event product; behavior pending observation.
- LANTERN_KEY: key-fight card product (-1 cost self); behavior pending.
- FRANTIC_ESCAPE: sandpit-holes event card (~3 cost self); observed play had
  subtle effect — re-verify against sandpit mechanics.

## Selection-screen notes

- Reward screens sometimes show unclaimable buttons (potion slots full) —
  clicking no-ops; proceed leaves the screen.
- Skip button exists on most card_reward screens but not all
  (NDeckCardSelectScreen removal flow has none — removal is mandatory pick).
