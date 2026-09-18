# Potions

Deterministic potion effects. Source: decompiled game code
`MegaCrit.Sts2.Core.Models.Potions` (/tmp/sts2-decomp). Every listed class in
that folder is covered. Numbers are the class `CanonicalVars` base values.

Format: `- Name (rarity, usage, target): exact effect.`

Usage: `combat` = CombatOnly; `anytime` = AnyTime; `auto` = Automatic (fires on its trigger without being drunk); `event` = only obtainable from events, never in potion pools.
Target: `self` / `any player` / `any enemy` / `ALL enemies`. ALL-enemies potions select every hittable enemy automatically — do not send a single-target id.

## Potions

- Ashwater (Uncommon, combat, self): exhaust any number of cards in your hand.
- Attack Potion (Common, combat, self): choose 1 of 3 distinct Attack cards generated from your character card pool (may skip); the card is added to hand and is free this turn.
- Beetle Juice (Rare, combat, any enemy): apply ShrinkPower 4 to the target. ShrinkPower: the owner's attack damage is ×0.7 (−30%); 1 stack is removed at the end of the owner's turn; negative amount = infinite, no decay. With 4 stacks: −30% attack damage for 4 of its turns.
- Blessing of the Forge (Uncommon, combat, self): upgrade every upgradable card in your hand for the combat.
- Block Potion (Common, combat, any player): gain 12 Block.
- Blood Potion (Common, anytime, any player): heal 20% of Max HP.
- Bone Brew (Uncommon, combat, self): Summon Osty with 15.
- Bottled Potential (Rare, combat, any player): move your hand into the draw pile, shuffle the draw pile, draw 5.
- Clarity Extract (Uncommon, combat, any player): draw 1; apply ClarityPower 3 — draw +1 card at the start of each of your next 3 turns (decrements at your turn start).
- Colorless Potion (Common, combat, self): choose 1 of 3 distinct Colorless-pool cards (may skip); add to hand, free this turn.
- Cosmic Concoction (Rare, combat, self): add 3 distinct upgraded Colorless-pool cards to hand.
- Cunning Potion (Uncommon, combat, self): add 3 upgraded Shivs to hand.
- Cure All (Uncommon, combat, any player): gain 1 Energy; draw 2.
- Dexterity Potion (Common, combat, any player): +2 Dexterity for the combat.
- Distilled Chaos (Rare, combat, self): play the top 3 cards of your draw pile.
- Droplet of Precognition (Rare, combat, self): choose 1 card from your draw pile; add it to hand.
- Duplicator (Uncommon, combat, self): apply DuplicationPower 1 — the next card you play this turn is played 1 extra time; removed at end of turn. Run-28 live: DUPLICATION_POWER:1 same state read on use; next Bash+ resolved twice — TheInsatiable 146→76 (single act 70 damage: (10+10str)×PaperPhrog-mult×2 plays + Vulnerable applied twice 5→11); power gone at end of turn as documented.
- Energy Potion (Common, combat, any player): gain 2 Energy.
- Entropic Brew (Rare, anytime, self): fill every empty potion slot with a random potion.
- Essence of Darkness (Rare, combat, self): channel 1 Dark orb per orb slot you have.
- Explosive Ampoule (Common, combat, ALL enemies): deal 10 damage to ALL enemies (automatic multi-target; do not send a target id).
- Fairy in a Bottle (Rare, auto, self): when you would die, this is discarded instead and you heal to 30% Max HP (minimum 1). Run-28 live: consumed when Inferno start-of-turn self-damage killed at HP 1 — HP set to 29/98 ≈ 29.6% of Max, consistent with the 30%-Max rule; potion vanished from belt same state read.
- Fysh Oil (Uncommon, combat, any player): +1 Strength and +1 Dexterity for the combat. Run-28 live: STRENGTH_POWER +1 and DEXTERITY_POWER:1 appeared same state read on use; Dex +1 raised subsequent card-block values by 1 each (Defend 5→6 class) same combat.
- Fire Potion (Common, combat, any enemy): deal 20 damage.
- Flex Potion (Common, combat, any player): apply FlexPotionPower +5 Strength — lose 5 Strength at end of this turn (temporary Strength).
- Focus Potion (Common, combat, self): +2 Focus.
- Fortifier (Uncommon, combat, any player): gain Block equal to 2× your current Block (your Block becomes 3×).
- Foul Potion (Event, anytime): in combat — deal 12 damage to every non-pet creature (including you); in a Merchant room — gain 100 Gold; in the FakeMerchant event — starts the FakeMerchant fight. **Run-27 live (A1 2026-09-18)**: combat use is a same-window AoE tool — 12 damage killed a 12-HP Decimillipede segment outright and set up a Thunderclap finish (all 3 segments at 0, REATTACH never resolved); the self-damage triggered Rupture (+Str per Amount live). Never use in a FakeMerchant room (fight clause) — holding it for a real Merchant room (+100g) is the economy line.
- Fruit Juice (Rare, anytime, any player): +5 Max HP.
- Fysh Oil (Uncommon, combat, any player): +1 Strength and +1 Dexterity for the combat.
- Gambler's Brew (Uncommon, combat, self): discard any number of hand cards, then draw that many.
- Ghost in a Jar (Rare, combat, any player): +1 Intangible.
- Gigantification Potion (Rare, combat, any player): apply GigantificationPower 1 — your next powered Attack card this combat deals ×3 damage; consumed by that attack.
- Glowwater Potion (Event, combat, self): exhaust your hand; draw 10.
- Heart of Iron (Uncommon, combat, any player): +7 Plating.
- King's Courage (Uncommon, combat, any player): Forge 15.
- Liquid Bronze (Uncommon, combat, any player): +3 Thorns.
- Liquid Memories (Rare, combat, self): choose 1 card from your discard pile; add it to hand and it is free this turn. Run-25 live (A1 2026-09-18): played with an EMPTY discard pile (all cards in hand/draw) — potion consumed with NO card_choice and no effect (total whiff). Check piles before use; unusable when discard=0.
- Lucky Tonic (Rare, combat, any player): +1 Buffer.
- Mazaleth's Gift (Rare, combat, any player): +1 Ritual.
- Orobic Acid (Rare, combat, self): add 1 random Attack, 1 random Skill, 1 random Power from your character card pool to hand; all 3 are free this turn.
- Poison Potion (Common, combat, any enemy): apply 6 Poison.
- Pot of Ghouls (Rare, combat, self): add 2 Soul cards to hand.
- Potion of Binding (Uncommon, combat, ALL enemies): apply 1 Weak and 1 Vulnerable to ALL enemies.
- Potion of Capacity (Uncommon, combat, self): +2 orb slots.
- Potion of Doom (Common, combat, any enemy): apply 33 Doom.
- Potion-Shaped Rock (Token, combat, any enemy): deal 15 damage.
- Powdered Demise (Uncommon, combat, any enemy): apply DemisePower 9 — the target takes 9 unblockable, unpowered damage at the end of each of its turns.
- Power Potion (Common, combat, self): choose 1 of 3 distinct Power cards from your character card pool (may skip); add to hand, free this turn.
- Radiant Tincture (Uncommon, combat, any player): gain 1 Energy now; apply RadiancePower 3 — +1 Energy on each of your next 3 energy resets.
- Regen Potion (Uncommon, combat, any player): +5 Regen.
- Shackling Potion (Rare, combat, ALL enemies): apply ShacklingPotionPower 7 to ALL enemies — temporary −7 Strength, lost at end of their turn.
- Ship in a Bottle (Rare, combat, any player): gain 10 Block; apply BlockNextTurnPower 10 — the first time your Block is cleared, gain 10 Block again (once).
- Skill Potion (Common, combat, self): choose 1 of 3 distinct Skill cards from your character card pool (may skip); add to hand, free this turn.
- Snecko Oil (Rare, combat, any player): draw 7; randomize the cost of every non-X card currently in your hand.
- Soldier's Stew (Rare, combat, any player): every card with the Strike tag in your combat piles gains +1 Replay for this combat. Run-16 live: the Replay behaves as a one-shot charge per card at use-time — strikes already in hand/draw when the potion is drunk replay once when played; strikes drawn later in the same combat resolved a single time.
- Speed Potion (Common, combat, any player): apply SpeedPotionPower +5 Dexterity — lose 5 Dexterity at end of this turn (temporary Dexterity).
- Stable Serum (Uncommon, combat, any player): apply RetainHandPower 2 — your hand is not flushed at end of turn for the next 2 turns.
- Star Potion (Common, combat, self): +3 stars (★).
- Strength Potion (Common, combat, any player): +2 Strength for the combat.
- Swift Potion (Common, combat, any player): draw 3.
- Touch of Insanity (Uncommon, combat, self): choose 1 hand card that costs Energy or stars; it costs 0 for the rest of combat.
- Vulnerable Potion (Common, combat, any enemy): apply 3 Vulnerable.
- Weak Potion (Common, combat, any enemy): apply 3 Weak.

## Notable code notes

- Attack / Skill / Power / Colorless potions call `CardSelectCmd.FromChooseACardScreen(..., canSkip: true)` — the choice screen can be skipped; generated cards are `SetToFreeThisTurn()`.
- ExplosiveAmpoule and PotionOfBinding iterate `CombatState.HittableEnemies` — targeting is automatic; the bridge must not pass `target_combat_id`.
- PotionOfBinding's OnUse reads its vars swapped (`WeakPower` applied with the Vulnerable value and vice versa) but both values are 1 — effect is 1 Weak + 1 Vulnerable on all enemies.
- FlexPotionPower / SpeedPotionPower are subclasses of Temporary Strength/Dexterity; ShacklingPotionPower is a negative-side temporary Strength.
- BloodPotion, FruitJuice, EntropicBrew are `AnyTime`; FairyInABottle is `Automatic`.

- Potion-Shaped Rock (PetrifiedToad spawn, combat, any enemy): deal 15 unpowered damage. Petrified Toad grants 1 at every combat start; slots can stack multiple rocks. Targeted like a normal single-enemy potion (pass target_combat_id); potion slot reindexes after each use.
- Fruit Juice (FRUIT_JUICE): **+5 Max HP — RESOLVED** (perplexity 2026-09-18, multi-source incl. namu/untapped/sportskeedia; STS2 behavior matches STS1). The 2026-09-17 "UNRESOLVED" note is retired. Also usable as StoneOfAllTime Lift fuel (+10 Max HP event path, run-23 live — better than drinking it alone). Seen as shop stock A1 Act1 (run-18); combat reward (run-23).
- Fysh Oil (Uncommon, anytime, self): **+1 Strength and +1 Dexterity immediately** (perplexity 2026-09-18 + run-30 live: Str 4→5 / Dex 1→2 same state read). Combat-scoped stat buff.
- Speed Potion (Common class, combat): **+5 Dexterity combat buff** — run-30 live: DEXTERITY_POWER 1→6 with SPEED_POTION_POWER:5 counter; **NOT a draw potion** (distinct from Swift Potion below); Dex boost observed to expire by next turn (combat-buff class, turns-capped — treat as same-turn/short window value).
- Cure All run-34 CORRECTION: **gain 1 Energy; draw 2** — the name reads like a heal but the effect is burst-class (+1e + draw 2). Run-34 memory initially misfiled it as a heal; treat CURE_ALL as a burst/dig tool (run-34 T2 GlobeHead use drew Defend+TwinStrike into a survival hand). Archive any "CureAll heals" notes as WRONG.
- Explosive Ampoule run-34 live: 10 dmg ALL enemies (auto-target, omit target id) — Entomancer T4 finisher: card chain brought boss to 4 HP, Ampoule 10 killed it same turn; run-24 BEES 4×7=28 death number never resolved.
- Speed Potion + Dexterity Potion stack run-34 live: DexPotion +2 (persistent) then SpeedPotion +5 (same-turn counter SPEED_POTION_POWER:5) → DEXTERITY_POWER:7 same read; Defend under Frail 2 resolved 9 block live; Speed component expired next turn (Dex back to 2) — run-30 expiry note reconfirmed exact.
- Potion of Binding run-34 live: applied Weak 3 + Vuln 1 to target (LouseProgenitor intent 19→14 weakened live); archive "Weak 1 + Vuln 1 ALL" — live single-target value was Weak 3 class; treat stack counts as live-read; ALL-target rule held (no target id needed).

- Clarity (Clarity Extract class, combat): **draw 1 card now + draw 1 extra at the start of each of your next 3 turns** (perplexity 2026-09-18 + run-30 live: CLARITY_POWER:3 counter appeared, one card drawn on use, counter ticked 3→2 next turn).
- Heart of Iron (potion): applies **PLATING_POWER 7 to the player** — see powers.md player-Plating entry for timing (mid-combat use grants block at end of player side turn).
- Run-32 live (A1, 2026-09-18, Seed random): **Blood Potion heal exact at 80 Max = +16 HP** (30→46, boss fight T7 — 20% Max formula confirmed). **Skill Potion pool live at Act1 Boss T6**: offered PrimalForce / **Impervious** / Offering — Impervious picked, generated free (cost=0) and granted **28 Block** (30 base −2 Dex tax at the time); card-choice potions set the generated card free-this-turn even when the card's printed cost is 2-3. **Colorless Potion pool live at Act1 Boss T8**: offered Finesse / **Eternal Armor** / Bolas — Eternal Armor picked, free (printed cost 3 waived), granted **PLATING_POWER 9** on the player (block at end of turn 9, then −1/turn — the structural anti-Dex-tax block class vs stat-drain bosses). Fire Potion 20-damage live (CorpseSlug finish). Potion slots full @Control@ dead-button class did NOT appear this run — card-reward buttons stayed claimable at 3/3 potions.
