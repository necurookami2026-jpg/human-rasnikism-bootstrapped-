# Edition 9 IObot validation

Full bootstrap passed on 2026-10-06T20:52:52.586297+00:00. [Receipt and commands](edition-9-validation/receipt.json), [IObot input hashes](edition-9-validation/iobot-input-hashes.json), and per-check logs are retained.

The new Node suite verifies every requested heading alias, exact integer output, arithmetic and input rejection, missing and unsupported commands, no-match results, command bounds before execution, complete paperwork, automatic input response, cancellation and stale-evidence removal. Loopback HTTP smoke checks also fetched the new bot page, response engine and method document successfully. The complete upstream and pinned-source checks passed; publication builds matched byte for byte.

This is a browser-local deterministic command bot; remote natural-language inference, external messaging and empirical investigation are not implemented.
