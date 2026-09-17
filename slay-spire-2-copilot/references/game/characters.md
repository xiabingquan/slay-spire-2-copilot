# Characters

Deterministic character facts. Source: decompiled game code
`MegaCrit.Sts2.Core.Models.Characters` + starter relics in
`MegaCrit.Sts2.Core.Models.Relics` + unlock gating in
`MegaCrit.Sts2.Core.Unlocks/UnlockState.cs` (/tmp/sts2-decomp).

All five playable characters start with 99 Gold (`StartingGold => 99` on every CharacterModel).

## Playable characters

- IRONCLAD — 80 HP, Masculine, NameColor red. Starter relic: BURNING_BLOOD — heal 6 HP after combat victory (Black Blood, its starter-relic upgrade, heals 12). Starter deck (10): Strike ×5, Defend ×4, Bash. Card pool: IroncladCardPool. `UnlocksAfterRunAs => null` — always unlocked at the character-model level.
- SILENT — 70 HP, Feminine, green. Starter relic: RING_OF_THE_SNAKE — +2 cards drawn on turn 1 only (`TurnNumber > 1` returns base draw). Starter deck (12): Strike ×5, Defend ×5, Neutralize, Survivor. Card pool: SilentCardPool. `UnlocksAfterRunAs => null` (code comment: any completed run unlocks her); roster access is gated by UnlockState below.
- DEFECT — 75 HP, Neutral, blue. Starter relic: CRACKED_CORE — on turn 1, channel 1 Lightning orb (`BeforeSideTurnStart` while `TurnNumber <= 1`). Base orb slots: 3 (`BaseOrbSlotCount`). Starter deck (10): Strike ×4, Defend ×4, Zap, Dualcast. Card pool: DefectCardPool. `UnlocksAfterRunAs => Necrobinder`.
- NECROBINDER — 66 HP, Feminine, purple. Starter relic: BOUND_PHYLACTERY — Summon Osty 1 at combat start (`BeforeCombatStart`); if Osty is gone on later turns, re-summons after energy reset (`AfterEnergyResetLate`, not on turn 1). SpawnsPets = true. Starter deck (10): Strike ×4, Defend ×4, Bodyguard, Unleash. Card pool: NecrobinderCardPool. `UnlocksAfterRunAs => Regent`.
- REGENT — 75 HP, Masculine, orange; star counter always shown (`ShouldAlwaysShowStarCounter`). Starter relic: DIVINE_RIGHT — +3 stars when entering a CombatRoom (`AfterRoomEntered`). Starter deck (10): Strike ×4, Defend ×4, FallingStar, Venerate. Card pool: RegentCardPool. `UnlocksAfterRunAs => Silent`.

State snapshot character ids: IRONCLAD, SILENT, DEFECT, NECROBINDER, REGENT. Test-only ids (not playable in normal runs): Deprived, RandomCharacter, DeprecatedCharacter.

## Unlock gating (deterministic game rules)

- `UnlockState.Characters` starts from `ModelDb.AllCharacters` and removes:
  - Silent — unless `IsEpochRevealed<Silent1Epoch>()`
  - Regent — unless `IsEpochRevealed<Regent1Epoch>()`
  - Necrobinder — unless `IsEpochRevealed<Necrobinder1Epoch>()`
  - Defect — unless `IsEpochRevealed<Defect1Epoch>()`
  - Ironclad is never removed — the roster always contains Ironclad.
- Design-intent chain from `CharacterModel.UnlocksAfterRunAs`: Ironclad and Silent are null (no run-as prerequisite in the model); Regent unlocks after Silent; Necrobinder after Regent; Defect after Necrobinder. Actual roster availability additionally requires the corresponding Epoch to be revealed on the player's UnlockState (Timeline progress save).
- `UnlockState` also tracks revealed Epochs per ancient/relic/potion/card content: e.g. Overgrowth removes Neow from `GetUnlockedAncients` unless `NeowEpoch` revealed; Underdocks applies the same NeowEpoch gate to its Neow; Hive removes Orobas unless `OrobasEpoch`; Glory's three ancients (Nonupeipe, Tanx, Vakuu) are ungated; shared ancient Darv removed unless `DarvEpoch`. Relic/potion/card pools filter via `GetUnlockedRelics/Potions/Cards(this)`.
- Unlock pipeline (how epochs actually get revealed — decomp, 2026-09-17): score-bar game-over unlocks walk `_agnosticEpochUnlockOrder` (18 agnostic epochs: Colorless/Relic/Potion/Underdocks/Act2B/Act3B/Event — **no character epochs ever**); character unlocks come ONLY from the Timeline chain — `NeowEpoch.QueueUnlocks()` writes `ObtainEpochOverride(Silent1Epoch, ObtainedNoSlot)`, Timeline slot click runs `RevealEpoch` + `Silent1Epoch.QueueUnlocks()` (PendingCharacterUnlock + character unlock UI + expansion slots via `UnlockSlot`, which promotes ObtainedNoSlot→Obtained). Earn rules: Silent1 — any completed run; Regent1/Necrobinder1/Defect1 — `UnlocksAfterRunAs` chain (a completed run as Silent/Regent/Necrobinder respectively). Automation note: the bridge mod's `timeline_sync` action / start_run Timeline visit replays this UI flow; repair steps only write ObtainedNoSlot+UnlockSlot (the game's own states); Neow hard-Revealed is boon-room fallback only. Observed live: SILENT1_EPOCH not_obtained → obtained_no_slot → revealed, pending_character_unlock=CHARACTER.SILENT, unlock_character_screen popped natively.

## Run structure facts (from act sources)

- Acts in code order: Overgrowth (Act 1), Hive (Act 2), Glory (Act 3), Underdocks (Act 4). Boss discovery orders: Overgrowth = Vantom, CeremonialBeast, TheKin; Hive = TheInsatiable, KnowledgeDemon, KaiserCrab; Glory = Queen, TestSubject, Aeonglass; Underdocks = WaterfallGiant, SoulFysh, LagavulinMatriarch.
- Map rooms: branching map of monster / elite / boss / event / shop / rest / treasure; card rewards after combat; an ancient/Neow-family boon room can appear at act start subject to the epoch gates above.
- Rest sites offer Rest and Smith plus character-specific options where relic/character code adds them (e.g. PaelsGrowth adds a Clone rest option).
