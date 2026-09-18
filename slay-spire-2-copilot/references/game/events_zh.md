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
- THE_LEGENDS_WERE_TRUE（传说是真的；仅 Act1；所有玩家 HP ≥ 10 且牌库非空）：NAB_THE_MAP → 向牌库加入 SpoilsMap（Quest，不可打出；SpoilsActIndex=1——在第二章地图标记价值 600 金币的战利品房）；SLOWLY_FIND_AN_EXIT → 受到 8 点不可格挡、无来源伤害，获得 1 瓶随机药水（角色药水池 + 共享池）。SpoilsMap 在 Act2 宝箱房兑现（约 600 战利品金 + 箱金）；兑现后任务牌离 deck。移除类服务在 Act2 宝箱前绝不可选中 SpoilsMap。
- MORPHIC_GROVE（变形灵林谷；共享；要求所有玩家金币 ≥ 100 且 ≥2 张可变形牌）：GROUP → 失去全部金币（被窃），自选 2 张牌库卡各自随机变形；LONER → +5 最大 HP。
- LUMINOUS_CHOIR（冷光合唱团；要求所有玩家金币 ≥ 花费且遗物队列仍有存货；花费 = 149 − rng 0..49 → 100–149 金币）：REACH_INTO_THE_FLESH → 移除自选 2 张牌库卡，向牌库加入诅咒 SporeMind（孢子之心：1 费，诅咒，带消耗关键词）；OFFER_TRIBUTE → 支付花费，获得遗物队列最前端的下一件遗物（金币不足则锁定）。
- JUNGLE_MAZE_ADVENTURE（丛林迷宫奇遇；共享）：SOLO_QUEST → 受到 18 点不可格挡、无来源伤害，获得 150 ± rng −15..+15 金币（135–165）；JOIN_FORCES → 获得 50 ± rng −15..+15 金币（35–65），不掉血。
- WHISPERING_HOLLOW（低语空谷；要求所有玩家金币 ≥ 44）：GOLD → 支付 35 ± rng −9..+9 金币（26–44），获得 2 瓶随机药水；HUG → 受到 9 点不可格挡、无来源伤害，自选 1 张牌库卡随机变形。
- THE_LANTERN_KEY（灯火钥匙；共享；战斗布局）：RETURN_THE_KEY → +100 金币；KEEP_THE_KEY → FIGHT → MysteriousKnightEventEncounter 战斗；获胜后每名玩家获得 LanternKey 任务卡（不可打出；Act 索引 2 时强制未知地图点为事件房，并将下一个事件重定向至 WarHistorianRepy）。
- AROMA_OF_CHAOS（混沌芳香）：LET_GO → 自选 1 张牌库卡随机变形；MAINTAIN_CONTROL → 自选 1 张牌库卡升级。
- FAKE_MERCHANT（伪商人；Act 索引 ≥1；仅单人；要求金币 ≥ 100 或持有 FoulPotion）：自定义商店布局；库存为 FakeAnchor、FakeBloodVial、FakeHappyFlower、FakeLeesWaffle、FakeMango、FakeOrichalcum、FakeSneckoEye、FakeStrikeDummy、FakeVenerableTeaSet 中随机 6 件；标价约 50 金/件（实测示例 FakeMango 54、FakeLee'sWaffle 47——非固定 50）。向商人投掷 FoulPotion → FakeMerchantEventEncounter 战斗；奖励 = FakeMerchantsRug + 所有仍在售的伪遗物。择买原则：FakeMango（+3 Max HP）与 FakeLee'sWaffle（拾取回 10% Max）为正面；FakeSneckoEye（战斗开始 Confused）为负面绝不购买。

## 其余含反编译数值的事件

- ABYSSAL_BATHS（深渊浴场）：变量 最大 HP +2 / 不可格挡 3 伤害 / 回复 10——存在 Immerse 与 Abstain 选项（选项与数值的逐项绑定部分为内部逻辑）；另有 Linger/ExitBaths 处理器。
- AMALGAMATOR（熔合者；要求 ≥2 张 Strike 标签牌且 ≥2 张 Defend 标签牌）：CombineStrikes → 移除 Strike 牌，加入 UltimateStrike；CombineDefends → 移除 Defend 牌，加入 UltimateDefend。 CombineDefends 移除所选 Defend（例如 4 张 Defend 的牌库中恰好移除 2 张）并加入 UltimateDefend（1 费 11 挡）——移除 2 张时牌库净 -1 张；deck_select 浮层可选具体副本，choose 后 proceed 确认。Strike 标签移除包含 POMMEL_STRIKE 副本——融合打击会连抽牌引擎一起吃掉。
- BRAIN_LEECH（脑蛭；Act 索引 < 2）：ShareKnowledge → 经卡牌堆流程加牌；Rip → 受到 5 点不可格挡伤害，获得 1 次奖励（选卡界面提供 3 个选项，非 5 选 1）。
- BATTLEWORN_DUMMY（战痕累累的训练假人；Act3）：Setting1/2/3 → 对战 BattleFriendV1/V2/V3——单人第三章 75/150/300 HP 固定值（事件走 scaleHpForMultiplayer；单人未缩放）。三档时限均为 TimeLimitPower 3；木人招式 NOTHING_MOVE（从不攻击）——纯输出竞速；时限到 1 时假人逃跑且 RanOutOfTime=true → 无奖励。击杀奖励：Setting1 → 1 瓶药水；Setting2 → 随机升级 2 张牌组卡；Setting3 → 1 件遗物（RelicFactory 队首）。
- BYRDONIS_NEST（多尼斯异鸟巢；要求无事件宠物）：EAT → +7 最大 HP；TAKE → 向牌库加入 ByrdonisEgg 卡。
- BUGSLAYER（害虫杀手）：Extermination → Exterminate 卡；Squash → Squash 卡。
- COLORFUL_PHILOSOPHERS（色彩哲学家；要求已解锁角色卡池 >1）：经 OfferCustom 提供 3 张卡奖励。
- COLOSSAL_FLOWER（巨大花卉；所有玩家 HP ≥ 19）：取蜜选项按 `_prizeCosts` 支付金币；ObtainPollinousCore → PollinousCore 遗物；ReachDeeper 扣血后进入更深层奖励。
- CRYSTAL_SPHERE（水晶球；Act >0；所有玩家金币 ≥ 100）：UncoverFuture → 支付 50 金币，开启
  CrystalSphereMinigame：11×11=121 格，DivinationCount=3 次点击；隐藏物品 CardReward/Curse/Gold/Potion/Relic
  经 Rng 播种于四角及其横纵连线（两轮扩展）；揭示后于小游戏 proceed 时统一发放。PaymentPlan → 加入 Debt 诅咒（6 次分期变量）。小游戏解码：点击三个角点（格 0/10/120）零命中——物品在线上随机位而非必在角点，视作 ~3/121 抽奖。
- DENSE_VEGETATION（茂密的植被）：TrudgeOn → 不可格挡伤害 + 金币；Rest → 模拟休息点回复；Fight → DenseVegetationEventEncounter。变量含 HpLoss 8。
- DOLL_ROOM（玩偶室；Act 索引 1）：ChooseRandom → 获得玩偶遗物；TakeSomeTime → 5 点不可格挡伤害；Examine → 15 点不可格挡伤害。
- DOORS_OF_LIGHT_AND_DARK（光与暗的门扉）：Light → 升级 2 张牌；Dark → 移除 2 张牌。
- DROWNING_BEACON（淹水灯塔）：BottleOption → 经奖励获得 GlowwaterPotion；ClimbOption → 失去 13 最大 HP，获得 FresnelLens 遗物。
- ENDLESS_CONVEYOR（无尽传送带；所有玩家金币 ≥ 120）：菜品处理器：ClamRoll 回复 10；Caviar +4 最大 HP；GoldenFysh +75 金币；SeapunkSalad 加入 FeedingFrenzy；JellyLiver 变形；SpicySnappy 升级；ObserveChef 升级；取餐费用 40 金币。
- FIELD_OF_MAN_SIZED_HOLES（人形洞穴之地；要求存在 PerfectFit 可附魔卡）：Resist → 移除卡牌 + 加入 2 张 Normality 诅咒；EnterYourHole → 对卡牌附魔 PerfectFit。
- GRAVE_OF_THE_FORGOTTEN（遗忘之墓；要求存在可附魔卡）：Confront → 加入 Decay 诅咒 + 附魔 SoulsPower；Accept → ForgottenSoul 遗物。
- HUNGRY_FOR_MUSHROOMS（蘑菇饥渴）：BigMushroom → BigMushroom 遗物；FragrantMushroom → FragrantMushroom 遗物。
- INFESTED_AUTOMATON（被寄生的自动机械）：Study → 向牌库添加 1 张角色池随机能力牌；TouchCore → 向牌库添加 1 张按能量费用过滤（decomp 对 `c.EnergyCost` 的委托）的角色池随机卡。
- LOST_WISP（迷失鬼火）：Search → +60 金币；Claim → 加入 Decay 诅咒 + LostWisp 遗物。
- POTION_COURIER（药水快递员；Act >0）：GrabPotions / Ransack → 药水奖励（FoulPotions 变量 3）。
- PUNCH_OFF（重拳出击；TotalFloor ≥ 6）：Nab → 加入 Injury 诅咒 + 奖励；TakeThem → 战斗 PunchOffEventEncounter。
- RANWID_THE_ELDER（长者兰伟德；Act >0；所有玩家金币 ≥ 100、≥1 件遗物、≥1 瓶药水）：GiveGold → 支付 100 金币，获得遗物；GivePotion → 给予药水换遗物；GiveRelic → 移除一件遗物，获得另一件。
- REFLECTIONS（镜中倒影）：TouchAMirror → 对一张牌降级再升级；Shatter → 加牌 + BadLuck 诅咒。
- RELIC_TRADER（遗物交换商；Act >0；所有玩家 ≥5 件有效遗物）：Top/Middle/Bottom → 交易（移除持有的该槽遗物，获得新的该槽遗物）。
- ROOM_FULL_OF_CHEESE（满屋芝士；Act 索引 < 2）：Gorge → 加牌；Search → 受到 14 点不可格挡伤害，获得 ChosenCheese 遗物。Search 税精确 −14；天选芝士每次战斗胜利后 +1 Max HP。
- TANX（Act3 远古赐福房；坦克斯）：从 9 件遗物池中随机展示 3 件 RelicOption——Claws、Crossbow、IronClub、MeatCleaver、Sai、SpikedGauntlets、TanxsWhistle、ThrowingAxe、WarHammer——若牌组中存在 ≥3 张可附魔 Instinct 的卡则追加 TriBoomerang（10 选 3）。坦克斯的哨子 → 向牌组加入 Whistle 卡（3 费攻击、消耗、33 伤害+眩晕目标；升级 +11 伤害）。带刺手甲 → +1 最大能量，但你的能力牌在战斗中 +1 费（与能力密集牌组反协同）。战锤 → 每次精英战斗胜利后，随机升级 4 张可升级的牌组卡。**祝福池效果解码**：Claws 利爪 → 将至多 6 张牌变形为 Maul（Maul = 5 伤 ×2，本场战斗内伤害递增）；IronClub 铁棒 → 每打出 4 张牌抽 1 张；TriBoomerang 三刃回旋镖 → 选 3 张攻击牌附魔 Instinct（各 −1 能量费用）；**切肉刀 MeatCleaver → 休息点获得 Cook 选项：永久移除牌库中 2 张牌并获得 9 最大 HP**。TriBoomerang deck_select：选 3 张后 proceed；Instinct −1 费使例如重锤降为 2 费，打开 Bash+重锤 同回合线。
- ROUND_TEA_PARTY（圆桌茶会；所有玩家 HP ≥ 12）：EnjoyTea → RoyalPoison 遗物 + 回复；PickFight → 11 点不可格挡伤害 + RoyalPoison。
- SAPPHIRE_SEED（蓝宝石种子）：Eat → 回复 9 + 升级；Plant → 附魔 Sown。
- SELF_HELP_BOOK（自助指南）：三选项已解码：**READ_THE_BACK → 为一张攻击牌附魔 Sharp 2（+2 伤害）；READ_PASSAGE → 为一张技能牌附魔 Nimble 2（+2 格挡）；READ_ENTIRE_BOOK → 为一张能力牌附魔 Swift 2（打出时抽 2 张）**。READ_PASSAGE 池仅技能牌；重振精神 Nimble 每张被消耗牌 +2 挡（5→7；对附魔副本锻造 7→9——非表中 +7）。READ_ENTIRE_BOOK 在牌库仅有唯一能力牌时自动指向该牌；Swift 2 打出抽 2 战斗内确认。
- SLIPPERY_BRIDGE（滑脚木桥；TotalFloor > 6；要求存在可移除牌）：Overcome → 移除 1 张随机卡；HoldOn → 受到 HP 损失 = 3 + 本事件已选 HoldOn 次数（3、4、5……递增）；事件在 HoldOn 与 Overcome 之间循环直到选择 Overcome。**除 Overcome 外没有出口**——拖延只是在同一随机移除之上叠加 HP 税；移除池为整个牌库（同层刚拿到的卡也可能被移除）。
- SPIRALING_WHIRLPOOL（螺旋漩涡；要求存在 Spiral 可附魔卡）：ObserveTheSpiral → 附魔 Spiral；Drink → 回复。
- SPIRIT_GRAFTER（灵魂嫁接者）：LetItIn → 回复 25 + 加入 Metamorphosis 卡；Rejection → 升级 + 受到 10 点伤害。LetItIn 治疗为 +25 精确（曾有一次 +45 样本——未解变异）；Metamorphosis 入牌库（已解码效果：将职业池 3 张随机攻击牌洗入抽牌堆，本场战斗免费——见 cards_zh.md 事件区 METAMORPHOSIS 条）。
- STONE_OF_ALL_TIME（永恒之石；Act 1；所有玩家 ≥1 瓶药水）：Lift → +10 最大 HP（饮用药水路径——精确消耗 1 瓶药水）；Push → 6 点伤害 + 附魔（+8 Vigorous 变量）。Lift 同次结算 **+10 最大 HP 且 +10 当前 HP** ——当前 HP 补足属于效果本体而非单独治疗；按 1 瓶药换 +10/+10 记账。
- SUNKEN_STATUE（沉没雕像）：GrabSword → SwordOfStone 遗物（relics_zh.md：击败 5 名精英后变化为 Sword of Jade）；DiveIntoWater → +111 金币，受到 7 点伤害。DiveIntoWater 金币在 A1 浮动 ~108–119（观察到 108 与 119；表值 +111 为近似），7 伤税精确。潜水是可靠的即时价值线。
- THE_FUTURE_OF_POTIONS（药水的未来；Act 2）：三个选项
  "放入 稀有 / 罕见 / 普通 药水" — 所选药水被消耗；奖励 = 1 次本职业卡池选卡
  （例如：放入普通 Speed Potion → 死灵池 WISP / INVOKE / NEGATIVE_PULSE 三选一）。
  优先消耗身上价值最低的那档药水。
- SUNKEN_TREASURY（淹水金库）：FirstChest → +60 金币；SecondChest → +333 金币 + Greed 诅咒。
- SYMBIOTE（共生体；Act >0）：Approach → 对 1 张攻击牌附魔 Corrupted——Corrupted 附魔：有源攻击伤害 ×1.5，但打出时其拥有者受到 2 点不可格挡无来源伤害；KillWithFire → 变形 1 张选定牌。Corrupted 的 deck_select 池**排除已带其它附魔的牌**——池内只有未附魔攻击（Strikes/Bash/Spite/Unrelenting/Headbutt/Ashen/Hemo/Feed 类）。消耗堆成长类攻击（如 Ashen Strike）享受 ×1.5 乘区，且每次打出 2 自伤可反哺 Rupture/Spite/自成型黏土。选择后 proceed 确认。
- TABLET_OF_TRUTH（真理石板）：Smash → 回复 20（20 点治疗溢出封顶至最大值；Smash 为价值线）。Decipher → 递增的最大 HP 阶梯：各级代价 −3/−6/−12 Max HP（翻倍；loc 键 DECIPHER_1/2/3，每级均有"继续解读"选项），每级均可"放弃"；**任何已完成级别与放弃均未观察到奖励**——实测为纯最大 HP 消耗事件；原一行摘要"失去 3 最大 HP + 升级路径"判定为错误，除非另有来源确认奖励路径，否则应选 Smash。三级+放弃共付 21 Max HP 换零收益。
- THE_ARCHITECT（建筑师；Act3 Boss 节点后的剧情事件）——**EA 结局屏**：到达本事件即代表第三幕 Boss 已被击破、当前 EA 版本所有已实装流程内容全部通关。游戏处于抢先体验阶段，建筑师 Boss 本体尚未实装；PROCEED → HP 0 是 EA 占位收束。机制：对白行走器——每行仅一个 回应/继续 选项（textKey THE_ARCHITECT.dialogue.N）；铁甲战士线为 威胁 → 继续 → PROCEED；PROCEED 将玩家 HP 置 0 → game_over（floor 48）。反编译备注（TheArchitect.cs）：WinRun() 仅播放攻击特效（玩家按 Score 输出伤害数字；Architect '反击'为特效——AnimArchitectAttackIfNecessary 未发出任何 CreatureCmd.Damage）随后 SetLocalPlayerReady() 切章同步；TheArchitectEventEncounter 只生成 Architect 占位体（9999 HP、NOTHING_MOVE 循环、HiddenIntent）——与"Boss 未实装"一致。铁甲战士对白：3 次访问档位，全部 EndAttackers=Both；访问档位由档案 TotalWins/Wins 经 LoadDialogue() 选取。
- THIS_OR_THAT（这个还是那个？）：Plain → 受到 6 点伤害 + 金币；Ornate → 获得遗物 + 加入 Clumsy 诅咒。Plain 金币在 A1 浮动 ~43–64；6 伤税每次精确。
- TINKER_TIME（打造时间）：选择卡牌类型 + 附加效果；附加效果含 12 伤害 / 8 格挡 / 2 Weak / 2 Vulnerable / 3 段暴力；加入 MadScience 卡。
- TRASH_HEAP（垃圾堆；所有玩家 HP > 5）：DiveIn → 8 点伤害 + 遗物；Grab → +100 金币 + 加牌。
- TRIAL（审判）：Accept/Reject 后按证人分支——MerchantGuilty：Regret 诅咒 + 遗物；MerchantInnocent：Shame 诅咒 + 升级；NobleGuilty：回复；NobleInnocent：Regret + 金币；NondescriptGuilty：Doubt + 奖励；NondescriptInnocent：Doubt + 变形。
- UNREST_SITE（无休之处；所有玩家 HP ≤ 70% 最大值）：Rest → 回复 + 诅咒；Kill → −8 最大 HP + 遗物。
- WAR_HISTORIAN_REPY（战史学家付袭；IsAllowed 正常为 false——由 LanternKey 门槛触发）：UnlockChest → 奖励；UnlockCage → HistoryCourse 遗物；LanternKey 任务完成时移除钥匙卡。
- WATERLOGGED_SCRIPTORIUM（水漫缮写室；所有玩家金币 ≥ 55）：BloodyInk → +6 最大 HP；TentacleQuill → 支付 55 金币，附魔 Steady；PricklySponge → 支付 99 金币，附魔 Steady + 卡牌选项。
- WELCOME_TO_WONGOS（欢迎来到旺购百货；门槛标注 Act 1，但 Act 2 亦可触发——章节标注视为软性；所有玩家金币 ≥ 100）：BuyBargainBin → 支付 100 金币，获得遗物；BuyFeaturedItem → 支付 200 金币，获得遗物；BuyMysteryBox → 支付 300 金币，获得 WongosMysteryTicket（5 场战斗后获得 3 件随机遗物）；Leave 离开。
- WELLSPRING（泉水）：Bottle → 药水奖励；Bathe → 移除卡牌（curses 变量 1——存在 Guilty 追加处理器）。
- WOOD_CARVINGS（木雕；要求存在可移除的基础牌）：Snake → 附魔 Slither；Bird → 变形为 Peck；Torus → 变形为 ToricToughness。Slither 附魔效果：被附魔的卡牌每次抽到时费用在 0~3 之间随机；随机化之后再施加的改费效果仍可能把最终费用抬到 3 以上。Peck = 2 伤 ×3，打击标签多段，吃力量加成；ToricToughness = 2 费 5 挡 + 后续 2 次挡被清空时重新获得该挡值。Slither 方差与组合技牌库反协同。
- ZEN_WEAVER（修禅织网者；所有玩家金币 ≥ 125）：BreathingTechniques → 支付 50 金币，**加入 2 张 Enlightenment**；EmotionalAwareness → 支付 125 金币，**移除 1 张牌**；ArachnidAcupuncture → 支付 250 金币，**移除 2 张牌**。注意：两个移除选项单价 125/张均贵于商店移除（75g）；事件无离开选项，必须三选一。ArachnidAcupuncture 有 250 金门槛——金币低于门槛时不出现。Enlightenment（启迪）0 费「手牌全部费用变 1」对 0 费引擎牌（Bloodletting/Brand 类）是反协同——Rupture 线牌库对该选项需谨慎。

## 远古事件选项

DARV 与 NONUPEIPE 在 act 池中以 `AncientEventModel` 形式存在（门槛见上），但本次审阅的反编译事件源码中没有其选项处理器——省略。（TANX 选项见上文条目；OROBAS、TEZCATARA、VAKUU 见下。）

- OROBAS（欧洛巴斯；Act2 虫巢远古）：ELECTRIC_SHRYMP 放电异虾 → 拾取时选 1 张技能牌附魔 **Imbued**（Imbued = 战斗开始自动打出、不耗能量——每战等效免费）；DRIFTWOOD 浮木 → 每张卡牌奖励可重掷 1 次；TOUCH_OF_OROBAS 欧洛巴斯之触 → 将初始遗物替换为远古版（IRONCLAD：燃烧之血每战+6 → **黑暗之血每战回 12**；遗物 id 更换，战斗结束回 12 与天选芝士 +1 Max HP 同战叠加）。**全选项池解码**：ELECTRIC_SHRYMP（1 技能牌 Imbued 附魔）、GLASS_EYE（2 普通+2 罕见+1 稀有卡）、SAND_CASTLE 沙堡（**拾取时随机升级 6 张牌**）、ALCHEMICAL_COFFER（**4 药槽填满随机药水**）、DRIFTWOOD（卡牌奖励重掷）、RADIANT_PEARL 发光珍珠（**每战开局手牌加 1 张 Luminesce**）、PRISMATIC_GEM（回合开始 +1；卡牌奖励混入他色牌）、SEA_GLASS（查看 15 张他角色牌选任意张）、TOUCH_OF_OROBAS（起始遗物→远古版）、ARCHAIC_TOOTH（1 张起始牌变化为远古版）。黑暗之血 12/战是 Act2 HP 经济的重要来源。
- TEZCATARA 选项：YUMMY_COOKIE 美味饼干 → 获得 YummyCookie 遗物并自选升级 4 张牌（deck_select 浮层：选择后 proceed 确认）；STORYBOOK 故事书 → 向牌库加入 1 张 Brightest Flame；SEAL_OF_GOLD 黄金印 → SealOfGold 遗物：回合开始花 5 金获得 1 能量（金不足 5 时无效；一处来源写 3，5 为多源印证值）。**祝福池其余选项**：NUTRITIOUS_SOUP 营养汤 → NutritiousSoup 遗物：拾取时为所有带 Strike 标签的基础牌附魔 Tezcatara's Ember（Ember = **0 费、+3 伤害、Eternal**）；TOASTY_MITTENS 烘焙手套 → ToastyMittens 遗物：每回合抽牌前消耗抽牌堆顶牌并获得 1 力量（被动力量引擎，消耗同时瘦牌；与 Headbutt 取回反协同）；GOLDEN_COMPASS 黄金罗盘 → GoldenCompass 遗物：拾取时以一条特殊路径替换第二章地图；PUMPKIN_CANDLE 南瓜蜡烛 → 遗物解码见 relics_zh.md（+1 能/回合、5 战后熄灭、休息点 KINDLE 选项——短暂性+休息点行动税）；VERY_HOT_COCOA 烫嘴可可 → 第 1 回合 +4 能量（与灯笼叠加 8 能已验证）。
- VAKUU（Act3 荣光远古；瓦库）选项解码：血染玫瑰 → BloodSoakedRose 遗物：每回合 +1 最大能量，但拾取时向牌库加入 1 张 **Enthralled**——Enthralled = 2 费诅咒、永恒、**在手时必须先于其他牌打出**（每次出现税 2 能、付清前封锁其他出牌；+1 能/回合无法对冲爆发线破坏）；原初之爪 → 拾取加 2 随机诅咒 + 3 张 Wish（诅咒代价类）；选择悖论 → 第 1 回合开始从 5 张随机卡选 1 加入手牌，这些卡均获 Retain——**语义解码：添加为带 Retain 的本战斗手牌添加，每战 T1 新五选一，非永久入牌库**。档案反编译此前缺 Vakuu 选项处理器——本解码补齐该缺口。

## 事件处理备注

- state 中 screen="event" 时 screen_detail.options 列出选项（kind=event_option）；用 `act choose index` 选择；锁定选项在游戏界面显示 IsLocked。
- `IsAllowed` 门槛：事件仅在其反编译前置条件满足时生成（章节索引、金币、HP、牌库内容）——存在门槛的已在上文逐条列出。
- 事件随机变量在打开事件时由对局 rng 计算（`CalculateVars`）——`基准 ± 范围` 即确定性的报价窗口。
- 漩涡/佩尔解码备注：Spiral 附魔 = EnchantPlayCount +1（每次打出结算两次；decomp Spiral.cs — 仅限基础打击/防御标签；附魔防御 5→"双结算"=10 基础，每次结算分别吃敏捷加成，与锻造升级 +3/次叠加）。Drink 治疗量为数据驱动（DynamicVars.Heal — decomp 未硬编码）。佩尔之角 = +2 张 RELAX（RELAX：3 费 技能 消耗 15 挡+下回合抽 2+2 能量）；Act2 幕开场远古祝福房另有满血回复（HP 回复似乎是幕开场远古房固有效果，与遗物选择无关）。
