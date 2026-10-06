# Exact Sciencerainbowrainbowscience — paperwork and computerwork

Publication edition 8 adds this reading lens to the complete wolf-password edition 7 collection at commit `075bcc9631420af2a3118a9f63b9bdfe33ca3f55`. The spelling Sciencerainbowrainbowscience is retained as the requested edition name. “Exact” describes preserved source bytes and rational arithmetic under stated assumptions. The publication retains all prior collected chapters, four parallel reading guides, the extra complete volume, code, tests, original licences and source provenance.

## Paperwork: seven ordered workpapers

Use the printable `SCIENCERAINBOWRAINBOWSCIENCE-PAPERWORK.html` beside the new full reading edition. Print to paper or save as PDF using the browser's Print command. Each colour is an organisational heading and a declared calculation sample, rather than a physical boundary. The seven colours are a conventional teaching sequence; the visible spectrum is continuous, and perception depends on the observer and conditions.

1. **Red — question and scope.** State one testable question, the system and units, exclusions and acceptance criteria. For the exercise: does converting each declared vacuum wavelength to frequency and back retain the exact original value?
2. **Orange — source and provenance.** Record repository, revision, file path, licence, byte size and SHA-256. Preserve the original evidence before interpreting it. The full upstream file manifest is `publication/wolf-password-origin.json`; the historical four-source lock remains `publication/source-lock.json`.
3. **Yellow — assumptions and method.** Declare vacuum propagation, the defined SI value `c = 299792458 m/s`, and the conversion `1 nm = 1/1000000000 m`. Use `f = c / λ`. No measured uncertainties are supplied for these chosen samples.
4. **Green — computerwork and observations.** Execute the documented command, retain its literal JSON, record Python and Node versions and the bootstrap receipt. Distinguish a generated result from a measurement.
5. **Blue — comparison and falsification.** Compare expected and actual values. Require exact wavelength round trips and decreasing wavelength/increasing frequency across the seven samples. Record discrepancies and failed checks without deleting evidence.
6. **Indigo — review and correction.** Record reviewer, date, unresolved questions, changed assumptions and versioned corrections. If using measured wavelengths, include instrument calibration and uncertainty; rational arithmetic does not remove measurement uncertainty.
7. **Violet — publication and reproduction.** Record release revision, output hashes, commands, host versions and receipt. Repeat the build and compare bytes. Keep the finite conclusion attached to its assumptions.

Each sheet provides fields for question, input, units, assumptions, expected result, actual result, evidence, uncertainty, reviewer and correction. Empty fields remain work to be completed by the reader; they are not automatically approved.

## Computerwork: exact finite spectrum exercise

Run from the checkout root, with Python 3.10 or newer:

```sh
python3 tools/rainbow.py
python3 tools/rainbow.py --output rainbow-observations.json
sh bootstrap.sh
python3 tools/publication.py build --check
```

The output option creates a new record and refuses to replace an existing file. The bootstrap also publishes `SCIENCERAINBOWRAINBOWSCIENCE-COMPUTERWORK.json`. Seven chosen wavelengths in nm are red 700, orange 620, yellow 580, green 530, blue 470, indigo 445 and violet 400. Fractions retain frequency in exact Hz; no binary floating-point rounding is introduced. The red example is `428274940000000 Hz`, and converting it back yields `700 nm`.

These samples are an illustrative model, not measured wavelength distributions, universal colour definitions or a simulation of refraction, dispersion, scattering, rain droplets or perception. The executable Kerot quilt remains available separately at `vendor/rasnikism/language.html`; this Python exercise does not extend its instruction set or implement native firmware.

## Full edition and evidence

`SCIENCERAINBOWRAINBOWSCIENCE.md` contains this edition guide and the complete standard collected body. The searchable offline reader links the new edition, printable paperwork and machine-readable computerwork. All new generated artifacts are included in `release-hashes.json`, and all existing editions remain reproducible. Bootstrap runs the current Python and JavaScript checks, the pinned contractual tests, Guardian tests and the complete upstream Rasnikism bootstrap, then builds twice and requires byte equality.

The receipt records which checks actually passed on the executing host. “Max quality” here means the complete supplied collection, preserved provenance, explicit methods, tested arithmetic and repeatable publication. It is not a claim that every proposal in the source has been implemented or scientifically established.
