# 状态与减益（afflictions）

卡牌绑定减益、状态牌与诅咒牌。每条均对照反编译类核实：affliction 在
`MegaCrit.Sts2.Core.Models.Afflictions.*`，卡牌在
`MegaCrit.Sts2.Core.Models.Cards.*`，逻辑宿主在
`MegaCrit.Sts2.Core.Models.Powers.*`。「虚无（Ethereal）」= 回合结束仍在
手牌则消失。「不可打出」= 无法打出。

## 卡牌绑定减益（附着在牌库卡牌上；逻辑在宿主 power 中）

- BOUND（束缚）：宿主 = CHAINS_OF_BINDING_POWER——每回合最多 Amount 张
  被抽到的牌附加 Bound；每回合只能打出 1 张 Bound 牌；你的回合结束时
  全部清除。
- ENTANGLED（缠绕）：宿主 = TANGLED_POWER——攻击牌被附加 Entangled；
  Entangled 牌费用 +Amount 能量；你的回合结束时清除。
- GALVANIZED（电镀，可叠加）：宿主 = GALVANIC_POWER——Power 牌被附加
  Galvanized（Amount）；打出 Galvanized 牌时其拥有者受到 Amount 点
  非攻击伤害。
- HEXED（诅咒）：宿主 = HEX_POWER——power 存在期间 Hexed 牌获得虚无
  关键词；施加者死亡或 power 移除时清除。
- RINGING（耳鸣）：宿主 = RINGING_POWER——本回合只要打出过任意一张牌，
  Ringing 牌即不可打出；你的回合结束时清除。
- SMOG（烟雾）：宿主 = SMOGGY_POWER——你打出技能牌后技能牌被附加 Smog；
  power 存在期间 Smog 牌不可打出；你的回合结束时清除。
- TAINTED（污染，可叠加，仅技能牌）：宿主 = TAINTED_POWER——对 power
  持有者的攻击伤害 +Amount；该 power 在敌方阵营回合结束时移除。
  （VitalSparkPower 给玩家技能牌附加 Tainted，并在打出 Tainted 牌时施加
  TaintedPower。）

## 状态牌

- SLIMED（黏液，Status）：费用 1；打出时抽 1 张牌，然后消耗（Exhaust）。
  （PersonalHivePower 将 Dazed 牌加入攻击者的抽牌堆。）
- DAZED（眩晕，Status）：不可打出，虚无——回合结束未打出则消失。
- WOUND（创伤，Status）：不可打出；纯牌库堵塞物。3 张 Wound 在手过回合末 HP 零损——无 Infection 级回合末税；「纯堵塞物」定性成立。
- TOXIC（剧毒，Status）：费用 1，消耗；回合结束仍在手牌时，对拥有者
  造成 5 点非攻击伤害（DamageVar 5）。
- DISINTEGRATION（崩解，Status，KnowledgeDemon 选项）：费用 -1，战斗中
  不可生成；被选择时施加 DISINTEGRATION_POWER 6——你的回合结束时失去
  6 HP（非攻击来源），power 存续期间持续生效。
- MIND_ROT（脑蚀，Status，KnowledgeDemon 选项）：费用 -1；被选择时施加
  MIND_ROT_POWER 1——每回合少抽 1 张牌。
- SLOTH（怠惰，Status，KnowledgeDemon 选项）：费用 -1；被选择时施加
  SLOTH_POWER 3——每回合最多打出 3 张牌（计数回合开始重置；显示层数
  为本回合已打出牌数）。
- WASTE_AWAY（衰朽，Status，KnowledgeDemon 选项）：费用 -1；被选择时
  施加 WASTE_AWAY_POWER 1——最大能量 -1。

## 诅咒牌

- ASCENDERS_BANE（天阶诅咒）：不可打出，虚无，永恒（Eternal）——无法
  正常移除。
- CURSE_OF_THE_BELL（钟之诅咒）：不可打出，永恒。
- CLUMSY（笨拙）：不可打出，虚无。
- INJURY（损伤）：不可打出。
- DECAY（腐化）：不可打出；回合结束仍在手牌时，对拥有者造成 2 点
  非攻击伤害（DamageVar 2）。
- DOUBT（猜疑）：不可打出；回合结束仍在手牌时，对拥有者施加 1 层
  WEAK_POWER（若其原本没有虚弱，该次施加跳过下一次持续时间递减）。
- REGRET（悔恨）：不可打出；回合结束时若在手牌，对拥有者造成不可格挡
  的非攻击伤害，数值 = 回合结束时的手牌数。
- NORMALITY（常态）：不可打出；它在你手牌中时，你本回合打出第 3 张牌后
  不能再打出任何牌（每回合上限 3 张）。

## 状态牌协同收益卡

- COMPACT（压缩，Defect）：手牌中的状态牌变为 Fuel 并获得格挡（卡面
  文案）。
- FLAK_CANNON（散射炮）：消耗所有状态牌，每张造成伤害。
- ITERATION（迭代）：ITERATION_POWER——每回合首次抽到状态牌时额外抽牌。
- ROCKET_PUNCH（火箭飞拳）：生成状态牌时变为免费。
- SMOKESTACK（烟囱）：SMOKESTACK_POWER——生成状态牌时对所有敌人造成伤害。
- TRASH_TO_TREASURE（化废为宝）：TRASH_TO_TREASURE_POWER——生成状态牌时
  引导随机充能球。

## 相关 power（交叉引用 powers_zh.md）

- Chains/Ringing/Tangled/Galvanic/Hex/Smoggy/Tainted 宿主 power，以及
  DISINTEGRATION_POWER、MIND_ROT_POWER、SLOTH_POWER、WASTE_AWAY_POWER、
  NO_DRAW_POWER、NO_ENERGY_GAIN_POWER——层数与 hook 细节见
  powers_zh.md。
