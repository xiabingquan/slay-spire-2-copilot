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

1. **解析日志文件夹并设置环境变量**。从调用参数解析绝对路径：
   - 参数中没有路径：在触碰游戏之前停下，向用户索要一个日志文件夹的绝对路径。
   - 路径已提供但目录不存在：直接创建（`mkdir -p`），并明确告知用户
     「传入的路径不存在，已创建：<路径>」；仅当创建失败（权限不足、路径非法等）
     时，向用户索要可行的日志文件夹路径。
   - 确定路径后设置 `SPIREBRIDGE_LOG_DIR=<绝对文件夹>`，**整个 session 有效**，
     此后每一次 spirectl 调用都携带：

         SPIREBRIDGE_LOG_DIR=<绝对文件夹> python3 bridge/spirectl.py <子命令>

2. **读记忆**（先于其他操作）：
   - memory/user guide.md（用户手写的记忆要点）
   - memory/runs/（每局一条记录）

3. **环境检查与 mod 自装/自愈**（cwd = 本 skill 文件夹
   `<repo>/slay-spire-2-copilot`，全部运行时文件都在此处）：
   `SPIREBRIDGE_LOG_DIR=<绝对文件夹> python3 bridge/spirectl.py doctor`
   - doctor 报 mod 文件 MISSING，或已安装 dll 早于 mod/SpireBridge 下任一源码
     `*.{cs,csproj,json}`（首次运行，或上次安装后代码有改动）→ 执行
     `bash scripts/install-mod.sh`（dotnet 构建并将 spire-copilot-bridge 拷入游戏
     mods 目录），然后重跑 doctor。
   - 游戏进程未运行 → `spirectl launch`（经 Steam 启动游戏并等待桥接）。首次带
     mod 启动时游戏内会出现一次 mod 警告，用户在游戏内点击接受——这是除发起
     skill 外用户唯一需要做的事。

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
（`bash scripts/install-mod.sh`），重启并继续。出牌决策保留在 AI 客户端——仅在
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

1. `... state` — 紧凑状态（仅当需要紧凑视图未包含的字段时用 `--json`）
2. 结合状态与记忆（user guide、近期 runs）决定动作
3. `... act <动作> --args '<json>' --wait` — action 立即返回（已提交）；`--wait`
   轮询至状态稳定（指纹不再跳动）后打印。战术已定时，多个动作合并为一次
   `batch --acts '[...]'` 提交（步间自动 settle；卡牌下标按从高到低排列由你负责）
4. 等待一律是状态变化轮询，绝不用超时死等（用户指令 2026-09-16）：
   `wait --quiet 3` 最多 ~3 秒——指纹一变立即返回；游戏空闲则带当前状态立刻
   返回。禁止长时间阻塞等待；若动作后界面没变，直接重读 state 诊断——动作
   可能不合法，或界面需要另一种输入
5. 若 act 返回 ok=false，读 message、重读 state、用修正后的 action 重试——不要
   盲目重复同一调用

每回合行动前至少检查：敌人意图、自身血量/格挡、能量、手牌可否打出。
回复中保持简短的实时解说，便于用户跟上出牌思路。决策经验与卡牌/药水/遗物/意图
等知识见文末「参考文档」。

## 对局结束

详细对局记录是自动的：每次 spirectl state/act/wait 调用都会把完整 JSON 追加到
`SPIREBRIDGE_LOG_DIR` 下的当前 run 文件（每局一个；start_run/continue_run 轮换，
game_over 时 finalize）。该文件夹在 skill 目录之外、仓库之外——日志永不入库；
对局进行中不要删除或改写活跃日志。`.claude/` 同样被 gitignore（仅 harness
运行时）。

对局结束时（game_over 界面，或 abandon）：

1. 将本局 memory 记录写入 memory/runs/<与 run 日志同名>.md
   （run-<YYYYmmdd-HHMMSS>-<hash8>.md）：结果、关键决策、有效的做法、
   导致失败的原因、值得保留的观察，遵循 memory/user guide.md。引用 run
   日志时只写文件名，绝不写个人绝对路径。
2. 对局中新观察到的游戏事实（卡牌/遗物/药水/能力/意图的效果）以条目形式
   直接写入 references/game/ 下对应文件及其 `_zh` 中文版——中英内容必须
   完全对应。memory 只记对局感悟与过程，不记游戏基础数据。
3. 将本局 memory 记录提交进仓库——memory 已纳入版本控制。
4. 若用户已停止游玩：解除看门狗武装（见「运行时约定」）。

## 自我迭代

- 工具缺陷（spirectl/mod/协议问题）：在当前分支的本仓库内修复；C# 有改动则重建
  mod（`bash scripts/install-mod.sh`），doctor 验证，然后在本局 memory 记录
  （memory/runs/）里写明原因与修复。以 [fix] 或 [feature] 性质提交。
- 策略文档被实战证伪：改正文档，并记录到本局 memory 记录。
- 游戏补丁破坏 hook（doctor 握手正常但 state 字段缺失/错误）：必要时反编译游戏
  程序集，适配 mod，并将修复记录进本局 memory 记录。

## 注意事项

- 修复只允许改本仓库代码；绝不修改游戏程序集。
- 游戏窗口可能显示其他语言或用户的其他 mod；状态以 bridge 为准，优先于截图。
- 不要在对局循环之外替用户操作游戏内货币（如永久解锁）：元进程类选择先询问用户。
- 绝不将个人绝对路径、会话日志文件夹或 harness 运行时文件提交进仓库。

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
- 外部看门狗（crontab 中的 `scripts/watchdog-external.sh`）从**它自己的环境**读取
  `SPIREBRIDGE_LOG_DIR`——若要跟踪本会话日志，需在 crontab 行 export 同一文件夹；
  变量未设置时它跳过日志新鲜度检查（同样无回退）。
- 看门狗仅在武装状态下运行检查并产生告警记录；用户停止游玩时解除武装，使其
  静默退出：

      python3 bridge/spirectl.py watchdog enable     # 会话启动时
      python3 bridge/spirectl.py watchdog disable    # 用户停止游玩时
      python3 bridge/spirectl.py watchdog status

## 参考文档

决策与排查时按需查阅以下文件（路径均相对本 skill 文件夹）：

references/ — 查阅知识：

- `references/README_zh.md` — 知识索引（中文版）
- `references/bridge/commands.md` — CLI 用法、动作与状态参考、日志目录契约
- `references/bridge/protocol.md` — 线协议 v1（本机 TCP 上的 JSON Lines）
- `references/game/characters_zh.md` — 可玩角色、初始配置、流派
- `references/game/cards_zh.md` — 卡牌
- `references/game/potions_zh.md` — 药水效果
- `references/game/powers_zh.md` — 能力/力量
- `references/game/relics_zh.md` — 遗物效果
- `references/game/intents_zh.md` — 敌人意图解读
- `references/game/monsters_zh.md` — 敌人招式表与被动
- `references/game/events_zh.md` — 事件房与已知分支
- `references/game/afflictions_zh.md` — 状态与负面效果

memory/ — 对局记忆（已纳入版本控制）：

- `memory/user guide.md` — 用户手写的记忆要点（agent 记录时的参考）
- `memory/runs/` — 每局一条记录，文件名 run-<YYYYmmdd-HHMMSS>-<hash8>.md

- `SKILL.md` — skill 触发与定义（英文版）；本文件为其说明
