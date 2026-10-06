# Rasniki I/O, IAU, and IObot editions

Version 0.1 · Implemented local text tools

“Max” is an expansion goal, not unlimited capacity. IAU remains the author's supplied label, interpreted here as an English-form rune notation. IObot means a deterministic text-command interface, not an external AI service. Definitions and implementation are AI-assisted.

## I/O edition

Open io.html. Enter text, import a UTF-8 text file or a Rasniki JSON record, and export text or JSON. Imports accept at most 1,000,000 bytes and working text accepts at most 100,000 UTF-16 code units. Malformed UTF-8 and invalid records are rejected. Import replaces the working text, so export any draft you need to keep first.

JSON records contain format `rasniki-io`, version 1, notation `english` or `iau`, and a text string. The edition field labels notation; it does not validate a language, certify provenance, or assert legal status. Importing does not execute text as code. The page does not retain drafts between loads or transmit them to a server.

## IAU edition

The page maps the 26 English letters to 26 distinct Unicode rune characters. This is a newly assigned substitution mapping, not a historical linguistic reconstruction or any organization's standard. Encoding folds uppercase English letters to lowercase. Punctuation, numbers, and other characters pass through. Decoding maps the selected rune characters back to lowercase English letters.

English text without pre-existing mapped runes round-trips apart from letter case. Mixed text containing those runes may not round-trip, because decoding interprets them as encoded letters. This is readable notation, not encryption or secure storage. Font support and screen-reader pronunciation vary; ordinary English remains available.

## IObot edition

Commands are help, find QUERY, runes TEXT, english RUNES, math OP A B, bitflip BYTE BIT, and show CATEGORY-ID. Math supports add, subtract, multiply, divide, and gcd using the existing exact-integer tool. Find returns at most ten local catalogue results. Commands are limited to 2000 characters. Unknown or invalid commands return an error.

The bot neither evaluates arbitrary code nor launches specialist systems. It has no remote model, shell, filesystem access beyond the user's selected import, background agent, or network operation. Output can be copied explicitly into the text workspace and exported.

## Checks

Run `node software/test_io.cjs`. Checks exercise all-letter rune mapping, case folding, punctuation, record validation, JSON round trips, command routing, limits, and arithmetic. Browser file selection and font rendering need device-specific checks; unit checks do not certify accessibility or file playback.
