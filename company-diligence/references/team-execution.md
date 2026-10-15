# Team, ownership, and execution diligence

Read this when assessing whether the visible organization can deliver the proposed product and close the evidenced risks.
Evaluate observable work and operating design; public activity is a partial view of people, not a performance review.

## Construct a fair evidence sample

Define repositories, date window, branch/revision, selection criteria, API pagination limits, and retrieval time before interpreting activity.
Sample work across critical domains and risk levels, including ordinary maintenance, incident recovery, migrations, product delivery, and release acceptance.
Read PR changes, discussion, review events, status checks, linked issues, and follow-up fixes; PR titles and descriptions alone are insufficient.
Record current draft/open/closed/merged status from direct records, not a stale search snippet or an earlier snapshot.
Distinguish author, coauthor, original contributor, reviewer, committer, merger, maintainer, bot, and generated contribution.
Preserve credit when work is harvested, squashed, rebased, or landed through another PR.
A closed-unmerged PR may be superseded or incorporated elsewhere; inspect the disposition before drawing a conclusion.
Missing visible reviews mean review was not observed in the sample; review may occur privately or outside the platform.
Separate author-reported tests from attached logs, independently reproduced checks, and deployment acceptance.
Record counterevidence and previously fixed problems, not only examples that support a negative thesis.

## Describe contribution without ranking people

Use an evidence card for each relevant contributor or role:

| Field | Required content |
| --- | --- |
| Identity | Public account, work-related name if explicit, identity-match confidence |
| Observed work | Specific change and its customer or operational purpose |
| Evidence | PR/source/review links, status, revision, retrieval date |
| Demonstrated practice | For example, bounded recovery, careful measurement, or cross-platform coordination |
| Limits | Sample coverage, unverified claims, missing deployment or private-work evidence |
| Follow-up | A concrete walkthrough, acceptance receipt, ownership clarification, or handoff exercise |

Do not rank ability or performance by commit count, lines changed, PR count, review count, or time online.
Activity volume can describe repository concentration only with context such as bots, merges, generated code, and sampling bounds.
One strong artifact demonstrates that practice in that artifact; it does not establish overall seniority, sole authorship, or consistent execution.
Do not infer low capability from absent public work, a small sample, a job title, institution prestige, or a young repository.
Assess engineering reasoning through specificity: explicit tradeoffs, confounds, tests that could fail, recovery design, and correction of mistaken claims.

## Public professional credentials and identity

Use public work-related biographies, directly linked professional profiles, publications, conference records, and official institutional or employer sources where relevant.
Prefer an explicit account-to-profile cross-link; a shared common name or photograph is insufficient to join identities.
Keep identity matching separate from credential verification: a linked profile can identify a person while its employment or degree remains self-reported.
Record each credential as self-reported, company-reported, independently supported, or unresolved, with source date and scope.
Use an available signed-in browser/profile only within the user's authorized scope. If required access is unavailable, mark the credential unverified and use attributable public alternatives; do not bypass access controls or scrape private profiles. Do not inspect unrelated tabs or personal account content.
Use publicly indexed material only when clearly attributable and label that limited provenance.
Collect no unrelated sensitive traits, personal contact details, age guesses, or family information.
Resolve ambiguous matches by leaving them unresolved or requesting an authorized clarification, not by guessing.
Credentials provide context; engineering conclusions must still rest on relevant work evidence.

## Map responsibility to acceptance

Build an ownership matrix by customer outcome and failure boundary, not merely repository or job title.
For each critical domain, identify accountable decision-maker, implementer, independent acceptor, operational owner, and backup; mark unknown roles explicitly.
Cover product scope and customer learning; dependency planning; architecture and reliability; security authority; embedded/hardware qualification; UX; release operations; and budget/headcount.
Distinguish the assessment lenses from proposed hires: one person may cover multiple roles, and a title does not prove responsibility.
Look for decision clarity at cross-team boundaries such as native/cloud lifecycle, consent/data export, firmware/app rollout, and support-to-engineering escalation.
Check whether acceptance is attached to the shipped revision and supported platform, and whether rollback/recovery has an owner.
Evaluate independent review quality using substantive challenge and risk coverage, not merely an approval checkbox or reviewer count.
Treat missing public ownership as a diligence question until corroborated; do not present an invented organization chart as fact.

## Capacity, concentration, and operating metrics

Estimate capacity with explicit assumptions for allocation, on-call, maintenance, support, recruiting, onboarding, and parallel-work contention.
Identify critical knowledge concentration using observed ownership and recovery dependency; commit concentration alone cannot establish bus factor.
Use a practical handoff test: can a secondary operator diagnose, deploy, roll back, or recover from documented evidence without the primary owner?
Prefer metrics tied to outcomes: correctly completed customer tasks, recovery time, cleanup backlog, acceptance coverage, support load, and rehearsed secondary ownership.
Define denominators, time windows, unknown states, and measurement sources; do not claim an SLO or trend from a single sample.
Separate a process hypothesis from a measured recurring failure, and an existing blocker from a newly discovered one.

## Costed staffing and sequencing

Translate each evidenced constraint into an outcome, required capability, accountable owner, dependencies, acceptance gate, and estimated effort range.
Compare reassignment, scope reduction, automation, specialist review, contract work, and hiring before recommending headcount.
For each proposed hire, specify the work unlocked, timing, loaded annual cost range, recruiting/onboarding delay, and opportunity cost.
Use dated, geography- and level-appropriate compensation sources when available; otherwise label numbers as scenario assumptions.
Include benefits/payroll burden, equipment, recruiting, management time, and contractor differences; keep equity, cash expense, and runway effects distinct.
Sequence foundational ownership and correctness work before expansion that depends on it; make the order follow the actual bottleneck.
An initial phase should establish the customer workflow, baseline, owners, and a reviewable fix or acceptance gate.
A subsequent phase should prove repeatable delivery and recovery on the real provider/device boundaries relevant to the product.
Expansion should depend on measured customer outcomes, operating load, economics, and a successful secondary-owner handoff.
Present staffing as conditional choices with triggers, not an unsupported universal team size or a judgment about named people.
End with a short set of evidence requests that would change the recommendation, such as a serving revision, incident receipt, capacity allocation, or verified pilot result.
