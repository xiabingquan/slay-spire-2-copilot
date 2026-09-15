# 敌人意图

敌人意图解读。标签格式观察自 v0.107.1（游戏 loc 表）；图标/行为语义来自
社区参考（slaythespire.gg、sts2-wiki）与实战。

- FORMAT_DAMAGE_SINGLE：造成 N 点伤害的攻击（N 显示为标签值）。
- FORMAT_DAMAGE_MULTI / 标签带 xN：攻击 N 次，每次按列出伤害（如 6x3 =
  原始 18 点）。
- FORMAT_STATUS_CARD_COUNT：向抽牌/弃牌堆加入状态牌，无直接伤害。
- FORMAT_EMPTY：无行动 / 占位。
- 攻击意图：敌人本回合计划造成伤害；显示数字为 Weak/Vulnerable/格挡
  修正前的原始伤害。
- 格挡/盾意图：敌人本回合计划获得格挡而非攻击。
- 增益意图：敌方强化——力量、Ritual、召唤、防御姿态
  （BURROWED/SOAR/TERRITORIAL）。
- 减益意图：敌方施加减益——Vulnerable、Weak、中毒、Frail、
  Chains of Binding。
- 未知意图：行动隐藏；稍后或满足条件后揭示。
- 蓄力/重击意图：高额蓄力一击（如 SLOW_POWER 精英：空意图慢速回合与
  约 23 伤害蓄力重击交替）；BURROWED 的蓄力意图在限时内破格挡可取消。
- Doom 意图（死灵相关战斗）：Doom 叠加体现在怪物行为中——注意 Doom 与
  敌方 HP 阈值的关系。
- 注意：原始 loc BBCode（如 [font_size=18]x3[/font_size]）可能泄漏到标签
  中（已知服务端待打磨项）——读取时自行剥离。
