# 卡牌

分角色卡牌参考。费用/效果来自社区数据库（stratgg.com 角色页、
spire-codex.com、mobalytics、namu.wiki），与 v0.107.1 实战观察及游戏内部
类名交叉核对。共通模式：Strike = 1 费攻击造成 6 点伤害；Defend = 1 费
技能获得 5 格挡（每个角色各有一份）。

## Ironclad（铁甲战士）

- STRIKE_IRONCLAD：1，攻击，造成 6 点伤害。
- DEFEND_IRONCLAD：1，技能，获得 5 格挡。
- BASH：2，攻击，造成 8 点伤害；施加 2 层 Vulnerable。
- ANGER：0，攻击，造成 6 点伤害；向弃牌堆加入自身拷贝。
- ARMAMENTS：1，技能，获得 5 格挡；升级一张手牌。
- ASHEN_STRIKE：1，攻击，造成 6 点伤害，消耗堆每张牌 +3。
- BATTLE_TRANCE：0，技能，抽 3 张牌；本回合不能再抽牌。
- BLUDGEON：3，攻击，造成 32 点伤害（配合升级/易伤实测 35-49）。
- BLOOD_WALL：2，技能，消耗 2 HP，获得 16 格挡（实战：对附近敌人约 8 点
  顺带伤害；低于约 5 HP 勿打）。
- BLOODLETTING：0，技能，消耗 3 HP，获得 2 能量。
- BODY_SLAM：1，攻击，按当前格挡值造成伤害。
- BREAKTHROUGH：1，攻击，对所有敌人造成 9 点伤害；消耗 1 HP。
- BULLY：0，攻击，造成 4 点伤害，目标每层 Vulnerable +2。
- BURNING_PACT：1，技能，消耗 1 张牌；抽 2 张牌。
- CINDER：2，攻击，造成 17 点伤害；消耗抽牌堆顶牌。
- DEMONIC_SHIELD：0，技能，消耗 1 HP；将等同你格挡值的格挡给予另一名玩家。
- DISMANTLE：1，攻击，造成 8 点伤害；目标带 Vulnerable 时命中两次
  （实战：另可移除一个敌方 power/充能）。
- FIGHT_ME：2，攻击，约 10 点伤害；对玩家与目标双方赋予 STRENGTH
  （"决斗邀请"）。
- HAVOC：1，技能，打出抽牌堆顶牌然后将其消耗。
- HEADBUTT：1，攻击，造成 9 点伤害；将一张弃牌放到抽牌堆顶。
- IRON_WAVE：1，攻击，造成 5 点伤害并获得 5 格挡。
- MOLTEN_FIST：1，攻击，造成 10 点伤害；目标的 Vulnerable 翻倍。
- PERFECTED_STRIKE：2，攻击，造成 6 点伤害，每张名称含 "Strike" 的
  持有牌 +2（实测 19-32）。
- POMMEL_STRIKE：1，攻击，造成 9 点伤害；抽 1 张牌。
- RAMPAGE：1，攻击，约 6 点基础伤害；随打出次数增长。
- SECOND_WIND：消耗手牌全部卡牌；每张被消耗牌获得格挡（boss 战实测 30+）。
- SETUP_STRIKE：1，攻击，造成 7 点伤害；本回合获得 2 力量。
- SHRUG_IT_OFF：1，技能，获得 8 格挡；抽 1 张牌。
- SWORD_BOOMERANG：1，攻击，对随机敌人造成 3 点伤害 ×3；力量按段生效。
- THUNDERCLAP：1，攻击，对所有敌人造成 4 点伤害；各施加 1 层 Vulnerable。
- TREMBLE：1，技能，施加 2 层 Vulnerable。
- TRUE_GRIT：1，技能，获得 7 格挡；消耗 1 张随机手牌。
- TWIN_STRIKE：1，攻击，造成 5 点伤害 ×2；力量按段生效。
- UPPERCUT：2，攻击，伤害 + Weak + Vulnerable（升级版实测约 8-21；
  双减益核心牌）。
- WHIRLWIND：X，攻击，对所有敌人造成 X 次伤害（配合力量/能量实测
  总伤 27-81）。
- Ironclad 牌池待补效果名单：Demon Form、Limit Break、Heavy Blade、
  Corruption、Feel No Pain、Sentinel、Offering、Immolate、Reaper、
  Dark Embrace、Pact's End、Feed、Fiend Fire、Impervious、Inflame、
  Juggernaut、Rage、Rupture、Shockwave、Hemokinesis、Dual Wield、
  Entrench、Flame Barrier、Hellraiser、Hegemony、Hotfix、
  I Am Invincible、Kingly Kick、Knockout Blow、Mad Science、Omnislice、
  Scavenge、Scourge、Sovereign Blade、Spoils Map、Terraforming、
  The Hunt、Unmovable。

## Silent（寂静）

- STRIKE_SILENT：1，攻击，造成 6 点伤害。
- DEFEND_SILENT：1，技能，获得 5 格挡。
- NEUTRALIZE：0，攻击，造成 3 点伤害；施加 1 层 Weak。
- SURVIVOR：1，技能，获得 8 格挡；弃置 1 张牌。
- ACROBATICS：1，技能，抽 3 张牌；弃置 1 张牌。
- ACCURACY：1，能力，Shiv 额外造成 4 点伤害。
- ANTICIPATE：0，技能，本回合获得 3 敏捷。
- BACKFLIP：1，技能，获得 5 格挡；抽 2 张牌。
- BACKSTAB：0，攻击，造成 11 点伤害。
- BLADE_DANCE：1，技能，向手牌加入 3 张 Shiv。
- BLUR：1，技能，获得 5 格挡；下回合开始时格挡不被移除。
- BOUNCING_FLASK：2，技能，对随机敌人施加 3 层中毒 ×3。
- BUBBLE_BUBBLE：1，技能，若目标已有中毒，施加 9 层中毒。
- CALCULATED_GAMBLE：0，技能，弃置全部手牌，然后抽取等量牌。
- CLOAK_AND_DAGGER：1，技能，获得 6 格挡；向手牌加入 1 张 Shiv。
- DAGGER_SPRAY：1，攻击，对所有敌人造成 4 点伤害 ×2。
- DAGGER_THROW：1，攻击，造成 9 点伤害；抽 1 张牌；弃 1 张牌。
- DEADLY_POISON：1，技能，施加 5 层中毒。
- DEFLECT：0，技能，获得 4 格挡。
- DODGE_AND_ROLL：1，技能，获得 4 格挡；下回合再获得 4 格挡。
- FLICK_FLACK：1，攻击（Sly），对所有敌人造成 7 点伤害（升级 9）。
- LEADING_STRIKE：1，攻击，造成 7 点伤害；向手牌加入 1 张 Shiv。
- PIERCING_WAIL：1，技能，本回合所有敌人失去 6 力量。
- POISONED_STAB：1，攻击，造成 6 点伤害；施加 3 层中毒。
- PREPARED：0，技能，抽 1 张牌；弃 1 张牌。
- RICOCHET：2，攻击（Sly），对随机敌人造成 3 点伤害 ×4（升级 5 段；
  namu 标注费用 1——版本差异）。
- SLICE：0，攻击，造成 6 点伤害。
- SNAKEBITE：2，技能，施加 7 层中毒。
- SUCKER_PUNCH：1，攻击，造成 8 点伤害；施加 1 层 Weak。
- UNTOUCHABLE：2，技能（Sly），获得 9 格挡（升级 12；namu 标注费用 1
  ——版本差异）。
- Sly 关键词卡待补数据：Abrasive（Sly，+1 敏捷与 +1 荆棘，荆棘升级至 6）、
  Tactician（Sly，被弃置时获得能量）、Haze（Sly）。
- Silent 牌池待补效果名单：Catalyst、Corpse Explosion、Noxious Fumes、
  Adrenaline、Well-Laid Plans、Outbreak、Alchemize、Bullet Time、Burst、
  Storm of Steel、Envenom、Escape Plan、Expertise、Finisher、Flechettes、
  Footwork、Grand Finale、Leg Sweep、Malaise、Master of Strategy、
  Nightmare、Phantom Blades、Pinpoint、Putrefy、Reflex、Sneaky、
  Tools of the Trade、Wraith Form。

## Defect（缺陷）

- STRIKE_DEFECT：1，攻击，造成 6 点伤害。
- DEFEND_DEFECT：1，技能，获得 5 格挡。
- ZAP：1，技能，引导 1 个闪电球。
- DUALCAST：1，技能，激发最右侧充能球两次。
- BALL_LIGHTNING：1，攻击，造成 7 点伤害；引导 1 个闪电球。
- BARRAGE：1，攻击，每个已引导充能球造成 5 点伤害。
- BEAM_CELL：0，攻击，造成 3 点伤害；施加 1 层 Vulnerable。
- BOOT_SEQUENCE：0，技能，获得 10 格挡。
- BOOST_AWAY：0，技能，获得 6 格挡；向弃牌堆加入 1 张 Dazed。
- BULK_UP：2，能力，失去 1 个充能球槽；获得 2 力量 2 敏捷。
- CAPACITOR：1，能力，获得 2 个充能球槽。
- CHAOS：1，技能，引导 1 个随机充能球。
- CHARGE_BATTERY：1，技能，获得 7 格挡；下回合获得能量。
- CHILL：0，技能，每个敌人引导 1 个冰霜球。
- CLAW：0，攻击，造成 3 点伤害；本场战斗所有 Claw 伤害 +2。
- COLD_SNAP：1，攻击，造成 6 点伤害；引导 1 个冰霜球。
- COMPACT：1，技能，获得 6 格挡；手牌中的状态牌变为 Fuel。
- COMPILE_DRIVER：1，攻击，造成 7 点伤害；每种充能球类型抽 1 张牌。
- COOLHEADED：1，技能，引导 1 个冰霜球；抽 1 张牌。
- FOCUSED_STRIKE：1，攻击，造成 9 点伤害；本回合获得 1 Focus。
- GO_FOR_THE_EYES：0，攻击，造成 3 点伤害；若敌人意图攻击则施加 1 Weak。
- GUNK_UP：1，攻击，造成 4 点伤害 ×3；向弃牌堆加入 1 张 Slimed。
- HOLOGRAM：1，技能，获得 3 格挡；将弃牌堆一张牌收回手牌。
- HOTFIX：0，技能，本回合获得 2 Focus。
- LEAP：1，技能，获得 9 格挡。
- LIGHTNING_ROD：1，技能，获得 4 格挡；接下来 2 回合开始时引导闪电球。
- MOMENTUM_STRIKE：1，攻击，造成 10 点伤害；自身费用降为 0。
- SWEEPING_BEAM：1，攻击，对所有敌人造成 6 点伤害；抽 1 张牌。
- TURBO：0，技能，获得 2 能量；向弃牌堆加入 1 张 Void。
- UPROAR：2，攻击，造成 5 点伤害 ×2；从抽牌堆打出一张随机攻击牌。
- Defect 牌池待补效果名单：All for One、Biased Cognition、Buffer、
  Colossus、Consume、Creative AI、Darkness、Defragment、Double Energy、
  Echo Form、Fission、Fusion、Glacier、Hello World、Hyperbeam、Loop、
  Machine Learning、Meteor Strike、Multi-Cast、Rainbow、Reboot、Recursion、
  Recycle、Reinforced Body、Seek、Skim、Steam Barrier、Storm、Sunder、
  Tempest、Tesla Coil、White Noise。

## Necrobinder（死灵束缚者）

- STRIKE_NECROBINDER：1，攻击，造成 6 点伤害。
- DEFEND_NECROBINDER：1，技能，获得 5 格挡。
- BODYGUARD：1，技能，Summon 5。
- UNLEASH：1，攻击，Osty 造成 6 点伤害 + 等同 Osty 当前 HP 的额外伤害。
- AFTERLIFE：1，技能，Summon 6。
- BLIGHT_STRIKE：1，攻击，造成 8 点伤害；施加等同伤害值的 Doom。
- BONE_SHARDS：1，攻击，若 Osty 存活：Osty 对所有敌人造成 9 点伤害，
  你获得 9 格挡，随后 Osty 死亡。
- BORROWED_TIME：0，技能，对自身施加 3 层 Doom；获得 1 能量。
- BURY：4+，攻击，造成 52 点伤害。
- CALCIFY：1，能力，Osty 的攻击额外造成 4 点伤害。
- CAPTURE_SPIRIT：1，技能，敌人失去 3 HP；向抽牌堆加入 3 张 Soul。
- CLEANSE：1，技能，Summon 3；消耗抽牌堆 1 张牌。
- DEFILE：1，攻击，造成 13 点伤害。
- DEFY：1，技能，获得 6 格挡；施加 1 层 Weak。
- DRAIN_POWER：1，攻击，造成 10 点伤害；升级弃牌堆 2 张随机牌。
- FEAR：1，攻击，造成 7 点伤害；施加 1 层 Vulnerable。
- FLATTEN：2，攻击，Osty 造成 12 点伤害；若 Osty 本回合已攻击则费用为 0。
- GRAVE_WARDEN：1，技能，获得 8 格挡；向抽牌堆加入 1 张 Soul。
- GRAVEBLAST：1，攻击，造成 4 点伤害；将弃牌堆一张牌放入手牌。
- INVOKE：1，技能，下回合 Summon 2 并获得 2 能量。
- NEGATIVE_PULSE：1，技能，获得 5 格挡；对所有敌人施加 7 层 Doom。
- POKE：0，攻击，Osty 造成 6 点伤害。
- PULL_AGGRO：2，技能，Summon 4；获得 7 格挡。
- REAP：3，攻击，造成 27 点伤害。
- REAVE：1，攻击，造成 9 点伤害；向抽牌堆加入 1 张 Soul。
- SCOURGE：1，技能，施加 13 层 Doom；抽 1 张牌。
- SCULPTING_STRIKE：1，攻击，造成 8 点伤害；为一张手牌添加 Ethereal。
- SNAP：1，攻击，Osty 造成 7 点伤害；为一张手牌添加 Retain。
- SOW：1，攻击，对所有敌人造成 8 点伤害。
- WISP：0，技能，获得 1 能量。
- Necrobinder 牌池待补效果名单：Death's Door、Death March、
  Necro Mastery、Undeath、Call of the Void、Legion of Bone、
  Minion Dive Bomb、Minion Sacrifice、Minion Strike、Deathbringer、
  End of Days、Eidolon、Haunt、Howl from Beyond、Memento Mori、
  Reanimate、Shatter、Soul Storm、Summon Forth、The Scythe。

## Regent（摄政王）

- STRIKE_REGENT：1，攻击，造成 6 点伤害。
- DEFEND_REGENT：1，技能，获得 5 格挡。
- FALLING_STAR：0，攻击，造成 7 点伤害；施加 1 层 Weak；施加 1 层
  Vulnerable。
- VENERATE：1，技能，获得 2 点星星（★）。
- ALIGNMENT：0，技能，获得 2 能量。
- ASTRAL_PULSE：0，攻击，对所有敌人造成 14 点伤害。
- BEGONE：1，攻击，造成 4 点伤害；将一张手牌变为 Minion Dive Bomb。
- BLACK_HOLE：1，能力，每次消耗或获得星星时，对所有敌人造成 3 点伤害。
- BULWARK：2，技能，获得 13 格挡；Forge 10。
- CELESTIAL_MIGHT：2，攻击，造成 6 点伤害 ×3。
- CHARGE!!：1，技能，将抽牌堆 2 张牌变为 Minion Strike。
- CHILD_OF_THE_STARS：1，能力，每次消耗星星时，每颗星获得 2 格挡。
- CLOAK_OF_STARS：0，技能，获得 7 格挡。
- COLLISION_COURSE：0，攻击，造成 9 点伤害；向手牌加入 1 张 Debris。
- CONQUEROR：1，技能，Forge 3；本回合 Sovereign Blade 对一个敌人伤害翻倍。
- COSMIC_INDIFFERENCE：1，技能，获得 6 格挡；将弃牌堆一张牌放到抽牌堆顶。
- CRESCENT_SPEAR：1，攻击，造成 6 点伤害，牌库中每张星费牌 +2。
- CRUSH_UNDER：1，攻击，对所有敌人造成 7 点伤害；本回合其失去 1 力量。
- GATHER_LIGHT：1，技能，获得 7 格挡；获得 1 颗星。
- GLITTERSTREAM：2，技能，获得 11 格挡；下回合获得 4 格挡。
- GLOW：1，技能，获得 1 颗星；抽 2 张牌。
- GUIDING_STAR：1，攻击，造成 12 点伤害；下回合抽 2 张牌。
- HIDDEN_CACHE：1，技能，获得 1 颗星；下回合获得 3 颗星。
- KNOW_THY_PLACE：0，技能，施加 1 层 Weak；施加 1 层 Vulnerable。
- PATTER：1，技能，获得 8 格挡；获得 2 点 Vigor。
- PHOTON_CUT：1，攻击，造成 10 点伤害；抽 1 张牌；将一张手牌放到抽牌堆顶。
- REFINE_BLADE：1，技能，Forge 6；下回合获得能量。
- SOLAR_STRIKE：1，攻击，造成 8 点伤害；获得 1 颗星。
- SPOILS_OF_BATTLE：1，技能，Forge 10。
- WROUGHT_IN_WAR：0，攻击，造成 7 点伤害；Forge 5。
- Regent 牌池待补效果名单：Seven Stars、Summon Forth、Seeking Edge、
  Beat into Shape、Kingly Punch、Lunar Blast、Manifest Authority、
  Monarch's Gaze、Pagestorm、Protector、Royal Gamble、Royalties、
  Stratagem、The Sealed Throne、Tyranny、Heavenly Drill、Helix Drill。

## 无色 / 事件 / 状态牌（牌池，效果部分待补）

- ABRASIVE / ADAPTIVE_STRIKE / APOTHEOSIS / APPARITION / ASCENDERS_BANE /
  BAD_LUCK / BURN / BYRDONIS_EGG（不可打出的 -1 费状态牌，见
  afflictions_zh.md）/ CLUMSY / DARK_SHACKLES / DAZED / DEBT / DECAY /
  DOUBT / ENLIGHTENMENT / EXPECT_A_FIGHT / FRANTIC_ESCAPE / FRIENDSHIP /
  GOLD_AXE / GREED / INJURY / JACK_OF_ALL_TRADES / LANTERN_KEY /
  MIND_BLAST / NORMALITY / NULL / PANACHE / POOR_SLEEP / PYRE / REGRET /
  SECRET_TECHNIQUE / SECRET_WEAPON / SHAME / SLIMED / SOOT / SPOILS_MAP /
  STOMP / THINKING_AHEAD / WISH / WOUND / WRITHE。
- SHIV：0，攻击衍生物，造成伤害（Silent 套牌产出；数据库数据中 Accuracy
  +4）。

## 界面备注（卡牌奖励 / 选择）

- 药水栏满时奖励界面可能显示不可领取的按钮——点击无效；proceed 离开该界面。
- 多数 card_reward 界面有跳过按钮；NDeckCardSelectScreen 移除流程没有
  （必须选一张）。
- 事件 AROMA_OF_CHAOS 的 "LET_GO"：打开牌组变形——任选一张牌库卡，随机
  变形（观察到 STRIKE -> POMMEL_STRIKE）。
- 牌池规模（spire-codex）：Ironclad 87、Silent 88、Defect 88、
  Necrobinder 88、Regent 88；含无色/状态/衍生物共 577 张。
