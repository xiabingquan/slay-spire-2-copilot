# Characters

Five playable characters. Starter loadouts from game source extraction
(STS2-Agent characters index, authoritative for v0.107.x builds);
cross-checked with community databases (spire-codex, IGN, mobalytics).
All characters start with 99 Gold. Test-only ids: Deprived, RandomCharacter
(not playable in normal runs).

- IRONCLAD — 80 HP, masculine. Starter relic: BURNING_BLOOD (heal 6 HP at end of combat; Black Blood upgrade heals 12). Starter deck: Strike ×5, Defend ×4, Bash. Card pool: ~87 (38 Attack / 28 Skill / 21 Power). Archetype: Strength stacking, heavy single hits (Bludgeon), block-for-damage payoffs (Body Slam, Juggernaut), self-damage engines (Bloodletting, Offering, Hemokinesis). Key cards: Demon Form, Whirlwind, Uppercut, Blood Wall, Second Wind, Corruption (Ancient).
- SILENT — 70 HP, feminine. Starter relic: RING_OF_THE_SNAKE (draw 2 at combat start). Starter deck: Strike ×5, Defend ×5, Neutralize, Survivor. Card pool: ~88-89 (28 Attack / 42 Skill / 19 Power). Signature keyword: Sly — play for Energy cost, or discard to trigger the effect for free. Archetypes: Poison (Noxious Fumes, Deadly Poison, Accelerant, Envenom), Shivs (Blade Dance, Infinite Blades, Accuracy, Fan of Knives), discard synergy (Calculated Gamble, Tactician, Tough Bandages, Tingsha).
- DEFECT — 75 HP (game source; some community sites list 70), neutral. Starter relic: CRACKED_CORE (Channel 1 Lightning at combat start). Starter deck: Strike ×4, Defend ×4, Zap, Dualcast. Card pool: ~88. Unlocks after Necrobinder. Mechanic: Orbs — channel Lightning / Frost / Plasma / Dark into orb slots; passives trigger, evokes fire on leave; Focus scales orb output (Defragment, Data Disk; Biased Cognition strong but decays). Archetypes: orb stacking (Capacitor, Loop, Multi-Cast, Glacier), zero-cost Claw, power spam (Creative AI, Echo Form, Machine Learning).
- NECROBINDER — 66 HP, feminine. Starter relic: BOUND_PHYLACTERY (Summon 1 at start of your turn). Starter deck: Strike ×4, Defend ×4, Bodyguard, Unleash. Card pool: ~88. Unlocks after Regent. Mechanic: bone tokens, summons (Minion keyword; companion Osty commands many cards), Doom stacking death-clock (End of Days kills when Doom >= HP; Undying Sigil relic interacts), sacrifice loops (Minion Sacrifice, Death's Door, Necro Mastery).
- REGENT — 75 HP, masculine. Starter relic: DIVINE_RIGHT (gain 3 stars ★ at combat start). Starter deck: Strike ×4, Defend ×4, Falling Star, Venerate. Card pool: ~88 (33 Attack / 36 Skill / 19 Power per site header). Unlocks after Silent. Mechanic: stars (★) as combat resource for decree-style cards; Forge keyword (Fencing Manual: Forge 10; Spoils of Battle; Hammer Time shares Forge with allies); court attendant / Minion payoffs (Vitruvian Minion doubles Minion card damage and block); prestige scaling.

Unlock chain (game source): Silent is available from start; REGENT unlocks after Silent; NECROBINDER after Regent; DEFECT after Necrobinder. (Ironclad and Silent are the initial roster — verify exact fresh-save state in game.)

Shared run structure: 3 acts per run, branching map (monster / elite / boss / event / shop / rest / treasure); card rewards after combat; Neow boon at run start; rest sites offer Rest and Smith plus character-specific options. In state snapshots the character field uses ids IRONCLAD, SILENT, DEFECT, NECROBINDER, REGENT.
