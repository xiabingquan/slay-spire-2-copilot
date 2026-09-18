# References index

Paths are relative to this skill folder. bridge/ documents the tooling;
game/ is the static game reference consulted during play.

> Chinese version: [README_zh.md](README_zh.md). Every game/ knowledge file
> has a `_zh` twin with matching content.

bridge/ — tooling:

- [commands](bridge/commands.md) — CLI usage, action/state reference, log-directory contract
- [protocol](bridge/protocol.md) — wire protocol v1 (JSON Lines over TCP on localhost)

game/ — game knowledge (JSON reference DB):

- [characters](game/characters.json) + [characters_zh](game/characters_zh.json) — playable characters, starters, archetypes
- [cards](game/cards.json) + [cards_zh](game/cards_zh.json) — playable cards: costs, effects
- [powers](game/powers.json) + [powers_zh](game/powers_zh.json) — combat powers, buffs and debuffs
- [relics](game/relics.json) + [relics_zh](game/relics_zh.json) — relic effects
- [potions](game/potions.json) + [potions_zh](game/potions_zh.json) — potion effects
- [afflictions](game/afflictions.json) + [afflictions_zh](game/afflictions_zh.json) — statuses and card-bound debuffs
- [intents](game/intents.json) + [intents_zh](game/intents_zh.json) — enemy intent label formats
- [monsters](game/monsters.json) + [monsters_zh](game/monsters_zh.json) — enemy move tables and passives
- [events](game/events.json) + [events_zh](game/events_zh.json) — event rooms and known branches

JSON reference DB — key = live state id; resolve via `spirectl lookup <key>`;
miss path researches spire-codex.com and folds findings (curated:false) then
needs agent curation. Markdown twins (game/*.md) stay until live verification
passes, then retire — cite the JSON files.
