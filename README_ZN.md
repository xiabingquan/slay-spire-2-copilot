# slay-spire-2-copilot

> 英文版：[README.md](README.md)

让 Claude Code / Codex 在本机**自动游玩《杀戮尖塔 2》**的 AI 副驾驶（copilot）。
你只要说一句「用 Claude Code 打一局杀戮尖塔2」，智能体就会自己读牌局、做决策、
点技能、推图、打 Boss，直到对局结束并写下复盘。

## 这个项目是干啥的

- **全自动对局**：实时读取游戏状态（血量、手牌、敌人意图、地图…），由 AI 自主
  决定出牌、奖励、路线，通过通讯 mod 直接操作游戏
- **持续运转**：对局结束自动写复盘、更新经验库、开启下一局；看门狗监控进程
  存活，异常时通过飞书通知
- **越打越稳**：跨对局持久记忆（教训、工具修复台账），工具 bug 在本仓库修复后
  立即生效

## 怎么用

1. **构建 mod**（需要 .NET SDK 9+；游戏程序集引用自本机 Steam 安装目录）：

       cd slay-spire-2-copilot/slay-spire-2-copilot
       bash setup/install-mod.sh

2. **启动游戏并验证**（首次带 mod 启动，在游戏内接受一次 mod 警告）：

       python3 bridge/spirectl.py launch
       SPIREBRIDGE_LOG_DIR=<日志文件夹> python3 bridge/spirectl.py doctor

3. **开一局**：在 Claude Code 中调起 skill，传入一个绝对路径的**日志文件夹**：

       用 Claude Code 打一局杀戮尖塔2  /Users/me/spire-logs/tonight

   skill 会被这类说法触发（中英文皆可）："用 Claude Code 打一局杀戮尖塔2"、
   "play Slay the Spire 2 via Claude Code or Codex"。

4. **对局日志**写入你传入的文件夹，文件名形如 `run-20260916-013052-a3f9c012.log`
   （时间戳+哈希）；游玩仍在进行时如需暂停，可让 Claude 关闭看门狗告警。

## 基本技术路线

整体是**客户端–服务端**架构，协议为本机 TCP 上的 JSON Lines（127.0.0.1:17612）：

    Claude Code（决策客户端）
      → bridge/spirectl.py（CLI：state / act / wait / sl / profile …）
      → spire-copilot-bridge mod（跑在游戏进程内的 Godot .NET mod）
      → 游戏 API（出牌、回合、地图、奖励等）

- **服务端（mod）**：只做两件事——导出完整状态快照、执行客户端下达的操作
  （出牌/回合/选奖励/开店购物…），**不做任何决策**。缺界面支持时当场补实现、
  重建 mod、重启游戏继续（完整性规则）
- **客户端（spirectl + Claude）**：读快照 → 依经验库决策 → 发操作 → 等状态
  变化 → 循环；行动以 `act --wait` / `batch` 批量提交，决策与日志解耦
- **提速与稳定**：游戏内 `FastMode=Instant` + `NonInteractiveMode` 跳过动画；
  状态指纹哈希驱动等待；战斗结束/RINGING 卡死有服务端强制推进与 `sl`
  存档重载（约 18s，用于带信息重打）
- **记忆与迭代**：`memory/` 下的经验、复盘、changelog 随对局更新，下次会话
  自动加载；工具修复直接进本仓库

更细的协议见 `slay-spire-2-copilot/docs/protocol.md`，CLI 速查见
`slay-spire-2-copilot/references/commands.md`。
