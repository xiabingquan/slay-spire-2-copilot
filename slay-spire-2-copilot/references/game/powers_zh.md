# 能力（powers）

战斗增益/减益参考；名称与 state 中出现的 id 一致。数值来自社区数据库
（sts2-wiki、fandom、metabot），并与 v0.107.1 实战观察交叉核对。

## 核心战斗状态

- VULNERABLE_POWER：目标受到的攻击伤害 +50%（遗物 Paper Phrog 对铁甲
  战士提升为 +75%）；在玩家身上时同样放大受到的攻击伤害。
- WEAK_POWER：目标造成的攻击伤害 -25%（遗物 Paper Krane：带 Weak 的敌人
  对寂静造成的伤害 -40%）。
- FRAIL_POWER：目标从卡牌获得的格挡 -25%。
- STRENGTH_POWER：每次攻击命中附加固定伤害；多段攻击逐段生效。
- DEXTERITY_POWER：每次获得格挡的卡牌附加固定格挡。
- RITUAL_POWER（敌方）：每回合获得力量——优先击杀。
- POISON（中毒）：回合开始失去 HP，随后毒层每次触发 -1。
- THORNS_POWER：受击时反伤攻击者（BRONZE_SCALES：3 点）。
- PLATING_POWER（镀甲，如 GORGET）：回合结束获得格挡；每次受到未格挡的
  攻击伤害时失去 1 层。
- REGEN（再生）：每回合结束回复 HP，随后每回合 -1。
- CONFUSED_POWER（FAKE_SNECKO_EYE / Snecko Eye）：抽牌时费用随机（常见
  0-3 区间）。
- SLOW_POWER（敌方，如旧日雕像精英）：本回合你打出的卡牌越多，该敌人
  受到的攻击伤害越高（约每张 +10%，wiki 数值）；实战中与高额蓄力重击
  交替出现。
- MINION_POWER：标记召唤物（死灵/摄政王套牌、boss 召唤小怪）。
- DOOM_POWER（死灵机制）：叠加死兆；Doom >= HP 时击杀（遗物 Undying
  Sigil：Doom >= HP 的敌人伤害 -50%，且 Doom 改为其回合开始时触发）。
- FOCUS（缺陷）：强化充能球的被动与激发效果；可为负（Hyperbeam 对持有
  者施加 Focus 下降）。
- VIGOR_POWER：下一次攻击附加的额外伤害（遗物 Akabeko：战斗开始 8 点）。
- INTANGIBLE_POWER：受到的攻击伤害降为 1（经典效果）。
- SURROUNDED_POWER 与 BACK_ATTACK_LEFT/RIGHT：站位标记——BackAttack
  标记供 Surrounded 判定侧翼规则。

## 卡牌绑定减益 power（另见 afflictions.md）

- CHAINS_OF_BINDING_POWER：格挡压制（女王 boss 减益；与 Frail 叠加时实测
  格挡归零）。
- RINGING_POWER：手牌 can_play 翻为 false（出牌封锁）。
- TANGLED_POWER / GALVANIC_POWER / HEX_POWER / SMOGGY_POWER /
  TAINTED_POWER：分别承载 Entangled / Galvanized / Hexed / Smog / Tainted
  五种卡牌绑定减益的逻辑。

## 角色套牌 power

- DEMON_FORM_POWER（铁甲战士）：数回合内每回合 +力量；引擎牌。
- ClarityPower 与 DrawCardsNextTurnPower：下回合（们）额外抽牌；Clarity
  覆盖接下来 N 回合，DrawCardsNextTurn 仅下一回合。
- TemporaryStrength / FlexPotionPower：回合结束过期的临时力量（Flex
  药水模型）。
- DIE_FOR_YOU_POWER、OBLIVION_POWER、MAYHEM_POWER、STAMPEDE_POWER、
  PIERCING_WAIL_POWER、THIEVERY_POWER、SURPRISE_POWER、THE_BOMB_POWER、
  THE_HUNT_POWER、PARRY_POWER、SEEKING_EDGE_POWER、ILLUSION_POWER、
  REATTACH_POWER、ESCAPE_ARTIST_POWER、ACCELERANT_POWER、
  FAN_OF_KNIVES_POWER：由卡牌或怪物宿主承载——效果随宿主卡/怪（见
  cards.md；如 TheHunt 只是成功视觉标记、Accelerant 使中毒重复触发、
  FanOfKnives/Parry/SeekingEdge 为被 Shiv / Sovereign Blade 查询的惰性
  标记）。

## 实战观察（v0.107.1）

- SLIPPERY_POWER（如 墨宝）：首次受到的攻击伤害大减（Strike 6 -> 1）；
  充能每受击消耗一次。
- SHRINK_POWER（缩小甲虫）：降低玩家攻击伤害，持续到该敌人死亡。
- INFESTED_POWER（异蛙寄生虫精英）：死亡时生成 4 只约 17-21hp 小怪——
  AOE 留给召唤波。
- STOCK_POWER（机器人工厂）：每次死亡生成下一形态。
- RAMPART_POWER：活体盾牌盟友的格挡再生。
- BURROWED / TERRITORIAL / SOAR：精英/boss 防御姿态；burrowed 配合高额
  蓄力意图，限时破格挡可取消。
- DUPPLICATION_POWER（DUPLICATOR 药水）：临时复制卡牌状态。
