# Iteration changelog

Newest entries at the bottom. One line per change: date, nature, cause, fix.

- 2026-09-14 [feature] initial SpireBridge mod v0.1.0, spirectl v0, skill memory
  seeded. Mod built against game v0.107.1 (sts2.dll); CardCmd.AutoPlay path used
  because TryManualPlay does not exist on this game build.
- 2026-09-14 [fix] handshake BOM crash: C# StreamWriter(Encoding.UTF8) emitted a
  UTF-8 BOM that json.loads rejected. spirectl strips BOM per line; mod uses
  UTF8Encoding(false).
- 2026-09-14 [fix] map points stuck disabled after automated run start: nothing
  in the menu-automation path calls NMapScreen.SetTravelEnabled(true), and
  OnRelease/ForceClick no-op unless IsTravelable. map_select now sets travel
  (falling back to debug travel when Hook.ShouldProceedToNextMapPoint declines)
  and selects via NMapScreen.OnMapPointSelectedLocally (enqueues
  VoteForMapCoordAction). First map selection targets min-row points like AutoSlay.
- 2026-09-14 [feature] continue_run action for resuming saved runs from the menu.
- 2026-09-14 [fix] Steam launch race: direct .app open without a fully booted
  Steam client triggers "Steam init failed". spirectl launch now waits for
  steam_osx + Steam Helper/steamwebhelper processes and only uses
  steam://rungameid URLs.
- 2026-09-14 [fix] doctor false-OK during mod warm-up: bridge answers
  {"type":"error","message":"dispatcher not ready"} before GameDispatcher._Ready;
  doctor and launch now require type==hello_ok.
- 2026-09-14 [fix] LocString labels rendered as table metadata in state options
  and intents: resolve via LocString.GetFormattedText()/GetRawText() instead of
  ToString(); Godot node names serialized as objects -> Name.ToString().
- 2026-09-14 [fix] fingerprint blind to event option-page transitions: include
  act_floor, gold, and screen_detail option count in the hash input.
- 2026-09-14 [docs] acceptance session recorded (skill/memory/runs/
  2026-09-14-acceptance-session.md): two combat victories, reward and event
  decisions, map routing all verified through spirectl; energy display bug and
  untested treasure path logged as open gaps.
- 2026-09-14 [fix] selection screens deadlocked without a confirm action:
  deck-select/enchant screens need select + confirm. proceed now clicks
  %Confirm/%PreviewConfirm (deck select), the preview-container Confirm then
  main "Confirm" (enchant, no-% naming), and generic "Confirm" fallback; state
  offers proceed on card_choice/deck_select/relic_choice. Live-verified on
  NDeckEnchantSelectScreen (Sapphire Seed event: BASH enchanted).
- 2026-09-14 [feature] autopilot driver prototype (scratchpad, not shipped)
  with heartbeat logging + stall detection — retained as reference for the
  v2 headless runner TODO; play decisions return to the Claude-in-the-loop
  skill flow per user direction.
- 2026-09-14 [feature] shop + modal support per completeness rule (user
  directive): shop screen enumerates merchant slots (cost/affordable/stocked)
  and shop_buy calls MerchantEntry.OnTryPurchaseWrapper; shop_leave closes
  inventory via back then clicks room proceed; modal popups get confirm
  (Yes/Confirm/OK) and dismiss (No/Cancel) actions. Architecture formalized
  as client-server: server = mod (state + actuation, no decisions), client =
  spirectl + Claude (read state, decide, send ops). Rule: any unsupported
  screen encountered in play is implemented immediately, then game restart.
- 2026-09-15 [fix] live-play completeness series: rest-site button-wired flow
  (OnSelect bypassed room callbacks), generalized selection confirm chain
  (two-phase main/preview), treasure index alignment, shop inventory with
  MerchantEntry.OnTryPurchaseWrapper, deck probe via Player.Deck.Cards,
  rest option ids via RestSiteOption.OptionId. All verified live.
- 2026-09-15 [docs] run progress: Act 1 cleared (boss 墨影幻灵 floor 16 killed
  round 5 via potion-strip slippery + double BLUDGEON vuln window); run
  active in Act 2; VAJRA/GORGET relics; DEMON_FORM added; BYRDONIS_EGG removal
  still pending (selection-screen preview flow fixed but unverified on removal).
- 2026-09-15 [feature] crystal_sphere screen support per completeness rule:
  cell enumeration + choose + proceed traversal verified live (Crystal Sphere
  event floor 19 act 2); cell clickability filter pending polish.
- 2026-09-15 [fix] shop purchase hardening: shop_buy accepts item_id (exact
  entry match via model id / entry type name) eliminating index-space drift;
  purchase flow = hitbox UI-state click + MerchantEntry.OnTryPurchaseWrapper
  (real grant; removal opens deck select; relics run RelicCmd.Obtain; potions
  correctly refuse when slots full). Removal confirm chain v2 walks all
  NConfirmButton nodes preferring enabled preview-container confirms
  (%PreviewConfirm does not resolve from screen root). Verified live: BYRDONIS_EGG
  removed via item_id path; HEART_OF_IRON identified as STS2 potion not relic.
- 2026-09-15 [docs] run progress: act 2 floors through 24; key-fight knight
  killed; PERFECTED_STRIKE + WHIRLWIND upgraded + ODDLY_SMOOTH_STONE/777g chest;
  shop/rewards index-drift patterns documented; hatch mechanic coverage next.
- 2026-09-15 [feature] NFakeMerchant (fake merchant event) support: event-embedded
  merchant UIs routed through shop pipeline via NMerchantInventory discovery;
  ShopBuy/ShopOptions/ShopLeave generalized beyond NMerchantRoom. Live-verified:
  FAKE_SNECKO_EYE bought via item_id (777->723g) and event exited cleanly.
- 2026-09-15 [docs] run progress: Act 2 cleared (boss 无厌沙worm 321hp killed
  round 5 — upgraded demon form + whirlwind 81-dmg burst + perfected strike);
  act 3 entered; JUGGERNAUT picked; FAKE_SNECKO_EYE=CONFUSED costs verified
  (0-cost bludgeon/whirlwind windows exploited); LANTERN_KEY is a deck card.
- 2026-09-15 [docs] run progress: act 3 floor 34 — owl magistrate 231hp killed
  at 3 player hp (whirlwind 0-cost desperation kill); 10 relics accumulated;
  all potions consumed; ARMAMENTS picked after skip unavailable; next room
  unknown at 9hp — high failure probability, which is the user's notify trigger.
- 2026-09-15 [docs] run progress act 3 floors 36-41: factory robots survived
  at 2hp via duplicator bash; historian chest haul; battle dummy event; rest
  heal 14->53 (tea set+pillow); elite trio killed; HAPPY_FLOWER+ORNAMENTAL_FAN
  relics; strike trimmed; 15 relics total; run active at 45hp/126g.
- 2026-09-15 [docs] FAILURE RUN COMPLETE: ironclad died floor 45 act 3 boss
  round 7 vs 女王 at 39/400hp; full postmortem in runs/2026-09-15-act3-boss-
  defeat.md; all screens encountered supported live server-side; user notified
  via Feishu per instruction.
- 2026-09-15 [docs] watchdog pass 2: cards.md knowledge from live runs; reward
  options filter to visible+enabled buttons (unclaimable-button gap polish).
- 2026-09-15 [fix] watchdog pass 3: BBCode stripped from intent labels
  (server ResolveLoc + client render_compact); autopilot v2 design doc added
  under docs/design-autopilot-v2.md.
- 2026-09-15 [feature] per-run detailed logging (user directive): spirectl
  appends full JSON state/act/wait records to logs/run-*.log — one file per run,
  rotated on start_run/continue_run, finalized on game_over; logs committed as
  permanent record. Watchdog cron switched to 5-min interval (2-59/5, job 96b0e26a).
- 2026-09-15 [fix][feature] iteration batch: game-over takeover chain
  (Continue -> ReturnToMainMenu, start_run works from any game state); quiet
  game stop via spirectl stop + CrashReporter DialogType=none (macOS quit-
  unexpectedly dialogs from pkill restarts); SKILL: takeover rule + character
  rotation directive (IRONCLAD/SILENT/DEFECT/NECROBINDER/REGENT); 5-min
  continuous-play watchdog (7c6bad04); per-run logs in logs/ live.
- 2026-09-15 [chore] branch authority: 10h self-commit + dev-merge rights
  granted by user; feat/sts2-comm-mod merged into dev (--no-ff); ongoing play/
  docs commits land on dev, problem spikes branch fix/* off dev then merge back.
- 2026-09-15 [fix] boss-fight end-turn stall root fix: end_turn switched to
  multiplayer-sync entry (CombatManager.OnEndedTurnLocally +
  ActionQueueSynchronizer.RequestEnqueue(EndPlayerTurnAction)), fallback to
  PlayerCmd on exception. Third boss stall (RINGING + PlayerCmd freeze) motivated
  the switch; sync path validated live round 1-2 transition (run2 仪式兽 replay3).
- 2026-09-15 [docs] run2 milestone: Act 1 boss 仪式兽 killed on replay4
  (252hp, 8 rounds) — RINGING one-hit tactic + step-discipline + sync end_turn
  carried the fight; IMPERVIOUS picked for 19hp Act2 survival; gold 485.
- 2026-09-15 [docs] run2 Act2 early progress: f1 survival clear at 9hp
  (IMPERVIOUS 30-block anchor + forge-upgraded deck + step discipline); LOST_WISP
  relic re-claimed via known-safe event; shop f19 haul: VENERABLE_TEA_SET
  (rest-heal relic back), WEAK_POTION, DECAY removed -> 14hp/193g/20-card deck.
- 2026-09-15 [docs] RUN2 ENDED: defeat floor 26 act2 elite Infected Prism
  (3hp vs 8 no-block hand); postmortem runs/2026-09-15-run2-act2-elite-defeat.md;
  run log archived; user notified via Feishu; Run3 SILENT starting per rotation.
- 2026-09-15 [docs] run3 started: SILENT character filter fell back to ironclad
  (starter relic BURNING_BLOOD observed) — SILENT likely locked on this profile;
  rotation queue next tries DEFECT/NECROBINDER/REGENT names. game-over takeover
  chain validated live (return-to-menu click logged).
- 2026-09-15 [feature] SPEED MANDATE (user directive: framework stability/speed,
  full run ≤30min, not winrate). Historical profile (logs/run-20260915-051017.log):
  4750s span, 2684s (56%) idle after end_turn (p50=201s), gaps-before-act p50=14s —
  bottleneck is client cadence + game animation waits, not bridge RTT.
  Game-side: SpeedHooks.cs applies FastMode=Instant + SetFtuesEnabled(false) +
  NonInteractiveMode (reflection on AutoSlayerCheck) on hello/start_run; handshake
  now reports speed=; start_run path upgraded from Fast to Instant.
  Client-side: spirectl act --wait/--wait-play (settle/play-phase poll in-process,
  stall exit 3), batch mechanical act dumps, profile subcommand (rtt/server/queue/
  settle/client-decision decomposition + 30min budget check), per-call metrics in
  run logs (server_ms/queue_ms/settle_ms/rtt_ms). Autonomy: durable Claude cron
  fc8f404b (5-min watchdog with speed mandate) + crontab bridge/watchdog-external.sh
  (Feishu notify when game/bridge down or log stale >10min, independent of Claude).
- 2026-09-15 [docs][fix] SPEED SESSION RESULTS: instrumented profile vs historical
  — act cadence 30-36s -> ~3s, after-end_turn 201s p50 -> 1s, settle p50 ~800ms,
  rtt p50 8ms. Full run wall clock ~15min including 2 mod-restart fixes + 1 SL
  (budget 30min). RUN ENDED: ironclad died floor 16 Act1 boss 同族神官 (0/80 vs
  101/190) after SL replay; postmortem runs/2026-09-15-ironclad-act1-boss-defeat.md.
  Framework deliverables this session: SpeedHooks Instant+NIM, fingerprint
  content-hash, settle stability semantics, combat-end win-condition force path,
  skip fallback (still failing on card_reward — node names TBD), spirectl
  act --wait/--wait-play/batch/profile/sl, external crontab liveness watchdog,
  durable Claude cron fc8f404b. Open: card_reward skip discovery, continue_run
  room-load race, shop_leave async settle race.
- 2026-09-16 [docs] USER CLARIFICATION: 30min is an expectation for framework
  stage latency, not a run-time kill switch. Priority = floors/score > stable
  play > faster tooling. Never suicide or under-rest to hit a clock; speed
  optimizations stay in bridge/mod/client (settle, rtt, recovery, cadence on
  obvious boards). lessons.md priority section updated; watchdog cron prompt
  revised to match.
- 2026-09-16 [docs][feature] boss run ended frozen floor 16 (仪式兽 57/252, player
  6/87 RINGING-locked); postmortem runs/2026-09-16-ironclad-act1-boss-4sl.md;
  profile rtt=7ms settle=822ms cadence=3.6s. [feature] force_advance_turn action:
  clears RINGING/LOCK/PLOW powers (Creature.RemovePowerInternal) + re-queues
  sync end_turn — stall recovery without full SL reload.
- 2026-09-16 [chore] repo hygiene (user directive): .claude/ and logs/ are
  gitignored and untracked — runtime state stays on disk only. Tracked surface =
  README/.gitignore + bridge/ + setup/ + mod/SpireBridge sources+manifest +
  docs/ (protocol/design/research notes) + skill/ (knowledge/memory/postmortems).
  SKILL.md run-end protocol updated: postmortem references log paths as disk
  paths; never `git add` logs.
- 2026-09-16 [feature] skill renamed to **slay-spire-2-copilot** (trigger: "用
  Claude Code 打一局杀戮尖塔2" / "play Slay the Spire 2 via Claude Code or
  Codex"); ~/.claude/skills symlink renamed. [feature] invocation contract:
  explicit log-path required — `spirectl set-log-dir <abs>` writes
  <repo>/.spire-log-dir pointer; runtime run-*.log go there (fallback
  ~/.local/share/slay-spire-2-copilot/logs), never in skill tree or repo. spirectl
  --log-dir / SPIREBRIDGE_LOG_DIR overrides; doctor prints active log dir;
  watchdog-external.sh reads the pointer. [chore] git remote origin set to
  git@github.com:xiabingquan/slay-spire-2-copilot.git.
- 2026-09-16 [chore] rebrand scrub (user directive): zero prior-brand mentions —
  mod id/assembly/namespace -> spire-copilot-bridge / SpireCopilot.Bridge
  (manifest + dll rebuilt, old game-mod folder removed); project/docs/notify
  titles unified as slay-spire-2-copilot; on-disk repo dir moved to
  ~/projects/slay-spire-2-copilot with skill symlink + crontab updated.
