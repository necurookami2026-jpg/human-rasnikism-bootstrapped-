# Rasniki archive

The collection starts at `index.html`. Browser tools use native HTML, CSS, and JavaScript without external libraries or services. The Python-hosted K0 assembler and interpreter live in `software/kerot.py`. The collection includes lore, dictionaries, local management and voting records, game mechanics, I/O, search, planning, and manual tools. Catalogue statuses distinguish working features from proposed specialist systems.

Open `index.html` directly in a browser, or serve it locally:

```sh
cd /workspace/rasnikism
python3 -m http.server 8000 --bind 127.0.0.1
```

Edit the dictionary cards and sections directly in `index.html`. Search reads the visible dictionary text, so new cards automatically participate. Changes are local until committed and published separately.

The vocabulary is provisional and AI-assisted. It does not establish an authentic inherited tradition, a complete language, or compliance with a non-AI authorship requirement. The initial composition examples are creative conventions awaiting the author's definitions.

Run the implemented software checks from the repository root:

```sh
node software/test_manuals.cjs
node software/test_ostar.cjs
node software/test_jerry_pop.cjs
node software/test_reinterpret.cjs
node software/test_templates.cjs
node software/test_systematics.cjs
node software/test_game.cjs
node software/test_archangel.cjs
node software/test_catalogue.cjs
node software/test_search.cjs
node software/test_io.cjs
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s software -v
```

Node.js is a test host, not a browser runtime dependency. Browser rendering, media playback, accessibility, and external platform integration require their own checks. A passing suite does not establish professional advice or legal validity. Local records disappear on reload unless downloaded; exports are unencrypted.

The common Ostar browser format uses `ostar.css` and `ostar.js`; the latter carries a reading edition in local-page URLs. After modifying root-level Markdown, run `python3 software/build_editions.py` to refresh the three compiled Markdown editions. Do not edit generated files in `editions/` independently of their sources.

The primary published collection uses `encoded/*.io` and the offline data script `publication-data.js`. After any source change, run `python3 software/build_io_publication.py` and `node software/test_publication.cjs`. Do not edit the encoded artifacts independently. Browser document links open the encoded reader; original source filenames remain provenance labels inside the records.

The executable target publication is `language/ostar-final-quilt.kerot` plus its `.k0` bytecode and integrity manifest. Rebuild with `PYTHONDONTWRITEBYTECODE=1 python3 software/build_quilt.py`, verify with the Python suite, and run named modes through `software/quilt.py`. The .io bundles carry source/reference records; the .k0 file is a direct executable artifact for the declared host interpreter.
