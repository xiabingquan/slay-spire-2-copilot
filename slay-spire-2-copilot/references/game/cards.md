# Cards

Card reference by character. Costs/effects from community databases
(stratgg.com character pages, spire-codex.com, mobalytics, namu.wiki)
cross-checked with observed play on v0.107.1 and game-internal class names.
Shared pattern: Strike = 1-cost attack deal 6; Defend = 1-cost skill gain
5 Block (each character has its own copy).

## Ironclad

- STRIKE_IRONCLAD: 1, attack, deal 6 damage.
- DEFEND_IRONCLAD: 1, skill, gain 5 Block.
- BASH: 2, attack, deal 8 damage; apply 2 Vulnerable.
- ANGER: 0, attack, deal 6 damage; add a copy of itself to your discard pile.
- ARMAMENTS: 1, skill, gain 5 Block; upgrade a card in your hand.
- ASHEN_STRIKE: 1, attack, deal 6 damage +3 for each card in your exhaust pile.
- BATTLE_TRANCE: 0, skill, draw 3 cards; no more draws this turn.
- BLUDGEON: 3, attack, deal 32 damage (35-49 observed with upgrades/Vulnerable).
- BLOOD_WALL: 2, skill, costs 2 HP, gain 16 Block (live: also chips ~8 to nearby enemies; never play below ~5 HP).
- BLOODLETTING: 0, skill, costs 3 HP, gain 2 energy.
- BODY_SLAM: 1, attack, deal damage equal to your current Block.
- BREAKTHROUGH: 1, attack, deal 9 damage to ALL enemies; costs 1 HP.
- BULLY: 0, attack, deal 4 damage +2 per Vulnerable stack on the target.
- BURNING_PACT: 1, skill, exhaust 1 card; draw 2 cards.
- CINDER: 2, attack, deal 17 damage; exhaust the top card of your draw pile.
- DEMONIC_SHIELD: 0, skill, costs 1 HP; give another player Block equal to yours.
- DISMANTLE: 1, attack, deal 8 damage; if the enemy is Vulnerable it hits twice (live: also strips one enemy power/charge).
- FIGHT_ME: 2, attack, ~10 damage; grants STRENGTH to both player and target ("duel invite").
- HAVOC: 1, skill, play then exhaust the top card of your draw pile.
- HEADBUTT: 1, attack, deal 9 damage; move a discarded card to the top of your draw pile.
- IRON_WAVE: 1, attack, deal 5 damage and gain 5 Block.
- MOLTEN_FIST: 1, attack, deal 10 damage; double the target's Vulnerable.
- PERFECTED_STRIKE: 2, attack, deal 6 damage +2 for every owned card containing "Strike" (19-32 observed).
- POMMEL_STRIKE: 1, attack, deal 9 damage; draw 1 card.
- RAMPAGE: 1, attack, ~6 base damage; grows per play.
- SECOND_WIND: exhaust hand cards; gain Block per card exhausted (30+ observed in a boss fight).
- SETUP_STRIKE: 1, attack, deal 7 damage; gain 2 Strength this turn.
- SHRUG_IT_OFF: 1, skill, gain 8 Block; draw 1 card.
- SWORD_BOOMERANG: 1, attack, deal 3 damage to a random enemy 3 times; Strength applies per hit.
- THUNDERCLAP: 1, attack, deal 4 damage to ALL enemies; apply 1 Vulnerable to each.
- TREMBLE: 1, skill, apply 2 Vulnerable.
- TRUE_GRIT: 1, skill, gain 7 Block; exhaust 1 random card.
- TWIN_STRIKE: 1, attack, deal 5 damage twice; Strength per hit.
- UPPERCUT: 2, attack, damage + Weak + Vulnerable (~8-21 upgraded observed; dual-debuff staple).
- WHIRLWIND: X, attack, deal damage to ALL enemies X times (27-81 total observed with Strength/energy).
- Ironclad pool names pending effect data: Demon Form, Limit Break, Heavy Blade, Corruption, Feel No Pain, Sentinel, Offering, Immolate, Reaper, Dark Embrace, Pact's End, Feed, Fiend Fire, Impervious, Inflame, Juggernaut, Rage, Rupture, Shockwave, Hemokinesis, Dual Wield, Entrench, Flame Barrier, Hellraiser, Hegemony, Hotfix, I Am Invincible, Kingly Kick, Knockout Blow, Mad Science, Omnislice, Scavenge, Scourge, Sovereign Blade, Spoils Map, Terraforming, The Hunt, Unmovable.

## Silent

- STRIKE_SILENT: 1, attack, deal 6 damage.
- DEFEND_SILENT: 1, skill, gain 5 Block.
- NEUTRALIZE: 0, attack, deal 3 damage; apply 1 Weak.
- SURVIVOR: 1, skill, gain 8 Block; discard 1 card.
- ACROBATICS: 1, skill, draw 3 cards; discard 1 card.
- ACCURACY: 1, power, Shivs deal 4 additional damage.
- ANTICIPATE: 0, skill, gain 3 Dexterity this turn.
- BACKFLIP: 1, skill, gain 5 Block; draw 2 cards.
- BACKSTAB: 0, attack, deal 11 damage.
- BLADE_DANCE: 1, skill, add 3 Shivs to your hand.
- BLUR: 1, skill, gain 5 Block; Block is not removed at the start of your next turn.
- BOUNCING_FLASK: 2, skill, apply 3 Poison to a random enemy 3 times.
- BUBBLE_BUBBLE: 1, skill, if the enemy has Poison, apply 9 Poison.
- CALCULATED_GAMBLE: 0, skill, discard your hand, then draw that many cards.
- CLOAK_AND_DAGGER: 1, skill, gain 6 Block; add 1 Shiv to your hand.
- DAGGER_SPRAY: 1, attack, deal 4 damage to ALL enemies twice.
- DAGGER_THROW: 1, attack, deal 9 damage; draw 1 card; discard 1 card.
- DEADLY_POISON: 1, skill, apply 5 Poison.
- DEFLECT: 0, skill, gain 4 Block.
- DODGE_AND_ROLL: 1, skill, gain 4 Block; next turn gain 4 Block.
- FLICK_FLACK: 1, attack (Sly), deal 7 damage to ALL enemies (upgraded 9).
- LEADING_STRIKE: 1, attack, deal 7 damage; add 1 Shiv to your hand.
- PIERCING_WAIL: 1, skill, ALL enemies lose 6 Strength this turn.
- POISONED_STAB: 1, attack, deal 6 damage; apply 3 Poison.
- PREPARED: 0, skill, draw 1 card; discard 1 card.
- RICOCHET: 2, attack (Sly), deal 3 damage to a random enemy 4 times (upgraded 5 hits; namu lists cost 1 — version drift).
- SLICE: 0, attack, deal 6 damage.
- SNAKEBITE: 2, skill, apply 7 Poison.
- SUCKER_PUNCH: 1, attack, deal 8 damage; apply 1 Weak.
- UNTOUCHABLE: 2, skill (Sly), gain 9 Block (upgraded 12; namu lists cost 1 — version drift).
- Sly keyword cards pending full data: Abrasive (Sly, +1 Dexterity and +1 Thorns, Thorns upgrades to 6), Tactician (Sly, grants energy when discarded), Haze (Sly).
- Silent pool names pending effect data: Catalyst, Corpse Explosion, Noxious Fumes, Adrenaline, Well-Laid Plans, Outbreak, Alchemize, Bullet Time, Burst, Calculated Gamble combos (Storm of Steel), Envenom, Escape Plan, Expertise, Finisher, Flechettes, Footwork, Grand Finale, Leg Sweep, Malaise, Master of Strategy, Nightmare, Phantasmal-style tools (Phantom Blades), Piercing line tools (Pinpoint), Poison fumes line (Putrefy), Reflex, Setup line (Sneaky), Tools of the Trade, Wraith Form.

## Defect

- STRIKE_DEFECT: 1, attack, deal 6 damage.
- DEFEND_DEFECT: 1, skill, gain 5 Block.
- ZAP: 1, skill, Channel 1 Lightning.
- DUALCAST: 1, skill, evoke your rightmost Orb twice.
- BALL_LIGHTNING: 1, attack, deal 7 damage; Channel 1 Lightning.
- BARRAGE: 1, attack, deal 5 damage for each Channeled Orb.
- BEAM_CELL: 0, attack, deal 3 damage; apply 1 Vulnerable.
- BOOT_SEQUENCE: 0, skill, gain 10 Block.
- BOOST_AWAY: 0, skill, gain 6 Block; add a Dazed to your discard pile.
- BULK_UP: 2, power, lose 1 Orb Slot; gain 2 Strength and 2 Dexterity.
- CAPACITOR: 1, power, gain 2 Orb Slots.
- CHAOS: 1, skill, Channel 1 random Orb.
- CHARGE_BATTERY: 1, skill, gain 7 Block; gain energy next turn.
- CHILL: 0, skill, Channel Frost per enemy.
- CLAW: 0, attack, deal 3 damage; all Claw cards deal +2 this combat.
- COLD_SNAP: 1, attack, deal 6 damage; Channel 1 Frost.
- COMPACT: 1, skill, gain 6 Block; hand Status cards become Fuel.
- COMPILE_DRIVER: 1, attack, deal 7 damage; draw 1 card per unique Orb type.
- COOLHEADED: 1, skill, Channel 1 Frost; draw 1 card.
- FOCUSED_STRIKE: 1, attack, deal 9 damage; gain 1 Focus this turn.
- GO_FOR_THE_EYES: 0, attack, deal 3 damage; apply 1 Weak if the enemy intends attack.
- GUNK_UP: 1, attack, deal 4 damage 3 times; add a Slimed to your discard pile.
- HOLOGRAM: 1, skill, gain 3 Block; return a discard-pile card to your hand.
- HOTFIX: 0, skill, gain 2 Focus this turn.
- LEAP: 1, skill, gain 9 Block.
- LIGHTNING_ROD: 1, skill, gain 4 Block; Channel Lightning at start of next 2 turns.
- MOMENTUM_STRIKE: 1, attack, deal 10 damage; its own cost drops to 0.
- SWEEPING_BEAM: 1, attack, deal 6 damage to ALL enemies; draw 1 card.
- TURBO: 0, skill, gain 2 energy; add a Void to your discard pile.
- UPROAR: 2, attack, deal 5 damage twice; play a random Attack from your draw pile.
- Defect pool names pending effect data: All for One, Biased Cognition, Buffer, Colossus, Consume, Creative AI, Darkness, Defragment, Double Energy, Echo Form, Fission, Fusion, Glacier, Hello World, Hyperbeam, Loop, Machine Learning, Meteor Strike, Multi-Cast, Rainbow, Reboot, Recursion, Recycle, Reinforced Body, Seek, Skim, Steam Barrier, Storm, Sunder, Tempest, Tesla Coil, White Noise.

## Necrobinder

- STRIKE_NECROBINDER: 1, attack, deal 6 damage.
- DEFEND_NECROBINDER: 1, skill, gain 5 Block.
- BODYGUARD: 1, skill, Summon 5.
- UNLEASH: 1, attack, Osty deals 6 damage + additional damage equal to Osty's current HP.
- AFTERLIFE: 1, skill, Summon 6.
- BLIGHT_STRIKE: 1, attack, deal 8 damage; apply Doom equal to damage dealt.
- BONE_SHARDS: 1, attack, if Osty is alive: Osty deals 9 damage to ALL enemies, you gain 9 Block, then Osty dies.
- BORROWED_TIME: 0, skill, apply 3 Doom to yourself; gain 1 energy.
- BURY: 4+, attack, deal 52 damage.
- CALCIFY: 1, power, Osty's attacks deal 4 additional damage.
- CAPTURE_SPIRIT: 1, skill, enemy loses 3 HP; add 3 Souls to your draw pile.
- CLEANSE: 1, skill, Summon 3; exhaust 1 card from your draw pile.
- DEFILE: 1, attack, deal 13 damage.
- DEFY: 1, skill, gain 6 Block; apply 1 Weak.
- DRAIN_POWER: 1, attack, deal 10 damage; upgrade 2 random cards in your discard pile.
- FEAR: 1, attack, deal 7 damage; apply 1 Vulnerable.
- FLATTEN: 2, attack, Osty deals 12 damage; costs 0 if Osty attacked this turn.
- GRAVE_WARDEN: 1, skill, gain 8 Block; add a Soul to your draw pile.
- GRAVEBLAST: 1, attack, deal 4 damage; put a discard-pile card into your hand.
- INVOKE: 1, skill, next turn Summon 2 and gain 2 energy.
- NEGATIVE_PULSE: 1, skill, gain 5 Block; apply 7 Doom to ALL enemies.
- POKE: 0, attack, Osty deals 6 damage.
- PULL_AGGRO: 2, skill, Summon 4; gain 7 Block.
- REAP: 3, attack, deal 27 damage.
- REAVE: 1, attack, deal 9 damage; add a Soul to your draw pile.
- SCOURGE: 1, skill, apply 13 Doom; draw 1 card.
- SCULPTING_STRIKE: 1, attack, deal 8 damage; add Ethereal to a card in your hand.
- SNAP: 1, attack, Osty deals 7 damage; add Retain to a card in your hand.
- SOW: 1, attack, deal 8 damage to ALL enemies.
- WISP: 0, skill, gain 1 energy.
- Necrobinder pool names pending effect data: Death's Door, Death March, Necro Mastery, Undeath, Call of the Void, Legion of Bone, Minion Dive Bomb, Minion Sacrifice, Minion Strike, Deathbringer, End of Days, Eidolon, Haunt, Howl from Beyond, Memento Mori, Reanimate, Shatter, Soul Storm, Summon Forth, The Scythe.

## Regent

- STRIKE_REGENT: 1, attack, deal 6 damage.
- DEFEND_REGENT: 1, skill, gain 5 Block.
- FALLING_STAR: 0, attack, deal 7 damage; apply 1 Weak; apply 1 Vulnerable.
- VENERATE: 1, skill, gain 2 stars (★).
- ALIGNMENT: 0, skill, gain 2 energy.
- ASTRAL_PULSE: 0, attack, deal 14 damage to ALL enemies.
- BEGONE: 1, attack, deal 4 damage; transform a card in your hand into Minion Dive Bomb.
- BLACK_HOLE: 1, power, whenever you spend or gain a star, deal 3 damage to ALL enemies.
- BULWARK: 2, skill, gain 13 Block; Forge 10.
- CELESTIAL_MIGHT: 2, attack, deal 6 damage 3 times.
- CHARGE!!: 1, skill, transform 2 draw-pile cards into Minion Strikes.
- CHILD_OF_THE_STARS: 1, power, whenever you spend a star, gain 2 Block per star spent.
- CLOAK_OF_STARS: 0, skill, gain 7 Block.
- COLLISION_COURSE: 0, attack, deal 9 damage; add a Debris to your hand.
- CONQUEROR: 1, skill, Forge 3; Sovereign Blade deals double damage to an enemy this turn.
- COSMIC_INDIFFERENCE: 1, skill, gain 6 Block; move a discard-pile card to the top of your draw pile.
- CRESCENT_SPEAR: 1, attack, deal 6 damage +2 for each star-cost card in your deck.
- CRUSH_UNDER: 1, attack, deal 7 damage to ALL enemies; they lose 1 Strength this turn.
- GATHER_LIGHT: 1, skill, gain 7 Block; gain 1 star.
- GLITTERSTREAM: 2, skill, gain 11 Block; next turn gain 4 Block.
- GLOW: 1, skill, gain 1 star; draw 2 cards.
- GUIDING_STAR: 1, attack, deal 12 damage; next turn draw 2 cards.
- HIDDEN_CACHE: 1, skill, gain 1 star; next turn gain 3 stars.
- KNOW_THY_PLACE: 0, skill, apply 1 Weak; apply 1 Vulnerable.
- PATTER: 1, skill, gain 8 Block; gain 2 Vigor.
- PHOTON_CUT: 1, attack, deal 10 damage; draw 1 card; put a hand card on top of your draw pile.
- REFINE_BLADE: 1, skill, Forge 6; next turn gain energy.
- SOLAR_STRIKE: 1, attack, deal 8 damage; gain 1 star.
- SPOILS_OF_BATTLE: 1, skill, Forge 10.
- WROUGHT_IN_WAR: 0, attack, deal 7 damage; Forge 5.
- Regent pool names pending effect data: Seven Stars, Summon Forth, Seeking Edge, Beat into Shape, Kingly Punch, Lunar Blast, Manifest Authority, Monarch's Gaze, Pagestorm, Protector, Royal Gamble, Royalties, Stratagem, The Sealed Throne, Tyranny, Venerate-line payoffs (Vitruvian interactions), Guillotine-style finishers (Heavenly Drill, Helix Drill).

## Colorless / event / status names (pool, effects pending in part)

- ABRASIVE / ADAPTIVE_STRIKE / APOTHEOSIS / APPARITION / ASCENDERS_BANE / BAD_LUCK / BURN / BYRDONIS_EGG (unplayable -1-cost status, see afflictions.md) / CLUMSY / DARK_SHACKLES / DAZED / DEBT / DECAY / DOUBT / ENLIGHTENMENT / EXPECT_A_FIGHT / FRANTIC_ESCAPE / FRIENDSHIP / GOLD_AXE / GREED / INJURY / JACK_OF_ALL_TRADES / LANTERN_KEY / MIND_BLAST / NORMALITY / NULL / PANACHE / POOR_SLEEP / POTION-shaped tokens / PYRE / REGRET / SECRET_TECHNIQUE / SECRET_WEAPON / SHAME / SHIV (0-cost 4-damage token from Silent kits; Accuracy scales it) / SLIMED / SOOT / SPOILS_MAP / STOMP / THINKING_AHEAD / TRANSMUTATION-style (Trash to Treasure) / WISH / WOUND / WRITHE.
- SHIV: 0, attack token, deal damage (Silent kit; Accuracy +4 observed in DB data).

## Screen notes (card reward / selection)

- Reward screens may show unclaimable buttons when potion slots are full — click no-ops; proceed leaves the screen.
- Skip button exists on most card_reward screens; NDeckCardSelectScreen removal flow has none (mandatory pick).
- AROMA_OF_CHAOS event "LET_GO": opens deck transform — pick any deck card, it transforms at random (STRIKE -> POMMEL_STRIKE observed).
- Card pool sizes (spire-codex): Ironclad 87, Silent 88, Defect 88, Necrobinder 88, Regent 88; 577 total incl. colorless/status/token.
