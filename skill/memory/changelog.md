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
