# Rasnikism bootstrapped edition

Ainsuitable Kerot primitive · Ostar · Makkakah · Aantonymmakkakah

This edition packages the complete upstream collection, its glossary, K0 assembler and interpreter, executable quilt, and encoded document publications. “Max” means the full currently implemented collection. Kerot is the primitive mark and foundational machine operations; ainsuitable means conformity to the documented specification. See [the glossary](index.html#dictionary), [Kerot specification](KEROT.md), and [upstream provenance](UPSTREAM.md).

## Bootstrap and validate

Prerequisites: Python 3 and Node.js. No third-party package installation is required.

```sh
sh bootstrap.sh
```

This rebuilds the executable Kerot quilt and all three reading and encoded editions, runs the existing Python and JavaScript suites, and exercises the executable Aantonymmakkakah mode. Run it from any working directory; the script selects its own checkout.

## Reinterpretable programming

Open `jerry-pop.html` to edit all eight quilt modes, all five primitive examples, and the four templates. Record source/input/driver revisions, reinterpret them, replay earlier revisions, and export/import history across reloads. See [the programming contract](REINTERPRETATION.md).

## Run

From this repository:

```sh
python3 -m http.server 8000 --bind 127.0.0.1
```

Open `index.html` for the glossary, `ostar.html?edition=aantonymmakkakah` for the requested reading edition, `jerry-pop.html` for browser execution, or `language.html` for executable source and bytecode.

```sh
python3 software/quilt.py --mode aantonymmakkakah --values 1 1
python3 software/quilt.py --mode asakety --values 1 1
python3 software/quilt.py --mode asake --values 1
python3 software/quilt.py --mode makkakah --values 1
```

The complete eight-mode contract is in [QUILT.md](QUILT.md). Python and JavaScript are explicit hosts. This is a host-bootstrapped software edition; a native boot image and Magrigal operating system remain unimplemented. Existing definitions, scope limits, and GPL license are retained. This edition is AI-assisted.

## Original destination README

# rasnikism-bootstrapped
sethianism thaumaturgism, romanticism, wizardism, altruism, florist, vampirist, rapist children of men kindred 
