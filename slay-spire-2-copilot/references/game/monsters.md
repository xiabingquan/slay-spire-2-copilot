# Monsters

Enemy reference: move tables and passives auto-extracted from game source
(STS2-Agent extraction, game build near v0.107-0.111) plus live-play notes
on v0.107.1. Move tags map to intents: SingleAttack / MultiAttack(n) /
Buff / Debuff / Defend / Stun / Sleep / Status(n) / Summon / Heal / Hidden.

- Architect: NOTHING = Hidden intent.
- AssassinRubyRaider: KILLSHOT = single attack.
- Axebot: ONE_TWO = multi attack ×2; SHARPEN = buff. Passive: StockPower (death spawns next robot variant).
- AxeRubyRaider: BIG_SWING = single attack.
- BigDummy: NOTHING = Hidden intent.
- BowlbugEgg: no listed moves.
- BowlbugNectar: THRASH = single attack; BUFF = buff; THRASH2 = single attack.
- BowlbugRock: HEADBUTT = single attack; DIZZY = stun. Passive: ImbalancedPower.
- BowlbugSilk: TRASH = multi attack ×2.
- BruteRubyRaider: BEAT = single attack.
- BygoneEffigy (elite): INITIAL_SLEEP/WAKE/SLEEP cycle + SLASHES = single attack. Passive: SlowPower — alternating empty-intent slow turns with heavy charged hits; fortify before heavy turns.
- Byrdonis: PECK = multi attack; SWOOP = single attack. Passive: TerritorialPower.
- CalcifiedCultist / DampCultist / DevotedSculptor: INCANTATION / FORBIDDEN_INCANTATION = buff.
- CeremonialBeast (boss): STAMP = buff; STUN = stun; STOMP = single attack. Boss applies RINGING to player (hand card-play lockout — observed live).
- Chomper: CLAMP = multi attack ×2. Passive: ArtifactPower.
- CorpseSlug: WHIP_SLAP = multi; GLOMP = single; GOOP = debuff. Passive: RavenousPower.
- Crusher: THRASH + ENLARGING_STRIKE = single attacks; ADAPT = buff. Passive: BackAttackLeftPower + CrabRagePower.
- CubexConstruct: CHARGE_UP = buff; EXPEL_BLAST = multi ×2; SUBMERGE = defend (gain Block + ArtifactPower).
- DecimillipedeSegment: WRITHE = multi ×2; REATTACH = heal (SetMaxAndCurrentHp + ReattachPower) — kill segments carefully; back/front/middle variants exist.
- DevotedSculptor: FORBIDDEN_INCANTATION = buff.
- Door: DOOR_SLAM = multi. Passive: DoorRevivalPower.
- Doormaker: WHAT_IS_IT = stun; BEAM = single attack.
- Entomancer: PHEROMONE_SPIT = buff; BEES = multi. Passive: PersonalHivePower.
- Exoskeleton: SKITTER = multi; MANDIBLE = single; ENRAGE = buff. Passive: HardToKillPower.
- EyeWithTeeth: DISTRACT = status ×3. Passive: IllusionPower.
- Fabricator: FABRICATE = summon; DISINTEGRATE = single attack.
- FakeMerchantMonster: SWIPE = single; SPEW_COINS = multi ×8; ENRAGE = buff.
- FatGremlin: SPAWNED = stun.
- FlailKnight: WAR_CHANT = buff; FLAIL = multi ×2; RAM = single attack.
- Flyconid: VULNERABLE_SPORES = debuff; SMASH = single attack.
- Fogmog: ILLUSION = summon; HEADBUTT = single attack.
- FossilStalker: LATCH = single; LASH = multi. Passive: SuckPower.
- FrogKnight: FOR_THE_QUEEN = buff; STRIKE_DOWN_EVIL + BEETLE_CHARGE = single attacks. Passive: PlatingPower.
- FuzzyWurmCrawler: FIRST_ACID_GOOP / ACID_GOOP = single attacks.
- GasBomb: no listed moves. Passive: MinionPower.
- GlobeHead: THUNDER_STRIKE = multi ×3. Passive: GalvanicPower (links GALVANIZED affliction).
- GremlinMerc: GIMME = multi. Passive: SurprisePower.
- Guardbot: GUARD = defend.
- HauntedShip: SWIPE = single; STOMP = multi; HAUNT = debuff.
- HunterKiller: TENDERIZING_GOOP = debuff; BITE = single; PUNCTURE = multi ×3.
- InfestedPrism: JAB = single; WHIRLWIND = multi. Passive: VitalSparkPower.
- Inklet: JAB = single; WHIRLWIND = multi ×3; PIERCING_GAZE = single. Passive: SlipperyPower (first-hit damage greatly reduced, charges consumed per hit — observed live).
- KinFollower: QUICK_SLASH = single; BOOMERANG = multi ×2; POWER_DANCE = buff. Passive: MinionPower.
- KinPriest: BEAM = multi ×3; RITUAL = buff (strength growth — kill priority).
- KnowledgeDemon: CURSE_OF_KNOWLEDGE = debuff; SLAP = single; KNOWLEDGE_OVERWHELMING = multi ×3.
- LagavulinMatriarch: SLEEP = sleep; SLASH = single; DISEMBOWEL = multi. Passives: PlatingPower + AsleepPower.
- LeafSlimeM: CLUMP_SHOT = single; STICKY_SHOT = status ×2.
- LeafSlimeS: BUTT = single; GOOP = status ×1.
- LivingFog: SUPER_GAS_BLAST = single attack.
- LivingShield: SHIELD_SLAM = single attack. Passive: RampartPower (block regeneration source — strip with DISMANTLE-class effects, observed live).
- LouseProgenitor: POUNCE = single attack. Passive: CurlUpPower.
- MagiKnight: DAMPEN = debuff; PREP = defend; MAGIC_BOMB + RAM = single attacks.
- Mawler: RIP_AND_TEAR = single; ROAR = debuff; CLAW = multi ×2.
- MechaKnight: CHARGE = single; FLAMETHROWER = status ×4; HEAVY_CLEAVE = single. Passive: ArtifactPower.
- MysteriousKnight: passives StrengthPower + PlatingPower.
- Myte: TOXIC = status ×2; BITE = single attack.
- Nibbit: BUTT = single; HISS = buff.
- Noisebot: NOISE = status ×2.
- Osty: Necrobinder companion creature (summoned via Summon; many Necrobinder cards command Osty — see cards_zh.md).
- Ovicopter: LAY_EGGS = summon; SMASH = single; NUTRITIONAL_PASTE = buff.
- Queen-boss family (live play): applies CHAINS_OF_BINDING_POWER + MINION_POWER factory spawns; block suppression stacks with Frail — observed zeroing Block.
- Robot-assembly family (live play): STOCK_POWER — each death spawns next robot variant until fight end.
- ShrinkerBeetle (缩小甲虫, live play 2026-09-17): empty-intent turn applies SHRINK_POWER to the player (attack damage reduced while it lives); follows with single attacks ~7.
- ThievingHopper (偷窃草蜢/偷窃跳虫, Act 2, live play 2026-09-17): THIEVERY_MOVE = single attack (~17) + applies SWIPE_POWER (steals gold); EscapeArtistPower charges on the side; CardDebuff intent injects status cards (Wound observed).
- Vantom (墨影幻灵, Act 1 boss, live play 2026-09-17): INK_BLOT = single ~7; INKY_LANCE = multi ×2 (~8 each); DISMEMBER = heavy single (~26-28) + status cards ×3; PREPARE = buff (+2 Strength observed). Passive: SlipperyPower — incoming hit damage greatly reduced per charge (started at 8 charges; each attack hit consumes 1 — multi-hits strip faster).
- PhrogParasite (elite, live play): INFESTED_POWER spawns 4x ~17-21hp adds on death — save AOE for the spawn wave.
- CeremonialBeast (boss, live play): RINGING_POWER on player flips hand cards to can_play=false.

## Reading monsters mid-run

- state.combat.creatures[].intent carries id/damage/times/is_attack — pair with this table for what follows.
- Hidden intents (NOTHING) resolve later — play defensively.
- Sleep/stun cycles (BygoneEffigy, LagavulinMatriarch): burst windows after wake.
- ArtifactPower charges: debuffs are wasted until artifact strips.
- Doom threshold kills (Necrobinder runs) bypass normal damage race.
