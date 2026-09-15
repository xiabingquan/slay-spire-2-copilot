# 状态与减益

卡牌绑定减益与状态牌。来源：gamerblurb 状态牌列表、游戏 xml 减益类名、
spire-codex、v0.107.1 实战。

## 卡牌绑定减益（逻辑宿主）

- BOUND：逻辑在 CHAINS_OF_BINDING_POWER——格挡压制（女王 boss 减益）。
- ENTANGLED：逻辑在 TANGLED_POWER。
- GALVANIZED：逻辑在 GALVANIC_POWER。
- HEXED：逻辑在 HEX_POWER。
- RINGING：逻辑在 RINGING_POWER——手牌 can_play 翻为 false（出牌封锁）。
- SMOG：逻辑在 SMOGGY_POWER。
- TAINTED：逻辑在 TAINTED_POWER。

## 状态牌

- BECKON：可打出，无额外费用；回合结束仍在手牌则失去 6 HP。
- BURN：不可打出；回合结束仍在手牌则对你造成 2 点伤害。
- DAZED：不可打出；虚无（Ethereal）——回合结束未打出则消失。
- DEBRIS：可打出，1 能量；打出时消耗（Exhaust）。
- DISINTEGRATION：可打出；回合结束对你造成 6 点伤害。
- FRANTIC_ESCAPE：可打出，1 能量；使沙坑（Sandpit）+1；每次使用费用 +1。
- INFECTION：不可打出；回合结束仍在手牌则对你造成 3 点伤害。
- MIND_ROT：可打出；每回合抽牌 -1。
- SLIMED：可打出，1 能量；抽 1 张牌；打出时消耗。
- SLOTH：可打出；每回合最多打出 3 张牌。
- SOOT：不可打出；堵塞手牌/牌库（遗物 Biiig Hug 洗牌时会加入）。
- TOXIC：可打出，1 能量；回合结束仍在手牌则造成 5 点伤害，然后消耗。
- VOID：不可打出；虚无；抽到它会消耗无色能量（TURBO 的弃牌代价）。
- WASTE_AWAY：可打出；每回合少获得 1 点无色能量。
- WOUND：不可打出；堵塞手牌/牌库——SECOND_WIND 的燃料。
- BYRDONIS_EGG：不可打出（-1 费）的死抽，来自巢穴/Sapphire Seed 事件；
  在牌库中时休息点出现 HATCH 选项；商店移除。

## 状态牌协同卡（收益端）

- COMPACT（Defect）：手牌中的状态牌变为 Fuel 并获得格挡。
- FLAK_CANNON：消耗所有状态牌，每张造成伤害。
- ITERATION：每回合首次抽到状态牌时额外抽牌。
- ROCKET_PUNCH：生成状态牌时变为免费。
- SMOKESTACK：每次生成状态牌时对所有敌人造成伤害。
- TRASH_TO_TREASURE：生成状态牌时引导随机充能球。
