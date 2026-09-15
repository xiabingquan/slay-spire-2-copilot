# 角色

五个可玩角色。初始配置来自游戏源码提取（STS2-Agent characters 索引，
对 v0.107.x 构建具权威性）；与社区数据库（spire-codex、IGN、mobalytics）
交叉核对。所有角色初始金币 99。仅测试用 id：Deprived、RandomCharacter
（正常对局不可玩）。

- IRONCLAD（铁甲战士）— 80 HP，男性。初始遗物：BURNING_BLOOD（战斗结束
  回复 6 HP；升级 Black Blood 回复 12）。初始牌组：Strike ×5、Defend ×4、
  Bash。牌池约 87（攻击 38 / 技能 28 / 能力 21）。流派：力量叠加、重型
  单击（Bludgeon）、格挡转伤害（Body Slam、Juggernaut）、自伤引擎
  （Bloodletting、Offering、Hemokinesis）。核心牌：Demon Form、Whirlwind、
  Uppercut、Blood Wall、Second Wind、Corruption（Ancient）。
- SILENT（寂静）— 70 HP，女性。初始遗物：RING_OF_THE_SNAKE（战斗开始
  抽 2）。初始牌组：Strike ×5、Defend ×5、Neutralize、Survivor。牌池约
  88-89（攻击 28 / 技能 42 / 能力 19）。特色关键词：Sly——可按能量费用
  正常打出，也可弃置以免费触发效果。流派：中毒（Noxious Fumes、
  Deadly Poison、Accelerant、Envenom）、刀 Shiv（Blade Dance、
  Infinite Blades、Accuracy、Fan of Knives）、弃牌协同（Calculated
  Gamble、Tactician、Tough Bandages、Tingsha）。
- DEFECT（缺陷）— 75 HP（游戏源码；部分社区站记 70），中性。初始遗物：
  CRACKED_CORE（战斗开始引导 1 个闪电球）。初始牌组：Strike ×4、
  Defend ×4、Zap、Dualcast。牌池约 88。在死灵束缚者之后解锁。机制：
  充能球 Orb——引导 Lightning / Frost / Plasma / Dark 入球槽；被动触发、
  离场激发；Focus 提升球输出（Defragment、Data Disk；Biased Cognition
  强力但衰减）。流派：叠球（Capacitor、Loop、Multi-Cast、Glacier）、
  零费 Claw、能力风暴（Creative AI、Echo Form、Machine Learning）。
- NECROBINDER（死灵束缚者）— 66 HP，女性。初始遗物：BOUND_PHYLACTERY
  （回合开始 Summon 1）。初始牌组：Strike ×4、Defend ×4、Bodyguard、
  Unleash。牌池约 88。在摄政王之后解锁。机制：骨片、召唤（Minion
  关键词；伙伴 Osty 指挥大量卡牌）、Doom 叠加死兆（End of Days 在
  Doom ≥ HP 时击杀；遗物 Undying Sigil 与之互动）、献祭循环
  （Minion Sacrifice、Death's Door、Necro Mastery）。
- REGENT（摄政王）— 75 HP，男性。初始遗物：DIVINE_RIGHT（战斗开始获得
  3 点星星 ★）。初始牌组：Strike ×4、Defend ×4、Falling Star、Venerate。
  牌池约 88（按站头：攻击 33 / 技能 36 / 能力 19）。在寂静之后解锁。
  机制：星星 ★ 作为敕令类卡牌的战斗资源；Forge 关键词（Fencing
  Manual：Forge 10；Spoils of Battle；Hammer Time 与盟友共享 Forge）；
  庭臣/Minion 收益（Vitruvian Minion 使 Minion 卡伤害与格挡翻倍）；
  威望成长。

解锁链（游戏源码）：Silent 初始可用；REGENT 在 Silent 后解锁；
NECROBINDER 在 Regent 后；DEFECT 在 Necrobinder 后。（Ironclad 与
Silent 为初始阵容——全新存档的确切状态以游戏内为准。）

共通流程：每局 3 个章节，分支地图（战斗 / 精英 / boss / 事件 / 商店 /
休息 / 宝箱）；战斗后卡牌奖励；开局 Neow 赐福；休息点提供 Rest 与 Smith
及角色专属选项。state 快照中角色字段使用 id：IRONCLAD、SILENT、DEFECT、
NECROBINDER、REGENT。
