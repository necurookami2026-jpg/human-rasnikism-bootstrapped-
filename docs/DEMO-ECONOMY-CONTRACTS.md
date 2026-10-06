# Ruddered demonstration economy and contractual revision

This chamber joins a finite accounting exercise to a finite document workflow. Its unit is `DEMO_CREDIT`, an integer counter stored in the local laboratory database. The software makes no payment, opens no bank account, issues no public currency, charges no interest, and connects to no financial provider. A balance is an exercise record. A finalised contract is an internally consistent document revision with local assertions attached. Its receipt does not identify a person or create an enforceable agreement.

The practical aim is to make an undertaking legible. A learner can distinguish a proposal from a funded obligation, a repayment from a new issuance, a price illustration from a transfer, and an unchanged parent document from a later revision. The same distinction applies to a box office, franchise kiosk, merchandise exercise, household budget, community project, charity proposal or fictional ministry: selecting that label changes the narrative, while the ledger rules stay the same.

## Account, amount and the named vocabulary

`account`, `amount`, `debt`, `deficit`, `credit` and `discount` have narrow meanings in this implementation. An account is a named local ledger bucket. An amount is a positive integer from 1 through 1,000,000,000,000. A funded debt is an obligation whose lender has transferred an existing balance to its borrower. A deficit can describe a negative calculated net position; it does not authorise an overdraft. A credit is an exercise unit or the positive side of a posting, with its context recorded. A discount coupon is a single-use annotation of an imagined price reduction, with no ledger movement.

The publication preserves `count`, `aamount`, `imbalance`, `abalance`, `amint`, `racasidy`, `casidy`, `asupsidy`, `abenefit`, `gravy`, `ashanty` and `accredit` as requested vocabulary. Their invented spellings are not silently expanded into financial rules. A worksheet can state the meaning its author proposes for a term and the established operation, if any, it refers to. Until that definition exists, it remains an unresolved label. For example, a writer may propose `amint` as a display label for the existing demo mint, but this proposal grants no minting authority outside the exercise. A proposed `asupsidy` label does not make a coupon spendable or create an entitlement.

`economic coin`, `economic groin` and `republic credits` can appear as fictional display names for the same `DEMO_CREDIT` counters. They introduce no cryptocurrency, wallet secret, token market or exchange rate. A narrative described as `gravy`, revenue, passive income or franchise returns records an assumption when the learner supplies one; this software does not promise earnings or model a real investment. A counter copied into another story remains a counter.

## Conservation before enlargement

The existing `Ledger` keeps each movement as two postings: a negative delta in one account and an equal positive delta in another. The reserved `issuer` account is the balancing side of a demo mint. Ordinary transfers cannot use it as a source. The `Economy` wrapper adds obligation, coupon and contract tables in the same SQLite database without altering the original ledger class. Its lending and repayment paths only transfer existing units between ordinary accounts.

A proposed obligation contains a lender, borrower, principal and title. Creating it moves nothing and its outstanding amount is zero. Funding it requires the lender to have the full principal. Funding inserts the transfer and changes the obligation to `funded` in one transaction. A failed balance check leaves the obligation proposed and inserts no postings. A funded obligation cannot be funded again.

A repayment transfers units from the borrower to the lender and increases the obligation's paid amount in the same transaction. A partial repayment leaves the state funded. Paying exactly the remaining amount changes the state to `settled`. Repayment cannot exceed the outstanding amount, cannot draw an overdraft, and cannot run after settlement. Each obligation permits at most 256 repayment records. Its final available record is reserved for settling the entire outstanding amount: after 255 partial repayments, another partial repayment rejects before changing balances or debt, while payment of the full remaining amount can complete the obligation. If either the postings or the obligation update fails, SQLite rolls back both. This is an accounting property of the local application; it is not a recovery promise for an external service.

Consider a lender given 100 demo units. A proposed principal of 40 leaves its balance at 100. Funding leaves the lender at 60 and the borrower at 40, with a receivable and payable of 40 respectively. Repaying 15 leaves balances of 75 and 25, with a remaining obligation of 25. The lender's calculated position is 75 + 25 = 100; the borrower's is 25 − 25 = 0. Repaying the final 25 restores the lender's balance to 100 and settles the obligation. None of these steps creates additional units.

The portfolio uses `balance + receivable − payable` as a local demonstration net position. It does not price risk, recognise collateral or determine legal net worth. The report also checks each ledger entry's two postings, the funded principal against its recorded transfer, and repayments against their linked entries. `independent_audit` remains false because this is an internal consistency check over the same locally editable database.

## Coupons and subsidy illustrations

A coupon has a title, positive integer face amount and either `discount` or `subsidy` as its kind. It starts available and can be assigned once to an existing ordinary account. Redemption changes only the coupon record. It creates no balance, makes no payment, and asserts no right to goods or services. The returned field `transfers_units` is always false.

Use this worksheet for an ordinary educational price example:

> Item or service: ______. Imagined gross price: ______ demo units. Coupon kind: discount / subsidy. Coupon face amount: ______ demo units. Intended recipient account: ______. Fictional conditions: ______. Actual ledger movement: none. Real issuer, real redemption and payment integration: absent.

The implemented kinds describe budget illustrations. There is no coupon operation for an attack, bodily service, coercion or exclusion. Titles supplied by an operator are ordinary record text and are not endorsements, entitlements or instructions to carry out the named activity.

## Contractuals and a final quilt receipt

The document workflow has three states: `proposed`, `reviewed` and `finalised`. A proposed contract holds a title and text. A local operator records review by naming a reviewer and passing the literal Boolean `True` as `consent_asserted`. Finalisation separately names an author and requires the same explicit Boolean assertion. Strings such as `"yes"`, the integer `1`, omitted values and false do not count as assertions. Neither field verifies the named person's identity or agreement.

The content hash covers the record ID, version, parent ID, parent content hash, title and full text. A final receipt covers that content hash together with the recorded author, reviewer and their assertion fields. Verification recomputes the hashes and follows the parent chain. A successful check means these locally stored fields are consistent with the stored digests. Someone able to rewrite the database can also rewrite digests; therefore these checks are not signatures, external timestamping, witness testimony or proof of authenticity.

A finalised document remains retained. To change its terms, create a child with `parent_id` pointing to the intact finalised revision. The child receives the next version number and stores its parent's content hash. It begins proposed and must pass its own review and finalisation. Multiple proposed alternatives can share a parent; the software does not choose between them or silently replace the parent. An altered parent, damaged receipt or broken revision chain blocks creation or review of a dependent revision.

“Final quilt” can name this finite closing receipt in the publication. It means completion of this local workflow for this revision. It does not make every future interpretation final, settle an external debt, or override the source quilt's bounded Boolean semantics. The source modes `asakety`, `asake`, `sake` and `sakety` can supply exercise records elsewhere in the laboratory; their outputs do not establish actual safety, consent or contractual authority.

Use this document template before creating a proposed revision:

> Document title and purpose: ______. Version parent, if any: ______. Participants as supplied by the local operator: ______. Defined terms: ______. Voluntary proposed activities: ______. Demo units and their meaning: ______. Scope and end conditions: ______. Review date: ______. Author's local assertion: ______. Reviewer's local assertion: ______. External agreement, legal review or independently verified evidence, if any: ______. Unresolved questions: ______.

## Working API and finite limits

The wrapper can be used directly without the browser. This example creates local exercise accounts and records one partial repayment:

```python
from madrigal_lab.finance import Ledger
from madrigal_lab.economy import Economy

ledger = Ledger('.lab-state/demo.sqlite3')
ledger.account('lender')
ledger.account('borrower')
ledger.mint('lender', 100)
economy = Economy(ledger)
obligation = economy.create_obligation('lender', 'borrower', 40, 'Learning exercise')
economy.lend(obligation['id'])
economy.repay(obligation['id'], 15)
report = economy.report()
```

Run the example in a fresh exercise database; repeating the mint adds another issuance. Existing accounts and records persist across application restarts. The wrapper refuses a database, parent directory or SQLite sidecar that is a symlink. It accepts only the existing `Ledger` object rather than a remote URL or arbitrary database connection.

The complete public methods are `create_obligation(lender, borrower, amount, title='Demo obligation')`, `lend(obligation_id)`, `repay(obligation_id, amount)`, `create_coupon(title, amount, kind='discount')`, `redeem_coupon(coupon_id, account)`, `create_contract(title, text, parent_id=None)`, `review_contract(contract_id, reviewer, consent_asserted=False)`, `finalise_contract(contract_id, author, consent_asserted=False)`, `verify_contract(contract_id)` and `report()`.

The obligation, coupon and contract collections each permit at most 256 records. Repayments permit at most 256 records per obligation, with the last available record reserved for full settlement; the 256-obligation limit bounds the total to 65,536 repayment records. IDs are positive integers from 1 to 256; Boolean IDs and amounts are rejected. Titles have at most 120 characters, author and reviewer labels at most 80, and contract text at most 16,384 UTF-8 bytes. Accounts retain the ledger's letter-led, at-most-40-character naming rule, and `issuer` stays reserved. The recursion in revision verification is bounded by the retained record count. No method expands “all recursively” into an infinite document, executes a contract's text, deciphers a password, changes another provider's access decision or publishes personal financial records automatically.
