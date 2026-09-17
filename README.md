<div align="center">

https://github.com/user-attachments/assets/6eae44a2-312d-4a1c-abc3-f5617fe23f21

</div>

> 英文版：[README_EN.md](README_EN.md)

# slay-spire-2-copilot

一个可直接加载进 Claude Code、Codex 等 agent harness 的 skill，让智能体在本机
自动游玩《杀戮尖塔 2》（Slay the Spire 2）。skill 被触发后，智能体读取牌局
状态、做出决策并操作游戏，直至对局结束，随后写入本局 memory 记录
（Summary + 回顾）并开启下一局。

## 这个项目是干啥的

- **自动对局**：每回合实时读取游戏状态（血量、手牌、敌人意图、地图等），AI
  自主决定出牌、奖励与路线，通过通讯 mod 操作游戏
- **连续运行**：对局结束后自动写本局 memory 记录、开始下一局；附带的外部
  看门狗脚本可定时检查游戏进程、桥接与日志的存活状态
- **跨局记忆**：`memory/` 下的对局记录（summary、角色玩法）在后续会话自动
  加载；工具缺陷在本仓库内修复，对下次运行即时生效

## 怎么用

在 Claude Code 中发起 skill，并附带一个日志文件夹的绝对路径：

    用 Claude Code 打一局杀戮尖塔2  /Users/me/spire-logs/nightly

触发语（中英文皆可）："用 Claude Code 打一局杀戮尖塔2"、"play Slay the
Spire 2 via Claude Code or Codex"。

对局日志写入指定的文件夹，文件名形如 `run-20260916-013052-a3f9c012.log`
（时间戳+哈希）。

## 目录结构

    slay-spire-2-copilot/                  （仓库根目录）
      README.md / README_EN.md
      doctor.md                            （文档体检清单）
      .gitignore
      slay-spire-2-copilot/                （skill 文件夹 — 全部运行时文件）
        SKILL.md                           （skill 定义 / 调用契约）
        bridge/                            （spirectl.py CLI）
        scripts/                           （shell 脚本：mod 构建安装、看门狗）
        mod/SpireBridge/                   （游戏内通讯 mod 源码）
        references/bridge/                 （CLI 速查、线协议）
        references/game/                   （角色、卡牌、能力、遗物、药水、状态、意图、怪物、事件）
        memory/                            （对局记忆：user guide、每局记录）

skill 符号链接：`~/.claude/skills/slay-spire-2-copilot` → 上述 skill 文件夹。

文档体检：仓库根目录的 [doctor.md](doctor.md) 是文档组织结构检查清单——README 只做
项目综述、`mod/` 与 `bridge/` 只放代码、对局记忆只写入 `memory/runs/`、
`references/game/` 只保留静态资料、文档不含用户对话内容（评论、需求、改进等）。
使用方法：让 agent 按清单执行（如 "run doctor.md"）并修正违规。触发时机：每局对局
结束后、提交文档改动前，或怀疑文档放错位置时。

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
