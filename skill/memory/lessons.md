# Playing lessons

Short, generalizable, actionable. Add only after a run end or a mid-run
breakthrough; remove entries that prove wrong.

## Combat

- Read intents before playing: if incoming damage exceeds HP+block, prioritize
  block or kill the attacker this turn.
- Hand indices are volatile: re-read state after every act; never reuse an index
  from a previous snapshot.
- The game's can_play flag is authoritative — trust it over manual energy math
  (the bridge energy field has lagged behind real energy).
- Multi-enemy fights: killing a low-HP attacker this turn beats spreading damage,
  even when a bigger enemy has scarier stats.
- Status-only enemy intents (no damage) are free turns to set up powers/block.

## Rewards and deck

- Skip is a valid choice; a deck that stays consistent beats one stuffed with
  situational rares.
- Starter deck saturated on strikes: prefer block/utility picks (BLOOD_WALL paid
  off immediately in the next fight).
- Strength engines (INFLAME) scale every future strike — high priority for Ironclad.

## Map and events

- Frontier options may be the only path; Unknown (?) rooms resolved to events or
  combat — both handled fine by the loop.
- Event options with unreadable text: decide on option keys + STS event archetypes
  (TAKE-type options grant relics/cards, often with a deck cost).
- Treasure rooms are map-luck; don't stall a run hunting one.

## Tooling

- After any act, if wait times out, re-read state directly — fingerprint changes
  can lag option-page transitions.

## Event and relic mechanics (observed)

- FAKE_* relics from the NFakeMerchant event are traps with real effects:
  FAKE_SNECKO_EYE grants CONFUSED_POWER — hand costs randomized each draw
  (0-cost BLUDGEON possible). Exploit: play discounted high-cost cards first.
- ODDLY_SMOOTH_STONE verified: +1 DEXTERITY_POWER at combat start.
- Rest-site HATCH option appears only while an egg-type card is in deck.
- Shop index space can drift after purchases/removals; use shop_buy item_id.
- Reward buttons: executor index space is 0-based over current buttons; state
  options may include stale/unclaimable entries — prefer smallest index and
  re-read state after every claim.
- Boss-class hp pools (400) outlast burst engines: keep vuln cycling
  (UPPERCUT/THUNDERCLAP) every turn instead of stacking only raw damage.
- Chains/frail debuff stacks zeroed block in boss rounds — if block reads 0
  after block-card plays, incoming damage is full value; race or reposition.
- Rest-site relic stacking (VENERABLE_TEA_SET + REGAL_PILLOW) was the biggest
  run extender: +39 heals twice rescued the run from 8-14hp.
- Never issue actions during Enemy phase (potions included) — a GAMBLERS_BREW
  use during enemy turn coincided with a Cmd.Wait stack-trace stall that froze
  the elite fight (run2 f7 worm wave). Only act when turn_phase=Play.
- INFESTED strategy validated (run2 f7 elite, post-stall replay): single-target
  the parent, hoard AOE; on death-wave spawn, THUNDERCLAP x2 cleared 4 adds
  same-turn. Elite relic LASTING_CANDY + SWORD_BOOMERANG banked.
- ILLUSION_POWER (雾菇 family, run2 f12): respawning 6hp add (利齿之眼) that
  keeps returning while parent lives — kill the parent FIRST, adds despawn
  with it. Opposite priority vs INFESTED parasite waves.
- Run2 relic combat start: player showed STRENGTH+DEXTERITY and energy 6/3
  (SPARKLING_ROUGE / CHANDELIER suspects) — verify which relic grants what.
- Stall pattern #2 (run2 boss 仪式兽): enemy-phase transition freezes (fingerprint
  frozen, intent not advancing) struck twice mid-boss after heavy play turns.
  Recovery ladder proven: spirectl stop -> launch -> continue_run (~90s); boss
  fight reloads from room-entry save (in-combat progress lost, potions restored).
  Treat boss fights as burst-then-restart-tolerant; keep postmortems ready.
- Boss-fight turn stalls (#3): RINGING-locked hands + PlayerCmd.EndTurn froze
  turn transitions. Server fix: sync-queue end_turn path. Client rule stays:
  on frozen fingerprint >30s -> stop/launch/continue_run ladder (~90s, boss
  reloads from entry save).
- Boss stall #4 (run2 仪式兽 r9, boss at 19hp): RINGING-locked end-turn froze
  on BOTH end-turn paths (PlayerCmd and sync-queue) — freeze is enemy-turn/AI
  side, not our end-turn entry. Recovery ladder remains the remedy; cost is
  boss-fight replay from entry save. Future server work: inspect RINGING
  handler interactions / consider force-advance action via CombatManager
  internals if replays multiply.
- RINGING stall-avoidance tactic VALIDATED (run2 boss replay4 r6): on RINGING
  turns play AT MOST one attack then immediately sync end_turn with no further
  plays — enemy phase resolved cleanly to r7. Keep async residue minimal on
  locked turns; brute-forcing multiple locked-state attempts correlates with
  freezes.
- Client discipline: re-read state after EVERY act, even mid-"obvious" dumps —
  EXPECT_A_FIGHT misclicked twice from stale indices this fight.
- BURROWED cancel validated again (run2 Act2 f23): breaking the burrow block
  (32->0 via AOE chain) cancelled the 23-dmg charge — always dump attacks into
  burrowed enemies' block when IMPERVIOUS is unavailable; the cancel IS the
  defense.
- BODY_SLAM x2 + IMPERVIOUS engine: second copy picked; expect ~30-damage
  slams on shield turns. 14hp survival fights won on this + weak potions.
- VITAL_SPARK elite (run2 f26 Infected Prism): damage mitigation + block regen —
  long-fight attrition target; bring block every turn, don't burst-plan.
- Critical-hp hands without block: potions are the final lever — consider
  ENERGY_POTION for extra plays; leave no potion unspent at 3hp.
- SLOW_POWER elite pattern (run3 f6 旧日雕像): empty-intent turns alternate with
  ~23-dmg charges + str growth — dump attacks on slow turns, SHRUG/DEFEND stacks
  on charge turns. Elite cleared at 5hp: kill-margin math matters, keep hitting.
- INFLAME all-in validated (run3 f7 7hp comeback): INFLAME(1-cost) + BASH(vuln)
  + upgraded FEED + STRIKE chain dealt 47hp in one turn — str engine + molten-egg
  upgrades + vuln multiplies; at critical hp the race IS the defense when block
  is absent. FIRE_POTION kept in reserve never needed.
