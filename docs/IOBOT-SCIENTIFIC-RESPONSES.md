# IObot automatic scientific prose responses

## Implementation and entry point

Open `madrigal_lab/web/iobots/index.html` directly, or start `python3 -m madrigal_lab --port 8765` and visit `http://127.0.0.1:8765/iobots/index.html`. The desktop links the updated bot from Bots & servers and Dictionary & curriculum. This is a maintained derivative of the pinned Rasnikism IObot. The original `vendor/rasnikism/io.html`, source files, tests and source-lock records remain intact.

Automatic mode is enabled initially. The bot responds 350 milliseconds after the latest input edit; Enter and Respond run immediately. Turning automatic mode off cancels pending work. Editing the input discards the previous report so an export cannot silently retain stale evidence. There are no unsolicited remote messages, network calls or autonomous external actions.

## Response vocabulary

The author's supplied vocabulary is used as an ordered reporting scheme, with the following provisional meanings for this implementation. It does not redefine ordinary science terminology.

| Heading | Recorded meaning |
| --- | --- |
| this | Supplied request, response status and condition code |
| ahow / hot | How the method operates and what actually ran |
| awho / tho | Who supplies the request and which component responds |
| awhat / that | What result or inability was observed |
| awhen / then | When input triggers a response and the sequence of processing |
| awhere / there | Where interpretation and evidence reside |
| awhy / thy | Why the result or inhibition occurred, limits and next steps |

Each individual word is also accepted as a heading inquiry. An inquiry returns the reporting scheme; it does not invent an answer about an unspecified person, event, location or cause. For example, `awhen` explains the local trigger sequence rather than claiming to know an external event's date. `hot` is the supplied partner of `ahow`, not an inferred temperature measurement.

## Executable method and finite exactness

The existing command tool implements `help`, `find QUERY`, `runes TEXT`, `english RUNES`, `math OP A B`, `bitflip BYTE BIT`, and `show CATEGORY-ID`. Math accepts add, subtract, multiply, divide and gcd with exact JavaScript BigInt integers. Division returns an integer quotient and remainder, not a rounded decimal. Each integer operand is limited to 1000 characters; the command itself is limited to 2000 UTF-16 code units. `math gcd 42 30` returns the literal `6`. `math divide 7 2` returns `3 remainder 1`. A zero divisor is rejected with a prose explanation.

Search queries are limited to 200 characters and return at most ten local catalogue records. A no-match report describes the search outcome; it is not proof of nonexistence. Catalogue statuses, purposes and review text are retained. Byte-bit operations retain their original input constraints. Rune conversion uses the original English-letter substitution and folds case; it is notation, not encryption. The original I/O workspace's file exchange limits remain documented in `vendor/rasnikism/IO.md`; the new response page adds command reporting and exports, not file imports.

“Exact science responses” here means named inputs, a documented method, literal output or observed rejection, declared bounds and a reproducible explanation. This command bot cannot independently establish empirical facts, measurement uncertainty, personal identity, causation, legal approval or external capabilities. It records unknown evidence as unestablished, rather than filling missing paperwork with invented findings.

## Inability, limits and inhibits

A waiting report identifies absent input. An invalid-input report identifies a non-string argument to the response function. A command-limit report identifies an oversized command, records its original length and a bounded preview, and does not invoke the interpreter. An unsupported-command report identifies a capability that the implemented command vocabulary cannot perform. An operation-rejected report preserves the interpreter's actual reason, including division by zero, malformed integer operands, invalid bit positions, unknown categories and query bounds. A no-match report identifies a completed search without results.

These are observable interface conditions. The bot does not diagnose hidden motives, physical causes or unknown system restrictions. Its full explanation states whether processing occurred, the reason actually available, relevant limits and a concrete next step: supply missing input, correct the indicated field, shorten or split input, select an implemented operation, or obtain the evidence and authorised implementation needed for a different capability. Splitting input does not prove the equivalence of separate calculations; users must review each result. Limits are not bypassed.

## Full response paperwork and evidence

Every response carries format/version, status, condition code, the bounded supplied request, original request length, a truncation flag, literal result, inability reason, seven prose sections, limits and scientific scope. Its `paperwork` field contains a complete Markdown response, including the supplied request, literal output and an evidence/review paragraph. JSON preserves this structured record alongside the full prose.

Use Download full paperwork, Download response JSON or Print paperwork. These are deliberate user actions; no background storage or publication occurs. The response page uses `textContent` to display user input and output as text, including any markup-like strings. Exported Markdown retains the user's literal input as evidence; read it as source text when evaluating untrusted material. The page makes no independent claim that a downloaded record is authenticated. File retention and review are the user's responsibility.

Relevant paperwork consists of this method contract, the seven-section generated report, the literal request and result, the original I/O command contract, retained catalogue status/review entries when searched, provenance in `docs/REPUBLICATION.md`, and the publication release hashes and bootstrap receipt. For an empirical task, separately supply measurement records, units, instrument/calibration evidence, uncertainty, reviewer/date and corrections. These external records are not automatically generated or approved by the bot.

## Reproduction and checks

```sh
node tests/iobot-responses.cjs
sh bootstrap.sh
python3 tools/publication.py build --check
```

Checks cover every supplied heading alias, exact calculation output, division by zero and malformed requests, unsupported capabilities, no-match reporting, oversized-input refusal before execution, full paperwork and UI input-change behaviour. Bootstrap retains its full source-integrity and upstream suites and requires identical publication builds. This contract is included in the collected publication; pinned historical sources retain their original bytes.
