# Media, Data and Rendition Workbench

This chamber turns deliberately supplied material into a finite data record, a fictional seed rendition or a book-to-series production plan. The operator first confirms that they can use the material and that participating people consent. These confirmations are recorded assertions. The software cannot determine copyright ownership, verify someone's age or establish that a participant has consented. Work involving real people needs those questions resolved outside the generator before recording or publishing.

## Data to raw, raw to seed and seed to rendition

An owned text export can be supplied as UTF-8; an owned binary excerpt can be supplied as canonical base64. Both routes accept at most 65,536 decoded bytes. A supplied source name accompanies the byte count and SHA-256 fingerprint. The UTF-8 route also returns at most 32 short word samples. The binary route does not interpret or execute its contents. Nothing in this transformation reads another file, probes process memory, connects to an account or performs a disk scan.

The seed is the literal prefix `rasniki-data-seed:` followed by the fingerprint. It is an identifier for those bytes. It does not preserve the original content and cannot restore a deleted file, lost memory or forgotten experience. Keep the original export and a separately verified backup when recovery matters. A matching fingerprint establishes that two byte sequences match; it does not prove that the contents are accurate, safe, lawfully acquired or free from secrets.

The rendition route checks that the supplied seed matches its supplied fingerprint, then uses the existing original-fiction generator to produce between one and 32 prompts. Each result retains the supplied source name and fingerprint, so the operator can return to the intended source. The source bytes are absent from this request and their fingerprint is therefore unverified. These are new fictional prompts, not recovered source prose or a faithful adaptation of the original material. The same seed and count produce the same prompts.

Sensitive records, passwords, private account tokens and material belonging to someone else should not enter an export intended for publication. Review a local export before supplying it, retain access controls on its backup and delete unwanted browser downloads through the usual owner-controlled file tools. The pure Python transformation functions do not retain their inputs; browser displays, downloaded files and an operator's own recordings follow their separate retention choices.

## Book specification to series plan

The production-plan route accepts a supplied title of at most 160 UTF-8 bytes and a book specification of at most 12,000 UTF-8 bytes. Choose one to eight episodes, one to 24 total scenes and one to 30 seconds for each shot. Every episode requires at least one scene, and every requested scene requires at least one supplied word. These limits keep the plan reviewable and its eventual timed presentation bounded to 12 minutes.

The planner divides the source words in their original order across the requested scenes. It assigns consecutive scene numbers, groups them into nonempty episodes and gives each scene one editable text-card shot. A scene includes its source word range, a source excerpt of at most 640 UTF-8 bytes and a flag when the excerpt is shortened. The original specification's fingerprint accompanies the plan. Whitespace is normalized in the excerpts, while the fingerprint refers to the original supplied bytes.

The result is a deterministic production worksheet and timed animatic outline. It does not infer plot structure, invent footage or guarantee cinema quality. A director still develops narrative continuity, visual composition, casting, performance, sound, captions, rights clearances and accessible alternatives. Read each excerpt against its original passage before expanding it into a screenplay. Preserve contextual meaning when a scene is shortened or moved.

The local browser player can display the supplied cards and play permitted local media through the computer's normal screen and speakers. Those are ordinary hardware outputs. They do not modify another person's body, personality, attraction, abilities or beliefs. Optional media playback should respect participants' preferences and allow pausing, muting and leaving the presentation. A multimedia editor should preserve an original copy and make its revised selection and metadata visible before any export.

## Archangel effects and protective review

“Archangel” remains a publication label for voluntary guidance, fictional roles and supplied workpapers. A workpaper may record a wish, a duty, an accessibility adjustment or a proposed protection measure. A generated card does not confer authority over a real person. Image quality, narrative quality and an individual's worth are separate questions; a social-media following list is not a suitable standard for ranking or changing people. This workbench does not fetch the linked Instagram accounts or profile their followers.

Counterdisiri, counterlechery, counter child molestation and other supplied protective labels can accompany a review record, but their presence cannot certify that abuse has been prevented. The practical review asks whether the activity is voluntary, participants' privacy is respected, material is appropriate to their age, and anyone can refuse or withdraw. If a concern needs safeguarding support, use an appropriate trusted human or official reporting channel. The editor is a media tool rather than a substitute for such review.

For publication, the operator checks the original source reference, intended audience, permitted uses, credits and whether real participants have approved their portrayal. No background upload, account recovery bypass, social-media scraping, radio decryption or light-based intervention is part of this chamber. The finite plan and rendition can then enter the edition through its existing form, format, review and reproducible-build process.

## Declared software interfaces

`madrigal_lab.media.raw_seed(record)` accepts `name`, `encoding` (`utf8` or `base64`), `data`, `owned: true` and `consent: true`. It returns the supplied source name, byte count, fingerprint and bounded seed description. Unknown fields and invalid types are rejected.

`madrigal_lab.media.seed_rendition(record)` accepts `seed`, `source_sha256`, `source_name`, `count` from one to 32, `owned: true` and `consent: true`. It returns deterministic original-fiction prompts and the supplied origin reference. A seed whose digest differs from `source_sha256` is rejected.

`madrigal_lab.media.parse_story(record)` accepts `title`, `book`, `episodes`, `scenes`, `duration`, `owned: true` and `consent: true`. Its episode array contains scenes with source ranges and shot cards. Every returned excerpt is ordinary text and must be rendered through a text-safe interface rather than executed as HTML or code.
