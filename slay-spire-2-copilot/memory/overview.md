# 对局总览 Overview

全部对局一览表（数据来自 memory/runs/ 各局双语笔记）。

**表格规则（用户指令 2026-09-17 起生效）**：
- 列顺序：角色 | 日期 | **进阶** | 到达楼层 | 胜负 | SL 次数 | 备注
- **进阶**列只写数字（0、1、2…），即该局实际打出的进阶难度
- **最新对局放在表格最上方**（倒序排列）；追加新对局时插到表格顶部，不得追加在底部

**是否胜利图例**：✅ = 胜利（EA 内容通关：到达 THE_ARCHITECT；建筑师 Boss 未实装，PROCEED → HP 0 为占位收束）｜❌ = 失败（未到达建筑师：对局内死亡）｜⏸️ = 中止（非死亡，被控制器叫停）

| 角色 | 日期 | 进阶 | 到达楼层 | 胜负 | SL 次数 | 备注 |
|---|---|---|---|---|---|---|
| IRONCLAD | 2026-09-17 20:18 | 1 | 31 | ❌ | 0 | **A1 第二局**（run-14 ❌ 后 A1 通过 0/3 → 维持 A1；state `asc=1` 校验通过）：Act1 **A1 首杀 Boss 墨影幻灵 Vantom 173**（Slippery 充能泄尽后回合 5 击杀：Conflagration 36+Dismantle 双击 36+Strike）；Act1 三精英全清（异鸟 84/寄生虫 62+4 虫波/旧日雕像 127）；产卵虫 129 二次复仇（母体集火至 10 HP 后 O2P+Sharp3 Conflagration 一发清场）；死于 Act2 精英 (12,2) 感染棱柱 161（剩 24/161，回合 3）<br>- 引擎：Rupture+（锻造）×双放血/Offering 力量线；扭曲锤子 Sharp3 附魔 Conflagration/Dismantle/Rampage；佩尔之血 +1 抽；天选芝士每战 +1 最大 HP（滚至 83）<br>- 死因：**致命回合资源闲置**——20 HP 面对 7×3=21 入侵，0 挡结束回合，手牌邪眼 8 挡+防御 5 挡未打出，3 瓶药未用（用户局中"为啥不用药水"点名的失误模式致命重演）<br>- 教训：入侵 ≥ 剩余 HP 时先挡后输出、药水即时花；水晶球 50 金三连角点空手（物品在线上随机位）；自标卡带 target 仍会空转 |
| IRONCLAD | 2026-09-17 19:07 | 1 | 33 | ❌ | 0 | **存档首局进阶1（A1）**——长期策略生效（进阶0 已 4✅≥3 → 升 A1；state `asc=1`+godot 回执 `Ascension: 1 Seed: XYVN4ZKCPR` 双校验；bridge 本局新增 start_run ascension 参数+state 字段）：Act1 **首破 Boss 乐加维林族母 222**（沉睡唤醒战术：未格挡伤害去镀甲+眩晕）；Act2 击杀死 run-10 杀手直飞产卵虫 129（母体集火 6 回合）；死于 Act2 Boss 知识恶魔 379（剩 107/379，回合 8）<br>- 引擎：可可第1回合+4能（7 能开局）×放血+（6 能回合）×壁垒×撞击+0费格挡转伤×重锤×2×战栗/痛击易伤→欺凌兑现；红头骨（HP≤50% +3 力）+爬行动物饰品（用药+3 力）低血反打<br>- 死因：**bridge 自标静默空转**（Self 卡传 target_combat_id 被游戏丢弃）+末回合 overlay confirm 后索引过期——Armaments→Defend+ 未送达，5 挡对 13 伤，4 HP 阵亡；收尾同会话已补 fail-loud 修复<br>- 教训：怠惰（每回合≤3 张）+心智腐蚀（-1 抽）双诅咒压死引擎吞吐；钓鱼竿计数只算 Monster 房（精英不推进）；Primal Force 变形仅限战斗内；Act 切换满血（32→80） |
| REGENT | 2026-09-17 18:33 | 0 | 17 | ❌ | 0 | **存档第二局 Regent**（run-12 NECROBINDER 后按 roster 序轮换）：Act1 路线走完（Neow→商店→双精英→三休息→宝箱→Boss），双精英全下（旧日雕像 127 沉睡回合白嫖 37 伤；多尼斯异鸟 82 荆棘收尾）；死于 Act1 Boss 仪式兽 252（剩 109/252）<br>- 引擎：RADIATE×DIVINE_RIGHT 局内坐实（开局 +3★ 计入 RADIATE，回合 1 SS→RADIATE=0费15伤AoE）；ShiningStrike 77金循环回抽顶 +2★/次；TYRANNY +1抽/回合+自选消耗瘦牌；BronzeScales 荆棘多次收残；Forge 引擎 floor-15 才上线（WroughtInWar→Blade 17伤+Parry+14挡 实测两次）<br>- 死因：**RINGING_POWER 查阅失败** — BEAST_CRY 施加铃锁（references 三处有档：每回合仅可打出第 1 张牌），回合 9 batch 以 Venerate 开头致 GatherLight 8挡锁死，15 伤清空 10 HP；run-12 Gambit 同类错误重演<br>- 过程失误：卡牌奖励索引误读×2（口述 RADIATE 拿了 ManifestAuthority；口述引擎需求错过 REFINE_BLADE）；商店零 Forge 存货（ForegoneConclusion 差 3 金）；Boss 入场仅 31 HP |
| NECROBINDER | 2026-09-17 18:24 | 0 | 33 | ❌ | 5 | **存档首局死灵绑定师**（菜单请求 DEFECT/NECROBINDER 被拒后，IRONCLAD 回执实际进入 Necrobinder — state 权威）：Act1 全通关含 Boss 灵魂异鱼 211 首破（Boss 战零掉血，Doom 斩杀）；Act2 双精英千足虫同窗 Doom 团灭 + 蜂群术士 145（run-11 杀手）击破；死于 Act2 Boss 帝王蟹（双爪 99/100、100/199）<br>- 引擎：Reanimate×Unleash+×Doom-AOE(NegPulse×2)×Sleight-of-Flesh(debuff 附送 9伤)×BoneShards+；DIE_FOR_YOU+Reanimate 吸伤循环；PaelsTooth 瘦牌库 22→17<br>- 死因：THE_GAMBIT_POWER 死亡条款跨回合留存 — 第6回合打出，第8回合 8 点未格挡擦伤即死（32 HP 清零）；机制死后才查明<br>- 局中修复×4：能量守恒(AutoPlay 免费能量→PlayCardAction)、静默目标 fallback→fail-loud、NChoose 屏幽灵索引、NDeck 屏 OnCardClicked 反射；用户局中指令：SL 游戏内菜单路径、窗口化、机制先查、目标显式 |
| REGENT | 2026-09-17 16:58 | 0 | 30 | ❌ | 0 | **存档首局 Regent**（timeline_sync reveal Regent1）：Act1 全通关含 Boss Vantom 173 首破（SlipperyPower 8 层泄尽后 Blade 36 斩杀）；死于 Act2 (12,6) 精英蜂群术士 145（母体剩 18/145，进场 HP 16）<br>- 教训：Forge→SovereignBlade×Parry×Conqueror=Regent 引擎成立；DecisionsDecisions 星费三连 Bulwark=36 挡救命；GremlinHorn+BronzeScales 遗物契合<br>- 教训：Act2 Thorns/Hive 消耗战 HP 经济崩盘——<40 HP 禁入精英走廊；batch 索引漂移 6 次流血；DollysMirror 克隆异常待查 |
| SILENT | 2026-09-17 14:09 | 0 | 21 | ❌ | 1 | **存档首局寂静**（Timeline 解锁生效）：Act1 Boss 瀑布巨兽 240 首破（EXPLODE 51 以 9 HP 扛过）；死于 Act2 (3,1) 直飞产卵虫召唤波消耗战（母虫 44/128 时 HP 0）<br>- 教训：Spiral 附魔防御+Footwork+AfterImage=格挡引擎成立；召唤波战要母虫集火而非清波；工具交易弃牌弹窗有流程税<br>- 教训：右脊先商店路线优于左脊休息密度（产卵虫战前未消费 136g）<br>- SL：Act1 中游戏进程退出一次，continue_run 恢复同一房间续打 |
| IRONCLAD | 2026-09-17 10:28 | 0 | 48 | ✅ | 未记录 | - **荣耀女王 Boss 首破**（400+199，回合 8 连环拳+×腐化重锤 118→0，玩家 32 HP）<br>- session context 楔死后从 A3 f35 战中段恢复续打，未开新局<br>- 引擎：共生体 Corrupted 重锤×连环拳+×毒牙+×能量三件套（供奉+/产出/放血）；金刚杵/打击假人/钢笔尖商店线 |
| IRONCLAD | 2026-09-17 09:08 | 0 | 48 | ✅ | 未记录 | - 测试对象 #C9 战斗击破后到达建筑师<br>- 引擎：蛋+剃刀齿+臂甲+ 升级经济 / 连指手套×仪式×邪眼 / 弹珠袋×毒牙+ / 金刚杵+手里剑力量堆<br>- 教训：评价对局看 Boss 战表现而非最终楼层 |
| IRONCLAD | 2026-09-17 07:48 | 0 | 48 | ❌ | 未记录 | - **死于 Act3 Boss 战内**：荣耀女王 400+火炬头 199 回合 6 阵亡（女王剩 145）<br>- 原因：爪变形吃光全部防御，锁链出牌限制下无格挡可用<br>- 教训：没有替代方案前不要变形掉格挡牌 |
| IRONCLAD | 2026-09-17 07:36 | 0 | 48 | ✅ | 未记录 | - 永玻璃 512 回合 4 击杀（0 受伤）后到达建筑师<br>- 教训：双重供奉+×被遗忘仪式+×连指手套×邪眼 能量引擎秒杀 Boss |
| IRONCLAD | 2026-09-17 05:25 | 0 | 48 | ✅ | 未记录 | - 本存档首次 Act3 通关：仪式兽 252 / 帝王蟹 408 / 测试对象 #C8 全清后到达建筑师<br>- 教训：力量密集格挡引擎（壁垒×猛撞×失落之魂×回旋镖直觉）是 Act3 胜法 |
| IRONCLAD | 2026-09-17 03:38 | 0 | 32 | ❌ | 未记录 | - Act2 Boss 知识恶魔 379 回合 11 阵亡（剩 91）<br>- 教训：格挡收益包（杂耍+愤怒+无痛+巨兽）优于易伤爆发，但诅咒 HP/能量税需要续航<br>- 批次索引漂移在终局回合抛锚 |
| IRONCLAD | 2026-09-17 03:08 | 0 | 17 | ⏸️ | 未记录 | - Act1 Boss 祭司王 190 回合 6 全清，Act2 f1 被控制器叫停（非死亡）<br>- 教训：能量遗物+1 费能力优于 3 费引擎<br>- 教训：act 开场祝福房曾被 bridge 漏列 (0,3) 永久错过——之后列为硬规则 |
| IRONCLAD | 2026-09-17 03:01 | 0 | 16 | ❌ | 未记录 | - Act1 Boss 祭司王 190 回合 8 阵亡（剩 53）<br>- 教训：155g 商店壁垒无能量支撑成死卡——3 费引擎卡需能量线或低压窗口才买 |
| IRONCLAD | 2026-09-17 02:19 | 0 | 17 | ❌ | 未记录 | - Act1 Boss 虚无幽灵 173 击破后，Act2 f1 以 1 HP 进场死于窃跳兔<br>- 教训：弹珠袋+拆除为核心进攻；HP 经济在战前已决定结局；4 防御格挡密度不足 |

**统计**：15 局 · ✅ 4 胜（EA，全部 IRONCLAD，均为进阶0） · ❌ 10 败 · ⏸️ 1 中止 · 角色：IRONCLAD×11 + SILENT×1 + REGENT×2 + NECROBINDER×1（run-10 起 Timeline 解锁生效；DEFECT 仍未解锁）· **进阶策略（2026-09-17 起）**：角色锁定 IRONCLAD；同一进阶累计通过 3 局才升级——进阶0 已 4✅ 故 run-14 起为 A1；A1 通过 0/3（run-14/run-15 均 ❌）→ 下局维持 A1 · SL 次数自 run-11 起必录（run-14=0，run-15=0）· run-15 为 A1 首个 Act1 Boss 击杀（Vantom 173）+ 三 Act1 精英全清，死于 Act2 精英棱柱 · **表格规则（2026-09-17 起）**：进阶列只写数字；最新对局置顶追加 · **bridge 扩展（run-14）**：start_run ascension（fail-loud 对照 MaxAscension）+ state `run.ascension`/`player.character` + 自标卡 target fail-loud；机制查阅纪律保持（run-14/15 未知 power 全部先查后打）。

相关文件：memory/runs/<character>_<timestamp>_<hash>.md（英文）+ _zh.md（中文孪生）；游戏机制数据在 references/game/（EN/ZH，仅静态数据）。
