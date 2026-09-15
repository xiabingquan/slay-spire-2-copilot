# 怪物

敌人参考：招式表与被动技能源自游戏源码提取（STS2-Agent extraction，
游戏版本约 v0.107-0.111）及 v0.107.1 实战记录。招式标签对应意图：
SingleAttack / MultiAttack(n) / Buff / Debuff / Defend / Stun / Sleep /
Status(n) / Summon / Heal / Hidden。

- Architect：NOTHING = 隐藏意图。
- AssassinRubyRaider：KILLSHOT = 单次攻击。
- Axebot：ONE_TWO = 多段攻击 ×2；SHARPEN = 增益。被动：StockPower（死亡
  召唤下一机器人形态）。
- AxeRubyRaider：BIG_SWING = 单次攻击。
- BigDummy：NOTHING = 隐藏意图。
- BowlbugEgg：无已列招式。
- BowlbugNectar：THRASH = 单次攻击；BUFF = 增益；THRASH2 = 单次攻击。
- BowlbugRock：HEADBUTT = 单次攻击；DIZZY = 眩晕。被动：ImbalancedPower。
- BowlbugSilk：TRASH = 多段攻击 ×2。
- BruteRubyRaider：BEAT = 单次攻击。
- BygoneEffigy（旧日雕像精英）：INITIAL_SLEEP/WAKE/SLEEP 循环 +
  SLASHES = 单次攻击。被动：SlowPower——空意图慢速回合与高额蓄力重击
  交替；重击回合前做好防御。
- Byrdonis（墨宝）：PECK = 多段攻击；SWOOP = 单次攻击。被动：
  TerritorialPower；SlipperyPower（首次受击伤害大减，充能每受击消耗——
  实战验证）。
- CalcifiedCultist / DampCultist / DevotedSculptor：INCANTATION /
  FORBIDDEN_INCANTATION = 增益。
- CeremonialBeast（仪式兽 boss）：STAMP = 增益；STUN = 眩晕；STOMP =
  单次攻击。Boss 对玩家施加 RINGING（手牌出牌封锁——实战验证）。
- Chomper：CLAMP = 多段攻击 ×2。被动：ArtifactPower。
- CorpseSlug：WHIP_SLAP = 多段；GLOMP = 单次；GOOP = 减益。被动：
  RavenousPower。
- Crusher：THRASH 与 ENLARGING_STRIKE = 单次攻击；ADAPT = 增益。被动：
  BackAttackLeftPower + CrabRagePower。
- CubexConstruct：CHARGE_UP = 增益；EXPEL_BLAST = 多段 ×2；SUBMERGE =
  防御（获得格挡 + ArtifactPower）。
- DecimillipedeSegment（千足虫节段）：WRITHE = 多段 ×2；REATTACH =
  治疗（SetMaxAndCurrentHp + ReattachPower）——节段需谨慎处理；存在
  back/front/middle 变体。
- DevotedSculptor：FORBIDDEN_INCANTATION = 增益。
- Door：DOOR_SLAM = 多段。被动：DoorRevivalPower。
- Doormaker：WHAT_IS_IT = 眩晕；BEAM = 单次攻击。
- Entomancer：PHEROMONE_SPIT = 增益；BEES = 多段。被动：PersonalHivePower。
- Exoskeleton：SKITTER = 多段；MANDIBLE = 单次；ENRAGE = 增益。被动：
  HardToKillPower。
- EyeWithTeeth：DISTRACT = 状态 ×3。被动：IllusionPower。
- Fabricator：FABRICATE = 召唤；DISINTEGRATE = 单次攻击。
- FakeMerchantMonster：SWIPE = 单次；SPEW_COINS = 多段 ×8；ENRAGE = 增益。
- FatGremlin：SPAWNED = 眩晕。
- FlailKnight：WAR_CHANT = 增益；FLAIL = 多段 ×2；RAM = 单次攻击。
- Flyconid：VULNERABLE_SPORES = 减益；SMASH = 单次攻击。
- Fogmog：ILLUSION = 召唤；HEADBUTT = 单次攻击。
- FossilStalker：LATCH = 单次；LASH = 多段。被动：SuckPower。
- FrogKnight：FOR_THE_QUEEN = 增益；STRIKE_DOWN_EVIL 与 BEETLE_CHARGE =
  单次攻击。被动：PlatingPower。
- FuzzyWurmCrawler：FIRST_ACID_GOOP / ACID_GOOP = 单次攻击。
- GasBomb：无已列招式。被动：MinionPower。
- GlobeHead：THUNDER_STRIKE = 多段 ×3。被动：GalvanicPower（关联
  GALVANIZED 减益）。
- GremlinMerc：GIMME = 多段。被动：SurprisePower。
- Guardbot：GUARD = 防御。
- HauntedShip：SWIPE = 单次；STOMP = 多段；HAUNT = 减益。
- HunterKiller：TENDERIZING_GOOP = 减益；BITE = 单次；PUNCTURE =
  多段 ×3。
- InfestedPrism（异蛙寄生虫系）：JAB = 单次；WHIRLWIND = 多段。被动：
  VitalSparkPower；实战变体 INFESTED_POWER 死亡时生成 4 只约 17-21hp
  小怪——AOE 留给召唤波。
- Inklet：JAB = 单次；WHIRLWIND = 多段 ×3；PIERCING_GAZE = 单次。被动：
  SlipperyPower。
- KinFollower：QUICK_SLASH = 单次；BOOMERANG = 多段 ×2；POWER_DANCE =
  增益。被动：MinionPower。
- KinPriest：BEAM = 多段 ×3；RITUAL = 增益（力量成长——优先击杀）。
- KnowledgeDemon：CURSE_OF_KNOWLEDGE = 减益；SLAP = 单次；
  KNOWLEDGE_OVERWHELMING = 多段 ×3。
- LagavulinMatriarch：SLEEP = 睡眠；SLASH = 单次；DISEMBOWEL = 多段。
  被动：PlatingPower + AsleepPower。
- LeafSlimeM：CLUMP_SHOT = 单次；STICKY_SHOT = 状态 ×2。
- LeafSlimeS：BUTT = 单次；GOOP = 状态 ×1。
- LivingFog：SUPER_GAS_BLAST = 单次攻击。
- LivingShield：SHIELD_SLAM = 单次攻击。被动：RampartPower（格挡再生
  来源——用 DISMANTLE 类效果剥离，实战验证）。
- LouseProgenitor：POUNCE = 单次攻击。被动：CurlUpPower。
- MagiKnight：DAMPEN = 减益；PREP = 防御；MAGIC_BOMB 与 RAM = 单次攻击。
- Mawler：RIP_AND_TEAR = 单次；ROAR = 减益；CLAW = 多段 ×2。
- MechaKnight：CHARGE = 单次；FLAMETHROWER = 状态 ×4；HEAVY_CLEAVE =
  单次。被动：ArtifactPower。
- MysteriousKnight：被动 StrengthPower + PlatingPower。
- Myte：TOXIC = 状态 ×2；BITE = 单次攻击。
- Nibbit：BUTT = 单次；HISS = 增益。
- Noisebot：NOISE = 状态 ×2。
- Osty：死灵束缚者的召唤伙伴（通过 Summon 出场；大量死灵卡牌指挥
  Osty——见 cards_zh.md）。
- Ovicopter：LAY_EGGS = 召唤；SMASH = 单次；NUTRITIONAL_PASTE = 增益。
- 女王 boss 系（实战）：施加 CHAINS_OF_BINDING_POWER + MINION_POWER
  工厂式召唤；格挡压制与 Frail 叠加可使格挡归零。
- 机器人工厂系（实战）：STOCK_POWER——每次死亡生成下一形态直至战斗结束。
- 仪式兽 boss（实战）：RINGING_POWER 使玩家手牌 can_play 翻为 false。

## 对局中读怪物

- state.combat.creatures[].intent 携带 id/damage/times/is_attack——与本表
  对照判断后续动作。
- 隐藏意图（NOTHING）稍后揭示——稳健打法应对。
- 睡眠/眩晕循环（BygoneEffigy、LagavulinMatriarch）：苏醒后是爆发窗口。
- ArtifactPower 层数：神器未剥离前施加减益是浪费。
- Doom 阈值击杀（死灵对局）绕过常规伤害竞速。
