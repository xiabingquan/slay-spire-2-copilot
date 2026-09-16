# 角色

五个可玩角色；括号内为简中译名（来源：slaythespire2.net/zh-CN、
sts2.gg/zh）。初始配置来自游戏源码提取（STS2-Agent characters 索引，
对 v0.107.x 构建具权威性）；与社区数据库交叉核对。所有角色初始金币 99。
仅测试用 id：Deprived、RandomCharacter（正常对局不可玩）。

- IRONCLAD（铁甲战士）— 80 HP，男性。初始遗物：BURNING_BLOOD（燃烧之血，战斗结束回复 6 HP；升级 Black Blood=黑暗之血 回复 12）。初始牌组：Strike（打击）×5、Defend（防御）×4、Bash（痛击）。牌池约 87（攻击 38 / 技能 28 / 能力 21）。流派：力量叠加、重型单击（Bludgeon=重锤）、格挡转伤害（Body Slam=全身撞击、Juggernaut=势不可当）、自伤引擎（Bloodletting=放血、Offering=祭品、Hemokinesis=御血术）。核心牌：Demon Form=恶魔形态、Whirlwind=旋风斩、Uppercut=上勾拳、Blood Wall=血墙、Second Wind=重振精神、Corruption=腐化（Ancient）。
- SILENT（静默猎手）— 70 HP，女性。初始遗物：RING_OF_THE_SNAKE（蛇之戒指，战斗开始抽 2）。初始牌组：Strike×5、Defend×5、Neutralize=中和、Survivor=生存者。牌池约 88-89（攻击 28 / 技能 42 / 能力 19）。特色关键词：Sly——可按能量费用正常打出，也可弃置以免费触发效果。流派：中毒（Noxious Fumes=毒雾、Deadly Poison=致命毒药、Accelerant=触媒、Envenom=涂毒）、刀 Shiv=匕首（Blade Dance=刀刃之舞、Infinite Blades=无尽刀刃、Accuracy=精准、Fan of Knives=刀扇）、弃牌协同（Calculated Gamble=计算下注、Tactician=战术大师、Tough Bandages=结实绷带、Tingsha=铜钹）。
- DEFECT（故障机器人）— 75 HP（游戏源码；部分社区站记 70），中性。初始遗物：CRACKED_CORE（破损核心，战斗开始引导 1 个闪电球）。初始牌组：Strike×4、Defend×4、Zap=电击、Dualcast=双重释放。牌池约 88。在亡灵契约师之后解锁。机制：充能球 Orb——引导 Lightning / Frost / Plasma / Dark 入球槽；被动触发、离场激发；Focus（专注）提升球输出（Defragment=碎片整理、Data Disk=数据磁盘；Biased Cognition=偏差认知 强力但衰减）。流派：叠球（Capacitor=扩容、Loop=循环、Multi-Cast=多重释放、Glacier=冰川）、零费 Claw=爪击、能力风暴（Creative AI=创造性AI、Echo Form=回响形态、Machine Learning=机器学习）。
- NECROBINDER（亡灵契约师）— 66 HP，女性。初始遗物：BOUND_PHYLACTERY（缚魂命匣，回合开始 Summon 1）。初始牌组：Strike×4、Defend×4、Bodyguard=护卫、Unleash=出击。牌池约 88。在储君之后解锁。机制：骨片、召唤（Minion=仆从 关键词；伙伴 Osty=奥斯提 指挥大量卡牌）、Doom=末日 叠加死兆（End of Days=末日降临 在 Doom ≥ HP 时击杀；遗物 Undying Sigil=不死符文 与之互动）、献祭循环（Minion Sacrifice、Death's Door=死亡之门、Necro Mastery=亡灵精通）。
- REGENT（储君）— 75 HP，男性。初始遗物：DIVINE_RIGHT（天赋君权，战斗开始获得 3 点星星 ★）。初始牌组：Strike×4、Defend×4、Falling Star=陨星、Venerate=崇拜。牌池约 88（按站头：攻击 33 / 技能 36 / 能力 19）。在静默猎手之后解锁。机制：星星 ★ 作为敕令类卡牌的战斗资源；Forge 关键词（Fencing Manual=击剑指南：Forge 10；Spoils of Battle=战利品；Hammer Time=锤子时间 与盟友共享 Forge）；庭臣/仆从收益（Vitruvian Minion=维特鲁威仆从 使 Minion 卡伤害与格挡翻倍）；威望成长。

解锁链（游戏源码）：Silent 初始可用；REGENT 在 Silent 后解锁；NECROBINDER 在 Regent 后；DEFECT 在 Necrobinder 后。（Ironclad 与 Silent 为初始阵容——全新存档的确切状态以游戏内为准。）

共通流程：每局 3 个章节，分支地图（战斗 / 精英 / boss / 事件 / 商店 / 休息 / 宝箱）；战斗后卡牌奖励；开局 Neow（尼奥）赐福；休息点提供 Rest 与 Smith 及角色专属选项。state 快照中角色字段使用 id：IRONCLAD、SILENT、DEFECT、NECROBINDER、REGENT。
