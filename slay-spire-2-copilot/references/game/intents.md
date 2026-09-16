# Enemy intents

How to read enemy intents. Label formats observed on v0.107.1 (game loc
tables); icon/behavior semantics from community references (slaythespire.gg,
sts2-wiki) and live play.

- FORMAT_DAMAGE_SINGLE: attack for N damage (N shown as the label value).
- FORMAT_DAMAGE_MULTI / label with xN: attack N times for the listed damage each (e.g. 6x3 = 18 raw).
- FORMAT_STATUS_CARD_COUNT: adds status cards to draw/discard piles, no direct damage.
- FORMAT_EMPTY: no action / placeholder.
- Attack intent: enemy plans damage this turn; the displayed number is raw damage before Weak/Vulnerable/Block modifiers.
- Block/shield intent: enemy plans to gain Block this turn instead of attacking.
- Buff intent: enemy powers up — Strength, Ritual, summoning, defensive stances (BURROWED/SOAR/TERRITORIAL).
- Debuff intent: enemy applies debuffs — Vulnerable, Weak, Poison, Frail, Chains of Binding.
- Unknown intent: action hidden; revealed later or after certain conditions.
- Charged/heavy intent: big windup hit (e.g. SLOW_POWER elites alternate empty-intent turns with ~23-dmg charged hits); BURROWED charged intents cancel if block broken in time.
- Doom intent (Necrobinder fights): Doom stacking displayed as part of monster behavior — watch Doom vs enemy HP threshold.
- CardDebuff intent (class CardDebuffIntent, live 2026-09-17): injects status/curse cards into your piles that turn (Wound from Vantom DISMEMBER, slime SLIMED); label often FORMAT_EMPTY — treat as "deck pollution incoming", not damage.
- Combined labels like "17; 3" or "26; 3" = attack N plus status-card injection in the same move; "4×2" / "6×2" / "8×2" = multi-attack (per-hit value × hits).
- Note: raw loc BBCode like [font_size=18]x3[/font_size] may leak into labels (known server polish item) — strip mentally when reading.
