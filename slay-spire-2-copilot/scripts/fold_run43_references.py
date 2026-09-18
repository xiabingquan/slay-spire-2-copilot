#!/usr/bin/env python3
"""Fold run-43 live facts into references/game EN+ZH twins (curated:true)."""
import json
from pathlib import Path

REF = Path(__file__).resolve().parents[1] / "references" / "game"

def load(dom):
    en = json.loads((REF / f"{dom}.json").read_text())
    zh = json.loads((REF / f"{dom}_zh.json").read_text())
    return en, zh

def save(dom, en, zh):
    (REF / f"{dom}.json").write_text(json.dumps(en, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    (REF / f"{dom}_zh.json").write_text(json.dumps(zh, ensure_ascii=False, indent=2, sort_keys=True) + "\n")

def upsert(en, zh, key, en_ent, zh_ent):
    """Merge into both twins; curated:true; keep unknown keys forward."""
    for store, ent in ((en, en_ent), (zh, zh_ent)):
        cur = store.get(key, {})
        cur.update(ent)
        cur["curated"] = True
        cur["id"] = cur.get("id", key)
        cur["kind"] = cur.get("kind", en_ent.get("kind", "entry"))
        store[key] = cur

SRC = "run-43 live fold 2026-09-19 (log run-20260919-020127-e4b53676.log)"

# ---------------- monsters ----------------
en, zh = load("monsters")
upsert(en, zh, "SoulFysh",
  {"kind":"monster","name":"SoulFysh","aliases":["SoulFysh","Soulfysh","SOUL_FYSH","灵魂异鱼"],
   "is_boss":True,"acts":["Act1"],"hp":{"base":211,"notes":"Act1 Boss live 211/211 A1 run-43"},
   "cycle":["BECKON_MOVE","DE_GAS_MOVE","GAZE_MOVE","FADE_MOVE","SCREAM_MOVE"],
   "description":("Act1 Boss. Live run-43 A1 211 HP, killed T11 at 27/80. Cycle BECKON(Status x2, injects BECKON status cards) -> "
     "DE_GAS single 16 (A:17, live intent 16-24 under player Vuln) -> GAZE single 7 (A:8) + 1 status card -> "
     "FADE applies INTANGIBLE 2 to self (ticks down end of owner turn; our T-of-FADE is still a full-damage window, "
     "intangible lands on enemy turn) -> SCREAM single 13 (A:15) + 3 Vulnerable to player -> repeat. "
     "Doctrine: dump on BECKON/GAZE free windows; account for Intangible 1-2 turns where every damage INSTANCE caps at 1 "
     "(Stone Calendar 52 also caps to 1); BECKON status cards in hand at end of turn deal 6 unblockable HP EACH - "
     "play them (1 cost, target=None still playable) or exhaust them same turn. Run-43 lost 18 HP to 3 unplayed Beckons."),
   "play_notes":SRC,
   "source":"run-43 live T11 kill + cards.json BECKON + powers INTANGIBLE"},
  {"kind":"monster","name":"灵魂异鱼","aliases":["SoulFysh","Soulfysh","SOUL_FYSH","灵魂异鱼"],
   "is_boss":True,"acts":["Act1"],"hp":{"base":211,"notes":"Act1 Boss live 211/211 A1 对局43"},
   "cycle":["BECKON_MOVE","DE_GAS_MOVE","GAZE_MOVE","FADE_MOVE","SCREAM_MOVE"],
   "description":("Act1 Boss。对局43 A1 实测 211HP，T11 以 27/80 击杀。循环 BECKON（状态×2，注入 BECKON 状态牌）→ "
     "DE_GAS 单体16（A:17，玩家带易伤时 live 意图 16-24）→ GAZE 单体7（A:8）+1 状态牌 → "
     "FADE 给自身 INTANGIBLE 2（敌方回合末递减；FADE 所在我方回合仍是全额伤害窗，虚无在敌方回合才生效）→ "
     "SCREAM 单体13（A:15）+ 给玩家易伤3 → 循环。"
     "教条：BECKON/GAZE 免费窗倾泻；虚无期每次伤害实例上限1（石日历52伤同样被压成1）；"
     "回合结束仍留在手牌的 BECKON 状态牌每张造成 6 无视格挡伤害——必须当回合打出（1费，target=None 仍可打）或排出。"
     "对局43 因 3 张未打出的 Beckon 白付 18HP。"),
   "play_notes":"对局43 T11 击杀实证","source":"对局43 live + cards.json BECKON + powers INTANGIBLE"})

upsert(en, zh, "SLUMBERING_BEETLE",
  {"kind":"monster","name":"Slumbering Beetle","aliases":["SlumberingBeetle","SLUMBERING_BEETLE","熟睡甲虫"],
   "is_boss":False,"acts":["Act2"],"hp":{"base":86,"notes":"live 86/86 A1 run-43"},
   "cycle":["SNORE_MOVE","ROLL_OUT_MOVE"],
   "description":("Act2 normal, 86 HP live run-43. PLATING:15 = +15 Block at combat start AND at end of owner's side turn, "
     "-1 stack per turn start. SLUMBER:3 = counter decrements on unblocked damage received AND at end of owner turn; "
     "at 0 owner wakes and cycles SNORE(sleep) -> ROLL_OUT (single 16 A:18 + self Strength 2). "
     "Doctrine: while it sleeps it is 0 threat - kill the other enemies first; each unblocked HP instance chips Slumber, "
     "so even chip damage wakes it. Once awake ROLL_OUT 16-18+ per turn is the fight's biggest intent. "
     "Run-43 death factor: woke mid-fight at player 6 HP and ROLL_OUT leaked through remaining block."),
   "play_notes":SRC,"source":"codex-api + run-43 live"},
  {"kind":"monster","name":"熟睡甲虫","aliases":["SlumberingBeetle","SLUMBERING_BEETLE","熟睡甲虫"],
   "is_boss":False,"acts":["Act2"],"hp":{"base":86,"notes":"live 86/86 A1 对局43"},
   "cycle":["SNORE_MOVE","ROLL_OUT_MOVE"],
   "description":("Act2 普通怪，对局43 实测 86HP。PLATING:15 = 战斗开始与自身回合末各获得 15 格挡，回合开始 −1 层。"
     "SLUMBER:3 = 受到未格挡伤害与自身回合末各递减 1，归零醒来后循环 SNORE（睡眠）→ ROLL_OUT（单体16 A:18 + 自身力量2）。"
     "教条：睡着时 0 威胁，先杀其他敌人；任何穿透格挡的伤害都会削 Slumber，微量输出也会唤醒它。"
     "醒后 ROLL_OUT 16-18+/回合是本战最大意图。对局43 死因之一：玩家 6HP 时甲虫醒来，ROLL_OUT 穿挡击杀。"),
   "play_notes":"对局43 live","source":"codex-api + 对局43 live"})

upsert(en, zh, "BOWLBUG_SILK",
  {"kind":"monster","name":"Bowlbug (Silk)","aliases":["BowlbugSilk","BOWLBUG_SILK","盛碗虫（丝）"],
   "is_boss":False,"acts":["Act2"],"hp":{"base":43,"notes":"live 43/43 A1 run-43"},
   "cycle":["TOXIC_SPIT_MOVE","THRASH_MOVE"],
   "description":("Act2 bowlbug variant, 43 HP live run-43. TOXIC_SPIT = debuff only (Weak 1 to player, 0 damage, free window); "
     "THRASH = multi 4x2 (A:5 per hit). No HardToKill/Plating - plain HP. Kill-first with the Rock sibling when possible: "
     "the Rock's IMBALANCED stun window is the cleanup turn for this add."),
   "play_notes":SRC,"source":"codex + run-43 live"},
  {"kind":"monster","name":"盛碗虫（丝）","aliases":["BowlbugSilk","BOWLBUG_SILK","盛碗虫（丝）"],
   "is_boss":False,"acts":["Act2"],"hp":{"base":43,"notes":"live 43/43 A1 对局43"},
   "cycle":["TOXIC_SPIT_MOVE","THRASH_MOVE"],
   "description":("Act2 碗虫变体，对局43 实测 43HP。TOXIC_SPIT = 仅 debuff（玩家 Weak 1，0 伤，免费窗）；"
     "THRASH = 多段 4x2（A:5/击）。无 HardToKill/Plating，纯血量。优先与石碗虫一同处理："
     "石虫 IMBALANCED 眩晕窗就是清理本体的回合。"),
   "play_notes":"对局43 live","source":"codex + 对局43 live"})

upsert(en, zh, "BOWLBUG_ROCK",
  {"kind":"monster","name":"Bowlbug (Rock)","aliases":["BowlbugRock","BOWLBUG_ROCK","盛碗虫（石）"],
   "is_boss":False,"acts":["Act2"],"hp":{"base":48,"notes":"live 47-48 A1 run-42/43"},
   "cycle":["HEADBUTT_MOVE","POST_HEADBUTT"],
   "description":("Act2, 47-48 HP live A1. IMBALANCED:1 - when owner's attack is FULLY blocked, owner is stunned "
     "(IsOffBalance); partial block does NOT stun. HEADBUTT single 15 live (A:16-class). "
     "Doctrine: need >= incoming block on its attack turn (15 base; Dex buffs lower the card count needed - "
     "run-43: UltimateDefend 13+Dex3=16 solo stun; run-39 note Dex+Defend x2=14 was one short). "
     "Stun window = cleanup turn for adds (silk/egg). Run-43 reconfirmed stun at 18 block vs 15."),
   "play_notes":SRC,"source":"run-39/40/43 live"},
  {"kind":"monster","name":"盛碗虫（石）","aliases":["BowlbugRock","BOWLBUG_ROCK","盛碗虫（石）"],
   "is_boss":False,"acts":["Act2"],"hp":{"base":48,"notes":"live 47-48 A1 对局42/43"},
   "cycle":["HEADBUTT_MOVE","POST_HEADBUTT"],
   "description":("Act2，live A1 47-48HP。IMBALANCED:1——其攻击被完全格挡时眩晕（部分格挡不触发）。"
     "HEADBUTT 单体 15（A:16 级）。教条：其攻击回合需要 ≥ 来伤的格挡（基础15；敏捷加成后所需挡牌更少——"
     "对局43：终极防御13+敏捷3=16 单卡眩晕；对局39 注记：敏捷+Defend×2=14 差一点）。"
     "眩晕窗 = 清理随从（丝/卵）的回合。对局43 以 18 挡 vs 15 再次实证眩晕。"),
   "play_notes":"对局43 live","source":"对局39/40/43 live"})

upsert(en, zh, "LOUSE_PROGENITOR",
  {"kind":"monster","name":"Louse Progenitor","aliases":["LouseProgenitor","LOUSE_PROGENITOR","虱虫之祖"],
   "is_boss":False,"acts":["Act2"],"hp":{"base":136,"notes":"live 136/136 A1 run-43; archive A 138-141"},
   "cycle":["WEB_CANNON_MOVE","CURL_AND_GROW_MOVE","POUNCE_MOVE"],
   "description":("Act2, 136 HP live run-43 A1 (archive 134-136 base / A1 138-141 table drift - live wins). "
     "Cycle live run-43: WEB_CANNON (single 9 A:10 + Frail 2; live intent inflates with its Strength, 14-24 observed) "
     "-> CURL_AND_GROW (Defend+Buff: block 14 + self Strength 5 - FREE window, dump damage here) "
     "-> POUNCE (single 14 A:16; live intent 19-24 with Str stacks). "
     "CURL_UP-style post-damage block still applies on hit turns. Each Curl adds +5 Str - POUNCE after two Curls is "
     "24-class; block math must use the Str-inflated number. Stone Calendar turn-7 52 AoE killed it at 36 HP in run-43."),
   "play_notes":SRC,"source":"codex-api + run-43 live"},
  {"kind":"monster","name":"虱虫之祖","aliases":["LouseProgenitor","LOUSE_PROGENITOR","虱虫之祖"],
   "is_boss":False,"acts":["Act2"],"hp":{"base":136,"notes":"live 136/136 A1 对局43；档案 A 138-141"},
   "cycle":["WEB_CANNON_MOVE","CURL_AND_GROW_MOVE","POUNCE_MOVE"],
   "description":("Act2，对局43 A1 实测 136HP（档案表值 134-136/A1 138-141——live 为准）。"
     "对局43 实测循环：WEB_CANNON（单体9 A:10 + Frail 2；意图随其力量膨胀，观测到 14-24）"
     "→ CURL_AND_GROW（防御+增益：自身 14 挡 + 力量5——免费窗，倾泻回合）"
     "→ POUNCE（单体14 A:16；叠力量后 live 意图 19-24）。"
     "受击回合仍有 CurlUp 类后置挡。每次 Curl +5 力量——两次 Curl 后 POUNCE 是 24 级，挡位计算必须用力量膨胀后的数字。"
     "对局43 中石日历第7回合 52 伤在它 36HP 时完成击杀。"),
   "play_notes":"对局43 live","source":"codex-api + 对局43 live"})

upsert(en, zh, "EXOSKELETON",
  {"kind":"monster","name":"Exoskeleton","aliases":["Exoskeleton","EXOSKELETON","外骨骼虫"],
   "is_boss":False,"acts":["Act2"],"hp":{"base":25,"notes":"live trio 24/25/26 A1 run-43"},
   "cycle":["SKITTER_MOVE","MANDIBLES_MOVE","ENRAGE_MOVE"],
   "description":("Act2 normal, live run-43 trio 24/26/25 HP. HARD_TO_KILL:9 = damage received per INSTANCE capped at 9 "
     "(excess discarded, not banked) - distinct from per-turn caps: pace MULTIPLE hits <=9 each (TwinStrike 5x2 full value; "
     "one 32-dmg Bludgeon wastes 23). Moves: SKITTER multi 1x3 (Str-inflates, 3x3 seen at Str2), MANDIBLES single 8 "
     "(A:9, Str-inflates to 10+), ENRAGE self +2 Strength (free window). Doctrine: kill-first order by current HP, "
     "use Enrage turns as dump windows, Feed Fatal for +MaxHP on the lowest-HP bug. Run-43 Feed Fatal on the 4-HP bug."),
   "play_notes":SRC,"source":"run-40/41/43 live"},
  {"kind":"monster","name":"外骨骼虫","aliases":["Exoskeleton","EXOSKELETON","外骨骼虫"],
   "is_boss":False,"acts":["Act2"],"hp":{"base":25,"notes":"live 三只 24/25/26 A1 对局43"},
   "cycle":["SKITTER_MOVE","MANDIBLES_MOVE","ENRAGE_MOVE"],
   "description":("Act2 普通怪，对局43 三只实测 24/26/25HP。HARD_TO_KILL:9 = 每次伤害实例上限 9（溢出作废，不存银行）"
     "——与按回合上限不同：要打多段 ≤9 的小伤（TwinStrike 5x2 全额；单发 32 伤的重锤浪费 23）。"
     "招式：SKITTER 多段 1x3（随力量膨胀，力量2 时见 3x3）、MANDIBLES 单体8（A:9，力量下 10+）、"
     "ENRAGE 自身力量+2（免费窗）。教条：按当前血量定击杀顺序，ENRAGE 回合倾泻，"
     "对最低血量的虫子打 Feed Fatal 拿 MaxHP。对局43 在 4HP 的虫子上打出 Feed Fatal。"),
   "play_notes":"对局43 live","source":"对局40/41/43 live"})
save("monsters", en, zh)

# ---------------- powers ----------------
en, zh = load("powers")
upsert(en, zh, "SLUMBER_POWER",
  {"kind":"power","name":"Slumber","aliases":["SLUMBER","SlumberPower"],"power_type":"Buff","stack_type":"Counter","counter_class":True,
   "description":("counter decrements on unblocked damage received AND at end of owner's side turn; at 0, owner wakes "
     "(Slumbering Beetle -> ROLL_OUT cycle). Sleeping owner is 0 threat; any HP-leaking chip accelerates the wake. "
     "Live run-43: Slumber 3 -> 2 -> 1 -> wake mid-fight; ROLL_OUT then killed the player at 6 HP."),
   "play_notes":SRC,"source":"powers.md + run-43 live"},
  {"kind":"power","name":"沉睡","aliases":["SLUMBER","SlumberPower"],"power_type":"Buff","stack_type":"Counter","counter_class":True,
   "description":("受到未格挡伤害时与拥有者回合末各递减 1；归零时醒来（熟睡甲虫 → ROLL_OUT 循环）。"
     "沉睡中 0 威胁；任何穿透格挡的微量伤害都会加速醒来。对局43：Slumber 3→2→1→ 中途醒来，"
     "ROLL_OUT 在玩家 6HP 时完成击杀。"),
   "play_notes":"对局43 live","source":"powers.md + 对局43 live"})

upsert(en, zh, "INTANGIBLE_POWER",
  {"kind":"power","name":"Intangible","aliases":["INTANGIBLE","IntangiblePower"],"power_type":"Buff","stack_type":"Counter","counter_class":True,
   "description":("damage AND HP loss received by owner capped at 1 per INSTANCE; ticks down at end of owner's side turn. "
     "Multi-hit cards deal 1 per hit (best rate during the window); one big hit wastes everything above 1. "
     "Relic AoE like Stone Calendar 52 is also capped to 1 while stacks remain. Live run-43: SoulFysh FADE applied 2, "
     "ticked to 1 end of the same enemy turn - our next turn still faced Intangible 1."),
   "play_notes":SRC,"source":"powers.md + run-43 live"},
  {"kind":"power","name":"虚无","aliases":["INTANGIBLE","IntangiblePower"],"power_type":"Buff","stack_type":"Counter","counter_class":True,
   "description":("拥有者每次受到的伤害与 HP 流失实例上限 1；拥有者回合末递减。多段牌每段 1（窗内最优速率）；"
     "单发大伤超过 1 的部分全部作废。石日历 52 伤这类遗物 AoE 在层数存续时同样被压成 1。"
     "对局43：灵魂异鱼 FADE 施加 2 层，同一敌方回合末减为 1——下一我方回合仍面对虚无 1。"),
   "play_notes":"对局43 live","source":"powers.md + 对局43 live"})

upsert(en, zh, "IMBALANCED_POWER",
  {"kind":"power","name":"Imbalanced","aliases":["IMBALANCED","ImbalancedPower"],"power_type":"Debuff","stack_type":"Single","counter_class":False,
   "description":("when owner's attack is fully blocked, owner is stunned (BowlbugRock family sets IsOffBalance). "
     "Partial block does NOT trigger. Threshold = the attack's live intent value (15-class HEADBUTT). "
     "Live run-43: 18 block vs 15 stunned; 8 block vs 15 did not (leaked 7 + died to the add's hit the same turn)."),
   "play_notes":SRC,"source":"powers.md + run-39/43 live"},
  {"kind":"power","name":"失衡","aliases":["IMBALANCED","ImbalancedPower"],"power_type":"Debuff","stack_type":"Single","counter_class":False,
   "description":("拥有者的攻击被完全格挡时，拥有者被眩晕（碗虫石系走 IsOffBalance）。部分格挡不触发。"
     "阈值 = 该攻击的 live 意图值（HEADBUTT 15 级）。对局43：18挡 vs 15 触发眩晕；8挡 vs 15 未触发"
     "（漏 7，同回合被随从补刀致死）。"),
   "play_notes":"对局43 live","source":"powers.md + 对局39/43 live"})

upsert(en, zh, "HARD_TO_KILL_POWER",
  {"kind":"power","name":"Hard To Kill","aliases":["HARD_TO_KILL","HardToKillPower"],"power_type":"Buff","stack_type":"Counter","counter_class":True,
   "description":("owner's damage received per INSTANCE capped at Amount (ModifyDamageCap); excess on that hit discarded, "
     "not banked. Exoskeleton Amount=9 live run-41/43: pace MULTIPLE hits <=Amount (TwinStrike 5x2 each hit full; "
     "one huge hit wastes the excess). Distinct from per-turn caps (HARDENED_SHELL) - this is per-hit."),
   "play_notes":SRC,"source":"powers.md + run-41/43 live"},
  {"kind":"power","name":"难以击杀","aliases":["HARD_TO_KILL","HardToKillPower"],"power_type":"Buff","stack_type":"Counter","counter_class":True,
   "description":("拥有者每次受到的伤害实例上限 Amount，该次溢出作废（不存银行）。外骨骼虫 Amount=9（对局41/43 live）："
     "打多段 ≤Amount 的小伤（TwinStrike 5x2 每段全额；单发大伤浪费溢出）。"
     "与按回合上限（HARDENED_SHELL）不同——这是按击。"),
   "play_notes":"对局43 live","source":"powers.md + 对局41/43 live"})

upsert(en, zh, "PLATING_POWER",
  {"kind":"power","name":"Plating","aliases":["PLATING","PlatingPower"],"power_type":"Buff","stack_type":"Counter","counter_class":True,
   "description":("at start of owner's side turn (not turn 1 for the holder) owner loses 1 stack; at end of owner's side "
     "turn owner gains Amount Block. Enemies with Plating also gain Amount Block at combat start. Exact-cover math: "
     "current block + end-of-turn plating vs enemy intent. Live run-43: Slumbering Beetle PLATING 15, block 15->14->13 "
     "as stacks decremented, refreshed every its turn end."),
   "play_notes":SRC,"source":"powers.md + run-43 live"},
  {"kind":"power","name":"镀甲","aliases":["PLATING","PlatingPower"],"power_type":"Buff","stack_type":"Counter","counter_class":True,
   "description":("拥有者回合开始时（持有者第1回合除外）−1 层；拥有者回合末获得 Amount 格挡。"
     "带镀甲的敌人战斗开始时也获得 Amount 格挡。精确覆盖算式：当前挡 + 回合末镀甲挡 vs 敌方意图。"
     "对局43：熟睡甲虫 PLATING 15，挡 15→14→13 随层递减，其每回合末刷新。"),
   "play_notes":"对局43 live","source":"powers.md + 对局43 live"})

upsert(en, zh, "CURL_UP_POWER",
  {"kind":"power","name":"Curl Up","aliases":["CURL_UP","CurlUpPower"],"power_type":"Buff","stack_type":"Counter","counter_class":True,
   "description":("post-damage block grant: after damage lands on the owner, owner gains Amount Block "
     "(run-42 live order: 6 damage landed THEN +14 block appeared - not pre-block). "
     "Live run-43 LouseProgenitor CURL_UP 14 with the same post-damage order on hit turns."),
   "play_notes":SRC,"source":"powers.md + run-42/43 live"},
  {"kind":"power","name":"蜷缩","aliases":["CURL_UP","CurlUpPower"],"power_type":"Buff","stack_type":"Counter","counter_class":True,
   "description":("后置格挡授予：伤害落到拥有者身上之后，拥有者获得 Amount 格挡"
     "（对局42 live 顺序：6 伤先落地，然后才出现 +14 挡——不是前置挡）。"
     "对局43 虱虫之祖 CURL_UP 14 在受击回合呈现同样的后置顺序。"),
   "play_notes":"对局43 live","source":"powers.md + 对局42/43 live"})

upsert(en, zh, "DEMON_FORM_POWER",
  {"kind":"power","name":"Demon Form","aliases":["DEMON_FORM","DemonFormPower"],"power_type":"Buff","stack_type":"Counter","counter_class":False,
   "description":("at start of owner's side turn, apply +Amount STRENGTH_POWER to owner. Long-fight strength engine; "
     "card form seen in run-43 Act1-boss reward (not picked - Feed taken for MaxHP economy instead)."),
   "play_notes":SRC,"source":"powers.md + run-43 reward screen"},
  {"kind":"power","name":"恶魔之形","aliases":["DEMON_FORM","DemonFormPower"],"power_type":"Buff","stack_type":"Counter","counter_class":False,
   "description":("拥有者回合开始时，给自身 +Amount 力量。长战力量引擎；对局43 Act1 Boss 奖励屏出现卡牌形态"
     "（未选——为 MaxHP 经济选了狂宴）。"),
   "play_notes":"对局43 奖励屏","source":"powers.md + 对局43"})

upsert(en, zh, "COLOSSUS_POWER",
  {"kind":"power","name":"Colossus","aliases":["COLOSSUS","ColossusPower"],"power_type":"Buff","stack_type":"Counter","counter_class":True,
   "description":("attacks against owner from a dealer that has VULNERABLE_POWER deal x0.5 (DamageDecrease 0.5); "
     "decrements 1 at end of Enemy side turn. Requires the attacker to carry Vuln - useless if no Vuln source is in hand. "
     "Live run-43: power online at 1 HP but neither enemy carried Vuln, so no halving fired."),
   "play_notes":SRC,"source":"powers.md + run-43 live"},
  {"kind":"power","name":"巨像","aliases":["COLOSSUS","ColossusPower"],"power_type":"Buff","stack_type":"Counter","counter_class":True,
   "description":("携带 VULNERABLE_POWER 的攻击者对拥有者的攻击 ×0.5（DamageDecrease 0.5）；敌方回合末递减 1。"
     "前提是攻击者身上有易伤——手牌无易伤源时无效。对局43：1HP 时 power 上线但两名敌人均无易伤，减半未触发。"),
   "play_notes":"对局43 live","source":"powers.md + 对局43 live"})
save("powers", en, zh)

# ---------------- cards ----------------
en, zh = load("cards")
upsert(en, zh, "BECKON",
  {"kind":"card","name":"Beckon","aliases":["Beckon","BECKON","招引"],"card_type":"status","character_pool":"STATUS",
   "cost":"1","rarity":"status","target_type":None,"upgrade":None,"keywords":[],
   "description":("status card injected by SoulFysh BECKON_MOVE (2 per cast). In hand at end of turn: lose 6 HP "
     "unblockable PER CARD. Play cost 1 with target=None - playing it removes the EoT tax (it has no other effect); "
     "exhaust also works. Run-43 lesson: 3 Beckons left in hand at EoT = 18 unblockable HP lost; 'target=None ok' "
     "cards ARE playable - the 1-cost dump is always cheaper than the tax."),
   "play_notes":SRC,"source":"cards.md L569 + run-43 live"},
  {"kind":"card","name":"招引","aliases":["Beckon","BECKON","招引"],"card_type":"status","character_pool":"STATUS",
   "cost":"1","rarity":"status","target_type":None,"upgrade":None,"keywords":[],
   "description":("灵魂异鱼 BECKON_MOVE 注入的状态牌（每次 2 张）。回合结束仍在手牌：每张失去 6 HP（无视格挡）。"
     "打出费用 1、target=None——打出即可免除回合末税（无其他效果）；排出同样有效。"
     "对局43 教训：3 张 Beckon 留在手牌 = 白付 18 无视格挡 HP；「target=None ok」的牌是可打出的——"
     "1 费打出永远比交税便宜。"),
   "play_notes":"对局43 live","source":"cards.md + 对局43 live"})

upsert(en, zh, "BARRICADE",
  {"kind":"card","name":"Barricade","aliases":["Barricade","BARRICADE","壁垒"],"card_type":"power","character_pool":"IRONCLAD",
   "cost":"3","rarity":"uncommon",
   "description":("cost 3 power: gain BARRICADE_POWER - owner's Block is NOT cleared at turn end (ShouldClearBlock false). "
     "Block accumulates every turn (Orichalcum 6/turn + all block cards stack into a wall). "
     "Shop (5,0) Act2 live price 150g run-43. Run-2 death cause was 'Barricade never resolved' - when it lands early "
     "with block density it is an archetype win condition; at 3 cost it needs energy support (Pyre+) or a free window."),
   "play_notes":SRC,"source":"run-2 autopsy + run-43 shop live"},
  {"kind":"card","name":"壁垒","aliases":["Barricade","BARRICADE","壁垒"],"card_type":"power","character_pool":"IRONCLAD",
   "cost":"3","rarity":"uncommon",
   "description":("3费 power：获得 BARRICADE_POWER——拥有者的格挡不再回合末清空。格挡逐回合累积"
     "（橙铜每回合6 + 所有挡牌堆叠成墙）。对局43 Act2 商店 (5,0) live 价格 150金。"
     "对局2 死因是「Barricade 从未结算」——在挡密度足够时早落地即架构胜利条件；3 费需要能量支持（Pyre+）或免费窗。"),
   "play_notes":"对局43 live","source":"对局2 复盘 + 对局43 商店 live"})

upsert(en, zh, "FEED",
  {"kind":"card","name":"Feed","aliases":["Feed","FEED","狂宴"],"card_type":"attack","character_pool":"IRONCLAD",
   "cost":"1","rarity":"common",
   "description":("Exhaust, deal 10 damage; if Fatal gain 3 Max HP (upgrade +2 dmg / +4 MaxHP). "
     "MaxHP gain also raises current HP by the same amount (live run-43: 38->42/88 on Fatal, 80->84 then 84->88). "
     "1-cost HP-economy engine: Act2 trash fights offer frequent Fatals. Live run-43 x2 Fatals in one Act."),
   "play_notes":SRC,"source":"cards.md + run-43 live x2 Fatal"},
  {"kind":"card","name":"狂宴","aliases":["Feed","FEED","狂宴"],"card_type":"attack","character_pool":"IRONCLAD",
   "cost":"1","rarity":"common",
   "description":("消耗，造成10伤；击杀则 +3 MaxHP（升级 +2伤/+4MaxHP）。MaxHP 增益同步增加当前 HP"
     "（对局43 live：Fatal 时 38→42/88；本局 80→84→88 两次 Fatal）。1费 HP 经济引擎：Act2 小怪战 Fatal 机会密集。"),
   "play_notes":"对局43 live 两次 Fatal","source":"cards.md + 对局43 live"})

upsert(en, zh, "FORGOTTEN_RITUAL",
  {"kind":"card","name":"Forgotten Ritual","aliases":["Forgotten Ritual","FORGOTTEN_RITUAL","被遗忘的仪式"],
   "card_type":"skill","character_pool":"IRONCLAD","cost":"1","rarity":"uncommon",
   "description":("Exhaust; if another card was Exhausted this turn, gain 3 Energy (upgrade 4). Own exhaust does NOT "
     "count (EvilEye-class). Synergy spine: TrueGrit/AshenStrike/Tremble/Feed exhaust first, Ritual refunds +3e. "
     "Variance tax live run-43: TrueGrit's random exhaust ate the Ritual itself on its debut turn - treat random "
     "exhaust as a threat to engine pieces, not only a thinning tool."),
   "play_notes":SRC,"source":"cards.md + run-42 engine + run-43 variance"},
  {"kind":"card","name":"被遗忘的仪式","aliases":["Forgotten Ritual","FORGOTTEN_RITUAL","被遗忘的仪式"],
   "card_type":"skill","character_pool":"IRONCLAD","cost":"1","rarity":"uncommon",
   "description":("消耗；若本回合已有其他牌被排出，获得 3 能量（升级4）。自身的排出不算（EvilEye 类）。"
     "协同脊：坚毅/AshenStrike/Tremble/狂宴先排出，仪式 +3 费返还。"
     "对局43 方差税：坚毅的随机排出于仪式首秀回合就吃掉了仪式本身——随机排出是引擎件的威胁，不只是瘦身工具。"),
   "play_notes":"对局43 live","source":"cards.md + 对局42引擎 + 对局43方差"})

upsert(en, zh, "EVIL_EYE",
  {"kind":"card","name":"Evil Eye","aliases":["Evil Eye","EVIL_EYE","邪眼"],"card_type":"skill","character_pool":"IRONCLAD",
   "cost":"1","rarity":"uncommon",
   "description":("Exhaust, gain 8 Block; if another card was Exhausted this turn, gain the Block twice (16). "
     "Own exhaust does NOT count for the double trigger; build anomaly: own disposal lands in discard (exhaust pile "
     "unchanged) but the double-block condition still fires off PRIOR exhausts. Shop (5,0) Act2 live price 79g run-43 "
     "(not bought - Barricade taken instead at 150g)."),
   "play_notes":SRC,"source":"cards.md + run-43 shop live"},
  {"kind":"card","name":"邪眼","aliases":["Evil Eye","EVIL_EYE","邪眼"],"card_type":"skill","character_pool":"IRONCLAD",
   "cost":"1","rarity":"uncommon",
   "description":("消耗，获得8格挡；若本回合已有其他牌被排出，格挡翻倍（16）。自身排出不触发翻倍；"
     "构筑异常：自身处置落入弃牌堆（排出堆不变），但翻倍条件仍由先前的排出触发。"
     "对局43 Act2 商店 (5,0) live 价格 79金（未买——150金买了 Barricade）。"),
   "play_notes":"对局43 live","source":"cards.md + 对局43 商店 live"})

upsert(en, zh, "STOMP",
  {"kind":"card","name":"Stomp","aliases":["Stomp","STOMP","践踏"],"card_type":"Attack","character_pool":"ironclad",
   "cost":"3","rarity":"Uncommon","target_type":"AllEnemies",
   "description":("Deal 12 damage to ALL enemies. Costs 1 less for each Attack played this turn - in an attack-dense "
     "hand (Bloodletting-funded) it approaches 0-1 cost for 12 AoE. Codex fold run-43; not yet live-verified in hand."),
   "play_notes":"codex fold run-43, pending live","source":"codex-api:/cards/STOMP"},
  {"kind":"card","name":"践踏","aliases":["Stomp","STOMP","践踏"],"card_type":"Attack","character_pool":"ironclad",
   "cost":"3","rarity":"Uncommon","target_type":"AllEnemies",
   "description":("对所有敌人造成12伤。本回合每打出一张攻击牌费用 −1——在攻击密集手牌（放血供能）中可降至 0-1 费打 12 AoE。"
     "对局43 codex 折叠；尚未在手牌中 live 验证。"),
   "play_notes":"对局43 codex 折叠，待 live","source":"codex-api:/cards/STOMP"})

upsert(en, zh, "SOLDIER_STEW",
  {"kind":"potion","name":"Soldier's Stew","aliases":["Soldier's Stew","SOLDIER_STEW","SOLDIERS_STEW","士兵炖汤"],
   "rarity":"Rare","usage":"combat",
   "description":("All cards containing 'Strike' in the name gain 1 Replay this combat (each Strike-tagged card "
     "resolves twice when played). Live run-43: TwinStrike 5+5+5+5=20 per play, Strike 6+6=12, under Weak each "
     "replayed hit still landed. Fight-defining on Ravenous packs (one kill -> double stun window) and boss races. "
     "Not a Strike-tag relic substitute - replay is combat-scoped potion effect."),
   "play_notes":SRC,"source":"codex-api + run-43 live replay confirmed"},
  {"kind":"potion","name":"士兵炖汤","aliases":["Soldier's Stew","SOLDIER_STEW","SOLDIERS_STEW","士兵炖汤"],
   "rarity":"Rare","usage":"combat",
   "description":("本场战斗所有名称含「Strike」的牌获得 1 次 Replay（每张 Strike 类牌打出时结算两次）。"
     "对局43 live：TwinStrike 每次 5+5+5+5=20，Strike 6+6=12，Weak 下每次 replay 命中仍落地。"
     "在 Ravenous 战（一杀→双眩晕窗）与 Boss 竞速中是战斗定义级药水。"
     "注意：replay 是药水战斗范围效果，不能替代 Strike 标签遗物。"),
   "play_notes":"对局43 live replay 实证","source":"codex-api + 对局43 live"})
# remove lookup-duplicate key if present
if "SOLDIER_S_STEW" in en:
    en.pop("SOLDIER_S_STEW"); zh.pop("SOLDIER_S_STEW", None)
save("cards", en, zh)

# ---------------- relics ----------------
en, zh = load("relics")
upsert(en, zh, "STONE_CALENDAR",
  {"kind":"relic","name":"Stone Calendar","aliases":["Stone Calendar","STONE_CALENDAR","石日历"],"rarity":"Rare",
   "description":("at end of turn 7, deal 52 damage to ALL enemies (counter ticks per combat, resets next fight). "
     "Live run-43 x2: LouseProgenitor killed from 36 HP at end of our T7 (calendar fired before enemy T7 acted); "
     "also observed NOT firing on T6 - the trigger is end of turn 7 specifically. Intangible 1-2 caps this 52 to 1 "
     "per instance - do not count on it during FADE windows."),
   "play_notes":SRC,"source":"relics.md + run-43 live kill"},
  {"kind":"relic","name":"石日历","aliases":["Stone Calendar","STONE_CALENDAR","石日历"],"rarity":"Rare",
   "description":("第 7 回合结束时，对所有敌人造成 52 伤（计数按战斗，下一场重置）。"
     "对局43 live 两次观测：虱虫之祖在第7回合末从 36HP 被击杀（日历在敌方 T7 行动前触发）；"
     "第 6 回合末确认不触发——触发点专指第 7 回合结束。虚无 1-2 层会把这 52 压成每实例 1——FADE 窗内不要指望它。"),
   "play_notes":"对局43 live 击杀实证","source":"relics.md + 对局43 live"})

upsert(en, zh, "YUMMY_COOKIE",
  {"kind":"relic","name":"Yummy Cookie","aliases":["Yummy Cookie","YUMMY_COOKIE","美味饼干"],"rarity":"Ancient",
   "description":("on pickup, upgrade 4 chosen cards permanently (deck_select overlay: choose each then proceed once "
     "to confirm all). Live run-43 Tezcatara Act2 boon: Bloodletting+/UltimateDefend+/Tremble+/Feed+ applied in one "
     "confirm chain. Best-in-class permanent boon when the deck already has engine pieces worth upgrading."),
   "play_notes":SRC,"source":"relics.md + run-43 live"},
  {"kind":"relic","name":"美味饼干","aliases":["Yummy Cookie","YUMMY_COOKIE","美味饼干"],"rarity":"Ancient",
   "description":("拾取时，永久升级自选 4 张牌（deck_select 覆盖层：逐张 choose 后一次 proceed 确认全部）。"
     "对局43 Tezcatara Act2 赐福 live：放血+/终极防御+/Tremble+/狂宴+ 在一次确认链中全部生效。"
     "当牌库已有值得升级的引擎件时，这是顶级永久赐福。"),
   "play_notes":"对局43 live","source":"relics.md + 对局43 live"})

upsert(en, zh, "ORICHALCUM",
  {"kind":"relic","name":"Orichalcum","aliases":["Orichalcum","ORICHALCUM","橙铜"],"rarity":"Uncommon",
   "description":("end of turn, if you have no Block, gain 6 Block. Passive safety net on attack-heavy hands; "
     "with OddlySmoothStone +1 Dex the passive stays 6 (relic block is not card block). "
     "Live run-43: repeatedly covered 6 of 15-24 incoming on no-block-card turns."),
   "play_notes":SRC,"source":"relics.md + run-43 live"},
  {"kind":"relic","name":"橙铜","aliases":["Orichalcum","ORICHALCUM","橙铜"],"rarity":"Uncommon",
   "description":("回合结束时若没有格挡，获得 6 格挡。攻击密集手牌的被动安全网；"
     "配合滑石 +1 敏捷时被动仍为 6（遗物挡不是卡牌挡）。对局43：多次在无挡手牌回合覆盖 15-24 来伤中的 6 点。"),
   "play_notes":"对局43 live","source":"relics.md + 对局43 live"})

upsert(en, zh, "ODDLY_SMOOTH_STONE",
  {"kind":"relic","name":"Oddly Smooth Stone","aliases":["Oddly Smooth Stone","ODDLY_SMOOTH_STONE","滑石"],"rarity":"Common",
   "description":("start each combat with 1 Dexterity (card-block values +1 all fight). Shop (14,2) Act1 live price "
     "191g run-43 - bought as the Act1-tail gold sink with Tremble (243/244=99.6% sunk). "
     "Stacks additively with Dex potions in-combat."),
   "play_notes":SRC,"source":"relics.md + run-43 shop live"},
  {"kind":"relic","name":"滑石","aliases":["Oddly Smooth Stone","ODDLY_SMOOTH_STONE","滑石"],"rarity":"Common",
   "description":("每场战斗开始时 +1 敏捷（卡牌挡全程 +1）。对局43 Act1 尾部商店 (14,2) live 价格 191金——"
     "与 Tremble 一同作为 Act1 尾部沉淀口买入（243/244=99.6% 沉淀）。战斗中与敏捷药水加算叠加。"),
   "play_notes":"对局43 live","source":"relics.md + 对局43 商店 live"})

upsert(en, zh, "WINGED_BOOTS",
  {"kind":"relic","name":"Winged Boots","aliases":["Winged Boots","WINGED_BOOTS","羽翼之靴"],"rarity":"Uncommon",
   "description":("3 charges: when choosing the next floor's room, ignore current route connectivity (any point on "
     "the next row). Neow Act1 live run-43 pick over Pommelander(+1 card upgrade) and SilverCrucible(3 upgraded "
     "rewards / empty first chest). Doctrine: reserve for rest/shop geometry escapes and pre-boss emergency jumps; "
     "charges unused all run-43 (draft geometry held) - unused charges are not a loss if the draft was correct."),
   "play_notes":SRC,"source":"run-43 Neow live"},
  {"kind":"relic","name":"羽翼之靴","aliases":["Winged Boots","WINGED_BOOTS","羽翼之靴"],"rarity":"Uncommon",
   "description":("3 次充能：选择下一层房间时无视当前路线连通性（下一行任意点可达）。"
     "对局43 Act1 Neow live 之选（对比：橙塑香盒+1 升级 / 白银熔炉 3 次卡奖升级+首个宝箱为空）。"
     "教条：留给休息/商店几何逃生与 Boss 前紧急跳层；对局43 全程未消耗（草稿几何守住了）——"
     "草稿正确时未用掉的充能不是损失。"),
   "play_notes":"对局43 live","source":"对局43 Neow live"})

upsert(en, zh, "MEAL_TICKET",
  {"kind":"relic","name":"Meal Ticket","aliases":["Meal Ticket","MEAL_TICKET","餐券"],"rarity":"Common",
   "description":("on entering a MerchantRoom, heal 15 HP; only obtainable before the Act-3 treasure chest. "
     "Shop prices live run-43: 187g Act1 (14,2) / not offered Act2 (5,0). HP-economy relic tied to shop spines."),
   "play_notes":SRC,"source":"relics.md + run-43 shop screens"},
  {"kind":"relic","name":"餐券","aliases":["Meal Ticket","MEAL_TICKET","餐券"],"rarity":"Common",
   "description":("进入商人房时恢复 15HP；仅在 Act3 宝箱前可获得。对局43 live 价格：Act1 (14,2) 187金 / Act2 (5,0) 未刷出。"
     "与商店脊线绑定的 HP 经济遗物。"),
   "play_notes":"对局43 live","source":"relics.md + 对局43 商店"})

upsert(en, zh, "WHETSTONE",
  {"kind":"relic","name":"Whetstone","aliases":["Whetstone","WHETSTONE","磨刀石"],"rarity":"Common",
   "description":("on pickup, upgrade 2 random Attack cards in your deck. Shop (5,0) Act2 live price 151g run-43 "
     "(not bought - Barricade taken at 150g instead). Random targets - value depends on attack density."),
   "play_notes":SRC,"source":"relics.md + run-43 shop live"},
  {"kind":"relic","name":"磨刀石","aliases":["Whetstone","WHETSTONE","磨刀石"],"rarity":"Common",
   "description":("拾取时，随机升级牌库中 2 张攻击牌。对局43 Act2 商店 (5,0) live 价格 151金（未买——150金选了 Barricade）。"
     "目标随机——价值取决于攻击牌密度。"),
   "play_notes":"对局43 live","source":"relics.md + 对局43 商店"})

upsert(en, zh, "DINGY_RUG",
  {"kind":"relic","name":"Dingy Rug","aliases":["Dingy Rug","DINGY_RUG","破地毯"],"rarity":"Shop",
   "description":("card rewards can now contain Colorless cards. Shop (5,0) Act2 live price 208g run-43 (unaffordable). "
     "Dilutes class-pool rewards - low priority unless hunting specific Colorless tools."),
   "play_notes":SRC,"source":"relics.md + run-43 shop live"},
  {"kind":"relic","name":"破地毯","aliases":["Dingy Rug","DINGY_RUG","破地毯"],"rarity":"Shop",
   "description":("卡牌奖励中可出现无色牌。对局43 Act2 商店 (5,0) live 价格 208金（买不起）。"
     "稀释职业池奖励——除非定向找无色工具，优先级低。"),
   "play_notes":"对局43 live","source":"relics.md + 对局43 商店"})

upsert(en, zh, "BOOK_OF_FIVE_RINGS",
  {"kind":"relic","name":"Book of Five Rings","aliases":["Book of Five Rings","BOOK_OF_FIVE_RINGS","五轮书"],"rarity":"Common",
   "description":("every 5 cards added to your deck, heal 20 HP. Shop (5,0) Act2 live price 196g run-43 (unaffordable). "
     "Anti-thinning relic - pays out only in card-add-heavy routes."),
   "play_notes":SRC,"source":"relics.md + run-43 shop live"},
  {"kind":"relic","name":"五轮书","aliases":["Book of Five Rings","BOOK_OF_FIVE_RINGS","五轮书"],"rarity":"Common",
   "description":("牌库每增加 5 张牌，恢复 20HP。对局43 Act2 商店 (5,0) live 价格 196金（买不起）。"
     "反精简遗物——只在加牌密集的路线上回本。"),
   "play_notes":"对局43 live","source":"relics.md + 对局43 商店"})

upsert(en, zh, "RINGING_TRIANGLE",
  {"kind":"relic","name":"Ringing Triangle","aliases":["Ringing Triangle","RINGING_TRIANGLE","铃三角"],"rarity":"Shop",
   "description":("you retain your hand on the first turn of combat. Shop (14,2) Act1 live price 202g run-43 "
     "(not bought - OddlySmoothStone+Tremble 243g sunk instead; per-turn Dex valued over T1-only consistency). "
     "Do NOT confuse with the RINGING counter-class power from run-13 (1 card/turn) - different thing."),
   "play_notes":SRC,"source":"relics.md + run-43 shop live"},
  {"kind":"relic","name":"铃三角","aliases":["Ringing Triangle","RINGING_TRIANGLE","铃三角"],"rarity":"Shop",
   "description":("战斗第 1 回合保留手牌。对局43 Act1 商店 (14,2) live 价格 202金"
     "（未买——243金沉淀了滑石+Tremble；每回合敏捷 > 仅 T1 的一致性）。"
     "切勿与对局13 的 RINGING counter-class power（每回合限1牌）混淆——完全不同的东西。"),
   "play_notes":"对局43 live","source":"relics.md + 对局43 商店"})
save("relics", en, zh)

# ---------------- potions ----------------
en, zh = load("potions")
upsert(en, zh, "DEXTERITY_POTION",
  {"kind":"potion","name":"Dexterity Potion","aliases":["Dexterity Potion","DEXTERITY_POTION","敏捷药水"],"rarity":"Common","usage":"combat",
   "description":("Gain 2 Dexterity for the combat (card-block +2, stacks with OddlySmoothStone). "
     "Live run-43: Dex1+2=3 total; Defend 6+3=9, TrueGrit 8+3=11, UltimateDefend 13+3=16 - 16>=15 solo-stunned "
     "BowlbugRock HEADBUTT. Bowlbug doctrine note run-39: Dex+Defend x2=14 was one short of 15 - always compute the "
     "live total vs the intent number before concluding stun is impossible."),
   "play_notes":SRC,"source":"potions.md + run-39/43 live"},
  {"kind":"potion","name":"敏捷药水","aliases":["Dexterity Potion","DEXTERITY_POTION","敏捷药水"],"rarity":"Common","usage":"combat",
   "description":("本场战斗 +2 敏捷（卡牌挡 +2，与滑石叠加）。对局43 live：滑石1+药2=3 总计；"
     "Defend 6+3=9、坚毅 8+3=11、终极防御 13+3=16——16≥15 单卡眩晕碗虫石 HEADBUTT。"
     "对局39 注记：敏捷+Defend×2=14 差 15 一点——下眩晕结论前必须用 live 总挡对意图数字精算。"),
   "play_notes":"对局43 live","source":"potions.md + 对局39/43 live"})

upsert(en, zh, "BLESSING_OF_THE_FORGE",
  {"kind":"potion","name":"Blessing of the Forge","aliases":["Blessing of the Forge","BLESSING_OF_THE_FORGE","锻造祝福"],
   "rarity":"Uncommon","usage":"combat",
   "description":("Upgrade every upgradable card in your hand for THIS combat (Armaments-class, reverts after). "
     "Spend on highest hand-density / lethal-intent turns. Live run-43 Act2 (4,0): 5-card attack hand upgraded "
     "IronWave+2/+2, TwinStrike+2, Pommel+1/draw2, Strike+3 - used on a 19-intent POUNCE turn. "
     "Also the RANSACK event rare-potion roll run-43 (claimed properly - run-42 had skipped the claim screen)."),
   "play_notes":SRC,"source":"potions.md + run-38/43 live"},
  {"kind":"potion","name":"锻造祝福","aliases":["Blessing of the Forge","BLESSING_OF_THE_FORGE","锻造祝福"],
   "rarity":"Uncommon","usage":"combat",
   "description":("本场战斗升级手牌中所有可升级牌（武装级，战后还原）。在手牌密度最高/致命意图回合使用。"
     "对局43 Act2 (4,0) live：5 张攻击手牌升级——铁斩波+2/+2、双打击+2、剑柄+1/抽2、打击+3，用在 19 伤 POUNCE 回合。"
     "对局43 RANSACK 事件稀有药水即为此（正确领取——对局42 曾跳过领取屏）。"),
   "play_notes":"对局43 live","source":"potions.md + 对局38/43 live"})

upsert(en, zh, "FOUL_POTION",
  {"kind":"potion","name":"Foul Potion","aliases":["Foul Potion","FOUL_POTION","污浊药水"],"rarity":"Event","usage":"Event",
   "description":("In combat: deal 12 damage to EVERY non-pet creature INCLUDING you (AoE 12 + self 12; suicide-class "
     "below ~15 HP; self-damage triggers Rupture). In a Merchant room: gain 100 Gold. In FakeMerchant event it starts "
     "the fight - never use there. POTION_COURIER event offers x3 (run-42 declined at 13 HP; run-43 at 44 HP still "
     "declined - bridge rejects use_potion outside combat, so the merchant-gold line is not agent-reachable yet)."),
   "play_notes":SRC,"source":"potions.md + run-42/43 live"},
  {"kind":"potion","name":"污浊药水","aliases":["Foul Potion","FOUL_POTION","污浊药水"],"rarity":"Event","usage":"Event",
   "description":("战斗中：对所有非宠物生物（含自己）造成 12 伤（AoE12+自伤12；HP<15 时是自杀级；自伤触发 Rupture）。"
     "在商人房：获得 100金。FakeMerchant 事件中使用会触发战斗——绝不能在那用。"
     "POTION_COURIER 事件提供 ×3（对局42 13HP 拒绝；对局43 44HP 仍拒绝——桥拒绝战斗外 use_potion，"
     "商人房换金线目前 agent 不可达）。"),
   "play_notes":"对局43 live","source":"potions.md + 对局42/43 live"})

upsert(en, zh, "SWIFT_POTION",
  {"kind":"potion","name":"Swift Potion","aliases":["Swift Potion","SWIFT_POTION","迅捷药水"],"rarity":"Common","usage":"combat",
   "description":("Draw 3 cards. Boss-reward roll run-43; spent T1 of the Act2 (1,1) Bowlbug fight digging for block "
     "to reach IMBALANCED stun threshold - drew attacks instead (Pommel/TwinStrike/Strike), stun line missed that turn."),
   "play_notes":SRC,"source":"potions.md + run-43 live"},
  {"kind":"potion","name":"迅捷药水","aliases":["Swift Potion","SWIFT_POTION","迅捷药水"],"rarity":"Common","usage":"combat",
   "description":("抽 3 张牌。对局43 Boss 奖励获得；在 Act2 (1,1) 碗虫战 T1 使用，想挖挡牌凑 IMBALANCED 眩晕阈值——"
     "抽上来的是攻击牌（剑柄/双打击/打击），当回合眩晕线落空。"),
   "play_notes":"对局43 live","source":"potions.md + 对局43 live"})

upsert(en, zh, "WEAK_POTION",
  {"kind":"potion","name":"Weak Potion","aliases":["Weak Potion","WEAK_POTION","弱化药水"],"rarity":"Common","usage":"combat",
   "description":("Apply 3 Weak to the target (attacks -25% for 3 turns). Live run-43 Act1 Boss SoulFysh T7: DE_GAS "
     "intent 24->18 on a player-Vuln turn - the 6-point cut plus 6 block turned a 24-leak into 12. "
     "Boss-gate reserve doctrine: spend on the highest live intent, keep a heal-class potion behind it."),
   "play_notes":SRC,"source":"potions.md + run-43 live"},
  {"kind":"potion","name":"弱化药水","aliases":["Weak Potion","WEAK_POTION","弱化药水"],"rarity":"Common","usage":"combat",
   "description":("对目标施加 3 层虚弱（攻击 −25%，持续3回合）。对局43 Act1 Boss 灵魂异鱼 T7 live："
     "玩家带易伤时 DE_GAS 意图 24→18，6 点削减 + 6 挡把 24 漏伤压到 12。"
     "Boss 闸门储备教条：花在 live 意图最高的一回合，身后保留一瓶治疗类药水。"),
   "play_notes":"对局43 live","source":"potions.md + 对局43 live"})

upsert(en, zh, "SPEED_POTION",
  {"kind":"potion","name":"Speed Potion","aliases":["Speed Potion","SPEED_POTION","速度药水"],"rarity":"Common","usage":"combat",
   "description":("apply +5 Dexterity for the current turn only; lose it end of turn. One-turn burst block - "
     "spend on the turn the lethal intent lands, not earlier. Live run-43 Act1 Boss T10: Dex 1->6 under Speed, "
     "but hand had no block cards so the burst went unused that turn (planned for SCREAM 13; Beckon tax hit instead). "
     "Lesson: Speed Potion pays only when block CARDS are in hand to amplify."),
   "play_notes":SRC,"source":"potions.md + run-41/43 live"},
  {"kind":"potion","name":"速度药水","aliases":["Speed Potion","SPEED_POTION","速度药水"],"rarity":"Common","usage":"combat",
   "description":("当回合 +5 敏捷，回合末失去。单回合爆发挡——花在致命意图落地的那回合，不要提前。"
     "对局43 Act1 Boss T10 live：敏捷 1→6，但手牌没有挡牌，爆发当回合未兑现"
     "（原计划挡 SCREAM 13，结果 Beckon 税先到）。教训：速度药只有在手上有挡牌可放大时才有价值。"),
   "play_notes":"对局43 live","source":"potions.md + 对局41/43 live"})

upsert(en, zh, "SHACKLING_POTION",
  {"kind":"potion","name":"Shackling Potion","aliases":["Shackling Potion","SHACKLING_POTION","枷锁药水"],"rarity":"Rare","usage":"combat",
   "description":("apply ShacklingPotionPower 7 to ALL enemies - temporary -7 Strength, lost at end of their turn. "
     "Seen in both run-43 shops (99g Act1-tail / 95g Act2 (5,0)); potion slots were full or gold spent on relics - "
     "not bought. Boss-gate class: cuts every multi-hit intent by 7 per hit."),
   "play_notes":SRC,"source":"potions.md + run-43 shop screens"},
  {"kind":"potion","name":"枷锁药水","aliases":["Shackling Potion","SHACKLING_POTION","枷锁药水"],"rarity":"Rare","usage":"combat",
   "description":("对所有敌人施加 ShacklingPotionPower 7——临时 −7 力量，其回合末消失。"
     "对局43 两家商店都出现（Act1 尾部 99金 / Act2 (5,0) 95金）；药槽满或金币已投遗物——未买。"
     "Boss 闸门级：每段多段意图按击 −7。"),
   "play_notes":"对局43 live","source":"potions.md + 对局43 商店"})

upsert(en, zh, "DISTILLED_CHAOS",
  {"kind":"potion","name":"Distilled Chaos","aliases":["Distilled Chaos","DISTILLED_CHAOS","蒸馏混沌"],"rarity":"Rare","usage":"combat",
   "description":("Play the top 3 cards of your Draw Pile. Variance-class - cost/targets uncontrolled. "
     "Shop (5,0) Act2 live price 102g run-43 (not bought)."),
   "play_notes":SRC,"source":"potions.md + run-43 shop live"},
  {"kind":"potion","name":"蒸馏混沌","aliases":["Distilled Chaos","DISTILLED_CHAOS","蒸馏混沌"],"rarity":"Rare","usage":"combat",
   "description":("打出抽牌堆顶 3 张牌。方差类——费用/目标不可控。对局43 Act2 商店 (5,0) live 价格 102金（未买）。"),
   "play_notes":"对局43 live","source":"potions.md + 对局43 商店"})
save("potions", en, zh)

# ---------------- events ----------------
en, zh = load("events")
upsert(en, zh, "TRASH_HEAP",
  {"kind":"event","name":"Trash Heap","aliases":["Trash Heap","TRASH_HEAP","垃圾堆"],
   "description":("DiveIn = lose 8 HP, gain a forgotten (removed-content) relic - reported pool DarkstonePeriapt / "
     "DreamCatcher / HandDrill / MawBank / TheBoot (mediocre). Grab = +100 Gold + a forgotten card - reported pool "
     "Caltrops / Distraction / Outmaneuver / Clash / DualWield / Entrench / HelloWorld / Rebound / Stack / RipAndTear. "
     "Run-43 at 44 HP before an elite corridor took GRAB (HP-economy doctrine: do not pay 8 HP for a mediocre relic "
     "pool; 100g sank at the tail shop fork). Caltrops (3 Thorns power, 1c) came from this pool and carried two fights."),
   "play_notes":SRC,"source":"perplexity pools 2026-09 + run-43 live",
   "options":{
     "TRASH_HEAP.pages.INITIAL.options.DIVE_IN":{"kind":"event_option","name":"Dive In","aliases":["DIVE_IN"],"page":"INITIAL",
       "description":"Lose 8 HP; gain 1 forgotten relic (mediocre pool).","zh_description":"失去8HP；获得1件旧日遗物（池平庸）。","zh_name":"扎进垃圾堆","curated":True},
     "TRASH_HEAP.pages.INITIAL.options.GRAB":{"kind":"event_option","name":"Grab","aliases":["GRAB"],"page":"INITIAL",
       "description":"+100 Gold; add 1 forgotten card (Caltrops-class live run-43).","zh_description":"+100金；加入1张旧日卡牌（对局43 live 得铁蒺藜）。","zh_name":"随便拿点垃圾","curated":True}}},
  {"kind":"event","name":"垃圾堆","aliases":["Trash Heap","TRASH_HEAP","垃圾堆"],
   "description":("DiveIn = 失去 8HP，获得一件被遗忘（已移除内容）遗物——报告池 DarkstonePeriapt / DreamCatcher / "
     "HandDrill / MawBank / TheBoot（平庸）。Grab = +100金 + 一张被遗忘卡牌——报告池 铁蒺藜/分心/失衡/冲突/双持/"
     "战壕/你好世界/弹回/叠放/撕咬。对局43 在 44HP 精英走廊前选 GRAB（HP 经济教条：不为平庸遗物池付 8HP；"
     "100金在尾部商店岔路沉淀）。Caltrops（1费3荆棘 power）即出自此池，carry 了两场战斗。"),
   "play_notes":"对局43 live","source":"perplexity 池 2026-09 + 对局43 live",
   "options":{
     "TRASH_HEAP.pages.INITIAL.options.DIVE_IN":{"kind":"event_option","name":"Dive In","aliases":["DIVE_IN"],"page":"INITIAL",
       "description":"Lose 8 HP; gain 1 forgotten relic (mediocre pool).","zh_description":"失去8HP；获得1件旧日遗物（池平庸）。","zh_name":"扎进垃圾堆","curated":True},
     "TRASH_HEAP.pages.INITIAL.options.GRAB":{"kind":"event_option","name":"Grab","aliases":["GRAB"],"page":"INITIAL",
       "description":"+100 Gold; add 1 forgotten card (Caltrops-class live run-43).","zh_description":"+100金；加入1张旧日卡牌（对局43 live 得铁蒺藜）。","zh_name":"随便拿点垃圾","curated":True}}})

upsert(en, zh, "TEZCATARA",
  {"kind":"event","name":"Tezcatara","aliases":["Tezcatara","TEZCATARA","特兹卡塔拉"],
   "description":("Act2+ act-start boon room (act-heal fires at boon entry, not map transition - reconfirmed run-43 "
     "27->80). Options rotate per run. Live run-43 seed AYPP0CQ14G: YUMMY_COOKIE (upgrade 4 cards) / STORYBOOK "
     "(add Brightest Flame) / TOY_BOX (4 wax relics, leftmost melts every 3 combats). Run-40 seed had VERY_HOT_COCOA "
     "(+4e T1) / BIIIG_HUG (remove 4 + Soot on shuffle) / SEAL_OF_GOLD (5g -> 1e per turn). "
     "Run-43 pick: Yummy Cookie - permanent upgrades beat decaying wax and unknown-card pollution."),
   "play_notes":SRC,"source":"run-40/43 live",
   "options":{
     "TEZCATARA.pages.INITIAL.options.YUMMY_COOKIE":{"kind":"event_option","name":"Yummy Cookie","page":"INITIAL",
       "description":"Upgrade 4 chosen cards permanently.","zh_description":"永久升级自选4张牌。","zh_name":"美味饼干","curated":True},
     "TEZCATARA.pages.INITIAL.options.STORYBOOK":{"kind":"event_option","name":"Storybook","page":"INITIAL",
       "description":"Add 1 Brightest Flame to your deck.","zh_description":"将1张至亮之焰加入牌库。","zh_name":"故事书","curated":True},
     "TEZCATARA.pages.INITIAL.options.TOY_BOX":{"kind":"event_option","name":"Toy Box","page":"INITIAL",
       "description":"Gain 4 Wax relics; leftmost melts every 3 combats.","zh_description":"获得4件蜡制遗物；每3场战斗最左侧融化。","zh_name":"玩具盒","curated":True}}},
  {"kind":"event","name":"特兹卡塔拉","aliases":["Tezcatara","TEZCATARA","特兹卡塔拉"],
   "description":("Act2+ 章首赐福房（act-heal 在赐福房入口结算，不是地图切换时——对局43 27→80 再确认）。"
     "选项按局轮换。对局43 种子 AYPP0CQ14G：美味饼干（升级4张）/ 故事书（加至亮之焰）/ 玩具盒（4件蜡制遗物，每3战最左融化）。"
     "对局40 种子：VERY_HOT_COCOA（T1 +4费）/ BIIIG_HUG（移除4张+洗牌加烟尘）/ SEAL_OF_GOLD（5金→1费/回合）。"
     "对局43 选：美味饼干——永久升级优于衰减蜡件与未知卡污染。"),
   "play_notes":"对局43 live","source":"对局40/43 live",
   "options":{
     "TEZCATARA.pages.INITIAL.options.YUMMY_COOKIE":{"kind":"event_option","name":"Yummy Cookie","page":"INITIAL",
       "description":"Upgrade 4 chosen cards permanently.","zh_description":"永久升级自选4张牌。","zh_name":"美味饼干","curated":True},
     "TEZCATARA.pages.INITIAL.options.STORYBOOK":{"kind":"event_option","name":"Storybook","page":"INITIAL",
       "description":"Add 1 Brightest Flame to your deck.","zh_description":"将1张至亮之焰加入牌库。","zh_name":"故事书","curated":True},
     "TEZCATARA.pages.INITIAL.options.TOY_BOX":{"kind":"event_option","name":"Toy Box","page":"INITIAL",
       "description":"Gain 4 Wax relics; leftmost melts every 3 combats.","zh_description":"获得4件蜡制遗物；每3战最左侧融化。","zh_name":"玩具盒","curated":True}}})

upsert(en, zh, "POTION_COURIER",
  {"kind":"event","name":"Potion Courier","aliases":["Potion Courier","POTION_COURIER","药水信使"],
   "description":("GrabPotions = 3x FOUL_POTION (combat AoE12+self12; merchant-room use = +100g each - blocked for "
     "agents: bridge rejects use_potion outside combat). Ransack = 1 random rare potion via a rewards screen - "
     "CLAIM IT (choose the reward node) before proceeding; run-42 skipped the claim and lost the rare potion, "
     "run-43 claimed BLESSING_OF_THE_FORGE properly."),
   "play_notes":SRC,"source":"run-42/43 live",
   "options":{
     "POTION_COURIER.pages.INITIAL.options.GRAB_POTIONS":{"kind":"event_option","name":"Grab Potions","page":"INITIAL",
       "description":"Gain 3x Foul Potion.","zh_description":"获得3瓶污浊药水。","zh_name":"拿走这批药水","curated":True},
     "POTION_COURIER.pages.INITIAL.options.RANSACK":{"kind":"event_option","name":"Ransack","page":"INITIAL",
       "description":"Gain 1 random rare potion (claim on the rewards screen!).","zh_description":"获得1瓶随机罕见药水（务必在奖励屏领取！）。","zh_name":"洗劫","curated":True}}},
  {"kind":"event","name":"药水信使","aliases":["Potion Courier","POTION_COURIER","药水信使"],
   "description":("GrabPotions = 3×污浊药水（战斗 AoE12+自伤12；商人房使用每瓶 +100金——对 agent 被挡：桥拒绝战斗外 use_potion）。"
     "Ransack = 1 瓶随机罕见药水，经奖励屏发放——先 choose 领取再 proceed；对局42 跳过领取损失稀有药水，"
     "对局43 正确领到锻造祝福。"),
   "play_notes":"对局42/43 live","source":"对局42/43 live",
   "options":{
     "POTION_COURIER.pages.INITIAL.options.GRAB_POTIONS":{"kind":"event_option","name":"Grab Potions","page":"INITIAL",
       "description":"Gain 3x Foul Potion.","zh_description":"获得3瓶污浊药水。","zh_name":"拿走这批药水","curated":True},
     "POTION_COURIER.pages.INITIAL.options.RANSACK":{"kind":"event_option","name":"Ransack","page":"INITIAL",
       "description":"Gain 1 random rare potion (claim on the rewards screen!).","zh_description":"获得1瓶随机罕见药水（务必在奖励屏领取！）。","zh_name":"洗劫","curated":True}}})
save("events", en, zh)

print("folds applied: monsters, powers, cards, relics, potions, events")
