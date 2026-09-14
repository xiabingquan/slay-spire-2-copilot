# mimo-spire

Claude Code skill and tooling that let an AI agent play Slay the Spire 2 on a local machine.

## Layout

- mod/ — C# communication mod for STS2 (Godot 4 .NET): state export + command input
- bridge/ — Python CLI connecting Claude sessions to the mod over localhost
- skill/ — Claude Code skill: play loop, references, persistent memory
- setup/ — installation helpers for game mod files
- docs/ — design and protocol documents
