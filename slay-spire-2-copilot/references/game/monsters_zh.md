# 怪物

敌人参考：招式表与被动技能源自游戏源码提取（STS2-Agent extraction，
游戏版本约 v0.107-0.111）及 v0.107.1 实战记录；括号内为简中译名（来源：
slaythespire2.net/zh-CN/monster）。招式标签对应意图：SingleAttack /
MultiAttack(n) / Buff / Debuff / Defend / Stun / Sleep / Status(n) /
Summon / Heal / Hidden。

- Architect：NOTHING = 隐藏意图。
- AssassinRubyRaider（红宝石劫掠者系）：KILLSHOT = 单次攻击。
- Axebot（巨斧机器人）：ONE_TWO = 多段攻击 ×2；SHARPEN = 增益。被动：StockPower（死亡召唤下一机器人形态）。
- AxeRubyRaider（红宝石劫掠者系）：BIG_SWING = 单次攻击。
- BigDummy：NOTHING = 隐藏意图。
- BowlbugEgg：无已列招式。
- BowlbugNectar（盛碗虫系）：THRASH = 单次攻击；BUFF = 增益；THRASH2 = 单次攻击。
- BowlbugRock（盛碗虫（石））：HEADBUTT = 单次攻击；DIZZY = 眩晕。被动：ImbalancedPower。
- BowlbugSilk（盛碗虫（丝））：TRASH = 多段攻击 ×2。
- BruteRubyRaider（红宝石劫掠者系）：BEAT = 单次攻击。
- BygoneEffigy（旧日雕像，精英）：INITIAL_SLEEP/WAKE/SLEEP 循环 + SLASHES = 单次攻击。被动：SlowPower——空意图慢速回合与高额蓄力重击交替；重击回合前做好防御。
- Byrdonis（多尼斯异鸟）：PECK = 多段攻击；SWOOP = 单次攻击。被动：TerritorialPower。
- CalcifiedCultist（钙化邪教徒）/ DampCultist（潮湿邪教徒）/ DevotedSculptor（虔诚雕刻师）：INCANTATION / FORBIDDEN_INCANTATION = 增益。
- CeremonialBeast（仪式兽，boss）：STAMP = 增益；STUN = 眩晕；STOMP = 单次攻击。Boss 对玩家施加 RINGING（手牌出牌封锁——实战验证）。
- Chomper（啃咬机）：CLAMP = 多段攻击 ×2。被动：ArtifactPower。
- CorpseSlug（噬尸蛞蝓）：WHIP_SLAP = 多段；GLOMP = 单次；GOOP = 减益。被动：RavenousPower。
- Crusher（碾碎爪）：THRASH 与 ENLARGING_STRIKE = 单次攻击；ADAPT = 增益。被动：BackAttackLeftPower + CrabRagePower。
- CubexConstruct（立柱构造体）：CHARGE_UP = 增益；EXPEL_BLAST = 多段 ×2；SUBMERGE = 防御（获得格挡 + ArtifactPower）。
- DecimillipedeSegment（残杀千足虫节段）：WRITHE = 多段 ×2；REATTACH = 治疗（SetMaxAndCurrentHp + ReattachPower）——节段需谨慎处理；存在 back/front/middle 变体。
- DevotedSculptor（虔诚雕刻师）：FORBIDDEN_INCANTATION = 增益。
- Door：DOOR_SLAM = 多段。被动：DoorRevivalPower。
- Doormaker：WHAT_IS_IT = 眩晕；BEAM = 单次攻击。
- Entomancer（蜂群术士）：PHEROMONE_SPIT = 增益；BEES = 多段。被动：PersonalHivePower。
- Exoskeleton（外骨骼虫）：SKITTER = 多段；MANDIBLE = 单次；ENRAGE = 增益。被动：HardToKillPower。
- EyeWithTeeth：DISTRACT = 状态 ×3。被动：IllusionPower。
- Fabricator（组装师）：FABRICATE = 召唤；DISINTEGRATE = 单次攻击。
- FakeMerchantMonster：SWIPE = 单次；SPEW_COINS = 多段 ×8；ENRAGE = 增益。
- FatGremlin：SPAWNED = 眩晕。
- FlailKnight（连枷骑士）：WAR_CHANT = 增益；FLAIL = 多段 ×2；RAM = 单次攻击。
- Flyconid（飞蝇菌子）：VULNERABLE_SPORES = 减益；SMASH = 单次攻击。
- Fogmog（雾菇）：ILLUSION = 召唤；HEADBUTT = 单次攻击。
- FossilStalker（化石追踪者）：LATCH = 单次；LASH = 多段。被动：SuckPower。
- FrogKnight（青蛙骑士）：FOR_THE_QUEEN = 增益；STRIKE_DOWN_EVIL 与 BEETLE_CHARGE = 单次攻击。被动：PlatingPower。
- FuzzyWurmCrawler（毛绒伏地虫）：FIRST_ACID_GOOP / ACID_GOOP = 单次攻击。
- GasBomb：无已列招式。被动：MinionPower。
- GlobeHead（电球头）：THUNDER_STRIKE = 多段 ×3。被动：GalvanicPower（关联 GALVANIZED 减益）。
- GremlinMerc（地精佣兵）：GIMME = 多段。被动：SurprisePower。
- Guardbot（守护机器人）：GUARD = 防御。
- HauntedShip（幽灵船）：SWIPE = 单次；STOMP = 多段；HAUNT = 减益。
- HunterKiller（猎人杀手）：TENDERIZING_GOOP = 减益；BITE = 单次；PUNCTURE = 多段 ×3。
- InfestedPrism（感染棱柱）：JAB = 单次；WHIRLWIND = 多段。被动：VitalSparkPower。
- Inklet（墨宝）：JAB = 单次；WHIRLWIND = 多段 ×3；PIERCING_GAZE = 单次。被动：SlipperyPower（首次受击伤害大减，充能每受击消耗——实战验证）。
- KinFollower（同族信徒）：QUICK_SLASH = 单次；BOOMERANG = 多段 ×2；POWER_DANCE = 增益。被动：MinionPower。
- KinPriest（同族神官）：BEAM = 多段 ×3；RITUAL = 增益（力量成长——优先击杀）。
- KnowledgeDemon（知识恶魔）：CURSE_OF_KNOWLEDGE = 减益；SLAP = 单次；KNLEDGE_OVERWHELMING = 多段 ×3。
- LagavulinMatriarch（乐加维林族母）：SLEEP = 睡眠；SLASH = 单次；DISEMBOWEL = 多段。被动：PlatingPower + AsleepPower。
- LeafSlimeM（树叶史莱姆（中））：CLUMP_SHOT = 单次；STICKY_SHOT = 状态 ×2。
- LeafSlimeS（树叶史莱姆（小））：BUTT = 单次；GOOP = 状态 ×1。
- LivingFog（活雾）：SUPER_GAS_BLAST = 单次攻击。
- LivingShield（活体盾）：SHIELD_SLAM = 单次攻击。被动：RampartPower（格挡再生来源——用 DISMANTLE 类效果剥离，实战验证）。
- LouseProgenitor（虱虫之祖）：POUNCE = 单次攻击。被动：CurlUpPower。
- MagiKnight（魔法骑士）：DAMPEN = 减益；PREP = 防御；MAGIC_BOMB 与 RAM = 单次攻击。
- Mawler（蛮兽）：RIP_AND_TEAR = 单次；ROAR = 减益；CLAW = 多段 ×2。
- MechaKnight（机甲骑士）：CHARGE = 单次；FLAMETHROWER = 状态 ×4；HEAVY_CLEAVE = 单次。被动：ArtifactPower。
- MysteriousKnight：被动 StrengthPower + PlatingPower。
- Myte（异螨）：TOXIC = 状态 ×2；BITE = 单次攻击。
- Nibbit（小啃兽）：BUTT = 单次；HISS = 增益。
- Osty（奥斯提）：Necrobinder 的召唤伙伴（通过 Summon 出场；大量死灵卡牌指挥 Osty——见 cards_zh.md）。
- Ovicopter（直飞产卵虫）：LAY_EGGS = 召唤；SMASH = 单次；NUTRITIONAL_PASTE = 增益。
- PhrogParasite（异蛙寄生虫，精英）：实战变体 INFESTED_POWER 死亡时生成 4 只约 17-21hp 小怪——AOE 留给召唤波。
- Queen（女王，boss）：施加 CHAINS_OF_BINDING_POWER + MINION_POWER 工厂式召唤；格挡压制与 Frail 叠加可使格挡归零。
- 机器人工厂系（实战）：STOCK_POWER——每次死亡生成下一形态直至战斗结束。

## 对局中读怪物

- state.combat.creatures[].intent 携带 id/damage/times/is_attack——与本表对照判断后续动作。
- 隐藏意图（NOTHING）稍后揭示——稳健打法应对。
- 睡眠/眩晕循环（BygoneEffigy、LagavulinMatriarch）：苏醒后是爆发窗口。
- ArtifactPower 层数：神器未剥离前施加减益是浪费。
- Doom 阈值击杀（死灵对局）绕过常规伤害竞速。
