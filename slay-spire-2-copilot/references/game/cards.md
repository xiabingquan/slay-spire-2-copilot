# Cards

Static card reference from live play. The can_play flag in state is always
authoritative.

- STRIKE_IRONCLAD: 1-cost attack, ~6 dmg + strength; enchant/upgrade scales.
- DEFEND_IRONCLAD: 1-cost, ~5 block + dexterity.
- BASH: 2-cost, ~8-10 dmg + 2x VULNERABLE (upgraded ~10+); core vuln applier.
- BLOOD_WALL: 2-cost self, ~16 block at 2hp cost, also chips nearby enemies
  (~8 dmg). Never play below ~5hp.
- SHRUG_IT_OFF: 1-cost, 8 block + draw 1.
- DISMANTLE: 1-cost attack ~1 dmg + strips one enemy power/charge.
- THUNDERCLAP: 1-cost AOE ~4+str all enemies + 1x VULNERABLE each; strips
  enemy block fully (observed).
- UPPERCUT (upgraded): 2-cost ~8-21 dmg + WEAK + VULNERABLE.
- BLUDGEON: 3-cost, 32+str single target (35-49 observed). Boss/elite killer.
- WHIRLWIND (upgraded): X-cost AOE multi-hit, str-scaling (27-81 total
  observed with DEMON_FORM + energy relics).
- PERFECTED_STRIKE (upgraded): dmg + bonus per STRIKE in deck.
- SWORD_BOOMERANG (upgraded): multi-hit random targets, str-scaling.
- DEMON_FORM (upgraded): 3-cost power, +strength per turn for several turns —
  engine card, play turn 1-2.
- JUGGERNAUT: power — deals damage when gaining block.
- IRON_WAVE: ~10 dmg + ~5-8 block hybrid.
- SECOND_WIND: exhaust hand cards -> block per exhausted card.
- ARMAMENTS: 5 block + upgrades a hand card for the combat.
- BATTLE_TRANCE: draw 3, no draws after this turn.
- FLAME_BARRIER: block + temporary thorns power.
- TWIN_STRIKE: 2-hit attack; strength applies per hit.
- BLOODLETTING / OFFERING: hp-cost energy/draw — dangerous below 20hp.
- FIGHT_ME: 2-cost attack ~10 dmg; grants STRENGTH to both player and target.
- BREAKTHROUGH: 1-cost AOE ~9 dmg all enemies + 1hp self cost.
- BURNING_PACT: 1-cost self, exhaust/draw engine, no direct damage.
- RAMPAGE: 1-cost attack ~6 base dmg, per-play scaling grows.
- EXPECT_A_FIGHT / PYRE / STOMP / SPOILS_MAP / LANTERN_KEY / FRANTIC_ESCAPE:
  effects pending observation.
- AROMA_OF_CHAOS event "LET_GO": opens deck transform — pick any deck card, it
  transforms at random (STRIKE -> POMMEL_STRIKE).

## Screen notes

- Reward screens may show unclaimable buttons when potion slots are full —
  click no-ops; proceed leaves the screen.
- Skip button exists on most card_reward screens; NDeckCardSelectScreen
  removal flow has none (mandatory pick).
