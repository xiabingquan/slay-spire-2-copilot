#!/usr/bin/env python3
"""Phase 1A — SpireBridge JSON reference DB generator + checker.

Builds references/game/<domain>.json + <domain>_zh.json (9 pairs) from the
legacy markdown archive, the live-id census (scripts/.cache/live_ids.json),
frozen decomp schema constants, and hand-curated extras. Markdown parsers
are the legacy path; the JSON output is the durable store — after Phase 4
live verification the *.md files are retired.

Usage:
  python3 scripts/build_game_reference_json.py            # generate + write
  python3 scripts/build_game_reference_json.py --check    # coverage gate

--check exits nonzero when: (1) any hard-domain live id from the census does
not resolve in the flattened index (top-level keys + aliases + monster moves
+ event options); (2) any entry lacks a non-empty EN description, or (except
needs_zh:true) a non-empty ZH description.

Language discipline: the EN *.json carries English name/description fields
(aliases may include Chinese display names so lookup resolves live ZH
creature/option strings); the *_zh.json twin carries Chinese name/
description with identical numeric/enum fields. CJK in an EN `name` field is
a bug.

Merge policy: existing output is read first; entries with curated:true are
never overwritten; unknown keys on regenerated entries are carried forward.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_MD_DIR = SKILL_ROOT / "references" / "game"
DEFAULT_LIVE_IDS = SKILL_ROOT / "scripts" / ".cache" / "live_ids.json"
DEFAULT_OUT_DIR = SKILL_ROOT / "references" / "game"
DEFAULT_DECOMP = Path("/tmp/sts2-decomp")  # ephemeral; constants below are frozen

DOMAINS = [
    "characters", "cards", "powers", "relics", "potions",
    "afflictions", "intents", "monsters", "events",
]

# ---------------------------------------------------------------------------
# Frozen schema constants
# decomp refs (ephemeral /tmp/sts2-decomp paths kept for provenance):
#   MegaCrit.Sts2.Core.MonsterMoves.Intents.*   intent classes
#   MegaCrit.Sts2.Core Models IntentType enum
#   MegaCrit.Sts2.Core.Models.Monsters.*        MoveRepeatType / move ids
#   MegaCrit.Sts2.Core.Models.Potions.*         potion classes
# intents.md lines 6-8 stale singular-intent schema claims are DISCARDED —
# never copy them into JSON. Accurate table = intents.md bullets lines 10-73.
# ---------------------------------------------------------------------------

INTENT_TYPE_MEMBERS = {
    "Attack": ["SingleAttackIntent", "MultiAttackIntent"],
    "Buff": ["BuffIntent"],
    "Debuff": ["DebuffIntent"],
    "DebuffStrong": ["DebuffIntent"],
    "Defend": ["DefendIntent"],
    "Heal": ["HealIntent"],
    "Sleep": ["SleepIntent"],
    "Stun": ["StunIntent"],
    "Summon": ["SummonIntent"],
    "StatusCard": ["StatusIntent"],
    "CardDebuff": ["CardDebuffIntent"],
    "Escape": ["EscapeIntent"],
    "DeathBlow": ["DeathBlowIntent"],
    "Hidden": ["HiddenIntent"],
    "Unknown": ["UnknownIntent"],
}

INTENT_STATE_FIELDS = {
    "SingleAttackIntent": ["type", "class", "label", "damage", "total_damage",
                           "hits", "base_damage", "description"],
    "MultiAttackIntent": ["type", "class", "label", "damage", "total_damage",
                          "hits", "base_damage", "description"],
    "DeathBlowIntent": ["type", "class", "label", "damage", "total_damage",
                        "hits", "base_damage", "description"],
    "BuffIntent": ["type", "class", "label", "description"],
    "DebuffIntent": ["type", "class", "label", "description"],
    "DefendIntent": ["type", "class", "label", "description"],
    "HealIntent": ["type", "class", "label", "description"],
    "SleepIntent": ["type", "class", "label", "description"],
    "StunIntent": ["type", "class", "label", "description"],
    "SummonIntent": ["type", "class", "label", "description"],
    "StatusIntent": ["type", "class", "label", "card_count", "description"],
    "CardDebuffIntent": ["type", "class", "label", "description"],
    "EscapeIntent": ["type", "class", "label", "description"],
    "HiddenIntent": ["type", "class", "label", "description"],
    "UnknownIntent": ["type", "class", "label", "description"],
}

INTENT_DECISION_RULES = {
    "SingleAttackIntent": ("Incoming single attack — the label number is the live "
                           "damage preview (Strength/Weak/Vulnerable already applied, "
                           "floored at 0). Compare damage vs your Block + HP; Weak on "
                           "the attacker cuts it (x0.75 per stack)."),
    "MultiAttackIntent": ("Incoming multi-hit attack — label shows per-hit x hits; "
                          "total = per-hit x hits. Block absorbs EACH hit separately, "
                          "so high Block is twice as effective here. Weak cuts the "
                          "per-hit number."),
    "DeathBlowIntent": ("Lethal-styled single attack (DeathBlow icon). Same math as "
                        "SingleAttackIntent — treat as ordinary attack damage; "
                        "block or kill."),
    "BuffIntent": ("Enemy self/allied buff this turn (Strength, Ritual, stances, some "
                   "summons). Free damage window if you can race the ramp — check "
                   "monsters.json move effect for the exact buff before ignoring."),
    "DebuffIntent": ("Enemy applies debuffs (Vulnerable/Weak/Frail/Poison/card "
                     "afflictions). No direct damage — often a setup turn; Artifact "
                     "blocks one visible debuff application; plan burst timing "
                     "around the debuff window."),
    "DefendIntent": ("Enemy gains Block this turn — a low-threat turn; pile damage "
                     "now or prepare Vulnerable for after the block decays."),
    "HealIntent": ("Enemy heals (also revive moves like REVIVE_MOVE). Kill-pressure "
                   "turn: race the heal or re-apply kill-window conditions."),
    "SleepIntent": ("Enemy sleeps/skips action (AsleepPower/SlumberPower stances). "
                    "Free damage window — but unblocked card damage wakes sleepers "
                    "(strips Plating + Asleep, flips to Stun); decide deliberately "
                    "between free hits and controlled wake-stun."),
    "StunIntent": ("Enemy stunned/skips action this turn (burrow break, wake-up "
                   "stuns, Imbalanced). Pure free-damage window — spend it."),
    "SummonIntent": ("Enemy summons adds this turn. Master-minion doctrine usually "
                     "applies: killing the summoner despawns/clears adds; check the "
                     "monster entry before switching targets."),
    "StatusIntent": ("Adds status/curse cards to player piles — card_count = number "
                     "of cards. No direct damage; deck pollution incoming. Thin with "
                     "exhaust/draw tools; status cards are usually unplayable clog."),
    "CardDebuffIntent": ("Injects status/curse cards into player piles (sometimes "
                         "combined with attack on the same move). Treat as deck "
                         "pollution unless the move table also lists an attack — "
                         "then plan block for the attack half."),
    "EscapeIntent": ("Enemy flees combat this turn — kill it NOW or it escapes at "
                     "current HP (often unrewarded). Flutter/escape-timer counters "
                     "can flip this intent if resolved first."),
    "HiddenIntent": ("No sprite, no hover tip — action fully hidden. Play safe: "
                     "keep block/economy; check monsters.json for hidden-move pools "
                     "(e.g. burrowed BELOW_MOVE)."),
    "UnknownIntent": ("Action not yet revealed. Treat as unknown threat — keep "
                      "defensive posture and consult the monster move table."),
}

MOVE_REPEAT_TYPES = ["CanRepeatForever", "UseOnlyOnce", "CannotRepeat", "Cooldown"]

POTION_ID_OVERRIDES = {
    "Clarity Extract": "CLARITY",
    "Cure All": "CURE_ALL",
}

# Kill-timer / countdown / trigger-counter-class powers (plan + coordinator
# audit 2026-09-18): RINGING, SANDPIT, HARD_TO_KILL, PLATING, HATCH,
# TIME_LIMIT, ESCAPE_ARTIST, RAVENOUS, VITAL_SPARK and similar semantics.
COUNTER_CLASS_POWERS = {
    "RINGING_POWER", "SANDPIT_POWER", "HARD_TO_KILL_POWER", "PLATING_POWER",
    "HATCH_POWER", "BATTLEWORN_DUMMY_TIME_LIMIT_POWER", "ESCAPE_ARTIST_POWER",
    "SLOTH_POWER", "THE_BOMB_POWER", "ASLEEP_POWER", "SLUMBER_POWER",
    "SHRIEK_POWER", "PLOW_POWER", "TIME_LIMIT_POWER",
    "RAVENOUS_POWER", "VITAL_SPARK_POWER", "GALVANIC_POWER",
    "CHAINS_OF_BINDING_POWER", "THE_GAMBIT_POWER",
}
COUNTER_CLASS_RE = re.compile(
    r"countdown|timer|time limit|kill timer|escape timer|hatch timer|"
    r"instantly devoured|devour timer|kill clock|kill-timer",
    re.IGNORECASE,
)

SECTION_TO_POOL = {
    "ironclad": "IRONCLAD", "silent": "SILENT", "defect": "DEFECT",
    "necrobinder": "NECROBINDER", "regent": "REGENT", "colorless": "COLORLESS",
    "event": "EVENT", "status": "STATUS", "token": "TOKEN",
    "curse": "CURSE", "quest": "QUEST",
}

CARD_KEYWORDS = [
    "Exhaust", "Ethereal", "Innate", "Retain", "Strike-tagged", "Unplayable",
    "Eternal", "Minion", "Quest", "Goopy", "Cloned", "Defend-tagged",
]

STOP_TOKENS = {
    "HP", "AI", "T1", "T2", "T3", "T4", "T5", "T6", "T7", "T8", "T9",
    "A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8", "A9", "A10",
    "XOR", "ID", "VFX", "LIVE", "DEBUFF", "BUFF", "SLEEP", "STUN", "DEFEND",
    "ATTACK", "STATUS", "ZH", "EN", "DB", "EA", "GOLD", "MAX", "MIN",
    "POWER", "NONE", "SELF", "REPEAT", "AND", "THE", "FOR", "NOT",
    "SHED", "GLORY", "HIVE", "OVERGROWTH", "UNDERDOCKS",
}

# live creature display name -> monster key
CREATURE_NAME_TO_KEY = {
    "铁甲战士": "IRONCLAD", "静默猎手": "SILENT", "储君": "REGENT",
    "亡灵契约师": "NECROBINDER", "故障机器人": "DEFECT",
    "奥斯提": "Osty", "树叶史莱姆（中）": "LeafSlimeM",
    "树叶史莱姆（小）": "LeafSlimeS", "树枝史莱姆（中）": "TwigSlimeM",
    "树枝史莱姆（小）": "TwigSlimeS", "缩小甲虫": "ShrinkerBeetle",
    "墨宝": "Inklet", "蛮兽": "Mawler", "小啃兽": "Nibbit",
    "闪光贾克斯果": "SnappingJaxfruit", "飞蝇菌子": "Flyconid",
    "毛绒伏地虫": "FuzzyWurmCrawler", "雾菇": "Fogmog",
    "利齿之眼": "EyeWithTeeth", "地道虫": "Tunneler",
    "劫掠者刺客": "AssassinRubyRaider", "劫掠者斧手": "AxeRubyRaider",
    "劫掠者暴徒": "BruteRubyRaider", "劫掠者弩手": "CrossbowRubyRaider",
    "劫掠者追踪手": "TrackerRubyRaider", "异蛙寄生虫": "PhrogParasite",
    "扭动虫": "Wriggler", "蛇行扼杀者": "SlitheringStrangler",
    "藤蔓蹒跚者": "VineShambler", "藤蔓妖": "VineShambler",
    "外骨骼虫": "Exoskeleton", "多尼斯异鸟": "Byrdonis",
    "旧日雕像": "BygoneEffigy", "同族神官": "KinPriest",
    "同族信徒": "KinFollower", "噬尸蛞蝓": "CorpseSlug",
    "仪式兽": "CeremonialBeast", "盛碗虫（卵）": "BowlbugEgg",
    "盛碗虫（蜜）": "BowlbugNectar", "盛碗虫（石）": "BowlbugRock",
    "盛碗虫（丝）": "BowlbugSilk", "异螨": "Myte", "啃咬机": "Chomper",
    "猎人杀手": "HunterKiller", "虱虫之祖": "LouseProgenitor",
    "直飞产卵虫": "Ovicopter", "结实的卵": "ToughEgg",
    "熟睡甲虫": "SlumberingBeetle", "棘刺蟾蜍": "SpinyToad",
    "感染棱柱": "InfestedPrism", "立柱构造体": "InfestedPrism",
    "蜂群术士": "Entomancer", "残杀千足虫": "Decimillipede",
    "胧光怪": "TheObscura", "墨影幻灵": "Parafright",
    "寄生惧魔": "Parafright", "偷窃草蜢": "ThievingHopper",
    "无厌沙虫": "TheInsatiable", "碾碎爪": "Crusher", "火箭": "Rocket",
    "知识恶魔": "KnowledgeDemon", "女王": "Queen",
    "实验体 #C8": "TestSubject", "实验体 #C9": "TestSubject",
    "实验体 #C10": "TestSubject", "灵魂枢纽": "SoulNexus",
    "猫头鹰法官": "OwlMagistrate", "连枷骑士": "FlailKnight",
    "幽灵骑士": "SpectralKnight", "魔法骑士": "MagiKnight",
    "失落之物": "LostThing", "遗忘之物": "ForgottenThing",
    "火炬头聚合体": "TorchHeadAggregate",
    "虔诚雕刻师": "DevotedSculptor", "史莱姆狂战士": "SlimedBerserker",
    "活体盾": "LivingShield", "高塔炮手": "TowerGunner",
    "青蛙骑士": "FrogKnight", "电球头": "GlobeHead",
    "机甲骑士": "MechKnight", "战斗好伙伴V3.0": "BattleFriendV3",
    "咬人卷轴": "ScrollOfBiting", "拳击构装体": "PunchConstruct",
    "永世沙漏": "Aeonglass", "瀑布巨兽": "WaterfallGiant",
    "灵魂异鱼": "SoulFysh", "乐加维林族母": "LagavulinMatriarch",
    "下水道蚌": "SewerClam", "蟾蜍蝌蚪": "Toadpole",
    "鬼祟珊瑚群": "CoralCluster", "淤泥旋螺": "SludgeSpinner",
    "花园幽灵鳗": "PhantasmalGardener", "骇鳗": "TerrorEel",
    "幽灵船": "HauntedShip", "地精佣兵": "GremlinMerc",
    "卑鄙地精": "SneakyGremlin", "胖地精": "FatGremlin",
    "钙化邪教徒": "CalcifiedCultist", "潮湿邪教徒": "DampCultist",
    "活雾": "LivingFog", "气态炸弹": "GasBomb", "幼虫": "Larvae",
    "海洋混混": "CorpseSlug", "组装师": "Assembler",
    "神秘骑士": "MysteriousKnight", "佩尔的士兵": "PaelsSoldier",
    "化石追踪者": "FossilStalker", "双尾鼠": "TwoTailedRats",
    "巨斧机器人": "Axebot", "灵魂异鱼": "SoulFysh",
}

CJK_NAME_RE = re.compile(r"[一-鿿][一-鿿·、]*")

# ---------------------------------------------------------------------------
# Hand-curated extras: live ids absent from (or under-specified in) markdown,
# plus curation fixes (counter_class, EN name purity, missing powers/monsters).
# Applied when the generated entry is missing or not already curated:true.
# ---------------------------------------------------------------------------

CURATED_EXTRAS: dict[str, dict[str, dict]] = {
    "powers": {
        "CRIMSON_MANTLE_POWER": {"en": {
            "id": "CRIMSON_MANTLE_POWER", "kind": "power", "name": "Crimson Mantle",
            "description": ("At start of owner's side turn, owner loses 1 HP "
                            "(unblockable) and gains Amount Block (card "
                            "CRIMSON_MANTLE: 8 base, 10 upgraded). The turn-start "
                            "HP loss fires same-turn HP-loss triggers (Rupture, "
                            "Self-Forming Clay, Centennial Puzzle class) and "
                            "counts for Spite/Inferno-style 'lost HP this turn' "
                            "conditions."),
            "power_type": "Buff", "stack_type": "Counter",
            "source": "curated:cards.md CRIMSON_MANTLE + powers doctrine",
        }, "zh": {
            "name": "猩红披风",
            "description": ("持有者阵营回合开始时失去 1 HP（无视格挡）并获得 Amount 格挡"
                            "（卡牌 CRIMSON_MANTLE：基础 8、升级 10）。回合开始掉血可触发"
                            "同回合失去-HP 触发器（撕裂/自成黏土/百年积木类），并满足怨恨/"
                            "狱火类「本回合失去过 HP」条件。"),
        }},
        "CRUELTY_POWER": {"en": {
            "id": "CRUELTY_POWER", "kind": "power", "name": "Cruelty",
            "description": ("Vulnerable enemies take +Amount% attack damage from "
                            "owner (card CRUELTY: +25% base, +50% upgraded). "
                            "Stacks additively with Paper Phrog (+25%) — both "
                            "active a Vulnerable target takes +100% attack damage "
                            "(x2.0 total). Multiplies after Strength additions."),
            "power_type": "Buff", "stack_type": "Counter",
            "source": "curated:cards.md CRUELTY + relics.md PaperPhrog",
        }, "zh": {
            "name": "残忍",
            "description": ("持有者的攻击对处于易伤的敌人伤害 +Amount%（卡牌 CRUELTY："
                            "基础 +25%、升级 +50%）。与纸青蛙（+25%）加法叠加——两者同时"
                            "在场时易伤目标承受 +100% 攻击伤害（总倍率 x2.0）。力量加算"
                            "之后再乘。"),
        }},
        "FLEX_POTION_POWER": {"en": {
            "id": "FLEX_POTION_POWER", "kind": "power", "name": "Flex Potion Power",
            "description": ("Temporary Strength subclass: grants +Amount Strength "
                            "on apply (Flex Potion = +5); the same amount is "
                            "reverted at end of owner's side turn. Type shows Buff "
                            "when positive. Does not persist to next turn — use "
                            "the same-turn burst window."),
            "power_type": "Buff", "stack_type": "Counter",
            "source": "curated:potions.md FlexPotion + powers.md temporary family",
        }, "zh": {
            "name": "屈伸药水之力",
            "description": ("临时力量子类：施加时获得 +Amount 力量（屈伸药水 = +5），"
                            "持有者阵营回合结束时等量回退。数值为正显示 Buff。不跨回合"
                            "——只在当回合爆发窗口内有效。"),
        }},
        "FLUTTER_POWER": {"en": {
            "id": "FLUTTER_POWER", "kind": "power", "name": "Flutter",
            "description": ("Incoming powered-attack damage to owner multiplied by "
                            "x0.5 while stacks > 0; each unblocked attack hit on "
                            "owner decrements 1 stack; at 0 the owner is stunned "
                            "(ThievingHopper stops hovering). Multi-hit attacks "
                            "decrement per unblocked hit — pace chip to clear "
                            "Flutter, then burst."),
            "power_type": "Buff", "stack_type": "Counter",
            "source": "curated:monsters.md ThievingHopper passives",
        }, "zh": {
            "name": "振翅",
            "description": ("层数 >0 时持有者受到的攻击伤害 x0.5；每次未格挡的攻击命中"
                            "持有者消耗 1 层；归零时持有者被击晕（偷窃草蜢停止悬停）。"
                            "多段攻击逐段消耗——先用小伤害清层数再爆发。"),
        }},
        "INFERNO_POWER": {"en": {
            "id": "INFERNO_POWER", "kind": "power", "name": "Inferno",
            "description": ("At start of owner's side turn, owner loses 1 HP "
                            "(unblockable); whenever owner loses HP during owner's "
                            "side turn, deal Amount unpowered damage to ALL "
                            "hittable enemies (card INFERNO: Amount 6 base, 9 "
                            "upgraded). Self-damage cards (Bloodletting, Blood "
                            "Wall, Breakthrough, Hemokinesis) and any same-turn "
                            "HP loss fire the AoE once per loss event. Kills "
                            "through enemy turns only if the loss happens on "
                            "owner's own turn."),
            "power_type": "Buff", "stack_type": "Counter",
            "source": "curated:cards.md INFERNO",
        }, "zh": {
            "name": "狱火",
            "description": ("持有者阵营回合开始时失去 1 HP（无视格挡）；持有者在自己"
                            "回合内失去 HP 时，对所有可命中敌人造成 Amount 点非攻击伤害"
                            "（卡牌 INFERNO：基础 6、升级 9）。自伤牌（放血/血墙/突破/"
                            "放血术等）与任意同回合掉血每次事件触发一次 AoE。"),
        }},
        "JUGGLING_POWER": {"en": {
            "id": "JUGGLING_POWER", "kind": "power", "name": "Juggling",
            "description": ("The 3rd Attack card owner plays each turn is copied "
                            "into owner's hand (card JUGGLING). The copy enters "
                            "hand — it is not auto-played and still costs energy "
                            "unless discounted."),
            "power_type": "Buff", "stack_type": "Counter",
            "source": "curated:cards.md JUGGLING",
        }, "zh": {
            "name": "戏法",
            "description": ("持有者每回合打出的第 3 张攻击牌会复制进手牌（卡牌 "
                            "JUGGLING）。复制体进手而非自动打出，未被减费时仍耗能。"),
        }},
        "PALE_BLUE_DOT_POWER": {"en": {
            "id": "PALE_BLUE_DOT_POWER", "kind": "power", "name": "Pale Blue Dot",
            "description": ("If owner played 5 or more cards last turn, owner "
                            "draws Amount additional cards this turn (card "
                            "PALE_BLUE_DOT, Regent pool: draw 1 base, 2 "
                            "upgraded)."),
            "power_type": "Buff", "stack_type": "Counter",
            "source": "curated:cards.md PALE_BLUE_DOT",
        }, "zh": {
            "name": "苍白蓝点",
            "description": ("若持有者上回合打出 ≥5 张牌，本回合额外抽 Amount 张"
                            "（卡牌 PALE_BLUE_DOT，储君池：基础抽 1、升级抽 2）。"),
        }},
        "PIERCING_WAIL_POWER": {"en": {
            "id": "PIERCING_WAIL_POWER", "kind": "power", "name": "Piercing Wail",
            "description": ("Temporary Strength subclass (negative): applies "
                            "-Amount Strength to affected enemies on apply; the "
                            "same amount is reverted at end of each affected "
                            "enemy's side turn. Type shows Debuff when the "
                            "granted amount is negative."),
            "power_type": "Debuff", "stack_type": "Counter",
            "source": "curated:powers.md temporary-strength family",
        }, "zh": {
            "name": "穿刺哀嚎",
            "description": ("临时力量子类（负向）：施加时给受影响敌人 -Amount 力量，"
                            "各敌人阵营回合结束时等量回退。数值为负时显示 Debuff。"),
        }},
        "REPTILE_TRINKET_POWER": {"en": {
            "id": "REPTILE_TRINKET_POWER", "kind": "power", "name": "Reptile Trinket",
            "description": ("Temporary Strength subclass: whenever owner uses a "
                            "potion, gain +Amount Strength this turn (relic "
                            "REPTILE_TRINKET: +3); reverted at end of owner's "
                            "side turn. Fires on any potion use — stacks "
                            "same-turn with potion-native Strength effects."),
            "power_type": "Buff", "stack_type": "Counter",
            "source": "curated:relics.md ReptileTrinket + powers.md family",
        }, "zh": {
            "name": "爬虫饰品",
            "description": ("临时力量子类：持有者每次使用药水时本回合获得 +Amount 力量"
                            "（遗物 REPTILE_TRINKET：+3），阵营回合结束时回退。任意药水"
                            "使用均触发——可与药水自身的力量效果同回合叠加。"),
        }},
        "SETUP_STRIKE_POWER": {"en": {
            "id": "SETUP_STRIKE_POWER", "kind": "power", "name": "Setup Strike",
            "description": ("Temporary Strength subclass: +Amount Strength for the "
                            "rest of the current turn (card SETUP_STRIKE: +2 "
                            "base, +3 upgraded); reverted at end of owner's side "
                            "turn."),
            "power_type": "Buff", "stack_type": "Counter",
            "source": "curated:cards.md SETUP_STRIKE",
        }, "zh": {
            "name": "预备打击",
            "description": ("临时力量子类：本回合内 +Amount 力量（卡牌 SETUP_STRIKE："
                            "基础 +2、升级 +3），持有者阵营回合结束时回退。"),
        }},
        "SLEIGHT_OF_FLESH_POWER": {"en": {
            "id": "SLEIGHT_OF_FLESH_POWER", "kind": "power", "name": "Sleight of Flesh",
            "description": ("Whenever owner applies a non-temporary debuff to an "
                            "enemy, deal Amount unpowered damage to that enemy "
                            "(card SLEIGHT_OF_FLESH, Necrobinder: 9 base, 13 "
                            "upgraded). Temporary-stat debuffs do not proc it."),
            "power_type": "Buff", "stack_type": "Counter",
            "source": "curated:cards.md SLEIGHT_OF_FLESH",
        }, "zh": {
            "name": "血肉戏法",
            "description": ("持有者每次对敌人施加非临时减益时，对该敌人造成 Amount 点"
                            "非攻击伤害（卡牌 SLEIGHT_OF_FLESH，亡灵契约师：基础 9、"
                            "升级 13）。临时属性类减益不触发。"),
        }},
        "SLOTH_POWER": {"en": {
            "id": "SLOTH_POWER", "kind": "power", "name": "Sloth",
            "description": ("Owner may play at most Amount cards per turn "
                            "(counter resets at owner's turn start; display shows "
                            "cards played this turn). Applied at Amount 3 by the "
                            "KnowledgeDemon CURSE_OF_KNOWLEDGE choice card SLOTH. "
                            "Counter-class kill-window semantics: the cap is the "
                            "fight constraint — burst plans needing >Amount plays "
                            "per turn are dead under Sloth."),
            "power_type": "Debuff", "stack_type": "Counter",
            "source": "curated:afflictions.md SLOTH + monsters.md KnowledgeDemon",
            "counter_class": True,
        }, "zh": {
            "name": "怠惰",
            "description": ("持有者每回合最多打出 Amount 张牌（持有者回合开始时计数"
                            "重置；显示为本回合已打出数）。知识恶魔 CURSE_OF_KNOWLEDGE "
                            "选项卡 SLOTH 施加 Amount 3。计数器级战斗约束：需要单回合"
                            ">Amount 次出牌的爆发线在怠惰下不可行。"),
        }},
        "SPEEDSTER_POWER": {"en": {
            "id": "SPEEDSTER_POWER", "kind": "power", "name": "Speedster",
            "description": ("Whenever owner draws a card outside the normal hand "
                            "draw, deal Amount unpowered damage to ALL hittable "
                            "enemies (card SPEEDSTER, Silent pool: Amount 2 base, "
                            "Innate; upgraded value per card text)."),
            "power_type": "Buff", "stack_type": "Counter",
            "source": "curated:cards.md SPEEDSTER",
        }, "zh": {
            "name": "疾行者",
            "description": ("持有者每次在常规抽牌之外抽牌时，对所有可命中敌人造成 "
                            "Amount 点非攻击伤害（卡牌 SPEEDSTER，静默池：基础 2、"
                            "固有；升级数值见卡面）。"),
        }},
        "SPEED_POTION_POWER": {"en": {
            "id": "SPEED_POTION_POWER", "kind": "power", "name": "Speed Potion Power",
            "description": ("Temporary Dexterity subclass: +Amount Dexterity on "
                            "apply (Speed Potion = +5); reverted at end of "
                            "owner's side turn. NOT a draw potion (distinct from "
                            "Swift Potion) — treat as same-turn block value; the "
                            "Dex boost expires by next turn."),
            "power_type": "Buff", "stack_type": "Counter",
            "source": "curated:potions.md SpeedPotion + powers.md family",
        }, "zh": {
            "name": "速度药水之力",
            "description": ("临时敏捷子类：施加时 +Amount 敏捷（速度药水 = +5），"
                            "持有者阵营回合结束时回退。不是抽牌药水（区别于迅捷药水）"
                            "——按同回合格挡价值使用；敏捷加成下回合即失效。"),
        }},
        "SUCK_POWER": {"en": {
            "id": "SUCK_POWER", "kind": "power", "name": "Suck",
            "description": ("After owner's powered attack deals unblocked damage "
                            "to any target, owner gains +Amount Strength per "
                            "successful hit instance (FossilStalker passive: +3). "
                            "Full-block attack turns keep SUCK dormant — blocking "
                            "attack-intent turns prevents the Strength ramp."),
            "power_type": "Buff", "stack_type": "Counter",
            "source": "curated:monsters.md FossilStalker + power quick reference",
        }, "zh": {
            "name": "汲取",
            "description": ("持有者的攻击牌对任意目标造成未格挡伤害后，按成功命中实例"
                            "每段 +Amount 力量（化石追踪者被动：+3）。攻击意图被完全"
                            "格挡的回合不触发——格挡攻击轮可阻止力量滚雪球。"),
        }},
        "SWIPE_POWER": {"en": {
            "id": "SWIPE_POWER", "kind": "power", "name": "Swipe",
            "description": ("Owner holds 1 stolen deck card (ThievingHopper "
                            "THIEVERY_MOVE priority: non-Imbued Uncommon → "
                            "Common/Rare/Event → Basic/Quest → Ancient/Imbued); "
                            "on owner's death the stolen card returns to the "
                            "victim's deck and an extra card reward is granted. "
                            "Lucky Fysh pays +15 Gold on the silent deck-add."),
            "power_type": "Buff", "stack_type": "Single",
            "source": "curated:monsters.md ThievingHopper",
        }, "zh": {
            "name": "夺取",
            "description": ("持有者控制 1 张被窃牌库卡（偷窃草蜢 THIEVERY_MOVE 优先级："
                            "非铭刻罕见 → 普通/稀有/事件 → 基础/任务 → 远古/铭刻）；"
                            "持有者死亡时被窃牌归还受害者牌库并额外给一张卡牌奖励。"
                            "幸运飞鱼在静默加牌时 +15 金。"),
        }},
        "BACK_ATTACK_LEFT_POWER": {"en": {
            "id": "BACK_ATTACK_LEFT_POWER", "kind": "power", "name": "Back Attack Left",
            "description": ("Inert facing marker (Buff, Single) consumed by "
                            "SURROUNDED_POWER flank checks — the claw carrying "
                            "this marker hits a Surrounded owner at x1.5 when "
                            "the owner faces the opposite direction. No hooks of "
                            "its own."),
            "power_type": "Buff", "stack_type": "Single",
            "source": "curated:powers.md SURROUNDED facing + KaiserCrab",
        }, "zh": {
            "name": "背袭·左",
            "description": ("惰性面向标记（Buff，Single），被 SURROUNDED_POWER 侧袭"
                            "判定读取——持有该标记的爪在持有者面向反方向时对其 ×1.5。"
                            "自身无钩子。"),
        }},
        "BACK_ATTACK_RIGHT_POWER": {"en": {
            "id": "BACK_ATTACK_RIGHT_POWER", "kind": "power", "name": "Back Attack Right",
            "description": ("Inert facing marker (Buff, Single) consumed by "
                            "SURROUNDED_POWER flank checks — the claw carrying "
                            "this marker hits a Surrounded owner at x1.5 when "
                            "the owner faces the opposite direction. No hooks of "
                            "its own."),
            "power_type": "Buff", "stack_type": "Single",
            "source": "curated:powers.md SURROUNDED facing + KaiserCrab",
        }, "zh": {
            "name": "背袭·右",
            "description": ("惰性面向标记（Buff，Single），被 SURROUNDED_POWER 侧袭"
                            "判定读取——持有该标记的爪在持有者面向反方向时对其 ×1.5。"
                            "自身无钩子。"),
        }},
        "FAN_OF_KNIVES_POWER": {"en": {
            "id": "FAN_OF_KNIVES_POWER", "kind": "power", "name": "Fan of Knives",
            "description": ("Inert marker power (Buff, Counter) — no hooks of its "
                            "own; queried by Shiv-tagged cards (Shiv-family "
                            "effects read it, e.g. Shiv hitting ALL enemies "
                            "while Fan of Knives is active)."),
            "power_type": "Buff", "stack_type": "Counter",
            "source": "curated:powers.md inert marker group",
        }, "zh": {
            "name": "刀扇之力",
            "description": ("惰性标记 power（Buff，Counter）——自身无钩子；由 Shiv "
                            "标签卡牌查询（如刀扇激活时 Shiv 类命中全体敌人）。"),
        }},
        "PARRY_POWER": {"en": {
            "id": "PARRY_POWER", "kind": "power", "name": "Parry",
            "description": ("Inert marker power (Buff, Counter) — no hooks of its "
                            "own; queried by specific cards (SovereignBlade "
                            "family parry logic)."),
            "power_type": "Buff", "stack_type": "Counter",
            "source": "curated:powers.md inert marker group",
        }, "zh": {
            "name": "招架",
            "description": ("惰性标记 power（Buff，Counter）——自身无钩子；由特定卡牌"
                            "查询（SovereignBlade 家族招架逻辑）。"),
        }},
        "SEEKING_EDGE_POWER": {"en": {
            "id": "SEEKING_EDGE_POWER", "kind": "power", "name": "Seeking Edge",
            "description": ("Inert marker power (Buff, Counter) — no hooks of its "
                            "own; queried by SovereignBlade-family cards."),
            "power_type": "Buff", "stack_type": "Counter",
            "source": "curated:powers.md inert marker group",
        }, "zh": {
            "name": "寻隙锋",
            "description": "惰性标记 power（Buff，Counter）——自身无钩子；由 SovereignBlade 家族卡牌查询。",
        }},
        "THE_HUNT_POWER": {"en": {
            "id": "THE_HUNT_POWER", "kind": "power", "name": "The Hunt",
            "description": ("Inert success-marker power (Buff, Counter) — no hooks "
                            "of its own; queried by TheHunt card logic."),
            "power_type": "Buff", "stack_type": "Counter",
            "source": "curated:powers.md inert marker group",
        }, "zh": {
            "name": "狩猎",
            "description": "惰性成功标记 power（Buff，Counter）——自身无钩子；由 TheHunt 卡逻辑查询。",
        }},
        "THIEVERY_POWER": {"en": {
            "id": "THIEVERY_POWER", "kind": "power", "name": "Thievery",
            "description": ("Thievery logic marker (Buff, Counter) — queried by "
                            "theft logic; GremlinMerc's version steals 20 Gold "
                            "from the player on its turn. No hooks of its own."),
            "power_type": "Buff", "stack_type": "Counter",
            "source": "curated:powers.md inert marker group + monsters.md GremlinMerc",
        }, "zh": {
            "name": "盗窃",
            "description": ("盗窃逻辑标记（Buff，Counter）——由盗窃逻辑查询；地精佣兵"
                            "版本在其回合窃取玩家 20 金。自身无钩子。"),
        }},
        "FORBIDDEN_GRIMOIRE_POWER": {"en": {
            "id": "FORBIDDEN_GRIMOIRE_POWER", "kind": "power",
            "name": "Forbidden Grimoire",
            "description": ("Source-hosted utility power (Buff, Counter) — "
                            "combat-end / pre-play logic hosted by the source "
                            "card; see the hosting card text for exact trigger."),
            "power_type": "Buff", "stack_type": "Counter",
            "source": "curated:powers.md source-hosted utility group",
        }, "zh": {
            "name": "禁忌魔典",
            "description": "宿主型 utility power（Buff，Counter）——战斗结束/预打出逻辑由源卡牌承载；精确触发见宿主卡面。",
        }},
        "ROYALTIES_POWER": {"en": {
            "id": "ROYALTIES_POWER", "kind": "power", "name": "Royalties",
            "description": ("Source-hosted utility power (Buff, Counter) — "
                            "trigger logic hosted by the source card; see the "
                            "hosting card text."),
            "power_type": "Buff", "stack_type": "Counter",
            "source": "curated:powers.md source-hosted utility group",
        }, "zh": {
            "name": "王权",
            "description": "宿主型 utility power（Buff，Counter）——触发逻辑由源卡牌承载；见宿主卡面。",
        }},
        "THE_SEALED_THRONE_POWER": {"en": {
            "id": "THE_SEALED_THRONE_POWER", "kind": "power",
            "name": "The Sealed Throne",
            "description": ("Source-hosted utility power (Buff, Counter) — "
                            "combat-end / pre-play logic hosted by the source "
                            "card; see the hosting card text."),
            "power_type": "Buff", "stack_type": "Counter",
            "source": "curated:powers.md source-hosted utility group",
        }, "zh": {
            "name": "封印王座",
            "description": "宿主型 utility power（Buff，Counter）——战斗结束/预打出逻辑由源卡牌承载；见宿主卡面。",
        }},
        "POSSESS_STRENGTH_POWER": {"en": {
            "id": "POSSESS_STRENGTH_POWER", "kind": "power", "name": "Possess Strength",
            "description": ("On the holder's turn the holder steals player "
                            "Strength (each holder gains +2 of the stolen stat "
                            "per steal; player Strength display empties as it is "
                            "stolen). Stolen stats return to the player "
                            "same-resolution on holder death — kill holders to "
                            "reclaim. Carried by LostThing (失落之物)."),
            "power_type": "Buff", "stack_type": "Counter",
            "source": "curated:powers.md POSSESS group + monsters.md LostThing",
        }, "zh": {
            "name": "夺力",
            "description": ("持有者回合窃取玩家力量（每次偷取各持有者 +2 对应属性；"
                            "玩家力量显示随窃取清空）。持有者死亡时被窃属性同帧归还玩家"
                            "——击杀持有者即可收回。失落之物携带。"),
        }},
        "POSSESS_SPEED_POWER": {"en": {
            "id": "POSSESS_SPEED_POWER", "kind": "power", "name": "Possess Speed",
            "description": ("On the holder's turn the holder steals player "
                            "Dexterity (each holder gains +2 of the stolen stat "
                            "per steal). Stolen stats return to the player "
                            "same-resolution on holder death — kill holders to "
                            "reclaim. Carried by ForgottenThing (遗忘之物)."),
            "power_type": "Buff", "stack_type": "Counter",
            "source": "curated:powers.md POSSESS group + monsters.md ForgottenThing",
        }, "zh": {
            "name": "夺迅",
            "description": ("持有者回合窃取玩家敏捷（每次偷取各持有者 +2 对应属性）。"
                            "持有者死亡时被窃属性同帧归还玩家——击杀持有者即可收回。"
                            "遗忘之物携带。"),
        }},
        "RAVENOUS_POWER": {"en": {
            "id": "RAVENOUS_POWER", "kind": "power", "name": "Ravenous",
            "description": ("When another creature on owner's side dies and owner "
                            "lives, owner is stunned into a devour move and gains "
                            "+Amount STRENGTH. Kill-window doctrine (CorpseSlug/"
                            "SEAPUNK-class): one kill per turn converts each ally "
                            "death into a free stun window on survivors — "
                            "sequence kills to open stun windows, or avoid "
                            "feeding Strength by leaving adds alive."),
            "power_type": "Buff", "stack_type": "Counter",
            "counter_class": True,
            "source": "curated:powers.md RAVENOUS + coordinator audit 2026-09-18",
        }, "zh": {
            "name": "贪婪",
            "description": ("当同侧另一生物死亡且持有者存活时，持有者被击晕进入吞噬"
                            "招式并获得 +Amount 力量。击杀窗口教条（海洋混混/"
                            "SEAPUNK 级）：每回合一杀把每次友方死亡转化为对幸存者的"
                            "免费晕窗——排布击杀顺序制造晕窗，或留怪不杀避免喂力量。"),
        }},
        "VITAL_SPARK_POWER": {"en": {
            "id": "VITAL_SPARK_POWER", "kind": "power", "name": "Vital Spark",
            "description": ("On the enemy: player Skill cards are afflicted with "
                            "Tainted (Amount) at combat start and on entering "
                            "combat; playing a Tainted card applies "
                            "TAINTED_POWER Amount to the card's owner (incoming "
                            "attack damage +Amount tax, removed end of Enemy "
                            "side turn). Counter-class: displayed as "
                            "VITAL_SPARK_POWER:n and can rise mid-fight (e.g. "
                            "InfestedPrism 2→4) — track it every turn; leave "
                            "Tainted Skills unplayed on key turns."),
            "power_type": "Buff", "stack_type": "Counter",
            "counter_class": True,
            "source": "curated:powers.md VITAL_SPARK + monsters.md InfestedPrism",
        }, "zh": {
            "name": "生命火花",
            "description": ("敌方携带：战斗开始/进入战斗时玩家技能牌被附加污染"
                            "（Amount 层）；打出污染牌时对牌主施加 TAINTED_POWER "
                            "Amount（来袭攻击伤害 +Amount 税，敌方回合结束移除）。"
                            "计数器级：显示为 VITAL_SPARK_POWER:n 且可能战斗中上涨"
                            "（如感染棱柱 2→4）——每回合读取；关键回合留污染技能不打。"),
        }},
    },
    "monsters": {
        "SEAPUNK": {"en": {
            "id": "SEAPUNK", "kind": "monster", "name": "Seapunk",
            "description": ("Live model_id for 海洋混混 (archive name CorpseSlug; "
                            "~44-46 HP, 47-49 at Ascension). Cycle: SEA_KICK_MOVE "
                            "(single attack 11, A:13) → SPINNING_KICK_MOVE "
                            "(multi 2x4) → BUBBLE_BURP_MOVE (2 intents) → repeat. "
                            "Passive RAVENOUS_POWER: when an ALLY dies and this "
                            "creature lives, it is stunned into a devour move and "
                            "gains +Amount Strength — one kill per turn converts "
                            "each death into a free stun window on survivors. "
                            "Doctrine: kill-window via ally-death stun; live "
                            "intents can exceed table values (Glomp 8 table / "
                            "11-class observed at A1)."),
            "aliases": ["海洋混混", "Seapunk", "SeapunkMonster"],
            "acts": ["Act1"], "hp": {"base": 45, "notes": "44-46 base; 47-49 A"},
            "is_boss": False,
            "passives": [{"power_id": "RAVENOUS_POWER", "amount": None,
                          "counter_class": True,
                          "description": "On ally death: self-stun devour move + Strength gain — see RAVENOUS_POWER."}],
            "cycle": ["SEA_KICK_MOVE", "SPINNING_KICK_MOVE", "BUBBLE_BURP_MOVE"],
            "moves": {},
            "source": "curated:census run-37 SEAPUNK model_id + monsters.md CorpseSlug",
            "zh_name": "海洋混混",
        }, "zh": {
            "name": "海洋混混",
            "description": ("live model_id=SEAPUNK（档案旧名 CorpseSlug；约 44-46 HP，"
                            "升格 47-49）。循环：SEA_KICK_MOVE（单段攻击 11，A:13）→ "
                            "SPINNING_KICK_MOVE（多段 2x4）→ BUBBLE_BURP_MOVE（2 意图）"
                            "→ 循环。被动 RAVENOUS_POWER：同侧盟友死亡且自身存活时自晕"
                            "进入吞噬招式并获得 +Amount 力量——每回合一杀即对幸存者开"
                            "免费晕窗。教条：利用盟友死亡晕窗打击杀节奏；live 意图可高于"
                            "表值（Glomp 表 8 / A1 实测 11 级）。"),
        }},
        "CALCIFIED_CULTIST": {"en": {
            "id": "CALCIFIED_CULTIST", "kind": "monster", "name": "Calcified Cultist",
            "description": ("Live model_id for 钙化邪教徒 (38-41 HP). Cycle: "
                            "INCANTATION_MOVE (Buff — RITUAL_POWER self +2) → "
                            "DARK_STRIKE_MOVE (single attack 9, A:11) → repeat. "
                            "Ritual ramps Strength every buff cycle — burst "
                            "before the ramp compounds; race doctrine."),
            "aliases": ["钙化邪教徒", "CalcifiedCultist", "RitualCultist"],
            "acts": ["Act1", "Act2"], "hp": {"base": 40, "notes": "38-41 base"},
            "is_boss": False,
            "passives": [{"power_id": "RITUAL_POWER", "amount": 2,
                          "counter_class": False,
                          "description": "RITUAL_POWER +2 Strength at end of each of its side turns — see powers.json."}],
            "cycle": ["INCANTATION_MOVE", "DARK_STRIKE_MOVE"],
            "moves": {},
            "source": "curated:census run-37 CALCIFIED_CULTIST model_id + monsters.md cultists",
            "zh_name": "钙化邪教徒",
        }, "zh": {
            "name": "钙化邪教徒",
            "description": ("live model_id=CALCIFIED_CULTIST（38-41 HP）。循环："
                            "INCANTATION_MOVE（增益——RITUAL_POWER 自身 +2）→ "
                            "DARK_STRIKE_MOVE（单段攻击 9，A:11）→ 循环。仪式每轮增益"
                            "循环抬升力量——在滚雪球前击杀；竞速教条。"),
        }},
        "DampCultist": {"en": {
            "id": "DampCultist", "kind": "monster", "name": "Damp Cultist",
            "description": ("Ritual cultist sibling (潮湿邪教徒; ~53 HP class): "
                            "RITUAL_POWER at Buff turns (stacks vary, e.g. 5) — "
                            "Strength ramps each subsequent turn start. Race "
                            "doctrine: burst the smaller cultist (Calcified, "
                            "38-41) first, then out-damage the remaining ramp."),
            "aliases": ["潮湿邪教徒", "DampCultist", "RitualCultist"],
            "acts": ["Act1", "Act2"], "hp": {"base": 53, "notes": "~53 HP class"},
            "is_boss": False,
            "passives": [{"power_id": "RITUAL_POWER", "amount": None,
                          "counter_class": False,
                          "description": "RITUAL_POWER stacks vary (e.g. 5) — Strength ramps per turn start."}],
            "cycle": [],
            "moves": {},
            "source": "curated:monsters.md ritual cultists",
            "zh_name": "潮湿邪教徒",
        }, "zh": {
            "name": "潮湿邪教徒",
            "description": ("仪式邪教徒姐妹体（约 53 HP 级）：增益回合施加 RITUAL_POWER"
                            "（层数不定，如 5）——之后每回合开始力量递增。竞速教条：先杀"
                            "较弱的钙化邪教徒（38-41），再对剩余的滚雪球打出伤害差。"),
        }},
        "Osty": {"en": {
            "id": "Osty", "kind": "monster", "name": "Osty",
            "description": ("Necrobinder pet summon. BOUND_PHYLACTERY summons 1 "
                            "at combat start and re-summons after energy reset on "
                            "later turns if gone; Phylactery Unbound summons 5 at "
                            "combat start + 2 each turn. Osty attacks feed Bone "
                            "Flute (owner +2 Block per Osty attack) and "
                            "NECRO_MASTERY_POWER (Osty HP lost x Amount "
                            "unblockable AoE). Card UNLEASH: Osty deals damage = "
                            "6 + Osty's current HP (upgraded base 9). "
                            "DIE_FOR_YOU_POWER-class death handling: Osty death "
                            "does not end combat; pet logic revives/respawns per "
                            "character kit."),
            "aliases": ["奥斯提", "OstyPet"],
            "acts": [], "hp": {"base": None, "notes": "pet summon — HP set by summon source"},
            "is_boss": False,
            "passives": [{"power_id": "DIE_FOR_YOU_POWER", "amount": None,
                          "counter_class": False,
                          "description": "Osty-family death handler — combat does not end on owner death; pet logic revives."}],
            "cycle": [], "moves": {},
            "source": "curated:relics.md BoundPhylactery + cards.md UNLEASH",
            "zh_name": "奥斯提",
        }, "zh": {
            "name": "奥斯提",
            "description": ("亡灵契约师宠物召唤物。缚魂命匣战斗开始召唤 1 只，后续回合"
                            "若不在场则能量重置后重召；无界命匣战斗开始召唤 5 只、每回合"
                            "+2。Osty 攻击喂骨笛（每次攻击持有者 +2 格挡）与 "
                            "NECRO_MASTERY_POWER（Osty 掉血 x Amount 不可格挡 AoE）。"
                            "卡牌 UNLEASH：Osty 造成 6 + Osty 当前 HP 伤害（升级基础 9）。"
                            "DIE_FOR_YOU_POWER 级死亡处理：Osty 死亡不结束战斗，宠物逻辑"
                            "按角色套件复活/重召。"),
        }},
        "Axebot": {"en": {
            "id": "Axebot", "kind": "monster", "name": "Axebot",
            "description": ("StockPower death-spawn robot chain (巨斧机器人): on "
                            "holder death with Amount > 0, spawns Axebot in the "
                            "same slot with StockAmount = Amount - 1; combat does "
                            "not end while chain charges remain. Chain-link spawn "
                            "HP is not guaranteed full (1/x current HP observed) "
                            "— same class as MechKnight spawn variance. Clear the "
                            "chain or the assembler keeps replacing bodies."),
            "aliases": ["巨斧机器人", "Axebot"],
            "acts": ["Act2", "Act3"], "hp": {"base": None, "notes": "spawn HP not guaranteed full"},
            "is_boss": False,
            "passives": [{"power_id": "STOCK_POWER", "amount": None,
                          "counter_class": True,
                          "description": "STOCK_POWER chain — death spawns next robot variant with StockAmount-1."}],
            "cycle": [], "moves": {},
            "source": "curated:powers.md STOCK_POWER + monsters.md StockPower notes",
            "zh_name": "巨斧机器人",
        }, "zh": {
            "name": "巨斧机器人",
            "description": ("StockPower 死亡生成机器人链：持有者死亡且 Amount > 0 时，"
                            "在同槽位生成 Axebot（StockAmount = Amount - 1）；链上充能"
                            "未尽时战斗不结束。链环生成 HP 不保证满血（观测到 1/x 当前"
                            "HP）——与机甲骑士生成变异同类。清链否则组装师不断补位。"),
        }},
        "GasBomb": {"en": {
            "id": "GasBomb", "kind": "monster", "name": "Gas Bomb",
            "description": ("LivingFog summon (气态炸弹): 7 HP minion "
                            "(MINION_POWER), attack-class intent ~8. Master-minion "
                            "doctrine: killing LivingFog (the summoner) despawns/"
                            "clears its adds — do not grind the bombs while the "
                            "fog lives and keeps summoning."),
            "aliases": ["气态炸弹", "GasBomb"],
            "acts": ["Act2"], "hp": {"base": 7, "notes": "7 HP minion"},
            "is_boss": False,
            "passives": [{"power_id": "MINION_POWER", "amount": None,
                          "counter_class": False,
                          "description": "Minion mark — death does not trigger combat-end fatal logic."}],
            "cycle": [], "moves": {},
            "source": "curated:monsters.md LivingFog",
            "zh_name": "气态炸弹",
        }, "zh": {
            "name": "气态炸弹",
            "description": ("活雾召唤物：7 HP 小怪（MINION_POWER），攻击类意图约 8。"
                            "主体-小怪教条：击杀活雾（召唤者）会驱散其召唤物——雾存活并"
                            "持续召唤时不要消耗战清炸弹。"),
        }},
        "MysteriousKnight": {"en": {
            "id": "MysteriousKnight", "kind": "monster", "name": "Mysterious Knight",
            "description": ("THE_LANTERN_KEY KEEP_THE_KEY fight "
                            "(MysteriousKnightEventEncounter; 神秘骑士). Victory "
                            "grants each player a LanternKey quest card "
                            "(Unplayable; in Act index 2 it forces unknown map "
                            "points to be Event rooms and redirects the next "
                            "event to WAR_HISTORIAN_REPY). Treat live intents as "
                            "authoritative — move table not decoded in "
                            "monsters.md."),
            "aliases": ["神秘骑士", "MysteriousKnight"],
            "acts": ["Act1", "Act2"], "hp": {"base": None, "notes": "event fight — HP not tabled"},
            "is_boss": False, "passives": [], "cycle": [], "moves": {},
            "source": "curated:events.md THE_LANTERN_KEY",
            "zh_name": "神秘骑士",
        }, "zh": {
            "name": "神秘骑士",
            "description": ("灯火钥匙事件 KEEP_THE_KEY 战斗（神秘骑士）。胜利后每名玩家"
                            "获得 LanternKey 任务卡（不可打出；Act 索引 2 时强制未知地图"
                            "点为事件房并把下一个事件重定向到 WAR_HISTORIAN_REPY）。"
                            "以 live 意图为权威——monsters.md 未解码其招式表。"),
        }},
        "Assembler": {"en": {
            "id": "Assembler", "kind": "monster", "name": "Assembler",
            "description": ("Live-seen Act monster (组装师). Details not decoded "
                            "in monsters.md — resolve its move ids via "
                            "`spirectl lookup <move_id>` each combat and treat "
                            "live intent fields (damage/hits/description) as "
                            "authoritative. Suspected robot-assembly family "
                            "(StockPower chain spawns)."),
            "aliases": ["组装师", "Assembler"],
            "acts": ["Act2", "Act3"], "hp": {"base": None, "notes": "not tabled"},
            "is_boss": False, "passives": [], "cycle": [], "moves": {},
            "source": "curated:census creature_name 组装师",
            "zh_name": "组装师",
        }, "zh": {
            "name": "组装师",
            "description": ("live 观测怪物（组装师）。monsters.md 未解码——每场战斗用 "
                            "`spirectl lookup <move_id>` 解析其招式 id，以 live 意图字段"
                            "（damage/hits/description）为权威。疑似机器人组装家族"
                            "（StockPower 链生成）。"),
        }},
        "SneakyGremlin": {"en": {
            "id": "SneakyGremlin", "kind": "monster", "name": "Sneaky Gremlin",
            "description": ("SurprisePower spawn on GremlinMerc death (卑鄙地精; "
                            "11 HP): carries HEIST_POWER-class escape logic — "
                            "intent Escape; escapes at 1 HP unrewarded if not "
                            "killed in time. Kill both gremlins before they "
                            "flee."),
            "aliases": ["卑鄙地精", "SneakyGremlin"],
            "acts": ["Act2"], "hp": {"base": 11, "notes": "11 HP spawn"},
            "is_boss": False,
            "passives": [{"power_id": "HEIST_POWER", "amount": None,
                          "counter_class": False,
                          "description": "Escape/reward logic marker — see powers.json HEIST_POWER."}],
            "cycle": [], "moves": {},
            "source": "curated:monsters.md GremlinMerc SurprisePower",
            "zh_name": "卑鄙地精",
        }, "zh": {
            "name": "卑鄙地精",
            "description": ("地精佣兵 SurprisePower 死亡生成物（11 HP）：携带 "
                            "HEIST_POWER 级逃跑逻辑——意图 Escape；未及时击杀会在 1 HP "
                            "逃脱且无奖励。两只地精都要在逃脱前杀掉。"),
        }},
        "FatGremlin": {"en": {
            "id": "FatGremlin", "kind": "monster", "name": "Fat Gremlin",
            "description": ("SurprisePower spawn on GremlinMerc death (胖地精; "
                            "17 HP): carries HEIST_POWER-class escape logic — "
                            "intent Escape; escapes unrewarded. Kill both "
                            "gremlins before they flee."),
            "aliases": ["胖地精", "FatGremlin"],
            "acts": ["Act2"], "hp": {"base": 17, "notes": "17 HP spawn"},
            "is_boss": False,
            "passives": [{"power_id": "HEIST_POWER", "amount": None,
                          "counter_class": False,
                          "description": "Escape/reward logic marker — see powers.json HEIST_POWER."}],
            "cycle": [], "moves": {},
            "source": "curated:monsters.md GremlinMerc SurprisePower",
            "zh_name": "胖地精",
        }, "zh": {
            "name": "胖地精",
            "description": ("地精佣兵 SurprisePower 死亡生成物（17 HP）：携带 "
                            "HEIST_POWER 级逃跑逻辑——意图 Escape；逃脱无奖励。两只"
                            "地精都要在逃脱前杀掉。"),
        }},
        "PaelsSoldier": {"en": {
            "id": "PaelsSoldier", "kind": "monster", "name": "Pael's Soldier",
            "description": ("Pael-family encounter add (佩尔的士兵; Act2 Hive). "
                            "Not detailed in monsters.md — resolve move ids via "
                            "`spirectl lookup` and treat live intent fields as "
                            "authoritative."),
            "aliases": ["佩尔的士兵", "PaelsSoldier"],
            "acts": ["Act2"], "hp": {"base": None, "notes": "not tabled"},
            "is_boss": False, "passives": [], "cycle": [], "moves": {},
            "source": "curated:census creature_name 佩尔的士兵",
            "zh_name": "佩尔的士兵",
        }, "zh": {
            "name": "佩尔的士兵",
            "description": ("佩尔家族遭遇随从（Act2 虫巢）。monsters.md 未记载——用 "
                            "`spirectl lookup` 解析招式 id，以 live 意图字段为权威。"),
        }},
        "Larvae": {"en": {
            "id": "Larvae", "kind": "monster", "name": "Larvae",
            "description": ("Ovicopter hatchlings (幼虫; 19–21 HP): MINION_POWER; "
                            "NIBBLE-class single attack 4 base, Strength grows "
                            "each cycle (4→6). Death does not end combat. "
                            "Mother-first doctrine: killing Ovicopter despawns "
                            "ALL adds same frame (MinionPower master-death rule) "
                            "— wave-clear attrition loses to her Strength ramp."),
            "aliases": ["幼虫", "Larvae", "ToughEggHatchling"],
            "acts": ["Act2"], "hp": {"base": 20, "notes": "19-21 HP"},
            "is_boss": False,
            "passives": [{"power_id": "MINION_POWER", "amount": None,
                          "counter_class": False,
                          "description": "Minion mark — death does not end combat."}],
            "cycle": ["NIBBLE_MOVE"], "moves": {},
            "source": "curated:monsters.md Ovicopter/Larvae notes",
            "zh_name": "幼虫",
        }, "zh": {
            "name": "幼虫",
            "description": ("直飞产卵虫孵化体（19–21 HP）：MINION_POWER；NIBBLE 级单段"
                            "攻击基础 4，力量随循环增长（4→6）。死亡不结束战斗。母体优先"
                            "教条：击杀直飞产卵虫同帧驱散全部召唤物（MinionPower 主体"
                            "死亡规则）——清波消耗战打不过她的力量滚雪球。"),
        }},
        "CoralCluster": {"en": {
            "id": "CoralCluster", "kind": "monster", "name": "Coral Cluster",
            "description": ("Act1 elite, archive pair name Coral Cluster / "
                            "Skulking Colony (鬼祟珊瑚群; 75 HP). Passive "
                            "HARDENED_SHELL_POWER 20 (patch raised base 15→20): "
                            "HP loss per turn capped at Amount minus damage "
                            "already taken this turn (tracker resets at turn "
                            "start); excess wasted — pace hits to land exactly "
                            "20/turn (75 HP → minimum 4 turns). Cycle: Smash/"
                            "Zoom → Inertia (damage + self Strength — race; Str "
                            "stacks make later turns deadly) → Piercing Stabs "
                            "(multi-hit) → loop. Counterplay: cap-efficient "
                            "pacing, full block on Piercing Stabs turns, kill "
                            "before Inertia Strength snowball."),
            "aliases": ["鬼祟珊瑚群", "Coral Cluster", "SkulkingColony",
                        "Skulking Colony", "CoralCluster"],
            "acts": ["Act1"], "hp": {"base": 75, "notes": "75 HP elite"},
            "is_boss": True,
            "passives": [{"power_id": "HARDENED_SHELL_POWER", "amount": 20,
                          "counter_class": True,
                          "description": "HP loss per turn capped at Amount minus damage already taken this turn — pace to exactly 20/turn."}],
            "cycle": ["SMASH_MOVE", "ZOOM_MOVE", "INERTIA_MOVE",
                      "PIERCING_STABS_MOVE"],
            "moves": {},
            "source": "curated:monsters.md additional decodes Coral Cluster",
            "zh_name": "鬼祟珊瑚群",
        }, "zh": {
            "name": "鬼祟珊瑚群",
            "description": ("Act1 精英，档案并名 Coral Cluster / Skulking Colony（75 HP）。"
                            "被动 HARDENED_SHELL_POWER 20（补丁基线 15→20）：每回合 HP "
                            "损失上限 = Amount − 本回合已受伤害（回合开始重置）；超出"
                            "浪费——按每回合恰好 20 伤配速（75 HP → 最少 4 回合）。循环："
                            "Smash/Zoom → Inertia（伤害 + 自身力量——竞速；力量叠层让"
                            "后续回合致命）→ Piercing Stabs（多段）→ 循环。反制：按上限"
                            "配速、Piercing Stabs 回合满挡、在 Inertia 力量滚雪球前击杀。"),
        }},
        "SkulkingColony": {"en": {
            "id": "SkulkingColony", "kind": "monster", "name": "Skulking Colony",
            "description": ("Alternate archive name for the Act1 elite pair "
                            "documented as Coral Cluster / Skulking Colony "
                            "(鬼祟珊瑚群; 75 HP). Same entry: HARDENED_SHELL_POWER "
                            "20 per-turn damage cap (pace to exactly 20/turn); "
                            "cycle Smash/Zoom → Inertia → Piercing Stabs. See "
                            "CoralCluster for full doctrine."),
            "aliases": ["Skulking Colony", "CoralCluster", "Coral Cluster",
                        "鬼祟珊瑚群"],
            "acts": ["Act1"], "hp": {"base": 75, "notes": "75 HP elite"},
            "is_boss": True,
            "passives": [{"power_id": "HARDENED_SHELL_POWER", "amount": 20,
                          "counter_class": True,
                          "description": "HP loss per turn capped at Amount minus damage already taken this turn."}],
            "cycle": [], "moves": {},
            "source": "curated:monsters.md additional decodes",
            "zh_name": "鬼祟珊瑚群",
        }, "zh": {
            "name": "鬼祟珊瑚群",
            "description": ("Act1 精英并名档案的另一名称（Coral Cluster / Skulking "
                            "Colony；75 HP）。同一条目：HARDENED_SHELL_POWER 20 每回合"
                            "伤害上限（按恰好 20/回合配速）；循环 Smash/Zoom → Inertia → "
                            "Piercing Stabs。完整教条见 CoralCluster。"),
        }},
        "BattleFriendV2": {"en": {
            "id": "BattleFriendV2", "kind": "monster", "name": "Battle Friend V2.0",
            "description": ("BattlewornDummy event sparring dummy V2 (战斗好伙伴"
                            "V2; 150 HP flat single-player Act3). Move NOTHING_MOVE "
                            "— never attacks; spawn BATTLEWORN_DUMMY_TIME_LIMIT_"
                            "POWER 3 (decrements at end of dummy side turns; at 1 "
                            "the dummy Escapes and RanOutOfTime=true → no event "
                            "reward). Pure DPS race. Reward on kill (Setting2): "
                            "upgrade 2 random deck cards."),
            "aliases": ["战斗好伙伴V2.0", "BattleFriendV2"],
            "acts": ["Act3"], "hp": {"base": 150, "notes": "150 HP flat single-player"},
            "is_boss": False,
            "passives": [{"power_id": "BATTLEWORN_DUMMY_TIME_LIMIT_POWER",
                          "amount": 3, "counter_class": True,
                          "description": "Decrees at end of dummy side turns; at 1 dummy escapes — no reward."}],
            "cycle": ["NOTHING_MOVE"], "moves": {},
            "source": "curated:events.md BATTLEWORN_DUMMY + monsters.md",
            "zh_name": "战斗好伙伴V2",
        }, "zh": {
            "name": "战斗好伙伴V2",
            "description": ("战痕假人事件陪练 V2（单人 Act3 固定 150 HP）。招式 "
                            "NOTHING_MOVE——从不攻击；生成 "
                            "BATTLEWORN_DUMMY_TIME_LIMIT_POWER 3（假人阵营回合结束"
                            "递减；到 1 时假人逃跑且 RanOutOfTime=true → 无事件奖励）。"
                            "纯 DPS 竞速。击杀奖励（Setting2）：升级 2 张随机牌库卡。"),
        }},
        "BattleFriendV3": {"en": {
            "id": "BattleFriendV3", "kind": "monster", "name": "Battle Friend V3.0",
            "description": ("BattlewornDummy event sparring dummy V3 (战斗好伙伴"
                            "V3.0; 300 HP flat single-player Act3). Move "
                            "NOTHING_MOVE — never attacks; spawn "
                            "BATTLEWORN_DUMMY_TIME_LIMIT_POWER 3 — at 1 the dummy "
                            "Escapes, RanOutOfTime=true → no reward. Pure DPS "
                            "race. Reward on kill (Setting3): 1 relic "
                            "(RelicFactory front)."),
            "aliases": ["战斗好伙伴V3.0", "BattleFriendV3"],
            "acts": ["Act3"], "hp": {"base": 300, "notes": "300 HP flat single-player"},
            "is_boss": False,
            "passives": [{"power_id": "BATTLEWORN_DUMMY_TIME_LIMIT_POWER",
                          "amount": 3, "counter_class": True,
                          "description": "Decrees at end of dummy side turns; at 1 dummy escapes — no reward."}],
            "cycle": ["NOTHING_MOVE"], "moves": {},
            "source": "curated:events.md BATTLEWORN_DUMMY + monsters.md",
            "zh_name": "战斗好伙伴V3.0",
        }, "zh": {
            "name": "战斗好伙伴V3.0",
            "description": ("战痕假人事件陪练 V3（单人 Act3 固定 300 HP）。招式 "
                            "NOTHING_MOVE——从不攻击；生成 "
                            "BATTLEWORN_DUMMY_TIME_LIMIT_POWER 3——到 1 时假人逃跑，"
                            "RanOutOfTime=true → 无奖励。纯 DPS 竞速。击杀奖励"
                            "（Setting3）：1 件遗物（RelicFactory 队首）。"),
        }},
        "IRONCLAD": {"en": {
            "id": "IRONCLAD", "kind": "monster", "name": "Ironclad (player)",
            "description": ("Player character placeholder — live creature name "
                            "铁甲战士 resolves here for combat-state creature "
                            "lines. See characters.json IRONCLAD for stats "
                            "(80 HP, BURNING_BLOOD, IroncladCardPool)."),
            "aliases": ["铁甲战士", "CHARACTER.IRONCLAD"],
            "acts": [], "hp": {"base": 80, "notes": "player character"},
            "is_boss": False, "passives": [], "cycle": [], "moves": {},
            "source": "curated:characters.json cross-ref",
            "zh_name": "铁甲战士",
        }, "zh": {
            "name": "铁甲战士（玩家）",
            "description": ("玩家角色占位条目——战斗状态生物行中的 live 名称 铁甲战士 "
                            "解析到此处。数值见 characters.json IRONCLAD（80 HP、"
                            "BURNING_BLOOD、IroncladCardPool）。"),
        }},
        "SILENT": {"en": {
            "id": "SILENT", "kind": "monster", "name": "Silent (player)",
            "description": ("Player character placeholder — live creature name "
                            "静默猎手 resolves here. See characters.json SILENT "
                            "(70 HP, RING_OF_THE_SNAKE)."),
            "aliases": ["静默猎手", "CHARACTER.SILENT"],
            "acts": [], "hp": {"base": 70, "notes": "player character"},
            "is_boss": False, "passives": [], "cycle": [], "moves": {},
            "source": "curated:characters.json cross-ref",
            "zh_name": "静默猎手",
        }, "zh": {
            "name": "静默猎手（玩家）",
            "description": "玩家角色占位条目——live 名称 静默猎手 解析到此处。数值见 characters.json SILENT（70 HP、RING_OF_THE_SNAKE）。",
        }},
        "REGENT": {"en": {
            "id": "REGENT", "kind": "monster", "name": "Regent (player)",
            "description": ("Player character placeholder — live creature name "
                            "储君 resolves here. See characters.json REGENT "
                            "(75 HP, DIVINE_RIGHT, star counter kit)."),
            "aliases": ["储君", "CHARACTER.REGENT"],
            "acts": [], "hp": {"base": 75, "notes": "player character"},
            "is_boss": False, "passives": [], "cycle": [], "moves": {},
            "source": "curated:characters.json cross-ref",
            "zh_name": "储君",
        }, "zh": {
            "name": "储君（玩家）",
            "description": "玩家角色占位条目——live 名称 储君 解析到此处。数值见 characters.json REGENT（75 HP、DIVINE_RIGHT、星星套件）。",
        }},
        "NECROBINDER": {"en": {
            "id": "NECROBINDER", "kind": "monster", "name": "Necrobinder (player)",
            "description": ("Player character placeholder — live creature name "
                            "亡灵契约师 resolves here. See characters.json "
                            "NECROBINDER (66 HP, BOUND_PHYLACTERY, SpawnsPets)."),
            "aliases": ["亡灵契约师", "CHARACTER.NECROBINDER"],
            "acts": [], "hp": {"base": 66, "notes": "player character"},
            "is_boss": False, "passives": [], "cycle": [], "moves": {},
            "source": "curated:characters.json cross-ref",
            "zh_name": "亡灵契约师",
        }, "zh": {
            "name": "亡灵契约师（玩家）",
            "description": "玩家角色占位条目——live 名称 亡灵契约师 解析到此处。数值见 characters.json NECROBINDER（66 HP、BOUND_PHYLACTERY、SpawnsPets）。",
        }},
        "DEFECT": {"en": {
            "id": "DEFECT", "kind": "monster", "name": "Defect (player)",
            "description": ("Player character placeholder — live creature name "
                            "故障机器人 resolves here. See characters.json DEFECT "
                            "(75 HP, CRACKED_CORE, 3 orb slots)."),
            "aliases": ["故障机器人", "CHARACTER.DEFECT"],
            "acts": [], "hp": {"base": 75, "notes": "player character"},
            "is_boss": False, "passives": [], "cycle": [], "moves": {},
            "source": "curated:characters.json cross-ref",
            "zh_name": "故障机器人",
        }, "zh": {
            "name": "故障机器人（玩家）",
            "description": "玩家角色占位条目——live 名称 故障机器人 解析到此处。数值见 characters.json DEFECT（75 HP、CRACKED_CORE、3 球槽）。",
        }},
    },
    "events": {
        "NONUPEIPE": {"en": {
            "id": "NONUPEIPE", "kind": "event", "name": "Nonupeipe",
            "description": ("Act3 Glory ancient boon room. Option handlers not "
                            "present in the decompiled event sources reviewed — "
                            "live options seen: BRILLIANT_SCARF, FUR_COAT, "
                            "LOOMING_FRUIT (ancient relics; effects in "
                            "relics.json). Ungated ancient per act sources."),
            "source": "curated:events.md ancient options + census",
        }, "zh": {
            "name": "诺努佩佩",
            "description": ("Act3 荣光之殿远古增益房。已审阅的反编译事件源中无选项"
                            "处理器——live 观测选项：BRILLIANT_SCARF、FUR_COAT、"
                            "LOOMING_FRUIT（远古遗物；效果见 relics.json）。按章节源"
                            "无门槛远古。"),
        }},
    },
}

# ---------------------------------------------------------------------------
# small helpers
# ---------------------------------------------------------------------------

def camel_to_upper_snake(name: str) -> str:
    s = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", name)
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s)
    s = re.sub(r"[^A-Za-z0-9]+", "_", s)
    return re.sub(r"_+", "_", s).strip("_").upper()


def has_cjk(s) -> bool:
    return bool(s) and bool(re.search(r"[一-鿿]", str(s)))


def humanize(token: str) -> str:
    words = [w for w in re.split(r"[_\-\s]+", token) if w]
    return " ".join(w.capitalize() if not w.isupper() or len(w) > 3 else w.title()
                    for w in words) or token


def name_from_power_id(pid: str) -> str:
    base = pid
    for suffix in ("_STRENGTH_DOWN_POWER", "_POWER"):
        if base.endswith(suffix) and base != suffix:
            base = base[: -len(suffix)]
            break
    return humanize(base)


def envelope(entry_id: str, kind: str, name: str, description: str,
             aliases=None, play_notes: str = "", source: str = "", **extra):
    # EN name must never carry CJK — fall back to the id humanized form
    if has_cjk(name):
        name = humanize(entry_id) if not has_cjk(entry_id) else entry_id
    e = {
        "id": entry_id,
        "kind": kind,
        "name": name,
        "description": (description or "").strip(),
        "aliases": sorted({str(a) for a in (aliases or []) if a and a != entry_id}),
        "play_notes": (play_notes or "").strip(),
        "curated": False,
        "needs_zh": False,
        "source": source,
    }
    e.update(extra)
    return e


def join_bullets(path: Path):
    if not path.exists():
        return []
    lines = path.read_text(encoding="utf-8").splitlines()
    out = []
    cur = None
    start = 0
    indent = 0
    for i, raw in enumerate(lines, 1):
        if re.match(r"^\s*-\s+", raw):
            if cur is not None:
                out.append((start, cur, indent))
            indent = len(raw) - len(raw.lstrip())
            cur = raw.lstrip()[2:].rstrip()
            start = i
        elif cur is not None and raw.strip() and (raw.startswith(" ") or raw.startswith("\t")):
            cur += " " + raw.strip()
        elif cur is not None and not raw.strip():
            continue
        else:
            if cur is not None:
                out.append((start, cur, indent))
                cur = None
    if cur is not None:
        out.append((start, cur, indent))
    return out


def split_meta(meta: str):
    return [t.strip() for t in re.split(r"[,，;；]", meta) if t.strip()]


def load_existing(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except json.JSONDecodeError:
        return {}


def merge_domain(old: dict, new: dict) -> dict:
    merged = {}
    for key, entry in new.items():
        prior = old.get(key)
        if isinstance(prior, dict) and prior.get("curated") is True:
            merged[key] = prior
            continue
        if isinstance(prior, dict):
            carried = dict(entry)
            for k, v in prior.items():
                if k not in carried:
                    carried[k] = v
            merged[key] = carried
        else:
            merged[key] = entry
    for key, entry in old.items():
        if key not in merged and isinstance(entry, dict) and entry.get("curated") is True:
            merged[key] = entry
    return merged


# ---------------------------------------------------------------------------
# domain parsers
# ---------------------------------------------------------------------------

def parse_relics(md_path: Path, zh_path: Path) -> dict:
    entries = {}
    zh_by_key = {}
    for line_no, text, _ in join_bullets(zh_path):
        m = re.match(r"^([^(（]+?)\s*[（(]([^）)]+)[）)]\s*[:：]\s*(.*)$", text)
        if not m:
            continue
        zh_name, meta, body = m.group(1).strip(), m.group(2), m.group(3).strip()
        parts = split_meta(meta)
        camel = next((p for p in parts if re.match(r"^[A-Z][A-Za-z0-9]*$", p)), None)
        if not camel:
            continue
        key = camel_to_upper_snake(camel)
        zh_by_key[key] = {"name": zh_name, "description": body,
                          "source": f"md:relics_zh.md:L{line_no}"}

    for line_no, text, _ in join_bullets(md_path):
        m = re.match(r"^([^(]+?)\s*\(([^)]+)\)\s*[:：]\s*(.*)$", text)
        if not m:
            continue
        en_name, meta, body = m.group(1).strip(), m.group(2), m.group(3).strip()
        parts = split_meta(meta)
        camel = next((p for p in parts if re.match(r"^[A-Z][A-Za-z0-9]*$", p)), None)
        if not camel:
            continue
        rarity = next((p for p in parts if p in {
            "Starter", "Common", "Uncommon", "Rare", "Ancient", "Shop",
            "Event", "None", "Token"}), None)
        character = next((p for p in parts if p in {
            "Ironclad", "Silent", "Defect", "Necrobinder", "Regent"}), None)
        key = camel_to_upper_snake(camel)
        zh = zh_by_key.get(key, {})
        entry = envelope(
            key, "relic",
            en_name,  # EN file carries the English name
            body,
            aliases=[camel, en_name],
            play_notes="",
            source=f"md:relics.md:L{line_no}" + (
                f"; {zh['source']}" if zh else ""),
            rarity=rarity,
            character=character,
            counter_shown=key in COUNTER_SHOWN_RELICS if 'COUNTER_SHOWN_RELICS' in dir() else key in {
                "HAPPY_FLOWER", "FISHING_ROD", "PUMPKIN_CANDLE", "GIRYA",
                "PEN_NIB", "NUNCHAKU", "TUNING_FORK", "STONE_CALENDAR",
                "LASTING_CANDY", "LAVA_ROCK", "WONGOS_MYSTERY_TICKET"},
        )
        if zh:
            entry["zh_name"] = zh["name"]
            entry["zh_description"] = zh["description"]
        entries[key] = entry
    return entries


COUNTER_SHOWN_RELICS = {
    "HAPPY_FLOWER", "FISHING_ROD", "PUMPKIN_CANDLE", "GIRYA", "PEN_NIB",
    "NUNCHAKU", "TUNING_FORK", "STONE_CALENDAR", "LASTING_CANDY", "LAVA_ROCK",
    "WONGOS_MYSTERY_TICKET",
}


def parse_powers(md_path: Path, zh_path: Path) -> dict:
    entries = {}
    zh_by_key = {}
    for line_no, text, _ in join_bullets(zh_path):
        m = re.match(r"^([A-Z][A-Z0-9_]*)\s*[（(]([^）)]*)[）)]\s*[:：]\s*(.*)$", text)
        if m:
            pid, meta, body = m.group(1), m.group(2), m.group(3).strip()
            parts = split_meta(meta)
            zh_name = next((p for p in parts if re.search(r"[一-鿿]", p)), "")
            zh_by_key.setdefault(pid, {"name": zh_name, "description": body,
                                        "source": f"md:powers_zh.md:L{line_no}"})
            continue
        m = re.match(r"^([A-Z][A-Z0-9_]*)\s*[:：]\s*(.*)$", text)
        if m:
            pid, body = m.group(1), m.group(2).strip()
            zh_by_key.setdefault(pid, {"name": "", "description": body,
                                        "source": f"md:powers_zh.md:L{line_no}"})

    def add_power(pid: str, ptype: str, stack: str, body: str, line_no: int,
                  aliases=None):
        zh = zh_by_key.get(pid, {})
        counter_class = (pid in COUNTER_CLASS_POWERS
                         or bool(COUNTER_CLASS_RE.search(body)))
        entry = envelope(
            pid, "power",
            name_from_power_id(pid),  # EN name — never the ZH display
            body,
            aliases=aliases or [name_from_power_id(pid).replace(" ", "") + "Power"],
            play_notes="",
            source=f"md:powers.md:L{line_no}" + (f"; {zh['source']}" if zh else ""),
            power_type=ptype or None,
            stack_type=stack or None,
            counter_class=counter_class,
            host_of_affliction=False,
        )
        if zh:
            entry["zh_name"] = zh["name"] or name_from_power_id(pid)
            entry["zh_description"] = zh["description"]
        prev = entries.get(pid)
        if prev is None or (len(prev.get("description", "")) < len(body)
                            and not prev.get("curated")):
            entries[pid] = entry

    meta_re = re.compile(r"^([A-Z][A-Z0-9_]*(?:\s*/\s*[A-Z][A-Z0-9_]*)*)\s*"
                         r"(?:\(([^)]*)\))?\s*[:：]\s*(.*)$")

    def parse_meta(meta):
        ptype = stack = ""
        for tok in split_meta(meta):
            tl = tok.strip()
            if tl in ("Buff", "Debuff"):
                ptype = tl
            elif tl in ("Counter", "Single", "None-stack"):
                stack = tl
        return ptype, stack

    for line_no, text, indent in join_bullets(md_path):
        m = meta_re.match(text)
        if not m:
            continue
        key_part, meta, body = m.group(1).strip(), m.group(2) or "", m.group(3).strip()
        ids = [k.strip() for k in key_part.split("/")
               if re.match(r"^[A-Z][A-Z0-9_]*$", k.strip())]
        if not ids:
            continue
        ptype, stack = parse_meta(meta)
        if re.search(r"\bfamily\b", text) or (
                len(ids) == 1 and re.search(rf"\b{ids[0]}\b\s*,\s*[A-Z_]+", body)):
            member_src = body
            if "—" in body:
                member_src = body.split("—", 1)[0]
            members = [t.strip() for t in re.split(r"[,，/]", member_src)
                       if re.match(r"^[A-Z][A-Z0-9_]*$", t.strip())]
            fam_desc = body.split("—", 1)[-1].strip() if "—" in body else body
            for member in members or ids:
                add_power(member, ptype, stack,
                          f"Member of the {ids[0]} family. {fam_desc}".strip(),
                          line_no)
            if members and ids[0] not in members:
                add_power(ids[0], ptype, stack, body, line_no)
            continue
        for pid in ids:
            add_power(pid, ptype, stack, body, line_no)
    return entries


def parse_cards(md_path: Path, zh_path: Path) -> dict:
    entries = {}
    zh_by_key = {}
    if zh_path.exists():
        for raw in zh_path.read_text(encoding="utf-8").splitlines():
            m = re.match(r"^- ([A-Z][A-Z0-9_]*)（([^）]*)）\s*[:：]\s*(.*)$", raw)
            if not m:
                continue
            cid, zh_name, body = m.group(1), m.group(2).strip(), m.group(3).strip()
            zh_by_key[cid] = {"name": zh_name, "description": body,
                              "source": "md:cards_zh.md"}

    section = ""
    md_lines = md_path.read_text(encoding="utf-8").splitlines() if md_path.exists() else []
    for i, raw in enumerate(md_lines, 1):
        if raw.startswith("## "):
            section = raw[3:].strip()
            continue
        m = re.match(r"^- ([A-Z][A-Z0-9_]*)\s*[:：]\s*(.*)$", raw)
        if not m:
            continue
        cid, body = m.group(1), m.group(2).strip()
        parts = body.split(",", 3)
        cost = card_type = rarity = None
        rest = body
        if len(parts) >= 3:
            cost_tok = parts[0].strip()
            type_tok = parts[1].strip().lower()
            rarity_tok = parts[2].strip().lower()
            if re.match(r"^(X|\-?\d+)$", cost_tok) and type_tok in {
                    "attack", "skill", "power", "status", "curse", "token",
                    "quest", "kind"}:
                cost, card_type, rarity = cost_tok, type_tok, rarity_tok
                rest = parts[3].strip() if len(parts) > 3 else ""
        upgrade = ""
        um = re.search(r"\bUpgrade:\s*(.*)$", rest)
        if um:
            upgrade = um.group(1).strip()
        keywords = [k for k in CARD_KEYWORDS if re.search(rf"\b{re.escape(k)}\b", rest)]
        target = None
        if re.search(r"ALL enemies", rest):
            target = "AllEnemies"
        elif re.search(r"random enemy", rest, re.I):
            target = "RandomEnemy"
        zh = zh_by_key.get(cid, {})
        pool = SECTION_TO_POOL.get(section.lower(), section.upper() or None)
        entry = envelope(
            cid, "card",
            humanize(cid) if not zh.get("name") else humanize(cid),
            rest,
            aliases=[humanize(cid)] + ([zh["name"]] if zh.get("name") else []),
            play_notes="",
            source=f"md:cards.md:L{i}" + ("; md:cards_zh.md" if zh else ""),
            cost=cost,
            card_type=card_type,
            rarity=rarity,
            target_type=target,
            character_pool=pool,
            keywords=keywords,
            upgrade=upgrade or None,
        )
        if zh:
            entry["zh_name"] = zh["name"]
            entry["zh_description"] = zh["description"]
        entries[cid] = entry
    return entries


def potion_display_to_id(display: str) -> str:
    if display in POTION_ID_OVERRIDES:
        return POTION_ID_OVERRIDES[display]
    return re.sub(r"[^A-Za-z0-9]+", "_", display).strip("_").upper()


POTION_RARITIES = {"Common", "Uncommon", "Rare", "Event", "Token", "Special"}


def parse_potions(md_path: Path, zh_path: Path) -> dict:
    entries = {}
    zh_by_display = {}
    for line_no, text, _ in join_bullets(zh_path):
        m = re.match(r"^([^（(]+?)\s*[（(]([^）)]*)[）)]\s*(?:[（(]([^）)]*)[）)])?\s*[:：]\s*(.*)$",
                     text)
        if not m:
            continue
        display = m.group(1).strip()
        zh_name = next((t for t in split_meta(m.group(2) or "")
                        if has_cjk(t)), "")
        meta2 = m.group(3) or ""
        body = m.group(4).strip()
        if not any(p in POTION_RARITIES for p in split_meta(meta2) + split_meta(m.group(2) or "")):
            continue  # not a potion entry (notes bullets)
        zh_by_display[display] = {
            "name": zh_name, "description": body,
            "source": f"md:potions_zh.md:L{line_no}"}

    for line_no, text, _ in join_bullets(md_path):
        m = re.match(r"^(.+?)\s*\(([^)]+)\)\s*[:：]\s*(.*)$", text)
        if not m:
            continue
        display, meta, body = m.group(1).strip(), m.group(2), m.group(3).strip()
        parts = split_meta(meta)
        if not any(p in POTION_RARITIES for p in parts):
            continue  # skip 'Notable code notes' / decode-note bullets
        rarity = next((p for p in parts if p in POTION_RARITIES), None)
        usage = next((p for p in parts if p.lower() in {
            "combat", "anytime", "auto", "event", "combatonly", "any time",
            "automatic"}), None)
        target = next((p for p in parts if p not in (rarity, usage)), None)
        pid = potion_display_to_id(display)
        zh = zh_by_display.get(display, {})
        entry = envelope(
            pid, "potion",
            display,
            body,
            aliases=[display, display.replace(" ", "").replace("'", ""),
                     display.replace(" ", "_").replace("'", "").upper()],
            play_notes="",
            source=f"md:potions.md:L{line_no}" + (f"; {zh['source']}" if zh else ""),
            rarity=rarity,
            usage=usage,
            target=target,
            display_name=display,
        )
        if zh:
            entry["zh_name"] = zh["name"] or display
            entry["zh_description"] = zh["description"]
        entries[pid] = entry
    return entries


def parse_afflictions(md_path: Path, zh_path: Path) -> dict:
    entries = {}
    zh_by_key = {}
    for line_no, text, _ in join_bullets(zh_path):
        m = re.match(r"^([A-Z][A-Z0-9_]*)\s*[（(]([^）)]*)[）)]\s*[:：]\s*(.*)$", text)
        if m:
            key, meta, body = m.group(1), m.group(2), m.group(3).strip()
            zh_name = next((t for t in split_meta(meta) if has_cjk(t)), "")
            zh_by_key[key] = {"name": zh_name, "description": body,
                              "source": f"md:afflictions_zh.md:L{line_no}"}
            continue
        m = re.match(r"^([A-Z][A-Z0-9_]*)\s*[:：]\s*(.*)$", text)
        if m:
            zh_by_key.setdefault(m.group(1), {
                "name": "", "description": m.group(2).strip(),
                "source": f"md:afflictions_zh.md:L{line_no}"})

    section = ""
    md_lines = md_path.read_text(encoding="utf-8").splitlines() if md_path.exists() else []
    for i, raw in enumerate(md_lines, 1):
        if raw.startswith("## "):
            section = raw[3:].strip().lower()
            continue
        m = re.match(r"^- ([A-Z][A-Z0-9_]*)\s*(?:\(([^)]*)\))?\s*[:：]\s*(.*)$", raw)
        if not m:
            continue
        key, meta, body = m.group(1), m.group(2) or "", m.group(3).strip()
        j = i
        while j < len(md_lines):
            nxt = md_lines[j]
            if nxt.startswith("- ") or nxt.startswith("#") or not nxt.strip():
                break
            if nxt.startswith("  "):
                body += " " + nxt.strip()
            j += 1
        meta_l = meta.lower()
        if "related power" in section:
            continue
        if "curse" in section:
            kind = "curse"
        elif "status card" in section or "(status" in meta_l:
            kind = "status_card"
        elif "payoff" in section or "synergy" in section:
            kind = "status_payoff_card"
        else:
            kind = "affliction"
        host = None
        hm = re.search(r"host\s*=\s*([A-Z][A-Z0-9_]*)", body)
        if hm:
            host = hm.group(1)
        zh = zh_by_key.get(key, {})
        entry = envelope(
            key, kind,
            humanize(key),
            body,
            aliases=[humanize(key)] + ([zh["name"]] if zh.get("name") else []),
            play_notes="",
            source=f"md:afflictions.md:L{i}" + (f"; {zh['source']}" if zh else ""),
            host_power_id=host,
        )
        if zh:
            entry["zh_name"] = zh["name"] or humanize(key)
            entry["zh_description"] = zh["description"]
        entries[key] = entry
    return entries


def parse_intents(md_path: Path, zh_path: Path) -> dict:
    entries = {}
    zh_desc = {}
    for line_no, text, _ in join_bullets(zh_path):
        m = re.match(r"^([A-Za-z]+Intent|[A-Z][A-Za-z]+)\s*[（(]([^）)]*)[）)]\s*[:：]\s*(.*)$",
                     text)
        if m:
            zh_desc[m.group(1)] = {"description": m.group(3).strip(),
                                    "source": f"md:intents_zh.md:L{line_no}"}

    class_re = re.compile(r"^([A-Za-z]+Intent)\s*\(([^)]*)\)\s*[:：]\s*(.*)$")
    for line_no, text, _ in join_bullets(md_path):
        m = class_re.match(text)
        if not m:
            continue
        cls, meta, body = m.group(1), m.group(2), m.group(3).strip()
        intent_type = None
        tm = re.search(r"IntentType\.([A-Za-z]+)", meta)
        if tm:
            intent_type = tm.group(1)
        elif "/" in meta:
            intent_type = meta.split("/")[0].strip()
        zh = zh_desc.get(cls, {})
        entry = envelope(
            cls, "intent_class",
            cls,
            body,
            aliases=[intent_type] if intent_type else [],
            play_notes=INTENT_DECISION_RULES.get(cls, ""),
            source=f"md:intents.md:L{line_no}" + (f"; {zh['source']}" if zh else ""),
            intent_type=intent_type,
            label_semantics=body,
            state_fields=INTENT_STATE_FIELDS.get(cls, []),
            decision_rule=INTENT_DECISION_RULES.get(cls, ""),
        )
        if zh:
            entry["zh_description"] = zh["description"]
            entry["zh_play_notes"] = zh["description"]
        entries[cls] = entry

    for type_name, members in INTENT_TYPE_MEMBERS.items():
        zh = zh_desc.get(type_name, {})
        desc = (f"IntentType enum value `{type_name}`. Member intent classes: "
                + ", ".join(members) + ".")
        entry = envelope(
            type_name, "intent_type",
            type_name,
            desc,
            # NOT aliases: member class names are top-level intent_class keys;
            # putting them here made lookup return the type entry for class ids
            aliases=[],
            play_notes=INTENT_DECISION_RULES.get(members[0], "") if members else "",
            source="decomp:IntentType enum (frozen constant; /tmp/sts2-decomp)",
            member_classes=members,
        )
        if zh:
            entry["zh_description"] = (zh["description"] + " 成员类："
                                       + "、".join(members) + "。")
        else:
            entry["zh_description"] = (f"IntentType 枚举值 `{type_name}`。成员意图类："
                                       + "、".join(members) + "。")
        entries[type_name] = entry
    return entries


def parse_characters(md_path: Path, zh_path: Path) -> dict:
    entries = {}
    zh_by_key = {}
    for line_no, text, _ in join_bullets(zh_path):
        m = re.match(r"^([A-Z][A-Z0-9_]*)\s*[（(]?([^—:：]*?)[）)]?\s*[—–-]{1,2}\s*(.*)$",
                     text)
        if not m:
            continue
        key = m.group(1)
        zh_name = next((t for t in CJK_NAME_RE.findall(m.group(2) or "") if t), "")
        zh_by_key[key] = {"name": zh_name, "description": m.group(3).strip(),
                          "source": f"md:characters_zh.md:L{line_no}"}

    for line_no, text, _ in join_bullets(md_path):
        m = re.match(r"^([A-Z][A-Z0-9_]*)\s*[—–-]{1,2}\s*(.*)$", text)
        if not m:
            continue
        key, body = m.group(1), m.group(2).strip()
        hp = None
        hm = re.search(r"(\d+)\s*HP", body)
        if hm:
            hp = int(hm.group(1))
        starter_relic = None
        sm = re.search(r"Starter relic:\s*([A-Z][A-Z0-9_]*)", body)
        if sm:
            starter_relic = sm.group(1)
        pool = None
        pm = re.search(r"([A-Za-z]+CardPool)", body)
        if pm:
            pool = pm.group(1)
        unlocks = None
        um = re.search(r"UnlocksAfterRunAs\s*=>\s*([A-Za-z]+|null)", body)
        if um:
            unlocks = None if um.group(1) == "null" else um.group(1)
        deck = None
        dm = re.search(r"Starter deck\s*\((\d+)\)\s*:\s*([^.]*)", body)
        if dm:
            deck = dm.group(2).strip()
        zh = zh_by_key.get(key, {})
        entry = envelope(
            key, "character",
            humanize(key),
            body,
            aliases=[f"CHARACTER.{key}", humanize(key)]
                    + ([zh["name"]] if zh.get("name") else []),
            play_notes="",
            source=f"md:characters.md:L{line_no}" + (f"; {zh['source']}" if zh else ""),
            hp=hp,
            gold=99,
            starter_relic=starter_relic,
            starter_deck=deck,
            card_pool=pool,
            unlocks_after_run_as=unlocks,
        )
        if zh:
            entry["zh_name"] = zh["name"] or humanize(key)
            entry["zh_description"] = zh["description"]
        entries[key] = entry
    return entries

# ---------------------------------------------------------------------------
# monsters — the rich domain
# ---------------------------------------------------------------------------

def resolve_move_id(token: str, census: set) -> str:
    t = re.sub(r"[^A-Za-z0-9]+", "_", token).strip("_").upper()
    if not t:
        return t
    if t in census:
        return t
    snake = camel_to_upper_snake(token)
    if snake in census:
        return snake
    for base in {t, snake}:
        if base + "_MOVE" in census:
            return base + "_MOVE"
        if base.endswith("_MOVE") and base[: -len("_MOVE")] in census:
            return base[: -len("_MOVE")]
        m = re.match(r"^(.*?)(\d+)$", base)
        if m:
            b, n = m.group(1).rstrip("_"), m.group(2)
            for cand in (f"{b}_MOVE_{n}", f"{b}{n}_MOVE", f"{b}_MOVE{n}",
                         f"{b}_{n}_MOVE", f"{b}_{n}"):
                if cand in census:
                    return cand
    return snake if (snake.endswith("_MOVE") or snake == "STUNNED") else (
        snake + "_MOVE" if snake else t)


def build_move_display_forms(mid: str):
    """SEA_KICK_MOVE -> {'sea kick','seakick','sea_kick',...}; THRASH_MOVE_2 -> thrash 2."""
    m = re.match(r"^(.*?)(?:_MOVE)?(?:_(\d+))?$", mid)
    base = m.group(1) if m else mid
    num = m.group(2) if m else None
    human = base.replace("_", " ").title()
    forms = {human.lower(), human.replace(" ", "").lower(),
             base.replace("_", "").lower(), base.lower()}
    if num:
        forms |= {f"{human} {num}".lower(), f"{human}{num}".lower(),
                  f"{base} {num}".lower(), f"{base}_{num}".lower()}
    return forms


def move_tokens_in(text: str, census: set):
    found = []
    for m in re.finditer(r"\b([A-Z][A-Z0-9_]{2,})\b", text):
        tok = m.group(1)
        if tok in STOP_TOKENS or tok.endswith("_POWER"):
            continue
        is_candidate = (
            tok in census or tok == "STUNNED" or tok.endswith("_MOVE")
            or re.match(r"^.*_MOVE_\d+$", tok)
            or re.search(rf"\b{re.escape(tok)}\s*=", text)
        )
        if not is_candidate:
            continue
        rid = resolve_move_id(tok, census)
        found.append((m.start(), m.end(), rid, tok))
    # CamelCase display names before a digit/equals: "Glomp 8", "WhipSlap 3x2"
    for m in re.finditer(r"\b([A-Z][a-z]+(?:[A-Z][a-z0-9]+)+)\b(?=\s*(?:\d|[=x×]))",
                         text):
        rid = resolve_move_id(m.group(1), census)
        if rid in census or rid.endswith("_MOVE"):
            found.append((m.start(), m.end(), rid, m.group(1)))
    # reverse display-form scan against census (free-form prose cycles)
    if census:
        low = text.lower()
        for mid in census:
            for form in build_move_display_forms(mid):
                if len(form) < 4 or form in STOP_TOKENS:
                    continue
                for m in re.finditer(r"(?<![a-z0-9_])" + re.escape(form)
                                     + r"(?![a-z0-9_])", low):
                    # avoid double-counting positions already claimed
                    found.append((m.start(), m.end(), mid, text[m.start():m.end()]))
    found.sort()
    dedup = []
    for item in found:
        if dedup and item[0] < dedup[-1][1]:
            # keep the longer/resolved-census version
            prev = dedup[-1]
            if item[2] in census and prev[2] not in census:
                dedup[-1] = item
            continue
        dedup.append(item)
    return dedup


def parse_move_effect(seg: str) -> dict:
    seg = seg.strip().strip("；;。，, ")
    out = {"effect": seg, "intents": [], "display_note": None,
           "base_damage": None, "base_damage_ascension": None,
           "status_count": None, "hits": None}
    if not seg:
        return out
    low = seg.lower()
    multi = re.search(r"multi(?:-|\s)?attack\s*(\d+)\s*(?:\((A:\s*\d+)\))?\s*[x×]\s*(\d+)",
                      seg, re.I)
    single = re.search(r"single(?:-|\s)?attack\s*(\d+)\s*(?:\((A:\s*\d+)\))?", seg, re.I)
    if not single:
        single = re.search(r"(?:attack|单段攻击|=\s*)\s*(\d+)\s*(?:\((A:\s*\d+)\))?", seg)
    status = re.search(r"status(?:\s*(?:cards?|牌))?\s*[×x]\s*(\d+)", seg, re.I)
    # free-form "Glomp 8" / "Whirl 7" / "SEA_KICK(11, A:13)" patterns
    bare = re.search(r"(?:^|[\s>→])(\d+)\s*(?:\((A:\s*\d+)\))?(?:\s*[x×]\s*(\d+))?", seg)
    if multi:
        dmg, hits, asc = int(multi.group(1)), int(multi.group(3)), multi.group(2)
        out["intents"].append({"class": "MultiAttackIntent", "type": "Attack",
                               "base_damage": dmg, "hits": hits,
                               "base_damage_ascension":
                                   int(asc.split(":")[1]) if asc else None})
        out["base_damage"] = dmg
        out["hits"] = hits
        out["display_note"] = f"{dmg}x{hits}"
        if asc:
            out["base_damage_ascension"] = int(asc.split(":")[1])
    elif single:
        dmg = int(single.group(1))
        asc = single.group(2)
        out["intents"].append({"class": "SingleAttackIntent", "type": "Attack",
                               "base_damage": dmg, "hits": 1,
                               "base_damage_ascension":
                                   int(asc.split(":")[1]) if asc else None})
        out["base_damage"] = dmg
        out["display_note"] = str(dmg)
        if asc:
            out["base_damage_ascension"] = int(asc.split(":")[1])
    elif bare and re.search(r"damage|attack|hit|dmg|伤", low):
        dmg = int(bare.group(1))
        hits = int(bare.group(3)) if bare.group(3) else 1
        out["base_damage"] = dmg
        out["hits"] = hits if hits > 1 else None
        cls = "MultiAttackIntent" if (bare.group(3) or re.search(r"[x×]\s*\d", seg)) \
            else "SingleAttackIntent"
        out["intents"].append({"class": cls, "type": "Attack",
                               "base_damage": dmg, "hits": hits})
        out["display_note"] = f"{dmg}x{hits}" if hits > 1 else str(dmg)
        if bare.group(2):
            out["base_damage_ascension"] = int(bare.group(2).split(":")[1])
    elif status:
        out["intents"].append({"class": "StatusIntent", "type": "StatusCard",
                               "status_count": int(status.group(1))})
        out["status_count"] = int(status.group(1))
        out["display_note"] = f"status x{status.group(1)}"
    if re.search(r"\bbuff\b|增益", low):
        out["intents"].append({"class": "BuffIntent", "type": "Buff"})
    if re.search(r"\bdebuff\b|减益", low):
        out["intents"].append({"class": "DebuffIntent", "type": "Debuff"})
    if re.search(r"\bdefend\b|格挡|block", low):
        out["intents"].append({"class": "DefendIntent", "type": "Defend"})
    if re.search(r"\bsummon|召唤", low):
        out["intents"].append({"class": "SummonIntent", "type": "Summon"})
    if re.search(r"\bstun|击晕|眩晕", low):
        out["intents"].append({"class": "StunIntent", "type": "Stun"})
    if re.search(r"\bsleep|沉睡|睡眠", low):
        out["intents"].append({"class": "SleepIntent", "type": "Sleep"})
    if re.search(r"\bheal|回复|治疗", low):
        out["intents"].append({"class": "HealIntent", "type": "Heal"})
    if re.search(r"\bescape|逃跑|逃离", low):
        out["intents"].append({"class": "EscapeIntent", "type": "Escape"})
    return out


MONSTER_KEY_BLOCKLIST = {
    "Three", "After", "While", "Where", "These", "Those", "Their", "There",
    "Other", "Every", "Never", "Always", "Before", "Under", "Above", "Notes",
    "Note", "Elite", "Boss", "Normal", "Class", "Variant", "Spawn", "Pair",
    "With", "From", "Into", "Only", "Both", "Same", "Live", "Data", "Name",
    "Body", "Move", "Moves", "Cycle", "Passive", "Passives", "Intent",
    "Intents", "Once", "Each", "Turn", "Start", "Combat", "Attack", "Buff",
    "Debuff", "Defend", "Heal", "Sleep", "Stun", "Summon", "Escape", "Hidden",
    "Unknown", "Death", "Blow", "Multi", "Single", "Target", "Player",
    "Enemy", "Allies", "Owner", "Amount", "Counter", "Stack", "Power",
    "Powers", "Damage", "Block", "Strength", "Dexterity", "Poison", "Doom",
    "Disintegration", "MindRot", "WasteAway", "Sloth", "SteamEruption",
    "Setting", "Choose", "Option", "Reward", "First", "Second", "Third",
    "Continue", "Repeat", "Back", "Loop", "Branch", "Random", "Cannot",
    "Master", "Minion", "Add", "Adds", "Wave", "Kill", "Death",
    "Ruby", "Ritual", "Cultist", "Cultists", "Knight", "Knights", "Trio",
}


def valid_monster_key(tok: str) -> bool:
    if not tok or len(tok) < 4 or tok in STOP_TOKENS:
        return False
    if not re.match(r"^[A-Z][A-Za-z0-9]+$", tok):
        return False
    if re.match(r"^Act\d", tok) or tok.endswith("Power"):
        return False
    if re.match(r"^\d", tok) or tok in MONSTER_KEY_BLOCKLIST:
        return False
    # multi-hump CamelCase, digit-bearing ids, or single-hump class names
    # (Inklet / Nibbit / Fogmog / Crusher / Tunneler ... are all 1 capital)
    capitals = sum(1 for c in tok if c.isupper())
    if capitals >= 2 or any(c.isdigit() for c in tok):
        return True
    # single-hump: accept lowercase-rest class names, reject PROSE-like tokens
    return bool(re.match(r"^[A-Z][a-z]+$", tok))


def split_paren_bullet(text: str):
    """'Name (meta): body' with nested parens tolerated. None if not shaped."""
    m = re.match(r"^([^(（]*?)\s*([（(])(.*)$", text)
    if not m:
        return None
    display = m.group(1).strip()
    open_ch = m.group(2)
    close_ch = "）" if open_ch == "（" else ")"
    rest = m.group(3)
    depth = 1
    close_idx = -1
    for idx, ch in enumerate(rest):
        if ch == open_ch:
            depth += 1
        elif ch == close_ch:
            depth -= 1
            if depth == 0:
                close_idx = idx
                break
    if close_idx < 0:
        return None
    meta = rest[:close_idx]
    after = rest[close_idx + 1:]
    bm = re.match(r"^\s*[:：]\s*(.*)$", after)
    if not bm:
        return None
    return display, meta, bm.group(1).strip()


def extract_monster_keys(display: str, meta: str, body: str, census=None):
    census = census or set()
    keys, zh_names = [], []
    # display-side identifiers: "KaiserCrab 皇蟹", "Coral Cluster / Skulking Colony",
    # "BattleFriendV1/V2/V3 战斗好伙伴"
    disp_head = display.strip()
    vmatch = re.match(r"^([A-Za-z][A-Za-z0-9]+)(V\d+)((?:\s*/\s*V?\d+)+)", disp_head)
    if vmatch:
        stem = vmatch.group(1)
        for part in re.findall(r"V?(\d+)", vmatch.group(0)):
            keys.append(f"{stem}V{part}")
    for part in re.split(r"/", disp_head):
        words = re.findall(r"[A-Za-z][A-Za-z0-9]+", part)
        if not words:
            continue
        if len(words) == 1:
            if valid_monster_key(words[0]):
                keys.append(words[0])
        else:
            if all(w[0].isupper() for w in words):
                joined = "".join(words)
                if valid_monster_key(joined):
                    keys.append(joined)
            if valid_monster_key(words[0]):
                keys.append(words[0])
    # meta encounter/model tokens — only accept if present in body/display too
    meta_head = re.split(r"[,;]", meta)[0].strip() if meta else ""
    if meta_head and re.match(r"^[A-Za-z0-9/]+$", meta_head) and "/" in meta_head:
        parts = [p for p in meta_head.split("/") if p]
        if parts and len(parts[0]) > 6:
            # DecimillipedeSegmentBack/Front/Middle -> stem = longest shared
            # prefix of humps: DecimillipedeSegment + Back/Front/Middle
            stem_m = re.match(r"^(.*(?:[A-Z][a-z]+)+?)([A-Z][a-z]+)$", parts[0])
            stem = stem_m.group(1) if stem_m else parts[0]
            for idx, part in enumerate(parts):
                cand = part if idx == 0 else stem + part
                if valid_monster_key(cand):
                    keys.append(cand)
    meta_first = re.match(r"^\s*([A-Za-z][A-Za-z0-9]+)", meta or "")
    if meta_first:
        tok = meta_first.group(1)
        stripped = re.sub(r"(Normal|Weak|Elite|Boss|Encounter|Class)$", "", tok)
        for cand in (stripped, tok):
            if valid_monster_key(cand) and (
                    re.search(rf"\b{re.escape(cand)}\b", display or "")
                    or cand == tok or cand == stripped):
                keys.append(cand)
                break
    # sub-monsters named in body followed by a move token
    for m in re.finditer(
            r"\b([A-Z][a-z]+(?:[A-Z][A-Za-z0-9]+)+)\b\s+([A-Z][A-Z0-9_/]*)",
            body or ""):
        tok = m.group(1)
        follower = (m.group(2) or "").split("/")[0]
        if not valid_monster_key(tok):
            continue
        ok = (follower in census or follower == "STUNNED"
              or follower.endswith("_MOVE")
              or bool(re.match(r"^[A-Z][A-Z0-9_]*_\d+$", follower))
              or bool(re.match(r"^[A-Z][A-Z0-9_]*_(SHOT|SWING|MOVE|BLAST)$", follower))
              or bool(re.search(rf"\b{re.escape(follower)}\s*=", body or "")))
        if ok:
            keys.append(tok)
    for zm in CJK_NAME_RE.findall(display + " " + (meta or "")):
        zh_names.append(zm)
    out, seen = [], set()
    for k in keys:
        if k not in seen:
            out.append(k)
            seen.add(k)
    return out, zh_names


def build_monster_entry(key: str, display: str, zh_name: str, body: str,
                        census: set, line_no: int, source_md: str,
                        zh_body: str = None) -> dict:
    hp_base = hp_notes = None
    hm = re.search(r"(\d+)\s*(?:[–\-/]|to)\s*(\d+)\s*HP", body)
    if hm:
        hp_base, hp_notes = int(hm.group(1)), f"{hm.group(1)}–{hm.group(2)} HP range"
    else:
        hm = re.search(r"(\d+)\s*HP", body)
        if hm:
            hp_base = int(hm.group(1))
    acts = sorted({f"Act{a}" for a in re.findall(r"\bAct\s*([1-4])\b", body)})
    is_boss = bool(re.search(r"\bBoss\b", body, re.I))
    moves = {}
    zh_moves = {}
    tokens = move_tokens_in(body, census)
    zh_tokens = move_tokens_in(zh_body, census) if zh_body else []
    for idx, (start, end, rid, raw_tok) in enumerate(tokens):
        seg_end = tokens[idx + 1][0] if idx + 1 < len(tokens) else len(body)
        seg = body[end:seg_end].lstrip(" =:：-—").strip()
        info = parse_move_effect(seg)
        mv = envelope(
            rid, "move",
            humanize(re.sub(r"_MOVE(_\d+)?$", "", rid)),
            info["effect"] or f"{rid} — performed by {key}; see cycle.",
            aliases=sorted({raw_tok, humanize(raw_tok)} - {rid}),
            play_notes="",
            source=f"md:{source_md}:L{line_no}",
            monster_id=key,
            intents=info["intents"],
            base_damage=info["base_damage"],
            base_damage_ascension=info["base_damage_ascension"],
            hits=info["hits"],
            status_count=info["status_count"],
            display_note=info["display_note"],
        )
        prev = moves.get(rid)
        if prev is None or len(prev.get("description", "")) < len(mv["description"]):
            moves[rid] = mv
    for idx, (start, end, rid, raw_tok) in enumerate(zh_tokens):
        seg_end = zh_tokens[idx + 1][0] if idx + 1 < len(zh_tokens) else len(zh_body)
        seg = zh_body[end:seg_end].lstrip(" =:：-—").strip()
        if seg and rid not in zh_moves:
            zh_moves[rid] = seg
    # reverse-scan moves may appear in prose cycles without ALLCAPS — also run
    # display-form claims for census ids mentioned in body
    for mid in census:
        if mid in moves:
            continue
        for form in build_move_display_forms(mid):
            if len(form) < 4:
                continue
            m = re.search(r"(?<![a-z0-9_])" + re.escape(form)
                          + r"(?![a-z0-9_])", body.lower())
            if m:
                # segment: from match to next move mention or end
                rest = body[m.end():]
                seg = re.split(r"[→>]|repeat|循环", rest)[0]
                info = parse_move_effect(seg)
                desc = info["effect"] or body.strip()
                moves[mid] = envelope(
                    mid, "move", humanize(re.sub(r"_MOVE(_\d+)?$", "", mid)),
                    desc[:400],
                    aliases=[humanize(mid)],
                    source=f"md:{source_md}:L{line_no}",
                    monster_id=key,
                    intents=info["intents"],
                    base_damage=info["base_damage"],
                    base_damage_ascension=info["base_damage_ascension"],
                    hits=info["hits"], status_count=info["status_count"],
                    display_note=info["display_note"],
                )
                break
    cycle = []
    for cm in re.finditer(r"[Cc]ycle[:\s]*([^.;]+)|循环[:：]?\s*([^。;]+)", body):
        chunk = cm.group(1) or cm.group(2) or ""
        for part in re.split(r"[→>➜\s]+", chunk):
            part = part.strip().strip("….,;，。")
            if not part or part.lower() in {"and", "repeat", "back", "to", "循环"}:
                continue
            if re.match(r"^[A-Za-z]", part):
                rid = resolve_move_id(part, census)
                if rid and rid not in cycle:
                    cycle.append(rid)
    passives = []
    seen_pass = set()

    def add_passive(name, amount, desc):
        pid = camel_to_upper_snake(name)
        if not pid.endswith("_POWER") and pid not in {"POISON"}:
            pid = pid + "_POWER" if "POWER" not in pid else pid
        if pid in seen_pass:
            return
        seen_pass.add(pid)
        passives.append({
            "power_id": pid,
            "amount": int(amount) if amount else None,
            "counter_class": pid in COUNTER_CLASS_POWERS,
            "description": desc.strip() or f"{pid} — see powers.json.",
        })

    for pm in re.finditer(
            r"(?:Passive|Passives|passive|spawn passive|被动)\s+"
            r"([A-Za-z][A-Za-z0-9]*)\s*(?:Power)?(?:\s*(\d+))?"
            r"(?:\s*[/,]\s*([A-Za-z][A-Za-z0-9]*)\s*(?:Power)?(?:\s*(\d+))?)?"
            r"\s*[:：\-—]?\s*([^.;]*)", body):
        add_passive(pm.group(1), pm.group(2), pm.group(5))
        if pm.group(3):
            add_passive(pm.group(3), pm.group(4), pm.group(5))
    for pm in re.finditer(r"\b([A-Z][a-zA-Z0-9]+Power)(?:\s*(\d+))?", body):
        add_passive(pm.group(1), pm.group(2), "")
    aliases = sorted({display.strip(), key} | set(zh_name and [zh_name] or [])
                     | {humanize(key)} | {a for a in
                        (CREATURE_NAME_TO_KEY.get(zh_name) and [zh_name] or [])
                        if a})
    # attach every live display name that maps to this key
    for zh_display, mapped in CREATURE_NAME_TO_KEY.items():
        if mapped == key:
            aliases.append(zh_display)
    entry = envelope(
        key, "monster",
        key if not has_cjk(display) else key,  # EN name = class id
        body,
        aliases=sorted({a for a in aliases if a}),
        play_notes="",
        source=f"md:{source_md}:L{line_no}",
        acts=acts,
        hp={"base": hp_base, "notes": hp_notes},
        is_boss=is_boss,
        passives=passives,
        cycle=cycle,
        moves=moves,
        display_names=sorted({display.strip()} | ({zh_name} if zh_name else set())),
    )
    if zh_name:
        entry["zh_name"] = zh_name
    if zh_body:
        entry["zh_description"] = zh_body
    if zh_moves:
        entry["zh_moves"] = zh_moves
    return entry


def parse_monsters(md_path: Path, zh_path: Path, census: set) -> dict:
    entries: dict[str, dict] = {}
    zh_bodies: dict[str, dict] = {}

    def upsert(entry: dict):
        key = entry["id"]
        prev = entries.get(key)
        if prev is None:
            entries[key] = entry
            return
        merged = dict(prev)
        if len(entry.get("description", "")) > len(prev.get("description", "")):
            merged["description"] = entry["description"]
            merged["source"] = entry["source"]
        moves = dict(prev.get("moves") or {})
        for mk, mv in (entry.get("moves") or {}).items():
            pm = moves.get(mk)
            if pm is None or len(mv.get("description", "")) > len(
                    pm.get("description", "")):
                moves[mk] = mv
        merged["moves"] = moves
        zh_moves = dict(prev.get("zh_moves") or {})
        zh_moves.update(entry.get("zh_moves") or {})
        if zh_moves:
            merged["zh_moves"] = zh_moves
        pas = list(prev.get("passives") or [])
        seen = {p.get("power_id") for p in pas}
        for p in entry.get("passives") or []:
            if p.get("power_id") not in seen:
                pas.append(p)
                seen.add(p.get("power_id"))
        merged["passives"] = pas
        if entry.get("cycle") and not prev.get("cycle"):
            merged["cycle"] = entry["cycle"]
        if (entry.get("hp") or {}).get("base") and not (prev.get("hp") or {}).get("base"):
            merged["hp"] = entry["hp"]
        merged["aliases"] = sorted(set(prev.get("aliases") or [])
                                   | set(entry.get("aliases") or []))
        for f in ("zh_name", "zh_description"):
            if entry.get(f) and not prev.get(f):
                merged[f] = entry[f]
        entries[key] = merged

    # ZH body index — ident -> {name, body}; CJK-name regex must not swallow Latin
    for path in (zh_path, md_path):
        if not path.exists():
            continue
        for line_no, text, _ in join_bullets(path):
            m = re.match(r"^([A-Za-z][A-Za-z0-9]*)\s*(.*)$", text)
            if not m:
                continue
            ident = m.group(1)
            rest = m.group(2)
            zh_name = ""
            cm = CJK_NAME_RE.search(rest[:40])
            if cm:
                zh_name = cm.group(0)
            body_m = re.search(r"[:：]\s*(.*)$", rest)
            zbodies = zh_bodies.setdefault(ident, {"name": "", "body": "", "line": line_no})
            if path == zh_path:
                if zh_name and not zbodies.get("name"):
                    zbodies["name"] = zh_name
                if body_m and body_m.group(1).strip():
                    zbodies["body"] = body_m.group(1).strip()
                    zbodies["line"] = line_no
            CREATURE_NAME_TO_KEY.setdefault(zh_name, ident) if zh_name else None

    # name-mapping pairs (EN ZH) anywhere in either file
    for path in (md_path, zh_path):
        if not path.exists():
            continue
        text_all = path.read_text(encoding="utf-8")
        for m in re.finditer(r"\b([A-Z][A-Za-z0-9]{2,})\s+([一-鿿][一-鿿·、]{0,10})",
                             text_all):
            CREATURE_NAME_TO_KEY.setdefault(m.group(2), m.group(1))

    bullet_re = re.compile(r"^([^(（]*?)\s*[（(]([^）)]+)[）)]\s*[:：]\s*(.*)$")
    loose_re = re.compile(
        r"^([A-Za-z][A-Za-z0-9]*)\s*(?:[一-鿿][^:：]*)?\s*[:：]\s*(.*)$")

    skip_sections = ("name mapping", "power quick reference", "act pools",
                     "format", "power effects")

    for path, is_zh in ((md_path, False), (zh_path, True)):
        if not path.exists():
            continue
        lines = path.read_text(encoding="utf-8").splitlines()
        section = ""
        i = 0
        while i < len(lines):
            raw = lines[i]
            i += 1
            if raw.startswith("## ") or raw.startswith("### "):
                section = raw.lstrip("#").strip().lower()
                continue
            if any(s in section for s in skip_sections):
                continue
            m = re.match(r"^(\s*)-\s+(.*)$", raw)
            if not m:
                continue
            indent = len(m.group(1))
            text = m.group(2).rstrip()
            while i < len(lines):
                nxt = lines[i]
                if re.match(r"^\s*-\s+", nxt) or nxt.startswith("#") or not nxt.strip():
                    break
                if nxt.startswith("  ") or nxt.startswith("\t"):
                    text += " " + nxt.strip()
                    i += 1
                else:
                    break
            bm = split_paren_bullet(text) or bullet_re.match(text)
            if bm:
                if isinstance(bm, tuple):
                    display, meta, body = bm
                else:
                    display, meta, body = bm.group(1).strip(), bm.group(2), bm.group(3).strip()
                keys, zh_names = extract_monster_keys(display, meta, body, census)
                zh_name = next((z for z in zh_names if has_cjk(z)), "")
                for k in keys:
                    zb = zh_bodies.get(k) or {}
                    body_use = body if not is_zh else body
                    zh_body_use = zb.get("body") if not is_zh else None
                    if is_zh:
                        zh_body_use = body
                    entry = build_monster_entry(
                        k, display, zb.get("name") or zh_name or "",
                        body_use, census, i, path.name,
                        zh_body=zh_body_use if not is_zh else None)
                    if is_zh and body:
                        entry["zh_description"] = body
                        if zb.get("name") or zh_name:
                            entry["zh_name"] = zb.get("name") or zh_name
                    upsert(entry)
                continue
            lm = loose_re.match(text)
            if lm:
                display, body = lm.group(1).strip(), lm.group(2).strip()
                if not body or display in STOP_TOKENS:
                    continue
                keys, zh_names = extract_monster_keys(display, "", body, census)
                zh_name = next((z for z in zh_names if has_cjk(z)), "")
                for k in keys:
                    zb = zh_bodies.get(k) or {}
                    entry = build_monster_entry(
                        k, display, zb.get("name") or zh_name or "",
                        body, census, i, path.name,
                        zh_body=(zb.get("body") if not is_zh else body) or None)
                    if is_zh:
                        entry["zh_description"] = body
                        entry["zh_name"] = zb.get("name") or zh_name or entry.get("zh_name")
                    upsert(entry)

    # register live creature display names as aliases
    for zh_display, key in list(CREATURE_NAME_TO_KEY.items()):
        target = entries.get(key)
        if target is not None:
            target["aliases"] = sorted(set(target.get("aliases") or []) | {zh_display})

    # alias + junk cleanup: drop prose fragments and paren-laden captures
    prose_alias = re.compile(r"[（）()/#]|^(召唤|组队|出生|精英|失衡|多阶段|同模式|"
                             r"可阻止继续召唤|存活时盾使用|由雾菇召唤|红宝石劫掠者系|"
                             r"每次增益循环抬升其力量)$")
    for key, ent in list(entries.items()):
        clean = []
        for a in ent.get("aliases") or []:
            a = str(a).strip()
            if not a:
                continue
            # live display names from the census survive any prose filter —
            # lookup must resolve whatever the wire actually emits — unless
            # this display name canonically belongs to a DIFFERENT monster key
            if a in CREATURE_NAME_TO_KEY:
                if CREATURE_NAME_TO_KEY[a] in (key, None):
                    clean.append(a)
                continue
            if prose_alias.search(a):
                continue
            if has_cjk(a) and len(a) > 8:
                continue
            if len(a) > 40:
                continue
            clean.append(a)
        ent["aliases"] = sorted(set(clean) | {key})
    ZH_MONSTER_FIXUPS = {
        "SEAPUNK": ("海洋混混",
                    "live model_id=SEAPUNK（档案旧名 CorpseSlug；约 44-46 HP，升格 "
                    "47-49）。循环：SEA_KICK_MOVE（单段攻击 11，A:13）→ "
                    "SPINNING_KICK_MOVE（多段 2x4）→ BUBBLE_BURP_MOVE（2 意图）→ "
                    "循环。被动 RAVENOUS_POWER：同侧盟友死亡且自身存活时自晕进入吞噬"
                    "招式并获得 +Amount 力量——每回合一杀即对幸存者开免费晕窗。教条："
                    "利用盟友死亡晕窗打击杀节奏；live 意图可高于表值。"),
        "CALCIFIED_CULTIST": ("钙化邪教徒",
                              "live model_id=CALCIFIED_CULTIST（38-41 HP）。循环："
                              "INCANTATION_MOVE（增益——RITUAL_POWER 自身 +2）→ "
                              "DARK_STRIKE_MOVE（单段攻击 9，A:11）→ 循环。仪式每轮"
                              "增益循环抬升力量——在滚雪球前击杀；竞速教条。"),
        "GremlinMerc": ("地精佣兵",
                        "地精佣兵：THIEVERY_POWER 每回合偷取玩家 20 金；死亡时 "
                        "SurprisePower 生成卑鄙地精（11 HP）+ 胖地精（17 HP），两者"
                        "携带 HEIST_POWER、意图 Escape，1 HP 逃脱无奖励。死后假人模式："
                        "999999999 HP + Stun 意图，EXPLODE 死亡打击约 51 基础 / A1 36"
                        "（可用格挡吃下；EXPLODE 后战斗结束）。"),
        "RubyRaiders": ("红宝石劫掠者",
                        "红宝石劫掠者小队（Act1 RubyRaidersNormal）：刺客 KILLSHOT 10"
                        "（A:11，18-23 HP）；斧手 SWING_1/2 单段 5+5 格挡（A:6）、"
                        "BIG_SWING 12（A:13，20-22 HP）；暴徒 BEAT 7（A:8）、ROAR "
                        "自身+3 力量（30-33 HP）；弩手 FIRE 14（A:16）、RELOAD 防御"
                        "（18-21 HP）；追踪手 TRACK 减益 2 脆弱、HOUNDS 多段 1x8"
                        "（A:9，21-25 HP）。优先击杀暴徒/弩手的高伤意图。"),
        "TerrorEel": ("骇鳗",
                      "骇鳗类精英（~140 HP）：SHRIEK_POWER——未格挡伤害跨过其 HP 区间"
                      "时自晕（其大招回合被吞掉）；下一回合击杀。先压血线到区间下方再"
                      "打未格挡命中触发晕窗。"),
        "ThreeKnights": ("三骑士",
                         "Act3 三骑士精英（连枷骑士 FlailKnight 101 HP / 幽灵骑士 "
                         "SpectralKnight 93 HP / 魔法骑士 MagiKnight 82 HP）——见各"
                         "骑士条目。"),
        "generic": ("共享招式",
                    "共享/未归属的 live 招式 id。当没有怪物条目认领时 lookup 在此解析"
                    "——折叠进对应怪物条目前以 live state 的意图字段为权威。"),
        "Decimillipede": ("残杀千足虫",
                          "残杀千足虫（Act2 DecimillipedeElite；各节段基础 40-46 HP）："
                          "节段 DecimillipedeSegmentBack/Front/Middle。招式：WRITHE_MOVE "
                          "多段 5x2（A:6）；CONSTRICT_MOVE 单段 8（A:9）+1 虚弱；"
                          "BULK_MOVE 单段 6（A:7）+自身 2 力量；REATTACH_MOVE 治疗；"
                          "DEAD_MOVE 死亡态。被动 ReattachPower 25：节段死亡而他段存活时"
                          "进入 DEAD（不可选中），回合结束若仍有活段则回贴并治疗 25——"
                          "全部其他节段死亡时整组消亡。同窗清段是击杀条件；0 HP DEAD 段"
                          "不可选中，不要对其出招。"),
        "AxeRubyRaider": ("红宝石劫掠者·斧手",
                           "红宝石劫掠者斧手（Act1 RubyRaidersNormal；20-22 HP）："
                           "SWING_1/SWING_2 = 单段攻击 5（A:6）+自身 5 格挡（A:6）；"
                           "BIG_SWING = 单段攻击 12（A:13）。"),
        "SnappingJaxfruit": ("闪光贾克斯果",
                             "闪光贾克斯果（Act1 SnappingJaxfruitNormal，与飞蝇菌子同场；"
                             "31-33 HP）：ENERGY_ORB_MOVE = 单段攻击 3（A:4）+自身 2 力量；"
                             "每回合重复——力量滚雪球，尽早击杀。"),
        "CORPSE_SLUG": ("尸体蛞蝓",
                        "尸体蛞蝓（codex CORPSE_SLUG；25-27 HP，升格 27-29）：与 "
                        "SEAPUNK（海洋混混，44-46 HP）是不同怪物——档案旧文曾混用 "
                        "CorpseSlug 名称。招式 WHIP_SLAP 系；携带吞噬类机制的以 "
                        "SEAPUNK 条目为准。招式 id 与数值以 live state 意图字段校对。"),
        "AXEBOT": ("巨斧机器人",
                   "巨斧机器人（StockPower 死亡生成机器人链）：持有者死亡且 Amount>0 时"
                   "在同槽位生成，StockAmount=Amount-1；链上充能未尽时战斗不结束。"
                   "生成 HP 不保证满血。参见 Axebot 条目。"),
        "OSTY": ("奥斯提",
                 "奥斯提（亡灵契约师宠物召唤物）：缚魂命匣战斗开始召唤 1 只；Osty 攻击"
                 "喂骨笛与 NECRO_MASTERY_POWER。死亡不结束战斗。参见 Osty 条目。"),
        "BattlewornDummy": ("战痕训练假人",
                            "战痕假人事件（BATTLEWORN_DUMMY，Act3）的陪练假人统称："
                            "BattleFriendV1/V2/V3 = 战斗好伙伴 1/2/3（单人 Act3 固定 "
                            "75/150/300 HP）。招式 NOTHING_MOVE 从不攻击；生成 "
                            "BATTLEWORN_DUMMY_TIME_LIMIT_POWER 3——假人阵营回合结束"
                            "递减，到 1 时逃跑且无奖励。纯 DPS 竞速；奖励见各 V 条目。"),
    }
    for key, (zh_name, zh_desc) in ZH_MONSTER_FIXUPS.items():
        ent = entries.get(key)
        if ent is not None:
            ent["zh_name"] = zh_name
            ent["zh_description"] = zh_desc
            ent.setdefault("aliases", [])
            if zh_name not in ent["aliases"]:
                ent["aliases"] = sorted(set(ent["aliases"]) | {zh_name})
    # drop non-curated junk keys (empty description and no moves)
    for key in list(entries):
        ent = entries[key]
        if ent.get("curated"):
            continue
        if not (ent.get("description") or "").strip() and not (ent.get("moves") or {}):
            del entries[key]
    # non-curated archive keys that a curated entry already aliases -> drop
    curated_aliases = set()
    for ent in entries.values():
        if ent.get("curated"):
            curated_aliases.update(ent.get("aliases") or [])
    for key in list(entries):
        if entries[key].get("curated"):
            continue
        if key in curated_aliases:
            del entries[key]

    # merge duplicate Decimillipede slash-expansion artifacts into canonical keys
    seg_fix = {
        "DecimillipedeSegmentBackFront": "DecimillipedeSegmentFront",
        "DecimillipedeSegmentBackMiddle": "DecimillipedeSegmentMiddle",
    }
    for bad, good in seg_fix.items():
        if bad in entries:
            if good not in entries:
                entries[good] = entries[bad]
                entries[good]["id"] = good
            del entries[bad]

    # generic holder for census move ids not claimed by any monster
    claimed = set()
    for ent in entries.values():
        claimed.update((ent.get("moves") or {}).keys())
    unclaimed = sorted(census - claimed)
    if unclaimed:
        generic = entries.get("generic") or envelope(
            "generic", "monster", "Generic shared moves",
            "Shared/unassigned live move ids. Lookup resolves them here when no "
            "monster entry claims them — treat live intent fields in state as "
            "authoritative until folded into a monster entry.",
            aliases=["generic", "shared"],
            source="generator:synthesized",
            acts=[], hp={"base": None, "notes": None}, is_boss=False,
            passives=[], cycle=[], moves={},
            zh_description=(
                "共享/未归属的 live 招式 id。当没有怪物条目认领时 lookup 在此解析"
                "——折叠进对应怪物条目前以 live state 的意图字段为权威。"),
            zh_name="共享招式",
        )
        gmoves = dict(generic.get("moves") or {})
        for move_id in unclaimed:
            gmoves[move_id] = envelope(
                move_id, "move",
                humanize(re.sub(r"_MOVE(_\d+)?$", "", move_id)),
                f"{move_id} — live move id seen in run logs; not yet attributed "
                f"to a monster entry in monsters.json. Resolve intent fields "
                f"(damage/hits/description) from the live state; fold the "
                f"effect into the owning monster entry when identified.",
                aliases=[humanize(move_id)],
                play_notes="",
                source="census:live_ids.json",
                monster_id=None,
                intents=[], base_damage=None, base_damage_ascension=None,
                hits=None, status_count=None, display_note=None,
            )
        generic["moves"] = gmoves
        entries["generic"] = generic
    return entries


# ---------------------------------------------------------------------------
# events
# ---------------------------------------------------------------------------

def humanize_option_key(option_key: str) -> str:
    return humanize(option_key.rsplit(".", 1)[-1])


def norm_token(s: str) -> str:
    return re.sub(r"[^A-Z0-9]", "", s.upper())


def parse_events(md_path: Path, zh_path: Path, live_ids: dict,
                 relic_entries: dict, card_entries: dict) -> dict:
    entries: dict[str, dict] = {}
    textkey_re = re.compile(r"\.(?:pages|dialogue)\.", re.IGNORECASE)

    def event_body_index(path: Path):
        idx: dict[str, dict] = {}
        if not path.exists():
            return idx
        lines = path.read_text(encoding="utf-8").splitlines()
        i = 0
        while i < len(lines):
            raw = lines[i]
            i += 1
            # id must be a full UPPER_SNAKE token, not a sentence fragment
            m = re.match(r"^- ([A-Z][A-Z0-9_]{2,})(?![A-Za-z0-9])"
                         r"\s*[（(]?([^:：]*?)[）)]?\s*[:：]\s*(.*)$", raw)
            if not m:
                continue
            eid = m.group(1)
            text = m.group(3).strip()
            zh_name = next((z for z in CJK_NAME_RE.findall(m.group(2) or "") if z), "")
            while i < len(lines):
                nxt = lines[i]
                if nxt.startswith("- ") or nxt.startswith("#") or not nxt.strip():
                    break
                text += " " + nxt.strip()
                i += 1
            idx[eid] = {"body": text, "zh_name": zh_name}
        return idx

    en_index = event_body_index(md_path)
    zh_index = event_body_index(zh_path)

    def find_option_effect(event_id: str, option_key: str, en_body: str,
                           zh_body: str):
        last = option_key.rsplit(".", 1)[-1]
        nlast = norm_token(last)
        best = ""
        for m in re.finditer(r"\b([A-Za-z][A-Za-z0-9_']*)\s*→\s*([^;。]+)", en_body):
            tok, eff = m.group(1), m.group(2).strip()
            nt = norm_token(tok)
            if nlast and (nlast == nt or nlast in nt or nt.endswith(nlast)
                          or (len(nt) > 3 and nt in nlast)):
                best = eff
                break
        if not best:
            relic_key = last
            rel = relic_entries.get(relic_key) or relic_entries.get(
                camel_to_upper_snake(last))
            if rel is None:
                for rk, rv in relic_entries.items():
                    if norm_token(rk) == nlast or norm_token(
                            rv.get("display_name") or rv.get("name") or "") == nlast:
                        rel = rv
                        break
            if rel:
                best = (f"Gain relic {rel['id']} ({rel.get('name')}): "
                        f"{rel.get('description', '')}")
        if not best:
            card = card_entries.get(last)
            if card:
                best = f"Add card {card['id']}: {card.get('description', '')}"
        if not best and en_body:
            for m in re.finditer(r"[A-Za-z][A-Za-z0-9_' /-]{2,80}", en_body):
                if nlast and nlast in norm_token(m.group(0)):
                    best = m.group(0).strip()
                    break
        if not best:
            best = (f"Option `{last}` of event {event_id}. Per-option binding not "
                    f"decoded in events.md — treat locked/gold gates from the "
                    f"event description as authoritative and read the live event "
                    f"screen's option description field (mod 0.2.0 wires it).")
        zh_best = ""
        if zh_body:
            for m in re.finditer(r"\b([A-Za-z][A-Za-z0-9_']*)\s*→\s*([^;。]+)",
                                 zh_body):
                nt = norm_token(m.group(1))
                if nlast and (nlast == nt or nlast in nt or nt.endswith(nlast)
                              or (len(nt) > 3 and nt in nlast)):
                    zh_best = m.group(2).strip()
                    break
        return best, zh_best

    event_ids = set(en_index) | set(zh_index)
    live_options_by_event: dict[str, list] = {}
    textkey_re = re.compile(r"\.(?:pages|dialogue)\.", re.IGNORECASE)
    for opt_id in live_ids.get("event_option_ids") or []:
        if opt_id == "PROCEED":
            continue
        m = textkey_re.search(opt_id)
        if m:
            eid = opt_id[: m.start()]
            event_ids.add(eid)
            live_options_by_event.setdefault(eid, []).append(opt_id)
        elif re.match(r"^[A-Z][A-Z0-9_]+$", opt_id):
            live_options_by_event.setdefault(opt_id, []).append(opt_id)

    for eid in sorted(e for e in event_ids if re.match(r"^[A-Z][A-Z0-9_]+$", e)):
        en_body = (en_index.get(eid) or {}).get("body", "")
        zh_body = (zh_index.get(eid) or {}).get("body", "")
        zh_name = (zh_index.get(eid) or {}).get("zh_name", "")
        options = {}
        md_option_tokens = [m.group(1) for m in
                            re.finditer(r"\b([A-Za-z][A-Za-z0-9_']*)\s*→", en_body)
                            if m.group(1)[:1].isupper() and len(m.group(1)) >= 3]
        text_keys = list(live_options_by_event.get(eid, []))
        for tok in md_option_tokens:
            tk = f"{eid}.pages.INITIAL.options.{camel_to_upper_snake(tok)}"
            if tk not in text_keys:
                text_keys.append(tk)
        for tk in text_keys:
            last = tk.rsplit(".", 1)[-1]
            eff, zh_eff = find_option_effect(eid, tk, en_body, zh_body)
            page = "INITIAL"
            if ".pages." in tk:
                page = tk.split(".pages.")[1].split(".")[0]
            elif ".dialogue." in tk:
                page = "dialogue"
            options[tk] = envelope(
                tk, "event_option",
                humanize_option_key(tk),
                eff,
                aliases=[last, humanize(last)],
                play_notes="",
                source="md:events.md + census live textKeys",
                event_id=eid,
                page=page,
            )
            if zh_eff:
                options[tk]["zh_description"] = zh_eff
                options[tk]["zh_name"] = humanize_option_key(tk)
            elif zh_body:
                options[tk]["zh_description"] = (
                    f"事件 {eid} 的选项 `{last}`。完整逐项效果见事件描述；"
                    f"以 live 事件屏选项 description 字段为准。")
            else:
                options[tk]["zh_description"] = (
                    f"事件 {eid} 的选项 `{last}`——events.md 未解码逐项绑定；"
                    f"以 live 事件屏为准。")
        desc = en_body or (f"Event {eid} — options vary by act/gates; see the "
                           f"options map for live textKeys.")
        entry = envelope(
            eid, "event",
            humanize(eid),
            desc,
            aliases=[humanize(eid)] + ([zh_name] if zh_name else []),
            play_notes="",
            source=("md:events.md" if en_body else "census:live_ids.json")
                    + ("; md:events_zh.md" if zh_body else ""),
            options=options,
        )
        if zh_body:
            entry["zh_description"] = zh_body
        else:
            entry["zh_description"] = (f"事件 {eid}——选项随章节/门槛变化；"
                                       f"见 options 映射中的 live textKey。")
        if zh_name:
            entry["zh_name"] = zh_name
        entries[eid] = entry

    entries["PROCEED"] = envelope(
        "PROCEED", "event_option", "Proceed",
        "Continue / advance the event screen or dialogue. The generic continue "
        "option (is_proceed=true) — used by dialogue-walker events (e.g. "
        "THE_ARCHITECT) and any screen offering a forward step without a named "
        "choice.",
        aliases=["continue", "继续"],
        play_notes="",
        source="generator:synthesized; census:live_ids.json",
        event_id=None, page=None,
        zh_description="继续——事件屏/对白的前进选项（is_proceed=true）。",
        zh_name="继续",
    )

    # localized option ids on the wire (option id = localized string)
    for opt_id in live_ids.get("event_option_ids") or []:
        if opt_id in entries or opt_id == "PROCEED":
            continue
        if textkey_re.search(opt_id) or (
                "." in opt_id and re.match(r"^[A-Z0-9_.]+$", opt_id)):
            # live textKey — only stub if NO event entry nests this option key
            nested = any(opt_id in (e.get("options") or {})
                         for e in entries.values() if isinstance(e, dict))
            if opt_id not in entries and not nested:
                last = opt_id.rsplit(".", 1)[-1]
                eid = textkey_re.split(opt_id, 1)[0] if textkey_re.search(opt_id) \
                    else opt_id.split(".")[0]
                rel = None
                for rk, rv in relic_entries.items():
                    if norm_token(rk) == norm_token(last):
                        rel = rv
                        break
                card = card_entries.get(last)
                if rel:
                    desc = (f"Gain relic {rel['id']} ({rel.get('name')}): "
                            f"{rel.get('description', '')}")
                    zh_desc = (f"获得遗物 {rel['id']}（{rel.get('zh_name') or rel.get('name')}）："
                               f"{rel.get('zh_description') or rel.get('description', '')}")
                elif card:
                    desc = f"Add card {card['id']}: {card.get('description', '')}"
                    zh_desc = (f"加入卡牌 {card['id']}："
                               f"{card.get('zh_description') or card.get('description', '')}")
                else:
                    desc = (f"Event option `{last}` of {eid} — see the event "
                            f"description; per-option binding not decoded in "
                            f"events.md.")
                    zh_desc = f"事件 {eid} 的选项 `{last}`——见事件描述。"
                page = "INITIAL"
                pm = re.search(r"\.pages\.([A-Z0-9_]+)\.", opt_id, re.IGNORECASE)
                if pm:
                    page = pm.group(1)
                elif ".dialogue." in opt_id.lower():
                    page = "dialogue"
                entries[opt_id] = envelope(
                    opt_id, "event_option", humanize(last), desc,
                    aliases=[last], play_notes="",
                    source="census:live_ids.json",
                    event_id=eid, page=page, zh_description=zh_desc,
                )
            continue
        rel_guess = None
        for rk, rv in relic_entries.items():
            cands = {rv.get("zh_name"), rv.get("name")} | set(rv.get("aliases") or [])
            if opt_id in cands:
                rel_guess = rv
                break
        if rel_guess:
            desc = (f"Event option (live id is a localized name) granting or "
                    f"referencing relic {rel_guess['id']}: "
                    f"{rel_guess.get('description', '')}")
            zh_desc = (f"事件选项（live id 为本地化名称），关联遗物 "
                       f"{rel_guess['id']}：{rel_guess.get('zh_description') or rel_guess.get('description', '')}")
            en_name = f"{rel_guess.get('name')} (event option)"
        else:
            desc = (f"Event option with localized live id `{opt_id}` — resolve "
                    f"context from the event screen; effect not decoded in "
                    f"events.md.")
            zh_desc = f"本地化 live id 的事件选项 `{opt_id}`——events.md 未解码其效果。"
            en_name = f"Localized event option {opt_id}"
        entries[opt_id] = envelope(
            opt_id, "event_option", en_name,
            desc, aliases=[opt_id], play_notes="",
            source="census:live_ids.json",
            event_id=None, page=None, zh_description=zh_desc,
            zh_name=opt_id,
        )
    return entries

# ---------------------------------------------------------------------------
# generation + check
# ---------------------------------------------------------------------------

def apply_extras(domain: str, entries: dict, zh_entries: dict):
    for key, extra in (CURATED_EXTRAS.get(domain) or {}).items():
        en = dict(extra.get("en") or {})
        zh = dict(extra.get("zh") or {})
        if not en:
            continue
        en.setdefault("id", key)
        en["curated"] = True
        prev = entries.get(key)
        if prev is None or prev.get("curated") is not True:
            if prev:
                carried = dict(en)
                for k, v in prev.items():
                    if k not in carried:
                        carried[k] = v
                # curated field-level overrides win
                for k, v in en.items():
                    carried[k] = v
                en = carried
                en["curated"] = True
                # absorb parser-discovered moves if curated entry lacks them
                if not (en.get("moves") and any(
                        (en["moves"] or {}).values())) and prev.get("moves"):
                    en["moves"] = prev["moves"]
                if not en.get("cycle") and prev.get("cycle"):
                    en["cycle"] = prev["cycle"]
            entries[key] = en
        if zh:
            zh = dict(zh)
            zh.setdefault("id", key)
            for k, v in entries[key].items():
                if k not in ("name", "description", "play_notes", "zh_name",
                             "zh_description", "zh_moves", "aliases"):
                    zh.setdefault(k, v)
            zh["name"] = zh.get("name") or entries[key].get("name")
            zh["description"] = zh.get("description") or entries[key].get("description")
            zh["curated"] = True
            zh["needs_zh"] = False
            prevz = zh_entries.get(key)
            if prevz is None or prevz.get("curated") is not True:
                zh_entries[key] = zh


def to_zh_entry(en_entry: dict) -> dict:
    zh = {}
    for k, v in en_entry.items():
        if k in ("zh_name", "zh_description", "zh_moves", "zh_play_notes"):
            continue
        zh[k] = v
    zh["name"] = en_entry.get("zh_name") or en_entry.get("name") or en_entry.get("id", "")
    desc = en_entry.get("zh_description") or ""
    if not desc:
        desc = en_entry.get("description", "")
        zh["needs_zh"] = True
    else:
        zh["needs_zh"] = False
    zh["description"] = desc
    zh["play_notes"] = en_entry.get("zh_play_notes") or en_entry.get("play_notes", "")
    if en_entry.get("kind") == "monster":
        zh_moves = en_entry.get("zh_moves") or {}
        moves = {}
        for mk, mv in (en_entry.get("moves") or {}).items():
            mv_zh = dict(mv)
            zh_desc = zh_moves.get(mk) or mv.get("zh_description")
            if zh_desc:
                mv_zh["description"] = zh_desc
                mv_zh["needs_zh"] = False
            moves[mk] = mv_zh
        zh["moves"] = moves
    if en_entry.get("kind") == "event":
        options = {}
        for ok, ov in (en_entry.get("options") or {}).items():
            ov_zh = dict(ov)
            if ov.get("zh_description"):
                ov_zh["description"] = ov["zh_description"]
                ov_zh["needs_zh"] = False
            options[ok] = ov_zh
        zh["options"] = options
    return zh


def flatten_index(all_en: dict) -> dict:
    index: dict[str, list] = {}

    def reg(key, domain, entry):
        if key:
            index.setdefault(str(key), []).append((domain, entry))

    for domain, entries in all_en.items():
        for key, entry in entries.items():
            reg(key, domain, entry)
            for alias in entry.get("aliases") or []:
                reg(alias, domain, entry)
            if domain == "monsters":
                for mk, mv in (entry.get("moves") or {}).items():
                    reg(mk, "monster_move", mv)
                    for alias in mv.get("aliases") or []:
                        reg(alias, "monster_move", mv)
            if domain == "events":
                for ok, ov in (entry.get("options") or {}).items():
                    reg(ok, "event_option", ov)
                    for alias in ov.get("aliases") or []:
                        reg(alias, "event_option", ov)
    return index


def run_check(all_en: dict, all_zh: dict, live_ids: dict) -> int:
    index = flatten_index(all_en)
    hard_domains = [
        "move_ids", "power_ids", "relic_ids", "card_ids", "potion_ids",
        "event_option_ids", "card_option_ids", "character_ids",
        "intent_classes", "intent_types", "event_ids",
    ]
    soft_domains = ["creature_names", "relic_option_ids"]
    misses = []
    for domain in hard_domains:
        for lid in live_ids.get(domain) or []:
            if lid and lid not in index:
                misses.append((domain, lid))
    soft_misses = []
    for domain in soft_domains:
        for lid in live_ids.get(domain) or []:
            if lid and lid not in index:
                soft_misses.append((domain, lid))

    desc_problems = []
    cjk_name_problems = []
    for domain, entries in all_en.items():
        zh_entries = all_zh.get(domain) or {}
        for key, entry in entries.items():
            if has_cjk(entry.get("name")):
                cjk_name_problems.append((domain, key, entry.get("name")))
            if not (entry.get("description") or "").strip():
                desc_problems.append((domain, key, "EN description empty"))
            zh_e = zh_entries.get(key)
            if zh_e is None:
                desc_problems.append((domain, key, "missing in _zh.json"))
                continue
            if not (zh_e.get("description") or "").strip():
                if zh_e.get("needs_zh"):
                    desc_problems.append((domain, key, "needs_zh:true (ZH empty)"))
                else:
                    desc_problems.append((domain, key, "ZH description empty"))
            if domain == "monsters":
                for mk, mv in (entry.get("moves") or {}).items():
                    if not (mv.get("description") or "").strip():
                        desc_problems.append((domain, f"{key}.moves.{mk}",
                                              "move EN description empty"))
            if domain == "events":
                for ok, ov in (entry.get("options") or {}).items():
                    if not (ov.get("description") or "").strip():
                        desc_problems.append((domain, f"{key}.options.{ok}",
                                              "option EN description empty"))

    print("== live-id coverage ==")
    total = sum(len(live_ids.get(d) or []) for d in hard_domains)
    print(f"hard-domain live ids: {total}; misses: {len(misses)}")
    if misses:
        print("\nMISSING-ID TABLE (live id -> not resolvable in references/game/*.json)")
        print(f"{'domain':<20} live_id")
        for domain, lid in misses:
            print(f"{domain:<20} {lid}")
    if soft_misses:
        print(f"\nsoft misses (report-only): {len(soft_misses)}")
        for domain, lid in soft_misses[:40]:
            print(f"  {domain:<20} {lid}")
        if len(soft_misses) > 40:
            print(f"  ... {len(soft_misses) - 40} more")

    print("\n== entry counts (EN) ==")
    needs_zh_report = []
    for domain in DOMAINS:
        entries = all_en.get(domain) or {}
        zh_entries = all_zh.get(domain) or {}
        needs = [k for k, e in zh_entries.items() if e.get("needs_zh")]
        needs_zh_report.extend((domain, k) for k in needs)
        print(f"  {domain:<14} EN={len(entries):<5} ZH={len(zh_entries):<5} "
              f"needs_zh={len(needs)}")

    print("\n== EN name CJK leakage ==")
    print(f"count: {len(cjk_name_problems)}")
    for domain, key, name in cjk_name_problems[:40]:
        print(f"  {domain:<14} {key:<40} name={name!r}")

    print("\n== description problems ==")
    hard_desc = [p for p in desc_problems if not p[2].startswith("needs_zh:true")]
    needs_zh_desc = [p for p in desc_problems if p[2].startswith("needs_zh:true")]
    print(f"hard: {len(hard_desc)}; needs_zh flags: {len(needs_zh_desc)}")
    for domain, key, msg in hard_desc[:60]:
        print(f"  {domain:<14} {key:<48} {msg}")
    if len(hard_desc) > 60:
        print(f"  ... {len(hard_desc) - 60} more")
    if needs_zh_report:
        print("\n== needs_zh:true keys (ZH description falls back to EN) ==")
        for domain, key in needs_zh_report[:80]:
            print(f"  {domain:<14} {key}")
        if len(needs_zh_report) > 80:
            print(f"  ... {len(needs_zh_report) - 80} more")

    ok = not misses and not hard_desc and not cjk_name_problems
    print("\n--check:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


STARTER_SPECS = {
    "IRONCLAD": {
        "STRIKE_IRONCLAD": ("Strike", "1", "attack", "basic",
                            "Strike-tagged, deal 6 damage. Upgrade: +3 damage.",
                            "打击：造成 6 点伤害（打击标签）。升级：伤害 +3。"),
        "DEFEND_IRONCLAD": ("Defend", "1", "skill", "basic",
                            "Gain 5 Block. Upgrade: +3 Block.",
                            "防御：获得 5 格挡。升级：格挡 +3。"),
    },
    "SILENT": {
        "STRIKE_SILENT": ("Strike", "1", "attack", "basic",
                          "Strike-tagged, deal 6 damage. Upgrade: +3 damage.",
                          "打击：造成 6 点伤害（打击标签）。升级：伤害 +3。"),
        "DEFEND_SILENT": ("Defend", "1", "skill", "basic",
                          "Gain 5 Block. Upgrade: +3 Block.",
                          "防御：获得 5 格挡。升级：格挡 +3。"),
    },
    "DEFECT": {
        "STRIKE_DEFECT": ("Strike", "1", "attack", "basic",
                          "Strike-tagged, deal 6 damage. Upgrade: +3 damage.",
                          "打击：造成 6 点伤害（打击标签）。升级：伤害 +3。"),
        "DEFEND_DEFECT": ("Defend", "1", "skill", "basic",
                          "Gain 5 Block. Upgrade: +3 Block.",
                          "防御：获得 5 格挡。升级：格挡 +3。"),
    },
    "NECROBINDER": {
        "STRIKE_NECROBINDER": ("Strike", "1", "attack", "basic",
                               "Strike-tagged, deal 6 damage. Upgrade: +3 damage.",
                               "打击：造成 6 点伤害（打击标签）。升级：伤害 +3。"),
        "DEFEND_NECROBINDER": ("Defend", "1", "skill", "basic",
                               "Gain 5 Block. Upgrade: +3 Block.",
                               "防御：获得 5 格挡。升级：格挡 +3。"),
    },
    "REGENT": {
        "STRIKE_REGENT": ("Strike", "1", "attack", "basic",
                          "Strike-tagged, deal 6 damage. Upgrade: +3 damage.",
                          "打击：造成 6 点伤害（打击标签）。升级：伤害 +3。"),
        "DEFEND_REGENT": ("Defend", "1", "skill", "basic",
                          "Gain 5 Block. Upgrade: +3 Block.",
                          "防御：获得 5 格挡。升级：格挡 +3。"),
    },
}



# ---------------------------------------------------------------------------
# spire-codex.com structured API (primary numeric source; coordinator 2026-09-18)
# API ids: monsters/powers WITHOUT live suffixes (API SEA_KICK = live SEA_KICK_MOVE;
# API RAVENOUS = live RAVENOUS_POWER). JSON keys stay in LIVE form; API ids land
# in aliases[]. Responses cached under scripts/.cache/codex/ — the JSON DB is the
# durable store; the cache is reproducible input.
# ---------------------------------------------------------------------------

CODEX_CACHE = SKILL_ROOT / "scripts" / ".cache" / "codex"
BBCode_RE = re.compile(r"\[/?[a-zA-Z_]+\]")


def codex_clean(text):
    if not text:
        return text
    return BBCode_RE.sub("", str(text)).strip()


def codex_fetch(kind: str, cid: str, refresh: bool = False):
    cache_path = CODEX_CACHE / kind / f"{cid}.json"
    if cache_path.exists() and not refresh:
        try:
            return json.loads(cache_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass
    import time
    import urllib.request
    url = f"https://spire-codex.com/api/{kind}/{cid}"
    try:
        req = urllib.request.Request(
            url, headers={"User-Agent": "SpireBridge-json-pipeline/0.2"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
    except Exception as exc:
        data = {"_error": str(exc)}
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n",
                          encoding="utf-8")
    time.sleep(0.2)
    return data


def codex_probe_ids(kind: str, live_id: str):
    """Candidate API ids for a live id (suffix-stripped probes)."""
    cands = [live_id]
    if kind == "powers" and live_id.endswith("_POWER"):
        cands.append(live_id[: -len("_POWER")])
    if kind == "monsters":
        cands.append(live_id)
    return cands


def fold_codex(all_en: dict, live_ids: dict, refresh: bool = False) -> int:
    """Fold codex API facts into EN/ZH entries. Returns fetch-hit count."""
    hits = 0
    # --- powers: live RAVENOUS_POWER <- API RAVENOUS
    for pid in live_ids.get("power_ids") or []:
        for cand in codex_probe_ids("powers", pid):
            data = codex_fetch("powers", cand, refresh)
            if data.get("_error"):
                continue
            hits += 1
            ent = all_en["powers"].get(pid)
            if ent is None:
                continue
            ent.setdefault("aliases", [])
            if data.get("id") and data["id"] not in ent["aliases"] \
                    and data["id"] != pid:
                ent["aliases"] = sorted(set(ent["aliases"]) | {data["id"]})
            desc = codex_clean(data.get("description"))
            if desc and (len(ent.get("description") or "") < 40
                         or not ent.get("description")):
                ent["description"] = desc
                ent["source"] = (ent.get("source") or "") + f"; codex:powers/{cand}"
            if data.get("type") and not ent.get("power_type"):
                ent["power_type"] = data["type"]
            break
    # --- relics / potions / cards / events / characters: same-id probes
    for domain, kind, id_list in [
        ("relics", "relics", live_ids.get("relic_ids")),
        ("potions", "potions", live_ids.get("potion_ids")),
        ("cards", "cards", list(dict.fromkeys(
            (live_ids.get("card_ids") or []) + (live_ids.get("card_option_ids") or [])))),
        ("events", "events", live_ids.get("event_ids")),
        ("characters", "characters", ["IRONCLAD", "SILENT", "DEFECT",
                                      "NECROBINDER", "REGENT"]),
    ]:
        for lid in id_list or []:
            if not lid or not re.match(r"^[A-Z][A-Z0-9_]+$", lid):
                continue
            data = codex_fetch(kind, lid, refresh)
            if data.get("_error"):
                continue
            hits += 1
            ent = all_en[domain].get(lid)
            if ent is None:
                continue
            desc = codex_clean(data.get("description"))
            if desc and len(ent.get("description") or "") < 40:
                ent["description"] = desc
                ent["source"] = (ent.get("source") or "") + f"; codex:{kind}/{lid}"
            if domain == "cards" and data.get("cost") is not None \
                    and ent.get("cost") is None:
                ent["cost"] = str(data["cost"])
            if domain == "relics" and data.get("rarity_key") and not ent.get("rarity"):
                ent["rarity"] = data["rarity_key"]
            if domain == "potions" and data.get("rarity_key") and not ent.get("rarity"):
                ent["rarity"] = data["rarity_key"]
            if domain == "characters":
                if data.get("starting_hp") and not ent.get("hp"):
                    ent["hp"] = data["starting_hp"]
                if data.get("description") and len(ent.get("description") or "") < 40:
                    ent["description"] = codex_clean(data["description"])
    # --- monsters: fold structured hp/moves; keys stay LIVE-shaped
    monster_probe_ids = set()
    for key in (all_en.get("monsters") or {}):
        if re.match(r"^[A-Z][A-Z0-9_]+$", key):
            monster_probe_ids.add(key)
    for zh_name, key in CREATURE_NAME_TO_KEY.items():
        monster_probe_ids.add(key)
    monster_probe_ids |= {"SEAPUNK", "CORPSE_SLUG", "CALCIFIED_CULTIST",
                          "CULTIST", "CorpseSlug"}
    for mid in sorted(monster_probe_ids):
        data = codex_fetch("monsters", mid, refresh)
        if data.get("_error"):
            continue
        hits += 1
        api_id = data.get("id") or mid
        # canonical key: live-shaped entry key — prefer existing entry whose id
        # or aliases carry the api id / the probe id
        target_key = None
        for key, ent in (all_en.get("monsters") or {}).items():
            if key == api_id or key == mid or api_id in (ent.get("aliases") or []) \
                    or mid in (ent.get("aliases") or []):
                target_key = key
                break
        if target_key is None:
            target_key = api_id
        mon = all_en["monsters"].get(target_key)
        if mon is None:
            mon = envelope(
                target_key, "monster", data.get("name") or target_key,
                codex_clean(data.get("description")) or
                f"Monster {data.get('name', target_key)} — codex {api_id}.",
                aliases=[api_id, data.get("name")] if api_id else [],
                source=f"codex:monsters/{api_id}",
                acts=[], hp={"base": None, "notes": None},
                is_boss=str(data.get("type", "")).lower() == "boss",
                passives=[], cycle=[], moves={},
            )
            all_en["monsters"][target_key] = mon
        mon.setdefault("aliases", [])
        for a in {api_id, data.get("name"), mid} - {None, target_key}:
            if a not in mon["aliases"]:
                mon["aliases"] = sorted(set(mon["aliases"]) | {a})
        min_hp, max_hp = data.get("min_hp"), data.get("max_hp")
        amin, amax = data.get("min_hp_ascension"), data.get("max_hp_ascension")
        if min_hp:
            notes = f"{min_hp}-{max_hp} HP"
            if amin:
                notes += f"; A: {amin}-{amax}"
            mon["hp"] = {"base": min_hp, "notes": notes}
        if str(data.get("type", "")).lower() == "boss":
            mon["is_boss"] = True
        moves = dict(mon.get("moves") or {})
        cycle = list(mon.get("cycle") or [])
        for mv in data.get("moves") or []:
            api_mid = mv.get("id") or ""
            live_mid = api_mid if api_mid.endswith("_MOVE") or api_mid == "STUNNED" \
                else (api_mid + "_MOVE" if api_mid else "")
            if not live_mid:
                continue
            dmg = mv.get("damage") or {}
            norm, asc, hits_n = dmg.get("normal"), dmg.get("ascension"), \
                dmg.get("hit_count")
            intent = mv.get("intent")
            effect_bits = [f"codex: {mv.get('name', api_mid)}"]
            if intent:
                effect_bits.append(f"intent={intent}")
            if norm is not None:
                if hits_n and hits_n > 1:
                    effect_bits.append(f"damage {norm}x{hits_n}"
                                       + (f" (A:{asc})" if asc else ""))
                else:
                    effect_bits.append(f"damage {norm}"
                                       + (f" (A:{asc})" if asc else ""))
            if mv.get("block"):
                effect_bits.append(f"block {mv['block']}")
            if mv.get("heal"):
                effect_bits.append(f"heal {mv['heal']}")
            if mv.get("powers"):
                effect_bits.append(f"powers {mv['powers']}")
            codex_desc = "; ".join(effect_bits)
            prev = moves.get(live_mid)
            intents = []
            if intent:
                cls_map = {"Attack": "SingleAttackIntent" if not (hits_n and hits_n > 1)
                           else "MultiAttackIntent",
                           "Buff": "BuffIntent", "Debuff": "DebuffIntent",
                           "Defend": "DefendIntent", "Heal": "HealIntent",
                           "Sleep": "SleepIntent", "Stun": "StunIntent",
                           "Summon": "SummonIntent", "Status": "StatusIntent",
                           "Unknown": "UnknownIntent"}
                cls = cls_map.get(intent)
                if cls:
                    entry_i = {"class": cls,
                               "type": "Attack" if "Attack" in cls else intent}
                    if norm is not None:
                        entry_i["base_damage"] = norm
                        entry_i["hits"] = hits_n or 1
                        if asc is not None:
                            entry_i["base_damage_ascension"] = asc
                    intents.append(entry_i)
            if prev is None:
                moves[live_mid] = envelope(
                    live_mid, "move", mv.get("name") or humanize(api_mid),
                    codex_desc,
                    aliases=[api_mid] if api_mid and api_mid != live_mid else [],
                    source=f"codex:monsters/{api_id} move {api_mid}",
                    monster_id=target_key, intents=intents,
                    base_damage=norm,
                    base_damage_ascension=asc,
                    hits=hits_n, status_count=None,
                    display_note=(f"{norm}x{hits_n}" if hits_n and hits_n > 1
                                  else (str(norm) if norm is not None else None)),
                )
            else:
                if api_mid and api_mid not in (prev.get("aliases") or []) \
                        and api_mid != live_mid:
                    prev["aliases"] = sorted(set(prev.get("aliases") or [])
                                             | {api_mid})
                # thin md fragment -> replace with codex numbers + keep md text
                prev_desc = prev.get("description") or ""
                thin = len(prev_desc) < 40 or prev_desc.strip().endswith("→") \
                    or prev_desc.strip().startswith("(") \
                    or prev_desc.strip().startswith(str(prev_desc.strip()[:1]))
                if thin and codex_desc:
                    prev["description"] = codex_desc + (
                        f" | archive: {prev_desc}" if prev_desc.strip() else "")
                    prev["source"] = (prev.get("source") or "") + \
                        f"; codex:monsters/{api_id}"
                elif norm is not None and prev.get("base_damage") is None:
                    prev["base_damage"] = norm
                    prev["base_damage_ascension"] = asc
                    prev["hits"] = hits_n
                    if not prev.get("intents"):
                        prev["intents"] = intents
                if mv.get("name") and not prev.get("name"):
                    prev["name"] = mv["name"]
            if live_mid not in cycle and len(cycle) < 12:
                cycle.append(live_mid)
        mon["moves"] = moves
        if cycle and not mon.get("cycle"):
            mon["cycle"] = cycle
        elif cycle:
            merged_cycle = list(dict.fromkeys(list(mon.get("cycle") or []) + cycle))
            mon["cycle"] = merged_cycle[:12]
    return hits


# canonical descriptions for shared/system move ids that md fragments mangle
MOVE_TEXT_FIXUPS = {
    "STUNNED": (
        "Stunned — the creature skips its action this turn. Sources: spawn "
        "stun (SPAWNED_MOVE class), wake-up stuns after sleep, burrow-break "
        "(AfterBlockBroken), Imbalanced self-stun after a fully blocked "
        "attack, RAVENOUS ally-death devour stun, PlowPower threshold stun. "
        "Intent shows Stun — pure free-damage window; spend it.",
        "被击晕——本回合跳过行动。来源：生成回合晕、沉睡唤醒晕、钻地破防晕、"
        "失衡自晕（攻击被完全格挡后）、RAVENOUS 盟友死亡吞噬晕、PlowPower 阈值晕。"
        "意图显示 Stun——纯免费输出窗口，尽情倾泻。"),
    "UNSET_MOVE": (
        "UNSET_MOVE — placeholder move id (no action selected yet / transition "
        "state). The creature has no committed move this read; re-read state "
        "after the turn advances.",
        "UNSET_MOVE——占位招式 id（尚未选择行动/过渡状态）。本次读取该生物没有"
        "已确定的招式；回合推进后重新读取 state。"),
    "THRASH_MOVE_2": (
        "THRASH_MOVE_2 — multi attack 8 (A:9) x2 — TheInsatiable (无底之沙虫) "
        "cycle move. Weak shaves the per-hit number. Part of cycle LIQUIFY -> "
        "THRASH -> SALIVATE -> THRASH_2 -> LUNGING_BITE -> repeat; see "
        "SANDPIT_POWER kill timer doctrine on the monster entry.",
        "THRASH_MOVE_2——多段攻击 8（A:9）x2——无底之沙虫（TheInsatiable）循环招式。"
        "虚弱削减每段伤害。循环 LIQUIFY → THRASH → SALIVATE → THRASH_2 → "
        "LUNGING_BITE → 循环；击杀计时教条见该怪物条目的 SANDPIT_POWER。"),
    "THRASH2_MOVE": (
        "THRASH2_MOVE — single attack 3 (+ current Strength) — BowlbugNectar "
        "(盛碗虫·蜜) cycle self-loop move after its +15 Strength BUFF. Kill "
        "before the buff lands to defuse the timer.",
        "THRASH2_MOVE——单段攻击 3（+当前力量）——盛碗虫（蜜）在 +15 力量 BUFF "
        "后的循环自循环招式。在增益落地前击杀即可拆掉计时器。"),
    "REVIVE_MOVE": (
        "REVIVE_MOVE — heal-to-full revive (HealIntent) queued by "
        "ILLUSION_POWER on death: the owner is untargetable while reviving, "
        "keeps buffs, then heals to Max HP and resumes. Kill the summoner "
        "(master) to stop revive loops.",
        "REVIVE_MOVE——ILLUSPHANTOM_POWER 死亡时排队的满血复活（HealIntent）："
        "复活期间持有者不可选中、保留增益，随后回复至满血并继续行动。击杀召唤者"
        "（主体）可终止复活循环。"),
}


POST_ZH_FIXUPS = {
    "Axebot": ("巨斧机器人",
               "巨斧机器人（StockPower 死亡生成机器人链）：持有者死亡且 Amount>0 时在"
               "同槽位生成 Axebot（StockAmount=Amount-1）；链上充能未尽时战斗不结束。"
               "生成 HP 不保证满血（观测 1/x 当前 HP）。清链否则组装师不断补位。"),
    "AXEBOT": ("巨斧机器人",
               "巨斧机器人（StockPower 死亡生成机器人链）：持有者死亡且 Amount>0 时在"
               "同槽位生成（StockAmount=Amount-1）；链上充能未尽时战斗不结束。参见 Axebot。"),
    "Osty": ("奥斯提",
             "奥斯提（亡灵契约师宠物召唤物）：缚魂命匣战斗开始召唤 1 只，后续回合能量"
             "重置后重召；无界命匣开局 5 只、每回合 +2。Osty 攻击喂骨笛（+2 格挡/次）"
             "与 NECRO_MASTERY_POWER；卡牌 UNLEASH = Osty 造成 6+当前 HP 伤害。"
             "DIE_FOR_YOU_POWER：死亡不结束战斗，宠物逻辑复活/重召。"),
    "OSTY": ("奥斯提",
             "奥斯提（亡灵契约师宠物召唤物）：死亡不结束战斗；参见 Osty 条目。"),
    "CORPSE_SLUG": ("尸体蛞蝓",
                    "尸体蛞蝓（codex CORPSE_SLUG；25-27 HP，升格 27-29）：与 SEAPUNK"
                    "（海洋混混，44-46 HP）是不同怪物——档案旧文曾混用 CorpseSlug 名称。"
                    "循环含 WHIP_SLAP_MOVE / GLOMP_MOVE / GOOP_MOVE；携带吞噬类机制的"
                    "以 SEAPUNK 条目为准。招式数值以 live state 意图字段校对。"),
}


def apply_post_fixups(all_en: dict):
    """Apply ZH fixups + cross-monster move-text canonicalization pre-write."""
    monsters = all_en.get("monsters") or {}
    for key, (zh_name, zh_desc) in POST_ZH_FIXUPS.items():
        ent = monsters.get(key)
        if ent is not None:
            ent["zh_name"] = zh_name
            ent["zh_description"] = zh_desc
            ent["aliases"] = sorted(set(ent.get("aliases") or []) | {zh_name})
    # thin codex-born monster descriptions -> hp/cycle summary
    for key, ent in monsters.items():
        desc = ent.get("description") or ""
        if len(desc) >= 80:
            continue
        hp = ent.get("hp") or {}
        cycle = ent.get("cycle") or []
        moves = ent.get("moves") or {}
        summary_bits = [f"{ent.get('name', key)}"]
        if hp.get("notes"):
            summary_bits.append(hp["notes"])
        elif hp.get("base"):
            summary_bits.append(f"{hp['base']} HP")
        if cycle:
            summary_bits.append("cycle " + " -> ".join(cycle[:8]))
        elif moves:
            summary_bits.append("moves " + ", ".join(sorted(moves)[:8]))
        summary = "; ".join(summary_bits)
        if len(summary) > len(desc):
            ent["description"] = summary + (
                f" | {desc}" if desc.strip() and not desc.startswith("Monster ")
                else " — resolve move ids via spirectl lookup; live intent "
                     "fields are authoritative.")
    apply_move_fixups(all_en)


def apply_move_fixups(all_en: dict):
    monsters = all_en.get("monsters") or {}
    # choose canonical rich text per move id across all monsters
    best = {}
    for mon in monsters.values():
        for mk, mv in (mon.get("moves") or {}).items():
            desc = mv.get("description") or ""
            if len(desc) > len(best.get(mk, "")):
                best[mk] = desc
    for mon_key, mon in monsters.items():
        moves = mon.get("moves") or {}
        for mk, (en_desc, zh_desc) in MOVE_TEXT_FIXUPS.items():
            mv = moves.get(mk)
            if mv is None:
                continue
            cur = mv.get("description") or ""
            if len(cur) < len(en_desc) or cur.strip().endswith("→") \
                    or len(cur) < 40:
                mv["description"] = en_desc
                mv["zh_description"] = zh_desc
                mv["source"] = (mv.get("source") or "") + "; curated:move-fixup"
        for mk, mv in moves.items():
            if mk in MOVE_TEXT_FIXUPS:
                continue
            cur = mv.get("description") or ""
            # thin/codex-fragment text loses to the richest text found anywhere
            thin = (len(cur) < 60 or cur.strip().endswith("→")
                    or cur.strip().lower().startswith("codex:"))
            if thin and best.get(mk) and len(best[mk]) > len(cur) + 20:
                mv["description"] = best[mk]
    return


def main() -> int:
    parser = argparse.ArgumentParser(description="Build references/game JSON DB")
    parser.add_argument("--md-dir", default=str(DEFAULT_MD_DIR))
    parser.add_argument("--live-ids", default=str(DEFAULT_LIVE_IDS))
    parser.add_argument("--decomp", default=str(DEFAULT_DECOMP))
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    parser.add_argument("--check", action="store_true",
                        help="coverage gate only (reads existing JSON output)")
    parser.add_argument("--no-codex", action="store_true",
                        help="skip spire-codex.com fold (md-only generation)")
    parser.add_argument("--codex-refresh", action="store_true",
                        help="re-fetch codex API instead of using cache")
    args = parser.parse_args()

    md_dir = Path(args.md_dir)
    out_dir = Path(args.out_dir)
    live_path = Path(args.live_ids)
    live_ids = {}
    if live_path.exists():
        live_ids = json.loads(live_path.read_text(encoding="utf-8"))
    else:
        print(f"build_game_reference_json: WARN live-ids missing ({live_path})",
              file=sys.stderr)
    census = set(live_ids.get("move_ids") or [])

    if args.check:
        all_en, all_zh = {}, {}
        for domain in DOMAINS:
            all_en[domain] = load_existing(out_dir / f"{domain}.json")
            all_zh[domain] = load_existing(out_dir / f"{domain}_zh.json")
        return run_check(all_en, all_zh, live_ids)

    print(f"build_game_reference_json: md={md_dir} live-ids={live_path} out={out_dir}")

    en: dict[str, dict] = {d: {} for d in DOMAINS}
    en["relics"] = parse_relics(md_dir / "relics.md", md_dir / "relics_zh.md")
    print(f"  parsed relics: {len(en['relics'])}")
    en["powers"] = parse_powers(md_dir / "powers.md", md_dir / "powers_zh.md")
    print(f"  parsed powers: {len(en['powers'])}")
    en["cards"] = parse_cards(md_dir / "cards.md", md_dir / "cards_zh.md")
    print(f"  parsed cards: {len(en['cards'])}")
    # starter-deck synthesis from characters.md + census
    for pool, cards in STARTER_SPECS.items():
        for cid, spec in cards.items():
            if cid in en["cards"]:
                continue
            name, cost, ctype, rarity, desc, zh_desc = spec
            entry = envelope(
                cid, "card", name, desc,
                aliases=[name], play_notes="",
                source="generator:synthesized from characters.md starter decks",
                cost=cost, card_type=ctype, rarity=rarity,
                target_type=None, character_pool=pool,
                keywords=["Strike-tagged"] if "Strike" in name else [],
                upgrade=None,
            )
            entry["zh_name"] = name
            entry["zh_description"] = zh_desc
            en["cards"][cid] = entry
    en["potions"] = parse_potions(md_dir / "potions.md", md_dir / "potions_zh.md")
    print(f"  parsed potions: {len(en['potions'])}")
    en["afflictions"] = parse_afflictions(md_dir / "afflictions.md",
                                          md_dir / "afflictions_zh.md")
    print(f"  parsed afflictions: {len(en['afflictions'])}")
    en["intents"] = parse_intents(md_dir / "intents.md", md_dir / "intents_zh.md")
    print(f"  parsed intents: {len(en['intents'])}")
    en["characters"] = parse_characters(md_dir / "characters.md",
                                        md_dir / "characters_zh.md")
    print(f"  parsed characters: {len(en['characters'])}")
    en["monsters"] = parse_monsters(md_dir / "monsters.md", md_dir / "monsters_zh.md",
                                    census)
    print(f"  parsed monsters: {len(en['monsters'])} "
          f"(moves total: {sum(len(m.get('moves') or {}) for m in en['monsters'].values())})")
    en["events"] = parse_events(md_dir / "events.md", md_dir / "events_zh.md",
                                live_ids, en["relics"], en["cards"])
    print(f"  parsed events: {len(en['events'])} "
          f"(options total: {sum(len(e.get('options') or {}) for e in en['events'].values())})")

    if not args.no_codex:
        hits = fold_codex(en, live_ids, refresh=args.codex_refresh)
        print(f"  codex fold: {hits} API hits (cache: {CODEX_CACHE})")
    apply_move_fixups(en)

    # power host_of_affliction flags from afflictions
    for aff in en["afflictions"].values():
        host = aff.get("host_power_id")
        if host and host in en["powers"]:
            en["powers"][host]["host_of_affliction"] = True
            keys = set(en["powers"][host].get("affliction_keys") or [])
            keys.add(aff["id"])
            en["powers"][host]["affliction_keys"] = sorted(keys)

    zh: dict[str, dict] = {}
    # move tables for live-model-id monsters (census + archive prose)
    curated_moves = {
        "SEAPUNK": {
            "SEA_KICK_MOVE": (
                "SEA_KICK_MOVE", "Sea Kick",
                "single attack 11 (A:13) — SEAPUNK cycle opener. Live model_id "
                "SEA_KICK (codex) = SEA_KICK_MOVE (state).",
                {"class": "SingleAttackIntent", "type": "Attack",
                 "base_damage": 11, "hits": 1, "base_damage_ascension": 13},
                11, 13, 1),
            "SPINNING_KICK_MOVE": (
                "SPINNING_KICK_MOVE", "Spinning Kick",
                "multi attack 2 x4 (2 damage per hit, 4 hits; total 8 base) — "
                "cycle move 2. Weak cuts the per-hit number.",
                {"class": "MultiAttackIntent", "type": "Attack",
                 "base_damage": 2, "hits": 4}, 2, None, 4),
            "BUBBLE_BURP_MOVE": (
                "BUBBLE_BURP_MOVE", "Bubble Burp",
                "two-intent cycle move (live display shows 2 intents) — exact "
                "damage/debuff split not decoded in archive; resolve live "
                "intent fields (damage/hits/description) each combat.",
                None, None, None, None),
            "GLOMP_MOVE": (
                "GLOMP_MOVE", "Glomp",
                "single attack 8 (live intents can exceed table — 11-class "
                "observed at A1). Part of the CorpseSlug/SEAPUNK archive cycle "
                "(WhipSlap 3x2 -> Glomp 8 -> Goop Frail 2 -> repeat). "
                "Counterplay: kill-window doctrine via RAVENOUS ally-death stun.",
                {"class": "SingleAttackIntent", "type": "Attack",
                 "base_damage": 8, "hits": 1}, 8, None, 1),
            "WHIP_SLAP_MOVE": (
                "WHIP_SLAP_MOVE", "Whip Slap",
                "multi attack 3 x2 (archive CorpseSlug cycle opener; 3 per hit, "
                "2 hits).",
                {"class": "MultiAttackIntent", "type": "Attack",
                 "base_damage": 3, "hits": 2}, 3, None, 2),
            "GOOP_MOVE": (
                "GOOP_MOVE", "Goop",
                "debuff move — applies Frail 2 to the player (CorpseSlug/"
                "SEAPUNK archive: Goop Frail 2); LeafSlimeS variant is Status "
                "x1 (adds status cards). Check the owning monster entry.",
                {"class": "DebuffIntent", "type": "Debuff"}, None, None, None),
        },
        "CALCIFIED_CULTIST": {
            "INCANTATION_MOVE": (
                "INCANTATION_MOVE", "Incantation",
                "buff — applies RITUAL_POWER +2 to self (cycle opener). Ritual "
                "grants +2 Strength at end of each subsequent side turn — race "
                "doctrine: burst before the ramp compounds.",
                {"class": "BuffIntent", "type": "Buff"}, None, None, None),
            "DARK_STRIKE_MOVE": (
                "DARK_STRIKE_MOVE", "Dark Strike",
                "single attack 9 (A:11) — cycle damage move after Incantation.",
                {"class": "SingleAttackIntent", "type": "Attack",
                 "base_damage": 9, "hits": 1, "base_damage_ascension": 11},
                9, 11, 1),
        },
    }
    for mon_key, move_map in curated_moves.items():
        mon = en["monsters"].get(mon_key)
        if mon is None:
            continue
        moves = dict(mon.get("moves") or {})
        for mk, (mid, mname, mdesc, mintent, bdmg, basc, hits) in move_map.items():
            mv = envelope(
                mid, "move", mname, mdesc,
                aliases=[humanize(mid.replace("_MOVE", ""))],
                play_notes="",
                source="curated:census + monsters.md archive cycle",
                monster_id=mon_key,
                intents=[mintent] if mintent else [],
                base_damage=bdmg,
                base_damage_ascension=basc,
                hits=hits,
                status_count=None,
                display_note=None,
            )
            prev = moves.get(mk)
            if prev is None or not prev.get("curated"):
                moves[mk] = mv
        mon["moves"] = moves
        mon.setdefault("cycle", [])
        if mon_key == "SEAPUNK" and not mon["cycle"]:
            mon["cycle"] = ["SEA_KICK_MOVE", "SPINNING_KICK_MOVE",
                            "BUBBLE_BURP_MOVE"]

    for domain in DOMAINS:
        zh[domain] = {k: to_zh_entry(v) for k, v in en[domain].items()}
        apply_extras(domain, en[domain], zh[domain])
        # re-apply curated moves after extras (extras may replace the entry)
        for mon_key, move_map in curated_moves.items():
            if domain != "monsters":
                continue
            mon = en[domain].get(mon_key)
            if mon is None:
                continue
            moves = dict(mon.get("moves") or {})
            for mk, (mid, mname, mdesc, mintent, bdmg, basc, hits) in move_map.items():
                if mk in moves and (moves[mk].get("description") or "").strip() \
                        and not moves[mk].get("description", "").startswith(mid):
                    continue
                moves[mk] = envelope(
                    mid, "move", mname, mdesc,
                    aliases=[humanize(mid.replace("_MOVE", ""))],
                    source="curated:census + monsters.md archive cycle",
                    monster_id=mon_key,
                    intents=[mintent] if mintent else [],
                    base_damage=bdmg, base_damage_ascension=basc, hits=hits,
                    status_count=None, display_note=None,
                )
            mon["moves"] = moves
            prior_zh = zh[domain].get(mon_key)
            if prior_zh is None or prior_zh.get("curated") is not True:
                zh[domain][mon_key] = to_zh_entry(mon)
            else:
                # curated zh wins; refresh its moves map from EN structure
                twin = to_zh_entry(mon)
                twin["description"] = prior_zh.get("description")
                twin["name"] = prior_zh.get("name")
                twin["curated"] = True
                twin["needs_zh"] = False
                zh[domain][mon_key] = twin
        for k, v in en[domain].items():
            prior = zh[domain].get(k)
            if prior is None or prior.get("curated") is not True:
                zh[domain][k] = to_zh_entry(v)

    # unify case-variant duplicate monster keys (Axebot/AXEBOT, Osty/OSTY):
    # keep the curated or mixed-case key; the other form survives as an alias
    mons = en["monsters"]
    by_lower: dict[str, list] = {}
    for key in list(mons):
        by_lower.setdefault(key.lower(), []).append(key)
    for lk, keys in by_lower.items():
        if len(keys) < 2:
            continue

        def _rank(k):
            e = mons[k]
            return (0 if e.get("curated") else 1,
                    1 if k.isupper() else 0,
                    len(k))

        keys.sort(key=_rank)
        keep, drops = keys[0], keys[1:]
        kept = mons[keep]
        for d in drops:
            de = mons.pop(d)
            extra_aliases = set(de.get("aliases") or []) | {d, de.get("name"),
                                                            de.get("zh_name")}
            kept["aliases"] = sorted({a for a in
                                       set(kept.get("aliases") or []) | extra_aliases
                                       if a})
            km = dict(kept.get("moves") or {})
            for mk, mv in (de.get("moves") or {}).items():
                if mk not in km or len(mv.get("description") or "") > len(
                        km.get(mk, {}).get("description") or ""):
                    km[mk] = mv
            kept["moves"] = km
            if not (kept.get("description") or "").strip() and de.get("description"):
                kept["description"] = de["description"]
            if (de.get("hp") or {}).get("base") and not (kept.get("hp") or {}).get("base"):
                kept["hp"] = de["hp"]
            for f in ("zh_description", "zh_name"):
                if de.get(f) and not kept.get(f):
                    kept[f] = de[f]
            kp = list(kept.get("passives") or [])
            seen = {x.get("power_id") for x in kp}
            for x in de.get("passives") or []:
                if x.get("power_id") not in seen:
                    kp.append(x)
            kept["passives"] = kp
            # drop the duplicate from the ZH twin map as well; re-twin the keeper
            zh_mons = zh.get("monsters") or {}
            zh_mons.pop(d, None)
            zh_mons[keep] = to_zh_entry(kept)



    apply_post_fixups(en)
    # re-twin monsters after post-fixups (zh fields may have been enriched)
    zh_mons = zh.get("monsters") or {}
    for k, v in en["monsters"].items():
        prior = zh_mons.get(k)
        if prior is None or prior.get("curated") is not True:
            zh_mons[k] = to_zh_entry(v)
        elif v.get("zh_description") and (prior.get("needs_zh")
                                          or not prior.get("description")):
            prior["description"] = v["zh_description"]
            prior["needs_zh"] = False
            if v.get("zh_name"):
                prior["name"] = v["zh_name"]

    for domain in DOMAINS:
        old_en = load_existing(out_dir / f"{domain}.json")
        old_zh = load_existing(out_dir / f"{domain}_zh.json")
        merged_en = merge_domain(old_en, en[domain])
        merged_zh = merge_domain(old_zh, zh[domain])
        for k, e in merged_en.items():
            if k not in merged_zh:
                merged_zh[k] = to_zh_entry(e)
            else:
                z = merged_zh[k]
                if not z.get("curated"):
                    twin = to_zh_entry(e)
                    if z.get("description") and not z.get("needs_zh"):
                        twin["description"] = z["description"]
                        twin["needs_zh"] = False
                    if z.get("name"):
                        twin["name"] = z["name"]
                    merged_zh[k] = twin
        en_path = out_dir / f"{domain}.json"
        zh_path = out_dir / f"{domain}_zh.json"
        en_path.write_text(json.dumps(merged_en, ensure_ascii=False, indent=2,
                                      sort_keys=True) + "\n", encoding="utf-8")
        zh_path.write_text(json.dumps(merged_zh, ensure_ascii=False, indent=2,
                                      sort_keys=True) + "\n", encoding="utf-8")
        print(f"  wrote {en_path.name} ({len(merged_en)}) + {zh_path.name} "
              f"({len(merged_zh)})")

    all_en = {d: load_existing(out_dir / f"{d}.json") for d in DOMAINS}
    all_zh = {d: load_existing(out_dir / f"{d}_zh.json") for d in DOMAINS}
    return run_check(all_en, all_zh, live_ids)


if __name__ == "__main__":
    sys.exit(main())
