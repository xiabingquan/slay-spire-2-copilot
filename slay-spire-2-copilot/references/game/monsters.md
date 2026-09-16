# Monsters

Deterministic enemy reference. Source: decompiled game code
`MegaCrit.Sts2.Core.Models.Monsters` + `MegaCrit.Sts2.Core.Models.Encounters` +
act pools in `MegaCrit.Sts2.Core.Models.Acts` (/tmp/sts2-decomp). Power effects
verified in `MegaCrit.Sts2.Core.Models.Powers`.

Format: `- Name (id, where): moves — MOVE_ID = deterministic effect; passives with exact values.`

Damage/block numbers are base (Ascension 0). When an ascension tier exists it is shown as `(A: n)` — `ToughEnemies` raises HP/block, `DeadlyEnemies` raises damage. HP shown as base (A-range) where known.

Act pools (from `GenerateAllEncounters`):
- Act 1 Overgrowth: bosses VantomBoss, CeremonialBeastBoss, TheKinBoss; elites BygoneEffigyElite, ByrdonisElite, PhrogParasiteElite.
- Act 2 Hive: bosses TheInsatiableBoss, KnowledgeDemonBoss, KaiserCrabBoss; elites DecimillipedeElite, EntomancerElite, InfestedPrismsElite.

## Act 1 — Overgrowth

- LeafSlimeM (LeafSlimeM, Act1 Slimes/SlitheringStrangler/Flyconid encounters; 32–35 HP): CLUMP_SHOT = single attack 8 (A:9); STICKY_SHOT = Status ×2 (adds status cards to discard).
- LeafSlimeS (LeafSlimeS, Act1 Slimes; 11–15 HP): TACKLE_MOVE = single attack 3 (A:4); GOOP_MOVE = Status ×1.
- TwigSlimeM (TwigSlimeM, Act1 Slimes/SlitheringStrangler; 26–28 HP): POKEY_POUNCE_MOVE = single attack 11 (A:12); STICKY_SHOT_MOVE = Status ×1.
- TwigSlimeS (TwigSlimeS, Act1 Slimes; 7–11 HP): TACKLE_MOVE = single attack 4 (A:5).
- ShrinkerBeetle (ShrinkerBeetle, Act1 ShrinkerBeetleWeak / OvergrowthCrawlers; 38–40 HP): SHRINKER_MOVE = debuff — applies ShrinkPower −1 to the player (negative = infinite): player attack damage ×0.7 (−30%) while the beetle lives; CHOMP_MOVE = single attack 7 (A:8); STOMP_MOVE = single attack 13 (A:14). Cycle: SHRINKER → CHOMP → STOMP → CHOMP…
- Inklet (Inklet, Act1 InkletsNormal; 11–17 HP): JAB_MOVE = single attack 3 (A:4); WHIRLWIND_MOVE = multi attack 2 (A:3) ×3; PIERCING_GAZE_MOVE = single attack 10 (A:11). Passive SlipperyPower: while charges remain, HP lost per hit is capped at 1; each unblocked hit ≥1 consumes 1 charge.
- Mawler (Mawler, Act1 MawlerNormal; 72 HP): RIP_AND_TEAR_MOVE = single attack 14 (A:16); ROAR_MOVE = debuff — 3 Vulnerable to the player; CLAW_MOVE = multi attack 4 (A:5) ×2.
- Nibbit (Nibbit, Act1 NibbitsNormal/Weak; 42–46 HP): BUTT_MOVE = single attack 12 (A:13); SLICE_MOVE = single attack 6 (A:7) + self 5 Block (A:6); HISS_MOVE = buff +2 Strength (A:3). Cycle BUTT → SLICE → HISS → BUTT…
- SnappingJaxfruit (SnappingJaxfruit, Act1 SnappingJaxfruitNormal (with Flyconid); 31–33 HP): ENERGY_ORB_MOVE = single attack 3 (A:4) + self +2 Strength; repeats every turn.
- Flyconid (Flyconid, Act1 FlyconidNormal / SnappingJaxfruitNormal; 47–49 HP): VULNERABLE_SPORES_MOVE = debuff — 2 Vulnerable to the player; FRAIL_SPORES_MOVE = single attack 8 (A:9) + 2 Frail; SMASH_MOVE = single attack 11 (A:12).
- FuzzyWurmCrawler (FuzzyWurmCrawler, Act1 FuzzyWurmCrawlerWeak / OvergrowthCrawlers; 55–57 HP): FIRST_ACID_GOOP = single attack 4 (A:6); ACID_GOOP = single attack 4 (A:6); INHALE = buff +7 Strength. Cycle: acid → inhale → acid…
- Fogmog (Fogmog, Act1 FogmogNormal; 74 HP): ILLUSION_MOVE = summon 1 EyeWithTeeth; SWIPE_MOVE = single attack 8 (A:9) + self +1 Strength; HEADBUTT_MOVE = single attack 14 (A:16). After first swipe, 40% SWIPE_RANDOM / 60% HEADBUTT branch. Kill Fogmog to stop further summons.
- EyeWithTeeth (EyeWithTeeth, summoned by Fogmog; 6 HP): DISTRACT_MOVE = add 3 Dazed to each target's discard; repeats. Passive IllusionPower 1 (+ MinionPower): on death it is not removed — it queues REVIVE_MOVE (Heal intent) and heals back to full Max HP, untargetable while reviving, then resumes its move loop. Illusions keep buffs on death.
- Tunneler (Tunneler, Act2 TunnelerWeak/Normal; 87 HP): BITE_MOVE = single attack 13 (A:15); BURROW_MOVE = Buff+Defend — BurrowedPower 1 + 32 Block (A:37), becomes hidden; BELOW_MOVE = hidden single attack 23 (A:26), self-loops while burrowed; DIZZY_MOVE = stun wakeup (not shown in bestiary). BurrowedPower AfterBlockBroken: if the Tunneler's Block is broken, it is stunned (DIZZY → then BITE) and BurrowedPower is removed (all remaining Block lost via AfterRemoved −999999999). Break its Block to cancel the burrowed attack.
- Ruby Raiders (RubyRaidersNormal; Act1): AssassinRubyRaider KILLSHOT_MOVE = single 10 (A:11), 18–23 HP; AxeRubyRaider SWING_1/SWING_2 = single 5 (A:6) + 5 Block (A:6), BIG_SWING = single 12 (A:13), 20–22 HP; BruteRubyRaider BEAT_MOVE = single 7 (A:8), ROAR_MOVE = self +3 Strength, 30–33 HP; CrossbowRubyRaider FIRE_MOVE = single 14 (A:16), RELOAD_MOVE = Defend, 18–21 HP; TrackerRubyRaider TRACK_MOVE = debuff — 2 Frail, HOUNDS_MOVE = multi 1 (A:1) ×8 (A:9), 21–25 HP.
- CubexConstruct (CubexConstruct, Act1 CubexConstructNormal; 65 HP): CHARGE_UP_MOVE = buff ArtifactPower 1; REPEATER_BLAST_MOVE = single attack 7 (A:8) + self +2 Strength (two consecutive copies in the cycle); EXPEL_MOVE = multi attack 5 (A:6) ×2 + self +2 Strength. Cycle: CHARGE → BLAST → BLAST → EXPEL → BLAST… ArtifactPower 1 absorbs the first debuff applied.
- PhrogParasite (PhrogParasite, Act1 PhrogParasiteElite; 61–64 HP): INFECT_MOVE = add 3 Infection status cards to each target's discard (Infection: unplayable; if in hand at end of turn, take 3 unpowered damage); LASH_MOVE = multi attack 4 (A:5) ×4. Passive InfestedPower 4 (Single, applied on spawn): on death, spawns 4 Wrigglers (StartStunned=true) and combat cannot end while InfestedPower owner is alive — the spawn wave continues the fight.
- Wriggler (Wriggler, Act1 PhrogParasiteElite spawn wave; 17–21 HP): SPAWNED_MOVE = stun (their spawn turn does nothing); NASTY_BITE_MOVE = single attack 6 (A:7); WRIGGLE_MOVE = buff +2 Strength. Cycle NASTY_BITE ↔ WRIGGLE.
- SlitheringStrangler (SlitheringStrangler, Act1 SlitheringStranglerNormal with slimes; 53–55 HP): CONSTRICT = debuff — ConstrictPower 3 on the player: at the end of the player's turn, take 3 unpowered damage per stack; removed when the applier dies; THWACK = single attack 7 (A:8) + self Block; LASH = single attack 12 (A:13).
- VineShambler (藤蔓妖 VineShambler, Act1 VineShamblerNormal; 61 HP): GRASPING_VINES_MOVE = single attack 8 (A:9) + TangledPower 1 on the player; SWIPE_MOVE = multi attack 6 (A:7) ×2; CHOMP_MOVE = single attack 16 (A:18). TangledPower: your Attack cards gain Entangled (+1 Energy cost) for the turn; removed at end of your turn.
- Exoskeleton (Exoskeleton, Act2 ExoskeletonsNormal/Weak; 24–28 HP): SKITTER_MOVE = multi 1 ×3 (A: ×4); MANDIBLES_MOVE = single attack 8 (A:9); ENRAGE_MOVE = buff +2 Strength. Passive HardToKillPower 9: every damage instance the owner takes is capped at 9 (`ModifyDamageCap` returns 9 for the owner) — excess damage on a hit is discarded.
- Byrdonis (Byrdonis, Act1 ByrdonisElite; 81–84 HP min / 84–90 max): PECK_MOVE = multi attack 3 (A:4) ×3; SWOOP_MOVE = single attack 17 (A:19); cycle SWOOP → PECK → SWOOP… Passive TerritorialPower 1: at the end of its side's turn, +1 Strength.
- BygoneEffigy (BygoneEffigy, Act1 BygoneEffigyElite; 127 HP): SLEEP_MOVE (initial) sleep → WAKE_MOVE buff (self +10 Strength) → SLASHES_MOVE = single attack 13 (A:15), self-loop SLASHES. Passive SlowPower: each card you play this turn raises damage the owner takes from your powered attacks by +10% (counter resets at the start of the owner's side turn) — burst after cards are played.
- KinPriest (KinPriest, Act1 TheKinBoss leaderSlot; 190 HP): ORB_OF_FRAILTY_MOVE = single attack 8 (A:9) + 1 Frail; ORB_OF_WEAKNESS_MOVE = single attack 8 (A:9) + 1 Weak; BEAM_MOVE = multi attack 3 ×3; RITUAL_MOVE = buff self +2 Strength (A:3). Cycle Frail-orb → Weak-orb → BEAM → RITUAL → repeat.
- KinFollower (KinFollower, Act1 TheKinBoss slot1+slot2 — 2 flanking the priest; 58–59 HP): QUICK_SLASH_MOVE = single attack 5; BOOMERANG_MOVE = multi attack 2 ×2; POWER_DANCE_MOVE = buff self +2 Strength (A:3). Passive MinionPower 1. Cycle QUICK → BOOMERANG → POWER_DANCE.
- Vantom (Vantom, Act1 VantomBoss; 173 HP): INK_BLOT_MOVE = single attack 7 (A:8); INKY_LANCE_MOVE = multi attack 6 (A:7) ×2; DISMEMBER_MOVE = single attack 26 (A:30); PREPARE_MOVE = buff self +2 Strength. Cycle INK_BLOT → INKY_LANCE → DISMEMBER → PREPARE → repeat. Passive SlipperyPower (amount scales in multiplayer × player count): HP lost per hit capped at 1 while charges remain; each unblocked hit ≥1 consumes 1 charge.
- CeremonialBeast (CeremonialBeast, Act1 CeremonialBeastBoss; 252 HP): STAMP_MOVE = buff — PlowPower 150 (A:160) on self; PLOW_MOVE = single attack 18 (A:20) + Buff, self-loop; STUN_MOVE = stun wakeup; BEAST_CRY_MOVE = debuff — RingingPower 1 on all players; STOMP_MOVE = single attack 15 (A:17); CRUSH_MOVE = single attack 17 (A:19) + self +3 Strength (A:4). Flow: STAMP → PLOW (loop) — PlowPower: when the owner takes unblocked damage and Current HP ≤ Plow amount (150), all Strength (incl. temporary) is removed and it is stunned → STUN → BEAST_CRY → STOMP → CRUSH → BEAST_CRY… RingingPower: all your cards gain the Ringing affliction — while it lasts you may only start 1 card play per turn; removed at end of your turn (cards un-afflicted then).

## Act 2 — Hive

- BowlbugEgg (BowlbugEgg, Act2 BowlbugsNormal; 21–22 HP): BITE_MOVE = single attack 7 (A:8) + 7 Block (A:8) on protect variant.
- BowlbugNectar (BowlbugNectar, Act2 BowlbugsNormal; 35–38 HP): THRASH_MOVE = single attack 3; BUFF_MOVE = self +15 Strength (A:16); THRASH2_MOVE = single attack 3. Cycle THRASH → BUFF → THRASH2 (self-loop).
- BowlbugRock (BowlbugRock, Act2 BowlbugsNormal / SlumberingBeetleNormal; 45–48 HP): HEADBUTT_MOVE = single attack 15 (A:16); DIZZY_MOVE = stun wakeup. Passive ImbalancedPower 1: when this monster's attack is fully blocked, it becomes off-balance — after its next HEADBUTT it stuns itself (DIZZY). Fully block Headbutt to force the stun.
- BowlbugSilk (BowlbugSilk, Act2 BowlbugsNormal / SlumberingBeetleNormal; 40–43 HP): THRASH_MOVE = multi attack 4 (A:5) ×2; TOXIC_SPIT_MOVE = debuff — 1 Weak.
- Myte (Myte, Act2 MytesNormal; 61–67 HP): TOXIC_MOVE = Status ×2 (inject toxic status cards); BITE_MOVE = single attack 13 (A:15); SUCK_MOVE = single attack 4 (A:6) + self +2 Strength (A:3). Cycle TOXIC → BITE → SUCK.
- Chomper (Chomper, Act2 ChompersNormal; 60–64 HP): CLAMP_MOVE = multi attack ×2; SCREECH_MOVE = Status ×3. Passive ArtifactPower 2 at spawn.
- HunterKiller (HunterKiller, Act2 HunterKillerNormal; 121 HP): TENDERIZING_GOOP_MOVE = debuff TenderPower 1; BITE_MOVE = single attack 17 (A:19); PUNCTURE_MOVE = multi attack 7 (A:8) ×3.
- LouseProgenitor (LouseProgenitor, Act2 LouseProgenitorNormal; 134–136 HP): WEB_CANNON_MOVE = single attack 9 (A:10) + 2 Frail; POUNCE_MOVE = single attack 14 (A:16); CURL_AND_GROW_MOVE = Defend — CurlUpPower 14 (A:18) + self +5 Strength. CurlUpPower: after you hit it with a card attack, it gains Block equal to the power amount once, then the power is removed.
- Ovicopter (Ovicopter, Act2 OvicopterNormal with ToughEgg; 124–130 HP): LAY_EGGS_MOVE = summon ToughEgg (MinionPower 1 on spawn); SMASH_MOVE = single attack 16 (A:17); TENDERIZER_MOVE = single attack 7 (A:8) + 2 Vulnerable; NUTRITIONAL_PASTE_MOVE = buff self +3 Strength (A:4).
- ToughEgg (ToughEgg, Act2 OvicopterNormal spawn; 14–18 HP): NIBBLE_MOVE = single attack; HATCH_MOVE = summon (HatchPower countdown). SPAWNED turns stun.
- SlumberingBeetle (SlumberingBeetle, Act2 SlumberingBeetleNormal with BowlbugRock/Silk; 86 HP): SNORE_MOVE = sleep; ROLL_OUT_MOVE = single attack 16 (A:18) + self +2 Strength. Passives PlatingPower 15 (A:18), SlumberPower 3.
- SpinyToad (SpinyToad, Act2 SpinyToadNormal; 116–119 HP): PROTRUDING_SPIKES_MOVE = buff Thorns +5; SPIKE_EXPLOSION_MOVE = single attack 23 (A:25) then Thorns −5; TONGUE_LASH_MOVE = single attack 17 (A:19). Cycle spikes → explosion → lash.
- InfestedPrism (InfestedPrism, Act2 InfestedPrismsElite; 161 HP): JAB_MOVE = single attack 15 (A:17); RADIATE_MOVE = single attack 11 (A:13) + equal Block (11/13); WHIRLWIND_MOVE = multi attack 5 (A:6) ×3; PULSATE_MOVE = single attack 8 (A:10) + 20 Block (A:22). Passive VitalSparkPower 2 (A:3): at combat start your Skill cards gain Tainted; playing a Tainted card applies TaintedPower 2 to you.
- Entomancer (Entomancer, Act2 EntomancerElite; 145 HP): PHEROMONE_SPIT_MOVE = buff — PersonalHivePower 1 (+ Strength gains 1/2); BEES_MOVE = multi attack 3 ×7 (A:8); SPEAR_MOVE = single attack 18 (A:20). Passive PersonalHivePower 1: whenever the owner is hit by a powered attack, the attacker gets 1 Dazed added to their draw pile at a random position (per stack; Osty hits credit its owner).
- Decimillipede segments (DecimillipedeSegmentBack/Front/Middle, Act2 DecimillipedeElite; base segment 40–46 HP): WRITHE_MOVE = multi attack 5 (A:6) ×2; CONSTRICT_MOVE = single attack 8 (A:9) + 1 Weak; BULK_MOVE = single attack 6 (A:7) + self +2 Strength; REATTACH_MOVE = heal; DEAD_MOVE = death state. Passive ReattachPower 25: when a segment dies while other segments are alive, it enters DEAD state (untargetable); at end of its turn it reattaches and heals 25. When all other segments are dead, all segments fade out and die for good — clear every segment in the same window or they revive.
- TheObscura (TheObscura, Act2 TheObscuraNormal; 123 HP): ILLUSION_MOVE = summon 1 Parafright; PIERCING_GAZE_MOVE = single attack 10 (A:11); SAIL_MOVE (Wail) = buff — +3 Strength to all its teammates; HARDENING_STRIKE_MOVE = single attack 6 (A:7) + self 6 Block (A:7). After the first ILLUSION, moves branch randomly among Gaze/Wail/Hardening (no repeats).
- Parafright (Parafright, Act2 TheObscuraNormal summon; 21 HP): SLAM_MOVE = single attack 16 (A:17); repeats. Passive IllusionPower 1: revives to full HP on death via REVIVE_MOVE (see EyeWithTeeth). Kill TheObscura to stop further summons.
- ThievingHopper (ThievingHopper, Act2 ThievingHopperWeak; 79 HP): THIEVERY_MOVE = single attack 17 (A:19) + steals 1 deck card (priority: non-Imbued Uncommon → Common/Rare/Event → Basic/Quest → Ancient/Imbued) from draw/discard via SwipePower; NAB_MOVE = single attack 14 (A:16); HAT_TRICK_MOVE = single attack 21 (A:23); FLUTTER_MOVE = buff FlutterPower 5; ESCAPE_MOVE = escape (self-loop once reached). Cycle: THIEVERY → FLUTTER → HAT_TRICK → NAB → ESCAPE. Passives: EscapeArtistPower 5 — visual countdown, decrements at end of its turns; FlutterPower 5 — incoming attack damage ×0.5, each unblocked attack hit decrements 1, at 0 it is stunned and stops hovering. SwipePower: on the Hopper's death the stolen card returns to your deck as a combat reward.
- TheInsatiable 无底之欲 (TheInsatiable, Act2 TheInsatiableBoss; 321 HP): LIQUIFY_GROUND_MOVE = buff; THRASH_MOVE / THRASH_MOVE_2 = multi attack 8 (A:9) ×2; LUNGING_BITE_MOVE = single attack 28 (A:31); SALIVATE_MOVE = buff self +2 Strength (A:3). Cycle: LIQUIFY → THRASH → SALIVATE → THRASH_2 → LUNGING_BITE → THRASH…
- KaiserCrab 皇蟹 (KaiserCrab, Act2 KaiserCrabBoss): boss encounter — see `KaiserCrabBoss.cs` for slots; move ids not re-extracted here.
- KnowledgeDemon 知识恶魔 (KnowledgeDemon, Act2 KnowledgeDemonBoss; 379 HP): move cycle CURSE_OF_KNOWLEDGE_MOVE (debuff) → SLAP_MOVE → KNOWLEDGE_OVERWHELMING_MOVE → PONDER_MOVE → branch (Curse while curse counter < 3, else Slap).
  - CURSE_OF_KNOWLEDGE_MOVE: the player chooses 1 of 2 IChoosable curse cards — sets by counter: 0 = Disintegration | MindRot; 1 = Disintegration | Sloth; 2 = Disintegration | WasteAway. The chosen card is NOT added to the deck; its OnChosen applies its power immediately: Disintegration → DisintegrationPower N (6/7/8 by counter — take N unpowered damage at end of each of your turns); MindRot → MindRotPower 1 (draw −1 each turn); Sloth → SlothPower 3 (max 3 card plays per turn); WasteAway → WasteAwayPower 1 (max Energy −1). Counter increments after each Curse.
  - SLAP_MOVE = single attack 17 (A:18).
  - KNOWLEDGE_OVERWHELMING_MOVE = multi attack 8 (A:9) ×3.
  - PONDER_MOVE = single attack 11 (A:13) + heal 30 × number of players + self +2 Strength (A:3).

## Other acts — selected bosses (deterministic extracts)

- Queen (Queen, Act3 QueenBoss; 400 HP): PUPPET_STRINGS_MOVE = CardDebuff — ChainsOfBindingPower 3; YOU_ARE_MINE_MOVE = debuff — 99 Frail/Weak/Vulnerable; BURN_BRIGHT_FOR_ME_MOVE = buff; OFF_WITH_YOUR_HEAD_MOVE = multi attack 3 (A:4) ×5; EXECUTION_MOVE = single attack 15 (A:18); ENRAGE_MOVE = buff +2 Strength.
- TestSubject (TestSubject, Act3 TestSubjectBoss; multi-phase): BITE 20 (A:22), SKULL_BASH 14 (A:16), MULTI_CLAW 10 ×3, PHASE3_LACERATE 10 (A:11) ×3, BIG_POUNCE 45, BURNING_GROWL = Status burns 3 (A:5) + self +2 Strength (A:3); respawn/heal phases via RESPAWN_MOVE. Passives AdaptablePower, EnragePower 2 (A:3), PainfulStabsPower, NemesisPower.
- Aeonglass (Aeonglass, Act3 AeonglassBoss; 512 HP): EBB_MOVE = single 26 (A:32) + 33 Block; EYE_LASERS_MOVE = multi 11 (A:12) ×2; INCREASING_INTENSITY_MOVE = Status Wither 1 (A:2) + Strength ramp; ArtifactPower 3 at spawn.
- WaterfallGiant (WaterfallGiant, Act4 WaterfallGiantBoss; 240 HP): PRESSURIZE buff SteamEruption 15 (A:20) → STOMP 15 (A:16) → RAM 10 (A:11) → SIPHON heal → PRESSURE_GUN 20 (A:23, +5 per Pressure Up) → PRESSURE_UP 13 (A:14) → back to STOMP; ABOUT_TO_BLOW stun → EXPLODE deathblow.
- SoulFysh (SoulFysh, Act4 SoulFyshBoss; 211 HP): BECKON Status ×2 → DE_GAS single 16 (A:17) → GAZE single 7 (A:8) → FADE Intangible 2 → SCREAM single 13 (A:15) + 3 Vulnerable → repeat.
- LagavulinMatriarch (LagavulinMatriarch, Act4 LagavulinMatriarchBoss; 222 HP): SLEEP → SLASH 19 (A:21) → SLASH2 12 (A:14) + Block → DISEMBOWEL 9 (A:10) ×2 → SOUL_SIPHON debuff (−2 Str/Dex to player, +2 Str to self). Passives PlatingPower 12, AsleepPower 3.

## Power quick reference (exact values from Powers source)

- SlipperyPower: owner HP loss per hit ≤ 1 while charges remain; each unblocked hit ≥1 decrements 1 charge; multiplayer scales amount × players.
- TerritorialPower / HighVoltagePower: at end of owner's side turn, +Strength = amount.
- HardToKillPower 9: per-damage-instance cap on the owner = 9 (`ModifyDamageCap`); excess on a hit is discarded.
- PersonalHivePower 1: owner hit by powered attack → attacker's draw pile +1 Dazed at random position per stack.
- InfestedPower 4: on death spawn 4 stunned Wrigglers; blocks combat end while alive.
- IllusionPower: on death, revive to full Max HP via REVIVE_MOVE; untargetable while reviving; keeps buffs; applies MinionPower.
- ReattachPower 25: dead segment untargetable; heals 25 on reattach at end of turn while other segments live; all die when the rest are dead.
- ImbalancedPower: fully blocked attack → BowlbugRock off-balance → self-stun after next Headbutt.
- SlowPower: +10% damage taken from owner's attackers per card you play this turn; resets at owner's side turn start.
- ConstrictPower N: owner takes N unpowered damage at end of own turn; removed on applier death.
- TangledPower N: your Attack cards cost +N Energy (Entangled); removed at end of your turn.
- ShrinkPower: owner's attack damage ×(100−30)/100; stacks decay 1/owner-turn unless amount < 0 (infinite).
- EscapeArtistPower 5: countdown to ThievingHopper escape, −1 at end of its turns.
- FlutterPower 5: incoming attack damage ×0.5; unpowered hits don't decrement; at 0 the Hopper is stunned.
- SwipePower: holds a stolen deck card; on owner death the card returns to the victim's deck + extra card reward.
- RingingPower: all your cards gain Ringing — only the first card play each turn may start; removed at end of your turn.
- PlowPower 150/160: when owner takes unblocked damage and Current HP ≤ amount, all Strength removed + stun → BEAST_CRY phase.
- DemisePower 9: owner takes 9 unblockable damage at end of its turn (Powdered Demise potion).
- CurlUpPower N: after being hit by a player card attack, gain N Block once, then removed.
- RavenousPower: on ally death, owner gains Strength + self-stun (CorpseSlug devour).
- StockPower: on death spawn Axebot with StockAmount−1 (robot assembly chain; blocks combat end while charges remain).
- GalvanicPower N: your Power cards gain Galvanized; playing one deals N damage to you.
- VitalSparkPower N: your Skill cards gain Tainted; playing one applies TaintedPower N to you.
- SuckPower N: after owner's powered attack deals unblocked damage to any target, +N Strength per successful hit instance.
- SurprisePower: on death spawn SneakyGremlin + FatGremlin and hand over stolen gold (GremlinMerc).
- Burst/Thorns moves that apply negative Thorns (e.g. SpinyToad explosion −5) remove the buff they granted.
