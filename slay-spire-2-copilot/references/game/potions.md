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
- Cure All (Uncommon, combat, any player): gain 1 Energy; draw 2. Despite the name this is NOT a heal — burst/dig class (+1e + draw 2); any "CureAll heals" note is wrong.
- Dexterity Potion (Common, combat, any player): +2 Dexterity for the combat.
- Distilled Chaos (Rare, combat, self): play the top 3 cards of your draw pile.
- Droplet of Precognition (Rare, combat, self): choose 1 card from your draw pile; add it to hand.
- Duplicator (Uncommon, combat, self): apply DuplicationPower 1 — the next card you play this turn is played 1 extra time; removed at end of turn. DUPLICATION_POWER:1 visible same state read on use; the next attack resolves twice (e.g. Bash+ doubled); power gone at end of turn as documented.
- Energy Potion (Common, combat, any player): gain 2 Energy.
- Entropic Brew (Rare, anytime, self): fill every empty potion slot with a random potion.
- Essence of Darkness (Rare, combat, self): channel 1 Dark orb per orb slot you have.
- Explosive Ampoule (Common, combat, ALL enemies): deal 10 damage to ALL enemies (automatic multi-target; do not send a target id).
- Fairy in a Bottle (Rare, auto, self): when you would die, this is discarded instead and you heal to 30% Max HP (minimum 1). Consumed when killed at HP 1 by start-of-turn self-damage — HP set to ~29.6% of Max, consistent with the 30%-Max rule; potion vanishes from belt same state read.
- Fysh Oil (Uncommon, combat, any player): +1 Strength and +1 Dexterity for the combat. STRENGTH_POWER +1 and DEXTERITY_POWER:1 appear same state read on use; Dex +1 raises subsequent card-block values by 1 each (Defend 5→6 class) same combat. Usage-timing variant attested: a later decode lists Fysh Oil as anytime/self with the same immediate +1/+1 — verify timing per build.
- Fire Potion (Common, combat, any enemy): deal 20 damage.
- Flex Potion (Common, combat, any player): apply FlexPotionPower +5 Strength — lose 5 Strength at end of this turn (temporary Strength).
- Focus Potion (Common, combat, self): +2 Focus.
- Fortifier (Uncommon, combat, any player): gain Block equal to 2× your current Block (your Block becomes 3×).
- Foul Potion (Event, anytime): in combat — deal 12 damage to every non-pet creature (including you); in a Merchant room — gain 100 Gold; in the FakeMerchant event — starts the FakeMerchant fight. Combat use is a same-window AoE tool — 12 damage kills 12-HP segments outright (e.g. a Decimillipede segment; sets up a Thunderclap finish); the self-damage triggers Rupture (+Str per Amount). Never use in a FakeMerchant room (fight clause) — holding it for a real Merchant room (+100g) is the economy line.
- Fruit Juice (Rare, anytime, any player): +5 Max HP.
- Gambler's Brew (Uncommon, combat, self): discard any number of hand cards, then draw that many.
- Ghost in a Jar (Rare, combat, any player): +1 Intangible.
- Gigantification Potion (Rare, combat, any player): apply GigantificationPower 1 — your next powered Attack card this combat deals ×3 damage; consumed by that attack.
- Glowwater Potion (Event, combat, self): exhaust your hand; draw 10.
- Heart of Iron (Uncommon, combat, any player): +7 Plating.
- King's Courage (Uncommon, combat, any player): Forge 15.
- Liquid Bronze (Uncommon, combat, any player): +3 Thorns.
- Liquid Memories (Rare, combat, self): choose 1 card from your discard pile; add it to hand and it is free this turn. Unusable when the discard pile is empty — played with an empty discard the potion is consumed with NO card_choice and no effect (total whiff). Check piles before use.
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
- Soldier's Stew (Rare, combat, any player): every card with the Strike tag in your combat piles gains +1 Replay for this combat. The Replay behaves as a one-shot charge per card at use-time — strikes already in hand/draw when the potion is drunk replay once when played; strikes drawn later in the same combat resolve a single time.
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

## Additional decode notes

- Potion-Shaped Rock (PetrifiedToad spawn, combat, any enemy): deal 15 unpowered damage. Petrified Toad grants 1 at every combat start; slots can stack multiple rocks. Targeted like a normal single-enemy potion (pass target_combat_id); potion slot reindexes after each use.
- Fruit Juice: +5 Max HP confirmed (multi-source research; STS2 behavior matches STS1). Also usable as StoneOfAllTime Lift fuel (the event's +10 Max HP path — better value than drinking it alone). Seen as shop stock and as a combat reward.
- Speed Potion: **NOT a draw potion** (distinct from Swift Potion); the Dex boost expires by next turn (combat-buff class, turns-capped — treat as same-turn/short-window value). Speed Potion + Dexterity Potion stack: DexPotion +2 (persistent) then SpeedPotion +5 (same-turn counter SPEED_POTION_POWER:5) → DEXTERITY_POWER:7 same read; the Speed component expires next turn (Dex returns to the persistent +2).
- Potion of Binding: decomp OnUse reads its vars swapped (WeakPower applied with the Vulnerable value and vice versa) but both values are 1 — table effect 1 Weak + 1 Vulnerable on all enemies. A single-target sample read Weak 3 + Vuln 1 applied (intent 19→14 weakened) — treat stack counts as verify-on-use; the ALL-target auto rule held (no target id needed).
- Blood Potion: 20% Max formula exact (at 80 Max the heal was +16 HP).
- Card-choice potions (Attack/Skill/Power/Colorless class): the generated card is free this turn even when its printed cost is 2–3; the choice screen can be skipped. The Colorless pool includes high-cost cards such as Eternal Armor (PLATING_POWER 9 — end-of-turn 9 Block, then −1/turn; structural anti-drain block class).
- Heart of Iron (potion): applies **PLATING_POWER 7 to the player** — see powers.md player-Plating entry for timing (mid-combat use grants block at end of player side turn).
- Card-reward potion buttons stayed claimable at 3/3 potion slots (no dead-button lockout observed at full slots).
