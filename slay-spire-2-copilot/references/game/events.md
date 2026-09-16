# Events

Event reference. Internal names from game source extraction (STS2-Agent
event index, 69 events; AncientEventModel marks the ancient/Neow-family
track). Behaviors known from live play, relic interactions, and community
notes are attached where available — most events present choices whose
rewards scale with HP/relics/multiplayer state, so read the in-game screen
as authoritative.

- ABYSSAL_BATHS: event room encounter (choices pending live observation).
- AMALGAMATOR: event room encounter.
- AROMA_OF_CHAOS: "LET_GO" option opens deck transform — pick any deck card, it transforms at random (STRIKE -> POMMEL_STRIKE observed).
- BATTLEWORN_DUMMY: event room encounter.
- BRAIN_LEECH: offers card-related branches (one branch adds cards via a non-NCardReward screen — see cards.md screen notes).
- BUGSLAYER: event room encounter.
- BYRDONIS_NEST: Sapphire-seed/nest family — grants BYRDONIS_EGG status card (unplayable; HATCH rest option while in deck; shop-remove target).
- COLORFUL_PHILOSOPHERS: event room encounter.
- COLOSSAL_FLOWER: event room encounter.
- CRYSTAL_SPHERE: crystal-sphere screen family (deck modification flow; server support via CrystalSphereScreenHandler).
- DARV: ancient-track event (AncientEventModel).
- DENSE_VEGETATION: event room encounter.
- DOLL_ROOM: event room encounter.
- DOORS_OF_LIGHT_AND_DARK: event room encounter.
- DROWNING_BEACON: event room encounter.
- ENDLESS_CONVEYOR: event room encounter.
- FAKE_MERCHANT: NFakeMerchant flow — sells FAKE_SNECKO_EYE for 54g (trap relic; Confused-like hand randomization observed).
- FIELD_OF_MAN_SIZED_HOLES: sandpit-holes family — FRANTIC_ESCAPE card product (cost rises each use; +1 Sandpit).
- GRAVE_OF_THE_FORGOTTEN: event room encounter.
- HUNGRY_FOR_MUSHROOMS: event room encounter.
- INFESTED_AUTOMATON: event room encounter.
- JUNGLE_MAZE_ADVENTURE: branch choice verified live — SOLO_QUEST ~-18 HP for ~+147g; JOIN_FORCES ~+63g at zero HP cost (live 2026-09-17: JOIN paid +50g at 63 HP). JOIN at mid/low HP, SOLO only over 60 HP; prefer JOIN when the boss is imminent and gold has no shop sink.
- LOST_WISP: "claim" option grants LOST_WISP relic (effect pending observation).
- LUMINOUS_CHOIR: verified live 2026-09-17 — REACH_INTO_THE_FLESH removes 2 cards of your choice and adds SPORE_MIND curse (1 cost, Exhaust) to the deck; OFFER_TRIBUTE costs 149 Gold (locked without it) and grants a random Relic. Deck-select uses the standard 2-pick removal grid.
- MORPHIC_GROVE: event room encounter.
- NEOW: ancient-track run-start boon (opening offer; Neow's Fury/Bones/Talisman/Torment relic family).
- NONUPEIPE: ancient-track event.
- OROBAS: ancient-track event (Touch of Orobas relic family — replaces starter relic with ancient version).
- PAEL: ancient-track event (Pael's Claw/Eye/Flesh/Growth/Horn/Legion/Tears/Tooth/Wing relic family — see relics.md).
- POTION_COURIER: event room encounter (potion offers).
- PUNCH_OFF: event room encounter.
- RANWID_THE_ELDER: event room encounter.
- REFLECTIONS: event room encounter.
- RELIC_TRADER: event room encounter (relic trade offers).
- ROOM_FULL_OF_CHEESE: event room encounter (The Chosen Cheese relic family — end of combat +1 Max HP).
- ROUND_TEA_PARTY: event room encounter (tea-set/pillow rest-synergy family).
- SAPPHIRE_SEED: seed/nest family — BYRDONIS_EGG-type status products.
- SELF_HELP_BOOK: event room encounter.
- SLIPPERY_BRIDGE: event room encounter.
- SPIRALING_WHIRLPOOL: event room encounter.
- SPIRIT_GRAFTER: event room encounter.
- STONE_OF_ALL_TIME: event room encounter.
- SUNKEN_STATUE: event room encounter.
- SUNKEN_TREASURY: event room encounter (treasure/loot offers).
- SYMBIOTE: event room encounter.
- TABLET_OF_TRUTH: event room encounter.
- TANX: ancient-track event (Tanx's Whistle relic — adds Whistle card).
- TEA_MASTER: event room encounter.
- TEZCATARA: ancient-track event (Nutritious Soup enchant family — Tezcatara's Ember on Strikes).
- THE_ARCHITECT: event room encounter.
- THE_FUTURE_OF_POTIONS: event room encounter (potion-choice family).
- THE_LANTERN_KEY: verified branches — RETURN_THE_KEY grants ~+100 gold instantly (no combat); KEEP_THE_KEY starts knight fight for the key card. RETURN at low HP, KEEP when healthy. Lantern Key quest card unlocks a special event next Act.
- THE_LEGENDS_WERE_TRUE: event room encounter.
- THIS_OR_THAT: verified branch — "ORNATE" pick granted MOLTEN_EGG (attack-card rewards arrive upgraded).
- TINKER_TIME: event room encounter.
- TRASH_HEAP: event room encounter.
- TRIAL: event room encounter.
- UNREST_SITE: rest-site variant event (non-standard rest options).
- VAKUU: ancient-track event (Whispering Earring relic — Vakuu plays your first turn).
- WAR_HISTORIAN_REPY: event room encounter.
- WATERLOGGED_SCRIPTORIUM: event room encounter.
- WELCOME_TO_WONGOS: verified — mystery box 300g grants WONGO'S_MYSTERY_TICKET (3 random relics after 5 combats); Wongo Customer Appreciation Badge does nothing.
- WELLSPRING: event room encounter.
- WHISPERING_HOLLOW: verified live 2026-09-17 — GOLD (exchange gold) costs ~36-50 Gold and pays 2 random potions (live: Potion of Binding + Swift Potion; paid 36g — beta-patched price, guides list 50); HUG (hug the tree) costs 9 HP and transforms a card at random.
- WOOD_CARVINGS: event room encounter.
- ZEN_WEAVER: event room encounter.

## Event handling notes

- screen "event" in state lists options via screen_detail.options (kind=event_option); pick via act choose index; locked options show IsLocked in game UI.
- Event rewards can transform cards, grant relics/potions/gold, or start combats — read the option text on screen before choosing; this index is for recognition, not exhaustive choice guidance.
- Ancient-track events (Darv, Neow, Nonupeipe, Orobas, Pael, Tanx, Tezcatara, Vakuu) share the Ancient relic/currency family.
