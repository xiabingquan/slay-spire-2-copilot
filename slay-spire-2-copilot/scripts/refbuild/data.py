"""Static curation data for the references/game JSON store.

Hand-curated extras, curated monster move tables, zh/move text fixups, and the
creature display-name map — pure data, no logic.
"""

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

# Curated move tables for live-model-id monsters (overlay-safe fills)
CURATED_MOVES = {
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
