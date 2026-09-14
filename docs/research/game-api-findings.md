# STS2 game API findings (from sts2.dll decompilation, game v0.107.1)

Research notes for the SpireBridge communication mod. All facts verified against
decompiled game code in docs/research/decompiled/ (gitignored) and sts2.xml member docs.

## Engine and runtime

- Godot 4.5.1 + .NET 9 (CoreCLR), game assembly sts2.dll, namespace root MegaCrit.Sts2.*
- Game executable: SlayTheSpire2.app/Contents/MacOS/Slay the Spire 2
- Managed DLLs: Contents/Resources/data_sts2_macos_arm64/ (sts2.dll, GodotSharp.dll, 0Harmony.dll 2.4.2)
- Game ships 0Harmony + MonoMod; deps: GodotSharp 4.5.1, Steamworks.NET, Sentry, SmartFormat
- Prefs: SaveManager.Instance.PrefsSave.FastMode (FastModeType.Fast/Normal/Instant)
- Tutorials can be disabled: SaveManager.Instance.SetFtuesEnabled(false)
- Seed override: NGame.Instance.DebugSeedOverride = seed
- NonInteractiveMode.IsActive suppresses animation waits; AutoSlayer sets NonInteractiveMode.AutoSlayerCheck

## Mod loading contract (ModManager.Initialize)

- Mods directory: Path.GetDirectoryName(OS.GetExecutablePath()) + "/mods"
  -> on this machine: SlayTheSpire2.app/Contents/MacOS/mods/
- Manifest: any *.json found recursively in mods dir. DLL must sit next to manifest
  and be named {manifest.id}.dll; PCK likewise {manifest.id}.pck
- Manifest fields (ModManifest.cs): id (required), name, author, description, version,
  has_pck, has_dll, dependencies [{id, min_version}], affects_gameplay (default true),
  min_game_version (SemanticVersion, e.g. "0.107.1")
- Loading: AssemblyLoadContext of the game assembly LoadFromAssemblyPath(dll) —
  mod code has full access to game types
- Entry point: static method marked [ModInitializer("MethodName")]; if no attribute on
  any type, falls back to new Harmony("{author}.{modId}").PatchAll(assembly)
- Mods load only during game init (before ModManagerState.Initialized); runtime adds
  get ModLoadState.AddedAtRuntime and are not loaded
- PlayerAgreedToModLoading must be true (one-time in-game warning acceptance)
- Game version check vs min_game_version; missing version warns but loads
- Assembly version mismatches tolerated: AssemblyResolve redirects sts2,* and 0Harmony,*
  to the game's own assemblies (mod can reference an older sts2.dll)
- CLI arg -nomods skips all mod loading
- Load order: topological by dependencies, then manual order from settings

## State read surface

- CombatManager.Instance: IsInProgress, IsEnding
- CombatState (per combat): RoundNumber, CurrentSide (CombatSide), Encounter,
  Enemies / Allies / Creatures / PlayerCreatures / Players, HittableEnemies,
  GetCreature(combatId), Modifiers, CreaturesChanged event
- RunManager.Instance.DebugOnlyGetState() -> RunState: CurrentRoom (RoomType),
  CurrentActIndex, ActFloor, TotalFloor, VisitedMapCoords, Map (BossMapPoint etc.),
  CurrentMapCoord, Acts
- LocalContext.GetMe(runState) -> Player: Creature, PlayerCombatState, Potions,
  PotionSlots, Relics
- PlayerCombatState: Phase (PlayerTurnPhase.Play ...), OrbQueue, AllPiles
- PileType.Hand.GetPile(player) -> CardPile.Cards -> CardModel:
  CanPlay(out UnplayableReason, out AbstractModel), Id.Entry, TargetType
- Current overlay screen: NOverlayStack.Instance.Peek(); map open: NMapScreen.Instance.IsOpen
- Scene tree anchors: /root/Game/RootSceneContainer/Run, .../MainMenu,
  .../Run/RoomContainer/{TreasureRoom,EventRoom,RestSiteRoom,...}

## Action surface

- Play card: await CardCmd.AutoPlay(choiceContext, cardModel, targetCreature)
  - choiceContext: BlockingPlayerChoiceContext / ThrowingPlayerChoiceContext
  - target only needed when card.TargetType == TargetType.AnyEnemy; use combatState.HittableEnemies
- End turn: PlayerCmd.EndTurn(player, canBackOut: false)
- Use potion: potionModel.EnqueueManualUse(targetCreature)
- Apply power (debug/buff): PowerCmd.Apply<TPower>(ctx, creature, amount, source, null)
- Card selection interception: CardSelectCmd.UseSelector(selectorScope)
- GameActions (executor-based): MoveToMapCoordAction, PickRelicAction, UsePotionAction,
  DiscardPotionGameAction, EndPlayerTurnAction, VoteForMapCoordAction
- UI-driven actions (from AutoSlay handlers, all main-thread):
  - Map: find NMapPoint under NMapScreen, UiHelper.Click(point); RunManager.Instance.RoomEntered event signals success
  - Card reward: NCardHolder.EmitSignal(SignalName.Pressed) on NCardRewardSelectionScreen
  - Treasure: click Chest node, pick NTreasureRoomRelicHolder, click room.ProceedButton
  - Event: NEventOptionButton with !Option.IsLocked
  - Main menu run start: AbandonRunButton if run active -> SingleplayerButton ->
    StandardButton -> NCharacterSelectButton.Select() -> ConfirmButton
- Waits: game code uses Godot SceneTreeTimers (Cmd.Wait / WaitHelper), not Task.Delay,
  for gameplay-coupled timing; FastMode=Instant skips waits

## AutoSlay (in-game smoke-test bot) — reference implementation

- MegaCrit.Sts2.Core.AutoSlay.AutoSlayer orchestrates a full run by seed:
  handlers per RoomType (Monster/Elite/Boss/Event/Shop/Treasure/RestSite) and per
  overlay screen type (rewards, card reward, deck select/upgrade/transform/enchant,
  relic choose, game over, crystal sphere)
- CombatRoomHandler strategy: apply huge Plating/Regen powers, then each turn play all
  playable hand cards via CardCmd.AutoPlay with random targets, PlayerCmd.EndTurn
- AutoSlayer.Start(seed) runs the whole loop and QuitGame()s the process at the end —
  useful as pattern reference, not as a library we call
- UiHelper.Click / WaitHelper.Until / WaitHelper.ForNode are the UI-drive utilities
  (our mod will implement equivalents for the commands we need)

## Implications for SpireBridge mod design

1. No Harmony patching required for v1: official command APIs (CardCmd/PlayerCmd) +
   UI click patterns cover all acceptance operations
2. Mod package: mods/mimo-spire-bridge/{mimo-spire-bridge.json, mimo-spire-bridge.dll}
   with has_dll true, min_game_version 0.107.1
3. Init: static Init() starts a localhost socket server on a background thread;
   game-state access and command execution must marshal onto the Godot main thread
4. State export is DTO-based: serialize snapshots built from CombatState/RunState/screen
   inspection — never raw game objects
5. Reference objects live only on the main thread; command handlers resolve
   card/creature references at execution time by id/index from current state
6. FastMode=Instant + SetFtuesEnabled(false) recommended when bridge is connected,
   to keep the decision loop fast
7. Version handshake: expose game version, assembly hash (release_info.json), mod
   version and protocol version in state responses for spirectl doctor
