# Enemy intents

Deterministic intent semantics from decompiled
`MegaCrit.Sts2.Core.MonsterMoves.Intents.*` classes and the SpireBridge
compact-view contract (`references/bridge/protocol.md`,
`references/bridge/commands.md`). JSON state per enemy:
`intent: null | {"id": "...", "damage": N, "times": N, "is_attack": bool}`;
`--json` also exposes `damage`/`hits`/`class`/`type` per intent.

## Intent classes -> compact-view labels

- SingleAttackIntent (IntentType.Attack): attack once. Label =
  FORMAT_DAMAGE_SINGLE → compact shows the damage number, e.g. `8`. The
  number is the game's live damage preview (`GetSingleDamage` runs damage
  hooks, floored at 0) — it already includes Strength/Weak/Vulnerable-style
  modifiers, not the raw move value.
- MultiAttackIntent (IntentType.Attack): attack Repeats times. Label =
  FORMAT_DAMAGE_MULTI with Damage + Repeat → compact shows per-hit × hits,
  e.g. `3×7` (7 hits of 3; total = per-hit × hits). Same live-preview rule
  for the per-hit number.
- DeathBlowIntent (IntentType.DeathBlow): SingleAttackIntent subclass with
  death-blow icon — a lethal-styled attack; label is still the damage number.
- BuffIntent (IntentType.Buff): enemy buffs itself / allies (Strength,
  Ritual, stances, summons in some moves). Label is FORMAT_EMPTY in loc →
  bridge replaces with the intent type; compact shows `Buff` or
  `Buff(move_id)` (e.g. `Buff(PREPARE_MOVE)`).
- DebuffIntent (IntentType.Debuff / DebuffStrong): enemy applies debuffs
  (Vulnerable, Weak, Poison, Frail, card afflictions, etc.). Compact shows
  `Debuff`, or `DebuffStrong` when constructed with strong=true.
- DefendIntent (IntentType.Defend): enemy gains Block this turn. Compact
  shows `Defend`.
- HealIntent (IntentType.Heal): enemy heals (also used by revive moves, e.g.
  IllusionPower REVIVE_MOVE). Compact shows `Heal`.
- SleepIntent (IntentType.Sleep): enemy sleeps / skips action (AsleepPower /
  SlumberPower stances). Compact shows `Sleep`.
- StunIntent (IntentType.Stun): enemy is stunned / skips action this turn
  (Burrowed break, wake-up stuns, Imbalanced, etc.). Compact shows `Stun`.
- SummonIntent (IntentType.Summon): enemy summons adds this turn. Compact
  shows `Summon`.
- StatusIntent (IntentType.StatusCard): adds `count` status cards to the
  player's piles, no direct damage. Label = FORMAT_STATUS_CARD_COUNT →
  compact shows the card count.
- CardDebuffIntent (IntentType.CardDebuff): injects status/curse cards into
  the player's piles (often combined with an attack on the same move). Label
  is FORMAT_EMPTY → compact falls back to `CardDebuff(move_id)`. Treat as
  deck pollution incoming, not damage — unless the move also carries an
  attack (see combined labels below).
- EscapeIntent (IntentType.Escape): enemy flees combat this turn. Compact
  shows `Escape`.
- HiddenIntent (IntentType.Hidden): no sprite, no hover tip — action fully
  hidden. Compact shows `Hidden`.
- UnknownIntent (IntentType.Unknown): action not yet revealed; revealed later
  or after conditions. Compact shows `Unknown`.

## Combined / presentation notes

- Combined moves (attack + status injection, e.g. Vantom DISMEMBER) surface
  both parts: `--json` has `damage`/`times` plus a CardDebuff class; compact
  labels observed in the form `17; 3` mean attack 17 plus status-card
  injection in the same move. `4×2` / `6×2` / `8×2` = multi-attack
  (per-hit × hits).
- Attack icon/animation tier is chosen by total damage: <5 → tier 1,
  <10 → tier 2, <20 → tier 3, <40 → tier 4, >=40 → tier 5 (display only;
  the label number is what matters for math).
- Loc leaks: raw loc keys like `intents:FORMAT_EMPTY` (or BBCode fragments
  such as `[font_size=18]x3[/font_size]`) can leak into labels; the bridge
  replaces FORMAT_EMPTY with the intent type server-side and the compact view
  falls back to `Type(move_id)`. Strip BBCode mentally when present.
- `intent: null` in JSON = no intent data this moment (e.g. mid-transition).
- Deterministic read: number labels are damage previews; word labels
  (`Buff`/`Debuff`/`Defend`/`Heal`/`Sleep`/`Stun`/`Summon`/`Escape`/
  `Hidden`/`Unknown`) carry no number — check the monster's move table
  (monsters.md) or `--json` for what the move actually does.
