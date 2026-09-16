# slay-spire-2-copilot

> 英文版：[README_EN.md](README_EN.md)

让 Claude Code / Codex 在本机自动游玩《杀戮尖塔 2》（Slay the Spire 2）的
AI 副驾驶。skill 被触发后，智能体读取牌局状态、做出决策并操作游戏，直至对局
结束，随后写入复盘并开启下一局。

## 演示

左右分屏实录：左侧游戏画面，右侧 Claude Code 终端实时决策日志。完整演示
约 2 分钟，含地图选择与整场战斗。

<div align="center">

https://github.com/user-attachments/assets/6eae44a2-312d-4a1c-abc3-f5617fe23f21

</div>

## 这个项目是干啥的

- **自动对局**：每回合实时读取游戏状态（血量、手牌、敌人意图、地图等），AI
  自主决定出牌、奖励与路线，通过通讯 mod 操作游戏
- **连续运行**：对局结束后自动写复盘、更新经验库、开始下一局；附带的外部
  看门狗脚本可定时检查游戏进程、桥接与日志的存活状态
- **跨局记忆**：`memory/` 下的经验与对局记录在后续会话自动加载；工具缺陷在
  本仓库内修复，对下次运行即时生效

## 怎么用

在 Claude Code 中发起 skill，并附带一个日志文件夹的绝对路径：

    用 Claude Code 打一局杀戮尖塔2  /Users/me/spire-logs/nightly

触发语（中英文皆可）："用 Claude Code 打一局杀戮尖塔2"、"play Slay the
Spire 2 via Claude Code or Codex"。

skill 启动后会依次完成环境准备与对局：检查 mod 安装状态，缺失或源码比已装
dll 更新时执行构建安装（dotnet build，产物拷贝至游戏 mods 目录）；游戏未运行
时通过 Steam 启动；随后经 doctor 完成握手验证并进入对局循环。首次带 mod
启动时，游戏内会出现一次 mod 警告，需要在游戏内点击接受。

对局日志写入指定的文件夹，文件名形如 `run-20260916-013052-a3f9c012.log`
（时间戳+哈希）。

以下命令用于排查与手动干预：

    cd slay-spire-2-copilot/slay-spire-2-copilot
    bash scripts/install-mod.sh                     # 构建/安装 mod
    python3 bridge/spirectl.py launch               # 启动游戏
    SPIREBRIDGE_LOG_DIR=<日志文件夹> python3 bridge/spirectl.py doctor

## 目录结构

    slay-spire-2-copilot/                  （仓库根目录）
      README.md / README_EN.md
      .gitignore
      slay-spire-2-copilot/                （skill 文件夹 — 全部运行时文件）
        SKILL.md                           （skill 定义 / 调用契约）
        bridge/                            （spirectl.py CLI）
        scripts/                           （shell 脚本：mod 构建安装、看门狗）
        mod/SpireBridge/                   （游戏内通讯 mod 源码）
        references/bridge/                 （CLI 速查、线协议）
        references/game/                   （角色、卡牌、能力、遗物、药水、状态、意图、怪物、事件）
        memory/                            （对局记忆：经验、台账、复盘）

skill 符号链接：`~/.claude/skills/slay-spire-2-copilot` → 上述 skill 文件夹。
运行时日志与看门狗状态写在仓库外的用户目录，不入库。

## 基本技术路线

整体是客户端–服务端架构，协议为本机 TCP 上的 JSON Lines（127.0.0.1:17612）：

    Claude Code（决策客户端）
      → bridge/spirectl.py（CLI：state / act / wait / sl / profile …）
      → spire-copilot-bridge mod（跑在游戏进程内的 Godot .NET mod）
      → 游戏 API（出牌、回合、地图、奖励等）

- **服务端（mod）**：只做两件事——导出完整状态快照、执行客户端下达的操作
  （出牌/回合/选奖励/开店购物…），不做任何决策。缺界面支持时当场补实现、
  重建 mod、重启游戏继续
- **客户端（spirectl + Claude）**：读快照 → 依经验库决策 → 发操作 → 等状态
  变化 → 循环；行动以 `act --wait` / `batch` 批量提交，决策与日志解耦
- **提速与稳定**：游戏内 `FastMode=Instant` + `NonInteractiveMode` 跳过动画；
  状态指纹哈希驱动等待；战斗结束/RINGING 卡死有服务端强制推进与 `sl`
  存档重载（约 18s，用于带信息重打）
- **记忆与迭代**：`memory/` 下的经验、复盘、changelog 随对局更新，下次会话
  自动加载；工具修复直接进本仓库

更细的协议见 `slay-spire-2-copilot/references/bridge/protocol.md`，CLI 速查见
`slay-spire-2-copilot/references/bridge/commands.md`。

## 致谢

modding 项目（社区参考实现）：

- [BaseLib-StS2](https://github.com/Alchyr/BaseLib-StS2) — Alchyr 的《杀戮尖塔 2》mod 基础库；mod 加载与游戏 API 约定的参考
- [CombatSolver](https://github.com/Torch1230/CombatSolver) — 战斗路线求解器 mod；卡牌/遗物/能力效果的结构化数据参考
- [STS2-Agent](https://github.com/CharTyr/STS2-Agent) — 游戏内 AI 队友 mod；怪物行为、事件与游戏知识提取参考
- [slay-the-streamer-2](https://github.com/Surfinite/slay-the-streamer-2) — Twitch 弹幕投票 mod；modding API 与界面流程研究参考
- [sts2-game-mod](https://github.com/AI-Ascension/sts2-game-mod)（AI-Ascension）— Rust 互操作 mod；游戏接口与实验记录参考

数据库与图鉴（参考文档数据来源）：

- [Spire Codex](https://spire-codex.com) — 卡牌/遗物数据库（577 卡、296 遗物）
- [slaythespire2.net](https://slaythespire2.net) — 中英文图鉴：卡牌/遗物/药水/怪物/事件（简中译名主要来源）
- [sts2.gg](https://sts2.gg) — 分角色卡牌数据库（简中卡名）
- [stratgg.com](https://www.stratgg.com) — 分角色卡牌与药水数据库
- [mobalytics](https://mobalytics.gg/slay-the-spire-2) — 卡牌 wiki
- [sts2-wiki.org](https://sts2-wiki.org) / [sts2.wiki](https://sts2.wiki) — 状态效果数值
- [gamerblurb](https://gamerblurb.com) — 状态牌列表
- [untapped.gg](https://sts2.untapped.gg) — 卡牌费用与稀有度
- [sts2guide.com](https://sts2guide.com)、[IGN wiki](https://www.ign.com/wikis/slay-the-spire-2/)、[游民星空](https://www.gamersky.com/z/slaythespire2/)、[灰机 wiki](https://sts.huijiwiki.com)、[namu.wiki](https://namu.wiki) — 攻略与译名参考
