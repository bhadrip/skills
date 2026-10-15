# Evidence, report and verification

## Evidence contract

Use this portable JSON contract for `report/data.json` when the included validator is useful. Additional fields are allowed. A narrower investigation may omit empty `experiments`, `metrics` and `assumptions` lists; do not invent records just to populate a report.
Empty ID-reference lists may be omitted unless the evidence grade or metric basis requires references under the rules below.
For an entirely fictional dossier or skill exercise, add `subject.provenance: "synthetic"` and label the report visibly. This is separate from using synthetic test fixtures against a real company's code; fictional claims must never become company evidence.

| Record | Required fields | Meaning |
|---|---|---|
| Root | `schema_version: 1`, `subject`, `sources`, `findings` | Subject has `name`, `as_of`, `decision`; dates use ISO 8601 |
| Source | `id`, `title`, `url`, `accessed_at`, `evidence_class`, `publisher_group`, `scope`, `artifacts` | URL can be null for supplied/private/local evidence; scope states what is supported and limited |
| Artifact | `path`, `sha256` | Path relative to investigation root; digest of exactly that file, not another representation |
| Finding | `id`, `lens`, `title`, `claim`, `evidence_grade`, `severity`, `confidence`, `source_ids`, `impact`, `recommendation`, `validation`, `boundary` | Separate observed outcome, inference, business impact, remedy and validation plan |
| Experiment | `id`, `revision`, `environment`, `command`, `expected`, `observed`, `control`, `artifacts`, `scope_limit` | Control explains comparison and outcome, or an explicit reason it was unavailable |
| Metric | `id`, `name`, `value`, `unit`, `period`, `population`, `basis`, `source_ids` | Preserve denominator, accounting period, currency and entity; unknown value is null |
| Assumption | `id`, `name`, `value`, `unit`, `rationale` | A scenario input, not a discovered company fact |

Source `evidence_class`: `primary_record`, `company_statement`, `independent_reporting`, `source_code`, `local_experiment`, `provided_document`.

Finding `evidence_grade`:

- `reproduced`: preserved local execution outcome, requiring `experiment_ids`; scope is exact tested revision/environment.
- `source_supported`: code or document supports the bounded claim; runtime/commercial outcome may remain unverified.
- `reported`: someone asserts the result; attribution is part of the claim.
- `hypothesis`: plausible risk or opportunity needing a specified test; do not write it as a discovered failure.
- `unknown`: material question without enough evidence to infer an answer.

Severity: `critical`, `high`, `medium`, `low`, `opportunity` or `unrated`. Confidence: `high`, `medium` or `low`. Use severity for consequences and confidence for evidence quality. Positive observations can use `opportunity` or `unrated` without implying defects.

Metrics use basis `documented`, `reported`, `assumed`, `derived` or `unknown`. Documented/reported values need source references. Assumed values need `assumption_ids`. Derived values need `formula` and `input_ids` resolving to metric/assumption IDs. Do not hide hypothetical inputs inside a number labeled actual. Use distinct IDs when periods, populations, entities or business lines differ.

Findings may additionally contain owner, affected revision, file/line citation, experiment IDs, acceptance criteria, dependencies, remediation cost range, alternative explanations and related finding IDs. Keep one finding per independently actionable underlying problem; group duplicate symptoms and do not inflate counts.

## Acquisition and traceability

- Record source location, redirect target if material, retrieval time and publication/effective date. A newly retrieved page may contain an old disclosure.
- Prefer primary records, filings, original data tables, release artifacts, official prices and counterparty statements. A company page establishes what it says, not the truth of every claim.
- Group syndicated stories, company-owned domains and repeated URLs by `publisher_group`. Multiple captures are not multiple independent confirmations.
- Save raw response and readable extraction separately when useful. Give each its own artifact record and SHA-256; never attach a raw HTML hash to a text extraction.
- Preserve exact commit hashes and line anchors for code. Mutable branch links alone are insufficient for reproducibility.
- Browser observations should record URL, time, visible text and limits. Do not claim a downloaded screenshot or file exists unless saved. Avoid retaining tokens, session data or unrelated personal information.
- Log unsuccessful searches with queries, sources and access limits. A blocked endpoint or zero results cannot establish a negative corporate/legal fact.
- Contradictions need a reconciliation note: dates, entities, definitions, changed product state, possible explanations and required definitive evidence.
- Keep lab logs and company statements distinct. Test counts describe checks performed, not security assurance. When a test is mocked, synthetic, static, source-only or unable to run, say so next to the conclusion.

## Report design

For broad diligence, produce a standalone local HTML report with embedded styles/scripts and no rendering dependency on third-party assets. Keep evidence links relative to the investigation root so the folder can move together. Escape untrusted source text before inserting it into HTML. Provide machine-readable data, reproducible commands and a date.

Adapt the report to the decision; useful sections are:

1. **Decision brief:** judgment, strongest positive and risk cases, confidence boundary and changes from earlier assessments.
2. **Entity/product map:** who owns, employs, sells and builds; product/repository/release status and local/cloud dependencies.
3. **Prioritized findings:** evidence grade, impact, proof, limitation, remedy, owner and acceptance test; searchable/filterable for larger sets.
4. **Technical lab:** revision/environment matrix, baseline/control/failure results, recovery, performance boundaries and untested surfaces.
5. **Market/GTM:** buyer and user, source-backed TAM/SAM/SOM, competitors, route to market, funnel assumptions and testable positioning.
6. **Organization/delivery:** observed ownership/review patterns, missing capabilities, funded hiring order and a costed near-term roadmap.
7. **Finance/viability:** entity-to-cash bridge, quality of revenue, unit contributions, cash conversion, obligations, sensitivities and data-room gaps.
8. **Decision gates:** evidence needed before joining, investing, partnering, scaling a product or accepting deployment risk.
9. **Evidence ledger:** dated sources, independence, raw/readable captures and search/access limits.

Show a coverage matrix for the requested lenses: executed, source-only, unavailable or inapplicable, with the reason and next useful evidence. An unavailable lens is not a completed investigation or automatically an adverse finding.

An interactive sensitivity is useful when inputs materially change the decision. Make assumption labels visible before controls. Display units and denominators. Separate operating cash burn from financing; stop temporary support at its stated horizon. Distinguish exit ARR from recognized yearly revenue and present negative cash as an additional funding requirement. Do not silently reset invalid inputs or impose unexplained bounds. Include zero-margin, negative-contribution and funding-expiry cases where applicable.

Use diagrams when they clarify ownership or dependency. Use tables for comparable offers/metrics. Avoid a composite score that treats unavailable information as failure. The number of issues or source records is not a measure of company quality.

## Review and meaningful checks

Before handoff:

- Trace consequential claims to supporting passages, code paths or run artifacts; inspect nearby qualifications. Review monetary amounts, dates, units and entity identity independently.
- Recalculate market denominators and financial equations separately from the implementation. Test zero contribution, negative contribution, zero opening liquidity, upfront obligations, support expiring mid-horizon and exhaustion before expiry. Test material new edges introduced by the model.
- Check HTML IDs, relative links, citations, unique ledger IDs and exact artifact hashes. Run `scripts/validate_evidence.py` for the contract above; do not describe its pass as substantive fact verification.
- When available and within the requested scope, open the report in the supported browser, inspect representative narrow/wide layouts, and exercise filters, disclosures, presets and reset behavior. Check labels and conclusions reflect changed scenarios. If UI access is unavailable or prohibited, deliver with the precise visual/interaction checks marked unverified. Do not claim print/export or mobile testing that was not performed.
- Ask an independent reviewer to challenge causal claims, negative inferences, source independence, comparability and the strongest alternative strategy. Supply raw evidence, not only the writer's summary. Record findings and resolution; stale hashes do not certify changed artifacts.
- Save review receipts with exact artifact revisions/hashes and scope. Fix material discrepancies, then repeat affected checks rather than endless broad retesting.

## Handoff and limits

No signup is needed merely to read a local report. State real account/device/data dependencies still needed to test the product or settle a decision. Distinguish a finished public-evidence review from a financial audit, hardware certification, production penetration test or confidential data-room process.

Keep working files outside the reusable skill. Stop only task-owned containers/services, preserve useful evidence and revisions, and record reproduction steps. Leave user-owned applications and unrelated infrastructure intact. Do not publish reports, contact subjects or send applications as an implicit part of diligence.

End with a clear conditional decision: what evidence currently supports, what it cannot establish, and the smallest next evidence set that would change the conclusion.
