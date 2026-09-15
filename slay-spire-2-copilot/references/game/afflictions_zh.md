# 状态与减益

卡牌绑定减益与状态牌的静态参考。

- BYRDONIS_EGG（巢穴/Sapphire Seed 事件）：不可打出（-1 费）的死抽——商店
  移除；在牌库中时休息点出现 HATCH 选项。
- SLIMED 类状态牌：敌方施加；部分可打出，效果轻微。
- DECAY / WOUND：敌方/事件状态牌；可打微量伤害或作为 SECOND_WIND 燃料；
  商店移除目标。
- RINGING：在玩家身上时手牌 can_play 翻为 false（RINGING_POWER）。
- 卡牌绑定减益（Bound、Entangled 等）是指向其 Power 逻辑的指针——实际效果
  见 powers_zh.md。
