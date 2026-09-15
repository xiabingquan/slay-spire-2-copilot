# Cards

Playable card knowledge from live runs. The can_play flag in state is always
authoritative; costs/values observed under normal and CONFUSED states.

## Verified

- STRIKE_IRONCLAD: 1-cost attack, ~6 dmg + strength; enchant/upgrade scales.
- DEFEND_IRONCLAD: 1-cost, ~5 block + dexterity.
- BASH: 2-cost, ~8-10 dmg + 2x VULNERABLE (upgraded ~10+). Core vuln applier.
- BLOOD_WALL: 2-cost self — ~16 block at 2hp cost; also chips nearby enemies
  (~8 dmg). Never play below ~5hp (hp cost kills).
- SHRUG_IT_OFF: 1-cost, 8 block + draw 1.
- DISMANTLE: 1-cost attack ~1 dmg + strips one enemy power/charge
  (SLIPPERY charges, RAMPART-style buffs — value is the strip).
- THUNDERCLAP: 1-cost AOE ~4+str all enemies + 1x VULNERABLE each; observed
  stripping enemy block fully.
- UPPERCUT (upgraded): 2-cost ~8-21 dmg + WEAK + VULNERABLE — best 2-debuff card.
- BLUDGEON: 3-cost, 32+str single target (35-49 observed, 49 under vuln +
  enchant). Boss/elite killer.
- WHIRLWIND (upgraded): X-cost AOE multi-hit; with str stacking observed
  27/33/49/80/81 total — scales with DEMON_FORM + energy relics.
- PERFECTED_STRIKE (upgraded): dmg + bonus per STRIKE in deck; 19-32 observed
  with 4-5 strikes deck.
- SWORD_BOOMERANG (upgraded): multi-hit random targets, str-scaling.
- DEMON_FORM (upgraded): 3-cost power, +strength each turn for multiple turns —
  engine card, play turn 1-2 whenever drawn.
- JUGGERNAUT: power — deals damage when gaining block; pairs with block cards.
- IRON_WAVE: dmg + block hybrid (~10 dmg + ~5-8 block).
- SECOND_WIND: exhaust hand cards -> block per exhausted card; converted status
  junk into 30+ block in a boss fight.
- ARMAMENTS: 5 block + upgrades a hand card for the combat.
- BATTLE_TRANCE: draw 3, no draws after this turn.
- FLAME_BARRIER: block + temporary thorns power.
- TWIN_STRIKE: 2-hit attack; str per hit.
- BLOODLETTING / OFFERING: hp-cost energy/draw — dangerous below 20hp.
- FIGHT_ME: 2-cost attack ~10 dmg; grants STRENGTH to both player and target
  ("duel invite" semantics).
- BREAKTHROUGH: 1-cost AOE ~9 dmg all enemies + 1hp self cost. Cheap wave-clear.
- BURNING_PACT: 1-cost self — exhaust/draw engine, no direct damage.
- RAMPAGE: 1-cost attack ~6 base dmg; per-play scaling unverified numerically.

## Reported

- EXPECT_A_FIGHT / PYRE / STOMP: picked or seen as rewards; effect pending
  first real observation.
- SPOILS_MAP: map-theft event product; behavior pending.
- LANTERN_KEY: key-fight card product (-1 cost self); behavior pending.
- FRANTIC_ESCAPE: sandpit-holes event card (~3 cost self); observed effect was
  subtle — re-verify against sandpit mechanics.

## Screen notes (card reward / selection)

- Reward screens may show unclaimable buttons (potion slots full) — clicking
  no-ops; proceed leaves the screen.
- Skip button exists on most card_reward screens but not all
  (NDeckCardSelectScreen removal flow has none — removal is mandatory pick).
- AROMA_OF_CHAOS event "LET_GO": opens NDeckTransformSelectScreen — pick any
  deck card, it transforms to a random one (STRIKE -> POMMEL_STRIKE observed).
  Good sink for redundant basics.
