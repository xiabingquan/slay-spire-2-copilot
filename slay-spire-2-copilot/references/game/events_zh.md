# 事件

事件参考。内部名称来自游戏源码提取（STS2-Agent 事件索引，共 69 个；
AncientEventModel 标记远古/Neow 系列）；括号内为简中译名（来源：
slaythespire2.net/zh-CN/event，正式版 v0.107.1 共 57 个事件）。实战、
遗物互动与社区笔记中已知的行为附在对应条目——多数事件的奖励随 HP/遗物/
多人状态变化，对局中以游戏内界面为准。

- ABYSSAL_BATHS（深渊浴场）：水底码头章节事件。
- AMALGAMATOR（熔合者）：虫巢章节事件。
- AROMA_OF_CHAOS（混沌芳香）："LET_GO" 选项打开牌组变形——任选一张牌库卡随机变形（实测 STRIKE -> POMMEL_STRIKE）。
- BATTLEWORN_DUMMY（战痕累累的训练假人）：荣光之殿章节事件。
- BRAIN_LEECH（脑蛭）：通用事件；提供卡牌相关分支（某分支经非 NCardReward 界面加牌——见 cards_zh.md 界面备注）。
- BUGSLAYER（害虫杀手）：虫巢章节事件。
- BYRDONIS_NEST（多尼斯异鸟巢）：蔓生之地章节；授予 BYRDONIS_EGG 状态牌（不可打出；在牌库中时休息点出现 HATCH；商店移除目标）。
- COLORFUL_PHILOSOPHERS（色彩哲学家）：虫巢章节事件。
- COLOSSAL_FLOWER（巨大花卉）：虫巢章节事件。
- CRYSTAL_SPHERE（水晶球）：通用事件；水晶球界面系（牌组修改流程；服务端经 CrystalSphereScreenHandler 支持）。
- DARV：远古系事件（AncientEventModel；中文名待核实）。
- DENSE_VEGETATION（茂密的植被）：蔓生之地章节事件。
- DOLL_ROOM（玩偶室）：通用事件。
- DOORS_OF_LIGHT_AND_DARK（光与暗的门扉）：水底码头章节事件。
- DROWNING_BEACON（淹水灯塔）：水底码头章节事件。
- ENDLESS_CONVEYOR（无尽传送带）：水底码头章节事件。
- FAKE_MERCHANT：NFakeMerchant 流程——54g 出售 FAKE_SNECKO_EYE（陷阱遗物；实测手牌费用随机化；中文名待核实）。
- FIELD_OF_MAN_SIZED_HOLES（人形洞穴之地）：虫巢章节；沙坑系——FRANTIC_ESCAPE 卡牌产物（每次使用费用递增；+1 沙坑）。
- GRAVE_OF_THE_FORGOTTEN（遗忘之墓）：荣光之殿章节事件。
- HUNGRY_FOR_MUSHROOMS（蘑菇饥渴）：荣光之殿章节事件。
- INFESTED_AUTOMATON（被寄生的自动机械）：虫巢章节事件。
- JUNGLE_MAZE_ADVENTURE（丛林迷宫奇遇）：蔓生之地章节；分支已实测——SOLO_QUEST 约 -18 HP 换约 +147g；JOIN_FORCES 零 HP 成本约 +63g（2026-09-17 实测 63 HP 下 JOIN 实付 +50g）。中低血量选 JOIN，仅过 60 HP 选 SOLO；boss 临近且金币无商店出口时优先 JOIN。
- LOST_WISP（迷失鬼火）：虫巢章节；"claim" 选项授予 LOST_WISP 遗物（效果待观察）。
- LUMINOUS_CHOIR（冷光合唱团）：蔓生之地章节事件；2026-09-17 实测——探入菌肉 REACH_INTO_THE_FLESH 自选移除 2 张卡牌并向牌组加入诅咒 SPORE_MIND（1 费，消耗）；供奉 OFFER_TRIBUTE 花费 149 金币（不足则锁定）获得随机遗物。移除界面为标准 2 选网格。
- MORPHIC_GROVE（变形灵林谷）：蔓生之地章节事件。
- NEOW（尼奥）：远古系开局赐福（Neow's Bones/Talisman/Torment 遗物家族——译名见 relics_zh.md）。
- 章节起始远古房（实战漏走 2026-09-17，用户确认）：每章地图最低一排是 Ancient/尼奥系赐福房——Act 2 起点 (0,3)=Ancient，先古移民选项含恢复血量（用户确认是非常强的 buff）。章节切换后 bridge 直接落在第 1 排地图，且 available_map_points 历史上不列起始房——agent 永久跳过了赐福（地图不能回头）。规则：先处理 `run.act_start_room`（visited=false 且 is_boon_room=true）——最先 map_select 该点；state 会把它重新注入 available_map_points 头部，紧凑视图会打印 ACT-START BOON ROOM UNVISITED 警告。
- NONUPEIPE：远古系事件（中文名待核实）。
- OROBAS：远古系事件（Touch of Orobas=欧洛巴斯之触 遗物家族——将初始遗物替换为远古版）。
- PAEL：远古系事件（Pael's 系列遗物中文名均以"佩尔之…"开头——见 relics_zh.md）。
- POTION_COURIER（药水快递员）：通用事件（药水供给）。
- PUNCH_OFF（重拳出击）：水底码头章节事件。
- RANWID_THE_ELDER（长者兰伟德）：通用事件。
- REFLECTIONS（镜中倒影）：荣光之殿章节事件。
- RELIC_TRADER（遗物交换商）：通用事件（遗物交易）。
- ROOM_FULL_OF_CHEESE（满屋芝士）：通用事件（The Chosen Cheese=天选芝士 遗物——战斗结束 +1 最大 HP）。
- ROUND_TEA_PARTY（圆桌茶会）：荣光之殿章节事件（茶具/靠垫休息协同家族）。
- SAPPHIRE_SEED（蓝宝石种子）：蔓生之地章节；seed/巢穴系——BYRDONIS_EGG 类状态产物。
- SELF_HELP_BOOK（自助指南）：通用事件。
- SLIPPERY_BRIDGE（滑脚木桥）：通用事件。
- SPIRALING_WHIRLPOOL（螺旋漩涡）：水底码头章节事件。
- SPIRIT_GRAFTER（灵魂嫁接者）：虫巢章节事件。
- STONE_OF_ALL_TIME（永恒之石）：通用事件。
- SUNKEN_STATUE（沉没雕像）：蔓生之地/水底码头两章均会出现。
- SUNKEN_TREASURY（淹水金库）：水底码头章节事件（宝物/战利品供给）。
- SYMBIOTE（共生体）：通用事件。
- TABLET_OF_TRUTH（真理石板）：蔓生之地章节事件。
- TANX：远古系事件（Tanx's Whistle=坦克斯的哨子 遗物——加入 Whistle 卡）。
- TEA_MASTER（茶艺大师）：通用事件。
- TEZCATARA：远古系事件（Nutritious Soup=营养汤 附魔家族——Strike 附 Tezcatara's Ember；中文名待核实）。
- THE_ARCHITECT：通用事件（中文名待核实）。
- THE_FUTURE_OF_POTIONS（药水的未来？）：通用事件（药水选择系）。
- THE_LANTERN_KEY（灯火钥匙）：虫巢章节；分支已实测——RETURN_THE_KEY 立得约 +100 金币无战斗；KEEP_THE_KEY 触发骑士战获取钥匙卡。低血量选 RETURN，健康时选 KEEP。Lantern Key 任务卡解锁下一章节特殊事件。
- THE_LEGENDS_WERE_TRUE（传说是真的）：通用事件。
- THIS_OR_THAT（这个还是那个？）：通用事件；分支已实测——"ORNATE" 选项授予 MOLTEN_EGG（攻击牌奖励到手即升级）。
- TINKER_TIME（打造时间）：荣光之殿章节事件。
- TRASH_HEAP（垃圾堆）：水底码头章节事件。
- TRIAL（审判）：荣光之殿章节事件。
- UNREST_SITE（无休之处）：蔓生之地章节；休息点变体事件（非标准休息选项）。
- VAKUU：远古系事件（Whispering Earring=低语耳环 遗物——Vakuu 代打第一回合；中文名待核实）。
- WAR_HISTORIAN_REPY（战史学家付袭）：通用事件。
- WATERLOGGED_SCRIPTORIUM（水漫缮写室）：水底码头章节事件。
- WELCOME_TO_WONGOS（欢迎来到旺购百货）：通用事件；已实测——300g 神秘箱授予 WONGO'S_MYSTERY_TICKET（5 场战斗后获得 3 件随机遗物）；Wongo 感谢徽章毫无用处。
- WELLSPRING（泉水）：蔓生之地章节事件。
- WHISPERING_HOLLOW（低语空谷）：蔓生之地章节事件；2026-09-17 实测——交换金币 GOLD 约花 36-50 金币得 2 瓶随机药水（实测缚魂药水 + 迅捷药水，实付 36g——beta 改价，攻略多记 50）；拥抱树木 HUG 失去 9 HP，随机变形一张卡牌。
- WOOD_CARVINGS（木雕）：蔓生之地章节事件。
- ZEN_WEAVER（修禅织网者）：虫巢章节事件。

## 事件处理备注

- state 中 screen="event" 时 screen_detail.options 列出选项（kind=event_option）；用 act choose index 选择；锁定选项在游戏界面显示 IsLocked。
- 事件奖励可能变形卡牌、授予遗物/药水/金币或触发战斗——选择前读界面文本；本索引用于识别，不是穷尽式选择攻略。
- 远古系事件（DARV、NEOW、NONUPEIPE、OROBAS、PAEL、TANX、TEZCATARA、VAKUU）共享远古遗物/货币家族。
