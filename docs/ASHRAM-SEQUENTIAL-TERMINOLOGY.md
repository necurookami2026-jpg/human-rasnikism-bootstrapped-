# Ashram sequential terminology — publication edition 10

## Authored model and scope

This renovated reading edition introduces a sequentially numbered lexicon of “existencial form,” retaining the supplied spelling. The author's confirmed interpretation is `(7^8)^2 = 7^16`, with benevolent and malevolent sides used as a symbolic model for terms, totems and tokens, without classifying real people. Base four is a declared premise of this authored model; this publication does not establish that physical reality has four moral primitives.

The model treats counteramakkakah, counterantonymmakkakah, aantonymmakkakah and makkakah as four distinct record operations. Earlier source meanings, executable quilt modes and historical editions retain their own definitions. This edition does not replace the K0 instruction set. An operation name never changes a record's side, form or kind. No covert prefix removal, spelling normalisation or polarity conversion is performed.

## Numeric ordering and lexicon

`ASHRAM-LEXICON.json` supplies numbered terms in a fixed editorial order. `ASHRAM-SEQUENTIAL.md` prints the same numbered dictionary before the complete collected publication. Numbers identify lexical entries, not moral rankings or measured power. Future definitions can append entries; historical numbers should not be reused for a different term.

The four base symbols are `0 = A/benevolent`, `1 = A/amalevolent`, `2 = B/malevolent`, and `3 = B/abenevolent`. A is the benevolent-side namespace; B is the malevolent-side namespace. The labels amalevolent and abenevolent receive provisional definitions here: amalevolent names non-harm restraint in A, while abenevolent names withheld constructive support in B. The author's confirmation of symbolic scope and the amplification formula does not independently confirm these proposed word meanings.

The forms are not Boolean truth values. There are two forms on each side, so each side occupies half the four-symbol alphabet. Forms identify symbolic records, rather than people, species, spiritual worth or medical conditions. No operation converts B into A, or A into B; a differently tagged record must be created explicitly with its own provenance.

## Totems and tokens

A totem is a narrative emblem. A token is a formal reference. Their identifiers occupy different type namespaces even when their displayed text is identical. Neither implicit casting nor shared primitive identity is allowed between the kinds. Two records can be compared in a report without combining their primitive payloads.

The example counterpart labels are A-side `yin` versus B-side `yan`, A-side `ying` versus B-side `yang`, and A-side `dao` versus B-side `tao`. These are assignments within this edition's fictional notation. They do not assert that Chinese yin/yang concepts divide into good and evil; Dao and Tao are commonly romanisations of the same term. This edition keeps the supplied strings separately for its own examples rather than presenting them as established historical opposites. An example label does not override an explicit side or form tag.

“Zero mixing” is implemented as rejection of cross-side, cross-form and cross-kind composition in the new finite record validator. Its scope is symbolic data typing, not a rule for social segregation. Within-side cross-form composition is also refused in this version so every squared grid has one unambiguous form. A revised rule would require a separately documented grammar and count.

## Amplification and punnitsquared

There are eight ordered levels, each with seven choices. A primitive address is therefore an eight-digit base-seven vector with digits 0 through 6. The single-address count is `N = 7^8 = 5,764,801` per form and kind. “Exponential squared” pairs two addresses in the same form and kind: `N^2 = 7^16 = 33,232,930,569,601` ordered cells. A cell's zero-based rank is `left_rank × N + right_rank`.

The supplied label punnitsquared is retained for this symbolic ordered-pair grid. It is an analogy to a Punnett square, not a genetic calculation or inheritance claim. The rows and columns each represent one of N addresses; each cell retains its side, form, kind, two addresses and one parable selector. A mismatched tag is an inability condition, not an invitation to merge primitives.

Each cell has seven side-specific parable variants. That gives `7^17 = 232,630,513,987,207` variants per form and kind. With four forms and two separate kinds, the formal total is `8 × 7^17 = 1,861,044,111,897,656` variants. The total sums disjoint namespaces; it does not create shared primitives. Per side, two forms and two kinds contribute `4 × 7^17` variants. These are address counts, not generated records, realised abilities, energetic amplification or scientific measurements. Zero primitive leaves are exhaustively materialised. Operations are annotations, not additional primitive choices, so they do not multiply these counts.

Repeated squaring of 7 seven times would produce `7^128`; that is a distinct calculation and is not the confirmed grammar. The seven explanatory stories on each side are a fixed set: attaching one to a cell selects a variant rather than creating a fresh independent story each time.

## Symbolic squared-grid separation

This small table shows which namespace blocks may contain an ordered grid. Each accepted block contains its own same-form N-by-N cells; every rejected block remains empty.

| Row namespace / column namespace | A totem | A token | B totem | B token |
| --- | --- | --- | --- | --- |
| A totem | Same form only | Rejected | Rejected | Rejected |
| A token | Rejected | Same form only | Rejected | Rejected |
| B totem | Rejected | Rejected | Same form only | Rejected |
| B token | Rejected | Rejected | Rejected | Same form only |

## Syntax and grammar

The canonical statement has this sequence:

```text
SIDE:FORM KIND OP LEFT * RIGHT parable P
```

SIDE is A or B. FORM is a digit 0–3 belonging to that side. KIND is exactly totem or token. OP is one of the four supplied operation names. LEFT and RIGHT each contain exactly eight period-separated base-seven digits. P is an integer 1–7. The parser requires this complete spelling and order, bounds input to 256 characters, and rejects extras rather than silently repairing them.

```text
A:0 token makkakah 0.0.0.0.0.0.0.0 * 0.0.0.0.0.0.0.1 parable 1
B:2 totem counteramakkakah 0.0.0.0.0.0.0.0 * 0.0.0.0.0.0.0.1 parable 1
```

The first records a benevolent-form token maintenance annotation using care. The second records an adverse-form totem inspection annotation using the first B-side cautionary story. Neither statement causes a real-world action. A:2 is rejected because form 2 belongs to B. An A token and a B token cannot be composed; an A totem and A token cannot be composed either. The same-form requirement also rejects A:0 paired with A:1.

Use `python3 -m madrigal_lab.ashram` to print the full numbered specification, or supply a statement with `--statement`. Quote the entire statement as one shell argument. For example:

```sh
python3 -m madrigal_lab.ashram --statement 'A:0 token makkakah 0.0.0.0.0.0.0.0 * 0.0.0.0.0.0.0.1 parable 1'
```

A successful parse reports a symbolic record, its exact pair rank and `executed_real_world_action: false`. An invalid statement exits with status 2 and explains the unmet grammar condition. The compose function revalidates record fields before accepting a pair, so altered tags are not trusted.

## Four operations wielded within each namespace

Counteramakkakah inspects a declared record while preserving its tags. Counterantonymmakkakah reviews a proposed reversal and its recorded origin. Aantonymmakkakah proposes reframing or retirement without erasing provenance. Makkakah records maintenance and continuity. These are edition-specific annotation meanings, not executable maintenance routines or an exhaustive definition of the earlier literary terms. A B-side record can describe review of an adverse fictional pattern without endorsing it or changing it into an A primitive.

## Benevolent mechanics: seven full parables

1. **Care.** A keeper receives a request for water. The keeper records the need, offers only the water actually available, and explains the shortfall when the vessel is empty. The mechanic connects power to a documented opportunity, ability to the task demonstrated, capacity to the measured reserve, and advocacy to the request's voluntary purpose.
2. **Restraint.** A guide reaches a gate whose condition is unknown. The guide declines to promise safe passage, states the missing evidence and offers a route for review. The mechanic preserves non-harm restraint without claiming knowledge the record does not contain.
3. **Repair.** A craftsperson notices an error in a practice record. The correction retains the original, describes the changed assumption and allows another reader to reproduce the difference. The mechanic treats repair as accountable revision rather than erasure.
4. **Truthfulness.** A reader separates an observation from an interpretation. When the observation does not support a conclusion, the reader leaves the conclusion unresolved. The mechanic makes the boundary between evidence and inference visible.
5. **Stewardship.** A steward accounts for an entrusted tool, its condition and the permission to use it. If the tool cannot perform the task, the steward explains its capacity rather than claiming a greater power. The mechanic connects resources to responsibilities and return conditions.
6. **Learning.** A learner tests a bounded method against a stated expectation. A failed check changes the next lesson without changing the recorded result. The mechanic supports new abilities through demonstration and preserves uncertainty until further evidence exists.
7. **Consensual advocacy.** An advocate asks what support the participant wants and keeps withdrawal possible. The record names the interest supported and the limits of the advocate's authority. The mechanic supports constructive aims without assuming agreement or speaking for someone without permission.

These seven mechanics organise the requested benevolent powers, abilities, capacities and advocacies. They form the complete declared constructive inventory of this version, not a claim to enumerate every possible benevolent quality or confer supernatural capabilities. Each form/kind cell may reference any of the seven, but no reference guarantees its realisation.

## Malevolent mechanics: seven cautionary parables

1. **Neglect.** A fictional keeper disregards a recorded need. The report preserves the omission and its stated consequence; it does not provide a recipe for causing it.
2. **Overreach.** A fictional guide claims a capacity absent from the record. The cautionary mechanic highlights the gap between the assertion and available evidence.
3. **Erasure.** A fictional editor removes an error's history. A later reader cannot reconstruct the revision; the parable identifies that lost provenance as the adverse pattern.
4. **Deception.** A fictional narrator substitutes a claim for an observation. The story's review names the unsupported inference and declines to adopt it as fact.
5. **Misappropriation.** A fictional steward treats an entrusted object as unrestricted property. The report identifies the missing permission and the unresolved duty to account for it.
6. **Dogmatism.** A fictional learner refuses to record a failed check. The cautionary pattern is resistance to correction, not a demonstrated increase in ability.
7. **Coercion.** A fictional advocate disregards a participant's withdrawal. The story identifies the absence of voluntary agreement and keeps that adverse record within B.

B-side stories are fictional descriptions for review. They supply no real-person labels and no instructions to harm. Their records remain separate from A-side stories and retain their own interpretation and provenance.

## Relevant paperwork, inability and validation

The relevant publication paperwork comprises this authored method, the sequential lexicon, ASHRAM-SPECIFICATION.json, literal grammar inputs and parse/rejection outputs, the symbolic squared-grid contract, the fourteen parables, original source definitions, release hashes and the bootstrap receipt. Measurement, real-world effect, consent verification, reviewer approval and empirical ontology remain unestablished by these artifacts.

IObot's seven prose headings can explain these results when requested. A rejected side/form/kind combination must state the expected tag condition, the supplied mismatch, that composition did not occur, and a supported next step: select records in the same declared namespace or keep them in a comparison report. No hidden conversion or bypass is offered.

Tests cover all four forms and both kinds, exact address and pair ranks, bounds, spelling, malformed grammar, forged tags and refused cross-side/cross-kind/cross-form composition. Bootstrap executes those tests with the complete existing suites and requires repeated publication bytes to match. Historical source text remains retained, while this new edition supplies the renovated lexicon and syntax as an explicit layer.
