# Systematics, negotiation, and reflective spiritual voting

Version 0.1 · Local Rasniki management prototype

The spiritual voting system is interpreted as a voluntary reflective process: participants can state values, reasons, and choices about a proposed change. It does not measure spiritual truth, speak for supernatural beings, authenticate voters, or constitute an official election. An individual can use it for personal deliberation or keep authorized records of a small discussion. This framework and its provisional vocabulary are AI-assisted.

## Named systems

| System | Proposed purpose |
| --- | --- |
| Archangel Yorkie | Attentive companionship, small acts of care, and clear boundaries. |
| Archangel Anticlaw | Review unwanted pressure, coercive arrangements, and permission boundaries. |
| Blue Esteemer Anticlaw | Support respectful self-regard while resisting coercion and humiliation. |
| Archangel Spiritual Sciences | Separate observation, interpretation, belief, and testable claims in a reflective inquiry. |
| Counterantonymmakkakah | Reconsider a reframing or release process itself, preserving useful work and correcting mistaken reversals. |
| Rasniki Counterantonymmakkakah | Apply that reconsideration to the Rasniki collection. |
| Blue-only Counterantonymmakkakah | Apply it within the explicitly chosen Blue framework; “blue only” limits scope, not the rights or worth of other people. |

The request's “rasiniki” and “counterantonymmakkkah” are treated as provisional spelling variants; the interface uses Rasniki and counterantonymmakkakah consistently. These names do not describe attacks on software, people, or other communities. Anticlaw is an ethical boundary metaphor here, not a security product or an external-platform integration.

## Implemented management

Open systematics.html. Select a system and propose replacement wording for its definition. Record a purpose, reasons, and a bounded participant list. Each proposal starts an open voting round. Record one choice per declared participant: yes, no, or abstain. A later choice replaces that participant's earlier vote in the current round.

Amending wording or reasons increments the proposal revision, preserves the prior round, and clears votes so a changed proposal does not inherit approval of its old text. Participant membership is fixed for the proposal; create a new proposal to change it. Existing vote reasons remain recorded in the prior-round history.

Quorum is a majority of the declared participants, rounded down plus one. Abstentions count toward participation but not toward yes/no preference. Acceptance requires quorum and more yes votes than no votes. A tie remains unresolved. An accepted proposal must be applied explicitly. Applying replaces only the chosen system's local definition and closes the proposal as adopted. Another open proposal for that system becomes stale and cannot be applied until reviewed and amended against the new system revision.

The user is responsible for recording only their own vote or another participant's explicitly authorized statement. Names are labels, not authenticated identities. Anyone with access to this page can alter its records. This is a deliberation aid, not tamper-proof governance or proof of democratic legitimacy.

## Negotiation cycle

State the issue. Hear differing reasons. Offer a specific change. Ask whether its effects, permissions, and boundaries are acceptable. Amend when necessary. Record votes without inventing consent. Keep a clear distinction between accepted wording and changes actually applied. Permit someone to leave a discussion without surrendering their rights.

An individual may name themselves as the sole participant; the resulting decision is a personal record, not community authorization. Spiritual language remains a chosen expressive layer, not a test of a person's value or belief.

## Spiritual sciences record

Use the separate inquiry fields for an observation, interpretation or belief, testable claim, method, and uncertainty. A belief need not be presented as measured evidence. A testable claim requires an appropriate method and results before a scientific conclusion can be drawn. This tool provides no experiment, clinical assessment, or supernatural validation.

## Data and bounds

Records are held only in the current page until exported as unencrypted JSON. Reload starts fresh. Exports include definitions, proposals, participant labels, choices, reasons, and inquiry notes. Do not enter secrets or private information about other people. No messages are sent, remote systems edited, elections run, or external accounts accessed.

Limits are 50 proposals, 50 participants per proposal, 50 revisions per proposal, 5000 characters of system wording, and 2000 characters per reason or inquiry field. Clearing resets the page's collection; it does not delete exported files or external records.

## Checks

Run `node software/test_systematics.cjs`. Tests cover quorum, abstentions, ties, replacement votes, revisions, vote reset, stale proposals, explicit adoption, bounds, exports, and key UI transitions. These checks do not authenticate votes, verify scientific claims, or establish legal or political authority.
