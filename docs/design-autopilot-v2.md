# Autopilot v2 design (headless run runner — deferred TODO)

Goal: unattended batch runs for iteration data collection, while keeping the
client-server contract and the completeness rule intact. Not implemented in v1.

## Roles (unchanged contract)

- Server: SpireBridge mod (state snapshots + actuation only, no decisions)
- Client: runner process that decides. Two client tiers:
  - Tier A (heuristic): evolve the scratchpad/autopilot.py prototype — heartbeat
    logging every loop, stall detection (unchanged fingerprint > 40s), recovery
    ladder (proceed -> skip -> abandon), outcome markers for watchers
  - Tier B (Claude-in-the-loop): Claude Code session plays via skill/spire;
    batches of runs driven session-by-session; memory updated per run

## Runner loop (Tier A)

1. ensure bridge up (spirectl launch; steam-ready check; no direct .app open)
2. start_run (or continue_run if save present and healthy)
3. loop: state -> decide(screen, stuck_count) -> act -> heartbeat log
4. terminal conditions:
   - game_over -> outcome=defeat; write run summary line; notify optional
   - act clear / floor cap -> outcome=survived; abandon_run or continue by config
   - stall ladder exhausted -> outcome=stall; diagnose; exit code 4
5. between runs: rotate seed; append stats line to skill/memory/runs/batch-log.md

## Decision knowledge injected into Tier A

- skill/doc/cards.md + powers.md + relics.md + lessons.md are the heuristic
  tuning source (keyword priorities, block thresholds from lessons)
- keep decisions cheap: no LLM calls inside Tier A loop

## Observability (hard requirements learned v1)

- append-only heartbeat log with screen/fingerprint/hp/floor per iteration
- outcome file (running/game_over/chunk_end/stall) written every terminal path
- never run the loop as an opaque foreground bash — background + poll logs

## Milestones

1. v2.0: Tier A hardened loop + batch-log + seed rotation + outcome notify
2. v2.1: completeness hook — runner detects screen=other/unknown, writes a
   stall marker naming the screen type, stops batch; human/Claude implements
   support, batch resumes (completeness rule automated as a tripwire)
3. v2.2: Tier B scheduler — cron or harness kicks Claude sessions for
   memory-driven play batches; lessons/changelog updated automatically
