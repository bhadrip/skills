---
name: company-diligence
description: Investigate a company for joining, investment research, partnership or vendor selection through product, engineering, security, hardware, UX, GTM, team and financial lenses. Use for substantive company due diligence with traceable evidence, bounded local product tests and a decision-ready report; not routine company summaries or isolated code reviews.
---

# Company Diligence

Produce a defensible assessment of what a company builds, whether customers can use and buy it, how it can fund itself, and what evidence would change the decision. Adopt the relevant specialist perspectives; do not imply actual professional credentials or an audited opinion.

## Frame the decision

Infer the company, purpose and scope from the request and existing work. Establish legal entities and product brands before treating similarly named websites or repositories as one business. A job candidate's target role is separate from the management perspective used in the investigation.

If the user asks to discuss direction first, provide a concise proposed scope and consequential tradeoffs before deep execution. Otherwise proceed with reasonable stated assumptions. Ask only for missing information that materially changes the work. Useful inputs are company/product/job URLs, repositories, geography, decision deadline, available data and authorization for local execution.

Scale the work to the request:

- **Focused review:** investigate selected lenses; retain evidence and uncertainty standards without running a full-company checklist.
- **Full diligence:** cover all applicable lenses, identify inapplicable ones, reconcile conclusions and build the report.
- **Update:** inspect existing artifacts, pinned revisions and source dates; investigate changed or unresolved claims and revise the conclusion instead of restarting.

State what public research, local testing and permissioned data can establish. If signup, paid data, hardware or cloud credentials would unlock material evidence, name the precise dependency and what it would resolve. Continue independent work. Do not make such access a prerequisite when public alternatives are adequate.

## Assemble the investigation

Use independent agents when available and helpful. Give each a bounded question, evidence requirements, exclusive output paths and a review boundary. With limited concurrency, combine adjacent lenses and reserve an independent challenge pass. Without agents, perform the same perspectives sequentially; do not claim independent review.

| Lens | Investigation responsibility | Read when applicable |
|---|---|---|
| PM / product strategy | Buyer, user, job, product maturity, substitutes, adoption, coherent scope | [Commercial and finance](references/commercial-finance.md) |
| TPM | Dependencies, critical path, acceptance criteria, release readiness, costed delivery plan | [Team and execution](references/team-execution.md) |
| Principal engineer | Architecture, integration, correctness, reliability, performance, operability | [Technical lab](references/technical-lab.md) |
| Senior principal security | Trust boundaries, identity, authorization, consent, secrets, data lifecycle, threat model | [Technical lab](references/technical-lab.md) |
| Embedded / hardware | Device lifecycle, provisioning, firmware, resource constraints, physical delivery and support | [Technical lab](references/technical-lab.md) |
| UX / research | First value, consent, errors, recovery, accessibility, workflow friction and net benefit | [Technical lab](references/technical-lab.md) |
| GTM / marketing / sales | ICP, market denominators, competition, willingness to pay, pipeline, channels, acquisition | [Commercial and finance](references/commercial-finance.md) |
| SDM / director | Engineering system, ownership, review quality, capacity, role gaps and hiring order | [Team and execution](references/team-execution.md) |
| Finance / diligence | Entity structure, quality of revenue, cash, obligations, unit economics, funding and equity | [Commercial and finance](references/commercial-finance.md) |
| Independent challenger | Positive and negative cases, alternative explanations, missing proof, numerical and citation integrity | [Evidence and delivery](references/evidence-and-delivery.md) |

Read only the references needed by each lane. Maintain one shared source/finding ledger so different agents do not count the same company statement as independent corroboration. Reconcile contradictory observations explicitly; voting among agents does not resolve evidence.

## Work from claims to tests

1. **Map the business.** Link exact entities, products, target buyers, repositories, deployment surfaces and revenue streams. Separate released, beta, design-only, announced and discontinued capabilities with dates. Do not assume the business is local-only because it advertises private or on-device operation.
2. **Acquire primary evidence.** Inspect company documents, official registries, dated filings, app listings, release history, public code and counterpart sources. Verify changing facts. Record source date, retrieval date, scope and independence. Preserve useful local captures without copying unnecessary sensitive information into the report.
3. **Trace important claims.** For each product promise, find the implementing path and a customer outcome. For each commercial or financial claim, identify the contract, cohort, account or entity that could substantiate it. Label uncertainty before prioritizing it.
4. **Run bounded local experiments when in scope.** Pin source revisions; keep upstream checkouts unchanged. Use synthetic fixtures, an isolated Docker lab where suitable, and native tooling only where necessary. Establish a baseline, inject a specific failure, run a control, and preserve commands/results. Source-only concerns stay source-only. See the technical reference for boundaries.
5. **Build economics from the actual business design.** Separate software, services, hardware, marketplace and financing flows. Reconcile market counts, prices, sales capacity, margins and cash timing. Show assumptions and downside sensitivities rather than inventing missing actuals.
6. **Connect the lenses.** Translate defects into customer impact, support cost, lost conversion, delivery delay or buyer eligibility. Translate GTM promises into engineering and staffing requirements. Avoid assigning dollar losses without a measured baseline or explicit scenario.
7. **Challenge the thesis.** Seek evidence against both optimism and pessimism, compare current substitutes, explain contradictory dates/entities and show what would reverse the conclusion. Consider a narrower viable business, not only the entire platform vision.
8. **Deliver and verify.** Produce the requested format, normally a local HTML report for a broad investigation, with structured evidence and reproducible experiments. Independently review consequential interpretations and calculations; then check rendering and interactions.

## Evidence rules that govern the conclusion

- Distinguish **reproduced**, **source-supported**, **reported**, **hypothesis** and **unknown**. Keep severity separate from confidence. A locally reproduced outcome does not establish production exposure or business-wide incidence.
- Missing public financials, unavailable profiles or absent search results are not evidence of zero customers, insolvency, misconduct or nonexistent agreements. Record search scope and access limits.
- Trace funds through ownership, economic entitlement, transfer restrictions, cash received and current usable balance. A commitment, fund NAV, target AUM, gross transaction value and operating revenue are different quantities.
- Do not rank people by commits, lines, credentials or inferred personality. Analyze observable work and the engineering system; identify hiring missions from missing capabilities.
- Do not manufacture a requested issue count. If asked for a top 50, prioritize 50 distinct supported issues and clearly marked hypotheses only when evidence warrants them; otherwise deliver fewer and explain the gap. Controls, positive findings and untested areas belong in the report too.
- Unknown metrics remain unknown. Do not create a precise valuation, survival probability, security score or current runway from public anecdotes. Scenario inputs must be explicitly hypothetical or linked to supplied evidence.
- The skill does not authorize outreach, account creation, paid services, production probing or changes to third-party systems. Continue authorized local/read-only work and identify concrete access limits. Do not turn routine reversible work into a permission ceremony.

## Artifacts and completion

Use an investigation directory outside this skill repository for company-specific outputs. Keep reusable instructions free of prior subjects, credentials, private data and downloaded company code. Prefer:

```text
investigation/
  report/index.html
  report/data.json
  evidence/                 # dated captures, exact file hashes, run logs
  lab/                      # task-owned Docker/native configs and fixtures
  research/                 # lane analyses, arithmetic and review receipts
  status.json               # scope, revisions, completed work, open questions
  REPRODUCE.txt
```

Read [Evidence and delivery](references/evidence-and-delivery.md) for the JSON contract, report contents, validation and handoff. The optional standard-library validator checks evidence integrity and local report links:

```sh
python3 /path/to/company-diligence/scripts/validate_evidence.py /path/to/investigation/report/data.json --root /path/to/investigation --html /path/to/investigation/report/index.html --output /path/to/investigation/research/validation.json
```

It does not verify factual truth, remote availability, financial formulas or production impact. Perform those reviews separately.

For long-running work, persist progress and evidence after each lane. Resume from the status record. If the user explicitly requests scheduled continuation, use available scheduling tools; do not imply an ordinary turn will keep running overnight. Stop only task-owned services when lab work ends and record retained artifacts. The final answer links the report and states the decision, its strongest evidence, material unknowns and what would change it.
