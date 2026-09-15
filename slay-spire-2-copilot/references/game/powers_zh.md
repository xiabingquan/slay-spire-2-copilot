# 能力（powers）

战斗增益/减益的静态参考；名称与 state 中出现的 id 一致。

- VULNERABLE_POWER：目标受到的攻击伤害 +50%；在玩家身上时同样放大受到的伤害。
- WEAK_POWER：目标造成的攻击伤害约 -25%。
- FRAIL_POWER：获得的格挡减少；与 CHAINS_OF_BINDING 叠加时观察到格挡完全归零。
- SLIPPERY_POWER（如 墨宝）：首次受到的攻击伤害大减（观察到 Strike 6 -> 1）；
  充能每受击消耗一次——之后的攻击恢复全额。
- STRENGTH_POWER / RITUAL_POWER（敌方）：每回合力量增长——优先击杀。
- DEMON_FORM_POWER（玩家）：每回合 +力量；核心引擎。
- CONFUSED_POWER（来自 FAKE_SNECKO_EYE）：每次抽牌手牌费用随机——利用 0 费牌。
- PLATING_POWER（GORGET）：战斗开始时获得固定格挡。
- THORNS_POWER（BRONZE_SCALES）：被攻击时反伤。
- FLAME_BARRIER_POWER：临时荆棘 + 格挡。
- DUPPLICATION_POWER（DUPLICATOR 药水）：临时复制卡牌状态。
- INFESTED_POWER（异蛙寄生虫精英）：死亡时生成多只小怪（观察到 4 只约
  17-21hp）——AOE 留给召唤波，不要打在母体上。
- MINION_POWER：boss 标志——死亡时生成替补小怪。
- STOCK_POWER：机器人工厂标志——每次死亡生成下一形态直至战斗结束。
- RAMPART_POWER：活体盾牌盟友的格挡再生来源。
- RINGING_POWER（仪式兽 boss）：在玩家身上时剩余手牌 can_play 翻为 false——
  出牌封锁。
- SLOW_POWER（旧日雕像精英）：交替节奏——空意图的慢速回合接高额蓄力一击 +
  力量增长；重击回合前做好防御。
- TERRITORIAL / SOAR / BURROWED_POWER：精英/boss 防御姿态；burrowed 配合高额
  蓄力意图，限时破格挡可取消。
- SHRINK_POWER（缩小甲虫）：降低玩家攻击伤害，持续到该敌人死亡。
- CHAINS_OF_BINDING_POWER：女王 boss 减益；疑似格挡压制。
- ClarityPower 与 DrawCardsNextTurnPower：都提供下回合抽牌；叠加规则不同——
  Clarity 覆盖接下来 N 回合，DrawCardsNextTurn 仅下一回合。
- 存在惰性标记 power（如 FanOfKnives 被 Shiv 的目标判定查询）——仅凭存在
  就可能改变卡牌行为。
