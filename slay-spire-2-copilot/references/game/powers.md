# Powers

Deterministic combat buffs/debuffs. IDs match state `powers[].id`. Every entry
verified against decompiled `MegaCrit.Sts2.Core.Models.Powers.*` classes
(`PowerType`, stack behavior, hook logic, `CanonicalVars` numbers). `Amount`
below = the stack count shown on the power. "Owner's side turn" = the turn of
the side the power holder belongs to (Player side for you, Enemy side for
monsters).

Format: `- POWER_ID (Buff/Debuff): effect.`

## Core combat statuses

- VULNERABLE_POWER (Debuff, Counter): attack damage received by owner is
  multiplied by x1.5 (`DamageIncrease` 1.5). Paper Phrog / CrueltyPower /
  DebilitatePower can modify that multiplier. Ticks down 1 at end of Enemy
  side turn.
- WEAK_POWER (Debuff, Counter): attack damage dealt by owner is multiplied by
  x0.75 (`DamageDecrease` 0.75). Paper Krane / DebilitatePower can modify the
  multiplier. Ticks down 1 at end of Enemy side turn.
- FRAIL_POWER (Debuff, Counter): Block owner gains from cards/monster moves is
  multiplied by x0.75. Ticks down 1 at end of Enemy side turn.
- STRENGTH_POWER (Buff, Counter, negative allowed): +Amount attack damage on
  every attack the owner deals (added per hit; multi-hit scales per hit).
- DEXTERITY_POWER (Buff, Counter, negative allowed): +Amount Block on every
  block-gaining card/monster move of the owner.
- POISON (Debuff, Counter): at start of owner's side turn, deals Amount
  unblockable unpowered damage to owner, then decrements 1; repeats per
  trigger. Trigger count = min(stacks, 1 + sum of opposing AccelerantPower
  amounts).
- THORNS_POWER (Buff, Counter): when owner is hit by a powered attack (or
  Omnislice), dealer takes Amount unpowered damage.
- PLATING_POWER (Buff, Counter): at start of owner's side turn (not turn 1 for
  the holder) owner loses 1 stack (enemies lose `Decrement`, = player count in
  multiplayer); at end of owner's side turn (early) owner gains Amount Block.
  Enemies with Plating also gain Amount Block at combat start (round 1).
  Players can hold Plating too (Heart of Iron potion applies 7) — same
  mechanics; combat-start block only when applied before round 1's player turn.
  Stack loss for players is 1/turn.
- REGEN_POWER (Buff, Counter): at end of owner's side turn, heal Amount HP,
  then decrement 1.
- INTANGIBLE_POWER (Buff, Counter): damage and HP loss received by owner capped
  at 1 per instance. Ticks down at end of owner's side turn.
- BUFFER_POWER (Buff, Counter): next Amount HP-loss events that would deal HP
  loss to owner deal 0 instead (consumed 1 per prevented loss; late hook, so
  other reducers apply first).
- RITUAL_POWER (Buff, Counter): at end of owner's side turn, apply +Amount
  STRENGTH_POWER to owner (skips the very turn it was applied if applied by an
  enemy during that enemy's turn).
- FOCUS_POWER (Buff, Counter, negative allowed): orb passive/evoke values of
  owner get Math.Max(value + Amount, 0) — scales orb effects, floors at 0.
- VIGOR_POWER (Buff, Counter): +Amount attack damage on the owner's next
  attack (ModifyDamageAdditive; consumed by that attack).
- DOOM_POWER (Debuff, Counter): at end of owner's side turn, if owner
  CurrentHp <= Amount, owner is killed (Doom kill, special VFX; all doomed
  creatures on that side die together).
- CONFUSED_POWER (Debuff, Single): every card drawn by owner (canonical cost
  >= 0) gets its combat cost rerolled to a random int in 0..3
  (`Rng.CombatEnergyCosts.NextInt(4)`).
- SLOW_POWER (Debuff, Counter): attack damage received by owner is multiplied
  by x(1 + 0.1 * cards the player has played this turn). `SlowAmount` +1 per
  card played; resets to 0 at start of owner's side turn. Display amount =
  SlowAmount * 10.
- MINION_POWER (Buff, Single): marks a summoned helper — its death does not
  trigger combat-end fatal logic (OwnerIsSecondaryEnemy; power not persisted
  after owner death).
- ARTIFACT_POWER (Buff, Counter): each incoming visible Debuff-type power
  application to owner is set to 0 amount, then 1 Artifact stack is consumed.
  Invisible/internal debuffs are not blocked.
- SURROUNDED_POWER (Debuff, Single): positioning state; attack damage to owner
  is multiplied by x1.5 when the attacker carries the matching
  BACK_ATTACK_LEFT_POWER / BACK_ATTACK_RIGHT_POWER marker for the owner's
  facing. Markers themselves are inert Single Buffs. Facing rule (decomp): the
  owner's facing flips whenever the player plays a card or potion targeting a
  creature whose BACK_ATTACK marker matches the opposite direction — targeting
  a claw turns the owner toward it, exposing the other claw as the ×1.5
  flanker. On flank-creature death, facing re-targets to the remaining
  marker-bearer if all survivors share one marker side.

## Card-bound affliction hosts (see afflictions.md)

- CHAINS_OF_BINDING_POWER (Debuff, Counter): on drawing cards during owner's
  side turn, afflict up to Amount cards with Bound (per-turn afflicted count
  capped at Amount). While this power is active only 1 Bound card may be
  played per turn; all Bound afflictions clear at end of owner's side turn.
- RINGING_POWER (Debuff, Single): on apply, afflict all owner's cards with
  Ringing; new cards entering combat also get it. A Ringing card is unplayable
  once any card has been played by owner this turn. Power removes itself at
  end of owner's side turn (clearing all Ringing).
- TANGLED_POWER (Debuff, Counter): on apply, afflict all owner's Attack cards
  with Entangled; new Attacks entering combat also get it. Entangled cards
  cost +Amount Energy. Power removes itself at end of owner's side turn.
- GALVANIC_POWER (Buff, Counter, on the enemy): at combat start and when Power
  cards enter combat, afflict player Power cards with Galvanized (Amount).
  Playing a Galvanized card deals Amount unpowered damage to its owner.
- HEX_POWER (Debuff, Single): afflict all owner's cards (and new ones) with
  Hexed; Hexed cards gain the Ethereal keyword while this power exists.
  Removed when the applier dies; clears Hexed on removal.
- SMOGGY_POWER (Debuff, Single): after owner plays a Skill, afflict all
  unafflicted Skill cards with Smog; new Skills entering combat after a Skill
  was played this turn also get it. Smog cards are unplayable while this power
  exists. Smog afflictions clear at end of owner's side turn.
- TAINTED_POWER (Debuff, Counter): attacks that hit owner deal +Amount damage
  (ModifyDamageAdditive on incoming powered attacks). Removed at end of Enemy
  side turn.
- VITAL_SPARK_POWER (Buff, Counter, on the enemy): player Skill cards are
  afflicted with Tainted (Amount) at combat start and on entering combat;
  playing a Tainted card applies TAINTED_POWER Amount to the card's owner.

## Player economy / draw powers

- MIND_ROT_POWER (Debuff, Counter): owner's hand draw each turn reduced by
  Amount (floored at 0): ModifyHandDraw = max(0, count - Amount).
- WASTE_AWAY_POWER (Debuff, Counter): owner's max Energy reduced by Amount.
- NO_DRAW_POWER (Debuff, Single): non-hand draws (card-effect draws) by owner
  are blocked for the rest of the turn. Removed at end of owner's side turn.
  Initial hand draw is not blocked.
- NO_ENERGY_GAIN_POWER (Debuff, Single): energy gains for owner this turn are
  set to 0. Removed at end of owner's side turn.
- CLARITY_POWER (Buff, Counter): +1 hand draw at the start of each of owner's
  next Amount turns; decrements at each of those turn starts.
- DRAW_CARDS_NEXT_TURN_POWER (Buff, Counter): +Amount hand draw at the start
  of owner's next turn only, then removed.
- MACHINE_LEARNING_POWER (Buff, Counter): +Amount hand draw every turn
  (permanent while power lasts).
- DEMESNE_POWER (Buff, Counter): +Amount hand draw per turn AND +Amount max
  Energy.
- PYRE_POWER (Buff, Counter): +Amount max Energy.
- FRIENDSHIP_POWER (Buff, Counter): +Amount max Energy.
- TOOLS_OF_THE_TRADE_POWER (Buff, Counter): +Amount hand draw per turn; at
  owner's turn start, select Amount cards from hand to discard.
- TYRANNY_POWER (Buff, Counter): +Amount hand draw per turn; at owner's turn
  start, select Amount cards from hand to Exhaust.
- ENERGY_NEXT_TURN_POWER (Buff, Counter): at next energy reset, gain Amount
  Energy, then removed.
- GENESIS_POWER (Buff, Counter): at each energy reset, gain Amount Stars.
- STAR_NEXT_TURN_POWER (Buff, Counter): at next energy reset, gain Amount
  Stars, then removed.
- RADIANCE_POWER (Buff, Counter): at energy reset, gain Energy equal to
  DynamicVars.Energy (set by applier), then decrement.
- LIGHTNING_ROD_POWER (Buff, Counter): at energy reset, Channel 1 Lightning
  orb, then decrement 1.
- SPINNER_POWER (Buff, Counter): at energy reset, Channel Amount Glass orbs.
- AUTOMATION_POWER (Buff, Counter): every 10th card drawn by owner grants
  Amount Energy (counter `BaseCards` 10, then resets to 10).
- ORBIT_POWER (Buff, Counter): every 4 Energy owner spends on cards triggers
  GainEnergy(Amount) per trigger (threshold 4).
- AGGRESSION_POWER (Buff, Counter): at start of owner's side turn, take Amount
  Attack cards from discard, move them to hand and Upgrade each (if
  upgradable).
- CURIOUS_POWER (Buff, Counter): owner's Power cards with cost > 0 cost
  Amount less (min 0).
- FREE_ATTACK_POWER (Buff, Counter): owner's Attack cards in hand/play cost 0;
  1 stack consumed per Attack played.
- FREE_SKILL_POWER (Buff, Counter): owner's Skill cards in hand/play cost 0;
  1 stack consumed per Skill played.
- FREE_POWER_POWER (Buff, Counter): owner's Power cards in hand/play cost 0;
  1 stack consumed per Power played.
- CORRUPTION_POWER (Buff, Single): owner's Skill cards cost 0 and Exhaust when
  played.
- VEILPIERCER_POWER (Buff, Counter): owner's Ethereal cards in hand/play cost
  0; 1 stack consumed per Ethereal card played.
- VOID_FORM_POWER (Buff, Counter): owner's cards (and Star costs) in
  hand/play cost 0 up to Amount non-autoplay cards played per turn; counter
  resets at turn start.
- BORROWED_TIME_POWER (Debuff, Counter): all owner's cards cost +Amount
  Energy. Removed at end of owner's side turn.
- CONFUSED_POWER: see core statuses (cost randomization).

## Block-related powers

- RAGE_POWER (Buff, Counter): whenever owner plays an Attack card, owner
  gains Amount Block. Power removed at end of owner's side turn.
- FEEL_NO_PAIN_POWER (Buff, Counter): whenever an owner's card is Exhausted,
  owner gains Amount Block.
- JUGGERNAUT_POWER (Buff, Counter): whenever owner gains >0 Block, deal Amount
  unpowered damage to a random hittable enemy.
- BARRICADE_POWER (Buff, Single): owner's Block is not cleared at turn
  (ShouldClearBlock always false for owner).
- BLUR_POWER (Buff, Counter): owner's Block is not cleared at turn start;
  decrements 1 at start of owner's side turn.
- BLOCK_NEXT_TURN_POWER (Buff, Counter): when owner's Block is cleared, gain
  Amount Block once and remove the power.
- SELF_FORMING_CLAY_POWER (Buff, Counter): when owner's Block is cleared, gain
  Amount Block once and remove the power.
- TORIC_TOUGHNESS_POWER (Buff, Counter): when owner's Block is cleared, gain
  DynamicVars.Block Block, then decrement 1.
- BEACON_OF_HOPE_POWER (Buff, Single): the first time owner gains Block on
  owner's side turn, all allies gain floor-half of that Block amount
  (amount * 0.5, only if >= 1); triggers once per instance.
- COOLANT_POWER (Buff, Counter): at start of owner's side turn, gain
  (number of distinct orb types in queue) * Amount Block.
- RAMPART_POWER (Buff, Counter): at start of Player side turn, each living
  TurretOperator enemy gains Amount Block.
- AFTERIMAGE_POWER (Buff, Counter): after owner plays a card, owner gains
  Amount Block.
- SHROUD_POWER (Buff, Counter): gains owner Amount Block (triggered by power
  amount changes — hosted by source card/relic).
- SNEAKY_POWER (Buff, Counter): owner gains Amount Block (fast VFX; trigger
  hosted by source card).
- SPIRIT_OF_ASH_POWER (Buff, Counter): before owner plays a card, owner gains
  Amount Block (source-hosted trigger).
- DANSE_MACABRE_POWER (Buff, Counter): before owner plays a card, owner gains
  Amount Block (source-hosted trigger).
- CHILD_OF_THE_STARS_POWER (Buff, Counter): when owner's player spends Stars,
  owner gains Amount * stars-spent Block.
- SHADOWMELD_POWER (Buff, Counter): owner's Block gains multiplied by
  2^Amount; power removed at end of owner's side turn.
- UNMOVABLE_POWER (Buff, Counter): owner's Block gains multiplied by x2.
- FASTEN_POWER (Buff, Counter): +Amount Block on owner's block gains
  (ModifyBlockAdditive, card/move-sourced block only).
- PILLAR_OF_CREATION_POWER (Buff, Counter): gains owner Amount Block
  (trigger hosted by source card/relic).

## Attack-damage modifying powers

- COLOSSUS_POWER (Buff, Counter): attacks against owner from a dealer that has
  VULNERABLE_POWER deal x0.5 (`DamageDecrease` 0.5). Decrements 1 at end of
  Enemy side turn.
- SHRINK_POWER (Debuff, Counter; Single if Amount < 0 = infinite): owner's
  attack damage dealt multiplied by x0.75 (`DamageDecrease` 30 →
  (100-30)/100). Decrements 1 at end of owner's side turn; removed if applier
  dies. Visual: owner scales to 0.5.
- SLOW_POWER: see core statuses (incoming attack damage ramps per card
  played).
- DOUBLE_DAMAGE_POWER (Buff, Counter): owner's attack damage dealt multiplied
  by x2 while stacks > 0; decrements at end of owner's side turn.
- LETHALITY_POWER (Buff, Counter): owner's card-sourced attack damage dealt
  multiplied by x(1 + Amount/100) — i.e. +Amount% while the card is being
  played from Play pile (hosted modifier; see card text for trigger).
- ACCURACY_POWER (Buff, Counter): +Amount attack damage on owner's Shiv-tagged
  attacks (ModifyDamageAdditive; only cards with CardTag.Shiv).
- CALCIFY_POWER (Buff, Counter): +Amount attack damage on owner's attacks
  (ModifyDamageAdditive; trigger hosted by source).
- LEADERSHIP_POWER (Buff, Counter): +Amount attack damage on owner's attacks
  (ModifyDamageAdditive; trigger hosted by source).
- PHANTOM_BLADES_POWER (Buff, Counter): +Amount attack damage on owner's
  attacks; also grants Retain to owner's cards on apply/enter-combat.
- TRACKING_POWER (Buff, Counter): owner's (or owner's pets') attack damage
  against a target with WEAK_POWER multiplied by Amount (x-value from stacks).
- GIGANTIFICATION_POWER (Buff, Counter): one owner's Attack per activation
  deals x3 damage; 1 stack consumed after that attack resolves.
- CONQUEROR_POWER (Debuff, Counter): SovereignBlade attacks against owner deal
  x2 damage. Decrements at end of owner's side turn.
- KNOCKDOWN_POWER (Debuff, Counter): attacks against owner from anyone except
  the applier deal xAmount damage. Removed at end of owner's side turn.
- FLANKING_POWER (Debuff, Counter): attacks against owner from anyone except
  the applier deal xAmount damage. Removed at end of owner's side turn.
- HANG_POWER (Debuff, Counter): the Hang card's attack against owner deals
  xAmount damage.
- SOAR_POWER (Buff, Single): owner's attack damage taken multiplied by x0.5
  (`DamageDecrease` 50/100) — i.e. owner takes half attack damage while
  active.
- DIAMOND_DIADEM_POWER (Buff, Single): attacks against owner deal x0.5; removed
  at end of Enemy side turn.
- INTERCEPT_POWER (Buff, Single): owner takes (covered-creatures-count + 1) x
  attack damage multiplier — used with CoveredPower flanking logic; removed at
  end of Enemy side turn.
- COVERED_POWER (Buff, Single, on the covered creature): attacks against owner
  deal x0 while the covering applier lives; removed at end of Enemy side turn
  or when applier dies.
- GUARDED_POWER (Buff, Single): attacks against owner deal x0.5; removed when
  applier dies.
- TANK_POWER (Buff, Single): owner's outgoing attack damage x2 (applies
  GuardedPower on apply per decomp interaction with guarded targets).
- SURROUNDED_POWER: see core statuses (x1.5 from flanking attackers).
- TENDER_POWER (Debuff, Counter): each card the owner plays this turn applies
  -1 Strength and -1 Dexterity to owner (silently); at end of owner's side
  turn those debuffs are refunded (+N Strength/Dex where N = cards played this
  turn).
- TAINTED_POWER: see affliction hosts (+Amount incoming attack damage).

## Poison / Doom / death-clock powers

- ENVENOM_POWER (Buff, Counter): when owner's powered attack deals unblocked
  damage > 0, apply Amount POISON to the target.
- NOXIOUS_FUMES_POWER (Buff, Counter): at start of owner's side turn, apply
  Amount POISON to all hittable enemies.
- ACCELERANT_POWER (Buff, Counter): inert by itself — opposing POISON on the
  other side triggers extra times: poison trigger count includes
  1 + sum(AccelerantPower on opposing side), capped at poison stacks.
- CORROSIVE_WAVE_POWER (Buff, Counter): on card draw hooks, applies Amount
  POISON to all hittable enemies (source-hosted trigger; see monster move).
- OUTBREAK_POWER (Buff, Counter): every 3rd time owner applies POISON to
  anyone (Amount-change > 0), deal Amount unpowered damage to all hittable
  enemies; internal counter resets modulo 3.
- REAPER_FORM_POWER (Buff, Counter): when owner (or owner's pet) deals attack
  damage > 0, apply DOOM = total damage * Amount to the target.
- OBLIVION_POWER (Debuff, Counter): each card the applier's player plays this
  turn applies Amount DOOM to owner. Removed at end of Player side turn.
- NEUROSURGE_POWER (Debuff, Counter): at start of owner's side turn, apply
  Amount DOOM to owner.
- COUNTDOWN_POWER (Buff, Counter): at start of owner's side turn, applies
  DOOM-related countdown (Apply<DoomPower> to owner — kill clock; see monster
  card text for displayed number).
- DEMISE_POWER (Debuff, Counter): at end of owner's side turn, deal Amount
  unblockable unpowered damage to owner.
- DISINTEGRATION_POWER (Debuff, Counter): at end of owner's side turn (late),
  deal Amount unpowered damage to owner.
- MAGIC_BOMB_POWER (Debuff, Counter): at end of owner's side turn, if applier
  still alive, deal Amount unpowered damage to owner, then remove the power.
  Removed also if applier dies.
- STRANGLE_POWER (Debuff, Counter): each card the applier's player plays this
  turn deals Amount unblockable unpowered damage to owner. Removed at end of
  owner's side turn.
- CONSTRICT_POWER (Debuff, Counter): at end of owner's side turn, deal Amount
  unpowered damage to owner. Removed when the applier dies.
- PAPER_CUTS_POWER (Buff, Counter): when owner's powered attack deals
  unblocked damage > 0 to a player, that player loses Amount max HP.
- DISINTEGRATION (card-applied): see afflictions.md — KnowledgeDemon choice
  card applies DISINTEGRATION_POWER 6.
- THE_GAMBIT_POWER (Debuff, Single): if owner takes unblocked powered-attack
  damage > 0, owner is killed (power removed as it fires).

## Revival / summon / monster stances

- HARD_TO_KILL_POWER (Buff, Counter): owner's damage received per instance is
  capped at Amount HP-loss (`ModifyDamageCap` = Amount). Exoskeleton applies
  it with Amount = 9 — HP loss per hit capped at 9; excess is discarded, not
  banked.
- SLIPPERY_POWER (Buff, Counter): any HP loss to owner that would be >= 1 is
  reduced to exactly 1; 1 stack consumed per hit that deals >= 1 unblocked
  damage.
- HARDENED_SHELL_POWER (Buff, Counter): HP loss to owner per turn is capped at
  Amount minus damage already received this turn (tracker resets at turn
  start).
- REATTACH_POWER (Buff, Single, Decimillipede segments): on death, if any
  other segment with Reattach is still alive, the segment enters a dead state
  (not removed from combat, untargetable) and at end of its turn reattaches —
  healing Amount HP. Death is fatal only when ALL other segments are dead.
  Buffs persist through death.
- ILLUSION_POWER (Buff, Single): on death, keeps its buffs (debuffs removed
  unless non-temporary), queues REVIVE_MOVE with HealIntent which heals owner
  to full (MaxHp - CurrentHp). Applies MINION_POWER on apply if missing.
  Reviving owner is untargetable until revive resolves.
- ADAPTABLE_POWER (Buff, Single): Test-Subject-style self-revive — death
  prevents combat end and creature removal until revive logic completes
  (monster-hosted state machine; buffs retained).
- DIE_FOR_YOU_POWER (Buff, Single): Osty-family death handler — combat does
  not end on owner death; owner removed from combat; revive handled by pet
  logic (see character cards).
- INFESTED_POWER (Buff, Single): on owner's death, spawns 4 Wriggler monsters
  (StartStunned = true) on the owner's side; combat end is blocked until the
  spawn resolves.
- STOCK_POWER (Buff, Counter): on owner's death (Amount > 0), spawns an Axebot
  in the same slot with StockAmount = Amount - 1 (next robot variant chain);
  combat does not end during spawn.
- STEAM_ERUPTION_POWER (Buff, Single): owner death handler — combat does not
  end on owner death; buffs retained for follow-up encounter logic.
- SURPRISE_POWER (Buff, Single): owner death handler — combat does not end
  until the surprise-spawn logic resolves (CreatureCmd.Add of next monster).
- CRAB_RAGE_POWER (Buff, Single): on death of another creature on owner's side, the surviving owner gains +6 Strength and 99 unpowered Block, then this power removes itself. (KaiserCrab claws; CanonicalVars Strength 6 / Block 99 Unpowered.)
- DAMPEN_POWER (Debuff, None-stack): on apply, every upgraded card in the owner's deck is downgraded; the prior upgrade levels are stored in internal data keyed per applier (casters set grows when re-applied). Observed on Act3 MagiKnight — the downgrade persists while the power exists.
- SOAR_POWER (Buff, Single): while active, damage the owner receives from powered attacks is multiplied by ×0.5 (CanonicalVars DamageDecrease 50 / 100). OwlMagistrate applies it via JUDICIAL_FLIGHT and removes it on VERDICT — its big hit turn is the window where it takes full damage.
- RAVENOUS_POWER (Buff, Counter): when another creature on owner's side dies
  and owner lives, owner is stunned into devour move and gains +Amount
  STRENGTH.
- SUMMON_NEXT_TURN_POWER (Buff, Counter): at start of owner player's turn,
  summon Amount Osty pets, then remove the power.
- SIC_EM_POWER (Debuff, Counter): when the applier's Osty pet damages owner,
  summon Amount Osty for the pet's player. Removed at end of owner's side
  turn.
- DEVOUR_LIFE_POWER (Buff, Counter): on card-play hooks, OstyCmd.Summon
  (Amount) — pet summon trigger hosted by source card.
- BURROWED_POWER (Buff, Single): owner cannot be targeted/hit
  (ShouldAllowHitting false for owner); if owner's Block breaks, owner is
  stunned into dizzy move and Burrowed is removed; on removal owner loses all
  Block (999999999).
- ASLEEP_POWER (Buff, Counter): owner sleeps — if owner takes unblocked damage
  != 0, owner wakes (removes own Plating if any, stuns self into WakeUpMove,
  removes Asleep). At end of owner's side turn, Asleep decrements 1; when it
  hits 0, owner wakes via WakeUpMove. When Asleep <= 1 at turn end, Plating is
  removed.
- SLUMBER_POWER (Buff, Counter): decrements on unblocked damage received AND
  at end of owner's side turn; at 0, owner wakes via WakeUpMove (Slumbering
  Beetle).
- PAINFUL_STABS_POWER (Buff, Counter): owner's attacks that deal unblocked
  damage to players apply Wound status cards to those players (per-hit logic
  in AfterAttack; power and creature persist after owner death until removal
  rules fire).
- ESCAPE_ARTIST_POWER (Buff, Counter): visual escape timer — decrements at end
  of owner's side turn while Amount > 1; at Amount == 1 starts pulsing
  (ThievingHopper escape imminent; escape action hosted by monster move).
- BATTLEWORN_DUMMY_TIME_LIMIT_POWER (Buff, Counter): decrements at end of
  owner's side turn; at 1, dummy escapes (event encounter logic).
- SANDPIT_POWER (Buff, Counter): The Insatiable arena state — decrements at
  start of Enemy side turn (late); creature positions update from Amount; at
  critical amounts the fight resolves via kill logic.
- HATCH_POWER (Buff, Counter): decrements at end of owner's side turn (hatch
  timer; hatch action hosted by monster/relic).
- FAN_OF_KNIVES_POWER / PARRY_POWER / SEEKING_EDGE_POWER / THE_HUNT_POWER /
  THIEVERY_POWER / ACCELERANT_POWER: inert marker powers — no hooks of their
  own; queried by specific cards (Shiv / SovereignBlade / TheHunt success
  marker / theft logic) or by Poison trigger-count math (Accelerant).

## Temporary-stat powers (subclasses; revert at end of owner's side turn)

All of these are abstract-hosted by `TemporaryStrengthPower` /
`TemporaryDexterityPower` / `TemporaryFocusPower`: on apply they grant
±Amount of the base stat; at end of owner's side turn the same amount is
reversed. Type shows as Buff when the granted stat amount is positive, Debuff
when negative.

- TEMPORARY_STRENGTH_POWER family: TEMPORARY_STRENGTH_POWER,
  FLEX_POTION_POWER, COORDINATE_POWER, CRUSH_UNDER_POWER, DARK_SHACKLES_POWER,
  DYING_STAR_POWER, ENFEEBLING_TOUCH_POWER, FEEDING_FRENZY_POWER, MANGLE_POWER,
  PIERCING_WAIL_POWER, REPTILE_TRINKET_POWER — temporary ±Strength (Amount),
  reverted at end of owner's side turn.
- TEMPORARY_DEXTERITY_POWER family: TEMPORARY_DEXTERITY_POWER,
  ANTICIPATE_POWER, HELICAL_DART_POWER, SPEED_POTION_POWER — temporary
  ±Dexterity (Amount), reverted at end of owner's side turn.
- TEMPORARY_FOCUS_POWER family: TEMPORARY_FOCUS_POWER, FOCUSED_STRIKE_POWER,
  HOTFIX_POWER, SYNCHRONIZE_POWER — temporary ±Focus (Amount), reverted at end
  of owner's side turn.

## Character-kit and card-hosted powers

- DEMON_FORM_POWER (Buff, Counter): at start of owner's side turn, apply
  +Amount STRENGTH_POWER to owner.
- DARK_EMBRACE_POWER (Buff, Counter): draw Amount cards whenever an owner's
  card is Exhausted; Ethereal-triggered exhausts batch their draws to end of
  owner's side turn (Amount * ethereal count).
- ENRAGE_POWER (Buff, Counter): whenever a Skill card is played (by anyone),
  owner gains +Amount STRENGTH.
- RUPTURE_POWER (Buff, Counter): when owner takes unblocked damage during
  owner's side turn from a card source, that card's post-play resolution
  applies +Amount STRENGTH to owner (per-card tracking).
- FLAME_BARRIER_POWER (Buff, Counter): when owner is hit by a powered attack,
  dealer takes Amount unpowered damage. Removed at end of the opposing side's
  turn (not owner's).
- WRAITH_FORM_POWER (Debuff, Counter): at start of owner's side turn, apply
  -Amount DEXTERITY_POWER to owner.
- BIASED_COGNITION_POWER (Debuff, Counter): at start of owner's side turn,
  apply -Amount FOCUS_POWER to owner.
- BURST_POWER (Buff, Counter): owner's next Amount Skill plays count twice
  (ModifyCardPlayCount +1 per Skill); 1 stack consumed per Skill played;
  removed at end of owner's side turn.
- DUPLICATION_POWER (Buff, Counter): owner's next Amount card plays count
  twice (any card type); 1 stack consumed per card played; removed at end of
  owner's side turn.
- ONE_TWO_PUNCH_POWER (Buff, Counter): owner's next Amount Attack plays count
  twice; 1 stack consumed per Attack played; removed at end of owner's side
  turn.
- SIGNAL_BOOST_POWER (Buff, Counter): owner's next Amount Power plays count
  twice; 1 stack consumed per Power played.
- ECHO_FORM_POWER (Buff, Counter): first card owner plays each turn is played
  twice (ModifyCardPlayCount doubles the first-in-series play each turn).
- MAYHEM_POWER (Buff, Counter): at start of owner's pre-play phase, auto-play
  Amount cards from top of draw pile (not exhausted).
- STAMPEDE_POWER (Buff, Counter): at end of owner's auto post-play phase,
  auto-play Amount Attack cards from hand.
- HELLRAISER_POWER (Buff, Single): Strike-tagged cards drawn by owner can
  auto-play (infinite-autoplay cap 9) with bonus VFX; data resets at end of
  owner's side turn.
- PANACHE_POWER (Buff, Counter, instanced): every 5th card owner plays deals
  Amount unpowered damage to ALL hittable enemies (`CardsLeft` starts at 5,
  decrements per card played after the first, resets to 5 on proc and at turn
  end).
- WITHERING_PRESENCE_POWER (Buff, Counter): every 6th card the target player
  plays adds a Wither curse/status card to their hand (`CardsLeft` 6 → 0 then
  add Wither).
- ITERATION_POWER (Buff, Counter): draw Amount cards the first time owner
  draws a Status card each turn (AfterCardDrawn, source-hosted gating).
- PAGESTORM_POWER (Buff, Counter): whenever owner draws an Ethereal card,
  draw Amount more.
- VICIOUS_POWER (Buff, Counter): whenever owner applies VULNERABLE_POWER to
  anyone (amount > 0), draw Amount cards.
- SWORD_SAGE_POWER (Buff, Counter): adds Amount replay counters to Sovereign
  Blade-family cards (BaseReplayCount); removed when power leaves.
- MASTER_PLANNER_POWER (Buff, Single): after owner plays a Skill, that Skill
  gains the Sly keyword.
- IMPROVEMENT_POWER (Buff, Counter): at combat end, Upgrade Amount random
  upgradable cards in owner's deck.
- HEIST_POWER (Buff, Counter): if owner (thief) dies before cashing out,
  stolen Gold reward (Amount) is granted back to base.Target player.
- FORBIDDEN_GRIMOIRE_POWER / ROYALTIES_POWER / THE_SEALED_THRONE_POWER /
  NOSTALGIA_POWER / REBOUND_POWER / RETAIN_HAND_POWER /
  WELL_LAID_PLANS_POWER / STRATAGEM_POWER / ARSENAL_POWER: source-hosted
  utility powers —
  - RETAIN_HAND_POWER (Counter): owner's hand is not flushed at turn end
    (ShouldFlush false); decrements at end of owner's side turn.
  - REBOUND_POWER (Counter): played-card result pile/position modified
    (card returns per card text); decrements at end of owner's side turn.
  - ARSENAL_POWER (Counter): on cards generated for combat, applies +Amount
    STRENGTH (hosted by generating effect).
  - STRATAGEM_POWER (Counter): on shuffle, selected draw-pile cards move to
    hand (selection prefs hosted by source).
  - NOSTALGIA_POWER (Counter): modifies played-card result pile/position
    (hosted by source card text).
  - WELL_LAID_PLANS_POWER (Counter): end-of-turn hand flush selection logic
    (retained-card choice; BeforeFlushLate).
  - FORBIDDEN_GRIMOIRE_POWER / ROYALTIES_POWER / THE_SEALED_THRONE_POWER:
    combat-end / pre-play hosted logic; see hosting card text.
- BLACK_HOLE_POWER (Buff, Counter): when owner's player spends Stars on a
  card (last in series) or gains Stars, deal damage to all hittable enemies
  (amount hosted by DynamicVars).
- CALAMITY_POWER (Buff, Counter): after owner plays an Attack, add Amount
  random class-pool cards to owner's hand (card generation hosted by source).
- CALL_OF_THE_VOID_POWER (Buff, Counter): before owner's hand draw, add
  Distinct cards (with keyword application) to owner's hand — source-hosted
  draw pollution.
- CREATIVE_AI_POWER (Buff, Counter): before owner's hand draw, add Amount
  distinct Power cards to hand.
- FOREGONE_CONCLUSION_POWER (Buff, Counter): before owner's hand draw,
  shuffle if necessary and move a selected draw-pile card to hand.
- HELLO_WORLD_POWER (Buff, Counter): before owner's hand draw (AmountOnTurnStart
  >= 1), add distinct unlocked cards to hand.
- INFINITE_BLADES_POWER (Buff, Counter): before owner's hand draw, create
  Amount Shiv cards in hand.
- NIGHTMARE_POWER (Buff, Counter): before owner's hand draw, add Amount clones
  of the selected card to hand (clones are affliction-cleared).
- SENTRY_MODE_POWER (Buff, Counter): before owner's hand draw, add Amount
  SweepingGaze cards to hand.
- SPECTRUM_SHIFT_POWER (Buff, Counter): before owner's hand draw, add Amount
  distinct Colorless-pool cards to hand.
- GRAVITY_POWER (Buff, Counter): each card owner plays deals Amount unpowered
  damage to all hittable enemies; power removed at end of owner's side turn.
- SERPENT_FORM_POWER (Buff, Counter): each card owner plays deals Amount
  unpowered damage to a random enemy (per-card amount tracked at play time).
- STORM_POWER (Buff, Counter): each Power card owner plays Channels Amount
  Lightning orbs.
- SUBROUTINE_POWER (Buff, Counter): Power-card play tracking — trigger hosted
  by source card (see card text).
- MONOLOGUE_POWER (Buff, Counter): card-play strength engine — tracks
  StrengthApplied; applies/revokes STRENGTH per cards played (hosted by
  source card; display shows accumulated Strength).
- THE_BOMB_POWER (Buff, Counter, instanced): decrements at end of owner's
  side turn while Amount > 1; at Amount <= 1, deals DynamicVars.Damage
  (default DamageVar 40 unpowered) to ALL hittable enemies, then removed.
- HIGH_VOLTAGE_POWER (Buff, Counter): at end of owner's side turn, apply
  +Amount STRENGTH_POWER to owner.
- THUNDER_POWER (Buff, Counter): when owner's player evokes a Lightning orb,
  deal Amount unpowered damage to the evoke targets.
- NECRO_MASTERY_POWER (Buff, Counter): when the owner's Osty pet loses HP,
  deal (HP lost * Amount) unblockable unpowered damage to all hittable
  enemies.
- HAUNT_POWER (Buff, Counter): after owner plays a Soul card, deal damage to
  a random enemy (amount hosted by source).
- HAMMER_TIME_POWER (Buff, Single): when any other player forges, all other
  living players also Forge that amount (Hammer Time relay).
- FURNACE_POWER (Buff, Counter): at start of owner's side turn, Forge Amount
  (upgrade Amount cards via forge logic).
- COUNTER / misc card-hosted: see hosting card for exact trigger amounts.

## Other monster/elite powers

- MINION_POWER: see core statuses.
- TERRITORIAL_POWER (Buff, Counter): at end of owner's side turn, apply
  +Amount STRENGTH_POWER to owner.
- RITUAL_POWER: see core statuses.
- CURL_UP_POWER (Buff, Counter): when owner would take attack damage from a
  new card source, owner curls — gains Block (hosted amount) once per
  incoming card; data resets via card-play tracking (Giant Louse).
- PLOW_POWER (Debuff, Counter): if owner takes unblocked damage while
  CurrentHp <= Amount, owner is stunned (temporary-strength powers on owner
  are consumed — decomp clears TemporaryStrengthPower instances; stun logic
  monster-hosted).
- SHRIEK_POWER (Debuff, Counter, negative allowed): if owner takes unblocked
  damage while CurrentHp <= Amount, owner is stunned into TerrorEel terror
  state and the power removes itself.
- IMBALANCED_POWER (Debuff, Single): when owner's attack is fully blocked,
  owner is stunned (BowlbugRock sets IsOffBalance instead).
- MONARCHS_GAZE_POWER (Buff, Counter): when owner's powered attack hits,
  apply Amount MONARCHS_GAZE_STRENGTH_DOWN_POWER to the target (strength-down
  engine hosted on target).
- MONARCHS_GAZE_STRENGTH_DOWN_POWER (Debuff, Counter): strength-down marker
  applied by MonarchsGaze; paired debuff logic hosted by Monarch cards.
- PAINFUL_STABS_POWER / SKITTISH_POWER: see stances — SKITTISH_POWER (Buff,
  Counter): if owner has not gained Block this turn and takes card-sourced
  attack damage, owner gains Amount Block (once per turn flag; flag resets at
  end of opposing side's turn).
- CONSUMING_SHADOW_POWER (Buff, Counter): at end of owner's side turn, if
  owner's player has orbs, evoke the last orb Amount times.
- FURNACE / FORGE-related: see FURNACE_POWER, HAMMER_TIME_POWER.
- FOCUS / orb kits: see FOCUS_POWER.
- BACK_ATTACK_LEFT_POWER / BACK_ATTACK_RIGHT_POWER (Buff, Single): inert
  facing markers consumed by SURROUNDED_POWER checks.
- BATTLEWORN_DUMMY_TIME_LIMIT_POWER / SANDPIT_POWER: see stances.

## Not a power

- BURNING_BLOOD is a Relic (Ironclad), not a power — see relics.md.
