# User guide（用户指南）

记忆写作指南——四点：格式、写入时机、查阅时机、备注。

## 格式

- 每局笔记（`memory/runs/` 下的英文 + `_zh` 中文对）：格式遵循
  `memory/template.md`
- 跨局总览表、阶段性反思、SL 列：规则遵循 `memory/overview.md` 自身
  （其表格规则块与 `# 阶段性反思` 节）

## 写入时机

- **run 笔记 + overview 行**：每局结束立即写——`memory/runs/` 下的笔记
  对，以及 overview.md 表格顶部插入一行
- **阶段性反思**：第一次覆盖当时为止全部对局；此后每 20 局一次
  （36–55、56–75……）——累计对局数到达边界时触发
- **lessons/**：本局沉淀出的前向经验写入对应分类文件；阶段性反思产出
  的常备结论同样进入 lessons

## 查阅时机

- **开局——读通用性经验**：`overview.md`（跨局全景）+ lessons 通用类
  内容——战斗原则、协同、角色脊线
- **每一步决策之前——查该决策对应的历史经验**，先查再动手：
  - 选遗物 → `lessons/relics.md`——这个遗物有没有已知 trick
  - 选路线 → `lessons/route.md`
  - 事件房选择 → `lessons/events.md`
  - 商店/经济决策 → `lessons/economy.md`
  - 进战斗前 → `lessons/enemies.md`（该敌人教条）+
    `spirectl lookup <id>`（机制数值：招式/intents/hp——结构化事实）
  - 抓牌/构筑抉择 → `lessons/cards.md`、`lessons/synergies.md`、
    `lessons/characters.md`
- **单局笔记按需**：文件名前缀 = overview.md 的对局序号——查号后开文件
- 原则：任何决策动念时先查历史经验再选，绝不凭印象行事

## 备注

- 经验是建议性的，不是硬性模式：措辞用「建议 / 参考」，避免「强烈建议 /
  强烈建议不要」
- 所有过去对局仅供参考——局内具体措施按当前局 live 状态定（HP、牌组、
  手牌、敌人、地图几何），live 永远优先。局中查阅时把旧经验当数据读、
  再适配，绝不照搬别局剧本
- 只记录/只沉淀前向价值内容：复仇叙事、过程/修复日志绝不进记忆
- 机制事实不作记忆：用 `spirectl lookup <id>` 解析（数据存储程序化、
  codex 为权威源）；系统侧缺陷在所属系统当场修复，绝不作为 run factor
