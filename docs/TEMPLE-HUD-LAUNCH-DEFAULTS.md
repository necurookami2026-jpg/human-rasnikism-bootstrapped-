# Temple blueprints and personal HUD — edition 12

## Seven default design priorities

Huwster Rasnikism now opens with a configurable temple blueprint and HUD above its existing architecture workbench. For a fresh or reset session, the exact temple order is botanical primary, rural secondary, urban tertiary, artificial quaternary, aggrestral quinary, modder sexenary and ley line septenary. Personal settings may nominate another primary template; all seven remain available. The default priority and ordinal labels are published in TEMPLE-HUD-DEFAULTS.json.

The botanical temple is the primary layout style, while its interior foliage uses artificial botanicals. An artificial-foliage material preference does not promote the quaternary artificial temple to first place. Botanical, rural and urban name design contexts; the artificial template is modular/simulated, aggrestral is a provisional cultivation/landscape interpretation of the supplied term, modder provides reversible maker/workshop space, and ley line uses symbolic connecting paths without claiming measurable spiritual energy lines.

The SVG blueprint supplies seven nonoverlapping schematic zones and connecting paths. Coordinates are conceptual grid units, not construction dimensions. It does not verify structure, drainage, fire escape, accessibility, zoning or site suitability. A real build requires a site survey and qualified architectural, engineering and jurisdiction-specific review. The default SVG can be downloaded or exported with validated custom preferences.

## User-supplied interior brief

The author prefers artificial botanical products rather than sacrificing plants for decorative interiors, and requests ancient-jungle scenery reminiscent of dinosaur-era movie depictions, Vancouver-inspired coastal forests, Yosemite-inspired valley forests and alpine settings. This release implements four original style presets: ancient-jungle, coastal-forest, valley-forest and alpine. They are schematic palettes and scenery briefs, not copied film assets or photorealistic reconstructions of historical ecosystems.

The default is rich ancient-jungle detail with artificial botanicals, simulated daylight, repairable furnishings and reusable scenery. Other styles are selectable in the HUD. Artificial botanicals are a material preference, not proof of a lower lifecycle impact; a real procurement plan should review materials, manufacturing, reuse and disposal using supplied evidence. Products and furnishings should serve a supplied client brief; if none exists, record and serve the supplied owner brief. This is a design orientation, not an automatic assignment of duties to a person.

No specific Amazon brands were named, so none are assumed. The brand/style field accepts only voluntarily supplied names. The software does not read purchase history, authenticate an Amazon account, order goods or spend money. “Great expenditure” means layered multientity artistry across primitives, composites, mechanics, chronological, structural and architectural layers. Its fashion references are paisley chic, Victorian Gothic and steampunk. Benevolent and malevolent Ashram motifs remain distinct symbolic design groups, coordinated through the selected palette rather than mixing primitives. Nomichenpenall records the author’s client-compatibility label without inventing a scientific definition. Rich interior detail remains editable. Budget amount and currency remain unset, and purchasing is disabled.

## Counter-review and settings terminology

The interior review label is maximum documented counteramakkakah and counterantonymmakkakah review. All supported configuration fields are checked against the declared schema before a blueprint is accepted. In this context, maximum means review of the implemented settings surface, not unlimited protection or universal suitability.

The settings terminology retains counteramakkakah, counterantonymmakkakah, aantonymmakkakah, makkah, ainsuitable, suitable, hen, apen, nomic and henapenall. The supplied spellings counteramakakah and counterantonymmakkah are recorded as aliases for the configuration labels; this does not alter the historical K0 modes or automatically create language-wide prefix/suffix rules. Ainsuitable/suitable here refer to conformity to this particular schema. Hen, apen and henapenall remain provisional labels without additional executable guarantees. Nomic denotes the documented version/review context rather than automatic lawmaking.

The persona title is **Rasniki Hoppit Huwster Demihuman**. It is a fictional HUD identity and decorative design brief, not a classification of the user, a biological claim or a third-party franchise licence.

## HUD customization and launch behaviour

The HUD provides seven panel labels: blueprint, settings, world, paperwork, ranks, lore and evidence. Settings remains visible so a user can recover hidden panels. Blueprint and settings have standard side-by-side and focused layouts. Users can select temple preference, palette, artificial botanical style, detail level, density and text scale, and show/hide the available panel groups. The settings schema limits text scale to 85–140 percent and accepts only declared panel, palette and template values.

Apply to this session changes the current view without saving a profile. Save local profile requires a supplied nickname and an explicit action, and stores the validated settings in this browser's local storage. On the next launch, a valid saved profile is restored. Reset launch defaults removes that local profile and restores the anonymous botanical-first defaults. Unreadable, invalid or inaccessible storage produces an explanation and leaves standard defaults available. A local nickname is not an authenticated login; this release contains no account service. With no saved valid profile, the session remains anonymous and unpersonalised by default.

Brand names and profile text are displayed as inert text and do not become executable markup. A blueprint is returned through a validated local API and shown as an SVG image. Download settings exports the current JSON record; Download blueprint SVG exports its schematic. No profile is sent to an external service. The local server validates settings to render a blueprint but does not persist the profile; explicitly chosen browser storage and downloads are the retention mechanisms.

## Runtime and publication compatibility

A world run receives the applied launch settings and includes its temple blueprint in the final-quilt result. The result hash includes that blueprint, so two otherwise identical worlds with different temple preferences have different final records. Applying new settings invalidates an older world export. Original source, legal draft corpus, career/rank records, Ashram grammar and historical licences remain intact. The 5,764,801-document corpus is not regenerated for a HUD change; its existing generation-input fingerprints and archive hashes remain checked.

Ostar Rawful remains the default publication mode. The new default JSON and SVG are hash-recorded publication outputs, and this contract is included in every complete reading edition. Earlier budgets or stylistic descriptions in historical sources remain in their original context; the current HUD uses the explicit defaults described here.

## Verification

Python tests exercise the exact seven-template order, independent default objects, valid personal preferences, schema refusal, default non-purchasing state and final-quilt hashes covering the blueprint. Chromium checks exercise fresh anonymous defaults, ancient-jungle artificial botanicals, explicit profile save and restoration, reset, panel visibility and world integration. The existing full bootstrap and repeated publication checks run alongside these changes.

```sh
python3 -m unittest discover -s tests -p test_temple.py -v
sh bootstrap.sh
python3 -m madrigal_lab --port 8765
```

Optional browser reproduction uses Playwright and Chromium already available on a suitable host: run `node tests/temple-browser.cjs` against the local service. Browser tests are not required dependencies for the Python/Node-only bootstrap.
