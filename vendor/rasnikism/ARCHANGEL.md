# Archangel Rawful systems and ministry workspace

Version 0.1 · Rasniki fictional framework and local management prototype

Archangel Rawful is a fictional organizing name, not a claim of supernatural authority. Rawful continues to mean direct making, observation, and revision; it does not displace legal obligations. The requested “arhcangel” is presented as “archangel” for readability. Unfamiliar names have proposed meanings only. This edition is AI-assisted. “Max” is an expansion goal, not exhaustive implementation.

## Systems glossary

| System | Proposed scope |
| --- | --- |
| Ethics | Examine effects, consent, fairness, evidence, and accountability. |
| Ethicalism | Maintain a revisable record of ethical commitments and their practice. |
| Huwsters | Participants who choose to contribute to the fictional community. |
| Huwsterics | Inquiry into how those participants cooperate and resolve disagreement. |
| Huwsterism | A voluntary tradition of care, feedback, and shared responsibility. |
| Riceness | A provisional name for generosity and sufficiency in shared resources. |
| Rice | A provisional resource-and-provisioning category, including ordinary food where relevant. |
| Polite | Address people respectfully while allowing firm disagreement. |
| Politness | Review whether courtesy supports understanding or obscures an unresolved issue. |
| Liberalics | Examine liberty, pluralism, autonomy, and their practical limits. |
| Liberalism | A discussion category for political traditions called liberalism; no single interpretation is imposed. |
| Socialics | Examine cooperation, institutions, shared needs, and distribution. |
| Socialism | A discussion category for political traditions called socialism; no single interpretation is imposed. |
| Account management | Keep local metadata about accounts the user is authorized to manage. |
| Profile management | Edit a local display name, biography, and chosen participation boundary. |
| Publication management | Track a work's title, status, rights basis, and next review. |
| Account ministry | A voluntary stewardship role for questions, permissions, and handoffs. |
| Republication copyleft | Check the actual license and permissions before redistributing a work. |
| Management | Coordinate records, owners, actions, and review dates. |
| Ministry | A voluntary service role without implied governmental or religious authority. |
| Archangel afaustian | A provisional literary commitment to reject coercive bargains and preserve the ability to refuse. |
| Afaustian software | Tools whose purposes, limits, exits, and data handling remain visible. |

The workspace shows these definitions and permits independent discussion. Political labels do not assign a reader's beliefs, membership, or allegiance.

## Ethical review cycle

1. State the intended benefit and whose interests are affected.
2. Separate established evidence, interpretations, and unknowns.
3. Check consent, permissions, and the ability to decline or leave.
4. Consider competing views and foreseeable consequences.
5. Choose a bounded action with an owner and review date.
6. Record results, correct mistakes, and revise or stop as needed.

Calling an action ethical does not establish its effects. Record disagreement without ranking people's worth or diagnosing their motives.

## Implemented management scope

Open archangel.html. The local workspace edits a profile, tracks account metadata and publication records, displays the systems glossary, exports records as JSON, and clears the current session. Account records include only a service label, account alias, and stewardship note. They do not contain passwords or tokens. The application does not log into services, create external accounts, publish content, send messages, manage permissions on a platform, or verify identities.

Publication states are draft, review, published, and retired. A state is the user's recorded assertion, not proof that publication happened. A published record must include a reference, but the workspace does not verify that reference. Review notes record rights and unresolved questions rather than asserting automatic legal validity.

Records stay in memory until explicitly downloaded. Page reload discards them. Exported JSON is unencrypted; do not enter secrets, health records, or another person's private information. Clear removes this page's records; it does not remove previously downloaded files or remote data.

## Republication and copyleft

Identify each work's author, source, actual license, notices, and modification history. Establish that the person granting permission can do so. Check the license's redistribution obligations, including source availability where required. Record third-party assets and their separate terms. A copied title or a copyleft label alone does not establish permission.

This repository retains its existing GPL version 3 license file. The checklist does not change that license or apply it automatically to every linked work. Legal requirements may vary with the work and circumstances; seek appropriate review when unclear.

## Optional panic-support panel

The panel offers a pause, gentle grounding prompts, and a space to type a contact or next step. It does not diagnose, prescribe, administer medication, summon a supernatural agent, monitor the user, or contact anyone automatically. “Soul panic” remains the author's expression; it is not presented as a clinical diagnosis.

If someone is in immediate danger, may hurt themselves or another person, or has severe symptoms that could be a medical emergency, they should contact their local emergency service or ask a nearby person for help. For ongoing or recurring distress, an appropriate healthcare professional can help assess what is happening. The tool has no location detection or verified emergency-number database.

Grounding suggestions are optional: find a comfortable place if possible, notice a few objects around you, feel the support of the chair or ground, and contact someone you trust. Do not force breathing exercises or continue a prompt that makes distress worse.

## Limits and checks

Most named ethical and political systems are definitions and review practices, not autonomous software institutions. The management workspace is a local prototype. It has no server, durable database, access control, encryption, or professional-care service. It does not attempt to manage every possible panic case.

Run `node software/test_archangel.cjs` for record validation, states, export, deletion, and core UI transitions. Unit checks do not establish clinical efficacy, legal compliance, spiritual effects, or comprehensive accessibility.
