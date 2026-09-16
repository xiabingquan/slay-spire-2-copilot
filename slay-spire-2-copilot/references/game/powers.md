# Powers

Combat buffs/debuffs reference; ids as they appear in state. Numerics from
community databases (sts2-wiki, fandom, metabot) cross-checked with observed
play on v0.107.1.

## Core combat statuses

- VULNERABLE_POWER: target takes +50% attack damage (Paper Phrog relic raises
  to +75% for Ironclad); amplifies incoming attack damage when on you too.
- WEAK_POWER: target deals -25% attack damage (Paper Krane: enemies with Weak
  deal -40% to Silent).
- FRAIL_POWER: target gains -25% Block from cards.
- STRENGTH_POWER: flat damage added to every attack hit; scales multi-hits.
- DEXTERITY_POWER: flat Block added to every block-gaining card.
- RITUAL_POWER (enemy): gains Strength every turn — kill priority.
- POISON: creature loses HP at start of its turn, then Poison -1 per tick.
- THORNS_POWER: deals damage back to attackers when hit (Bronze Scales: 3).
- PLATING_POWER (Plated Armor, e.g. GORGET): gains Block at end of turn;
  loses 1 stack each time it takes unblocked attack damage.
- REGEN (Regeneration): heals HP at end of each turn, then -1 per turn.
- CONFUSED_POWER (FAKE_SNECKO_EYE / Snecko Eye): card costs randomized when
  drawn (0-3 range typical).
- SLOW_POWER (enemy, e.g. BygoneEffigy elite): enemy takes more attack damage as
  you play cards this turn (~+10% per card played, wiki figure); alternating
  with heavy charged hits observed live.
- MINION_POWER: marks summoned helpers (Necrobinder/Regent kits, boss adds).
- DOOM_POWER (Necrobinder): stacking death-clock; kills when Doom >= HP
  (Undying Sigil relic: enemies with Doom >= HP deal -50% damage; Doom then
  triggers at their turn start instead of end).
- FOCUS (Defect): scales orb passives/evoke effects; can go negative
  (Hyperbeam applies Focus down to owner).
- VIGOR_POWER: bonus attack damage consumed by the next attack (Akabeko: 8
  at combat start).
- INTANGIBLE_POWER: attack damage taken reduced to 1 (classic effect).
- SURROUNDED_POWER + BACK_ATTACK_LEFT/RIGHT: positioning markers — BackAttack
  markers let Surrounded checks resolve flanking rules.

## Card-bound affliction powers (see afflictions.md)

- CHAINS_OF_BINDING_POWER: block suppression (queen-boss debuff; with Frail
  observed zeroing Block).
- RINGING_POWER: hand cards flip can_play=false (card-play lockout).
- TANGLED_POWER / GALVANIC_POWER / HEX_POWER / SMOGGY_POWER / TAINTED_POWER:
  logic hosts for afflictions Entangled / Galvanized / Hexed / Smog / Tainted.

## Character-kit powers

- DEMON_FORM_POWER (Ironclad): +Strength per turn for several turns; engine.
- HELLRAISER_POWER / HEGEMONY (Ironclad): card-hosted; per-card effects in
  cards.md.
- ClarityPower vs DrawCardsNextTurnPower: extra draws next turn(s); Clarity
  spans next N turns, DrawCardsNextTurn the next turn only.
- TemporaryStrength/FlexPotionPower: temporary Strength that expires end of
  turn (Flex potion model).
- DIE_FOR_YOU_POWER, OBLIVION_POWER, MAYHEM_POWER, STAMPEDE_POWER,
  PIERCING_WAIL_POWER, THIEVERY_POWER, SURPRISE_POWER, THE_BOMB_POWER,
  THE_HUNT_POWER, PARRY_POWER, SEEKING_EDGE_POWER, ILLUSION_POWER,
  REATTACH_POWER, ESCAPE_ARTIST_POWER, ACCELERANT_POWER, FAN_OF_KNIVES_POWER:
  card- or monster-hosted powers — effect follows the hosting card/monster
  (see cards.md; e.g. TheHunt is a visual success marker, Accelerant
  re-triggers Poison, FanOfKnives/Parry/SeekingEdge are inert markers checked
  by Shiv / Sovereign Blade cards).

## Live-play observations (v0.107.1)

- SLIPPERY_POWER (e.g. Inklet): first incoming hit greatly reduced (Strike 6
  -> 1); charges consumed per hit.
- SHRINK_POWER (ShrinkerBeetle): reduces player attack damage until the enemy dies.
- INFESTED_POWER (PhrogParasite elite): on death spawns 4x ~17-21hp adds — save
  AOE for the spawn wave.
- STOCK_POWER (robot factory): each death spawns next robot variant.
- RAMPART_POWER: living-shield ally block regeneration.
- BURROWED / TERRITORIAL / SOAR: elite/boss defensive stances; burrowed pairs
  with big charged intents that cancel if block broken in time.
- DUPPLICATION_POWER (DUPLICATOR potion): temporary card-duplication state.
