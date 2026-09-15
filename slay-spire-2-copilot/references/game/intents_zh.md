# 敌人意图

标签来自游戏 loc 表；游玩中观察到的格式：

- FORMAT_DAMAGE_SINGLE：造成 N 点伤害的攻击（N 显示为标签值）。
- FORMAT_DAMAGE_MULTI / 标签带 xN：攻击 N 次，每次按列出伤害。
- FORMAT_STATUS_CARD_COUNT：向抽牌/弃牌堆加入状态牌，无直接伤害。
- FORMAT_EMPTY：无行动 / 占位。

注意：原始 loc BBCode（如 [font_size=18]x3[/font_size]）可能泄漏到标签中
（已知的服务端待打磨项）。
