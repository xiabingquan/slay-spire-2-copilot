# 敌人意图（intents）

确定性意图语义，来源：反编译类
`MegaCrit.Sts2.Core.MonsterMoves.Intents.*` 与 SpireBridge 紧凑视图约定
（`references/bridge/protocol.md`、`references/bridge/commands.md`）。
JSON state 中每个敌人：`intent: null | {"id": "...", "damage": N,
"times": N, "is_attack": bool}`；`--json` 另给出每个意图的
`damage`/`hits`/`class`/`type`。

## 意图类 -> 紧凑视图标签

- SingleAttackIntent（IntentType.Attack）：单次攻击。标签 =
  FORMAT_DAMAGE_SINGLE → 紧凑视图显示伤害数字，如 `8`。该数字是游戏内
  实时伤害预览（`GetSingleDamage` 会跑伤害 hook，下限 0）——已包含
  力量/虚弱/易伤等修正，并非招式原始值。
- MultiAttackIntent（IntentType.Attack）：攻击 Repeats 次。标签 =
  FORMAT_DAMAGE_MULTI（Damage + Repeat）→ 紧凑视图显示 每段×次数，
  如 `3×7`（7 段每段 3；总伤 = 每段 × 次数）。每段数字同样为实时预览。
- DeathBlowIntent（IntentType.DeathBlow）：SingleAttackIntent 子类，
  使用致死一击图标——攻击语义不变；标签仍为伤害数字。
- BuffIntent（IntentType.Buff）：敌人自我/友方强化（力量、仪式、姿态、
  部分招式的召唤等）。loc 中标签为 FORMAT_EMPTY → bridge 服务端替换为
  意图类型；紧凑视图显示 `Buff` 或 `Buff(招式id)`（如
  `Buff(PREPARE_MOVE)`）。
- DebuffIntent（IntentType.Debuff / DebuffStrong）：敌人施加减益
  （易伤、虚弱、中毒、脆弱、卡牌绑定减益等）。紧凑视图显示 `Debuff`；
  strong=true 时为 `DebuffStrong`。
- DefendIntent（IntentType.Defend）：敌人本回合获得格挡。显示 `Defend`。
- HealIntent（IntentType.Heal）：敌人治疗（也用于复活招式，如
  IllusionPower 的 REVIVE_MOVE）。显示 `Heal`。
- SleepIntent（IntentType.Sleep）：敌人沉睡/跳过行动（AsleepPower /
  SlumberPower 姿态）。显示 `Sleep`。
- StunIntent（IntentType.Stun）：敌人被击晕/本回合跳过行动（钻地破防、
  醒来眩晕、Imbalanced 等）。显示 `Stun`。
- SummonIntent（IntentType.Summon）：敌人本回合召唤小怪。显示 `Summon`。
- StatusIntent（IntentType.StatusCard）：向玩家牌堆加入 `count` 张状态牌，
  无直接伤害。标签 = FORMAT_STATUS_CARD_COUNT → 紧凑视图显示卡牌数量。
- CardDebuffIntent（IntentType.CardDebuff）：向玩家牌堆注入状态/诅咒牌
  （常与攻击同招）。loc 标签为 FORMAT_EMPTY → 紧凑视图回退为
  `CardDebuff(招式id)`。按「牌组污染」应对，而非伤害——除非该招同时带
  攻击（见下条组合标签）。
- EscapeIntent（IntentType.Escape）：敌人本回合逃离战斗。显示 `Escape`。
- HiddenIntent（IntentType.Hidden）：无图标、无悬浮提示——行动完全隐藏。
  显示 `Hidden`。
- UnknownIntent（IntentType.Unknown）：行动尚未揭示；稍后或满足条件后
  揭示。显示 `Unknown`。

## 组合与展示说明

- 组合招式（攻击 + 状态注入，如 Vantom 的 DISMEMBER）两部分都会出现：
  `--json` 同时有 `damage`/`times` 与 CardDebuff 类；紧凑视图标签形如
  `17; 3` = 同一招式攻击 17 且注入状态牌。`4×2` / `6×2` / `8×2` =
  多段攻击（每段 × 次数）。
- 攻击图标/动画档位按总伤害选择：<5 → 档 1，<10 → 档 2，<20 → 档 3，
  <40 → 档 4，>=40 → 档 5（仅展示；计算以标签数字为准）。
- loc 泄漏：原始 loc 键如 `intents:FORMAT_EMPTY`（或 BBCode 片段如
  `[font_size=18]x3[/font_size]`）可能泄漏进标签；bridge 服务端将
  FORMAT_EMPTY 替换为意图类型，紧凑视图回退为 `Type(招式id)`。读取时
  自行剥离 BBCode。
- JSON 中 `intent: null` = 此刻无意图数据（如过渡中）。
- 确定性读法：数字标签是伤害预览；单词标签（`Buff`/`Debuff`/`Defend`/
  `Heal`/`Sleep`/`Stun`/`Summon`/`Escape`/`Hidden`/`Unknown`）不带数字
  ——具体行为查怪物招式表（monsters_zh.md）或 `--json`。
