# 卡牌

游玩中积累的静态卡牌参考。state 中的 can_play 标志永远是权威依据。

- STRIKE_IRONCLAD：1 费攻击，约 6 点伤害 + 力量；附魔/升级有加成。
- DEFEND_IRONCLAD：1 费，约 5 点格挡 + 敏捷。
- BASH：2 费，约 8-10 点伤害 + 2 层 VULNERABLE（升级约 10+）；核心易伤来源。
- BLOOD_WALL：2 费自身牌，约 16 格挡，消耗 2hp，同时对附近敌人造成约 8 点
  伤害。血量低于约 5hp 时绝不能打（hp 消耗会致死）。
- SHRUG_IT_OFF：1 费，8 格挡 + 抽 1。
- DISMANTLE：1 费攻击约 1 伤害 + 移除一个敌方 power/充能。
- THUNDERCLAP：1 费 AOE，对所有敌人约 4+力量伤害并各附 1 层 VULNERABLE；
  观察到可完全破除敌方格挡。
- UPPERCUT（升级）：2 费约 8-21 伤害 + WEAK + VULNERABLE。
- BLUDGEON：3 费，对单体 32+力量伤害（观察到 35-49）。Boss/精英杀手。
- WHIRLWIND（升级）：X 费 AOE 多段，随力量缩放（配合 DEMON_FORM 与能量遗物
  观察到总伤 27-81）。
- PERFECTED_STRIKE（升级）：伤害 + 每张牌组中 STRIKE 提供加成。
- SWORD_BOOMERANG（升级）：随机目标多段攻击，随力量缩放。
- DEMON_FORM（升级）：3 费能力牌，数回合内每回合 +力量——引擎牌，抽到即在
  第 1-2 回合打出。
- JUGGERNAUT：能力牌——获得格挡时造成伤害。
- IRON_WAVE：约 10 伤害 + 约 5-8 格挡的混合牌。
- SECOND_WIND：消耗手牌 -> 每张被消耗的牌给格挡。
- ARMAMENTS：5 格挡 + 升级一张手牌（本场战斗）。
- BATTLE_TRANCE：抽 3，本回合后不再抽牌。
- FLAME_BARRIER：格挡 + 临时荆棘 power。
- TWIN_STRIKE：2 段攻击；力量按段生效。
- BLOODLETTING / OFFERING：扣血换能量/抽牌——20hp 以下危险。
- FIGHT_ME：2 费攻击约 10 伤害；对玩家与目标双方赋予 STRENGTH。
- BREAKTHROUGH：1 费 AOE 对所有敌人约 9 伤害 + 自损 1hp。
- BURNING_PACT：1 费自身牌，消耗/抽牌引擎，无直接伤害。
- RAMPAGE：1 费攻击约 6 基础伤害，随打出次数递增。
- EXPECT_A_FIGHT / PYRE / STOMP / SPOILS_MAP / LANTERN_KEY / FRANTIC_ESCAPE：
  效果待观察。
- 事件 AROMA_OF_CHAOS 的 "LET_GO"：打开牌组变形——任选一张牌库卡，随机变形
  （观察到 STRIKE -> POMMEL_STRIKE）。

## 界面备注

- 药水栏满时奖励界面可能显示不可领取的按钮——点击无效；proceed 离开该界面。
- 多数 card_reward 界面有跳过按钮；NDeckCardSelectScreen 移除流程没有
  （必须选一张）。
