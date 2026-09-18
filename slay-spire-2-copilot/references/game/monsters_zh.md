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
- Vantom（墨影幻灵, Act1 VantomBoss; 173 HP）：INK_BLOT_MOVE = 单次攻击 7 (A:8)；INKY_LANCE_MOVE = 多段攻击 6 (A:7) ×2；DISMEMBER_MOVE = 单次攻击 26 (A:30)；PREPARE_MOVE = 增益 自身 +2 力量。循环 INK_BLOT → INKY_LANCE → DISMEMBER → PREPARE。DISMEMBER_MOVE = 单次攻击 26 (A:30) 并注入 WOUND 状态牌（意图显示「26; 3」= 26 伤 + 3 张 Wound）。被动 SlipperyPower：充能未耗尽时每次受击 HP 损失上限 1；每次未格挡命中 ≥1 消耗 1 层——水银沙漏回合开始伤害同样每 tick 消耗 1 层（≤1 规则对遗物伤害生效）。层数 = 基础 8，进阶 ToughEnemies 时 9（decomp `SlipperyAmt`；多人按 ×玩家数缩放）—— 先用多段/芯片伤害泄层；最后一层耗尽当帧 SlipperyPower 从 state 消失，全额伤害窗同帧开启。WOUND = 费用 −1、不可打出、**无回合末 HP 税**——纯牌库堵塞物，非 Infection 级伤害。
- CeremonialBeast（仪式兽, Act1 CeremonialBeastBoss; 252 HP）：STAMP_MOVE = 增益——自身 PlowPower 150 (A:160)；PLOW_MOVE = 单次攻击 18 (A:20) + 增益，自循环；STUN_MOVE = 眩晕苏醒；BEAST_CRY_MOVE = 减益——对全体玩家 RingingPower 1；STOMP_MOVE = 单次攻击 15 (A:17)；CRUSH_MOVE = 单次攻击 17 (A:19) + 自身 +3 力量 (A:4)。流程：STAMP → PLOW（循环）——PlowPower：拥有者受到未格挡伤害且当前 HP ≤ Plow 阈值时，移除全部力量（含临时）并被眩晕 → STUN → BEAST_CRY → STOMP → CRUSH → BEAST_CRY…。**Plow 阈值订正**：decomp 表值 基础150/A1 ToughEnemies 160，但行为是 **150**——打到 153 未触发眩晕、打到 145 触发。跨线一击按 ≤150 规划，不要按 ≤160。被动 tick（如狱火）可未格挡跨线自动眩晕。RingingPower：你的所有卡牌获得 Ringing 词缀——持续期间每回合只能起手打出 1 张牌；你的回合结束时移除。

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
- InfestedPrism（感染棱柱, Act2 InfestedPrismsElite; 161 HP）：JAB_MOVE = 单次攻击 15 (A:17)；RADIATE_MOVE = 单次攻击 11 (A:13) + 等额格挡（11/13）；WHIRLWIND_MOVE = 多段攻击 5 (A:6) ×3；PULSATE_MOVE = 单次攻击 8 (A:10) + 20 格挡 (A:22)。被动 VitalSparkPower 2 (A:3)：战斗开始时你的技能牌获得 Tainted；打出 Tainted 牌时对你施加 TaintedPower 2。**纯攻击/能力牌教条**——关键回合不打被 Tainted 的技能牌，攻击税不堆叠（显示意图随每张 Tainted 技能牌打出而上涨，单回合多技能 15→19→23→27→31）。VitalSpark 层数经 `VITAL_SPARK_POWER:n` 可见且战中上涨（如 2→4）——每回合跟踪。PULSATE 意图显示 `8; Buff; Defend` = 8 攻击 + 自身 20 格挡（A1 表值挡 22；显示为基础 8 + 挡 20）——吃下 PULSATE 回合后破挡；施加于它的易伤按层数=剩余回合数如期过期。
- Entomancer（蜂群术士, Act2 EntomancerElite; 145 HP）：PHEROMONE_SPIT_MOVE = 增益——PersonalHivePower 1（另有力量增益 1/2）；BEES_MOVE = 多段攻击 3 ×7 (A:8)；SPEAR_MOVE = 单次攻击 18 (A:20)。被动 PersonalHivePower 1：拥有者每次被有源攻击命中时，攻击者的抽牌堆随机位置加入 1 张 Dazed（每层 1 张；Osty 的攻击记在其主人头上）。**PHEROMONE_SPIT 确认 = PersonalHive 1→2 **且** +1 力量（次回合 compact state 两者同时可见）；蜂群意图显示基础+力量的每击值（Buff 后 3+1=4 ×7 = `intent=4×7`，Buff 前显示 `3×7`）。蜂群税：每打出一张有源攻击牌，抽牌堆加入的 Dazed 数随当前层数缩放（Hive:2 时多段攻击牌税极重）；Hive 可 1→2→3 逐次信息素递增且每次 +1 力量——蜂群意图 3×7→4×7→5×7。**在 Buff 回合结束前击杀是胜利条件**。虚弱对多段意图**按击削减**（Weak 1 把显示 5×7 变为 3×7）——虚弱是蜂群的正确答案。能力药水在信息素 Buff 回合可免费（当回合 0 费）打出 Demon Form 类引擎。LIVE（对局 36 击杀，145→0）：Inferno 类**能力伤害不触发 Hive Dazed 税**（Inferno 连续 tick 时 Hive 维持 :1；税只在有源攻击**卡牌**命中时触发）；血墙/Hemo/BT 自伤同回合触发 Inferno AoE——本战作为 1HP 残血时的击杀手段（蜜蜂 5×7 未及结算）。T1 零攻击 + 精确 21 挡（Shrug Legion 翻倍 16 + Defend 5）把 Hive 按在 1。
- 残杀千足虫节段（DecimillipedeSegmentBack/Front/Middle, Act2 DecimillipedeElite; 基础节段 40–46 HP）：WRITHE_MOVE = 多段攻击 5 (A:6) ×2；CONSTRICT_MOVE = 单次攻击 8 (A:9) + 1 Weak；BULK_MOVE = 单次攻击 6 (A:7) + 自身 +2 力量；REATTACH_MOVE = 治疗；DEAD_MOVE = 死亡状态。被动 ReattachPower 25：节段死亡而其他节段仍存活时进入 DEAD 状态（不可选中）；其回合结束时重新接合并回复 25。当其余节段全部死亡时，所有节段淡出彻底死亡——在同一窗口清掉全部节段，否则它们会复活。同窗清场=胜利条件（AoE 或单体数学均可，只要三段同窗倒下）；0 HP 时的复活表现为 Heal 意图（类 Parafright）。细节：低血段**留活**、其余段处 DEAD 等待时可避免双段回接回血；杀掉唯一存活段会让全部 DEAD 段在下个敌方回合走 Heal 意图回接（各 +25）——要么铺伤后同窗全倒，要么在其余段已 DEAD 时留一个存活段不动。0 HP DEAD 段不可选中——攻击不要指向它们（Iron Wave 类空转规则）。战斗内污浊药水（对全体 12 伤）可直接带走 12 HP 节段；其自伤触发 Rupture。
- TheObscura（TheObscura, Act2 TheObscuraNormal; 123 HP）：ILLUSION_MOVE = 召唤 1 只 Parafright；PIERCING_GAZE_MOVE = 单次攻击 10 (A:11)；SAIL_MOVE（Wail）= 增益——全体队友 +3 力量；HARDENING_STRIKE_MOVE = 单次攻击 6 (A:7) + 自身 6 格挡 (A:7)。首次 ILLUSION 后在 凝视/哀嚎/硬化 间随机分支（不连续重复）。
- Parafright（Parafright, Act2 TheObscuraNormal 召唤; 21 HP）：SLAM_MOVE = 单次攻击 16 (A:17)；重复。被动 IllusionPower 1：死亡时经 REVIVE_MOVE 回复满血复活（同 EyeWithTeeth）。击杀 TheObscura 可阻止继续召唤。
- ThievingHopper（偷窃跳虫, Act2 ThievingHopperWeak; 79 HP）：THIEVERY_MOVE = 单次攻击 17 (A:19) + 经 SwipePower 偷走 1 张牌库卡（优先级：非 Imbued 的 Uncommon → Common/Rare/Event → Basic/Quest → Ancient/Imbued，来源为抽牌堆/弃牌堆）；NAB_MOVE = 单次攻击 14 (A:16)；HAT_TRICK_MOVE = 单次攻击 21 (A:23)；FLUTTER_MOVE = 增益 FlutterPower 5；ESCAPE_MOVE = 逃跑（到位后自循环）。循环：THIEVERY → FLUTTER → HAT_TRICK → NAB → ESCAPE。被动：EscapeArtistPower 5——逃跑倒计时，其回合结束递减；FlutterPower 5——受到的攻击伤害 ×0.5，每次未格挡攻击命中递减 1，归零时被眩晕并结束悬停。SwipePower：跳虫死亡时被偷卡牌作为战斗奖励回到你的牌库。
- TheInsatiable 无底之欲（TheInsatiable, Act2 TheInsatiableBoss; 321 HP）：LIQUIFY_GROUND_MOVE = 增益；THRASH_MOVE / THRASH_MOVE_2 = 多段攻击 8 (A:9) ×2；LUNGING_BITE_MOVE = 单次攻击 28 (A:31)；SALIVATE_MOVE = 增益 自身 +2 力量 (A:3)。循环：LIQUIFY → THRASH → SALIVATE → THRASH_2 → LUNGING_BITE → THRASH… **击杀机制已解码**：SANDPIT_POWER 是吞噬倒计时，初始 **4**，每次敌方阵营回合开始 −1；**归 0 时玩家被直接吞噬，无视 HP/格挡**（早前「意图显示 bug」判定错误）。开战向玩家牌库注入 **6 张 FranticEscape**；**打出一张 FE = 沙坑 Amount +1**（该牌自身费用永久 +1）——留到计数 1–2 作紧急延时；早前档案「绝不打出 FranticEscape」规则是错误的。纯净从手牌消耗未打出的 FranticEscape = 沙坑零变化（安全瘦身）。战斗计划：**输出竞速**——在倒计时耗尽前打掉 321 HP；格挡应对 THRASH/LUNGING_BITE 但拦不住吞噬；每回合跟踪 `SANDPIT_POWER:amount`。意图：THRASH 8×2（虚弱按击削减）、LUNGING_BITE 28（力量强化约 30）、SALIVATE +2 力量 Buff；进场有效 HP >60 且竞速回合手上有挡线。
- KaiserCrab 皇蟹（KaiserCrab, Act2 KaiserCrabBoss；双爪遭遇）：槽位 crusher + rocket，无本体目标。遭遇生成 Crusher（crusher 槽）+ Rocket（rocket 槽）。玩家侧被动 SurroundedPower；每只爪各带 BackAttackLeftPower/BackAttackRightPower（朝向标记）+ CrabRagePower。
  - Crusher 碾碎爪（Crusher；209 HP）：循环 THRASH_MOVE = 单次攻击 12 (A:14) → ENLARGING_STRIKE_MOVE = 单次攻击 4 → BUG_STING_MOVE = 多段攻击 6 (A:7) ×2 + 2 Weak + 2 Frail → ADAPT_MOVE = 增益 自身 +2 力量 (A:3) → GUARDED_STRIKE_MOVE = 单次攻击 12 (A:14) + 自身 18 格挡 → 回 THRASH。
  - Rocket 火箭（Rocket；199 HP）：循环 TARGETING_RETICLE_MOVE = 单次攻击 3 (A:4) → PRECISION_BEAM_MOVE = 单次攻击 18 (A:20) → CHARGE_UP_MOVE = 增益 自身 +2 力量 (A:3) → LASER_MOVE = 单次攻击 31 (A:35) → RECHARGE_MOVE = 睡眠 → 回 TARGETING_RETICLE。
  - 战斗备注：意图数值已含夹击 ×1.5（侧击爪的 THRASH 12 显示为 18）。击杀顺序教条：先集火 Rocket（LASER 是致死尖峰）；其死亡触发存活爪的 CrabRagePower——Crusher 获得 +6 力量 + 99 无来源格挡（同帧读数）——99 挡可被伤害磨掉（挡后 HP 在挡清空前不掉）；同时用格挡应对力量强化后的循环。Rocket RECHARGE 睡眠回合是免费攻击窗。compact-state 的 `POWER:amount`（SURROUNDED:1、CRAB_RAGE:1、力量层数）每回合必读。
- KnowledgeDemon 知识恶魔（KnowledgeDemon, Act2 KnowledgeDemonBoss; 379 HP）：招式循环 CURSE_OF_KNOWLEDGE_MOVE（减益）→ SLAP_MOVE → KNOWLEDGE_OVERWHELMING_MOVE → PONDER_MOVE → 分支（诅咒计数 <3 回 Curse，否则 Slap）。
  - CURSE_OF_KNOWLEDGE_MOVE：玩家从 2 张 IChoosable 诅咒牌中选 1——按计数轮换：0 = Disintegration | MindRot；1 = Disintegration | Sloth；2 = Disintegration | WasteAway。所选牌不进牌库；OnChosen 立即施加对应能力：Disintegration → DisintegrationPower N（按计数 6/7/8——每个己方回合结束受 N 点无来源伤害）；MindRot → MindRotPower 1（每回合抽牌 −1）；Sloth → SlothPower 3（每回合最多打出 3 张牌）；WasteAway → WasteAwayPower 1（最大能量 −1）。每次 Curse 后计数 +1。
  - SLAP_MOVE = 单次攻击 17 (A:18)。
  - KNOWLEDGE_OVERWHELMING_MOVE = 多段攻击 8 (A:9) ×3。
  - PONDER_MOVE = 单次攻击 11 (A:13) + 回复 30 × 玩家数 + 自身 +2 力量 (A:3)。

## 其他章节 — 已提取 Boss（确定性数值）

- Queen（Queen, Act3 QueenBoss; 400 HP）：PUPPET_STRINGS_MOVE = 卡牌减益——ChainsOfBindingPower 3；YOU_ARE_MINE_MOVE = 减益——99 Frail/Weak/Vulnerable；BURN_BRIGHT_FOR_ME_MOVE = 增益；OFF_WITH_YOUR_HEAD_MOVE = 多段攻击 3 (A:4) ×5；EXECUTION_MOVE = 单次攻击 15 (A:18)；ENRAGE_MOVE = 增益 +2 力量。ChainsOfBindingPower 行为（实机观察）：玩家身上有 chains 时，部分出牌会消耗卡牌且零效果（静默无效）——该模式并非严格的每回合出牌次数上限（同一回合观察到全额生效与部分沉默并存）。火炬头聚合体是独立战斗目标——它存活时战斗不会结束。
- TestSubject（TestSubject, Act3 TestSubjectBoss; 多阶段）：BITE 20 (A:22)、SKULL_BASH 14 (A:16)、MULTI_CLAW 10 ×3、PHASE3_LACERATE 10 (A:11) ×3、BIG_POUNCE 45、BURNING_GROWL = 状态灼烧 3 (A:5) + 自身 +2 力量 (A:3)；经 RESPAWN_MOVE 重生/回复阶段。被动 AdaptablePower、EnragePower 2 (A:3)、PainfulStabsPower、NemesisPower。战斗要点：EnragePower 在任何人打出技能牌时都会触发——技能牌密集的牌组会快速喂养该 Boss；优先使用攻击/能力牌。AdaptablePower 使其死亡时经重生/回复阶段复活（阶段一刷新 ADAPTABLE_POWER:1 + ENRAGE_POWER:2；0 HP 时 Boss 翻转为 `Heal;Buff` 重生）。Enrage 之下惯用的 SecondWind/FeelNoPain 技能包是该 Boss 的燃料——反转为攻击/能力牌，仅生存所迫时才打技能牌。 ADAPTABLE_POWER:1 + ENRAGE_POWER:2 可见；全攻击包（Hemokinesis/Peck/Strike 线，零技能牌打出）让 Enrage 阶段一全程稳在 :2（单回合 97→53）；重锤一击带走阶段二残血（Boss 翻为 `Heal;Buff` 0 HP 状态）；end_turn 经 win-condition force path → 战斗奖励 → THE_ARCHITECT EA 结局 floor 48。教训：Enrage 战中惯用的 SecondWind/FeelNoPain 技能包就是 Boss 的燃料——反转为攻击/能力优先，技能仅在生存被逼时打出。
- SoulNexus（SoulNexus, Act3 SoulNexusElite; 234 HP）：SOUL_BURN_MOVE = 单次攻击 29 (A:31)；MAELSTROM_MOVE = 多段攻击 6 (A:7) ×4；DRAIN_LIFE_MOVE = 单次攻击 18 (A:19) + 强减益——对玩家施加 2 Vulnerable + 2 Weak。无特殊机制——直伤型精英；DRAIN_LIFE 减益确认（玩家 VULNERABLE_POWER:2 + WEAK_POWER:2 同帧读数）；后期单体意图随力量增长（观察到 43 级）——在其回合前击杀或用 Fortifier 类硬挡。
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
- FrogKnight 青蛙骑士（Act3，出现于 Unknown 房战斗; 191 HP）：被动 PlatingPower 15——回合 1 出场获得 15 格挡、其阵营回合末再获得 15 格挡，其阵营回合开始时（非回合 1）镀甲 −1 层；观察到的意图：单次 13+减益、多段 5×2、增益（+2 力量）、单次 21（力量加成后）、防御+增益。镀甲衰减+回挡循环逐回合追踪 15→14→13→12→11；每次增益回合永久累积 +2 力量（T4 时力量达 5——增益叠加在整场战斗内永久有效）；力量加成单体意图观察值 T4 为 18;减益、T5 为 26——表值 21 应视为随增益力量增长的下限。个位数 HP 下脆弱税挡值无法覆盖 26 意图。
- GlobeHead 电球头（Act3 Glory 普通怪；普通 148 HP / A+ 档 158；出场被动 **Galvanize / GALVANIC_POWER 6**——你的能力牌获得 Galvanized，打出一张对你造成 6 点伤害（该伤害**触发 Rupture**——Galvanic 战斗先部署 Rupture 再打 Power 牌喂养；己方回合的 Galvanic 税也会触发 Inferno 类回合开始引擎）。招式：**Thunder Strike 6伤 ×3**；**Shocking Slap 13伤 + 2 虚弱**（「13; Debuff」精确；有数据库记为 2 易伤——来源分歧，显示虚弱类减益）；**Galvanic Burst 16伤 + 自身 +2 力量**（「16; Buff」）。
- MechKnight 机甲骑士（Act3 MechKnightElite; 300 HP）：出场神器 3 层（每个可见减益施加被清零并消耗 1 层）；观察到的意图：单次 25 → 状态卡 4（向玩家手牌加入灼伤）→ 防御+增益（+5 力量 +15 格挡）→ 单次 40（力量加成后）。雷霆一击/猛击/嘲讽可烧神器层数——3 层烧完后易伤才能挂上。出生 HP 可变：观察到以 1/300 当前 HP 出生的场次——不保证满血。
- BattleFriendV1/V2/V3 战斗好伙伴（战痕假人事件陪练；单人第三章75/150/300 HP 不缩放）：招式 NOTHING_MOVE——从不攻击；出场 BattlewornDummyTimeLimitPower 3（假人阵营回合末递减；到 1 时假人逃跑并置 RanOutOfTime → 事件无奖励）。纯输出竞速。
- ScrollOfBiting 咬人卷轴（ScrollOfBiting, Act3 ScrollOfBitingNormal; 30–39 HP）：出场被动 PaperCutsPower 2；CHOMP = 单次 14 (A:16)；CHEW = 多段 5 (A:6) ×2；MORE_TEETH = 增益 自身 +2 力量。PaperCutsPower：持有者的有源攻击造成未格挡伤害时，对玩家追加纸割伤害（见 powers_zh.md）。
- PunchConstruct 拳击构装体（PunchConstruct, Act3 PunchConstructsNormal; 55 HP）：出场 ArtifactPower 1；READY_MOVE = 自身 10 格挡 → STRONG_PUNCH_MOVE = 单次 14 (A:16) → FAST_PUNCH_MOVE = 多段 5 (A:6) ×N + 玩家 1 Frail。
- InfestedPrism 立柱构造体（InfestedPrism）：Act2 精英与 Act3 普通怪（观察到 65 HP 变体）均出现；VitalSpark/REPEATER 行为见 Act2 精英条目。
- Aeonglass（Aeonglass, Act3 AeonglassBoss; 512 HP）：EBB_MOVE = 单次 26 (A:32) + 33 格挡；EYE_LASERS_MOVE = 多段 11 (A:12) ×2；INCREASING_INTENSITY_MOVE = 状态 Wither 1 (A:2) + 力量成长；出场 ArtifactPower 3。
- WaterfallGiant（WaterfallGiant, Act4 WaterfallGiantBoss; 240 HP）：PRESSURIZE 增益 SteamEruption 15 (A:20) → STOMP 15 (A:16) → RAM 10 (A:11) → SIPHON 治疗 → PRESSURE_GUN 20 (A:23，每次 Pressure Up +5) → PRESSURE_UP 13 (A:14) → 回 STOMP；ABOUT_TO_BLOW 眩晕 → EXPLODE 处决。
- SoulFysh（SoulFysh, Act4 SoulFyshBoss; 211 HP）：BECKON 状态 ×2 → DE_GAS 单次 16 (A:17) → GAZE 单次 7 (A:8) → FADE Intangible 2 → SCREAM 单次 13 (A:15) + 3 Vulnerable → 循环。
- LagavulinMatriarch（LagavulinMatriarch, Act4 LagavulinMatriarchBoss; 222 HP）：SLEEP → SLASH 19 (A:21) → SLASH2 12 (A:14) + 格挡 → DISEMBOWEL 9 (A:10) ×2 → SOUL_SIPHON 减益（玩家 −2 力量/敏捷，自身 +2 力量）。被动 PlatingPower 12、AsleepPower 3。epoch 内容：可作为 **Act 1 Boss** 出现（222 HP）——与 WaterfallGiant 同模式；以游戏为准，表内 Act4 标签不作数。唤醒眩晕教条：沉睡期间用卡牌打出未格挡伤害 → 同一结算内移除镀甲与 Asleep 并将其击晕进 WakeUpMove——优于白送它睡过镀甲 12 回合。醒后循环：19 单击 → 9×2 多段 → 12;防御（攻击+自身 12 挡）→ Debuff;Buff 属性抽取（玩家 −2 力量 且 −2 敏捷，Boss +2 力量/循环）→ 随力量强化重复——在 ~2 个抽取循环内击杀，否则敏捷税把格挡价格抬出战斗。

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
- GalvanicPower N：你的能力牌获得 Galvanized；打出时对你造成 N 点伤害。**该 Galvanic 伤害对 Rupture 计为 HP 损失事件——Rupture+ Amount2 部署后于 Galvanic 下打出能力牌 = 6伤 + 2力量同次结算（Rupture 部署自身即触发：力量 1→3；此后每张能力牌都付 6HP 换 2力）。Galvanic 战斗先部署 Rupture 再打 Power 牌喂养。
- VitalSparkPower N：你的技能牌获得 Tainted；打出时对你施加 TaintedPower N。
- SuckPower N：拥有者有源攻击对任意目标造成未格挡伤害后，每次命中实例 +N 力量。
- SurprisePower：死亡时生成 SneakyGremlin + FatGremlin 并移交被偷金币（地精佣兵）。
- 授予负荆棘的招式（如 SpinyToad 爆发 −5）会移除其先前授予的荆棘。

- 产卵虫 直飞产卵虫（Ovicopter，Act2 OvicopterNormal 族，128 HP）：SUMMON 召唤 3 枚结实的卵（各自 HATCH_POWER 倒计时）；孵化 → 幼虫；循环 召唤 → 单击 ~10+干扰 → 召唤（力量随战斗叠加，意图 10→28→33）。 战斗备注：应母虫集火；清波消耗战输给其力量叠层。EN: Ovicopter.
- 幼虫（产卵虫孵化体；19–21 HP）：MINION_POWER；NIBBLE 级单击基础 4，每轮循环叠力（4→6）。死亡不结束战斗。EN: Larvae.

## 其他怪物解码备注

主表之后解码的静态机制；无 run 记录。教条 = 击杀窗 / 对策规则。

### 中文名对照（state 名 ↔ 参考名）
ThievingHopper 偷窃草蜢；HauntedShip 幽灵船；BowlbugRock 盛碗虫（石）；BowlbugNectar 盛碗虫（蜜）；GremlinMerc 地精佣兵；TerrorEel/PhantasmalGardener 四鳗组 花园幽灵鳗（Act1 精英；26–31 HP ×4；SKITTISH_POWER；意图 1×3/5/7/Buff）；Act1 泥螺 = SludgeSpinner 淤泥旋螺；WaterfallGiant 瀑布巨兽（游戏内作为 Act1 Boss 出现——epoch 内容；以游戏为准）；Obscura 系召唤师 胧光怪；Act1 Boss 灵魂异鱼（211 HP；意图 2/11/Debuff 侧；INTANGIBLE_POWER 回合攻击减为 1–2/击；与表 Boss 身份未解——仅记 live 名）；LagavulinMatriarch 乐加维林族母；KnowledgeDemon 知识恶魔；Coral Cluster/Skulking Colony 鬼祟珊瑚群；Toadpole 蟾蜍蝌蚪；SewerClam 下水道蚌；DevotedSculptor 虔诚雕刻师；LivingShield 活体盾；TowerGunner 高塔炮手；LostThing 失落之物；ForgottenThing 遗忘之物；LivingFog 活雾；HunterKiller 猎人杀手；CorpseSlug 海洋混混；PunchConstruct 拳击构装体；LouseProgenitor 泥虫之祖/虱虫之祖（同类族）；SlumberingBeetle 熟睡甲虫；FossilStalker 化石追踪者；Ritual cultists 钙化邪教徒/潮湿邪教徒。

### 其他解码
- 瀑布巨兽 WaterfallGiant（Act1 Boss 类）：SteamEruption PRESSURIZE 时 Amount 15（基础值；A-deadly 20 档 A1 未激活），每次 PRESSURE_UP +3（15→18→21…）；SIPHON 回复 +10；EXPLODE 处决 = 当前 SteamEruption Amount；死后再出现 999999999 HP + Stun 意图假人，EXPLODE 随后结算（A1 4 层时显示 36）。LIVE 击杀序列（对局 36）：击杀回合 → 假体 999999999 HP + Stun 立即出现，EXPLODE **不在击杀回合结算**；假体回合为 Stun（无伤），EXPLODE 的 Amount 意图在**下一个敌方回合**结算——死亡爆炸的挡要备在那一回合（24 挡吃 36 → 实吃 12），EXPLODE 后战斗结束。
- 鬼祟珊瑚群 Coral Cluster / Skulking Colony（Act1 精英；75 HP）：HARDENED_SHELL_POWER:20（补丁自基础 15 上调至 20）——每回合 HP 损失上限 = Amount 减去本回合已受伤害；溢出浪费——节奏化命中，每回合恰好 20（75 HP → 至少 4 回合）。循环 Smash/Zoom → Inertia（伤害+自身力量——竞速，力量叠层使后回合致命）→ Piercing Stabs（多段）→ 循环。对策：按上限节奏化命中、Piercing Stabs 回合全挡、Inertia 力量雪球前击杀。
- 蟾蜍蝌蚪 Toadpole（Act1；21/24 HP 双体；数据库可标 Act3——epoch 软标签，以游戏为准）：固定循环 Spike Spit 3伤×3 → Whirl 7 → Spiken（Buff，自身 +2 荆棘）→ 循环。荆棘 2 = 每张命中它的攻击牌反伤 2（多段按实例付）；Spiken 荆棘次回合过期（单循环 Buff）。对策：Whirl 回合击杀攻击意图那只；Spiken 窗口倾泻伤害；免费窗还有一回合时不要打带荆棘的蝌蚪。
- 下水道蚌 SewerClam（Act1；56 HP；出生 8 挡 + PLATING_POWER:8）：镀甲 = 持有者回合结束获得等同当前镀甲层数的格挡，下回合开始镀甲 −1（自续衰减甲 8→7→6…；玩家 EternalArmor 同公式）。招式 Jet 10 / Pressurize +4 力量（竞速计时——Jet 变 14、18…）。对策：节奏化穿透滚动挡，2 层 Pressurize 前击杀；易伤窗（Bash→Cinder 类）高效破甲。
- 骇鳗类精英 TerrorEel（140 HP）：SHRIEK_POWER 在未格挡伤害越过其 HP 区间时将其击晕——其大意图回合被吃掉；次回合击杀。
- 啃咬机 Chomper：出生 ArtifactPower（观察到 1 或 2——出生值可变）；Thunderclap 易伤被 Artifact 吸收（每目标 −1 层，伤害部分照常命中）；对 0 易伤目标 MoltenFist 施加 0 层且**不消耗** Artifact 层——先 Bash/Thunderclap，后 MoltenFist。
- 外骨骼虫 Exoskeleton：HardToKill 9 上限——每次命中最多结算 9，超出舍弃（纸蛙加成命中同样封顶）；低于上限的小实例伤害（狱火 6、势不可当 6）全额生效；用多段小伤害节奏化。
- 螨虫 Myte：TOXIC 状态牌——费用 1，打出消耗，回合末仍在手则受 5 点无来源伤害；循环 TOXIC 2 → BITE 13–15（虚弱可削）→ SUCK 4+2力。TOXIC 意图显示为 StatusCard 标签=数量。
- 刺蟾 SpinyToad（约 116 HP）：Buff 回合 THORNS_POWER:5；SPIKE_EXPLOSION 意图 23——爆炸回合后荆棘递减至 0（之后是自由攻击窗）；TONGUE_LASH 17。
- 盛碗虫 Rock/Nectar 双体：IMBALANCED_POWER——攻击意图被完全格挡时自我击晕（意图翻为 Stun；眩晕回合后重新上膛——可连锁晕）。Nectar 循环 THRASH 3 → BUFF +15 力量 → THRASH2 3+力（Buff 落地前击杀即拆除击杀计时器）。
- 地道虫 Tunneler（87 HP 类）：BURROW 给约 32 挡 + BurrowedPower；潜地挡在**敌方回合**结算，非意图时预给；AfterBlockBroken（挡破）：Stun 意图 + Burrowed 移除 + 剩余挡清零同帧读数（攻击意图取消）。潜地目标**可以被攻击**——破挡即取消攻击。
- 偷窃草蜢 ThievingHopper（约 79 HP）：ESCAPE_ARTIST_POWER 倒计时 5，每其回合 −1；倒计时 1 且意图=Escape 时，清掉 Flutter（攻击减半 power，每次未挡命中递减）会把意图 Escape→Stun——逃脱前击杀。SWIPE_POWER 持有偷来的牌库卡；击杀时归还（静默入库触发 LuckyFysh +15）。
- 地精佣兵 GremlinMerc：THIEVERY_POWER 在其回合偷 20 金；死亡时 SurprisePower 生成 卑鄙地精 SneakyGremlin 11 HP + 胖地精 FatGremlin 17 HP（HEIST_POWER，意图 Escape——1 HP 时逃脱无奖励）。死后假人模式：999999999 HP + Stun 意图，EXPLODE 处决约 51 基础 / A1 36（可挡扛；结算后战斗结束）。
- 幽灵船 HauntedShip（63 HP）：SWIPE 13 / STOMP 4×3 + Weak 1 / HAUNT = Weak 3 + Dazed 状态牌注入（意图「Debuff; 5」= 5 张 Dazed）。
- 泥虫之祖/虱虫之祖 LouseProgenitor（135 HP 类）：CURL_UP 在首次卡牌攻击时给 14 格挡——顺序 = 伤害先落 HP，**然后**+14 挡（伤后授予，非预吸收）；用最便宜攻击先破壳。WEB 9 + 虚弱；CURL_AND_GROW = 自身 14 挡 + 力量 +5；POUNCE = 14+力（Boss 力量 5 时意图 19）；虚弱削 POUNCE（Weak 1 下 19→14）。
- 淤泥旋螺 SludgeSpinner（Act1 泥螺；37–39 HP；ToughEnemies 档 41–42 在 A1 未激活）：随机不重复循环 OIL_SPRAY 8 + Weak 1 / SLAM 11 / RAGE 6 + 自身力量 +3；意图「8;Debuff」= OIL_SPRAY。
- 花园幽灵鳗 PhantasmalGardener/四鳗组（26–31 HP）：SkittishPower 6（A-tough 7）——每回合首次卡牌攻击命中后**该次攻击结算完**再给 6 挡；多段单卡规则：同一攻击指令内全部命中先于 Skittish 挡结算（Dismantle 易伤双击可穿透「待定」挡击杀）。招式 BITE 5 / LASH 7 / FLAIL 1×3 / ENLARGE Buff 自身+力量。
- 海洋混混 CorpseSlug（约 45 HP 单体）：RAVENOUS——Amount = 盟友死亡时赋予持有者的力量 + 持有者被眩晕 1 动；每回合杀一只把每次死亡转化为幸存者身上的免费眩晕窗。循环 WhipSlap 3×2 → Glomp 8（live 意图可超表值）→ Goop Frail 2 → 循环。
- 胧光怪 Obscura 系召唤师（123 HP）：召唤 Parafright 寄生惧魔（ILLUSION_POWER+MINION_POWER，21 HP，SLAM 16）；杀主体即清场规则（主体死亡战斗立即结束，即使召唤物在 0 HP 排队复活）；Parafright 复活循环 0 HP → Heal 意图 → 满 21 HP 循环，直至主体死亡。
- 熟睡甲虫 SlumberingBeetle（86 HP，PlatingPower 15）：唤醒模式——沉睡期间未格挡卡牌伤害剥离沉睡并击晕（同类 LagavulinMatriarch）。
- 化石追踪者 FossilStalker（52 HP）：SUCK_POWER:3——未格挡攻击命中每实例 +3 力量；攻击回合全挡让 SUCK 休眠。
- 仪式邪教徒（钙化邪教徒 41 / 潮湿邪教徒 53）：Buff 回合 RITUAL_POWER（层数可变，如 2 和 5）；其后每回合开始力量递增——竞速教条；在雪球前集火较小的邪教徒。
- 活雾 LivingFog（Act2；80 HP；亦见 Act1——标签软性）：Advanced Gas 8 + Smoggy T1；Bloat 5 + 召唤 Gas Bomb（7 HP MINION_POWER，意图 8）；Smoggy = 本回合打出第一张技能牌后其余技能牌显示 no(None) 不可打出直至回合结束（区别于 EnergyCostTooHigh）。每回合一技能纪律。LIVE（对局 36）：击杀母体（本体）战斗即结束，召唤的 Gas Bomb 同帧消亡（母体死亡规则适用，即使炸弹仍在场）。
- 双尾鼠 TwoTailedRats（Act1/Underdocks 类群怪对，各 18–21 HP；对局 36 perplexity 研究补档，此前零档案条目）：循环 抓挠 8（不可连用）/ 疾病咬击 6（不可连用）/ 尖啸类减益 / 呼叫支援（召唤同类）。LIVE 对局 36 订正：减益招实测施加 **Frail**，非网络来源提示的 Vulnerable——在更多 live 样本前按 Frail 类对待。双体 T1 意图实测：6（咬击）、Debuff（尖啸）、8（抓挠）。对策：每回合集火一只；引擎 AoE（Inferno 6/回合）可单独清场。
- 猎人杀手 HunterKiller（Act2 121 HP）：TENDER_POWER 落在**玩家**身上（见 powers_zh.md——回合内力量/敏捷抽取，下一玩家回合开始恢复）；不尊重该机制战斗会尖峰化。
- 拳击构装体 PunchConstruct（55 HP 单体，Artifact 2）：Defend/READY 类自身挡 → 5×2;Debuff → Buff/Defend 类；Artifact 剥离教条：Bash 的易伤被 Artifact 吸收但伤害照常命中且 Artifact 层被消耗。
- 知识恶魔 KnowledgeDemon（Act2 Boss 379）：四回合循环——知识诅咒（选择弹窗：T1 崩解 vs 心灵腐蚀、T2 崩解 vs 怠惰、T3 崩解 vs 衰朽——伤害耐受/抽牌密集牌组选崩解；固定回合末伤害优于抽牌/能量否定；第三组诅咒后不再出诅咒）→ Slap 17（A9+ 18）→ Knowledge Overwhelming 8×3=24（A9+ 9×3）→ Ponder 11 伤 + 回复 30 + 自身力量 +2（A9+ 13/+3）。崩解层数随每次选择增长（每层回合末玩家伤害税）。LIVE（对局 36 败局，Boss 379→60 后 T8 死亡）：四回合循环与诅咒 counter 组 0/1 确认；崩解层实测 6 然后 13（6+7 按 counter——**无挡**回合末税，每个玩家回合都结算）；Ponder +30 回血 + 力量竞速意味着击杀窗必须每 4 回合循环打出 >30 净伤，否则回血循环获胜；教条选择（崩解胜心灵腐蚀/怠惰）两次正确，败因是战线长度 vs 税叠层 + Boss 闸门 0 药水。Weak 药水 live：施加 WEAK_POWER:3 回合（SLAP 17→12）。
- 活体盾 LivingShield（55 HP；A8+ 65）+ 高塔炮手 TowerGunner（41 HP 双体）：LivingShield RAMPART_POWER 25 盾缓冲；**击杀顺序与主仆类相反**：TowerGunner 存活时盾使用 Shield Slam 6；Gunner 死亡使盾永久翻为 Smash 16（+3 力量）——**先杀 LivingShield** 让 Gunner 保持 3×5 驯态。TowerGunner 出生 25 挡（经其 Defend 类招式回充）；青铜鳞荆棘硬反制其 3×5 多段（3 荆棘 ×5 命中 = 15/回合削血）。
- 虔诚雕刻师 DevotedSculptor（Act3 普通 162 HP）：T1 Forbidden Incantation = RITUAL_POWER 9（其后每回合开始 +9 力量）；T2 起每回合 Savage：12 基础 + 当前力量（意图 12→21→30 类）。竞速教条：每拖一回合进账约 +9——在 Savage+力量超出格挡预算前倾泻。
- 失落之物 LostThing（93）+ 遗忘之物 ForgottenThing（106）双体：PossessStrength/PossessSpeed 在持有者回合偷取玩家属性（每次偷取各 +2 对应属性）；**持有者死亡时被偷属性同帧归还玩家**——杀持有者夺回。两者开局均为 Debuff;Buff / Debuff;Defend;Buff 循环，其后 6×2/15 级攻击回合。
- Whirlwind 实例订正（全战）：Whirlwind+ 实例解析为**扁平 ~8/击，力量/木偶加法不进实例**（外骨骼虫包：3 实例 ×8=24/敌，非力量缩放 9×3）——反编译证实前按 8/击扁平处理；击杀数学改用 Strike/Bludgeon/PerfectedStrike 类力量缩放卡。
- StockPower：死亡时生成 Axebot，StockAmount−1（机器人装配链；充能未清零时战斗不结束）；链条 spawn HP 不保证满血（观察到 1/x 当前 HP）——同类 MechKnight。
- Headbutt/取回浮层（战斗堆 card_choice，NCombatPileCardSelectScreen）：choose 即结算——无 skip 键（`skip` 返回 ok=false）；必须提交 choose 索引。
