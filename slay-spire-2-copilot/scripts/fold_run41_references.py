#!/usr/bin/env python3
"""Run-41 reference folds: fill failing move descriptions EN/ZH, fix RAGE
misfold, fold run-41 live corrections, curated:true where live-verified."""
import json
from pathlib import Path

GAME = Path(__file__).resolve().parents[1] / "references" / "game"


def load(name):
    with open(GAME / name, encoding="utf-8") as f:
        return json.load(f)


def save(name, data):
    with open(GAME / name, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, sort_keys=True)
        f.write("\n")


# ---------------------------------------------------------------- moves EN/ZH
# (monster, move) -> (en_description, zh_description, play_notes_en, play_notes_zh)
MOVES = {
    ("INFESTED_PRISM", "JAB_MOVE"): (
        "Jab: single Attack; damage 15 (A:17). Run-41 live at A1: 15 on T1 at 34 HP entry.",
        "突刺：单体攻击；伤害 15（A:17）。run-41 A1 live：34 HP 入场 T1 实测 15。",
        "run-41: opening attack of the cycle; pairs with VITAL_SPARK tainted-skill tax on player block cards.",
        "run-41：周期首攻；与 VITAL_SPARK 对玩家技能牌的污染税叠加计算。",
    ),
    ("INFESTED_PRISM", "RADIATE_MOVE"): (
        "Radiate: Attack + Defend; damage 11 (A:13) and self-block 11. Run-41 live: intent displayed atk:13[base11] once TAINTED tax stacked on the player side; block component resolved on the prism itself.",
        "辐射：攻击+防御；伤害 11（A:13）并自身获得 11 格挡。run-41 live：玩家侧 TAINTED 税叠加后 intent 显示为 atk:13[base11]；挡由棱柱自身结算。",
        "run-41: damage-then-self-block order confirmed in history; the 11 self-block paces race damage.",
        "run-41：history 确认先伤后自身挡；自身 11 挡参与竞速配速。",
    ),
    ("INFESTED_PRISM", "WHIRLWIND_MOVE"): (
        "Whirlwind: multi Attack; damage 5x3 (A:6/hit). Run-41 live: with player TAINTED 4 the displayed intent inflated to 9x3=27 — per-hit tax stacking, the lethal line of that death.",
        "旋风：多段攻击；伤害 5×3（A:6/段）。run-41 live：玩家 TAINTED 4 时显示为 9×3=27 — 按段加税，是该局死亡的致命线。",
        "run-41 death cause: base 5x3 became 9x3 through tainted-skill tax stacking 2→4; block math must use the taxed number.",
        "run-41 死因：污染技能税 2→4 把 base 5×3 通胀为 9×3；挡值计算必须用含税数字。",
    ),
    ("INFESTED_PRISM", "PULSATE_MOVE"): (
        "Pulsate: Attack + Buff + Defend; damage 8 (A:10), self-block 20, and raises the prism's VITAL_SPARK by 2 (run-36/41 cycle data). Free-ish window only if the spark raise can be raced; otherwise skills tax harder after it.",
        "脉动：攻击+Buff+防御；伤害 8（A:10）、自身 20 挡，并使棱柱 VITAL_SPARK +2（run-36/41 周期数据）。仅当能竞速压制 spark 上涨时才算自由窗；否则此后技能税更重。",
        "run-41: cycle position after Whirlwind; the +2 spark raise is the fight's escalation timer — burst before the second Pulsate.",
        "run-41：位于旋风之后；+2 spark 是本战升级计时器 — 第二次脉动前须爆发。",
    ),
    ("SKULKING_COLONY", "ZOOM_MOVE"): (
        "Zoom: single Attack; damage 14-class (live intent atk:14 at A1, run-41).",
        "急速：单体攻击；伤害 14 级（run-41 A1 live intent atk:14）。",
        "run-41: first move of the fight on the (7,6) elite; Hardened Shell caps the player's return damage at 20/turn.",
        "run-41：(7,6) 精英首招；硬化甲壳把玩家回合伤害封顶 20。",
    ),
    ("SKULKING_COLONY", "ZOOM_MOVE_2_MOVE"): (
        "Zoom (second slot): same 14-class single Attack as ZOOM_MOVE; different cycle slot, cannot-repeat prevents two consecutive Zooms.",
        "急速（第二槽）：与 ZOOM_MOVE 同级 14 单体攻击；周期不同槽，cannot-repeat 防止连续两次急速。",
        "run-41: cycle ZOOM→ZOOM_2→INERTIA→PIERCING_STABS; both Zooms ran back-to-back turns 1-2 on that kill.",
        "run-41：周期 ZOOM→ZOOM_2→INERTIA→PIERCING_STABS；该次击杀中两次急速占据第 1-2 回合。",
    ),
    ("SKULKING_COLONY", "INERTIA_MOVE"): (
        "Inertia: Attack + Buff; damage 9 (A:11) and self-STRENGTH +2. Race timer — Str stacks make every later hit deadlier; free window only in the sense that block-carry value is nil between turns.",
        "惯性：攻击+Buff；伤害 9（A:11）并自身力量 +2。竞速计时器 — 力量叠加让后续每次命中更致命；所谓自由窗仅指挡不跨回合。",
        "run-41 doctrine: dump damage on this turn, then full-block the following Piercing Stabs turn.",
        "run-41 教条：本回合倾泻伤害，随后全力格挡穿刺回合。",
    ),
    ("SKULKING_COLONY", "PIERCING_STABS_MOVE"): (
        "Piercing Stabs: multi Attack; live A1 intent 9x2[base7] (run-41) — Str stacks scale per hit. Doctrine: the full-block turn of the fight; Shrug+Defend covered 13/18 in run-41.",
        "穿刺：多段攻击；run-41 A1 live intent 9×2[base7] — 每段受力量加成。教条：本战的全力格挡回合；run-41 耸肩+防御挡下 13/18。",
        "run-41: 18 incoming at fight HP peak; potions reserved because 44-HP entry could absorb the leak.",
        "run-41：峰值回合来伤 18；因 44 HP 入场可吸收漏伤而保留药水。",
    ),
    ("TERROR_EEL", "CRASH_MOVE"): (
        "Crash: single Attack; damage 16 (A:18). Cycle opener — run-41 took it unblocked on T1 while setting the SHRIEK bracket play.",
        "坠击：单体攻击；伤害 16（A:18）。周期首招 — run-41 T1 故意不挡，为 SHRIEK 括号线做铺垫。",
        "run-41: T1 deliberate take while dumping PS+Strike through Marbles vuln.",
        "run-41：T1 故意承伤，同时在弹珠易伤下倾泻 PS+打击。",
    ),
    ("TERROR_EEL", "THRASH_MOVE"): (
        "Thrash: multi Attack; 4x2-class (A:5/hit) — run-41 live intent showed multi:3x3 when a Vigor/Str stack had landed; live intents outrank the archive table.",
        "鞭挞：多段攻击；4×2 级（A:5/段）— run-41 在 Vigor/力量叠加后 live intent 显示为 multi:3×3；live intent 优先于档案表。",
        "run-41: free-window adjacent turn; kill priority stayed on crossing the SHRIEK bracket, not on blocking this.",
        "run-41：紧邻自由窗的回合；击杀优先级仍在跨 SHRIEK 括号，而非格挡本招。",
    ),
    ("TERROR_EEL", "STUN_MOVE"): (
        "Stunned: the eel skips its action this turn. Fired run-41 when an unblocked hit crossed the SHRIEK HP bracket (~70) — Plating stripped, power consumed.",
        "眩晕：鳗鱼本回合跳过行动。run-41 触发条件：未格挡伤害跨过 SHRIEK HP 括号（约 70）— 镀甲剥离、power 消耗。",
        "run-41 live: strike dealt 10 landing exactly at 70 → STUNNED same read; Bash 13 + Heart of Iron Plating filled the window.",
        "run-41 live：打击 10 精确落在 70 → 同一次读取即 STUNNED；重锤 13 + Heart of Iron 镀甲填满窗口。",
    ),
    ("TERROR_EEL", "TERROR_MOVE"): (
        "Terrorize: Debuff-class; applies Vulnerable 99 to the player (run-41 live: player powers showed the long vuln) — no attack damage that turn, so it is a free damage window for the player.",
        " terrorize：减益类；对玩家施加 99 层易伤（run-41 live：玩家 powers 显示长易伤）— 该回合无攻击伤害，对玩家是自由伤害窗。",
        "run-41: Unrelenting 22 + Inferno tick 6 + FREE_ATTACK_POWER PS closed the kill on this window; the 99 vuln never got a following attack turn.",
        "run-41：无情猛攻 22 + Inferno tick 6 + FREE_ATTACK_POWER 的 PS 在此窗完成击杀；99 易伤没有等到后续攻击回合。",
    ),
    ("TWO_TAILED_RAT", "SCRATCH_MOVE"): (
        "Scratch: single Attack; damage 8 (A:9).",
        "抓挠：单体攻击；伤害 8（A:9）。",
        "run-41: cycle SCRATCH→DISEASE_BITE→SCREECH→CALL_FOR_BACKUP at varying phases per rat.",
        "run-41：各鼠相位错开的 SCRATCH→DISEASE_BITE→SCREECH→CALL_FOR_BACKUP 周期。",
    ),
    ("TWO_TAILED_RAT", "DISEASE_BITE_MOVE"): (
        "Disease Bite: single Attack; damage 6 (A:7). No-repeat branch table governs which move follows.",
        "疾病之咬：单体攻击；伤害 6（A:7）。分支表的 no-repeat 规则决定后续招式。",
        "run-41: branch weights showed CALL_FOR_BACKUP w=0 on the immediate next roll for all three rats — no summon threat on T1.",
        "run-41：分支权重显示三只鼠下一次 roll 的 CALL_FOR_BACKUP w=0 — T1 无召唤威胁。",
    ),
    ("TWO_TAILED_RAT", "SCREECH_MOVE"): (
        "Screech: Status-class debuff; applies Frail 1-2 to the player (run-41 live: FRAIL_POWER:1 after the hit). Block does not prevent the debuff application.",
        "尖叫：状态类减益；对玩家施加 1-2 层虚弱（run-41 live：命中后 FRAIL_POWER:1）。格挡不能阻止减益施加。",
        "run-41: Frail tax cut Defend 5→3 live the following block turn.",
        "run-41：次回合格挡时虚弱税把防御 5→3 live 削减。",
    ),
    ("TWO_TAILED_RAT", "CALL_FOR_BACKUP_MOVE"): (
        "Call for Backup: Summon-class; summons an additional Two-Tailed Rat. Run-41 live correction: killing the summoner does NOT despawn existing summons in this family — the kill-master-despawns rule belongs to other monster families; summoned rats must be killed normally.",
        "呼叫支援：召唤类；额外召唤一只双尾鼠。run-41 live 订正：击杀召唤者不会令该家族已有召唤消失 — kill-master-despawns 规则属于其他怪物家族；召出的鼠需正常击杀。",
        "run-41 doctrine correction: focus-kill the summoner still matters for tempo, but budget HP for the summoned add as a normal fight.",
        "run-41 教条订正：集火召唤者仍有节奏价值，但须把召唤体当作正常战斗计入 HP 预算。",
    ),
}

# monster-level curated descriptions EN/ZH + play_notes
MONSTERS = {
    "INFESTED_PRISM": {
        "en": "Infested Prism (Act2 Elite): HP 161 base (A 171+); run-41 live 161/161 at A1. Cycle JAB→RADIATE→WHIRLWIND→PULSATE. VITAL_SPARK counter-class: player Skill cards are Tainted(N) at combat start — playing a Tainted card adds +N to incoming attack damage for the turn (removed end of enemy side); Pulsate raises the prism's Spark +2 (escalation timer). Discipline: attacks and Power cards only on key turns; self-damage skills (Brand) are still skill-class and tax. Kill before the second Pulsate.",
        "zh": "感染棱柱（Act2 精英）：基础 HP 161（A 171+）；run-41 A1 live 161/161。周期 突刺→辐射→旋风→脉动。VITAL_SPARK 反制类：玩家技能牌开局被 Tainted(N) — 打出污染牌使本回合受到的攻击伤害 +N（敌方回合结束移除）；脉动令棱柱 Spark +2（升级计时器）。纪律：关键回合只打攻击与能力牌；自伤技能（Brand）仍属技能类照样计税。须在第二次脉动前击杀。",
        "notes_en": "run-41 death at 83/161: entered 34/80 (<50 gate), zero-skill line held but skill-class block spine self-taxed Whirlwind 5x3→9x3=27; 1 HP after the block wall, Inferno turn-start tick killed at next turn start. Run-36 killed it T3 with BloodWall/Hemo→Inferno same-frame; both runs agree the fight is an HP-entry race against Spark escalation.",
        "notes_zh": "run-41 死亡剩 83/161：34/80 入场（<50 闸门），零技能线执行到位但技能类挡牌脊线自我加税，旋风 5×3→9×3=27；挡墙后剩 1 HP，次回合开始的 Inferno tick 收掉。run-36 以 血墙/放血→Inferno 同帧 T3 击杀；两局一致结论：本战是与 Spark 升级赛跑的入场 HP 竞速。",
    },
    "SKULKING_COLONY": {
        "en": "Skulking Colony (Act1 Elite): HP 75 base (A 80+); run-41 live 75/75 at A1. HARDENED_SHELL counter-class: HP loss per turn capped at Amount (20 run-41), excess discarded not banked — pace damage to fill exactly 20/turn (75 HP → 4-turn minimum). Cycle ZOOM(14)→ZOOM_2(14)→INERTIA(9+self Str2)→PIERCING_STABS(9x2 live). Doctrine: dump on Inertia turn, full-block Piercing Stabs turn; PS 30 raw shelled to exactly 20 live run-41.",
        "zh": "鬼祟珊瑚群（Act1 精英）：基础 HP 75（A 80+）；run-41 A1 live 75/75。HARDENED_SHELL 反制类：每回合 HP 损失封顶 Amount（run-41 为 20），超出作废不累计 — 配速到每回合恰好 20（75 HP → 最少 4 回合）。周期 急速(14)→急速2(14)→惯性(9+自身力量2)→穿刺(live 9×2)。教条：惯性回合倾泻，穿刺回合全力格挡；run-41 live 中 PS 30 被壳精确削到 20。",
        "notes_en": "run-41 T5 kill: Tremble vuln windows fed cap-efficient hits; potions 0/3 spent — Burning Blood + in-hand block covered the leaks; rewards Pocketwatch+Kunai+Inferno defined the rest of the run.",
        "notes_zh": "run-41 T5 击杀：战栗易伤窗喂上限高效命中；药水 0/3 未动 — 燃血 + 手牌挡覆盖漏伤；奖励 怀表+苦无+狱火 定义了之后整局。",
    },
    "TERROR_EEL": {
        "en": "Terror Eel (Act2/Act1 elite-class, run-41 Act1 Elite②): HP 140 base (A 150+); run-41 live 140/140. SHRIEK counter-class Amount 70: unblocked damage while owner HP≤Amount stuns the eel (STUNNED), consumes the power, strips its Plating — the kill window. Cycle CRASH(16)→THRASH(4x2)→STUN→TERROR(player Vuln 99, no attack = free window)→loop. Doctrine (run-36 T4 kill, run-41 T4 repeat): burst above the bracket, cross 70 with an unblocked hit, dump on the stun+terror windows.",
        "zh": "骇鳗（精英类，run-41 为 Act1 精英②）：基础 HP 140（A 150+）；run-41 live 140/140。SHRIEK 反制类 Amount 70：主人 HP≤Amount 时受到未格挡伤害即被眩晕（STUNNED）、power 消耗、自身镀甲剥离 — 即击杀窗。周期 坠击(16)→鞭挞(4×2)→眩晕→terrorize（玩家 99 易伤，无攻击=自由窗）→循环。教条（run-36 T4 击杀、run-41 T4 复现）：括号上方爆发，以未格挡命中跨过 70，在眩晕+terror 窗倾泻。",
        "notes_en": "run-41: strike landed exactly at 70 → stun live; FREE_ATTACK_POWER makes ALL attacks in hand cost 0 that turn (not just the next one) — live correction folded here and in powers.",
        "notes_zh": "run-41：打击精确落在 70 → 眩晕 live；FREE_ATTACK_POWER 让该回合手牌中所有攻击 0 费（不只是下一张）— 此订正入本条与 powers。",
    },
    "TWO_TAILED_RAT": {
        "en": "Two-Tailed Rat (Act2/Act1 normal): HP 17-21 (A 18-22); run-41 Act1 fought a trio 17/21/18. Cycle per rat at different phases: SCRATCH(8)→DISEASE_BITE(6)→SCREECH(Status Frail)→CALL_FOR_BACKUP(Summon). Branch tables carry cannot-repeat weights — check the live move_graph before assuming a summon is imminent. Run-41 correction: summons in this family persist after the summoner's death.",
        "zh": "双尾鼠（普通怪）：HP 17-21（A 18-22）；run-41 Act1 三只 17/21/18。各鼠相位错开的周期：抓挠(8)→疾病之咬(6)→尖叫（状态虚弱）→呼叫支援（召唤）。分支表带 no-repeat 权重 — 判断召唤是否临近须看 live move_graph。run-41 订正：该家族召唤体在召唤者死亡后仍然存留。",
        "notes_en": "run-41 T1: PS+Strike killed the 17-HP rat on the Marbles vuln window; Shrug covered the remaining Scratch exactly; kill-master-despawns did not apply when the last rat fell.",
        "notes_zh": "run-41 T1：弹珠易伤窗 PS+打击带走 17 HP 那只；耸肩精确挡下剩余抓挠；最后一只倒下时 kill-master-despawns 并未生效。",
    },
}

# powers / potions / relics / cards curated corrections from run-41
POWER_FOLDS = {
    "HARD_TO_KILL_POWER": (
        "owner's damage received per INSTANCE is capped at Amount HP-loss (ModifyDamageCap = Amount); excess on that hit is discarded, not banked. Exoskeleton Amount=9 run-41 live: Bludgeon 32→9, PS 30→9, Breakthrough 9 AoE each hit full value — pace MULTIPLE hits ≤Amount rather than one big hit. Distinct from Waterfall Giant's HARDENED_SHELL-style per-turn caps: this is per-hit.",
        "主人每次受到的伤害按「次」封顶 Amount（ModifyDamageCap = Amount）；该次超出部分作废不累计。外骨骼虫 Amount=9 run-41 live：重锤 32→9、PS 30→9、Breakthrough 9 AoE 每段全额 — 用多次 ≤Amount 的命中配速，而非单次大伤。与瀑布巨兽类按回合封顶不同：本 power 按命中计。",
        True,
    ),
    "FREE_ATTACK_POWER": (
        "owner's Attack cards cost 0 while stacks last; run-41 live correction: ALL attack cards in hand showed cost=0 after Unrelenting fired (Strike×4 and PS all playable at 0e), with stacks consumed per attack played — not a single-next-attack buff.",
        "层数存续期间主人所有攻击牌 0 费；run-41 live 订正：无情猛攻触发后手牌中所有攻击牌显示 cost=0（4 张打击与 PS 均 0 费可打），每打出一张攻击消耗一层 — 并非只作用于下一张攻击。",
        True,
    ),
    "CRUELTY_POWER": (
        "owner's attacks deal +Amount% damage to Vulnerable targets (Amount=25 base; run-41 live CRUELTY_POWER:25). Multiplies on top of Vulnerable's ×1.5 — a 32-base Bludgeon resolved 37 on a vuln target live run-41; PS 20-class resolved 25-30 with Strike Dummy tags. Permanent for the combat once played (power card).",
        "主人的攻击对易伤目标造成 +Amount% 伤害（基础 Amount=25；run-41 live CRUELTY_POWER:25）。在易伤 ×1.5 之上再乘 — run-41 live 中 32 基伤重锤对易伤目标结算 37；带打击假人 tag 的 PS 20 级结算 25-30。打出后整场战斗有效（能力牌）。",
        True,
    ),
    "VITAL_SPARK_POWER": (
        "counter-class on the enemy: player Skill cards are afflicted Tainted(Amount) at combat start; playing a Tainted card applies TAINTED_POWER Amount to the player — incoming attack damage +Amount that turn (removed end of enemy side). Amount can rise mid-fight (Pulsate +2 on Infested Prism). Run-41 live: Brand (self-damage skill) still counted — zero-skill discipline means attacks AND powers only; Blood Wall/Second Wind/Defend/Shrug all tax.",
        "敌方反制类：开局玩家技能牌被污染为 Tainted(Amount)；打出污染牌使玩家获得 TAINTED_POWER Amount — 本回合受到的攻击伤害 +Amount（敌方回合结束移除）。Amount 可在战斗中上升（棱柱脉动 +2）。run-41 live：Brand（自伤技能）照样计税 — 零技能纪律指只打攻击与能力牌；血墙/重振精神/防御/耸肩全部加税。",
        True,
    ),
    "RAVENOUS_POWER": (
        "when another creature on owner's side dies and owner lives, owner is stunned into a devour move and gains +Amount Strength. Kill-window doctrine (CorpseSlug/SEAPUNK-class): one kill per turn converts each ally death into a free stun window on survivors — run-41 live: PS one-shot the 26-HP slug on the T1 Marbles vuln window, survivor stunned +Str4, Strike closed it in the stun turn, zero damage taken.",
        "同侧另一生物死亡且主人存活时，主人被眩晕进入吞噬招式并获得 +Amount 力量。击杀窗教条（CorpseSlug/SEAPUNK 类）：每回合一杀把队友死亡转化为幸存者的免费眩晕窗 — run-41 live：PS 在 T1 弹珠易伤窗一击带走 26 HP 蛞蝓，幸存者眩晕 +力量4，眩晕回合打击收掉，零伤害。",
        True,
    ),
    "TAINTED_POWER": (
        "player-side debuff from VITAL_SPARK: incoming attack damage +Amount for the turn; removed at end of the enemy side's turn. Run-41 live: each tainted skill play added +2 (stacked 2→4 across a turn), inflating displayed enemy intents per-hit (Whirlwind base 5x3 showed 9x3 at stack 4). Does NOT persist into the next turn — the tax is same-turn only.",
        "来自 VITAL_SPARK 的玩家侧减益：本回合受到的攻击伤害 +Amount；敌方回合结束移除。run-41 live：每打一张污染技能 +2（单回合内 2→4 叠加），按段通胀敌方 intent 显示（旋风 base 5×3 在 4 层时显示 9×3）。不跨回合 — 税仅当回合有效。",
        True,
    ),
}

POTION_FOLDS = {
    "CURE_ALL": (
        "gain 1 Energy; draw 2 cards. Despite the name this is NOT a heal — burst/dig class potion; run-41 live confirmed +1e and 2 draws on a boss kill turn. Any archive note claiming healing is wrong.",
        "获得 1 能量；抽 2 张牌。名不副实——并非治疗药水，而是爆发/过牌类；run-41 在 Boss 击杀回合 live 确认 +1e 与抽 2。任何声称其治疗的档案注记均为错误。",
        True,
    ),
    "SPEED_POTION": (
        "apply SpeedPotionPower +5 Dexterity for the current turn; lose the 5 Dexterity at end of turn (temporary). Run-41 live: Defend 5→10 and Shrug 8→13 under the buff; one-turn burst block — spend it on the turn the lethal intent lands, not earlier.",
        "本回合获得 SpeedPotionPower +5 敏捷；回合结束失去这 5 敏捷（临时）。run-41 live：buff 下防御 5→10、耸肩 8→13；单回合爆发挡 — 须用在致命意图落地的那个回合，不要提前喝。",
        True,
    ),
    "POWDERED_DEMISE": (
        "apply DemisePower 9 to the target — the target takes 9 unblockable, unpowered damage at the end of each of its turns. Run-41 live: killed a 4-HP Exoskeleton end-of-turn after it had already attacked; a kill-timer potion for escape-clock and HP-wall fights, not a block tool.",
        "对目标施加 DemisePower 9 — 目标在自己每个回合结束时受到 9 点无视格挡、非能力加成的伤害。run-41 live：在 4 HP 外骨骼虫完成攻击后于回合末将其击杀；这是逃跑钟与 HP 墙战斗的击杀计时药水，不是挡伤工具。",
        True,
    ),
}

RELIC_FOLDS = {
    "POCKETWATCH": (
        "if you played ≤3 cards last turn, turn 2+ hand draws +3 cards. Run-41 discipline: budget exactly 3 plays on T1 (e.g. Inferno+Brand+Bash) to arm the watch — the 8-card T2 hands delivered Inferno+PS+Pyre lines at two elites and the Act1 boss; a 4th play disarms it for a whole turn.",
        "上回合打出 ≤3 张牌时，第 2 回合起手牌额外抽 3 张。run-41 纪律：T1 刻意只打 3 张（如 Inferno+Brand+重锤）给怀表上弦 — 精英与 Act1 Boss 的 T2 8 张手牌交付了 Inferno+PS+跃升线；多打第 4 张会让下一整回合失去加成。",
        True,
    ),
    "KUNAI": (
        "every 3 Attack cards played in one turn, gain 1 Dexterity. Run-41 live: Dex from this relic is combat-scoped — the +1 vanished at the next turn boundary in the Exoskeleton fight; block values computed the following turn must not assume it persists. Fires on the same 3-attack turns as Kusarigama.",
        "同一回合每打出 3 张攻击牌，获得 1 敏捷。run-41 live：该遗物敏捷为战斗内有效 — 外骨骼虫战中次回合边界即消失；下一回合的挡值计算不得默认其存续。与锁镰在同一 3 攻击回合触发。",
        True,
    ),
    "KUSARIGAMA": (
        "every 3 Attack cards played in one turn, deal 6 damage to a random enemy. Run-41 live: procced on the eel-quartet T1 third-attack line — the 6 landed on a different target than the attack chain, useful softening for pack fights.",
        "同一回合每打出 3 张攻击牌，对随机敌人造成 6 点伤害。run-41 live：鳗鱼群 T1 第三次攻击线上触发 — 6 点落在与攻击链不同的目标上，对群怪战有软化价值。",
        True,
    ),
    "PAELS_FLESH": (
        "Act2 Pael boon relic: from turn 3 of each combat onward, gain +1 Energy at the start of your turn. Run-41 live: T3+ energy showed 4/4 with Pyre uncast — stacks with Pyre (+1) and Lantern (T1 only) for a 4-5 energy floor from turn 3.",
        "Act2 佩尔赐福遗物：每场战斗自第 3 回合起，回合开始额外获得 1 能量。run-41 live：未打出跃升时 T3+ 能量已显示 4/4 — 与跃升（+1）及灯笼（仅 T1）叠加，第 3 回合起保底 4-5 能量。",
        True,
    ),
    "STRIKE_DUMMY": (
        "Strike-tagged attack cards deal +3 damage; the bonus applies BEFORE Vulnerable/Cruelty multipliers (run-36 formula note, run-41 live: PS resolved 25 at Prism T2 vs 20-class pre-purchase — tags ~8 × +3 each fed the base). Event Strike-tagged cards (Peck-class) unconfirmed for the bonus.",
        "带 Strike 标签的攻击牌伤害 +3；加成在易伤/残酷乘区之前生效（run-36 公式注记，run-41 live：棱柱 T2 PS 结算 25，购前为 20 级 — 约 8 个 tag × +3 喂入基伤）。事件类 Strike 标签牌（佩克类）是否享受加成未确认。",
        True,
    ),
    "AMETHYST_AUBERGINE": (
        "combat rewards gain +15 Gold (not on the final-act boss). Run-41 live: every fight reward showed +15 on top of base gold — funded the 255g Act2 Shop#1 100% sink together with treasure gold.",
        "战斗奖励额外 +15 金（最终章 Boss 除外）。run-41 live：每场战斗奖励在基础金币上 +15 — 与宝箱金共同支撑了 Act2 商店#1 的 255 金 100% 沉淀。",
        True,
    ),
    "LANTERN": (
        "start each combat with +1 Energy (T1 only). Run-41 live: boss T1 opened at 4/3 display capacity — PS+Strike+Strike or Inferno+Brand+Bash+Strike lines all fit; stacks with Pyre and Pael's Flesh.",
        "每场战斗开始时 +1 能量（仅 T1）。run-41 live：Boss T1 显示容量 4/3 — PS+双打击 或 Inferno+Brand+重锤+打击 线均可全打；可与跃升、佩尔之肉叠加。",
        True,
    ),
}

CARD_FOLDS = {
    "EXPECT_A_FIGHT": (
        "gain 1 Energy per Attack card in your hand; you cannot gain more Energy this turn (NO_ENERGY_GAIN locks further gains). Run-41 live: 3 attacks in hand at 2e cost resolved energy 5/4 — net +1e vs the 4e cap, effectively a 5e turn for attack-dense Pocketwatch hands.",
        "每有一张攻击牌在手便获得 1 点能量；本回合不能再获得其他能量（NO_ENERGY_GAIN 锁定后续获得）。run-41 live：手中 3 攻、2 费打出后能量 5/4 — 相对 4e 上限净 +1，对怀表大手牌的攻击密集回合等效 5e。",
        True,
    ),
    "BLOOD_WALL": (
        "lose 2 HP (unblockable); gain 16 Block. The self-damage fires Inferno's 'whenever you lose HP on your turn' AoE on the same play (run-36 double Act2-elite kill instrument; run-41: 16-block wall on the Exoskeleton Clamp turn). Upgrade +4 Block. Skill-class — tainted under Vital Spark, taxes the prism fight.",
        "失去 2 HP（无视格挡）；获得 16 格挡。自伤在同一打出中触发狱火「回合内失去 HP」的 AoE（run-36 双 Act2 精英击杀器械；run-41：外骨骼虫钳击回合的 16 挡墙）。升级 +4 挡。技能类 — 感染棱柱战的 Vital Spark 下会被污染计税。",
        True,
    ),
    "FEEL_NO_PAIN": (
        "Power card: whenever one of your cards is Exhausted, gain block (Amount per card). Run-23 A1-win exhaust spine; run-41 picked after the Exoskeleton fight — Brand exhausts self + chosen card = two procs per play, Second Wind multi-procs on skill-dense hands.",
        "能力牌：每当你的卡牌被消耗，获得格挡（每张 Amount）。run-23 A1 胜局的 exhaust 脊线；run-41 在外骨骼虫战后选取 — Brand 消耗自身+所选牌 = 每次打出双触发，重振精神在技能密集手牌上多次触发。",
        True,
    ),
    "IRON_WAVE": (
        "gain 5 Block; deal 5 damage. Run-41/live-fold: playing it with target_combat_id on an already-dead target returns ok=true but no-ops the WHOLE card — neither damage nor block applies; the block is tied to the attack resolving on a live target. Attack-class block — the only shape that survives Vital Spark zero-skill discipline in the current Ironclad pool.",
        "获得 5 格挡；造成 5 点伤害。run-41/live 折入：以 target_combat_id 指向已死亡目标时返回 ok=true 但整卡空转 — 伤害与格挡均不生效；格挡与攻击命中活目标绑定。攻击类挡牌 — 当前战士卡池中唯一能在 Vital Spark 零技能纪律下存活的挡牌形态。",
        True,
    ),
    "TAUNT": (
        "gain 7 Block; apply 1 Vulnerable. Run-41 live: Skill Potion fish at the Act1 boss PressureGun turn — 7 block + Vuln refresh in one card on a 2e-turn; free when granted by potion (cost 0 that turn).",
        "获得 7 格挡；施加 1 层易伤。run-41 live：Act1 Boss 压力炮回合的技能药水钓鱼 — 单卡同时给 7 挡 + 易伤刷新；药水赋予时当回合 0 费。",
        True,
    ),
    "PERFECTED_STRIKE": (
        "Strike-tagged; damage = 6 + 2 per Strike-tagged card owned (+3/tag more with Strike Dummy, applied before multipliers). Run-36 formula live; run-41 with Dummy+Str3 resolved 25 on Infested Prism T2 and 20-class on shell-capped Coral Colony — the PS+Strike-Dummy spine is the deck's primary single-hit instrument.",
        "带 Strike 标签；伤害 = 6 + 每张 Strike 标签牌 +2（配打击假人每 tag 再 +3，乘区前生效）。run-36 公式 live；run-41 在假人+力量3 下对感染棱柱 T2 结算 25，对壳上限珊瑚结算 20 级 — PS+打击假人脊线是牌组首要单击器械。",
        True,
    ),
    "CRUELTY": (
        "Power, 1 cost: Vulnerable enemies take +25% attack damage from you (CRUELTY_POWER:25 live run-41). Stacks multiplicatively with Vulnerable's ×1.5. Upgrade raises the total to +50%. Named the A1 graduation interaction in run-17 (PaperPhrog pairing) — run-41 bought it on the Act1 boss reward.",
        "能力牌，1 费：易伤目标受到你的攻击伤害 +25%（run-41 live CRUELTY_POWER:25）。与易伤 ×1.5 乘法叠加。升级提高到 +50%。run-17 将其命名为 A1 毕业级互动（纸蛙搭配）— run-41 在 Act1 Boss 奖励中选取。",
        True,
    ),
}


def fold_monster(mz, mid, zh_desc, notes_zh):
    ent = mz.get(mid)
    if not ent:
        return
    ent["description"] = zh_desc
    ent["play_notes"] = notes_zh
    ent["curated"] = True
    ent.pop("needs_zh", None)


def main():
    monsters = load("monsters.json")
    monsters_zh = load("monsters_zh.json")

    for (mid, move_id), (en, zh, notes_en, notes_zh) in MOVES.items():
        ment = monsters.get(mid, {})
        moves = ment.setdefault("moves", {})
        ment_move = moves.get(move_id)
        if ment_move is None:
            ment_move = {"id": move_id, "kind": "move", "monster_id": mid, "name": move_id}
            moves[move_id] = ment_move
        ment_move["description"] = en
        ment_move["play_notes"] = notes_en
        ment_move["curated"] = True
        ment_move.pop("needs_zh", None)

        mz_ent = monsters_zh.get(mid, {})
        mz_moves = mz_ent.setdefault("moves", {})
        mz_move = mz_moves.get(move_id)
        if mz_move is None:
            mz_move = {"id": move_id, "kind": "move", "monster_id": mid, "name": move_id}
            mz_moves[move_id] = mz_move
        mz_move["description"] = zh
        mz_move["play_notes"] = notes_zh
        mz_move["curated"] = True
        mz_move.pop("needs_zh", None)

    for mid, data in MONSTERS.items():
        ent = monsters.get(mid)
        if ent:
            ent["description"] = data["en"]
            ent["play_notes"] = data["notes_en"]
            ent["curated"] = True
            ent.pop("needs_zh", None)
        fold_monster(monsters_zh, mid, data["zh"], data["notes_zh"])

    save("monsters.json", monsters)
    save("monsters_zh.json", monsters_zh)

    # relics: delete RAGE misfold (Sling of Courage duplicate; card RAGE lives in cards.json)
    relics = load("relics.json")
    relics_zh = load("relics_zh.json")
    rage = relics.pop("RAGE", None)
    relics_zh.pop("RAGE", None)
    if rage and "SLING_OF_COURAGE" not in relics:
        rage["id"] = "SLING_OF_COURAGE"
        rage["needs_zh"] = True
        relics["SLING_OF_COURAGE"] = rage
    for rid, (en, zh, cur) in RELIC_FOLDS.items():
        for store, desc in ((relics, en), (relics_zh, zh)):
            ent = store.get(rid)
            if ent:
                ent["description"] = desc
                ent["curated"] = cur
                ent.pop("needs_zh", None)
    save("relics.json", relics)
    save("relics_zh.json", relics_zh)

    powers = load("powers.json")
    powers_zh = load("powers_zh.json")
    for pid, (en, zh, cur) in POWER_FOLDS.items():
        for store, desc in ((powers, en), (powers_zh, zh)):
            ent = store.get(pid)
            if ent:
                ent["description"] = desc
                ent["curated"] = cur
                ent.pop("needs_zh", None)
    save("powers.json", powers)
    save("powers_zh.json", powers_zh)

    potions = load("potions.json")
    potions_zh = load("potions_zh.json")
    for pid, (en, zh, cur) in POTION_FOLDS.items():
        for store, desc in ((potions, en), (potions_zh, zh)):
            ent = store.get(pid)
            if ent:
                ent["description"] = desc
                ent["curated"] = cur
                ent.pop("needs_zh", None)
    save("potions.json", potions)
    save("potions_zh.json", potions_zh)

    cards = load("cards.json")
    cards_zh = load("cards_zh.json")
    for cid, (en, zh, cur) in CARD_FOLDS.items():
        for store, desc in ((cards, en), (cards_zh, zh)):
            ent = store.get(cid)
            if ent:
                ent["description"] = desc
                ent["curated"] = cur
                ent.pop("needs_zh", None)
    save("cards.json", cards)
    save("cards_zh.json", cards_zh)

    print("folds applied: moves=%d monsters=%d relics=%d powers=%d potions=%d cards=%d RAGE_misfold=%s"
          % (len(MOVES), len(MONSTERS), len(RELIC_FOLDS), len(POWER_FOLDS),
             len(POTION_FOLDS), len(CARD_FOLDS), "removed" if rage else "absent"))


if __name__ == "__main__":
    main()
