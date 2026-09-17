# 怪物

敌人参考（确定性机制，仅含精确数值）。来源：反编译源码
`MegaCrit.Sts2.Core.Models.Monsters` + `MegaCrit.Sts2.Core.Models.Encounters`
+ 章节池 `MegaCrit.Sts2.Core.Models.Acts`（/tmp/sts2-decomp）；被动效果经
`MegaCrit.Sts2.Core.Models.Powers` 核实。括号内为简中译名（已核实者标注；
未核实官方译名的条目保留英文内部名，不臆造）。

格式：`- 名称（id, 出处）：招式 — MOVE_ID = 确定性效果；被动及精确数值。`

伤害/格挡为基础值（无进阶）。存在进阶档位时记为 `(A: n)`——`ToughEnemies` 提升 HP/格挡，`DeadlyEnemies` 提升伤害。HP 记为 基础值（A 区间）。

章节遭遇池（`GenerateAllEncounters`）：
- 第一章 蔓生之地 Overgrowth：Boss VantomBoss、CeremonialBeastBoss、TheKinBoss；精英 BygoneEffigyElite、ByrdonisElite、PhrogParasiteElite。
- 第二章 虫巢 Hive：Boss TheInsatiableBoss、KnowledgeDemonBoss、KaiserCrabBoss；精英 DecimillipedeElite、EntomancerElite、InfestedPrismsElite。

## 第一章 — 蔓生之地

- LeafSlimeM（树叶史莱姆（中）, Act1 Slimes/SlitheringStrangler/Flyconid 遭遇; 32–35 HP）：CLUMP_SHOT = 单次攻击 8 (A:9)；STICKY_SHOT = 状态牌 ×2（向弃牌堆注入状态牌）。
- LeafSlimeS（树叶史莱姆（小）, Act1 Slimes; 11–15 HP）：TACKLE_MOVE = 单次攻击 3 (A:4)；GOOP_MOVE = 状态牌 ×1。
- TwigSlimeM（TwigSlimeM, Act1 Slimes/SlitheringStrangler; 26–28 HP）：POKEY_POUNCE_MOVE = 单次攻击 11 (A:12)；STICKY_SHOT_MOVE = 状态牌 ×1。
- TwigSlimeS（TwigSlimeS, Act1 Slimes; 7–11 HP）：TACKLE_MOVE = 单次攻击 4 (A:5)。
- ShrinkerBeetle（缩小甲虫, Act1 ShrinkerBeetleWeak / OvergrowthCrawlers; 38–40 HP）：SHRINKER_MOVE = 减益——对玩家施加 ShrinkPower −1（负数=无限持续）：甲虫存活期间玩家攻击伤害 ×0.7（−30%）；CHOMP_MOVE = 单次攻击 7 (A:8)；STOMP_MOVE = 单次攻击 13 (A:14)。循环 SHRINKER → CHOMP → STOMP → CHOMP…
- Inklet（墨宝, Act1 InkletsNormal; 11–17 HP）：JAB_MOVE = 单次攻击 3 (A:4)；WHIRLWIND_MOVE = 多段攻击 2 (A:3) ×3；PIERCING_GAZE_MOVE = 单次攻击 10 (A:11)。被动 SlipperyPower：充能未耗尽时每次受击 HP 损失上限 1；每次未格挡命中 ≥1 消耗 1 层充能。
- Mawler（蛮兽, Act1 MawlerNormal; 72 HP）：RIP_AND_TEAR_MOVE = 单次攻击 14 (A:16)；ROAR_MOVE = 减益——对玩家施加 3 Vulnerable；CLAW_MOVE = 多段攻击 4 (A:5) ×2。
- Nibbit（小啃兽, Act1 NibbitsNormal/Weak; 42–46 HP）：BUTT_MOVE = 单次攻击 12 (A:13)；SLICE_MOVE = 单次攻击 6 (A:7) + 自身 5 格挡 (A:6)；HISS_MOVE = 增益 自身 +2 力量 (A:3)。循环 BUTT → SLICE → HISS → BUTT…
- SnappingJaxfruit（SnappingJaxfruit, Act1 SnappingJaxfruitNormal（与 Flyconid 同场）; 31–33 HP）：ENERGY_ORB_MOVE = 单次攻击 3 (A:4) + 自身 +2 力量；每回合重复。
- Flyconid（飞蝇菌子, Act1 FlyconidNormal / SnappingJaxfruitNormal; 47–49 HP）：VULNERABLE_SPORES_MOVE = 减益——2 Vulnerable；FRAIL_SPORES_MOVE = 单次攻击 8 (A:9) + 2 Frail；SMASH_MOVE = 单次攻击 11 (A:12)。
- FuzzyWurmCrawler（毛绒伏地虫, Act1 FuzzyWurmCrawlerWeak / OvergrowthCrawlers; 55–57 HP）：FIRST_ACID_GOOP = 单次攻击 4 (A:6)；ACID_GOOP = 单次攻击 4 (A:6)；INHALE = 增益 +7 力量。循环：酸液 → 吸气 → 酸液…
- Fogmog（雾菇, Act1 FogmogNormal; 74 HP）：ILLUSION_MOVE = 召唤 1 只 EyeWithTeeth；SWIPE_MOVE = 单次攻击 8 (A:9) + 自身 +1 力量；HEADBUTT_MOVE = 单次攻击 14 (A:16)。首次挥击后 40% SWIPE_RANDOM / 60% HEADBUTT 分支。击杀雾菇可阻止继续召唤。
- EyeWithTeeth（EyeWithTeeth, 由雾菇召唤; 6 HP）：DISTRACT_MOVE = 向每个目标弃牌堆加入 3 张 Dazed；重复。被动 IllusionPower 1（附带 MinionPower）：死亡时不退场——排队 REVIVE_MOVE（治疗意图）并回复至满最大 HP，复活期间不可被选中，随后恢复招式循环。幻象死亡后保留增益。
- Tunneler（Tunneler, Act2 TunnelerWeak/Normal; 87 HP）：BITE_MOVE = 单次攻击 13 (A:15)；BURROW_MOVE = 增益+防御——BurrowedPower 1 + 32 格挡 (A:37)，进入隐藏；BELOW_MOVE = 隐藏单次攻击 23 (A:26)，潜地期间自循环；DIZZY_MOVE = 眩晕苏醒（图鉴不显示）。BurrowedPower 的 AfterBlockBroken：其格挡被打破时被眩晕（DIZZY → 之后 BITE）并移除 BurrowedPower（AfterRemoved 清空全部剩余格挡）。打碎其格挡即可取消潜地攻击。
- 红宝石劫掠者系（RubyRaidersNormal; Act1）：AssassinRubyRaider KILLSHOT_MOVE = 单次 10 (A:11)，18–23 HP；AxeRubyRaider SWING_1/SWING_2 = 单次 5 (A:6) + 自身 5 格挡 (A:6)，BIG_SWING = 单次 12 (A:13)，20–22 HP；BruteRubyRaider BEAT_MOVE = 单次 7 (A:8)，ROAR_MOVE = 自身 +3 力量，30–33 HP；CrossbowRubyRaider FIRE_MOVE = 单次 14 (A:16)，RELOAD_MOVE = 防御，18–21 HP；TrackerRubyRaider TRACK_MOVE = 减益——2 Frail，HOUNDS_MOVE = 多段 1 (A:1) ×8 (A:9)，21–25 HP。
- CubexConstruct（立柱构造体, Act1 CubexConstructNormal; 65 HP）：CHARGE_UP_MOVE = 增益 ArtifactPower 1；REPEATER_BLAST_MOVE = 单次攻击 7 (A:8) + 自身 +2 力量（循环中连续两次）；EXPEL_MOVE = 多段攻击 5 (A:6) ×2 + 自身 +2 力量。循环：CHARGE → BLAST → BLAST → EXPEL → BLAST… ArtifactPower 1 吸收第一个施加的减益。
- PhrogParasite（异蛙寄生虫, Act1 PhrogParasiteElite; 61–64 HP）：INFECT_MOVE = 向每个目标弃牌堆加入 3 张 Infection（不可打出；回合结束在手则受 3 点无来源伤害）；LASH_MOVE = 多段攻击 4 (A:5) ×4。被动 InfestedPower 4（Single，出场时施加）：死亡时生成 4 只 Wriggler（StartStunned=true），且 InfestedPower 拥有者存活时战斗无法结束——召唤波延续战斗。
- Wriggler（扭动虫, Act1 PhrogParasiteElite 召唤波; 17–21 HP）：SPAWNED_MOVE = 眩晕（出场回合不动）；NASTY_BITE_MOVE = 单次攻击 6 (A:7)；WRIGGLE_MOVE = 增益 +2 力量。循环 NASTY_BITE ↔ WRIGGLE。
- SlitheringStrangler（蛇行扼杀者, Act1 SlitheringStranglerNormal（与史莱姆同场）; 53–55 HP）：CONSTRICT = 减益——对玩家施加 ConstrictPower 3：玩家每个回合结束时每层受到 3 点无来源伤害；施加者死亡时移除；THWACK = 单次攻击 7 (A:8) + 自身格挡；LASH = 单次攻击 12 (A:13)。
- VineShambler（藤蔓妖, Act1 VineShamblerNormal; 61 HP）：GRASPING_VINES_MOVE = 单次攻击 8 (A:9) + 对玩家 TangledPower 1；SWIPE_MOVE = 多段攻击 6 (A:7) ×2；CHOMP_MOVE = 单次攻击 16 (A:18)。TangledPower：你的攻击牌本回合获得 Entangled（+1 能量费用）；你的回合结束时移除。
- Exoskeleton（外骨骼虫, Act2 ExoskeletonsNormal/Weak; 24–28 HP）：SKITTER_MOVE = 多段 1 ×3 (A: ×4)；MANDIBLES_MOVE = 单次攻击 8 (A:9)；ENRAGE_MOVE = 增益 +2 力量。被动 HardToKillPower 9：拥有者每次受到的伤害实例上限 9（`ModifyDamageCap` 对拥有者返回 9）——单次命中超出部分直接作废。
- Byrdonis（多尼斯异鸟, Act1 ByrdonisElite; 81–84 HP min / 84–90 max）：PECK_MOVE = 多段攻击 3 (A:4) ×3；SWOOP_MOVE = 单次攻击 17 (A:19)；循环 SWOOP → PECK → SWOOP…。被动 TerritorialPower 1：其阵营回合结束时 +1 力量。
- BygoneEffigy（旧日雕像, Act1 BygoneEffigyElite; 127 HP）：SLEEP_MOVE（初始）睡眠 → WAKE_MOVE 增益（自身 +10 力量）→ SLASHES_MOVE = 单次攻击 13 (A:15)，SLASHES 自循环。被动 SlowPower：你本回合每打出一张牌，其受到你有源攻击的伤害 +10%（其阵营回合开始时计数清零）——多打牌后爆发。
- KinPriest（同族神官, Act1 TheKinBoss leaderSlot; 190 HP）：ORB_OF_FRAILTY_MOVE = 单次攻击 8 (A:9) + 1 Frail；ORB_OF_WEAKNESS_MOVE = 单次攻击 8 (A:9) + 1 Weak；BEAM_MOVE = 多段攻击 3 ×3；RITUAL_MOVE = 增益 自身 +2 力量 (A:3)。循环 Frail球 → Weak球 → BEAM → RITUAL。
- KinFollower（同族信徒, Act1 TheKinBoss slot1+slot2——神官两侧各 1; 58–59 HP）：QUICK_SLASH_MOVE = 单次攻击 5；BOOMERANG_MOVE = 多段攻击 2 ×2；POWER_DANCE_MOVE = 增益 自身 +2 力量 (A:3)。被动 MinionPower 1。循环 QUICK → BOOMERANG → POWER_DANCE。
- Vantom（墨影幻灵, Act1 VantomBoss; 173 HP）：INK_BLOT_MOVE = 单次攻击 7 (A:8)；INKY_LANCE_MOVE = 多段攻击 6 (A:7) ×2；DISMEMBER_MOVE = 单次攻击 26 (A:30)；PREPARE_MOVE = 增益 自身 +2 力量。循环 INK_BLOT → INKY_LANCE → DISMEMBER → PREPARE。被动 SlipperyPower：充能未耗尽时每次受击 HP 损失上限 1；每次未格挡命中 ≥1 消耗 1 层。层数 = 基础 8，进阶 ToughEnemies 时 9（decomp `SlipperyAmt`；多人按 ×玩家数缩放）—— 先用多段/芯片伤害泄层，层尽后再打大单发。run-25 A1 实测（2026-09-18, Seed TQLJKRW7W4）：水银沙漏回合开始伤害同样每 tick 消耗 1 层 Slippery（每击伤害≤1 规则对遗物伤害生效——沙漏全场充当被动泄层器）；玩家手牌中途出现 WOUND 状态牌（费用 −1、不可打出、Infection 类）——Vantom 会注入 Wound，档案招式表未标注注入来源（疑似 DISMEMBER/INK_BLOT 副作用）；本局充能经芯片+沙漏泄尽后 T5 击杀（痊愈药水+四连力量打击从 49 HP 收头）。
- CeremonialBeast（仪式兽, Act1 CeremonialBeastBoss; 252 HP）：STAMP_MOVE = 增益——自身 PlowPower 150 (A:160)；PLOW_MOVE = 单次攻击 18 (A:20) + 增益，自循环；STUN_MOVE = 眩晕苏醒；BEAST_CRY_MOVE = 减益——对全体玩家 RingingPower 1；STOMP_MOVE = 单次攻击 15 (A:17)；CRUSH_MOVE = 单次攻击 17 (A:19) + 自身 +3 力量 (A:4)。流程：STAMP → PLOW（循环）——PlowPower：拥有者受到未格挡伤害且当前 HP ≤ Plow 阈值时，移除全部力量（含临时）并被眩晕 → STUN → BEAST_CRY → STOMP → CRUSH → BEAST_CRY…。**Plow 阈值实测订正（run-23 A1, 2026-09-18）**：decomp 表值 基础150/A1 ToughEnemies 160，但实测行为是 **150**——重锤打到 153 未触发眩晕、Bash 打到 145 触发。跨线一击按 ≤150 规划，不要按 ≤160。RingingPower：你的所有卡牌获得 Ringing 词缀——持续期间每回合只能起手打出 1 张牌；你的回合结束时移除。

## 第二章 — 虫巢

- BowlbugEgg（盛碗虫卵, Act2 BowlbugsNormal; 21–22 HP）：BITE_MOVE = 单次攻击 7 (A:8) + 7 格挡 (A:8)。
- BowlbugNectar（盛碗虫（蜜）, Act2 BowlbugsNormal; 35–38 HP）：THRASH_MOVE = 单次攻击 3；BUFF_MOVE = 自身 +15 力量 (A:16)；THRASH2_MOVE = 单次攻击 3。循环 THRASH → BUFF → THRASH2（自循环）。
- BowlbugRock（盛碗虫（石）, Act2 BowlbugsNormal / SlumberingBeetleNormal; 45–48 HP）：HEADBUTT_MOVE = 单次攻击 15 (A:16)；DIZZY_MOVE = 眩晕苏醒。被动 ImbalancedPower 1：其攻击被完全格挡时进入失衡——下一次 HEADBUTT 后自我眩晕（DIZZY）。完全格挡头槌即可逼出眩晕。
- BowlbugSilk（盛碗虫（丝）, Act2 BowlbugsNormal / SlumberingBeetleNormal; 40–43 HP）：THRASH_MOVE = 多段攻击 4 (A:5) ×2；TOXIC_SPIT_MOVE = 减益——1 Weak。
- Myte（异螨, Act2 MytesNormal; 61–67 HP）：TOXIC_MOVE = 状态牌 ×2（注入毒性状态牌）；BITE_MOVE = 单次攻击 13 (A:15)；SUCK_MOVE = 单次攻击 4 (A:6) + 自身 +2 力量 (A:3)。循环 TOXIC → BITE → SUCK。
- Chomper（啃咬机, Act2 ChompersNormal; 60–64 HP）：CLAMP_MOVE = 多段攻击 ×2；SCREECH_MOVE = 状态牌 ×3。出场被动 ArtifactPower 2。
- HunterKiller（HunterKiller, Act2 HunterKillerNormal; 121 HP）：TENDERIZING_GOOP_MOVE = 减益 TenderPower 1；BITE_MOVE = 单次攻击 17 (A:19)；PUNCTURE_MOVE = 多段攻击 7 (A:8) ×3。
- LouseProgenitor（LouseProgenitor, Act2 LouseProgenitorNormal; 134–136 HP）：WEB_CANNON_MOVE = 单次攻击 9 (A:10) + 2 Frail；POUNCE_MOVE = 单次攻击 14 (A:16)；CURL_AND_GROW_MOVE = 防御——CurlUpPower 14 (A:18) + 自身 +5 力量。CurlUpPower：你用卡牌攻击命中它后，获得等额格挡一次，随后该能力移除。
- Ovicopter（直飞产卵虫, Act2 OvicopterNormal（与 ToughEgg 同场）; 124–130 HP）：LAY_EGGS_MOVE = 召唤 ToughEgg（出生 MinionPower 1）；SMASH_MOVE = 单次攻击 16 (A:17)；TENDERIZER_MOVE = 单次攻击 7 (A:8) + 2 Vulnerable；NUTRITIONAL_PASTE_MOVE = 增益 自身 +3 力量 (A:4)。
- ToughEgg（ToughEgg, Act2 OvicopterNormal 召唤; 14–18 HP）：NIBBLE_MOVE = 单次攻击；HATCH_MOVE = 召唤（HatchPower 倒计时）。出场回合眩晕。
- SlumberingBeetle（SlumberingBeetle, Act2 SlumberingBeetleNormal（与 BowlbugRock/Silk 同场）; 86 HP）：SNORE_MOVE = 睡眠；ROLL_OUT_MOVE = 单次攻击 16 (A:18) + 自身 +2 力量。被动 PlatingPower 15 (A:18)、SlumberPower 3。
- SpinyToad（SpinyToad, Act2 SpinyToadNormal; 116–119 HP）：PROTRUDING_SPIKES_MOVE = 增益 荆棘 +5；SPIKE_EXPLOSION_MOVE = 单次攻击 23 (A:25) 后荆棘 −5；TONGUE_LASH_MOVE = 单次攻击 17 (A:19)。循环 尖刺 → 爆发 → 舌击。
- InfestedPrism（感染棱柱, Act2 InfestedPrismsElite; 161 HP）：JAB_MOVE = 单次攻击 15 (A:17)；RADIATE_MOVE = 单次攻击 11 (A:13) + 等额格挡（11/13）；WHIRLWIND_MOVE = 多段攻击 5 (A:6) ×3；PULSATE_MOVE = 单次攻击 8 (A:10) + 20 格挡 (A:22)。被动 VitalSparkPower 2 (A:3)：战斗开始时你的技能牌获得 Tainted；打出 Tainted 牌时对你施加 TaintedPower 2。run-22 A1 实测击杀（2026-09-18）：**纯攻击牌战术**——关键回合不打被 Tainted 的技能牌，攻击税不堆叠；不得不打技能牌挡伤时税明知支付（显示意图随每张 Tainted 技能牌打出而上涨，单回合多技能实测 15→19→23→27→31）。易伤/力量/爆炸/锻造/能量药水全部在此战打出；Bludgeon 留棱柱 1 HP 后能量药水+Uppercut 收头。战术 HP 代价：整战 66→21——防御回合必然要打被税的技能牌。**run-24 A1 实测（2026-09-18, Seed K5XNGH7NPR, state 名 感染棱柱）**：纯攻击牌战术再次确认可净杀——PULSATE 意图现场显示 `8; Buff; Defend` = 8 攻击 + 自身 20 格挡（A1 表值 22 未显示，现场显示基础 8/挡 20）；VitalSpark 层数经 `VITAL_SPARK_POWER:n` 可见且战中上涨（2→4）——每回合都要跟踪。本局击杀顺序：吃下 PULSATE 回合 → Dismantle+Strike 破掉 20 挡 → Feed 对剩余 HP 打出 Fatal（刻意为 Max HP 而杀，非竞速）。易伤按层数=剩余回合数如期过期；易伤消失后 Dismantle 按单击规划。
- Entomancer（蜂群术士, Act2 EntomancerElite; 145 HP）：PHEROMONE_SPIT_MOVE = 增益——PersonalHivePower 1（另有力量增益 1/2）；BEES_MOVE = 多段攻击 3 ×7 (A:8)；SPEAR_MOVE = 单次攻击 18 (A:20)。被动 PersonalHivePower 1：拥有者每次被有源攻击命中时，攻击者的抽牌堆随机位置加入 1 张 Dazed（每层 1 张；Osty 的攻击记在其主人头上）。**run-24 A1 实测（2026-09-18, Seed K5XNGH7NPR, state 名 蜂群术士）**：PHEROMONE_SPIT 确认 = PersonalHive 1→2 **且** +1 力量（次回合 compact state 两者同时可见）；蜂群意图显示基础+力量的每击值（Buff 后 3+1=4 ×7 = `intent=4×7`，Buff 前显示 `3×7`）。蜂群税实测：每打出一张有源攻击牌，抽牌堆加入的 Dazed 数随当前层数缩放（Hive:2 时多段攻击牌税极重）。本局死法：T4 蜂群 4×7=28 对 HP17/0挡/空药槽 致死，蜂群术士剩 4/145——**在 Buff 回合结束前击杀是胜利条件**；信息素之后蜂群阈值随力量继续上涨。**run-25 A1 实测（2026-09-18, Seed TQLJKRW7W4）— 复仇击杀**：能力药水在信息素 Buff 回合给出 Demon Form 并免费打出（本回合 0 费）——「Buff 免费窗上引擎」是该药水的最佳用法；同窗腐化重锤 48（蜂群术士 127→79）；OTP×放血双结算再打 38（79→41→24，含沙漏 tick）；终局 4 HP 时手牌仅剩 Defend+Dazed，无色药水→Volley（X 费按全额能量结算、3 段命中）收头。本局 49 HP 入场，T1 蜂群 3×7 被格挡药水完全吸收（药水 12+防御×2=10 → 22 vs 21）。
- 残杀千足虫节段（DecimillipedeSegmentBack/Front/Middle, Act2 DecimillipedeElite; 基础节段 40–46 HP）：WRITHE_MOVE = 多段攻击 5 (A:6) ×2；CONSTRICT_MOVE = 单次攻击 8 (A:9) + 1 Weak；BULK_MOVE = 单次攻击 6 (A:7) + 自身 +2 力量；REATTACH_MOVE = 治疗；DEAD_MOVE = 死亡状态。被动 ReattachPower 25：节段死亡而其他节段仍存活时进入 DEAD 状态（不可选中）；其回合结束时重新接合并回复 25。当其余节段全部死亡时，所有节段淡出彻底死亡——在同一窗口清掉全部节段，否则它们会复活。run-20 A1 实测（2026-09-18）：同窗清场=胜利条件确认——恶魔之焰+卡戎之灰一回合把三段打到 0/3/1，随后打击杀掉一个低血节段、坚毅触发的灰烬杀掉另一个、第三段仍在 0 HP 时战斗立即结束，REATTACH 复活均未及结算。0 HP 时的复活表现为 Heal 意图（类 Parafright）。run-25 A1 实测（2026-09-18, Seed TQLJKRW7W4）— **零 AoE 同窗**：力量堆到 6（FightMe 层）后单体数学即可清场——放血对 21 血段精确 21、打击 12 对 4 血段，第三段已处 0；REATTACH 未触发。T3-T7 过程细节：低血段**留活**、其余段处 DEAD 等待时可避免双段回接回血；杀掉唯一存活段会让全部 DEAD 段在下个敌方回合走 Heal 意图回接（各 +25）——要么铺伤后同窗全倒，要么在其余段已 DEAD 时留一个存活段不动。0 HP DEAD 段不可选中——攻击不要指向它们（Iron Wave 类空转规则）。
- TheObscura（TheObscura, Act2 TheObscuraNormal; 123 HP）：ILLUSION_MOVE = 召唤 1 只 Parafright；PIERCING_GAZE_MOVE = 单次攻击 10 (A:11)；SAIL_MOVE（Wail）= 增益——全体队友 +3 力量；HARDENING_STRIKE_MOVE = 单次攻击 6 (A:7) + 自身 6 格挡 (A:7)。首次 ILLUSION 后在 凝视/哀嚎/硬化 间随机分支（不连续重复）。
- Parafright（Parafright, Act2 TheObscuraNormal 召唤; 21 HP）：SLAM_MOVE = 单次攻击 16 (A:17)；重复。被动 IllusionPower 1：死亡时经 REVIVE_MOVE 回复满血复活（同 EyeWithTeeth）。击杀 TheObscura 可阻止继续召唤。
- ThievingHopper（偷窃跳虫, Act2 ThievingHopperWeak; 79 HP）：THIEVERY_MOVE = 单次攻击 17 (A:19) + 经 SwipePower 偷走 1 张牌库卡（优先级：非 Imbued 的 Uncommon → Common/Rare/Event → Basic/Quest → Ancient/Imbued，来源为抽牌堆/弃牌堆）；NAB_MOVE = 单次攻击 14 (A:16)；HAT_TRICK_MOVE = 单次攻击 21 (A:23)；FLUTTER_MOVE = 增益 FlutterPower 5；ESCAPE_MOVE = 逃跑（到位后自循环）。循环：THIEVERY → FLUTTER → HAT_TRICK → NAB → ESCAPE。被动：EscapeArtistPower 5——逃跑倒计时，其回合结束递减；FlutterPower 5——受到的攻击伤害 ×0.5，每次未格挡攻击命中递减 1，归零时被眩晕并结束悬停。SwipePower：跳虫死亡时被偷卡牌作为战斗奖励回到你的牌库。
- TheInsatiable 无底之欲（TheInsatiable, Act2 TheInsatiableBoss; 321 HP）：LIQUIFY_GROUND_MOVE = 增益；THRASH_MOVE / THRASH_MOVE_2 = 多段攻击 8 (A:9) ×2；LUNGING_BITE_MOVE = 单次攻击 28 (A:31)；SALIVATE_MOVE = 增益 自身 +2 力量 (A:3)。循环：LIQUIFY → THRASH → SALIVATE → THRASH_2 → LUNGING_BITE → THRASH… **击杀机制已解码（perplexity 2026-09-18；订正 run-16/20/22 档案）**：SANDPIT_POWER 是吞噬倒计时，**初始 4 层**，每个敌方阵营回合开始 -1；**归 0 时玩家被直接吞噬，无视 HP/格挡**——run-16/20/22 A1 的「足够格挡下仍然致死」即倒计时归 0，**并非意图显示 bug**。Boss 开战注入 **6 张 FranticEscape**；**打出一张沙坑 Amount +1**（该牌自身费用永久 +1）——留到计数 1–2 紧急延时。旧档案「FranticEscape 绝不可打」规则对本 Boss **完全错误**，本身就是死因之一。战斗计划：**输出竞速**——在倒计时耗尽前打掉 321 HP；格挡只能应付 THRASH/LUNGING_BITE，拦不住吞噬；每回合跟踪沙坑层数（compact state 打印 `SANDPIT_POWER:amount`）。招式意图按表：A1 THRASH 9×2、LUNGING_BITE 31、SALIVATE +3 力。**run-26 A1 实测（2026-09-18, Seed H5LX9GRRAR）**：开战 SANDPIT_POWER:4 经 compact `POWER:amount` 可见；FranticEscape 在计数器 3–5 时打出 5 次 —— 倒计时全程 4–5，吞噬从未触发。死因不是吞噬：HP 5 面对 THRASH 11×2（A1 实测意图，力量叠加 8+3），手牌最大挡 9（Defend 5 + 波纹水盆无攻击回合 +4）。玩家 T6 阵亡时 Boss 剩 172/321 —— run-16/20/22 杀手类确定为「伤害竞速 + HP 缓冲」问题而非沙坑悬案；解码：进场有效 HP >60 且竞速回合手上有挡线，引擎 DPS ~40-60/回合需要 FE 延时之外再买 3-4 回合缓冲。
- KaiserCrab 皇蟹（KaiserCrab, Act2 KaiserCrabBoss；双爪遭遇）：槽位 crusher + rocket，无本体目标。遭遇生成 Crusher（crusher 槽）+ Rocket（rocket 槽）。玩家侧被动 SurroundedPower；每只爪各带 BackAttackLeftPower/BackAttackRightPower（朝向标记）+ CrabRagePower。
  - Crusher 碾碎爪（Crusher；209 HP）：循环 THRASH_MOVE = 单次攻击 12 (A:14) → ENLARGING_STRIKE_MOVE = 单次攻击 4 → BUG_STING_MOVE = 多段攻击 6 (A:7) ×2 + 2 Weak + 2 Frail → ADAPT_MOVE = 增益 自身 +2 力量 (A:3) → GUARDED_STRIKE_MOVE = 单次攻击 12 (A:14) + 自身 18 格挡 → 回 THRASH。
  - Rocket 火箭（Rocket；199 HP）：循环 TARGETING_RETICLE_MOVE = 单次攻击 3 (A:4) → PRECISION_BEAM_MOVE = 单次攻击 18 (A:20) → CHARGE_UP_MOVE = 增益 自身 +2 力量 (A:3) → LASER_MOVE = 单次攻击 31 (A:35) → RECHARGE_MOVE = 睡眠 → 回 TARGETING_RETICLE。
  - 实战记录（2026-09-17 对局）：意图数值已含夹击 ×1.5（侧击爪的 THRASH 12 显示为 18）。有效击杀顺序：先集火 Rocket（LASER 是致死尖峰）；其死亡触发存活爪的 CrabRagePower——Crusher 获得 +6 力量 + 99 无来源格挡——随后 1-2 回合内拆掉 99 格挡，同时用格挡应对力量强化后的循环。**run-23 A1 实测（2026-09-18, Seed 0Z4QQX6ERS, state 名 碾碎爪/火箭）**：火箭优先竞速再次确认——火药水+Bash易伤+重锤 T1 把火箭 199→103；LASER（显示 33）经心脏铁镀层（PLATING_POWER 可见）+ 格挡后仅 18 入身扛过；火箭死于 RECHARGE 睡眠回合的免费攻击；CrabRage 实弹触发（碾碎爪格挡 18→117 = 18+99，STR:8 可见）且在回合结束自然过期、无需全拆；碾碎爪 209 T9 击杀。compact-state 的 `POWER:amount`（SURROUNDED:1、CRAB_RAGE:1、力量层数）每回合必读——机制优先路径。
- KnowledgeDemon 知识恶魔（KnowledgeDemon, Act2 KnowledgeDemonBoss; 379 HP）：招式循环 CURSE_OF_KNOWLEDGE_MOVE（减益）→ SLAP_MOVE → KNOWLEDGE_OVERWHELMING_MOVE → PONDER_MOVE → 分支（诅咒计数 <3 回 Curse，否则 Slap）。
  - CURSE_OF_KNOWLEDGE_MOVE：玩家从 2 张 IChoosable 诅咒牌中选 1——按计数轮换：0 = Disintegration | MindRot；1 = Disintegration | Sloth；2 = Disintegration | WasteAway。所选牌不进牌库；OnChosen 立即施加对应能力：Disintegration → DisintegrationPower N（按计数 6/7/8——每个己方回合结束受 N 点无来源伤害）；MindRot → MindRotPower 1（每回合抽牌 −1）；Sloth → SlothPower 3（每回合最多打出 3 张牌）；WasteAway → WasteAwayPower 1（最大能量 −1）。每次 Curse 后计数 +1。
  - SLAP_MOVE = 单次攻击 17 (A:18)。
  - KNOWLEDGE_OVERWHELMING_MOVE = 多段攻击 8 (A:9) ×3。
  - PONDER_MOVE = 单次攻击 11 (A:13) + 回复 30 × 玩家数 + 自身 +2 力量 (A:3)。

## 其他章节 — 已提取 Boss（确定性数值）

- Queen（Queen, Act3 QueenBoss; 400 HP）：PUPPET_STRINGS_MOVE = 卡牌减益——ChainsOfBindingPower 3；YOU_ARE_MINE_MOVE = 减益——99 Frail/Weak/Vulnerable；BURN_BRIGHT_FOR_ME_MOVE = 增益；OFF_WITH_YOUR_HEAD_MOVE = 多段攻击 3 (A:4) ×5；EXECUTION_MOVE = 单次攻击 15 (A:18)；ENRAGE_MOVE = 增益 +2 力量。ChainsOfBindingPower 行为（实机观察）：玩家身上有 chains 时，部分出牌会消耗卡牌且零效果（静默无效）——该模式并非严格的每回合出牌次数上限（同一回合观察到全额生效与部分沉默并存）。火炬头聚合体是独立战斗目标——它存活时战斗不会结束。
- TestSubject（TestSubject, Act3 TestSubjectBoss; 多阶段）：BITE 20 (A:22)、SKULL_BASH 14 (A:16)、MULTI_CLAW 10 ×3、PHASE3_LACERATE 10 (A:11) ×3、BIG_POUNCE 45、BURNING_GROWL = 状态灼烧 3 (A:5) + 自身 +2 力量 (A:3)；经 RESPAWN_MOVE 重生/回复阶段。被动 AdaptablePower、EnragePower 2 (A:3)、PainfulStabsPower、NemesisPower。战斗要点：EnragePower 在任何人打出技能牌时都会触发——技能牌密集的牌组会快速喂养该 Boss；优先使用攻击/能力牌。AdaptablePower 使其死亡时经重生/回复阶段复活。**run-23 A1 实测（2026-09-18, Seed 0Z4QQX6ERS, state 名 实验体 #C10）**：阶段一刷新 100 HP + ADAPTABLE_POWER:1 + ENRAGE_POWER:2 可见；全攻击包（Hemokinesis/Peck/Strike 线，零技能牌打出）让 Enrage 阶段一全程稳在 :2（单回合 97→53）；重锤一击带走阶段二残血（Boss 翻为 `Heal;Buff` 0 HP 状态）；end_turn 经 win-condition force path → 战斗奖励 → THE_ARCHITECT EA 结局 floor 48。教训：Enrage 战中惯用的 SecondWind/FeelNoPain 技能包就是 Boss 的燃料——反转为攻击/能力优先，技能仅在生存被逼时打出。
- SoulNexus（SoulNexus, Act3 SoulNexusElite; 234 HP）：SOUL_BURN_MOVE = 单次攻击 29 (A:31)；MAELSTROM_MOVE = 多段攻击 6 (A:7) ×4；DRAIN_LIFE_MOVE = 单次攻击 18 (A:19) + 强减益——对玩家施加 2 Vulnerable + 2 Weak。战斗后期观察到意图 32 = 力量强化后的单次重击。**run-23 A1 实测（2026-09-18）**：无特殊机制——直伤型精英；DRAIN_LIFE 减益实测确认（玩家 VULNERABLE_POWER:2 + WEAK_POWER:2 可见）；Ashen Strike（消耗堆成长）+ Headbutt 取回循环 + 攻击包 5 回合打穿 234→0；后期意图涨到 43（力量强化单发）——在其回合前击杀或用 Fortifier 类硬挡。
- OwlMagistrate 猫头鹰法官（OwlMagistrate, Act3 OwlMagistrateElite 并有 Act3 普通怪变体; 231 HP）：循环 MAGISTRATE_SCRUTINY = 单次 16 (A:17) → PECK_ASSAULT = 多段 4 ×6 → JUDICIAL_FLIGHT = 增益——自身 SoarPower 1 → VERDICT = 单次 33 (A:36) + 4 Vulnerable + 移除自身 SoarPower。SoarPower：存续期间持有者受到的有源攻击伤害 ×0.5（在其 VERDICT 回合 Soar 脱落时集火）。compact 状态显示中文名 猫头鹰法官。
- 三骑士精英（Act3 FlailKnightsElite 遭遇；FlailKnight 101 HP / SpectralKnight 93 HP / MagiKnight 82 HP）：
  - FlailKnight 连枷骑士：WAR_CHANT = 增益 自身 +3 力量 → FLAIL_MOVE = 多段 9 (A:10) ×2 → RAM_MOVE = 单次 15 (A:17)。
  - SpectralKnight 幽灵骑士：HEX = 减益 HexPower 2 → SOUL_SLASH = 单次 15 (A:17) → SOUL_FLAME = 多段 3 (A:4) ×3。HexPower：玩家全部卡牌（含之后获得的）附加 Hexed → 施加者存活期间获得虚无；施加者死亡时移除——击杀幽灵骑士即可解除。
  - MagiKnight 魔法骑士：POWER_SHIELD_MOVE = 单次 6 (A:7) + 自身 5 (A:9) 格挡 → DAMPEN_MOVE = 减益 DampenPower（见 powers_zh.md）→ PREP_MOVE = 自身格挡 5 (A:9) → MAGIC_BOMB = 单次 35 (A:40) → RAM_MOVE = 单次 10 (A:11)。
- LostThing 失落之物（Act3 与 ForgottenThing 组队; 93 HP）：被动 PossessStrengthPower 1——战斗中跟踪
  玩家力量值的负向变化（窃取）；持有者死亡时玩家等量返还。起手观察：Debuff;Buff 后进入攻击循环（见 6×2）。
- ForgottenThing 遗忘之物（Act3 与 LostThing 组队; 106 HP）：被动 PossessSpeedPower 1——对敏捷同套
  窃取/返还机制。起手：Debuff;Defend;Buff 后单次 15。
- TorchHeadAggregate 火炬头聚合体（女王 Boss 随从，Act3 Glory; 199 HP）：MinionPower + 力量成长
  （观察 +2/回合）；意图区间 18 → 12×3 → 16×3 → 24（多段攻击循环）。独立战斗目标——存活时女王战不会结束。
- DevotedSculptor（DevotedSculptor, Act3 精英 + Act3 普通怪变体（floor37 观察）; 162 HP）：FORBIDDEN_INCANTATION_MOVE = 增益——RitualPower 9 → SAVAGE_MOVE = 单次 12 (A:15)；双状态循环。Ritual 每次增益循环抬升其力量——需速杀。
- SlimedBerserker（SlimedBerserker, Act3 SlimedBerserkerElite; 261 HP）：VOMIT_ICHOR_MOVE = 状态 10 → LEECHING_HUG_MOVE = 减益 玩家 3 Weak + 增益 自身 +3 力量 → SMOTHER_MOVE = 单次 30 (A:33) → FURIOUS_PUMMELING_MOVE = 多段 4 (A:5) ×4。
- LivingShield 活体盾（Act3 与高塔炮手组队; 55 HP）：被动 RAMPART_POWER 25——玩家阵营回合开始时，每名存活的 TurretOperator 系盟友（如高塔炮手）获得 25 格挡。必须先杀它，否则炮手格挡每回合回满。
- TowerGunner 高塔炮手（Act3 与活体盾组队; 41 HP）：出场自带 25 格挡；意图 3×5 多段（15）。活体盾存活期间，其格挡在玩家回合开始时刷新。
- FrogKnight 青蛙骑士（Act3，出现于 Unknown 房战斗; 191 HP）：被动 PlatingPower 15——回合 1 出场获得 15 格挡、其阵营回合末再获得 15 格挡，其阵营回合开始时（非回合 1）镀甲 −1 层；观察到的意图：单次 13+减益、多段 5×2、增益（+2 力量）、单次 21（力量加成后）、防御+增益。
- MechKnight 机甲骑士（Act3 MechKnightElite; 300 HP）：出场神器 3 层（每个可见减益施加被清零并消耗 1 层）；观察到的意图：单次 25 → 状态卡 4（向玩家手牌加入灼伤）→ 防御+增益（+5 力量 +15 格挡）→ 单次 40（力量加成后）。雷霆一击/猛击/嘲讽可烧神器层数——3 层烧完后易伤才能挂上。出生 HP 可变：观察到以 1/300 当前 HP 出生的场次——不保证满血。
- BattleFriendV1/V2/V3 战斗好伙伴（战痕假人事件陪练；单人第三章实测 75/150/300 HP 不缩放）：招式 NOTHING_MOVE——从不攻击；出场 BattlewornDummyTimeLimitPower 3（假人阵营回合末递减；到 1 时假人逃跑并置 RanOutOfTime → 事件无奖励）。纯输出竞速。
- ScrollOfBiting 咬人卷轴（ScrollOfBiting, Act3 ScrollOfBitingNormal; 30–39 HP）：出场被动 PaperCutsPower 2；CHOMP = 单次 14 (A:16)；CHEW = 多段 5 (A:6) ×2；MORE_TEETH = 增益 自身 +2 力量。PaperCutsPower：持有者的有源攻击造成未格挡伤害时，对玩家追加纸割伤害（见 powers_zh.md）。
- PunchConstruct 拳击构装体（PunchConstruct, Act3 PunchConstructsNormal; 55 HP）：出场 ArtifactPower 1；READY_MOVE = 自身 10 格挡 → STRONG_PUNCH_MOVE = 单次 14 (A:16) → FAST_PUNCH_MOVE = 多段 5 (A:6) ×N + 玩家 1 Frail。
- InfestedPrism 立柱构造体（InfestedPrism）：Act2 精英与 Act3 普通怪（观察到 65 HP 变体）均出现；VitalSpark/REPEATER 行为见 Act2 精英条目。
- Aeonglass（Aeonglass, Act3 AeonglassBoss; 512 HP）：EBB_MOVE = 单次 26 (A:32) + 33 格挡；EYE_LASERS_MOVE = 多段 11 (A:12) ×2；INCREASING_INTENSITY_MOVE = 状态 Wither 1 (A:2) + 力量成长；出场 ArtifactPower 3。
- WaterfallGiant（WaterfallGiant, Act4 WaterfallGiantBoss; 240 HP）：PRESSURIZE 增益 SteamEruption 15 (A:20) → STOMP 15 (A:16) → RAM 10 (A:11) → SIPHON 治疗 → PRESSURE_GUN 20 (A:23，每次 Pressure Up +5) → PRESSURE_UP 13 (A:14) → 回 STOMP；ABOUT_TO_BLOW 眩晕 → EXPLODE 处决。
- SoulFysh（SoulFysh, Act4 SoulFyshBoss; 211 HP）：BECKON 状态 ×2 → DE_GAS 单次 16 (A:17) → GAZE 单次 7 (A:8) → FADE Intangible 2 → SCREAM 单次 13 (A:15) + 3 Vulnerable → 循环。
- LagavulinMatriarch（LagavulinMatriarch, Act4 LagavulinMatriarchBoss; 222 HP）：SLEEP → SLASH 19 (A:21) → SLASH2 12 (A:14) + 格挡 → DISEMBOWEL 9 (A:10) ×2 → SOUL_SIPHON 减益（玩家 −2 力量/敏捷，自身 +2 力量）。被动 PlatingPower 12、AsleepPower 3。2026-09-17 A1 实测：作为 **Act 1 Boss** 出现（222 HP；epoch 内容——与 WaterfallGiant 同模式；以游戏为准，表内 Act4 标签不作数）。唤醒战术：沉睡期间用卡牌打出未格挡伤害 → 移除镀甲并将其击晕进 WakeUpMove——优于白送它睡过 2-3 个镀甲 12 回合。

## 能力速查（Powers 源码精确值）

- SlipperyPower：充能未耗尽时拥有者每次受击 HP 损失 ≤1；每次未格挡命中 ≥1 消耗 1 层；多人时层数 × 玩家数。
- TerritorialPower / HighVoltagePower：拥有者阵营回合结束时 +力量 = 层数。
- HardToKillPower 9：拥有者单个伤害实例上限 9（`ModifyDamageCap`）；单次命中超出部分作废。
- PersonalHivePower 1：拥有者被有源攻击命中 → 攻击者抽牌堆随机位置 +1 Dazed/层。
- InfestedPower 4：死亡时生成 4 只被眩晕的 Wriggler；存活时阻止战斗结束。
- IllusionPower：死亡时经 REVIVE_MOVE 回复满最大 HP；复活期间不可选中；保留增益；附带 MinionPower。
- ReattachPower 25：死亡节段不可选中；其他节段存活时回合结束接合并回复 25；其余全灭时全体彻底死亡。
- ImbalancedPower：攻击被完全格挡 → BowlbugRock 失衡 → 下次头槌后自我眩晕。
- SlowPower：你本回合每打一张牌，其受到的有源攻击伤害 +10%；其阵营回合开始清零。
- ConstrictPower N：拥有者每个自身回合结束受 N 点无来源伤害；施加者死亡时移除。
- TangledPower N：你的攻击牌 +N 能量费用（Entangled）；你的回合结束时移除。
- ShrinkPower：拥有者攻击伤害 ×(100−30)/100；层数每个拥有者回合 −1，层数 <0 时无限。
- EscapeArtistPower 5：偷窃跳虫逃跑倒计时，其回合结束 −1。
- FlutterPower 5：受到的攻击伤害 ×0.5；无来源伤害不递减；归零时跳虫被眩晕。
- SwipePower：持有被偷的牌库卡；拥有者死亡时卡牌回到受害者牌库 + 额外卡牌奖励。
- RingingPower：你的所有卡牌获得 Ringing——每回合只能起手打出第一张；你的回合结束移除。
- PlowPower 150/160：拥有者受未格挡伤害且当前 HP ≤ 阈值时，清空全部力量 + 眩晕 → 进入 BEAST_CRY 阶段。
- DemisePower 9：拥有者每个自身回合结束受 9 点不可格挡伤害（消亡粉末药水）。
- CurlUpPower N：被玩家卡牌攻击命中后获得 N 格挡一次，随后移除。
- RavenousPower：队友死亡时自身获得力量 + 自我眩晕（噬尸蛞蝓吞噬）。
- StockPower：死亡时生成 StockAmount−1 的 Axebot（机器人装配链；充能未尽时阻止战斗结束）。出生 HP 可变：观察到链环以 1/x 当前 HP 出生（一次遭遇上限 77→72→71）——与机甲骑士同类，不保证满血。
- GalvanicPower N：你的能力牌获得 Galvanized；打出时对你造成 N 点伤害。
- VitalSparkPower N：你的技能牌获得 Tainted；打出时对你施加 TaintedPower N。
- SuckPower N：拥有者有源攻击对任意目标造成未格挡伤害后，每次命中实例 +N 力量。
- SurprisePower：死亡时生成 SneakyGremlin + FatGremlin 并移交被偷金币（地精佣兵）。
- 授予负荆棘的招式（如 SpinyToad 爆发 −5）会移除其先前授予的荆棘。

- 产卵虫 直飞产卵虫（Ovicopter，Act2 OvicopterNormal 族，实测 128 HP）：SUMMON 召唤 3 枚结实的卵（各自 HATCH_POWER 倒计时）；孵化 → 幼虫；循环 召唤 → 单击 ~10+干扰 → 召唤（力量随战斗叠加，实测意图 10→28→33）。2026-09-17 实战笔记：应母虫集火；清波消耗战输给其力量叠层。EN: Ovicopter.
- 幼虫（产卵虫孵化体；实测 19–21 HP）：MINION_POWER；NIBBLE 级单击基础 4，每轮循环叠力（实测 4→6）。死亡不结束战斗。EN: Larvae.
- 实测中文名折叠：ThievingHopper 偷窃草蜢；HauntedShip 幽灵船；BowlbugRock 盛碗虫（石）；BowlbugNectar 盛碗虫（蜜）；GremlinMerc 地精佣兵；TerrorEel 族四鳗组 花园幽灵鳗（Act1 精英 (7,1) 实测：27–31 HP ×4，SKITTISH_POWER，意图 1×3/5/7/Buff）；Act1 淤泥旋螺（实测 39 HP，Debuff+5 意图循环，类未识别 — 仅现场观察）；WaterfallGiant 瀑布巨兽 — 2026-09-17 实测作为 **Act 1 Boss** 出现（epoch 内容；上表条目标注 Act4 — 以游戏为准）。Act1 Boss 灵魂异鱼 — 2026-09-17 run-12 实测：211 HP，意图在 2(类buff)/11/Debuff 侧循环，存在 INTANGIBLE_POWER 回合（攻击减为每击 1-2 点），召唤阶段无明显产物；与表内 Boss（Vantom/CeremonialBeast/TheKin）的对应关系未确认 — 仅按实测名单记录。地精佣兵 GremlinMerc 实测（run-12）：THIEVERY_POWER 每回合偷取 20 金币；死亡时 SurprisePower 生成 卑鄙地精 SneakyGremlin 11 HP + 胖地精 FatGremlin 17 HP（HEIST_POWER，Escape 意图 — 1 HP 时逃脱，无奖励）。死后假人模式：999999999/999999999 HP + Stun 意图，EXPLODE 处决 ~51（可用格挡硬吃；其后战斗结束）。run-16 实测（A1，2026-09-17）：瀑布巨兽再次作为 **Act 1 Boss** —— 假人 EXPLODE 在 A1 显示 **36**（A1 表值，非基础难度见过的 ~51）；骇鳗族精英 (14,0) 140 HP —— SHRIEK_POWER 在阈值未格挡伤害时自我眩晕，其 22 意图回合被完整吃掉，次回合击杀；残杀千足虫精英 (11,3) 节段 40/42/46 —— REATTACH 在 Heal 意图回合三次回血 25（0→25），逐段击杀被免费复活；同窗 AOE 始终未凑齐，战斗磨满 10 回合；同会话蜂群术士 145 被击杀（Personal Hive 的 Dazed 污染才是该战真正的消耗税）。run-17 实测（A1 2026-09-17）：MinionPower 随主结算再次确认 — 产卵虫母体死亡瞬间 3 幼虫同步消亡（与雾菇幻眼同规则，战斗立即结束）；结实的卵孵化→幼虫 19–21 HP 与档案一致；猎人杀手 TENDERIZING_GOOP 的 TenderPower 挂在玩家身上后，后续技能牌打出似反哺玩家力量+敏捷且会在回合中吞掉力量（Uppercut 斩杀算式 26→24 实测），机制未解仅记实测；无厌沙虫 SANDPIT_POWER 会向玩家牌库注入 FranticEscape 陷阱牌（打出使沙坑 Amount+1 且该牌费用永久+1；run-17 笔记称「绝不可打」——**错误，2026-09-18 已订正**：留到沙坑计数 1–2 作延时用，见 TheInsatiable 条目）；Vantom A1 泄层实测 8 层充能（基础 8），每层未格挡命中 −1、每击 HP 损失≤1，泄尽后 Bludgeon+ 满伤结算。
run-26 实测折叠（A1, 2026-09-18, Seed H5LX9GRRAR）：**仪式兽** 252 T5 击杀 —— Plow-150 眩晕由 Inferno 被动 tick 越线 152→140 未格挡自动触发；眩晕窗爆发 140→67；RINGING 未及施加（BEAST_CRY 前击杀）。**旧日雕像** 127 睡眠窗击杀；SlowPower 数学实测：2 张牌回合 Headbutt 12×1.2=14（显示按段下取整）。**地道虫** 87：burrow 挡（26 实测，Inferno chip 后）在**敌方回合**结算而非意图时预挂；AfterBlockBroken 碎挡眩晕再现。**偷窃草蜢** 79：ESCAPE_ARTIST_POWER:5 每其回合 -1 实测；SWIPE_POWER:1 持有偷走的牌；击杀后归还 + LuckyFysh 静默入库 +15；FlutterPower 减半实测（攻击 ×0.5，未格挡命中递减，归 0 眩晕）。**感染棱柱** 161：VITAL_SPARK_POWER 战中 2→4 上涨；每打出一张 Skill 对玩家施加 TAINTED_POWER（实测 TAINTED:8 → 同回合意图 +8，敌方回合结束清除 —— 必须攻击/能力牌 doctrine）。**产卵虫** 124：虫卵孵化为幼虫 19/21/21（HATCH_POWER:1→MINION_POWER:1）；Inferno 12-tick 单发清掉 5/2/4 HP 新卵；母体优先击杀全场清。**残杀千足虫** 42/44/46：留活规则（1 HP 段存活）令 REATTACH 休眠；Inferno tick T5 玩家回合开场三段齐杀 —— 无 AoE 爆发达成同窗清场，复活循环从未触发。
 run-18 实测（A1 2026-09-17）：Obscura 系召唤师 胧光怪 出现在 Act2 (7,1)，123 HP，召唤 Parafright 寄生惧魔（ILLUSION_POWER+MINION_POWER，21 HP，SLAM 意图 16 A1）——击杀主体即清场规则实测确认（主体 8 HP 被霹雳斩首时召唤物仍在 0 HP 排队复活，战斗立即结束）；Parafright 复活循环实测确认（0 HP → Heal 意图 → 下回合满血 21，循环至主体死亡）；熟睡甲虫 86 HP PlatingPower 15 唤醒模式实测确认——沉睡期未格挡伤害剥离 slumber 并击晕（同乐加维林族母）；盛碗虫 IMBALANCED_POWER 实测：石碗虫在自身攻击回合自眩（意图中途翻为 Stun）——攻击意图可被自身 power 浪费；TenderPower 扣税实测详见 powers.md 档案。
 run-19 实测（A1 2026-09-17）：皇蟹 Act2 Boss——碾碎爪 209 + 火箭 199，玩家 SURROUNDED_POWER；弹珠袋 T1 双爪易伤实测；火箭循环实测：TARGETING 3 → 光束 18 → CHARGE Buff → **LASER 33**（力量堆叠后 A1 区间确认）→ RECHARGE 睡眠（睡眠回合实测=免费输出窗）；火箭死亡触发存活爪 CrabRage（+6 力量+99 无视格挡挡值，档案值；本局未走到该步）。泥虫之祖实测（Act2 (13,4) 怪房，135 HP，state 名 虱虫之祖）：CURL_UP 首次卡牌攻击即触发（一次性 +14 挡后移除）；WEB 9+Frail → CURL_AND_GROW 防御+Buff（+5 力量）循环观测；T3 已见力量堆叠 POUNCE 19。外骨骼虫实测：HardToKill 9 上限确认——Bash+/上勾拳/重锤类命中一律结算 9，超出作废；节奏=多段小伤。地道虫实测（Act2 开荒 87 HP）：BURROW A1 给 32 挡+BurrowedPower，BELOW 显示 23；破挡眩晕复现（AfterBlockBroken → Stun 意图，BurrowedPower 剥除，溢出伤打本体）。ZH 实名折入 run-19：海洋混混（44 HP slug 类，RAVENOUS 同伴死亡自眩再验证）；钙化邪教徒/潮湿邪教徒（RITUAL_POWER 力量爬坡意图 9→12→16→21 实测）；泥虫之祖/虱虫之祖（LouseProgenitor 同族）；外骨骼虫（Exoskeleton）；地道虫（Tunneler）。
 run-27 实测折叠（A1, 2026-09-18, Seed N7RR2X8NWK）：**皇蟹** Act2 Boss ——完整循环再次实测：开战即玩家 SURROUNDED_POWER；火箭意图 TARGETING 3 → 光束 18 → CHARGE Buff → **LASER 33** → RECHARGE 睡眠 → 醒转 5；碾碎爪动作：18 → 6 → 9×2;Debuff（对玩家施加 Weak 2+Frail 2，每玩家回合衰减 2→1；实测 frail 挡值税约 -40%——IronWave 5→3、Defend 5→3、Shrug 8→6）→ 21;Defend（自挡 +18 实测）→ 力量堆叠后 12×2;Debuff。**CRAB_RAGE 火箭死亡 T8 实弹解码**：存活动力爪同帧获得**挡 99 + 力量 +6（2→8）**——档案「18→117」即此护甲；99 挡可被击碎（Bludgeon 59+Strike 23 一回合削至 17；挡在时 HP 无损）。LASER 33 在 HornCleat 14+BloodWall 16+Shrug+免费 IronWave 的 frail 后有效挡 ~21-29 下存活（吃 12）。**残杀千足虫** 44/40/46 三段同窗击杀（新方法）：**战斗中使用 Foul Potion**（对全体含玩家 12 伤——直接带走 12 HP 段，后续 Thunderclap AoE 清掉第二段；REATTACH/Heal 意图零结算；战斗结束时三段均显示 0）。Foul Potion 自伤同时实弹触发 Rupture。FestivePopper T1 9-AoE 本战预削实测（44→35 等）。**盛碗虫石/蜜对**：ImBALANCED 链式眩晕实弹——HEADBUTT 15 被全挡（Block Potion 12+Colossus 5=17）→ 意图翻 Stun；下一 Headbutt 回合再次全挡时二次链眩（单战两次）；蜜虫循环 THRASH 3 → BUFF +15 力量 → THRASH2 3+力 ——7 HP 处决于 Buff 落地前（击杀计时器拆除）。**异螨对** 67/62：TOXIC 状态牌实弹——1 费打出即消耗，**回合末仍在手则吃 5 无视格挡伤**（档案值确认；持有两张每回合税 ~10 HP，各花 1 费打出后清税）；循环 TOXIC 2 → BITE 13-15 → SUCK 4+2力 观测。**棘刺蟾蜍** 116：Buff 回合 THORNS_POWER:5 实测；SPIKE_EXPLOSION 意图 23 实测；爆发回合后荆棘递减归 0（其后自由攻击窗）；TONGUE_LASH 17。**外骨骼虫**三只：HardToKill 9 封顶再确认（BT 11→9×3 段）。**缩小甲虫** 39：DebuffStrong 落地 SHRINK_POWER:-1（攻击 ×0.7；Strike 6→4 实测）；循环 SHRINKER→CHOMP 7→STOMP 13→环 ——与既有条目吻合。**小啃兽 Nibbit** 45 单体：BUTT 12→SLICE 6+5挡→HISS +2力 循环实测——与既有条目吻合。**啃咬机对** 63/64（FestivePopper 预削至 54/55）：ArtifactPower 2 出生实测；Thunderclap 易伤被吸收（Artifact 2→1/目标，伤害部分照常落地）；**MoltenFist 对 0 层易伤目标施加 0 层且不消耗 Artifact**（0 层无 debuff 事件——价值浪费；先 Bash/Thunderclap 剥层再 MoltenFist）。FestivePopper 遗物 T1 全体 9 伤本局 3 场战斗实测确认。
