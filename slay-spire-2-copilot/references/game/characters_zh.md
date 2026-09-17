# 角色

角色参考（确定性机制，仅含精确数值）。来源：反编译源码
`MegaCrit.Sts2.Core.Models.Characters` + 初始遗物
`MegaCrit.Sts2.Core.Models.Relics` + 解锁门槛
`MegaCrit.Sts2.Core.Unlocks/UnlockState.cs`（/tmp/sts2-decomp）。
括号内为简中译名。

五名可玩角色初始金币均为 99（每个 CharacterModel `StartingGold => 99`）。

## 可玩角色

- IRONCLAD（铁甲战士）— 80 HP，男性，名称色红。初始遗物：BURNING_BLOOD（燃烧之血）——战斗胜利后回复 6 HP（其升级版 Black Blood=黑暗之血 回复 12）。初始牌组（10 张）：Strike×5、Defend×4、Bash。卡池：IroncladCardPool。`UnlocksAfterRunAs => null`——角色模型层面始终解锁。
- SILENT（静默猎手）— 70 HP，女性，绿色。初始遗物：RING_OF_THE_SNAKE（蛇之戒指）——仅第 1 回合抽牌 +2（`TurnNumber > 1` 返回基础抽牌数）。初始牌组（12 张）：Strike×5、Defend×5、Neutralize=中和、Survivor=生存者。卡池：SilentCardPool。`UnlocksAfterRunAs => null`（源码注释：任意角色完成一局即可解锁她）；名单可用性另受下方 UnlockState 门槛约束。
- DEFECT（故障机器人）— 75 HP，中性，蓝色。初始遗物：CRACKED_CORE（破损核心）——第 1 回合引导 1 个闪电球（`BeforeSideTurnStart`，条件 `TurnNumber <= 1`）。基础充能球槽：3（`BaseOrbSlotCount`）。初始牌组（10 张）：Strike×4、Defend×4、Zap=电击、Dualcast=双重释放。卡池：DefectCardPool。`UnlocksAfterRunAs => Necrobinder`。
- NECROBINDER（亡灵契约师）— 66 HP，女性，紫色。初始遗物：BOUND_PHYLACTERY（缚魂命匣）——战斗开始 Summon Osty 1（`BeforeCombatStart`）；后续回合若 Osty 不在场，能量重置后重新召唤（`AfterEnergyResetLate`，第 1 回合除外）。SpawnsPets = true。初始牌组（10 张）：Strike×4、Defend×4、Bodyguard=护卫、Unleash=出击。卡池：NecrobinderCardPool。`UnlocksAfterRunAs => Regent`。
- REGENT（储君）— 75 HP，男性，橙色；星数计数器常显（`ShouldAlwaysShowStarCounter`）。初始遗物：DIVINE_RIGHT（天赋君权）——进入战斗房时 +3 星星（`AfterRoomEntered`）。初始牌组（10 张）：Strike×4、Defend×4、FallingStar=陨星、Venerate=崇拜。卡池：RegentCardPool。`UnlocksAfterRunAs => Silent`。

state 快照角色字段 id：IRONCLAD、SILENT、DEFECT、NECROBINDER、REGENT。仅测试用 id（正常对局不可玩）：Deprived、RandomCharacter、DeprecatedCharacter。

## 解锁门槛（确定性游戏规则）

- `UnlockState.Characters` 以 `ModelDb.AllCharacters` 为起点，随后移除：
  - Silent——除非 `IsEpochRevealed<Silent1Epoch>()`
  - Regent——除非 `IsEpochRevealed<Regent1Epoch>()`
  - Necrobinder——除非 `IsEpochRevealed<Necrobinder1Epoch>()`
  - Defect——除非 `IsEpochRevealed<Defect1Epoch>()`
  - Ironclad 永不移除——名单中始终包含 Ironclad。
- 角色模型的 `UnlocksAfterRunAs` 设计链：Ironclad 与 Silent 为 null（模型层面无跑局前置）；Regent 在 Silent 之后；Necrobinder 在 Regent 之后；Defect 在 Necrobinder 之后。名单实际可用还需玩家 UnlockState（Timeline 进度存档）中对应 Epoch 已被揭示。
- `UnlockState` 同时以 Epoch 门槛过滤远古/遗物/药水/卡牌内容：例如 蔓生之地 的 `GetUnlockedAncients` 在 `NeowEpoch` 未揭示时移除 Neow；水底码头 对 Neow 施加同样的 NeowEpoch 门槛；虫巢 在 `OrobasEpoch` 未揭示时移除 Orobas；荣光之殿的三位远古（Nonupeipe、Tanx、Vakuu）无门槛；共享远古 Darv 在 `DarvEpoch` 未揭示时移除。遗物/药水/卡池经 `GetUnlockedRelics/Potions/Cards(this)` 过滤。
- 解锁管线（Epoch 实际如何被揭示——反编译，2026-09-17）：game_over 分数条按 `_agnosticEpochUnlockOrder`（18 个无关角色节点：Colorless/Relic/Potion/Underdocks/Act2B/Act3B/Event——**永不含角色节点**）顺序授予；角色解锁只能走 Timeline 链：`NeowEpoch.QueueUnlocks()` 写 `ObtainEpochOverride(Silent1Epoch, ObtainedNoSlot)` → Timeline 点击槽位 → `RevealEpoch` + `Silent1Epoch.QueueUnlocks()`（PendingCharacterUnlock + 角色解锁 UI + `UnlockSlot` 扩展槽并把 ObtainedNoSlot 晋升为 Obtained）。赚取条件：Silent1——任意角色完成一局；Regent1/Necrobinder1/Defect1——`UnlocksAfterRunAs` 链（分别以 Silent/Regent/Necrobinder 完成一局）。自动化备注：bridge mod 的 `timeline_sync` 动作 / start_run 的 Timeline 访问重放这条 UI 流程；repair 步骤只写 ObtainedNoSlot+UnlockSlot（游戏自身的状态）；Neow 硬写 Revealed 仅作祝福房兜底。实机验证：SILENT1_EPOCH not_obtained → obtained_no_slot → revealed，pending_character_unlock=CHARACTER.SILENT，unlock_character_screen 原生弹出。

## 对局结构（act 源码）

- 代码中的章节顺序：Overgrowth 蔓生之地（Act 1）、Hive 虫巢（Act 2）、Glory 荣光之殿（Act 3）、Underdocks 水底码头（Act 4）。Boss 出现顺序：蔓生之地 = Vantom、CeremonialBeast、TheKin；虫巢 = TheInsatiable、KnowledgeDemon、KaiserCrab；荣光之殿 = Queen、TestSubject、Aeonglass；水底码头 = WaterfallGiant、SoulFysh、LagavulinMatriarch。
- 地图房间：战斗 / 精英 / boss / 事件 / 商店 / 休息 / 宝箱 的分支地图；战斗后卡牌奖励；章节起始可能出现远古/尼奥系赐福房，受上述 epoch 门槛约束。
- 休息点提供 Rest 与 Smith，以及角色/遗物代码追加的专属选项（例如 PaelsGrowth 增加 Clone 休息选项）。
