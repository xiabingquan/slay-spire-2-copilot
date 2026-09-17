# Events

Deterministic event options only. Source: decompiled game code
`MegaCrit.Sts2.Core.Models.Events` + related relics/cards in
`MegaCrit.Sts2.Core.Models.Relics` / `Models.Cards` (/tmp/sts2-decomp).

Format: `- EVENT_ID (act): option → exact effect.`

Randomized values are written as `base ± range` exactly as `CalculateVars` computes them. Branches whose effects are not present in decompiled code are omitted.

Act ancients (from act sources): Overgrowth = Neow (removed unless `UnlockState.IsEpochRevealed<NeowEpoch>()`); Hive = Orobas (removed unless `OrobasEpoch`), Pael, Tezcatara; Glory = Nonupeipe, Tanx, Vakuu (ungated); Underdocks = Neow (same NeowEpoch gate). Shared ancient Darv removed unless `DarvEpoch` revealed.

## Verified events

- NEOW (Act1 Overgrowth ancient; also Act4 Underdocks): no-modifier run → 3 options = 2 random positive relics + 1 random curse-cost relic. Positive pool: ArcaneScroll, BoomingConch, FishingRod, GoldenPearl, Kaleidoscope, LeadPaperweight, LostCoffer, MassiveScroll, NeowsTorment, NewLeaf, PhialHolster, PreciseScissors, ScrollBoxes, WingedBoots; plus one XOR extra pair rolled independently: LavaRock XOR SmallCapsule (skipped if the curse relic is LargeCapsule), NutritiousOyster XOR StoneHumidifier, NeowsTalisman XOR Pomander. Curse pool: CursedPearl, HeftyTablet, LargeCapsule, LeafyPoultice, NeowsBones, PrecariousShears, SilkenTress, SilverCrucible. Conflicts removed from the positive pool: CursedPearl−GoldenPearl, HeftyTablet−ArcaneScroll, LeafyPoultice−NewLeaf, PrecariousShears−PreciseScissors. Each relic also filtered by `IsAllowedAtNeow`. With run modifiers active, Neow instead offers each modifier's `GenerateNeowOption` in sequence.
- PAEL (Act2 Hive ancient): 3 relic options rolled as: (1) random of PaelsFlesh / PaelsHorn / PaelsTears; (2) pool = PaelsWing + (PaelsClaw if ≥3 Goopy-enchantable Defend cards) + (PaelsTooth if ≥5 removable cards), pool then doubled + PaelsGrowth always → random pick; (3) pool = PaelsEye / PaelsBlood + (PaelsLegion if you have no event pet) → random pick.
  - PaelsFlesh: +1 max Energy from combat turn 3 onward.
  - PaelsHorn: on obtain, add 2 Relax cards to your deck.
  - PaelsTears: if you ended your last turn with unspent Energy, +2 Energy at the start of your next turn.
  - PaelsWing: card rewards gain a SACRIFICE alternative; every 2 sacrifices grants the next relic from the front of your relic queue.
  - PaelsClaw: on obtain, every Defend-tagged card in your deck gains Goopy 1 (Goopy: card gains Exhaust; +Amount−1 bonus Block; Amount +1 each time the card is played).
  - PaelsTooth: on obtain, remove up to 5 upgradeable cards (stored); after each combat, 1 random stored card returns to your deck upgraded.
  - PaelsEye: once per combat, the first time you end your turn having played 0 cards, exhaust your hand and take an extra turn.
  - PaelsBlood: +1 card draw each turn.
  - PaelsGrowth: on obtain, choose 1 deck card → Enchant Clone 4; rest sites gain a Clone rest option (Clone duplicates cards at rest).
  - PaelsLegion: adds the PaelsLegion pet; while ready, the first card play each combat that grants Block doubles that Block (×2), then cooldown 2 turns.
- TEA_MASTER (Act1-2; requires all players Gold ≥ 150): BONE_TEA → pay 50 Gold, gain BoneTea (locked without 50g) — for 1 combat: on turn 1, upgrade every card in your hand; EMBER_TEA → pay 150 Gold, gain EmberTea (locked without 150g) — for 5 combats: +2 Strength when you enter a combat room; TEA_OF_DISCOURTESY → free, gain TeaOfDiscourtesy — for 1 combat: before combat starts, 2 Dazed added to your draw pile at random positions.
- THE_LEGENDS_WERE_TRUE (Act1 only; all players HP ≥ 10 with non-empty deck): NAB_THE_MAP → add SpoilsMap to your deck (Quest, Unplayable; SpoilsActIndex=1 — marks a spoils room on the Act-2 map worth 600 Gold); SLOWLY_FIND_AN_EXIT → take 8 unblockable unpowered damage, gain 1 random potion from your character pool + shared pool. Run-19 live (2026-09-17): SpoilsMap cashed at the Act-2 treasure room (8,3) — gold jumped 65→708 (+643, ~600 spoils + chest gold); the quest card left the deck on cash-in. Removal services must never target SpoilsMap before the Act-2 treasure.
- MORPHIC_GROVE (shared; requires all players Gold ≥ 100 and ≥2 transformable cards): GROUP → lose ALL Gold (stolen), choose 2 deck cards and transform each at random; LONER → +5 Max HP.
- LUMINOUS_CHOIR (requires all players Gold ≥ cost and available relics; cost = 149 − rng 0..49 → 100–149 Gold): REACH_INTO_THE_FLESH → remove 2 chosen deck cards, add SporeMind curse (1 Energy, Curse, Exhaust keyword) to your deck; OFFER_TRIBUTE → pay the cost, gain the next relic from the front of your relic queue (locked without the gold).
- JUNGLE_MAZE_ADVENTURE (shared): SOLO_QUEST → take 18 unblockable unpowered damage, gain 150 ± rng −15..+15 Gold (135–165); JOIN_FORCES → gain 50 ± rng −15..+15 Gold (35–65), no damage.
- WHISPERING_HOLLOW (requires all players Gold ≥ 44): GOLD → pay 35 ± rng −9..+9 Gold (26–44), gain 2 random potions; HUG → take 9 unblockable unpowered damage, choose 1 deck card and transform it at random.
- THE_LANTERN_KEY (shared; combat layout): RETURN_THE_KEY → +100 Gold; KEEP_THE_KEY → FIGHT → MysteriousKnightEventEncounter combat; on victory each player gains a LanternKey quest card (Unplayable; in Act 2 (act index 2) it forces unknown map points to be Event rooms and redirects the next event to WarHistorianRepy).
- AROMA_OF_CHAOS: LET_GO → choose 1 deck card, transform it at random; MAINTAIN_CONTROL → choose 1 deck card, upgrade it.
- FAKE_MERCHANT (Act index ≥1; solo only; requires Gold ≥ 100 or owning a FoulPotion): custom shop layout; stocks 6 of 9 fake relics rolled from FakeAnchor, FakeBloodVial, FakeHappyFlower, FakeLeesWaffle, FakeMango, FakeOrichalcum, FakeSneckoEye, FakeStrikeDummy, FakeVenerableTeaSet; relic cost ≈50 Gold (run-20 live: FakeMango 54, FakeLee'sWaffle 47 — not flat 50). FoulPotion thrown at the merchant → FakeMerchantEventEncounter fight; rewards = FakeMerchantsRug + every still-stocked fake relic. Run-20 buy rule: FakeMango (+3 Max HP) and FakeLee'sWaffle (heal 10% Max on pickup) are positive; FakeSneckoEye (Confused at combat start) is a detriment — never buy.

## Additional events with decompiled option values

- ABYSSAL_BATHS: vars MaxHp +2 / unblockable 3 damage / heal 10 — Immerse and Abstain options present (exact per-option binding partially internal); Linger/ExitBaths handlers exist.
- AMALGAMATOR (requires ≥2 Strike-tagged and ≥2 Defend-tagged cards): CombineStrikes → remove Strikes, add UltimateStrike; CombineDefends → remove Defends, add UltimateDefend. Live (run-18 A1 2026-09-17): CombineDefends removed exactly 2 Defends from a 4-Defend deck and added UltimateDefend (1-cost, 11 Block) — net deck -1 card; a deck_select overlay lets you pick which copies, choose then proceed. Strike-tagged removal includes POMMEL_STRIKE copies — combining Strikes also eats draw engines.
- BRAIN_LEECH (Act index < 2): ShareKnowledge → add cards via card-pile add; Rip → take 5 unblockable damage, get 1 reward (choice screens: 1 pick from 5).
- BATTLEWORN_DUMMY (Act3; 战痕累累的训练假人): Setting1/2/3 → fight BattleFriendV1/V2/V3 — 75/150/300 HP flat in single-player Act3 (scaleHpForMultiplayer applied by the event; observed unscaled). TimeLimitPower 3 all tiers; dummy uses NOTHING_MOVE (never attacks) — pure DPS race; at TimeLimit 1 the dummy Escapes and RanOutOfTime=true → no reward. Rewards on kill: Setting1 → 1 potion; Setting2 → upgrade 2 random deck cards; Setting3 → 1 relic (RelicFactory front).
- BYRDONIS_NEST (requires no event pet): EAT → +7 Max HP; TAKE → add ByrdonisEgg card to deck.
- BUGSLAYER: Extermination → Exterminate card; Squash → Squash card (option effects add those cards).
- COLORFUL_PHILOSOPHERS (requires >1 unlocked character card pool): offers 3-card reward via OfferCustom.
- COLOSSAL_FLOWER (all players HP ≥ 19): extract prize options pay Gold from `_prizeCosts`; ObtainPollinousCore → PollinousCore relic; ReachDeeper takes damage then deeper prizes.
- CRYSTAL_SPHERE (Act >0; all players Gold ≥ 100): UncoverFuture → pay 50 Gold (3-card prophesize flow); PaymentPlan → add Debt curse (6-count plan). Run-15 live: minigame is an 11×11=121-cell grid, DivinationCount=3 clicks; hidden items seed along the corners' rows/cols at random positions — clicking the corners themselves (cells 0/10/120) yielded zero rewards; treat clicks as ~3/121 lottery, not corner-guaranteed.
- DENSE_VEGETATION: TrudgeOn → unblockable damage + Gold; Rest → mimic rest-site heal; Fight → DenseVegetationEventEncounter. Vars include HpLoss 8.
- DOLL_ROOM (Act index 1): ChooseRandom → obtain a doll relic; TakeSomeTime → 5 unblockable damage; Examine → 15 unblockable damage.
- DOORS_OF_LIGHT_AND_DARK: Light → upgrade 2 cards; Dark → remove 2 cards.
- DROWNING_BEACON: BottleOption → GlowwaterPotion via reward; ClimbOption → lose 13 Max HP, gain FresnelLens relic.
- ENDLESS_CONVEYOR (all players Gold ≥ 120): dish handlers: ClamRoll heal 10; Caviar +4 Max HP; GoldenFysh +75 Gold; SeapunkSalad adds FeedingFrenzy; JellyLiver transform; SpicySnappy upgrade; ObserveChef upgrade; grab cost 40 Gold.
- FIELD_OF_MAN_SIZED_HOLES (requires PerfectFit-enchantable card): Resist → remove cards + add Normality curses ×2; EnterYourHole → Enchant PerfectFit on a card.
- GRAVE_OF_THE_FORGOTTEN (requires enchantable cards): Confront → add Decay curse + Enchant SoulsPower; Accept → ForgottenSoul relic.
- HUNGRY_FOR_MUSHROOMS: BigMushroom → BigMushroom relic; FragrantMushroom → FragrantMushroom relic.
- INFESTED_AUTOMATON: Study → add 1 random Power card from your character pool to deck; TouchCore → add 1 random character-pool card filtered by EnergyCost (decomp delegate on `c.EnergyCost`) to deck.
- LOST_WISP: Search → +60 Gold; Claim → add Decay curse + LostWisp relic.
- POTION_COURIER (Act >0): GrabPotions / Ransack → potion rewards (FoulPotions var 3).
- PUNCH_OFF (TotalFloor ≥ 6): Nab → add Injury curse + reward; TakeThem → fight PunchOffEventEncounter.
- RANWID_THE_ELDER (Act >0; all players Gold ≥ 100, ≥1 relic, ≥1 potion): GiveGold → pay 100 Gold, obtain a relic; GivePotion → relic; GiveRelic → remove a relic, obtain another.
- REFLECTIONS: TouchAMirror → downgrade then upgrade a card (net re-roll of upgrade); Shatter → add card + BadLuck curse.
- RELIC_TRADER (Act >0; all players ≥5 valid relics): Top/Middle/Bottom → trade (remove owned relic, obtain new one of that slot).
- ROOM_FULL_OF_CHEESE (Act index < 2): Gorge → add card; Search → take 14 unblockable damage, gain ChosenCheese relic.
- TANX (Act3 ancient boon room; 坦克斯): offers 3 random RelicOptions drawn from a pool of 9 — Claws, Crossbow, IronClub, MeatCleaver, Sai, SpikedGauntlets, TanxsWhistle, ThrowingAxe, WarHammer — plus TriBoomerang when the deck holds ≥3 Instinct-enchantable cards (then 3 of 10 shown). TanxsWhistle → adds Whistle card to deck (3-cost Attack, Exhaust, 33 dmg + Stun target; upgrade +11 dmg). SpikedGauntlets → +1 Max Energy, BUT your Power cards cost +1 in combat (anti-synergy with power-dense decks). WarHammer → after each Elite combat victory, upgrade 4 random upgradable deck cards.
- ROUND_TEA_PARTY (all players HP ≥ 12): EnjoyTea → RoyalPoison relic + heal; PickFight → 11 unblockable damage + RoyalPoison.
- SAPPHIRE_SEED: Eat → heal 9 + upgrade; Plant → Enchant Sown.
- SELF_HELP_BOOK (自助指南): three options decoded (perplexity 2026-09-18, run-23 live): **READ_THE_BACK → Enchant an Attack with Sharp 2 (+2 dmg); READ_PASSAGE → Enchant a Skill with Nimble 2 (+2 Block); READ_ENTIRE_BOOK → Enchant a Power with Swift 2 (draw 2 when played)**. Run-20 live: READ_PASSAGE pool was skills-only (4× Defend + Second Wind); Second Wind Nimble value +2 Block per exhausted card (5→7; smith on enchanted copy 7→9, NOT table +7). Run-23 live: READ_ENTIRE_BOOK auto-targeted the deck's only Power (Rupture) — Swift 2 draw-on-play live-confirmed in combat. Older two-key observation (READ_THE_BACK/READ_PASSAGE only) was partial UI coverage.
- SLIPPERY_BRIDGE (TotalFloor > 6; removable card required): Overcome → remove 1 random card; HoldOn → take HP loss = 3 + times HoldOn was already chosen this event (3, 4, 5, … escalating); the event loops HoldOn vs Overcome until Overcome is picked. Run-19 live: there is NO exit other than Overcome — delaying only stacks HP tax on top of the same random removal; the removal pool is the full deck (a freshly-rewarded card was removed the same floor it was picked).
- SPIRALING_WHIRLPOOL (Spiral-enchantable card required): ObserveTheSpiral → Enchant Spiral; Drink → heal.
- SPIRIT_GRAFTER: LetItIn → heal 25 + add Metamorphosis card; Rejection → upgrade + take 10 damage. Run-15 live: LetItIn at 12 HP ended at 57 (+45 observed, refs say heal 25 — Metamorphosis-on-pickup or A1 scaling may add more; recheck if it matters).
- STONE_OF_ALL_TIME (Act 1; all players ≥1 potion): Lift → +10 Max HP (drink-potion path); Push → 6 damage + enchant (+8 Vigorous var).
- SUNKEN_STATUE: GrabSword → SwordOfStone relic; DiveIntoWater → +111 Gold, take 7 damage.
- THE_FUTURE_OF_POTIONS (live 2026-09-17 run-12, Act 2): three options "deposit
  a Rare / Uncommon / Common potion" — the chosen potion is consumed; reward =
  1 card pick from your class pool (live: deposited a Common Speed Potion →
  Necrobinder pool pick of WISP / INVOKE / NEGATIVE_PULSE). Deposit the
  least-valuable potion tier you hold.
- SUNKEN_TREASURY: FirstChest → +60 Gold; SecondChest → +333 Gold + Greed curse.
- SYMBIOTE (Act >0): Approach → Enchant Corrupted on an Attack card — Corrupted enchant: powered attack damage ×1.5, but on play its owner takes 2 unblockable unpowered damage; KillWithFire → transform 1 chosen card.
- TABLET_OF_TRUTH: Smash → heal 20. Decipher → escalating Max-HP chain (run-20 A1 live, 2026-09-18): stage costs −3 / −6 / −12 Max HP (doubling; loc keys DECIPHER_1/2/3, option 继续解读 each stage), Give Up (放弃) available at every stage; **no reward was observed on any stage completed nor on Give Up** — as experienced it is a pure Max-HP sink; treat the old one-line "lose 3 Max HP + upgrade path" summary as wrong, and pick Smash unless a reward path is independently confirmed. Run-20 paid 21 Max HP (85→64) across three stages + Give Up for nothing.
- THE_ARCHITECT (Act3, post-boss story event at the Act3 boss node) — **EA ending screen**: reaching this event means the Act-3 boss is dead and all currently shipped run content is cleared. The game is Early Access and the Architect boss fight is NOT implemented yet; the PROCEED → HP 0 flow is the EA placeholder ending. Mechanics: dialogue-line walker — one respond/continue option per line (textKey THE_ARCHITECT.dialogue.N); Ironclad line is Threaten → Continue → PROCEED; PROCEED sets player HP to 0 → game_over at floor 48. Decomp note (TheArchitect.cs): WinRun() plays attack VFX only (player hits Architect for Score; Architect 'attacks back' with VFX — AnimArchitectAttackIfNecessary issues NO CreatureCmd.Damage) then RunManager.ActChangeSynchronizer.SetLocalPlayerReady(); TheArchitectEventEncounter spawns only the Architect dummy (9999 HP, NOTHING_MOVE loop, HiddenIntent) — consistent with an unimplemented boss. Ironclad dialogues: 3 visits, all EndAttackers=Both; visit selection keys off profile TotalWins/Wins via LoadDialogue().
- THIS_OR_THAT: Plain → take 6 damage + Gold; Ornate → obtain a relic + add Clumsy curse.
- TINKER_TIME: choose card type + rider; riders include 12 damage / 8 block / 2 Weak / 2 Vulnerable / 3-hit violence; adds MadScience card.
- TRASH_HEAP (all players HP > 5): DiveIn → 8 damage + relic; Grab → +100 Gold + add card.
- TRIAL: Accept/Reject then witness branches — MerchantGuilty: Regret curse + relic; MerchantInnocent: Shame curse + upgrade; NobleGuilty: heal; NobleInnocent: Regret + Gold; NondescriptGuilty: Doubt + reward; NondescriptInnocent: Doubt + transform.
- UNREST_SITE (all players HP ≤ 70% Max): Rest → heal + curses; Kill → −8 Max HP + relic.
- WAR_HISTORIAN_REPY (IsAllowed false normally — LanternKey-gated): UnlockChest → reward; UnlockCage → HistoryCourse relic; LanternKey quest completion removes the key card.
- WATERLOGGED_SCRIPTORIUM (all players Gold ≥ 55): BloodyInk → +6 Max HP; TentacleQuill → pay 55 Gold, Enchant Steady; PricklySponge → pay 99 Gold, Enchant Steady + card options.
- WELCOME_TO_WONGOS (labeled Act 1 in gates; also observed spawning Act 2, run-6 2026-09-17 — treat act label as soft; all players Gold ≥ 100): BuyBargainBin → pay 100 Gold, relic; BuyFeaturedItem → pay 200 Gold, relic; BuyMysteryBox → pay 300 Gold, WongosMysteryTicket (3 random relics after 5 combats); Leave.
- WELLSPRING: Bottle → potion reward; Bathe → remove cards (curses var 1 — Guilty add handler exists).
- WOOD_CARVINGS (requires removable Basic card): Snake → Enchant Slither; Bird → transform into Peck; Torus → transform into ToricToughness. Slither enchant effect (perplexity research 2026-09-18, run-22): the enchanted card's cost randomizes from 0 to 3 each time you draw it; cost-changing effects applied after the randomization can still raise the final cost above 3. Run-22 chose Bird→Peck (2 dmg ×3, Strike-tagged multi-hit that scales with Strength) over Snake/Slither (variance anti-synergy with a combo deck) and Torus→ToricToughness (2-cost 5 Block + regain that Block next 2 times Block is cleared).
- ZEN_WEAVER (all players Gold ≥ 125): BreathingTechniques → pay 50 Gold, add Enlightenment; EmotionalAwareness → pay 125 Gold path; ArachnidAcupuncture → pay 250 Gold, remove cards path.

## Ancient events without extracted option tables

DARV, NONUPEIPE, TEZCATARA, VAKUU exist as `AncientEventModel`s in the act pools but their option handlers are not present in the decompiled event sources reviewed here — omitted. (TANX extracted 2026-09-17 run-6 — see its entry above. OROBAS extracted via perplexity research 2026-09-17 run-19 — see its entry below.)

- OROBAS (Act 2 Hive ancient; researched via perplexity 2026-09-17, run-19 live pick): ELECTRIC_SHRYMP → on pickup, choose 1 Skill card to enchant with **Imbued** (Imbued = the card automatically plays at combat start, before energy is spent — effectively free every fight); DRIFTWOOD → you may reroll each card reward once; TOUCH_OF_OROBAS → replace your starter relic with its Ancient version (IRONCLAD: Burning Blood +6/combat → **BlackBlood heal 12/combat**; run-19 live-verified: relic id swaps, combat-end heals 12 + ChosenCheese +1 Max HP stack each fight).
- TEZCATARA options (researched via perplexity 2026-09-17, run-18 live pick): YUMMY_COOKIE 美味饼干 → gain relic YummyCookie and upgrade 4 cards of your choice (deck_select overlay: choose cards then proceed to confirm); STORYBOOK 故事书 → add 1 Brightest Flame to your deck; SEAL_OF_GOLD 黄金印 → relic SealOfGold: at start of your turn, spend 5 Gold to gain 1 Energy (no effect if gold < 5; one source says 3 — 5 is the better-attested value). **Additional boon pool options (run-23 live 2026-09-18, relics.md cross-ref)**: NUTRITIOUS_SOUP 营养汤 → relic NutritiousSoup: on pickup enchant all Strike-tagged Basic cards with Tezcatara's Ember (Ember = **cost 0, +3 dmg, Eternal** — perplexity 2026-09-18); TOASTY_MITTENS 烘焙手套 → relic ToastyMittens: each turn before hand draw, exhaust top card of draw pile + gain 1 Strength (run-23 picked — passive Str engine, exhaust also thins); GOLDEN_COMPASS 黄金罗盘 → relic GoldenCompass: on pickup replace the Act 2 map with a single special path; VERY_HOT_COCOA 烫嘴可可 → +4 energy turn 1 (run-18/20/22 picks, Lantern-stacking live-verified run-22).

## Event handling notes

- screen `event` in run state lists options via `screen_detail.options` (kind=event_option); pick via `act choose index`; locked options show IsLocked.
- `IsAllowed` gates: events only spawn when their decompiled preconditions hold (act index, gold, HP, deck contents) — listed per event above where present.
- Randomized event vars use run rng at event open (`CalculateVars`) — treat `base ± range` as the deterministic offer window.

- Whirlpool live notes (2026-09-17): Spiral enchant = EnchantPlayCount +1 (card resolves twice per play; decomp Spiral.cs — Basic Strike/Defend tags only; observed: Enchant Defend 5→"two resolves" = 10 base, scales with Dex per resolve, stacks with Smith upgrade +3 per resolve). Drink heal value is data-driven (DynamicVars.Heal — not decomp-hardcoded). Pael live: Pael's Horn = +2 RELAX cards (RELAX: 3c skill Exhaust 15 Block + next turn draw 2 + 2 Energy); boon room also full-restored HP 9→70 on Act2 entry (HP restore appears inherent to the act-start ancient room regardless of relic choice).
