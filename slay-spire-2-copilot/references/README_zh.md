# References 索引

路径均相对本 skill 文件夹。bridge/ 是工具文档；game/ 是游玩时查阅的静态
游戏参考。英文版：[README.md](README.md)

bridge/ — 工具（仅有英文版）：

- [commands](bridge/commands.md) — CLI 用法、动作与状态参考、日志目录契约
- [protocol](bridge/protocol.md) — 线协议 v1（本机 TCP 上的 JSON Lines）

game/ — 游戏知识（JSON 参考库）：

- [characters_zh](game/characters_zh.json) + [characters](game/characters.json) — 可玩角色、初始配置、流派
- [cards_zh](game/cards_zh.json) + [cards](game/cards.json) — 可打出的卡牌：费用、效果
- [powers_zh](game/powers_zh.json) + [powers](game/powers.json) — 战斗中的能力、增益与减益
- [relics_zh](game/relics_zh.json) + [relics](game/relics.json) — 遗物效果
- [potions_zh](game/potions_zh.json) + [potions](game/potions.json) — 药水效果
- [afflictions_zh](game/afflictions_zh.json) + [afflictions](game/afflictions.json) — 状态与卡牌绑定减益
- [intents_zh](game/intents_zh.json) + [intents](game/intents.json) — 敌人意图标签格式
- [monsters_zh](game/monsters_zh.json) + [monsters](game/monsters.json) — 敌人招式表与被动
- [events_zh](game/events_zh.json) + [events](game/events.json) — 事件房与已知分支

JSON 参考库 — key = live state 中的游戏 id；用 `spirectl lookup <key>` 解析；
miss 时自动查 spire-codex.com 并折入发现（curated:false），之后需 agent 精修。
markdown 孪生文件（game/*.md）在 live 验证通过前保留，之后退役——引用一律
指向 JSON 文件。
