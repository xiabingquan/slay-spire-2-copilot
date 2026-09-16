# 能力（powers）

确定性战斗增益/减益参考。ID 与 state 中 `powers[].id` 一致。每条均对照
反编译类 `MegaCrit.Sts2.Core.Models.Powers.*`（`PowerType`、层数行为、
hook 逻辑、`CanonicalVars` 数值）核实。下文「Amount」= power 上显示的层数。
「持有者阵营回合」= power 持有者所属一方的回合（玩家侧为你的回合，敌方侧为
怪物回合）。

格式：`- POWER_ID（Buff/Debuff）：效果。`（括号内为通行中译，无官方译名时
仅用 ID + 机制描述。）

## 核心战斗状态

- VULNERABLE_POWER（易伤，Debuff，Counter）：持有者受到的攻击伤害 ×1.5
  （`DamageIncrease` 1.5）；Paper Phrog / CrueltyPower / DebilitatePower 可
  修改该倍率。敌方阵营回合结束时 -1 层。
- WEAK_POWER（虚弱，Debuff，Counter）：持有者造成的攻击伤害 ×0.75
  （`DamageDecrease` 0.75）；Paper Krane / DebilitatePower 可修改倍率。
  敌方阵营回合结束时 -1 层。
- FRAIL_POWER（脆弱，Debuff，Counter）：持有者从卡牌/怪物招式获得的格挡
  ×0.75。敌方阵营回合结束时 -1 层。
- STRENGTH_POWER（力量，Buff，Counter，可为负）：持有者每次攻击命中
  +Amount 伤害（多段逐段附加）。
- DEXTERITY_POWER（敏捷，Buff，Counter，可为负）：持有者每次从卡牌/招式
  获得格挡时 +Amount 格挡。
- POISON（中毒，Debuff，Counter）：持有者阵营回合开始时受到 Amount 点
  不可格挡、非攻击来源伤害，随后 -1 层；按触发次数重复。触发次数 =
  min(层数, 1 + 对面 AccelerantPower 层数之和)。
- THORNS_POWER（荆棘，Buff，Counter）：持有者被攻击（或 Omnislice）命中
  时，攻击者受到 Amount 点非攻击伤害。
- PLATING_POWER（镀甲，Buff，Counter）：持有者阵营回合开始时 -1 层
  （联机下敌方按 `Decrement`=玩家数 扣层）；阵营回合结束（early）时获得
  Amount 格挡。开局即带镀甲的敌人在第 1 轮还会获得 Amount 格挡。
- REGEN_POWER（再生，Buff，Counter）：持有者阵营回合结束时回复 Amount
  HP，随后 -1 层。
- INTANGIBLE_POWER（虚无，Buff，Counter）：持有者每次受到的伤害/HP 损失
  上限为 1。持有者阵营回合结束时 -1 层。
- BUFFER_POWER（缓冲，Buff，Counter）：接下来 Amount 次会使持有者损失 HP
  的事件改为损失 0（每次消耗 1 层；为 late hook，其他减伤先结算）。
- RITUAL_POWER（仪式，Buff，Counter）：持有者阵营回合结束时获得 +Amount
  STRENGTH_POWER（若由敌方在其回合施加，当回合跳过不触发）。
- FOCUS_POWER（专注，Buff，Counter，可为负）：持有者充能球被动/激发数值
  变为 max(原值 + Amount, 0)。
- VIGOR_POWER（活力，Buff，Counter）：持有者下一次攻击 +Amount 伤害
  （ModifyDamageAdditive；该次攻击后消耗）。
- DOOM_POWER（末日，Debuff，Counter）：持有者阵营回合结束时，若
  CurrentHp <= Amount 则直接被 Doom 击杀（特殊 VFX；同侧所有 doomed
  生物一并结算）。
- CONFUSED_POWER（混乱，Debuff，Single）：持有者每次抽到的卡（原费用
  >= 0）战斗内费用重掷为 0..3 的随机整数
  （`Rng.CombatEnergyCosts.NextInt(4)`）。
- SLOW_POWER（缓速，Debuff，Counter）：持有者受到的攻击伤害 ×
  (1 + 0.1 × 本回合玩家已打出的卡牌数)。`SlowAmount` 每打出一张牌 +1，
  持有者阵营回合开始时归零。显示层数 = SlowAmount × 10。
- MINION_POWER（仆从，Buff，Single）：标记召唤物——其死亡不触发战斗结束
  判定（OwnerIsSecondaryEnemy；持有者死后 power 不保留）。
- ARTIFACT_POWER（人工制品，Buff，Counter）：对持有者施加的可见 Debuff 类
  power 数值被置为 0，随后消耗 1 层人工制品。不可见/内部减益不被挡。
- SURROUNDED_POWER（被夹击，Debuff，Single）：站位状态；当攻击者带有与
  持有者朝向匹配的 BACK_ATTACK_LEFT_POWER / BACK_ATTACK_RIGHT_POWER
  标记时，对持有者的攻击伤害 ×1.5。标记本身为惰性 Single Buff。

## 卡牌绑定减益宿主（另见 afflictions_zh.md）

- CHAINS_OF_BINDING_POWER（束缚之链，Debuff，Counter）：持有者阵营回合内
  抽牌时，最多 Amount 张牌被附加 Bound（本回合已附加数达到 Amount 后停止）。
  power 生效期间每回合只能打出 1 张 Bound 牌；持有者阵营回合结束时清除
  所有 Bound。
- RINGING_POWER（耳鸣，Debuff，Single）：施加时给持有者所有卡牌附加
  Ringing，之后进入战斗的新牌也附加。本回合只要打出过任意一张牌，
  Ringing 牌即不可打出。power 在持有者阵营回合结束时自移除（并清除
  全部 Ringing）。
- TANGLED_POWER（缠结，Debuff，Counter）：施加时给持有者所有攻击牌附加
  Entangled，新进入战斗的攻击牌同样附加。Entangled 牌费用 +Amount 能量。
  power 在持有者阵营回合结束时自移除。
- GALVANIC_POWER（电镀，Buff，Counter，位于敌方）：战斗开始及 Power 牌
  进入战斗时，给玩家的 Power 牌附加 Galvanized（Amount）。打出 Galvanized
  牌时，其拥有者受到 Amount 点非攻击伤害。
- HEX_POWER（诅咒，Debuff，Single）：给持有者所有卡牌（及新牌）附加
  Hexed；power 存在期间 Hexed 牌获得虚无（Ethereal）关键词。施加者死亡
  时移除；移除时清除 Hexed。
- SMOGGY_POWER（烟雾，Debuff，Single）：持有者打出一张技能牌后，给所有
  未附加减益的技能牌附加 Smog；本回合已打出过技能后进入战斗的新技能牌
  同样附加。power 存在期间 Smog 牌不可打出。持有者阵营回合结束时清除
  Smog。
- TAINTED_POWER（污染，Debuff，Counter）：对持有者的攻击伤害 +Amount
  （ModifyDamageAdditive，仅对攻击伤害生效）。敌方阵营回合结束时移除。
- VITAL_SPARK_POWER（Buff，Counter，位于敌方）：战斗开始及进入战斗时给
  玩家技能牌附加 Tainted（Amount）；打出 Tainted 牌时对其拥有者施加
  TAINTED_POWER Amount。

## 玩家经济 / 抽牌类 power

- MIND_ROT_POWER（脑蚀，Debuff，Counter）：持有者每回合手牌抽取 -Amount
  （下限 0）：ModifyHandDraw = max(0, count - Amount)。
- WASTE_AWAY_POWER（衰朽，Debuff，Counter）：持有者最大能量 -Amount。
- NO_DRAW_POWER（禁止抽牌，Debuff，Single）：本回合内持有者的非起手抽牌
  （卡牌效果抽牌）被封锁。持有者阵营回合结束时移除。起手抽牌不受影响。
- NO_ENERGY_GAIN_POWER（Debuff，Single）：本回合持有者获得的能量变为 0。
  持有者阵营回合结束时移除。
- CLARITY_POWER（Buff，Counter）：持有者接下来 Amount 个回合的回合开始
  各 +1 抽牌；每个触发回合 -1 层。
- DRAW_CARDS_NEXT_TURN_POWER（Buff，Counter）：仅在持有者下一回合开始时
  +Amount 抽牌，随后移除。
- MACHINE_LEARNING_POWER（Buff，Counter）：每回合 +Amount 抽牌（power
  存续期间永久生效）。
- DEMESNE_POWER（Buff，Counter）：每回合 +Amount 抽牌 且 +Amount 最大能量。
- PYRE_POWER（Buff，Counter）：+Amount 最大能量。
- FRIENDSHIP_POWER（Buff，Counter）：+Amount 最大能量。
- TOOLS_OF_THE_TRADE_POWER（Buff，Counter）：每回合 +Amount 抽牌；持有者
  回合开始时从手牌选择 Amount 张弃掉。
- TYRANNY_POWER（Buff，Counter）：每回合 +Amount 抽牌；持有者回合开始时
  从手牌选择 Amount 张消耗（Exhaust）。
- ENERGY_NEXT_TURN_POWER（Buff，Counter）：下次能量重置时获得 Amount 能量，
  随后移除。
- GENESIS_POWER（Buff，Counter）：每次能量重置时获得 Amount 星辰（Stars）。
- STAR_NEXT_TURN_POWER（Buff，Counter）：下次能量重置时获得 Amount 星辰，
  随后移除。
- RADIANCE_POWER（Buff，Counter）：能量重置时获得 DynamicVars.Energy 点
  能量（数值由施加者设定），随后 -1 层。
- LIGHTNING_ROD_POWER（Buff，Counter）：能量重置时引导 1 个闪电球，随后
  -1 层。
- SPINNER_POWER（Buff，Counter）：能量重置时引导 Amount 个玻璃球
  （GlassOrb）。
- AUTOMATION_POWER（Buff，Counter）：持有者每抽第 10 张牌时获得 Amount
  能量（计数 `BaseCards` 10，触发后重置为 10）。
- ORBIT_POWER（Buff，Counter）：持有者每通过卡牌花费 4 点能量，触发
  获得 Amount 能量（阈值 4）。
- AGGRESSION_POWER（Buff，Counter）：持有者阵营回合开始时，从弃牌堆随机
  取 Amount 张攻击牌置入手牌并各升级 1 次（可升级时）。
- CURIOUS_POWER（Buff，Counter）：持有者费用 > 0 的 Power 牌费用 -Amount
  （下限 0）。
- FREE_ATTACK_POWER（Buff，Counter）：持有者手牌/打出区的攻击牌费用为 0；
  每打出 1 张攻击牌消耗 1 层。
- FREE_SKILL_POWER（Buff，Counter）：持有者手牌/打出区的技能牌费用为 0；
  每打出 1 张技能牌消耗 1 层。
- FREE_POWER_POWER（Buff，Counter）：持有者手牌/打出区的 Power 牌费用为
  0；每打出 1 张 Power 牌消耗 1 层。
- CORRUPTION_POWER（腐化，Buff，Single）：持有者的技能牌费用为 0，打出后
  消耗（Exhaust）。
- VEILPIERCER_POWER（Buff，Counter）：持有者手牌/打出区的虚无（Ethereal）
  牌费用为 0；每打出 1 张虚无牌消耗 1 层。
- VOID_FORM_POWER（Buff，Counter）：每回合持有者前 Amount 张非自动打出的
  手牌（及星辰费用）费用为 0；回合开始重置计数。
- BORROWED_TIME_POWER（Debuff，Counter）：持有者所有卡牌费用 +Amount。
  持有者阵营回合结束时移除。
- CONFUSED_POWER：见核心战斗状态（费用随机化）。

## 格挡类 power

- RAGE_POWER（愤怒，Buff，Counter）：持有者每当打出一张攻击牌，获得
  Amount 格挡。持有者阵营回合结束时移除该 power。
- FEEL_NO_PAIN_POWER（无痛，Buff，Counter）：持有者每消耗（Exhaust）一张
  自己的牌，获得 Amount 格挡。
- JUGGERNAUT_POWER（Buff，Counter）：持有者每当获得 >0 格挡，对一名随机
  可命中敌人造成 Amount 点非攻击伤害。
- BARRICADE_POWER（壁垒，Buff，Single）：持有者的格挡不再于回合开始时
  清空（ShouldClearBlock 恒 false）。
- BLUR_POWER（模糊，Buff，Counter）：持有者格挡不清空；持有者阵营回合
  开始时 -1 层。
- BLOCK_NEXT_TURN_POWER（Buff，Counter）：持有者格挡被清空时，获得
  Amount 格挡一次并移除该 power。
- SELF_FORMING_CLAY_POWER（自成型黏土，Buff，Counter）：持有者格挡被
  清空时，获得 Amount 格挡一次并移除该 power。
- TORIC_TOUGHNESS_POWER（Buff，Counter）：持有者格挡被清空时，获得
  DynamicVars.Block 格挡，随后 -1 层。
- BEACON_OF_HOPE_POWER（Buff，Single）：持有者在本方阵营回合内首次获得
  格挡时，全体队友各获得该格挡量的一半（×0.5，<1 不触发）；每实例仅
  触发一次。
- COOLANT_POWER（Buff，Counter）：持有者阵营回合开始时，获得
  （球队列中不同球种类数 × Amount）格挡。
- RAMPART_POWER（Buff，Counter）：玩家阵营回合开始时，每名存活的
  TurretOperator 敌人获得 Amount 格挡。
- AFTERIMAGE_POWER（余像，Buff，Counter）：持有者每打出一张牌，获得
  Amount 格挡。
- SHROUD_POWER（Buff，Counter）：为持有者提供 Amount 格挡（触发由宿主
  卡牌/遗物决定）。
- SNEAKY_POWER（Buff，Counter）：为持有者提供 Amount 格挡（触发由宿主
  卡牌决定）。
- SPIRIT_OF_ASH_POWER（Buff，Counter）：持有者出牌前获得 Amount 格挡
  （触发由宿主卡牌决定）。
- DANSE_MACABRE_POWER（Buff，Counter）：持有者出牌前获得 Amount 格挡
  （触发由宿主卡牌决定）。
- CHILD_OF_THE_STARS_POWER（Buff，Counter）：持有者玩家花费星辰时获得
  Amount × 花费星辰数 的格挡。
- SHADOWMELD_POWER（Buff，Counter）：持有者获得的格挡 ×2^Amount；
  持有者阵营回合结束时移除。
- UNMOVABLE_POWER（Buff，Counter）：持有者获得的格挡 ×2。
- FASTEN_POWER（Buff，Counter）：持有者卡牌/招式来源的格挡 +Amount
  （ModifyBlockAdditive）。
- PILLAR_OF_CREATION_POWER（Buff，Counter）：为持有者提供 Amount 格挡
  （触发由宿主卡牌/遗物决定）。

## 攻击伤害修正类 power

- COLOSSUS_POWER（巨像，Buff，Counter）：来自带有 VULNERABLE_POWER 的
  攻击者的攻击对持有者伤害 ×0.5（`DamageDecrease` 0.5）。敌方阵营回合
  结束时 -1 层。
- SHRINK_POWER（缩小，Debuff，Counter；Amount < 0 时为 Single = 永久）：
  持有者造成的攻击伤害 ×0.75（`DamageDecrease` 30 → (100-30)/100）。
  持有者阵营回合结束时 -1 层；施加者死亡时移除。视觉：持有者缩至 0.5。
- SLOW_POWER：见核心状态（按本回合出牌数递增的受击增伤）。
- DOUBLE_DAMAGE_POWER（Buff，Counter）：持有者造成的攻击伤害 ×2；
  持有者阵营回合结束时 -1 层。
- LETHALITY_POWER（Buff，Counter）：持有者卡牌来源的攻击伤害 ×
  (1 + Amount/100)（即 +Amount%；触发与生效窗口由宿主卡决定）。
- ACCURACY_POWER（精准，Buff，Counter）：持有者带 Shiv 标签的攻击
  +Amount 伤害（ModifyDamageAdditive，仅 CardTag.Shiv）。
- CALCIFY_POWER（Buff，Counter）：持有者攻击 +Amount 伤害
  （ModifyDamageAdditive；触发由宿主决定）。
- LEADERSHIP_POWER（Buff，Counter）：持有者攻击 +Amount 伤害
  （ModifyDamageAdditive；触发由宿主决定）。
- PHANTOM_BLADES_POWER（Buff，Counter）：持有者攻击 +Amount 伤害；施加
  及卡牌进入战斗时给持有者卡牌附加 Retain。
- TRACKING_POWER（Buff，Counter）：持有者（或其宠物）对带有 WEAK_POWER
  的目标造成的攻击伤害 ×Amount。
- GIGANTIFICATION_POWER（Buff，Counter）：持有者下一张攻击 ×3 伤害；
  该攻击结算后 -1 层。
- CONQUEROR_POWER（Debuff，Counter）：SovereignBlade 对持有者的攻击伤害
  ×2。持有者阵营回合结束时 -1 层。
- KNOCKDOWN_POWER（Debuff，Counter）：除施加者外任何人对持有者的攻击
  伤害 ×Amount。持有者阵营回合结束时移除。
- FLANKING_POWER（Debuff，Counter）：除施加者外任何人对持有者的攻击
  伤害 ×Amount。持有者阵营回合结束时移除。
- HANG_POWER（Debuff，Counter）：Hang 卡对持有者的攻击伤害 ×Amount。
- SOAR_POWER（Buff，Single）：持有者受到的攻击伤害 ×0.5
  （`DamageDecrease` 50/100）。
- DIAMOND_DIADEM_POWER（Buff，Single）：对持有者的攻击伤害 ×0.5；敌方
  阵营回合结束时移除。
- INTERCEPT_POWER（Buff，Single）：对持有者的攻击伤害倍率 =
  （被掩护生物数 + 1）；与 CoveredPower 联动；敌方阵营回合结束时移除。
- COVERED_POWER（Buff，Single，位于被掩护者）：掩护者存活期间对持有者的
  攻击伤害 ×0；敌方阵营回合结束或掩护者死亡时移除。
- GUARDED_POWER（Buff，Single）：对持有者的攻击伤害 ×0.5；施加者死亡时
  移除。
- TANK_POWER（Buff，Single）：持有者造成的攻击伤害 ×2（并按 decomp 与
  GuardedPower 联动）。
- SURROUNDED_POWER：见核心状态（侧翼攻击者 ×1.5）。
- TENDER_POWER（Debuff，Counter）：持有者每打出一张牌，静默获得 -1 力量
  与 -1 敏捷；持有者阵营回合结束时按本回合出牌数等量返还
  （+N 力量/敏捷）。
- TAINTED_POWER：见减益宿主（受到的攻击伤害 +Amount）。

## 中毒 / Doom / 死亡钟 power

- ENVENOM_POWER（中毒涂毒，Buff，Counter）：持有者的攻击造成未格挡伤害
  > 0 时，对目标施加 Amount 层 POISON。
- NOXIOUS_FUMES_POWER（恶臭气体，Buff，Counter）：持有者阵营回合开始时
  对所有可命中敌人施加 Amount 层 POISON。
- ACCELERANT_POWER（Buff，Counter）：自身无 hook——使对面 POISON 的触发
  次数 +（对面 AccelerantPower 层数之和），不超过毒层数。
- CORROSIVE_WAVE_POWER（Buff，Counter）：抽牌 hook 时对所有可命中敌人
  施加 Amount 层 POISON（触发由怪物招式宿主决定）。
- OUTBREAK_POWER（Buff，Counter）：持有者每次对他人施加 POISON（数值
  变化 > 0）计 1 次；每第 3 次对所有可命中敌人造成 Amount 点非攻击
  伤害；内部计数对 3 取模。
- REAPER_FORM_POWER（Buff，Counter）：持有者（或其宠物）造成攻击伤害
  > 0 时，对目标施加 DOOM = 总伤害 × Amount。
- OBLIVION_POWER（Debuff，Counter）：施加者玩家每打出一张牌，对持有者
  施加 Amount 层 DOOM。玩家阵营回合结束时移除。
- NEUROSURGE_POWER（Debuff，Counter）：持有者阵营回合开始时对持有者
  施加 Amount 层 DOOM。
- COUNTDOWN_POWER（Buff，Counter）：持有者阵营回合开始时触发倒计时
  逻辑（decomp 中 Apply<DoomPower> 到持有者——击杀钟；显示数值见怪物
  卡面文案）。
- DEMISE_POWER（Debuff，Counter）：持有者阵营回合结束时，持有者受到
  Amount 点不可格挡、非攻击伤害。
- DISINTEGRATION_POWER（崩解，Debuff，Counter）：持有者阵营回合结束
  （late）时，持有者受到 Amount 点非攻击伤害。
- MAGIC_BOMB_POWER（Debuff，Counter）：持有者阵营回合结束时，若施加者
  仍存活，持有者受到 Amount 点非攻击伤害，随后该 power 移除。施加者
  死亡时同样移除。
- STRANGLE_POWER（Debuff，Counter）：施加者玩家每打出一张牌，持有者
  受到 Amount 点不可格挡、非攻击伤害。持有者阵营回合结束时移除。
- CONSTRICT_POWER（缩紧，Debuff，Counter）：持有者阵营回合结束时，
  持有者受到 Amount 点非攻击伤害。施加者死亡时移除。
- PAPER_CUTS_POWER（Buff，Counter）：持有者的攻击对玩家造成未格挡伤害
  > 0 时，该玩家失去 Amount 最大 HP。
- THE_GAMBIT_POWER（Debuff，Single）：持有者受到未格挡的攻击伤害 > 0 时，
  持有者立即死亡（触发时移除 power）。

## 复活 / 召唤 / 怪物姿态 power

- HARD_TO_KILL_POWER（坚韧，Buff，Counter）：持有者单次受到的伤害上限
  为 Amount（`ModifyDamageCap` = Amount）。外骨骼虫（Exoskeleton）施加
  Amount = 9——单次 HP 损失上限 9，超出部分直接作废、不保留。
- SLIPPERY_POWER（湿滑，Buff，Counter）：对持有者任何 >= 1 的 HP 损失
  降为恰好 1；每次造成 >= 1 未格挡伤害的命中消耗 1 层。
- HARDENED_SHELL_POWER（Buff，Counter）：持有者每回合 HP 损失上限为
  Amount 减去本回合已受伤害（计数回合开始重置）。
- REATTACH_POWER（重组，Buff，Single，千足虫体节）：死亡时，若仍有其他
  带 Reattach 的体节存活，该体节进入死亡状态（不移出战斗、不可选中），
  并在其回合结束时重组——回复 Amount HP。仅当其他所有体节全部死亡时
  其死亡才为致命。死亡期间增益保留。
- ILLUSION_POWER（幻象，Buff，Single）：死亡时保留增益（减益除非常驻类
  外均移除），排入带 HealIntent 的 REVIVE_MOVE——回复至满血
  （MaxHp - CurrentHp）。施加时若无 MINION_POWER 则补 1 层。复活期间
  持有者不可被选中。
- ADAPTABLE_POWER（Buff，Single）：Test Subject 式自我复活——死亡时战斗
  不结束、生物不移除，直至复活逻辑完成（怪物状态机宿主；增益保留）。
- DIE_FOR_YOU_POWER（Buff，Single）：Osty 系死亡处理——持有者死亡时战斗
  不结束，持有者移出战斗；复活由宠物逻辑处理（见角色卡）。
- INFESTED_POWER（寄生，Buff，Single）：持有者死亡时在同侧生成 4 只
  Wriggler（StartStunned = true）；生成结算完成前战斗结束判定被阻塞。
- STOCK_POWER（储备，Buff，Counter）：持有者死亡（Amount > 0）时，在
  同格生成 1 只 Axebot，其 StockAmount = Amount - 1（机器人形态链）；
  生成期间战斗不结束。
- STEAM_ERUPTION_POWER（Buff，Single）：持有者死亡处理——死亡时战斗不
  立即结束，增益保留供后续遭遇逻辑使用。
- SURPRISE_POWER（Buff，Single）：持有者死亡处理——直至惊喜召唤逻辑
  （CreatureCmd.Add 下一只怪物）完成前战斗不结束。
- CRAB_RAGE_POWER（Buff，Single）：持有者死亡时，施加力量
  （DynamicVars）并获得 DynamicVars.Block 格挡（亡语姿态）。
- RAVENOUS_POWER（Buff，Counter）：同侧其他生物死亡且持有者存活时，
  持有者被击晕进入吞噬招式并获得 +Amount STRENGTH。
- SUMMON_NEXT_TURN_POWER（Buff，Counter）：持有者玩家回合开始时召唤
  Amount 只 Osty 宠物，随后移除该 power。
- SIC_EM_POWER（Debuff，Counter）：施加者的 Osty 宠物对持有者造成伤害
  时，为宠物主人召唤 Amount 只 Osty。持有者阵营回合结束时移除。
- DEVOUR_LIFE_POWER（Buff，Counter）：出牌 hook 时触发 OstyCmd.Summon
  （Amount）——宠物召唤触发由宿主卡决定。
- BURROWED_POWER（钻地，Buff，Single）：持有者不可被选中/命中
  （ShouldAllowHitting 对持有者 false）；持有者格挡被击破时，持有者被
  击晕进入眩晕招式并移除 Burrowed；移除时持有者失去全部格挡
  （999999999）。
- ASLEEP_POWER（沉睡，Buff，Counter）：持有者沉睡——若受到未格挡伤害
  != 0，立即醒来（移除自身镀甲（如有）、击晕自己进入 WakeUpMove、移除
  Asleep）。持有者阵营回合结束时 Asleep -1 层；归 0 时通过 WakeUpMove
  醒来。Asleep <= 1 的回合结束时移除其镀甲。
- SLUMBER_POWER（Buff，Counter）：受到未格挡伤害时 -1 层，且持有者阵营
  回合结束时 -1 层；归 0 时通过 WakeUpMove 醒来（沉睡甲虫）。
- PAINFUL_STABS_POWER（Buff，Counter）：持有者攻击对玩家造成未格挡伤害
  时，对该玩家施加 Wound 状态牌（逐次命中逻辑见 AfterAttack；持有者
  死亡后 power 与生物按移除规则保留）。
- ESCAPE_ARTIST_POWER（Buff，Counter）：逃跑倒计时视觉——持有者阵营
  回合结束时 Amount > 1 则 -1 层；Amount == 1 时开始脉冲（ThievingHopper
  即将逃跑；逃跑动作由怪物招式执行）。
- BATTLEWORN_DUMMY_TIME_LIMIT_POWER（Buff，Counter）：持有者阵营回合
  结束时 -1 层；归 1 时木偶逃脱（事件遭遇逻辑）。
- SANDPIT_POWER（沙坑，Buff，Counter）：The Insatiable 场地状态——敌方
  阵营回合开始（late）时 -1 层；生物站位随 Amount 更新；关键层数时通过
  击杀逻辑结算战斗。
- HATCH_POWER（Buff，Counter）：持有者阵营回合结束时 -1 层（孵化计时；
  孵化动作由怪物/遗物宿主执行）。
- FAN_OF_KNIVES_POWER / PARRY_POWER / SEEKING_EDGE_POWER / THE_HUNT_POWER /
  THIEVERY_POWER / ACCELERANT_POWER：惰性标记 power——自身无 hook，由
  特定卡牌查询（Shiv / SovereignBlade / TheHunt 成功标记 / 偷窃逻辑），
  Accelerant 例外（参与毒触发次数计算）。

## 临时属性 power（子类；持有者阵营回合结束时回退）

全部托管于抽象类 `TemporaryStrengthPower` / `TemporaryDexterityPower` /
`TemporaryFocusPower`：施加时授予 ±Amount 对应基础属性；持有者阵营回合
结束时等量回退。授予为正时 Type 显示 Buff，为负时显示 Debuff。

- TEMPORARY_STRENGTH_POWER 家族：TEMPORARY_STRENGTH_POWER、
  FLEX_POTION_POWER、COORDINATE_POWER、CRUSH_UNDER_POWER、
  DARK_SHACKLES_POWER、DYING_STAR_POWER、ENFEEBLING_TOUCH_POWER、
  FEEDING_FRENZY_POWER、MANGLE_POWER、PIERCING_WAIL_POWER、
  REPTILE_TRINKET_POWER——临时 ±力量（Amount），回合结束回退。
- TEMPORARY_DEXTERITY_POWER 家族：TEMPORARY_DEXTERITY_POWER、
  ANTICIPATE_POWER、HELICAL_DART_POWER、SPEED_POTION_POWER——临时 ±敏捷
  （Amount），回合结束回退。
- TEMPORARY_FOCUS_POWER 家族：TEMPORARY_FOCUS_POWER、
  FOCUSED_STRIKE_POWER、HOTFIX_POWER、SYNCHRONIZE_POWER——临时 ±专注
  （Amount），回合结束回退。

## 角色套牌 / 卡牌宿主 power

- DEMON_FORM_POWER（恶魔形态，Buff，Counter）：持有者阵营回合开始时
  获得 +Amount STRENGTH_POWER。
- DARK_EMBRACE_POWER（黑暗之拥，Buff，Counter）：持有者的牌被消耗
  （Exhaust）时抽 Amount 张牌；虚无触发的消耗在持有者阵营回合结束时
  批量结算（Amount × 虚无触发次数）。
- ENRAGE_POWER（暴怒，Buff，Counter）：任何人打出技能牌时，持有者获得
  +Amount STRENGTH。
- RUPTURE_POWER（破灭，Buff，Counter）：持有者在本方阵营回合内受到来自
  卡牌来源的未格挡伤害时，该卡牌的结算为持有者施加 +Amount STRENGTH
  （按卡追踪）。
- FLAME_BARRIER_POWER（火焰屏障，Buff，Counter）：持有者被攻击命中时，
  攻击者受到 Amount 点非攻击伤害。在对方阵营回合结束时移除（非持有者
  回合）。
- WRAITH_FORM_POWER（幽灵形态，Debuff，Counter）：持有者阵营回合开始时
  获得 -Amount DEXTERITY_POWER。
- BIASED_COGNITION_POWER（偏见认知，Debuff，Counter）：持有者阵营回合
  开始时获得 -Amount FOCUS_POWER。
- BURST_POWER（爆发，Buff，Counter）：持有者接下来 Amount 次技能牌打出
  计为 2 次（ModifyCardPlayCount +1）；每打出 1 张技能牌消耗 1 层；
  持有者阵营回合结束时移除。
- DUPLICATION_POWER（复制，Buff，Counter）：持有者接下来 Amount 次任意
  卡牌打出计为 2 次；每打出 1 张牌消耗 1 层；持有者阵营回合结束时移除。
- ONE_TWO_PUNCH_POWER（Buff，Counter）：持有者接下来 Amount 次攻击牌
  打出计为 2 次；每打出 1 张攻击牌消耗 1 层；持有者阵营回合结束时移除。
- SIGNAL_BOOST_POWER（Buff，Counter）：持有者接下来 Amount 次 Power 牌
  打出计为 2 次；每打出 1 张 Power 牌消耗 1 层。
- ECHO_FORM_POWER（回响形态，Buff，Counter）：持有者每回合打出的第一张
  牌计为打出 2 次（ModifyCardPlayCount 对每回合首次系列 play 翻倍）。
- MAYHEM_POWER（混乱，Buff，Counter）：持有者预打出阶段开始时，从抽牌堆
  顶自动打出 Amount 张牌（不消耗）。
- STAMPEDE_POWER（Buff，Counter）：持有者自动后打出阶段时，从手牌自动
  打出 Amount 张攻击牌。
- HELLRAISER_POWER（Buff，Single）：持有者抽到带 Strike 标签的牌时可
  自动打出（无限自动打出上限 9，附带额外 VFX）；数据在持有者阵营回合
  结束时重置。
- PANACHE_POWER（Buff，Counter，实例化）：持有者每打出第 5 张牌，对所有
  可命中敌人造成 Amount 点非攻击伤害（`CardsLeft` 初始 5，首张后递减，
  触发及回合结束时重置为 5）。
- WITHERING_PRESENCE_POWER（Buff，Counter）：目标玩家每打出第 6 张牌，
  其手牌加入 1 张 Wither（`CardsLeft` 6 → 0 后加入）。
- ITERATION_POWER（Buff，Counter）：持有者每回合首次抽到状态牌时抽
  Amount 张牌（AfterCardDrawn，门控由宿主决定）。
- PAGESTORM_POWER（Buff，Counter）：持有者每当抽到虚无（Ethereal）牌，
  额外抽 Amount 张。
- VICIOUS_POWER（Buff，Counter）：持有者每当对他人施加 VULNERABLE_POWER
  （数值 > 0），抽 Amount 张牌。
- SWORD_SAGE_POWER（Buff，Counter）：为 Sovereign Blade 系卡牌添加 Amount
  次重放计数（BaseReplayCount）；power 移除时回退。
- MASTER_PLANNER_POWER（Buff，Single）：持有者打出技能牌后，该牌获得
  Sly 关键词。
- IMPROVEMENT_POWER（Buff，Counter）：战斗结束时，随机升级持有者牌库中
  Amount 张可升级卡牌。
- HEIST_POWER（Buff，Counter）：持有者（窃贼）在结算前死亡时，被偷的
  金币奖励（Amount）返还给 base.Target 玩家。
- RETAIN_HAND_POWER（Buff，Counter）：持有者回合结束时手牌不被弃置
  （ShouldFlush false）；持有者阵营回合结束时 -1 层。
- REBOUND_POWER（Buff，Counter）：打出牌的结算牌堆/位置被修改（按卡面
  文案回手等）；持有者阵营回合结束时 -1 层。
- ARSENAL_POWER（Buff，Counter）：战斗生成卡牌时施加 +Amount STRENGTH
  （由生成效果宿主触发）。
- STRATAGEM_POWER（Buff，Counter）：洗牌时按选择偏好将抽牌堆中的牌移入
  手牌（选择逻辑由宿主决定）。
- NOSTALGIA_POWER（Buff，Counter）：修改打出牌的结算牌堆/位置（按宿主
  卡面文案）。
- WELL_LAID_PLANS_POWER（Buff，Counter）：回合结束手牌弃置时的选择逻辑
  （保留手牌；BeforeFlushLate）。
- FORBIDDEN_GRIMOIRE_POWER / ROYALTIES_POWER / THE_SEALED_THRONE_POWER：
  战斗结束 / 出牌前宿主逻辑——见宿主卡面文案。
- BLACK_HOLE_POWER（Buff，Counter）：持有者玩家在卡牌上花费星辰（系列
  最后一张）或获得星辰时，对所有可命中敌人造成伤害（数值由
  DynamicVars 宿主设定）。
- CALAMITY_POWER（Buff，Counter）：持有者打出攻击牌后，向其手牌加入
  Amount 张随机职业池卡牌（生成逻辑由宿主决定）。
- CALL_OF_THE_VOID_POWER（Buff，Counter）：持有者手牌抽取前，向其手牌
  加入 Distinct 卡（并附加关键词）——宿主驱动的牌组污染。
- CREATIVE_AI_POWER（Buff，Counter）：持有者手牌抽取前，加入 Amount 张
  不重复的 Power 牌。
- FOREGONE_CONCLUSION_POWER（Buff，Counter）：持有者手牌抽取前，必要时
  洗牌并将选中的抽牌堆卡牌移入手牌。
- HELLO_WORLD_POWER（Buff，Counter）：持有者手牌抽取前
  （AmountOnTurnStart >= 1），加入不重复的已解锁卡牌。
- INFINITE_BLADES_POWER（Buff，Counter）：持有者手牌抽取前，在手牌生成
  Amount 张 Shiv。
- NIGHTMARE_POWER（噩梦，Buff，Counter）：持有者手牌抽取前，向手牌加入
  Amount 张所选牌的复制（复制体清除减益附着）。
- SENTRY_MODE_POWER（Buff，Counter）：持有者手牌抽取前，向手牌加入
  Amount 张 SweepingGaze。
- SPECTRUM_SHIFT_POWER（Buff，Counter）：持有者手牌抽取前，加入 Amount
  张不重复的无色池卡牌。
- GRAVITY_POWER（Buff，Counter）：持有者每打出一张牌，对所有可命中敌人
  造成 Amount 点非攻击伤害；持有者阵营回合结束时移除。
- SERPENT_FORM_POWER（Buff，Counter）：持有者每打出一张牌，对一名随机
  敌人造成 Amount 点非攻击伤害（按打出时记录的数值）。
- STORM_POWER（Buff，Counter）：持有者每打出一张 Power 牌，引导 Amount
  个闪电球。
- SUBROUTINE_POWER（Buff，Counter）：Power 牌打出追踪——触发逻辑由宿主
  卡决定（见卡面文案）。
- MONOLOGUE_POWER（Buff，Counter）：出牌力量引擎——追踪 StrengthApplied，
  按打出牌数施加/回退 STRENGTH（由宿主卡驱动；显示层数为累积力量）。
- THE_BOMB_POWER（炸弹，Buff，Counter，实例化）：持有者阵营回合结束时
  Amount > 1 则 -1 层；Amount <= 1 时对所有可命中敌人造成
  DynamicVars.Damage（默认 DamageVar 40，非攻击）伤害，随后移除。
- HIGH_VOLTAGE_POWER（Buff，Counter）：持有者阵营回合结束时获得
  +Amount STRENGTH_POWER。
- THUNDER_POWER（Buff，Counter）：持有者玩家激发闪电球时，对激发目标
  造成 Amount 点非攻击伤害。
- NECRO_MASTERY_POWER（Buff，Counter）：持有者的 Osty 宠物失去 HP 时，
  对所有可命中敌人造成（失去 HP × Amount）点不可格挡、非攻击伤害。
- HAUNT_POWER（Buff，Counter）：持有者打出 Soul 卡后，对随机敌人造成
  伤害（数值由宿主决定）。
- HAMMER_TIME_POWER（Buff，Single）：其他玩家锻造时，其余存活玩家同样
  锻造该数量（锤击联动）。
- FURNACE_POWER（Buff，Counter）：持有者阵营回合开始时锻造 Amount 次
  （通过锻造逻辑升级 Amount 张牌）。
- 其他卡牌宿主 power：触发与数值以宿主卡面为准。

## 其他怪物/精英 power

- MINION_POWER：见核心战斗状态。
- TERRITORIAL_POWER（领域，Buff，Counter）：持有者阵营回合结束时获得
  +Amount STRENGTH_POWER。
- RITUAL_POWER：见核心战斗状态。
- CURL_UP_POWER（Buff，Counter）：持有者将受到来自新卡牌来源的攻击伤害
  时蜷缩——获得格挡（数值由宿主设定），每张来袭卡触发一次；数据通过
  出牌追踪重置（巨型虱）。
- PLOW_POWER（Debuff，Counter）：持有者在 CurrentHp <= Amount 时受到
  未格挡伤害，则被击晕（decomp 清除持有者身上 TemporaryStrengthPower
  实例；击晕逻辑由怪物宿主执行）。
- SHRIEK_POWER（Debuff，Counter，可为负）：持有者在 CurrentHp <= Amount
  时受到未格挡伤害，则被击晕进入 TerrorEel 恐惧状态并自移除该 power。
- IMBALANCED_POWER（Debuff，Single）：持有者的攻击被完全格挡时被击晕
  （BowlbugRock 改为设置 IsOffBalance）。
- MONARCHS_GAZE_POWER（Buff，Counter）：持有者的攻击命中时，对目标施加
  Amount 层 MONARCHS_GAZE_STRENGTH_DOWN_POWER（力量削减引擎在目标上）。
- MONARCHS_GAZE_STRENGTH_DOWN_POWER（Debuff，Counter）：由 MonarchsGaze
  施加的力量削减标记；配套减益逻辑由君主卡牌宿主。
- SKITTISH_POWER（Buff，Counter）：持有者本回合未获得过格挡且受到卡牌
  来源的攻击伤害时，获得 Amount 格挡（每回合一次标记；标记在对方阵营
  回合结束时重置）。
- CONSUMING_SHADOW_POWER（Buff，Counter）：持有者阵营回合结束时，若
  持有者玩家有充能球，将最后一个球激发 Amount 次。
- BACK_ATTACK_LEFT_POWER / BACK_ATTACK_RIGHT_POWER（Buff，Single）：
  惰性朝向标记，供 SURROUNDED_POWER 判定使用。

## 非 power

- BURNING_BLOOD 是遗物（铁甲战士），不是 power——见 relics_zh.md。
