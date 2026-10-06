# Executable publication — edition 14

The publication is distributed as executable software and a local browser app. `releases/huwster-rasnikism.pyz` is a single-file Python executable archive, not a native Windows EXE or macOS application bundle. Python 3.10 or newer and a browser for GUI/HUD are required. It extracts bundled files into a temporary directory, serves only loopback, and removes that directory at exit. Persistent user state is `.huwster-state` beneath the launch working directory; choose a writable working directory or supply `--state PATH` before the command.

## Run

- `python3 releases/huwster-rasnikism.pyz gui`: browser app and HUD.
- `python3 releases/huwster-rasnikism.pyz hud`: browser app with personalizable HUD.
- `python3 releases/huwster-rasnikism.pyz reader`: whole collected publication reader.
- `python3 releases/huwster-rasnikism.pyz read --edition rawful`: terminal reading; raw, law, lawful and complete are also available.
- `python3 releases/huwster-rasnikism.pyz catalogue`: publication index as JSON.
- `python3 releases/huwster-rasnikism.pyz run examples/huwster-commons.world`: compile and run an external world script, output final quilt JSON.
- `python3 releases/huwster-rasnikism.pyz action health-catalogue`: inspect educational modules.
- `python3 releases/huwster-rasnikism.pyz action health-workpaper --json @record.json`: process explicit local input.
- `python3 releases/huwster-rasnikism.pyz serve --port 8765`: start without opening a browser.

Linux/macOS can mark the archive executable and run it directly. A checkout also has executable `./huwster` CLI, `Huwster.command` for macOS/Linux and `Huwster.cmd` for Windows with the Python launcher installed. Stop the server with Ctrl+C. If automatic browser launch is unavailable, open the printed localhost URL manually. No installation, cloud model or network service is required for the included finite software.

## Coverage and limits

The archive includes the current complete collected reader, all four full reading editions, modules, HUD, methods, examples and bundled vendor runtime resources. The 367 MB corpus archives and historical `sources.zip` remain companion repository downloads. Links to those companions require the checkout/server with those files; the portable archive does not embed them. The publication's prose, archival material and proposals are readable data; only implemented commands are executable. Running prose does not make proposals operational.

No executable can guarantee absence of inability, disability, inhibition or limitation. Hardware, permissions, dependency availability, finite compute budgets, validation and unsupported features remain real conditions. Errors are disclosed instead of represented as success. This app does not bypass another platform's owner settings, policies, access controls or laws. There is no unrestricted generative chatbot in this release.

Non-graphic discussion of child sexual abuse, prevention, safeguarding, reporting and survivor support is legitimate educational material. It is not categorically unavailable. Sexual content involving children is outside this app's educational scope. Existing safeguarding documentation remains included. The reader displays publication text; it does not certify medical/legal claims or contact emergency services.

## Rebuild and verify

Run `sh bootstrap.sh`, then `python3 tools/package_app.py`. `releases/huwster-app-manifest.json` records the executable's SHA-256 and size. The package uses sorted entries and fixed timestamps. CLI and reader checks exercise the actual archive rather than only the source launcher.
