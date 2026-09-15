# 事件

事件参考。内部名称来自游戏源码提取（STS2-Agent 事件索引，共 69 个；
AncientEventModel 标记远古/Neow 系列）。实战、遗物互动与社区笔记中已知
的行为附在对应条目——多数事件的奖励随 HP/遗物/多人状态变化，对局中以
游戏内界面为准。

- ABYSSAL_BATHS：事件房遭遇（选项待实战观察）。
- AMALGAMATOR：事件房遭遇。
- AROMA_OF_CHAOS："LET_GO" 选项打开牌组变形——任选一张牌库卡随机变形
  （实测 STRIKE -> POMMEL_STRIKE）。
- BATTLEWORN_DUMMY：事件房遭遇。
- BRAIN_LEECH：提供卡牌相关分支（某分支经非 NCardReward 界面加牌——见
  cards_zh.md 界面备注）。
- BUGSLAYER：事件房遭遇。
- BYRDONIS_NEST：Sapphire seed/巢穴系——授予 BYRDONIS_EGG 状态牌
  （不可打出；在牌库中时休息点出现 HATCH；商店移除目标）。
- COLORFUL_PHILOSOPHERS：事件房遭遇。
- COLOSSAL_FLOWER：事件房遭遇。
- CRYSTAL_SPHERE：水晶球界面系（牌组修改流程；服务端经
  CrystalSphereScreenHandler 支持）。
- DARV：远古系事件（AncientEventModel）。
- DENSE_VEGETATION：事件房遭遇。
- DOLL_ROOM：事件房遭遇。
- DOORS_OF_LIGHT_AND_DARK：事件房遭遇。
- DROWNING_BEACON：事件房遭遇。
- ENDLESS_CONVEYOR：事件房遭遇。
- FAKE_MERCHANT：NFakeMerchant 流程——54g 出售 FAKE_SNECKO_EYE
  （陷阱遗物；实测手牌费用随机化）。
- FIELD_OF_MAN_SIZED_HOLES：沙坑系——FRANTIC_ESCAPE 卡牌产物
  （每次使用费用递增；+1 沙坑）。
- GRAVE_OF_THE_FORGOTTEN：事件房遭遇。
- HUNGRY_FOR_MUSHROOMS：事件房遭遇。
- INFESTED_AUTOMATON：事件房遭遇。
- JUNGLE_MAZE_ADVENTURE：分支已实测——SOLO_QUEST 约 -18 HP 换约 +147g；
  JOIN_FORCES 零 HP 成本约 +63g。中低血量选 JOIN，仅过 60 HP 选 SOLO。
- LOST_WISP："claim" 选项授予 LOST_WISP 遗物（效果待观察）。
- LUMINOUS_CHOIR：事件房遭遇。
- MORPHIC_GROVE：事件房遭遇。
- NEOW：远古系开局赐福（Neow's Fury/Bones/Talisman/Torment 遗物家族）。
- NONUPEIPE：远古系事件。
- OROBAS：远古系事件（Touch of Orobas 遗物家族——将初始遗物替换为远古版）。
- PAEL：远古系事件（Pael's Claw/Eye/Flesh/Growth/Horn/Legion/Tears/Tooth/
  Wing 遗物家族——见 relics_zh.md）。
- POTION_COURIER：事件房遭遇（药水供给）。
- PUNCH_OFF：事件房遭遇。
- RANWID_THE_ELDER：事件房遭遇。
- REFLECTIONS：事件房遭遇。
- RELIC_TRADER：事件房遭遇（遗物交易）。
- ROOM_FULL_OF_CHEESE：事件房遭遇（The Chosen Cheese 遗物家族——战斗
  结束 +1 最大 HP）。
- ROUND_TEA_PARTY：事件房遭遇（茶具/靠垫休息协同家族）。
- SAPPHIRE_SEED：seed/巢穴系——BYRDONIS_EGG 类状态产物。
- SELF_HELP_BOOK：事件房遭遇。
- SLIPPERY_BRIDGE：事件房遭遇。
- SPIRALING_WHIRLPOOL：事件房遭遇。
- SPIRIT_GRAFTER：事件房遭遇。
- STONE_OF_ALL_TIME：事件房遭遇。
- SUNKEN_STATUE：事件房遭遇。
- SUNKEN_TREASURY：事件房遭遇（宝物/战利品供给）。
- SYMBIOTE：事件房遭遇。
- TABLET_OF_TRUTH：事件房遭遇。
- TANX：远古系事件（Tanx's Whistle 遗物——加入 Whistle 卡）。
- TEA_MASTER：事件房遭遇。
- TEZCATARA：远古系事件（Nutritious Soup 附魔家族——Strike 附
  Tezcatara's Ember）。
- THE_ARCHITECT：事件房遭遇。
- THE_FUTURE_OF_POTIONS：事件房遭遇（药水选择系）。
- THE_LANTERN_KEY：分支已实测——RETURN_THE_KEY 立得约 +100 金币无战斗；
  KEEP_THE_KEY 触发骑士战获取钥匙卡。低血量选 RETURN，健康时选 KEEP。
  Lantern Key 任务卡解锁下一章节特殊事件。
- THE_LEGENDS_WERE_TRUE：事件房遭遇。
- THIS_OR_THAT：分支已实测——"ORNATE" 选项授予 MOLTEN_EGG（攻击牌奖励
  到手即升级）。
- TINKER_TIME：事件房遭遇。
- TRASH_HEAP：事件房遭遇。
- TRIAL：事件房遭遇。
- UNREST_SITE：休息点变体事件（非标准休息选项）。
- VAKUU：远古系事件（Whispering Earring 遗物——Vakuu 代打第一回合）。
- WAR_HISTORIAN_REPY：事件房遭遇。
- WATERLOGGED_SCRIPTORIUM：事件房遭遇。
- WELCOME_TO_WONGOS：已实测——300g 神秘箱授予 WONGO'S_MYSTERY_TICKET
  （5 场战斗后获得 3 件随机遗物）；Wongo 感谢徽章毫无用处。
- WELLSPRING：事件房遭遇。
- WHISPERING_HOLLOW：事件房遭遇。
- WOOD_CARVINGS：事件房遭遇。
- ZEN_WEAVER：事件房遭遇。

## 事件处理备注

- state 中 screen="event" 时 screen_detail.options 列出选项
  （kind=event_option）；用 act choose index 选择；锁定选项在游戏界面
  显示 IsLocked。
- 事件奖励可能变形卡牌、授予遗物/药水/金币或触发战斗——选择前读界面
  文本；本索引用于识别，不是穷尽式选择攻略。
- 远古系事件（Darv、Neow、Nonupeipe、Orobas、Pael、Tanx、Tezcatara、
  Vakuu）共享远古遗物/货币家族。
