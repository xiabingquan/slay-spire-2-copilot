# 事件

事件参考（确定性选项，仅含精确数值）。来源：反编译源码
`MegaCrit.Sts2.Core.Models.Events` + 相关遗物/卡牌
`MegaCrit.Sts2.Core.Models.Relics` / `Models.Cards`（/tmp/sts2-decomp）。
括号内为简中译名（已核实者标注；未核实官方译名的条目保留英文内部名）。

格式：`- EVENT_ID（章节）：选项 → 精确效果。`

随机化数值按 `CalculateVars` 的算法写成 `基准 ± 范围`。反编译代码中不存在的效果分支一律省略。

章节远古房（act 源码）：蔓生之地 = Neow（`UnlockState.IsEpochRevealed<NeowEpoch>()` 为假时移除）；虫巢 = Orobas（`OrobasEpoch` 门槛）、Pael、Tezcatara；荣光之殿 = Nonupeipe、Tanx、Vakuu（无门槛）；水底码头 = Neow（同 NeowEpoch 门槛）。共享远古 Darv 未揭示 `DarvEpoch` 时移除。

## 已核实事件

- NEOW（尼奥；Act1 蔓生之地远古；Act4 水底码头同样出现）：无 modifier 的对局 → 3 个选项 = 2 件随机正面遗物 + 1 件随机诅咒代价遗物。正面池：ArcaneScroll、BoomingConch、FishingRod、GoldenPearl、Kaleidoscope、LeadPaperweight、LostCoffer、MassiveScroll、NeowsTorment、NewLeaf、PhialHolster、PreciseScissors、ScrollBoxes、WingedBoots；另有三组独立 XOR 追加：LavaRock XOR SmallCapsule（诅咒为 LargeCapsule 时跳过）、NutritiousOyster XOR StoneHumidifier、NeowsTalisman XOR Pomander。诅咒池：CursedPearl、HeftyTablet、LargeCapsule、LeafyPoultice、NeowsBones、PrecariousShears、SilkenTress、SilverCrucible。冲突项从正面池剔除：CursedPearl−GoldenPearl、HeftyTablet−ArcaneScroll、LeafyPoultice−NewLeaf、PrecariousShears−PreciseScissors。每件遗物另经 `IsAllowedAtNeow` 过滤。对局存在 modifier 时，Neow 改为依次提供各 modifier 的 `GenerateNeowOption`。
- PAEL（佩尔；Act2 虫巢远古）：3 个遗物选项抽取规则：(1) PaelsFlesh / PaelsHorn / PaelsTears 中随机 1；(2) 池 = PaelsWing +（若牌库 ≥3 张可 Goopy 附魔的 Defend 牌 → PaelsClaw）+（若 ≥5 张可移除牌 → PaelsTooth），随后该池翻倍 + 恒定加入 PaelsGrowth → 随机 1；(3) 池 = PaelsEye / PaelsBlood +（若无事件宠物 → PaelsLegion）→ 随机 1。
  - PaelsFlesh（佩尔之肉）：战斗第 3 回合起，最大能量 +1。
  - PaelsHorn（佩尔之角）：拾取时向牌库加入 2 张 Relax。
  - PaelsTears（佩尔之泪）：上回合结束时有未花费能量 → 下回合开始 +2 能量。
  - PaelsWing（佩尔之翼）：卡牌奖励获得 SACRIFICE 替代选项；每献祭 2 次，获得遗物队列最前端的下一件遗物。
  - PaelsClaw（佩尔之爪）：拾取时，牌库中每张 Defend 标签卡牌获得 Goopy 1（Goopy：卡牌获得消耗；额外格挡 = Amount−1；每次打出该牌 Amount +1）。
  - PaelsTooth（佩尔之牙）：拾取时移除至多 5 张可升级牌（存入本遗物）；每场战斗后随机 1 张以升级状态回到牌库。
  - PaelsEye（佩尔之眼）：每场战斗首次未打出任何牌就结束回合时，消耗整副手牌并获得一个额外回合。
  - PaelsBlood（佩尔之血）：每回合额外抽 1 张牌。
  - PaelsGrowth（佩尔的增生组织）：拾取时选择 1 张牌库卡 → 附魔 Clone 4；休息点新增 Clone 休息选项（Clone 用于在休息点复制卡牌）。
  - PaelsLegion（佩尔的士兵）：加入 PaelsLegion 宠物；就绪时每场战斗首次获得格挡的卡牌打出使该格挡翻倍（×2），随后冷却 2 回合。
- TEA_MASTER（茶艺大师；Act1-2；要求所有玩家金币 ≥ 150）：BONE_TEA → 支付 50 金币，获得 BoneTea（骨茶；金币不足则锁定）——1 场战斗：第 1 回合升级手牌中所有卡牌；EMBER_TEA → 支付 150 金币，获得 EmberTea（余烬茶；金币不足则锁定）——5 场战斗：进入战斗房时 +2 力量；TEA_OF_DISCOURTESY → 免费，获得 TeaOfDiscourtesy（无礼之茶）——1 场战斗：战斗开始前向抽牌堆随机位置加入 2 张 Dazed。
- THE_LEGENDS_WERE_TRUE（传说是真的；仅 Act1；所有玩家 HP ≥ 10 且牌库非空）：NAB_THE_MAP → 向牌库加入 SpoilsMap（Quest，不可打出；SpoilsActIndex=1——在第二章地图标记价值 600 金币的战利品房）；SLOWLY_FIND_AN_EXIT → 受到 8 点不可格挡、无来源伤害，获得 1 瓶随机药水（角色药水池 + 共享池）。
- MORPHIC_GROVE（变形灵林谷；共享；要求所有玩家金币 ≥ 100 且 ≥2 张可变形牌）：GROUP → 失去全部金币（被窃），自选 2 张牌库卡各自随机变形；LONER → +5 最大 HP。
- LUMINOUS_CHOIR（冷光合唱团；要求所有玩家金币 ≥ 花费且遗物队列仍有存货；花费 = 149 − rng 0..49 → 100–149 金币）：REACH_INTO_THE_FLESH → 移除自选 2 张牌库卡，向牌库加入诅咒 SporeMind（孢子之心：1 费，诅咒，带消耗关键词）；OFFER_TRIBUTE → 支付花费，获得遗物队列最前端的下一件遗物（金币不足则锁定）。
- JUNGLE_MAZE_ADVENTURE（丛林迷宫奇遇；共享）：SOLO_QUEST → 受到 18 点不可格挡、无来源伤害，获得 150 ± rng −15..+15 金币（135–165）；JOIN_FORCES → 获得 50 ± rng −15..+15 金币（35–65），不掉血。
- WHISPERING_HOLLOW（低语空谷；要求所有玩家金币 ≥ 44）：GOLD → 支付 35 ± rng −9..+9 金币（26–44），获得 2 瓶随机药水；HUG → 受到 9 点不可格挡、无来源伤害，自选 1 张牌库卡随机变形。
- THE_LANTERN_KEY（灯火钥匙；共享；战斗布局）：RETURN_THE_KEY → +100 金币；KEEP_THE_KEY → FIGHT → MysteriousKnightEventEncounter 战斗；获胜后每名玩家获得 LanternKey 任务卡（不可打出；Act 索引 2 时强制未知地图点为事件房，并将下一个事件重定向至 WarHistorianRepy）。
- AROMA_OF_CHAOS（混沌芳香）：LET_GO → 自选 1 张牌库卡随机变形；MAINTAIN_CONTROL → 自选 1 张牌库卡升级。
- FAKE_MERCHANT（伪商人；Act 索引 ≥1；仅单人；要求金币 ≥ 100 或持有 FoulPotion）：自定义商店布局；库存为 FakeAnchor、FakeBloodVial、FakeHappyFlower、FakeLeesWaffle、FakeMango、FakeOrichalcum、FakeSneckoEye、FakeStrikeDummy、FakeVenerableTeaSet 中随机 6 件；遗物单价 50 金币。向商人投掷 FoulPotion → FakeMerchantEventEncounter 战斗；奖励 = FakeMerchantsRug + 所有仍在售的伪遗物。

## 其余含反编译数值的事件

- ABYSSAL_BATHS（深渊浴场）：变量 最大 HP +2 / 不可格挡 3 伤害 / 回复 10——存在 Immerse 与 Abstain 选项（选项与数值的逐项绑定部分为内部逻辑）；另有 Linger/ExitBaths 处理器。
- AMALGAMATOR（熔合者；要求 ≥2 张 Strike 标签牌且 ≥2 张 Defend 标签牌）：CombineStrikes → 移除 Strike 牌，加入 UltimateStrike；CombineDefends → 移除 Defend 牌，加入 UltimateDefend。
- BRAIN_LEECH（脑蛭；Act 索引 < 2）：ShareKnowledge → 经卡牌堆流程加牌；Rip → 受到 5 点不可格挡伤害，获得 1 次奖励（选择界面 5 选 1）。
- BATTLEWORN_DUMMY（战痕累累的训练假人）：Setting1/2/3 → 对战 BattleFriendV1/V2/V3（各档 HP 显示于界面）。
- BYRDONIS_NEST（多尼斯异鸟巢；要求无事件宠物）：EAT → +7 最大 HP；TAKE → 向牌库加入 ByrdonisEgg 卡。
- BUGSLAYER（害虫杀手）：Extermination → Exterminate 卡；Squash → Squash 卡。
- COLORFUL_PHILOSOPHERS（色彩哲学家；要求已解锁角色卡池 >1）：经 OfferCustom 提供 3 张卡奖励。
- COLOSSAL_FLOWER（巨大花卉；所有玩家 HP ≥ 19）：取蜜选项按 `_prizeCosts` 支付金币；ObtainPollinousCore → PollinousCore 遗物；ReachDeeper 扣血后进入更深层奖励。
- CRYSTAL_SPHERE（水晶球；Act >0；所有玩家金币 ≥ 100）：UncoverFuture → 支付 50 金币（3 张预言流程）；PaymentPlan → 加入 Debt 诅咒（6 次分期变量）。
- DENSE_VEGETATION（茂密的植被）：TrudgeOn → 不可格挡伤害 + 金币；Rest → 模拟休息点回复；Fight → DenseVegetationEventEncounter。变量含 HpLoss 8。
- DOLL_ROOM（玩偶室；Act 索引 1）：ChooseRandom → 获得玩偶遗物；TakeSomeTime → 5 点不可格挡伤害；Examine → 15 点不可格挡伤害。
- DOORS_OF_LIGHT_AND_DARK（光与暗的门扉）：Light → 升级 2 张牌；Dark → 移除 2 张牌。
- DROWNING_BEACON（淹水灯塔）：BottleOption → 经奖励获得 GlowwaterPotion；ClimbOption → 失去 13 最大 HP，获得 FresnelLens 遗物。
- ENDLESS_CONVEYOR（无尽传送带；所有玩家金币 ≥ 120）：菜品处理器：ClamRoll 回复 10；Caviar +4 最大 HP；GoldenFysh +75 金币；SeapunkSalad 加入 FeedingFrenzy；JellyLiver 变形；SpicySnappy 升级；ObserveChef 升级；取餐费用 40 金币。
- FIELD_OF_MAN_SIZED_HOLES（人形洞穴之地；要求存在 PerfectFit 可附魔卡）：Resist → 移除卡牌 + 加入 2 张 Normality 诅咒；EnterYourHole → 对卡牌附魔 PerfectFit。
- GRAVE_OF_THE_FORGOTTEN（遗忘之墓；要求存在可附魔卡）：Confront → 加入 Decay 诅咒 + 附魔 SoulsPower；Accept → ForgottenSoul 遗物。
- HUNGRY_FOR_MUSHROOMS（蘑菇饥渴）：BigMushroom → BigMushroom 遗物；FragrantMushroom → FragrantMushroom 遗物。
- INFESTED_AUTOMATON（被寄生的自动机械）：Study / TouchCore → 向牌库加牌。
- LOST_WISP（迷失鬼火）：Search → +60 金币；Claim → 加入 Decay 诅咒 + LostWisp 遗物。
- POTION_COURIER（药水快递员；Act >0）：GrabPotions / Ransack → 药水奖励（FoulPotions 变量 3）。
- PUNCH_OFF（重拳出击；TotalFloor ≥ 6）：Nab → 加入 Injury 诅咒 + 奖励；TakeThem → 战斗 PunchOffEventEncounter。
- RANWID_THE_ELDER（长者兰伟德；Act >0；所有玩家金币 ≥ 100、≥1 件遗物、≥1 瓶药水）：GiveGold → 支付 100 金币，获得遗物；GivePotion → 给予药水换遗物；GiveRelic → 移除一件遗物，获得另一件。
- REFLECTIONS（镜中倒影）：TouchAMirror → 对一张牌降级再升级；Shatter → 加牌 + BadLuck 诅咒。
- RELIC_TRADER（遗物交换商；Act >0；所有玩家 ≥5 件有效遗物）：Top/Middle/Bottom → 交易（移除持有的该槽遗物，获得新的该槽遗物）。
- ROOM_FULL_OF_CHEESE（满屋芝士；Act 索引 < 2）：Gorge → 加牌；Search → 受到 14 点不可格挡伤害，获得 ChosenCheese 遗物。
- ROUND_TEA_PARTY（圆桌茶会；所有玩家 HP ≥ 12）：EnjoyTea → RoyalPoison 遗物 + 回复；PickFight → 11 点不可格挡伤害 + RoyalPoison。
- SAPPHIRE_SEED（蓝宝石种子）：Eat → 回复 9 + 升级；Plant → 附魔 Sown。
- SELF_HELP_BOOK（自助指南）：ReadPassage/ReadEntireBook 附魔 Sharp/Nimble 等；SkipBook 离开。
- SLIPPERY_BRIDGE（滑脚木桥；TotalFloor > 6；要求存在可移除牌）：Overcome → 移除 1 张随机卡；HoldOn → 受到 HP 损失。
- SPIRALING_WHIRLPOOL（螺旋漩涡；要求存在 Spiral 可附魔卡）：ObserveTheSpiral → 附魔 Spiral；Drink → 回复。
- SPIRIT_GRAFTER（灵魂嫁接者）：LetItIn → 回复 25 + 加入 Metamorphosis 卡；Rejection → 升级 + 受到 10 点伤害。
- STONE_OF_ALL_TIME（永恒之石；Act 1；所有玩家 ≥1 瓶药水）：Lift → +10 最大 HP（饮用药水路径）；Push → 6 点伤害 + 附魔（+8 Vigorous 变量）。
- SUNKEN_STATUE（沉没雕像）：GrabSword → SwordOfStone 遗物；DiveIntoWater → +111 金币，受到 7 点伤害。
- SUNKEN_TREASURY（淹水金库）：FirstChest → +60 金币；SecondChest → +333 金币 + Greed 诅咒。
- SYMBIOTE（共生体；Act >0）：Approach → 对 1 张攻击牌附魔 Corrupted——Corrupted 附魔：有源攻击伤害 ×1.5，但打出时其拥有者受到 2 点不可格挡无来源伤害；KillWithFire → 变形 1 张选定牌。
- TABLET_OF_TRUTH（真理石板）：Smash → 回复 20；Decipher → 失去 3 最大 HP + 升级路径。
- THE_ARCHITECT（建筑师；Act3 Boss 节点后的剧情事件）：仅对话选项；观察到的分支 Threaten（威胁）→ 玩家 HP 置 0、对局结束（game_over）——剧情死亡即时生效，不是可打赢的战斗。Architect 怪物模型为 9999 HP、招式 NOTHING 的剧情占位体。
- THIS_OR_THAT（这个还是那个？）：Plain → 受到 6 点伤害 + 金币；Ornate → 获得遗物 + 加入 Clumsy 诅咒。
- TINKER_TIME（打造时间）：选择卡牌类型 + 附加效果；附加效果含 12 伤害 / 8 格挡 / 2 Weak / 2 Vulnerable / 3 段暴力；加入 MadScience 卡。
- TRASH_HEAP（垃圾堆；所有玩家 HP > 5）：DiveIn → 8 点伤害 + 遗物；Grab → +100 金币 + 加牌。
- TRIAL（审判）：Accept/Reject 后按证人分支——MerchantGuilty：Regret 诅咒 + 遗物；MerchantInnocent：Shame 诅咒 + 升级；NobleGuilty：回复；NobleInnocent：Regret + 金币；NondescriptGuilty：Doubt + 奖励；NondescriptInnocent：Doubt + 变形。
- UNREST_SITE（无休之处；所有玩家 HP ≤ 70% 最大值）：Rest → 回复 + 诅咒；Kill → −8 最大 HP + 遗物。
- WAR_HISTORIAN_REPY（战史学家付袭；IsAllowed 正常为 false——由 LanternKey 门槛触发）：UnlockChest → 奖励；UnlockCage → HistoryCourse 遗物；LanternKey 任务完成时移除钥匙卡。
- WATERLOGGED_SCRIPTORIUM（水漫缮写室；所有玩家金币 ≥ 55）：BloodyInk → +6 最大 HP；TentacleQuill → 支付 55 金币，附魔 Steady；PricklySponge → 支付 99 金币，附魔 Steady + 卡牌选项。
- WELCOME_TO_WONGOS（欢迎来到旺购百货；Act 1；所有玩家金币 ≥ 100）：BuyBargainBin → 支付 100 金币，获得遗物；BuyFeaturedItem → 支付 200 金币，获得遗物；BuyMysteryBox → 支付 300 金币，获得 WongosMysteryTicket（5 场战斗后获得 3 件随机遗物）；Leave 离开。
- WELLSPRING（泉水）：Bottle → 药水奖励；Bathe → 移除卡牌（curses 变量 1——存在 Guilty 追加处理器）。
- WOOD_CARVINGS（木雕；要求存在可移除的基础牌）：Snake → 附魔 Slither；Bird → 变形为 Peck；Torus → 变形为 ToricToughness。
- ZEN_WEAVER（修禅织网者；所有玩家金币 ≥ 125）：BreathingTechniques → 支付 50 金币，加入 Enlightenment；EmotionalAwareness → 支付 125 金币路径；ArachnidAcupuncture → 支付 250 金币，移除卡牌路径。

## 未提取选项表的远古事件

DARV、NONUPEIPE、OROBAS、TANX、TEZCATARA、VAKUU 在 act 池中以 `AncientEventModel` 形式存在（门槛见上），但本次审阅的反编译事件源码中没有其选项处理器——省略。relics_zh.md 中记录的遗物关联不在此处作为事件选项机制断言。

## 事件处理备注

- state 中 screen="event" 时 screen_detail.options 列出选项（kind=event_option）；用 `act choose index` 选择；锁定选项在游戏界面显示 IsLocked。
- `IsAllowed` 门槛：事件仅在其反编译前置条件满足时生成（章节索引、金币、HP、牌库内容）——存在门槛的已在上文逐条列出。
- 事件随机变量在打开事件时由对局 rng 计算（`CalculateVars`）——`基准 ± 范围` 即确定性的报价窗口。
