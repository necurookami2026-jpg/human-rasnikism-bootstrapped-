# Rasniki gaming software edition

Version 0.1 · Implemented standalone browser game and host adapter contract

Open game.html in a browser or serve the repository with the documented Python HTTP server. No installation, account, external library, or network API is needed. “Max” remains a goal of expansion; this edition is an initial game, not support for every gaming platform. It is AI-assisted.

## Implemented systems

The game provides an eight-room lair map, movement, one quest per room, provisions, care and repair counters, a turn counter, a bounded journal, a quiet layout, and validated JSON saves. Rest grants one provision. Makkakah and aantonymmakkakah actions each spend one provision. Quests grant their recorded reward once. All progress is fictional and local.

Quest completion is a button action, not a test of knowledge, actual care work, scientific correctness, or legal compliance. The game has no battles, monetary rewards, purchases, multiplayer accounts, matchmaking, gambling, robot control, or emergency-response service.

The broader archive remains available through links. Archangel management, IObot, rune conversion, catalogue search, and kerot host tools are not secretly simulated by game counters. The game's care and repair operations are JavaScript mechanics, not programs executed on the K0 interpreter.

## I/O and bounds

Download a save to retain progress after reload. Loading replaces the current game only after validation succeeds. Saves contain room, counters, mode, completed quest IDs, and the last 100 journal entries. Unknown rooms, duplicate quest IDs, unsupported versions, oversized journals, and invalid counters are rejected. Save import is limited to 100,000 bytes. Counters cap at one million. At the turn limit, start another game.

Saves are unencrypted and editable; this single-player game makes no anti-cheat or authenticated-progress claim. It does not store health or account records. No data is uploaded. Invalid saves do not replace the current game; a stale pending load cannot override a newer game action or reset.

## Integration into other gaming software

game.js supplies a host-neutral JavaScript state API: fresh(), validate(state), action(state, type, value), pack(state), and unpack(text). A browser-based host can load that script and render returned states. action returns a new state and does not modify its input. The caller owns rendering, persistence, timing, and player input.

Supported actions are move with a room ID, quest, care, repair, rest, and mode with explore or quiet. There is no arbitrary code execution, process launch, or device command API. A host must handle errors and preserve the stated bounds. A multiplayer host would also need authoritative server validation and authentication, neither supplied here.

No Unity, Unreal, Godot, console, game-store, or existing-game adapter has been implemented. Those require a selected engine, version, integration rights, and platform-specific validation. The JavaScript API is an integration starting point, not a compatibility certification.

## Checks

Run `node software/test_game.cjs`. Tests cover state validation, movement, quest rewards, duplicate prevention, resource exhaustion, care and repair, quiet mode, save round trips, malformed input, bounds, and key UI interactions. They do not certify graphics rendering, platform compatibility, accessibility, or therapeutic benefit.
