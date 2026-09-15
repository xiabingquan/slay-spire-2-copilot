# 角色

五个可玩角色。初始配置与游戏数据（本机 v0.107.1）及社区数据库交叉核对；
牌池数量来自 spire-codex.com。

- IRONCLAD（铁甲战士）— 80 HP。初始遗物：BURNING_BLOOD（战斗结束回复
  6 HP）。初始牌组：Strike ×5、Defend ×4、Bash。牌池约 87 张。
  流派：力量叠加、重型单击（Bludgeon）、格挡转伤害（Body Slam、
  Juggernaut）、自伤引擎（Bloodletting、Offering、Hemokinesis）。实战
  关键牌：Demon Form、Whirlwind、Uppercut、Blood Wall、Second Wind。
- SILENT（寂静）— 70 HP。初始遗物：RING_OF_THE_SNAKE（战斗开始抽 2）。
  初始牌组：Strike ×5、Defend ×5、Neutralize、Survivor。牌池约 88 张。
  特色关键词：Sly——可按费用正常打出，也可被弃置以免费自动触发效果。
  流派：中毒（Noxious Fumes、Deadly Poison、Poisoned Stab）、刀 Shiv
  （0 费攻击，Blade Dance、Infinite Blades）、弃牌协同（Calculated
  Gamble、Reflex、Tactician、Tough Bandages、Tingsha）。
- DEFECT（缺陷）— 70 HP。初始遗物：CRACKED_CORE（战斗开始引导 1 个
  闪电）。初始牌组：Strike ×4、Defend ×4、Zap、Dualcast。牌池约 88 张。
  机制：充能球 Orb——将 Lightning / Frost / Plasma / Dark 引导入球槽；
  每球有被动触发与离场激发两种效果；Focus 提升球输出（Data Disk：战斗
  开始 +1 Focus）。流派：叠球（Capacitor、Loop、Multi-Cast）、零费/爪、
  能力牌风暴（Creative AI、Echo Form）。
- NECROBINDER（死灵束缚者）— 66 HP。初始遗物：BOUND_PHYLACTERY（回合
  开始 Summon 1）。初始牌组：Strike ×4、Defend ×4、Bodyguard、Unleash。
  牌池约 88 张。机制：骨片 token、召唤物（Minion 关键词——召唤生物
  参战）、Doom（敌方叠加死兆；遗物 Undying Sigil 与之互动）、献祭循环
  （Minion Sacrifice、Death's Door）。
- REGENT（摄政王）— 75 HP。初始遗物：DIVINE_RIGHT（战斗开始获得 3 点
  星星 ★）。初始牌组：Strike ×4、Defend ×4、Falling Star、Venerate。
  牌池约 88 张。机制：星星 ★ 作为战斗资源由敕令类卡牌消耗；庭臣/
  Minion 收益（Vitruvian Minion 使含 Minion 的卡伤害与格挡翻倍）、
  Forge 关键词（Fencing Manual：战斗开始 Forge 10）、威望成长。

共通流程：每局 3 个章节，分支地图（战斗 / 精英 / boss / 事件 / 商店 /
休息 / 宝箱）；战斗后卡牌奖励；开局 Neow 赐福；休息点提供 Rest 与 Smith
及角色专属选项。state 快照中角色字段使用 id：IRONCLAD、SILENT、DEFECT、
NECROBINDER、REGENT。
