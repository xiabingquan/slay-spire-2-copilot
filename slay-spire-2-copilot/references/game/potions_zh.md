# 药水

药水效果参考（确定性机制，仅含精确数值）。来源：反编译源码
`MegaCrit.Sts2.Core.Models.Potions`（/tmp/sts2-decomp），该目录下全部
Potion 类均已覆盖；数值取各类 `CanonicalVars` 基础值。括号内为简中译名。

格式：`- 名称（稀有度，使用时机，目标）：精确效果。`

使用时机：`战斗中` = CombatOnly；`随时` = AnyTime；`自动` = Automatic（满足触发条件时自动生效，无需饮用）；`事件` = 仅事件产出，不在药水池中。
目标：`自身` / `任意玩家` / `任意敌人` / `全体敌人`。全体敌人药水自动选取全部可命中敌人——不要发送单体目标 id。

## 药水

- Ashwater（灰水）(Uncommon, 战斗中, 自身): 消耗手牌中任意数量的卡牌。
- Attack Potion（攻击药水）(Common, 战斗中, 自身): 从角色卡池生成 3 张不同攻击牌中选 1 张（可跳过）；加入手牌，本回合免费。
- Beetle Juice（甲虫汁）(Rare, 战斗中, 任意敌人): 对目标施加 ShrinkPower 4 层。ShrinkPower：拥有者攻击伤害 ×0.7（−30%）；拥有者回合结束移除 1 层；层数为负数时为无限持续、不衰减。4 层 = 其 4 个回合内攻击伤害 −30%。
- Blessing of the Forge（熔炉的祝福）(Uncommon, 战斗中, 自身): 本场战斗内升级手牌中所有可升级卡牌。
- Block Potion（格挡药水）(Common, 战斗中, 任意玩家): 获得 12 格挡。
- Blood Potion（鲜血药水）(Common, 随时, 任意玩家): 回复最大 HP 的 20%。
- Bone Brew（骨头酿）(Uncommon, 战斗中, 自身): Summon Osty，数值 15。
- Bottled Potential（瓶装潜能）(Rare, 战斗中, 任意玩家): 将手牌移入抽牌堆，洗牌，抽 5 张。
- Clarity Extract（明晰提取物）(Uncommon, 战斗中, 任意玩家): 抽 1 张；获得 ClarityPower 3——接下来 3 回合开始时各多抽 1 张（每次己方回合开始递减）。
- Colorless Potion（无色药水）(Common, 战斗中, 自身): 从无色卡池生成 3 张不同卡牌中选 1 张（可跳过）；加入手牌，本回合免费。
- Cosmic Concoction（宇宙药剂）(Rare, 战斗中, 自身): 向手牌加入 3 张不同的升级版无色池卡牌。
- Cunning Potion（狡诈药水）(Uncommon, 战斗中, 自身): 向手牌加入 3 张升级版 Shiv。
- Cure All（痊愈药水）(Uncommon, 战斗中, 任意玩家): 获得 1 能量；抽 2 张牌。
- Dexterity Potion（敏捷药水）(Common, 战斗中, 任意玩家): 本场战斗 +2 敏捷。
- Distilled Chaos（精炼混沌）(Rare, 战斗中, 自身): 打出抽牌堆顶的 3 张牌。
- Droplet of Precognition（预知之滴）(Rare, 战斗中, 自身): 从抽牌堆选 1 张牌加入手牌。
- Duplicator（复制药水）(Uncommon, 战斗中, 自身): 获得 DuplicationPower 1——本回合你打出的下一张牌额外打出 1 次；回合结束移除。run-28 实测：Boss 战使用后 DUPLICATION_POWER:1 同帧可见，下一张 Bash+ 双结算——无厌沙虫 146→76（单动作 70 伤：(10+10力)×纸蛙乘区×2 次打出+易伤双施加 5→11）；药水消费后 DuplicationPower 随回合结束消失。
- Energy Potion（能量药水）(Common, 战斗中, 任意玩家): 获得 2 能量。
- Entropic Brew（混沌药水）(Rare, 随时, 自身): 用随机药水填满所有空药水栏。
- Essence of Darkness（黑暗精华）(Rare, 战斗中, 自身): 每个充能球槽引导 1 个暗球。
- Explosive Ampoule（爆炸安瓿）(Common, 战斗中, 全体敌人): 对全体敌人造成 10 点伤害（自动多目标，不要发送目标 id）。
- Fairy in a Bottle（瓶中精灵）(Rare, 自动, 自身): 将死时改为弃掉此药水并回复至最大 HP 的 30%（最少 1 点）。run-28 实测：狱火回合开始自伤在 HP 1 时击杀触发——HP 置 29/98≈Max 的 29.6%，与 30% Max 规则吻合；药水同帧从药槽消失。
- Fire Potion（火焰药水）(Common, 战斗中, 任意敌人): 造成 20 点伤害。
- Flex Potion（肌肉药水）(Common, 战斗中, 任意玩家): 获得 FlexPotionPower +5 力量——本回合结束时失去 5 力量（临时力量）。
- Focus Potion（集中药水）(Common, 战斗中, 自身): +2 专注（Focus）。
- Fortifier（固化药水）(Uncommon, 战斗中, 任意玩家): 获得等同当前格挡 2 倍的格挡（格挡变为 3 倍）。
- Foul Potion（污浊药水）(Event, 随时): 战斗中——对每个非宠物生物（含你自己）造成 12 点伤害；商人房间——获得 100 金币；FakeMerchant 事件——触发伪商人战斗。**run-27 实测（A1 2026-09-18）**：战斗用法=同窗 AoE 工具——12 伤直接带走 12 HP 千足虫段并铺垫 Thunderclap 收头（三段全 0，REATTACH 零结算）；自伤触发 Rupture（按 Amount +力 实测）。伪商人房绝不可用（战斗条款）——留给真商人房 +100 金是经济线。
- Fruit Juice（果汁）(Rare, 随时, 任意玩家): +5 最大 HP。
- Fysh Oil（异鱼之油）(Uncommon, 战斗中, 任意玩家): 本场战斗 +1 力量 +1 敏捷。run-28 实测：使用后同帧 STRENGTH_POWER +1 与 DEXTERITY_POWER:1；敏捷 +1 使后续卡牌挡值各 +1（Defend 5→6 级）同战生效。
- Gambler's Brew（赌徒特酿）(Uncommon, 战斗中, 自身): 弃置任意数量手牌，然后抽取等量牌。
- Ghost in a Jar（罐装幽灵）(Rare, 战斗中, 任意玩家): +1 层 Intangible。
- Gigantification Potion（超巨化药水）(Rare, 战斗中, 任意玩家): 获得 GigantificationPower 1——本场战斗你打出的下一张有源攻击牌造成 ×3 伤害；被该次攻击消耗。
- Glowwater Potion（发光水）(Event, 战斗中, 自身): 消耗手牌；抽 10 张。
- Heart of Iron（铁心药水）(Uncommon, 战斗中, 任意玩家): +7 镀甲（Plating）。
- King's Courage（王之勇气）(Uncommon, 战斗中, 任意玩家): Forge 15。
- Liquid Bronze（流动铜液）(Uncommon, 战斗中, 任意玩家): +3 点荆棘。
- Liquid Memories（液态记忆）(Rare, 战斗中, 自身): 从弃牌堆选 1 张牌加入手牌，本回合免费。run-25 实测（A1 2026-09-18）：弃牌堆为空时打出（全部卡在手牌/抽牌堆）— 药水被消耗但**无选牌界面、无任何效果**（完全空耗）。使用前先确认 piles；弃牌堆=0 时不可用。
- Lucky Tonic（幸运补剂）(Rare, 战斗中, 任意玩家): +1 层 Buffer。
- Mazaleth's Gift（马萨雷斯的赠礼）(Rare, 战斗中, 任意玩家): +1 层 Ritual。
- Orobic Acid（欧洛巴斯之酸）(Rare, 战斗中, 自身): 从角色卡池随机攻击、技能、能力牌各 1 张加入手牌；3 张本回合均免费。
- Poison Potion（毒药水）(Common, 战斗中, 任意敌人): 施加 6 层中毒。
- Pot of Ghouls（尸鬼瓮）(Rare, 战斗中, 自身): 向手牌加入 2 张 Soul。
- Potion of Binding（缚魂药水）(Uncommon, 战斗中, 全体敌人): 对全体敌人施加 1 层 Weak 与 1 层 Vulnerable。
- Potion of Capacity（扩容药水）(Uncommon, 战斗中, 自身): +2 个充能球槽。
- Potion of Doom（灾厄药水）(Common, 战斗中, 任意敌人): 施加 33 层 Doom。
- Potion-Shaped Rock（药水形状的石头）(Token, 战斗中, 任意敌人): 造成 15 点伤害。
- Powdered Demise（消亡粉末）(Uncommon, 战斗中, 任意敌人): 施加 DemisePower 9——目标每个自身回合结束时受到 9 点不可格挡、无来源伤害。
- Power Potion（能力药水）(Common, 战斗中, 自身): 从角色卡池生成 3 张不同能力牌中选 1 张（可跳过）；加入手牌，本回合免费。
- Radiant Tincture（明耀酊剂）(Uncommon, 战斗中, 任意玩家): 立即获得 1 能量；获得 RadiancePower 3——接下来 3 次能量重置时各 +1 能量。
- Regen Potion（再生药水）(Uncommon, 战斗中, 任意玩家): +5 层再生（Regen）。
- Shackling Potion（镣铐药水）(Rare, 战斗中, 全体敌人): 对全体敌人施加 ShacklingPotionPower 7——临时 −7 力量，其回合结束时失去。
- Ship in a Bottle（瓶中船）(Rare, 战斗中, 任意玩家): 获得 10 格挡；获得 BlockNextTurnPower 10——你的格挡首次被清除时再次获得 10 格挡（仅一次）。
- Skill Potion（技能药水）(Common, 战斗中, 自身): 从角色卡池生成 3 张不同技能牌中选 1 张（可跳过）；加入手牌，本回合免费。
- Snecko Oil（异蛇之油）(Rare, 战斗中, 任意玩家): 抽 7 张；随机化手牌中所有非 X 费卡牌的费用。
- Soldier's Stew（士兵炖汤）(Rare, 战斗中, 任意玩家): 本场战斗内你战斗牌堆中所有含 Strike 标签的卡牌 +1 次 Replay。run-16 实测：Replay 表现为用药时对各张卡的一次性充能 —— 用药时已在手牌/抽牌堆中的打击牌打出时额外结算一次；战斗后期才抽到的打击只结算一次。
- Speed Potion（速度药水）(Common, 战斗中, 任意玩家): 获得 SpeedPotionPower +5 敏捷——本回合结束时失去 5 敏捷（临时敏捷）。
- Stable Serum（稳定血清）(Uncommon, 战斗中, 任意玩家): 获得 RetainHandPower 2——接下来 2 个回合结束时不弃手牌。
- Star Potion（星星药水）(Common, 战斗中, 自身): +3 点星星（★）。
- Strength Potion（力量药水）(Common, 战斗中, 任意玩家): 本场战斗 +2 力量。
- Swift Potion（迅捷药水）(Common, 战斗中, 任意玩家): 抽 3 张牌。
- Touch of Insanity（癫狂之触）(Uncommon, 战斗中, 自身): 选择手牌中 1 张消耗能量或星星的卡牌；本场战斗其费用为 0。
- Vulnerable Potion（易伤药水）(Common, 战斗中, 任意敌人): 施加 3 层 Vulnerable。
- Weak Potion（虚弱药水）(Common, 战斗中, 任意敌人): 施加 3 层 Weak。

## 源码要点

- Attack / Skill / Power / Colorless 药水调用 `CardSelectCmd.FromChooseACardScreen(..., canSkip: true)`——选择界面可跳过；生成牌 `SetToFreeThisTurn()`。
- ExplosiveAmpoule 与 PotionOfBinding 遍历 `CombatState.HittableEnemies`——目标自动选取；bridge 不得传 `target_combat_id`。
- PotionOfBinding 的 OnUse 中变量名互换（WeakPower 用了 Vulnerable 的值、反之亦然），但两者数值均为 1——实际效果为全体敌人 1 Weak + 1 Vulnerable。
- FlexPotionPower / SpeedPotionPower 是临时力量/敏捷的子类；ShacklingPotionPower 为负向临时力量。
- BloodPotion、FruitJuice、EntropicBrew 为 `AnyTime`；FairyInABottle 为 `Automatic`。

- 药石 Potion-Shaped Rock（石化蟾蜍产出，战斗限定，任意敌人）：造成 15 点无增幅伤害。石化蟾蜍每次战斗开始发 1 瓶；药水栏可叠多瓶。按普通单敌药水选目标（传 target_combat_id）；每次使用后药水槽位重排索引。
- Fruit Juice（FRUIT_JUICE）：**+5 最大 HP——已解**（perplexity 2026-09-18 多源确认：namu/untapped/sportskeedia 等；STS2 与 STS1 行为一致）。2026-09-17「效果未解」条目退役。亦可作 StoneOfAllTime Lift 燃料（run-23 实测：献祭药水换 +10 Max HP，优于单独喝掉）。run-18 A1 Act1 商店在售；run-23 战斗奖励实测。
- 鱼油 Fysh Oil（稀有，任意时机，自身）：**立刻 +1 力量与 +1 敏捷**（perplexity 2026-09-18 + run-30 实弹：同一 state 读数 Str 4→5 / Dex 1→2）。战斗内属性增益类。
- 速度药水 Speed Potion（普通档，战斗）：**+5 敏捷战斗增益**——run-30 实弹：DEXTERITY_POWER 1→6 伴随 SPEED_POTION_POWER:5 计数；**不是抽牌药水**（与下方 Swift Potion 区分）；观察到次回合过期（战斗增益类，回合数封顶——按同回合/短窗价值处理）。
- 清晰药水 Clarity（战斗）：**立刻抽 1 张，且后续 3 个回合开始各多抽 1 张**（perplexity 2026-09-18 + run-30 实弹：CLARITY_POWER:3 计数出现，使用时抽 1，次回合计数 3→2）。
- 铁心 HeartOfIron（药水）：对玩家施加 **PLATING_POWER 7**——时机见 powers.md 玩家镀层条目（战斗中途使用在玩家侧回合结束时给挡）。
- run-32 实弹（A1，2026-09-18，随机种子）：**Blood Potion 在 80 Max 时回血精确 +16 HP**（30→46，Boss 战 T7——20% Max 公式确认）。**Skill Potion 池 Act1 Boss T6 实弹**：开出 PrimalForce / **Impervious** / Offering——选 Impervious，生成牌免费（cost=0），给出 **28 挡**（基础 30 − 当时 Dex 税 2）；卡牌选择类药水生成的牌本回合免费，即使印刷费用 2–3。**Colorless Potion 池 Boss T8 实弹**：开出 Finesse / **Eternal Armor** / Bolas——选 Eternal Armor，免费（印刷 3 费豁免），对玩家给出 **PLATING_POWER 9**（回合结束 9 挡，之后每回合 −1——对属性吸取 Boss 的结构性反 Dex 税挡类）。火药水 20 伤实弹（海洋混混收头）。药槽满 @Control@ 死按钮类本局未出现——3/3 药槽下卡牌奖励按钮仍可领取。
