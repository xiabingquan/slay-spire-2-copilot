# 2026-09-14 acceptance session — first live play through SpireBridge

Result: acceptance bar met (basic operations playable end-to-end; boss clear not required).
Game: STS2 v0.107.1, mod mimo-spire-bridge 0.1.0, character Ironclad, seeds
bridge-acceptance-1/2/3. Run left active at map floor 3 (pos 4,2 frontier, Monster).

## What the agent did through the skill loop

- doctor green: handshake protocol=1 game=v0.107.1 mod=0.1.0 assembly_hash=-1718063421
- start_run: menu automation embarked Ironclad (twice; run-1 lost to Steam relaunch)
- map_select: (1,1) then (2,1) then (3,2) via VoteForMapCoordAction path
- combat 1 vs NIBBITS_WEAK: Bash (vuln) + Strikes, won in 2 rounds; BURNING_BLOOD healed
- rewards: gold claimed (99->114), card picked BLOOD_WALL (deck needed block)
- event BYRDONIS_NEST: chose TAKE -> BYRDONIS_EGG status card added to deck; PROCEED
- combat 2 vs leaf/twig slimes (12/32/9): kill order on low-HP attacker, BLOOD_WALL
  blocked (16 block, 2 HP cost), mop-up loop finished round 4; BURNING_BLOOD -> 78 hp
- rewards: gold 114->134, card picked INFLAME (strength scaling for Ironclad)
- treasure room never appeared on this seed path (map luck; treasure actions are
  implemented: treasure_open / choose relic / proceed — awaiting a real chest)

## Known issues found and fixed in this session

- UTF-8 BOM from StreamWriter(Encoding.UTF8) broke json.loads -> UTF8Encoding(false)
- map points disabled after automated start -> SetTravelEnabled + OnMapPointSelectedLocally
- first map selection targeted wrong row -> min-row frontier like game AutoSlay
- Steam launch raced client boot (and direct .app open broke Steamworks) -> wait for
  Steam Helper processes, launch only via steam://rungameid
- doctor treated dispatcher-not-ready error JSON as handshake OK -> require hello_ok
- LocString labels rendered as table metadata -> GetFormattedText/GetRawText resolution
- reward/rest/treasure option names serialized as Godot objects -> Name.ToString()
- fingerprint blind to option-page changes -> include act_floor/gold/option counts

## Remaining gaps (next iterations)

- energy field in combat snapshots stayed 3/3 after plays (display bug; can_play from
  the game itself was authoritative)
- intent labels need LocString variables resolved to show damage numbers
- treasure-room operations untested in a real run (map-luck dependent)
- card text/rules not exposed yet (decisions used card ids + archetype knowledge)
- headless auto-run runner and STS1 adapter remain deferred TODOs
