# slay-spire-2-copilot

让 Claude Code / Codex 智能体在本机自动游玩《杀戮尖塔 2》（Slay the Spire 2）的
skill 与配套工具。智能体实时读取游戏状态、完全自主决策，并通过自研通讯 mod
驱动游戏；跨会话、跨对局拥有持久记忆与自我迭代循环。

> 英文版：[README.md](README.md)

## 目录结构

外层仓库根目录只保留必要元文件；skill 运行所需的**全部文件**都在 skill 文件夹内
（与 skill 同名）：

    slay-spire-2-copilot/                  （仓库根目录）
      README.md
      README_ZN.md
      .gitignore
      slay-spire-2-copilot/                （skill 文件夹 — 全部运行时文件）
        SKILL.md                           （skill 定义 / 调用契约）
        bridge/spirectl.py                 （Python CLI：state/act/wait/sl 等）
        bridge/watchdog-external.sh        （crontab 存活看门狗）
        mod/SpireBridge/                   （C# 通讯 mod 源码 + 清单）
        setup/install-mod.sh               （构建并安装 mod 到游戏）
        docs/                              （协议规范 + API 逆向笔记）
        doc/                               （游玩知识：卡牌/药水/遗物等）
        memory/                            （lessons、changelog、对局复盘）
        references/commands.md             （CLI 与状态速查）

Claude Code 的 skill 符号链接指向 skill 文件夹：

    ~/.claude/skills/slay-spire-2-copilot -> <仓库>/slay-spire-2-copilot/slay-spire-2-copilot

运行时产物**不进仓库**：对局日志写入 `SPIREBRIDGE_LOG_DIR`（用户提供的**文件夹**，
文件名形如 `run-<时间戳>-<哈希>.log`）；看门狗/通知状态在
`~/.local/share/slay-spire-2-copilot/`。

## 整体协作关系

    Claude Code 会话（skill `slay-spire-2-copilot`）
        -> bridge/spirectl.py（TCP JSONL，127.0.0.1:17612）
        -> 游戏进程内的 spire-copilot-bridge mod
        -> MegaCrit.Sts2 游戏 API（CardCmd/PlayerCmd/UI 节点）

## 架构：客户端–服务端职责

**服务端** = 游戏进程内的 SpireBridge mod。监控游戏状态并返回快照，接受操作
指令并作用到游戏；它不做任何决策。

**客户端** = spirectl + 决策层（通过 skill 接入的 Claude）。读取状态快照、
做出全部决策、发送操作请求；不直接触碰游戏内部。

完整性规则：游玩中遇到服务端尚未支持的界面或组件时，立即实现（重建 mod +
重启游戏）并继续，绝不跳过或绕开。

## 安装与使用

以下命令均在 skill 文件夹 `slay-spire-2-copilot/slay-spire-2-copilot` 下执行：

1. 构建并安装 mod：`bash setup/install-mod.sh`
   （需要 .NET SDK 9+；游戏程序集从 Steam 安装目录引用）
2. 启动游戏：`python3 bridge/spirectl.py launch`
   首次带 mod 启动会弹出游戏内 mod 警告——接受一次即可。
3. 验证：`SPIREBRIDGE_LOG_DIR=<日志文件夹> python3 bridge/spirectl.py doctor`

## 通过 Claude Code 游玩

打开 Claude Code 会话并调用该 skill，例如「用 Claude Code 打一局杀戮尖塔2」或
"play Slay the Spire 2 via Claude Code or Codex"，并传入一个绝对路径的**日志
文件夹**。skill 会指示 Claude：加载记忆 → doctor 检查 → 武装看门狗 →
循环执行 state → 决策 → act → wait。

## 记忆与自我迭代

- `slay-spire-2-copilot/memory/lessons.md` — 可泛化的对局经验，证伪即删
- `slay-spire-2-copilot/memory/runs/` — 每局结束后的复盘
- `slay-spire-2-copilot/memory/changelog.md` — 工具修复与策略纠偏台账；
  工具 bug 在本仓库修复并记录于此

## 已推迟（TODO）

- 无人值守批量自动对局 runner（用于迭代数据采集）
- STS1 CommunicationMod 适配（协议按游戏无关设计）
- mod 的推送式事件（v1 为轮询）

## 参考文档

- `slay-spire-2-copilot/docs/protocol.md` — 线协议 v1
- `slay-spire-2-copilot/docs/research/game-api-findings.md` — 游戏 API 面
- `slay-spire-2-copilot/references/commands.md` — 操作与状态速查
