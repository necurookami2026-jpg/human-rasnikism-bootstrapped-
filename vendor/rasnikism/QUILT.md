# Executable kerot primitive final-quilt edition

This edition publishes actual K0 source and executable bytecode, rather than encoding documents and calling them programs. Its primary artifacts are language/ostar-final-quilt.kerot, language/ostar-final-quilt.k0, and language/quilt-manifest.json.

The program implements eight finite modes: exact addition of two Boolean bits, sakety planning conditions, asakety review conditions, sake purpose presence, asake reconsideration, makkakah care decisions, aantonymmakkakah reframing decisions, and counterantonymmakkkah reconsideration of a reversal.

Counterantonymmakkkah is retained as the requested edition spelling and provisionally related to the earlier counterantonymmakkakah concept. “Exact science” means the bit-addition result is checked against every Boolean input pair here, not that every scientific or metaphysical claim in the collection has been proved. Ainsuitable, suitable, rawful, and final quilt are edition labels, not independent safety or legal certifications. This is AI-assisted.

## Run the programming-language edition

From the repository root:

```sh
python3 software/quilt.py --mode exact-science --values 1 1
python3 software/quilt.py --mode sakety --values 1 1 1
python3 software/quilt.py --mode counterantonymmakkkah --values 1 1
```

Expected outputs respectively are 2, PLANNING CONDITIONS RECORDED, and PRESERVE USEFUL WORK. These records are not real-world actions or domain judgments.

The target source uses only mark, read, write, choose, step, and signal primitives as applicable. The generator and runner are declared Python host tools, not kerot-derived software. No browser script or document payload runs inside K0.

## Binary input and trace

The first three input bytes select one of eight modes as Boolean bits, most significant first. The following bytes supply that mode's named Boolean fields. Zero is false and any nonzero byte is true; the friendly runner permits only 0 and 1. There is no newline-separated command parser inside K0.

The mode bytes are copied to addresses 60000–60002, the selected mode to 60003, and payload bytes from 60010. The program emits a UTF-8 result and stops through port 2. If input is missing it pauses without pretending a decision was made. Extra input bytes remain unread. All output is deterministic for the supplied Boolean interpretation.

## Exact checks and boundaries

Run `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s software -v`. The quilt checks exhaust every Boolean payload for every mode, compare source assembly to the published binary, verify trace memory and missing-input behavior, and exercise runner outputs. Rebuild with `python3 software/build_quilt.py`.

The program does not certify safety, prescribe care, make contracts valid, authenticate consent, perform spiritual science, or implement every existing browser tool. “Consent” and “permission” inputs are user assertions, not verified facts. It is a finite executable edition with precisely stated behavior, not a finished general operating system.
