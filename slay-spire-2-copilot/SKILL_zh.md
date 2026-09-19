---
name: slay-spire-2-copilot
description: 中文说明版。skill 的触发与定义以 SKILL.md 为准：通过 SpireBridge mod（spirectl CLI）自动游玩《杀戮尖塔 2》。触发语：「用 Claude Code 打一局杀戮尖塔2」「play Slay the Spire 2 via Claude Code or Codex」等；查询游戏状态、继续对局、迭代 AI 对局会话时同样适用。
argument-hint: "<日志文件夹路径>（绝对目录；必填）"
---

# slay-spire-2-copilot — AI 游玩《杀戮尖塔 2》

> 本文件是 SKILL.md 的中文版说明；skill 的 name/description 触发配置以 SKILL.md 为准。

## 概述

通过 spire-copilot-bridge mod 控制本机安装的《杀戮尖塔 2》。全部决策由 AI 做出：
完全自主游玩，绝不询问用户选哪张牌。

用户只做两件事：**发起 skill**，并**提供一个日志文件夹的绝对路径**（可选：指定
本局角色）。mod 的构建安装、游戏启动、握手验证均由 skill 在会话启动时自动完成。

## 调用方式

在 Claude Code 中发起 skill，参数中包含日志文件夹的绝对目录，例如：

    /Users/<name>/spire-logs/session-a

或直接传裸路径——参数中的任意绝对目录均有效，不要求 `log-path=` 键名，不自造
路径。触发语（中英文皆可）："用 Claude Code 打一局杀戮尖塔2"、"play Slay the
Spire 2 via Claude Code or Codex"。

参数中也可显式指定本局角色（IRONCLAD / SILENT / DEFECT / NECROBINDER / REGENT
或其中文名）：**用户显式指定时以用户为准**；未指定时按「游玩 → 角色轮换」执行。

日志目录如何解析、环境变量如何生效、日志文件如何命名，见文末「运行时约定」。

## 会话启动

按顺序执行，全部为 skill 自身的工作：

0. **检查本地 Python 环境**。`python3 --version` 必须存在且版本 >= 3.8：
   spirectl 只使用 Python 标准库，无需 pip 安装、无需 venv。python3 缺失或
   版本过低时立即停止并向用户报告，不要继续后续步骤。

1. **解析日志文件夹并设置环境变量**。从调用参数解析绝对路径：
   - 参数中没有路径：在触碰游戏之前停下，向用户索要一个日志文件夹的绝对路径。
   - 路径已提供但目录不存在：直接创建（`mkdir -p`），并明确告知用户
     「传入的路径不存在，已创建：<路径>」；仅当创建失败（权限不足、路径非法等）
     时，向用户索要可行的日志文件夹路径。
   - 确定路径后设置 `SPIREBRIDGE_LOG_DIR=<绝对文件夹>`，**整个 session 有效**，
     此后每一次 spirectl 调用都携带：

         SPIREBRIDGE_LOG_DIR=<绝对文件夹> python3 bridge/spirectl.py <子命令>

2. **读记忆**（先于其他操作）。记忆体系是整个会话的常驻游玩参考：
   - **开局必读**：`memory/overview.md`（对局表 + 统计交叉表——跨局
     全景）+ lessons 通用类内容——战斗原则、协同、角色脊线
     （`memory/lessons/`）。
   - **每步决策之前**：只查**最小必要内容**——与该决策直接相关的那一条
     lessons 条目或 `spirectl lookup` 结果（选遗物 → lessons/relics.md；
     进战斗前 → lessons/enemies.md + lookup；选路线 → lessons/route.md；
     完整路由见 memory/user_guide.md），不做全量翻阅。
   - **按需**：单局笔记 memory/runs/——文件名前缀 = overview.md 的
     对局序号，查号后开文件。

3. **环境检查与 mod 自装/自愈**（cwd = 本 skill 文件夹
   `<repo>/slay-spire-2-copilot`，全部运行时文件都在此处）：
   `SPIREBRIDGE_LOG_DIR=<绝对文件夹> python3 bridge/spirectl.py doctor`
   - doctor 报 mod 文件 MISSING，或已安装 dll 早于 mod/SpireBridge 下任一源码
     `*.{cs,csproj,json}`（首次运行，或上次安装后代码有改动）→ 执行
     `bash scripts/install_mod.sh`（dotnet 构建并将 spire-copilot-bridge 拷入游戏
     mods 目录），然后重跑 doctor。
   - 游戏进程未运行 → `spirectl launch`（经 Steam 启动游戏并等待桥接）。首次带
     mod 启动时游戏内会出现一次 mod 警告，用户在游戏内点击接受——这是除发起
     skill 外用户唯一需要做的事。
   - 窗口落位（策略 2026-09-19）：每次优雅停止（`spirectl stop` / `sl`）
     都会记录游戏窗口当前的屏幕+位置；下一次启动将窗口还原到该记录。无
     记录或还原失败 → 回退方案：启动终端所在屏幕 + 固定偏移（2026-09-18
     偏好）。仅外观问题——绝不阻塞启动。

4. **握手校验**：确认 doctor 输出中的版本。游戏版本与 mod 的 min_game_version
   漂移属硬性中止项：如实报告，不要自行发挥。

5. **武装看门狗**：`python3 bridge/spirectl.py watchdog enable`（详见「运行时约定」）。

## 游玩

### 接管规则

无论游戏处于何种状态——刚启动、主菜单、对局中、休息/商店/事件界面、或
game_over——都要接管：读取状态并推进。game_over 时 `act start_run` 会自动清理
结算链（服务端）并开始新局；日志文件夹中派生新的 run 文件。

持续游玩是指令：每局结束后（写完本局 memory 记录）立即开始下一局。绝不死锁：若某个
action 循环而状态不变，诊断界面（补上服务端缺失的支持），重建 mod
（`bash scripts/install_mod.sh`），重启并继续。出牌决策保留在 AI 客户端——仅在
AI 选定战术后，才允许机械式批量下发 action。

### 角色轮换

**用户显式指定角色时，以用户指定为准**——skill 参数或对话中出现角色名（如
IRONCLAD / SILENT / DEFECT / NECROBINDER / REGENT，或「铁甲战士」「寂静」等中文
名），就用该角色开局，不再轮换。

用户未指定时才轮换：不要总玩同一角色，按游戏构建中的候选阵容依次尝试——
IRONCLAD、SILENT、DEFECT、NECROBINDER、REGENT。使用
`act start_run --args '{"character":"SILENT"}'` 等；菜单自动化按按钮名/角色 id
子串匹配，自动跳过未解锁角色。在本局 memory 记录与运行日志中记录每局所用角色；角色专属观察写在该局的
memory 记录里。

### 游戏循环

重复直到对局结束或用户叫停。每次 spirectl 调用都带
`SPIREBRIDGE_LOG_DIR=<绝对文件夹>`：

1. `... state` — 紧凑状态（仅当需要紧凑视图未包含的字段时用 `--json`）。
   compact 现在恒显每个怪物的 `move=<move_id>`、结构化意图位（`atk:8` /
   `multi:7x2` / `status:2c` / 小写意图类型）以及每个存活怪物的
   move-graph 段（state_log、循环、分支权重、`current=`）——任何 id 的
   完整条目用 `python3 bridge/spirectl.py lookup <id>` 解析。
   路线决策：JSON 状态里的 `run.map.rows[]` 携带完整 act 地图（每个点的
   `point_type` + `children` 连通性）——用它权衡精英/营火/商店/boss 路线，
   不要只看当前可选行。**每章开局路线草稿（硬规则）**：
   新章进入任何房间之前，先读全图并在回复中书写明确的路线草稿：精英数量/位置、
   商店数量/位置（及届时金币是否花得掉）、火堆几何——每个精英前是否有火堆、
   Boss 前是否有火堆、宝箱位置——然后选择满足核查清单的脊线。标注方差点
   （Unknown 房）。中途分叉或重大事件改变计算时修订草稿。
   章切换满血的假设会被战斗消耗税击穿——无前置火堆的精英若入场 HP <~50%，
   药水就是储备计划；金币要在精英走廊之前的最新商店花掉，而非之后。
   **赐福房（开局 + 章节切换）**：每章开头都有
   Ancient/尼奥系赐福房。第一章是**尼奥（Neow）**（遗物三选一类选项——
   正面遗物 vs 诅咒代价遗物）；`start_run` 会先在存档上揭示 NeowEpoch
   保证房间生成，随后游戏在开局**自动进入**尼奥事件——选正面赐福，
   无特殊理由绝不选诅咒代价选项。后续章节是先古移民式起始房。每次
   章节切换都要检查 `run.act_start_room`——在 `visited=false`/
   `is_boon_room=true`（或 `point_type` 为 Ancient）时必须**最先**
   map_select 该点；state 会把它重新注入 `available_map_points` 头部，
   紧凑视图会打印 ACT-START BOON ROOM UNVISITED 警告。该标志存在时
   绝不能跳到第 1 排及之后的点——跳过赐福是永久损失（地图不能回头）
2. 结合状态与记忆决定动作——只查该决策对应的最小必要内容：匹配的
   `memory/lessons/` 条目和/或 `spirectl lookup <id>` 结果
3. `... act <动作> --args '<json>' --wait` — action 立即返回（已提交）；`--wait`
   轮询至状态稳定（指纹不再跳动）后打印。**每次只打一张牌 — 硬规则**：
   战斗中的卡牌打出**绝不批量提交**。每次 `act play` 只打**一**
   张牌，然后重读 state，再根据最新下标决定下一张——禁止多卡 `batch` 倾泻、
   禁止预计算出牌链。从根源上杜绝索引漂移——批量或预计算链会重构手牌下标，
   可能静默打出错误的牌。`end_turn` 是独立一次调用，且仅在重读 state 确认无后续出牌后才
   发出。`batch` 仅可用于不会重构手牌下标的非卡牌序列（如单独一次 map_select），
   即便如此也优先分次调用。下标只对「从最新 state 打印计算出的那一次 act」
   有效。战斗中弹出的选牌覆盖层（boss 诅咒、药水选牌）现在会以
   screen=card_choice 暴露（mod 覆盖层扫描），像普通选牌界面一样用 `choose`
   应答。
4. 等待一律是状态变化轮询，绝不用超时死等：
   `wait --quiet 3` 最多 ~3 秒——指纹一变立即返回；游戏空闲则带当前状态立刻
   返回。禁止长时间阻塞等待；若动作后界面没变，直接重读 state 诊断——动作
   可能不合法，或界面需要另一种输入
5. 若 act 返回 ok=false，读 message、重读 state、用修正后的 action 重试——不要
   盲目重复同一调用
6. 动作后核验（结算滞后类）：act 返回后动作可能延迟 1-3 秒才生效——立即读到的
   state 可能是动作前手牌，据此计算的后续动作会静默空转。任何 `act`/`batch`
   之后先重读 state（首轮读数仍像动作前则读第二次）再计算后续索引。覆盖层
   （锻造/附魔/去除 deck_select、弃牌 hand_select、工具交易类 phase=Start
   弹窗）均为 choose(index) 后 **proceed 确认**——仅 choose 不算确认。宝箱用
   `treasure_open` 开启，不是 choose。`use_potion` 后药水槽位重排——下一次
   用药前重读 state。

### 机制优先战斗（硬规则）

此处的失败多因关键机制未纳入决策，而非硬实力不足。每场战斗机制优先：

1. **每场与不熟悉敌人的战斗首回合前，以及每场精英/Boss 战无例外**：
   先用 `python3 bridge/spirectl.py lookup <id>` 解析每一个不熟悉的
   move_id/power_id/relic_id（或直接读 bridge/spirectl_lib/data/monsters.json /
   powers.json）——招式循环、每一个被动 Power、施加的每一个
   debuff/buff。live state 显示的每个 power/意图都必须能用参考解释；
   任何未知 → perplexity-search → 折入 references 双语 → 再出牌。
2. **禁止标识符猜测**：live state 中出现的每一个 move_id、power_id、
   relic_id、card_id、potion_id、event id，凡不在工作记忆中的，必须先经
   `spirectl lookup` 解析后才能用于决策。凭档案记忆推导效果被禁止；
   lookup miss 是高声研究触发器（codex 回退自动执行；codex 也未命中时用
   perplexity-search 再把事实折入 JSON 双语对），绝不是猜测许可。
3. **计数类 power 是击杀倒计时，不是装饰**：SANDPIT（归 0 直接吞噬，
   格挡无效）、RINGING（每回合限 1 张牌）、ESCAPE_ARTIST、HATCH、
   TIME_LIMIT、HardToKill 上限、Plating 阈值等。每回合跟踪其 Amount；
   compact state 打印 `POWER:amount`——必读。回合计划要围绕计数器制定
   （竞速输出 vs 延时卡），不能只看攻击意图。
4. **绝不把无法解释的致死当作"显示 bug"**。若在算术上足够的格挡下仍然致死，
   原因是你还没研究的机制：下次尝试前先研究清楚。
5. **档案可能是错的**。live state + 研究来源优先于档案里
   的一行摘要；发现错误当次会话即订正 references。

每回合行动前检查：敌人全部 power/debuff/buff 及其层数、敌人意图、
自身血量/格挡、能量、手牌可否打出。回复中保持简短的实时解说，便于
用户跟上出牌思路。memory 在游玩全程随时可查——每步决策之前只打开
最小必要内容：匹配的 `memory/lessons/` 分类条目（敌人教条、遗物
trick、协同……）和/或 `spirectl lookup <id>` 的结构化机制事实；
单局笔记经 overview 对局序号按需查阅。

## 对局结束

详细对局记录是自动的：每次 spirectl state/act/wait 调用都会把完整 JSON 追加到
`SPIREBRIDGE_LOG_DIR` 下的当前 run 文件（每局一个；start_run/continue_run 轮换，
game_over 时 finalize）。该文件夹在 skill 目录之外、仓库之外——日志永不入库；
对局进行中不要删除或改写活跃日志。`.claude/` 同样被 gitignore（仅 harness
运行时）。

对局结束时（game_over 界面，或 abandon）：

1. 将本局 memory 记录写入
   memory/runs/<对局序号4位>_<CHARACTER>_<YYYYmmdd-HHMMSS>_<hash8>.md
   （对局序号 = 本局在 overview.md 将携带的序号——最新序号 + 1；后接角色
   id、run 日志时间戳与哈希，下划线分隔）及其对应中文版
   memory/runs/<对局序号4位>_<CHARACTER>_<YYYYmmdd-HHMMSS>_<hash8>_zh.md——
   两者内容必须完全对应。均遵循 memory/user_guide.md 与 memory/template.md
   （格式以 template.md 为准）。引用 run 日志时只写文件名，绝不写个人绝对路径。
2. 对局中新观察到的游戏**结构化事实**（卡牌/遗物/药水/能力/意图的机制
   字段）直接折入 bridge/spirectl_lib/data/ 下对应的 *.json 及其 `_zh` 双语对——
   key = live 游戏 id，schema 见 bridge/spirectl_lib/schema.py（信封 +
   按 kind 的 detail；codex 为权威结构源，散文教条归 memory/lessons）——
   随后运行 `python3 scripts/build_game_reference_json.py --check`，提交前
   必须 exit 0。memory 只记对局感悟与过程，不记游戏基础数据。
3. 更新 `memory/overview.md`：对局表**顶部**插入一行，随后按表格重新核算
   `## 统计` 交叉表（战绩总览 / 进阶进度）。
4. 将本局前向价值经验沉淀进 `memory/lessons/` 对应分类文件——能与条目
   清单表格某行一对一对应的写入该行「经验」格，其余以无序列表附在表格后。
5. 将本局 memory 记录、其 `_zh` 中文版、overview 更新与 lessons 沉淀一并
   提交进仓库——memory 已纳入版本控制。
6. 若用户已停止游玩：解除看门狗武装（见「运行时约定」）。
7. **阶段性反思**：反思内容绝不写入 `overview.md`——直接写入
   `memory/lessons/` 对应的分类 markdown，以带日期的无序列表条目记录
   （每条标注日期）。节奏：**第一次反思覆盖目前为止的全部对局**；从第二次
   起每次覆盖自上次以来的 **10 局**（如 36–45、46–55、56–65……累计
   对局数到达边界时触发）。素材是 `memory/runs/` 下覆盖区间的对局笔记。
   overview.md 只放整体对局结果（含 **对局序号** 列的表格，最新局置顶、
   序号最大）。

## 自我迭代

- 工具缺陷（spirectl/mod/协议问题）：在当前分支的本仓库内修复；C# 有改动则重建
  mod（`bash scripts/install_mod.sh`），doctor 验证，然后在本局 memory 记录
  （memory/runs/）里写明原因与修复。以 [fix] 或 [feature] 性质提交。
- 策略文档被实战证伪：改正文档，并记录到本局 memory 记录。
- 游戏补丁破坏 hook（doctor 握手正常但 state 字段缺失/错误）：必要时反编译游戏
  程序集，适配 mod，并将修复记录进本局 memory 记录。

## 注意事项

- 修复只允许改本仓库代码；绝不修改游戏程序集。
- 游戏窗口可能显示其他语言或用户的其他 mod；状态以 bridge 为准，优先于截图。
- 不要在对局循环之外替用户操作游戏内货币（如永久解锁）：元进程类选择先询问用户。
- 绝不将个人绝对路径、会话日志文件夹或 harness 运行时文件提交进仓库。
- skill 文件夹根目录的 proposal.md 是 agent 的本地流程建议便签：游玩过程
  或前后的任何时候，若觉得当前流程（Summary、memory 查阅方式、references
  组织等）有不合适之处，把问题与具体改进建议写进去。该文件被 gitignore，
  仅供用户查阅，不要提交。

## 运行时约定

- **日志目录的唯一来源是环境变量 `SPIREBRIDGE_LOG_DIR`**：无指针文件、无 CLI
  参数、无任何回退目录。变量未设置时，spirectl 中需要写日志的命令直接报错退出；
  由 skill 按「会话启动」第 1 步解决——参数里有路径就设置变量，没有就向用户索要。
- 该变量在**整个 session 内有效**。若调用时发现未设置，视为流程错误：立即停下
  修复，不得改用其他目录。
- spirectl 将该变量视为**文件夹**：每局在其中派生
  `run-<时间戳>-<哈希8>.log`（时间戳 + 短 sha256，例：
  `run-20260916-013052-a3f9c012.log`）。
- `doctor` 打印 `[0] run log dir: ... | SPIREBRIDGE_LOG_DIR=set|unset`；出现
  unset 时先修复再继续。
- 外部看门狗（crontab 中的 `scripts/watchdog_external.sh`）从**它自己的环境**读取
  `SPIREBRIDGE_LOG_DIR`——若要跟踪本会话日志，需在 crontab 行 export 同一文件夹；
  变量未设置时它跳过日志新鲜度检查（同样无回退）。
- 看门狗仅在武装状态下运行检查并产生告警记录；用户停止游玩时解除武装，使其
  静默退出：

      python3 bridge/spirectl.py watchdog enable     # 会话启动时
      python3 bridge/spirectl.py watchdog disable    # 用户停止游玩时
      python3 bridge/spirectl.py watchdog status

- **SL 恢复路径**：对局中需要 SL（读档恢复）时——死锁
  排除、mod 重建、界面卡死等——必须在**不关闭游戏进程**的前提下先退回游戏内
  **主菜单**，再从主菜单 `continue_run` 进入。**严禁为了 SL 直接退出/杀掉游戏
  进程再重启。** 游戏内路径：暂停菜单（顶栏暂停按钮 → `NPauseMenu`）→
  `Save And Quit`（`_saveAndQuitButton` / `OnSaveAndQuitButtonPressed`）→
  主菜单 → `act continue_run`。只有游戏进程真正崩溃（进程已不存在）才允许
  `spirectl launch`；`spirectl sl` 的 stop→launch 流程被本规则取代，不得用于
  常规 SL。

## 参考文档

决策与排查时按需查阅以下文件（路径均相对本 skill 文件夹）：

bridge/ — 工具文档与游戏数据：

- `bridge/docs/commands.md` — CLI 用法、动作与状态参考、日志目录契约
- `bridge/docs/protocol.md` — 线协议 v1（本机 TCP 上的 JSON Lines）
- `bridge/spirectl_lib/data/characters.json` + `characters_zh.json` — 可玩角色、
  初始配置、流派
- `bridge/spirectl_lib/data/cards.json` + `cards_zh.json` — 卡牌
- `bridge/spirectl_lib/data/potions.json` + `potions_zh.json` — 药水效果
- `bridge/spirectl_lib/data/powers.json` + `powers_zh.json` — 能力/力量
- `bridge/spirectl_lib/data/relics.json` + `relics_zh.json` — 遗物效果
- `bridge/spirectl_lib/data/intents.json` + `intents_zh.json` — 敌人意图解读
- `bridge/spirectl_lib/data/monsters.json` + `monsters_zh.json` — 敌人招式表与被动
  （招式嵌套在各怪物条目下）
- `bridge/spirectl_lib/data/events.json` + `events_zh.json` — 事件房与已知分支
  （选项嵌套在各事件条目下）
- `bridge/spirectl_lib/data/afflictions.json` + `afflictions_zh.json` — 状态与
  负面效果
- JSON 参考库：纯程序化存储（信封 + 按 kind 的 detail，schema 见
  bridge/spirectl_lib/schema.py），条目以 live 游戏 id 为 key；任何 id 用
  `python3 bridge/spirectl.py lookup <key>` 解析（flag：`--json/--lang/`
  `--domain/--all`；miss 时直接从 spire-codex.com 折入**结构**——codex 为
  权威源）。教条/散文归 memory/lessons，绝不进数据存储。

memory/ — 对局记忆（已纳入版本控制）：

- `memory/user_guide.md` — 记忆写作指南：格式、写入时机、查阅时机、备注
- `memory/template.md` — 每局 memory 记录的章节模板
- `memory/overview.md` — 跨局对局表（`## 对局表`）+ 统计交叉表（`## 统计`）；
  只放结果，不含经验内容
- `memory/lessons/` — 跨局常备经验，每类一个文件（characters / cards /
  relics / synergies / combat / economy / route / enemies / events），
  各含英文版与 `_zh` 中文版
- `memory/runs/` — 每局一条记录及其 `_zh` 中文版，文件名
  <对局序号4位>_<CHARACTER>_<YYYYmmdd-HHMMSS>_<hash8>.md / _zh.md——
  文件名前缀 = memory/overview.md 的对局序号（查阅键）

- `SKILL.md` — skill 触发与定义（英文版）；本文件为其说明
