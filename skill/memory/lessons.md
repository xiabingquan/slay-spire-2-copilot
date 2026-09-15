# Playing lessons

Short, generalizable, actionable. Add only after a run end or a mid-run
breakthrough; remove entries that prove wrong.

## Priority (user directive 2026-09-16)

- Run quality first: floors reached and score outrank any wall-clock target.
  The ~30min figure is a framework-latency expectation (tooling settle/RTT/
  client gaps), never a reason to suicide, skip rests, or rush a boss.
- Speed work means: faster bridge waits, faster recovery, faster decisions on
  obvious boards — not thinner play on dangerous turns. Think on bosses/low HP.

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
- SL (save/load) validated (2026-09-15 boss): `spirectl sl` reloads room-entry
  save in ~18s with seed-identical hand/intents. Use on lethal-incoming hands;
  replay with foreknowledge (which slime leaks, which turn is 27 incoming).
- CURE_ALL potion = draw cards + bonus energy (NOT a heal). FYSH_OIL = +STRENGTH
  +DEXTERITY buff. Spend both on tempo turns, not panic.
- MINION_POWER boss adds (Act1 同族神官): 58-59hp believers chip 7-9/turn while
  you burst the priest — burst-only decks fold ~R5-R6 when FRAIL/WEAK stack.
  Need kill-adds plan OR block every turn.
- Combat-end stall pattern #5: HAVOC/random-card kills left combat in Play phase
  with no living enemies. Server fix: end_turn win-condition force path
  (CheckWinCondition -> EndCombatInternal). No more restart ladder for this case.
- Floor5 shrink-beetle + STR-worm pack (2026-09-16): strike-heavy starter decks
  fold even with correct kill order — worm scales to 25dmg/turn. Two SL retries
  with foreknowledge still died R9-R10. Need block/heal relics before mid-act
  multi-enemy STR floors.
- POWER_POTION: no visible buff in bridge state after use — verify effect
  (target requirement? hidden power?) before relying on it in races.
- SL retry budget: 1-2 tries when the known line still loses; then write
  postmortem and move on — replaying a losing seed forever wastes the watch dog
  window without changing the deck.
- 仪式兽 boss 4xSL (2026-09-16): best line R15 boss 57/252 at 6hp; RINGING/PLOW
  end_turn freeze recurred — server `force_advance_turn` now clears lock powers
  via Creature.RemovePowerInternal then re-queues end turn. Use on fingerprint
  freeze before burning another SL.
- Boss block math: 252hp STR-scaler needs heal/relic sustain or Bludgeon-class
  burst; WHIRLWIND+FLAME+GRIT alone leaks ~10-20hp/turn from R6 on.
