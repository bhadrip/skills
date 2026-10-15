# Commercial, product, market, and financial diligence

Use this reference for product strategy, market sizing, go-to-market analysis, company viability, or joining/investing/vendor decisions. Select the relevant modules; do not force a full financial review onto a narrow product question. Findings should change a decision, identify a falsifiable experiment, or request evidence that resolves a material uncertainty.

## Evidence and accounting boundaries

- Set an as-of date, decision horizon, geography, currency, legal entity, offer, and business model before comparing claims.
- Label each material input as observed fact, company claim, independently corroborated fact, analyst assumption, derived calculation, or unknown. Calculations inherit their inputs' limitations.
- Record source date, period measured, unit, exact scope, independence, retrieval date, and the claim actually supported. Newer retrieval does not make an old measurement current.
- A company's announcement, founder interview, reseller copy, and articles repeating that announcement are one underlying source. Trace citations to their origin before counting corroboration.
- Company material establishes what was claimed or offered. Independent counterparty evidence may establish a relationship; contracts, delivery, billing, collections, and cohorts establish different commercial facts.
- Missing public evidence means unknown within the search performed. It does not establish zero revenue, nonexistent contracts, insolvency, misconduct, or absence of financing.
- Preserve conflicting dated statements until a documented bridge explains them. Do not silently choose the most favorable version or treat different entity names as interchangeable.
- Search current authoritative sources for changing prices, competitor capabilities, market populations, regulations, and financing facts. Use access limitations explicitly; never imply a paid database or data room was accessed when it was not.
- Keep actuals, forecasts, illustrative scenarios, and counterfactuals separate. Do not produce a synthetic diligence score, precise success probability, or valuation unsupported by the available evidence.

## Product and segment thesis

Build an offer map before estimating a market. One brand may contain unrelated businesses with different buyers, revenue recognition, delivery costs, and capital needs.

| Field | Questions that change the thesis |
|---|---|
| User and beneficiary | Who performs the work, who benefits, and who bears new review or consent work? |
| Buyer and authority | Who owns budget, signs, approves security, and can veto adoption? |
| Problem and trigger | Which recurring job is costly now; what event creates urgency and a buying window? |
| Current alternative | What happens without this product: incumbent tool, manual work, service provider, internal build, or no action? |
| Offer and entitlement | What is delivered, by whom, over what period, at what price and usage limit? |
| Value and friction | What net outcome improves after setup, review, training, switching, and support? |
| Dependencies | Which integrations, permissions, data rights, hardware, or procurement steps must succeed? |
| Revenue and cost owner | Which entity invoices, collects, fulfills, pays vendors, and carries refunds or warranties? |

- Segment by workflow, urgency, buyer, firm size, geography, installed systems, procurement burden, and willingness to pay. Industry labels alone rarely define an actionable initial customer profile.
- Separate users, seats, purchasing organizations, locations, transactions, and end beneficiaries. A multi-location company may have one budget; one user may hold several accounts.
- Choose a beachhead using observed pain, reachable buyers, purchase authority, repeat frequency, deployment effort, competition, and delivery economics. Make the strongest alternative segment explicit.
- Test problem and solution separately: evidence that a job is painful does not establish that this offer solves it or that this buyer will pay.
- Inspect the end-to-end workflow: discovery → qualification → trial/pilot → setup → first valuable job → repeated use → payment → renewal. Identify the main drop-off and its owner.
- Compare promised outcomes to released capability and actual adoption. Demos, repositories, feature counts, and roadmap claims do not establish reliable customer value.
- Evaluate roadmap work by its link to a buyer outcome, adoption bottleneck, price realization, retention, or cost reduction. Include maintenance, integration, migration, and support capacity.
- Define a bounded experiment with target segment, offer, price, baseline, denominator, observation period, owner, and advance/stop criterion. Avoid expanding to multiple markets before one workflow is repeatable.
- Interview or contact customers only when authorized. Without access, provide a concrete interview/measurement plan and label willingness to pay and ROI as untested.

## TAM, SAM, and SOM with defensible denominators

1. Define the billable unit and market boundary first: organizations, eligible seats, devices, usage, or transactions. State whether the value measures buyer spending, supplier revenue, GMV, or contribution.
2. Find a measured population in public administrative data, official business statistics, licensing records, procurement records, or comparable primary datasets. Prefer downloadable records or tables that allow reproducible filters.
3. Record dataset vintage, classification version, geography, reporting threshold, coverage exclusions, unit, and refresh cycle. Distinguish enterprises, establishments, registrants, employees, households, and accounts.
4. Preserve raw observations and document filters, joins, deduplication keys, exclusions, and calculations. Cite the specific table, series, field, or query used rather than only the publisher's homepage.
5. Do not add overlapping registries or adjacent industry counts. Keep a comparator population separate unless records can be reconciled and deduplicated.
6. Do not multiply marginal percentages as though they measure an intersection. If joint eligibility is unavailable, report bounds or an explicitly assumed qualification rate and prioritize obtaining the cross-tab or records.
7. Derive annual spend from observed comparable contracts, current relevant prices, buyer budgets, or a labeled willingness-to-pay hypothesis. Explain which price includes implementation, support, hardware, usage, and discounts.
8. Separate free entry offers from hypothetical paid packages. A listed price without a billing interval is not MRR; a free product does not imply the company has no other revenue.
9. Calculate TAM from eligible units and annual realized spend, avoiding double counting alternative offers sold to the same budget. For multiple mutually compatible products, make attach rates and overlap explicit.
10. Narrow SAM using product readiness, geography, integrations, buyer eligibility, procurement, channel access, and support capacity. A company directory count is not evidence that its members are serviceable buyers.
11. Derive SOM from execution capacity over a stated horizon, with acquisition cohorts, sales cycle, deployment capacity, churn, expansion, and collections. A chosen percentage of TAM is not an execution model.
12. Triangulate bottom-up results against an independent spending or population lens. Reconcile differences in units and scope; do not average incompatible estimates to create apparent precision.

Use formulas with named inputs and units:

- `Annual TAM = eligible billable units × annual realized spend per unit`; extend by nonoverlapping segment only when definitions match.
- `SAM = sum(serviceable eligible units by segment × applicable annual spend)`; uncertain serviceability is an assumption, not a measured fact.
- `New customers_t ≤ min(qualified opportunities from prior cohorts × observed win rate, sales capacity, onboarding capacity)`; account for stage timing and prospect exhaustion.
- `Customers_t = retained prior customers + new live customers_t`; distinguish signed, launched, billed, and collected cohorts.
- `Exit ARR_t = current annualized recurring contract value of live eligible customers`; it is neither cumulative revenue nor cash received during the horizon.
- `Marketplace revenue = eligible transaction volume × realized net take rate`; do not present transaction value as company revenue.

Show low/base/high cases only when each changes explicit drivers. Report sensitivity to the few inputs that dominate the result and state which new observation would narrow the range.
Do not infer software spending from client assets, deposits, sector GDP, fund assets, or total transaction value without a demonstrated monetization mechanism and justified take rate.

Use enrichment tools, including Clay or HG Insights when available, to identify accounts, technographics, roles, or contacts. Treat them as sampled, potentially stale enrichment, not an authoritative census or proof of demand.
Check coverage bias, duplicate firms, parent/subsidiary relations, stale titles, and inferred fields against primary records. Use named-account samples to test reachability and fit, not to extrapolate an unrepresentative response rate.
Separate measured population, modeled eligible population, enriched prospect list, contacted accounts, qualified opportunities, and paying customers in both prose and arithmetic.

## Competition, positioning, marketing, and sales

- Compare current direct competitors, adjacent tools, bundled incumbent features, internal builds, service providers, and doing nothing. Include alternatives buyers actually evaluate, not only companies using similar technology.
- Use a dated comparison of buyer, core job, deployment, integrations, pricing unit, contract minimum, support, switching cost, security eligibility, and demonstrated outcome. Flag unverified cells instead of treating silence as a missing feature.
- Normalize price to the same buyer, usage, contract term, support level, and workflow. Vendor throughput, benchmark, or customer claims require matching hardware, workload, concurrency, quality, and service level before comparison.
- State a falsifiable reason to win: lower total workflow cost, unique access, better reliability, difficult integration, trusted distribution, or another measured buyer outcome. An architectural choice alone is not a moat.
- Examine durability: incumbent bundling, supplier dependence, switching friction, data rights, customer-owned data portability, distribution control, and the time/cost for a competitor to reproduce the advantage.
- Write the strongest countercase: why the buyer might prefer the incumbent, defer purchase, reject new workflow friction, or find the differentiated feature insufficient to fund a separate contract.
- Tie positioning to a specific buyer, urgent problem, proof, alternative, and purchase trigger. Assess whether site messaging, packaging, onboarding, and sales collateral support the same offer.
- Evaluate marketing by qualified demand and cohort economics. Traffic, impressions, followers, downloads, email opens, and event attendance are intermediate signals whose downstream conversion must be measured.
- For each channel, record audience, acquisition mechanism, attribution rule, spend including labor, qualified opportunities, signed customers, collections, retention, and contribution. Separate paid, organic, founder network, affiliate, reseller, and product-led cohorts.
- Check blended CAC against marginal CAC at the next spending level; founder relationships, launch publicity, and early adopters may not recur. Attribute multi-touch paths transparently rather than double counting wins.
- Define funnel stages and observation windows. Report stage counts, conversion, time-in-stage, disqualification reasons, and losses; distinguish leads from qualified opportunities and trials from paid pilots.
- Treat recent open opportunities as censored observations when measuring win rate and sales cycle. Segment enterprise procurement, self-serve, pilots, and founder-led deals rather than averaging incompatible motions.
- Examine discounting, free implementation, custom engineering, founder time, payment terms, and guarantees required to win. These affect realized price, scalability, and contribution.
- Test renewal and expansion against the same eligible cohort. Report small cohorts as counts alongside percentages, and distinguish retention of accounts, users, revenue, and valuable workflow activity.
- Measure customer ROI net of implementation, training, consent, correction, review, internal operating costs, and fees. Time saved is not automatically payroll savings or additional revenue; validate the conversion mechanism.
- Distinguish a partner logo, developer program, purchased software, cloud credit, listing, referral contract, co-sell agreement, and guaranteed purchases. Each supports a different claim.
- Verify partner scope, counterparty, effective date, commercial rights, obligations, exclusivity, referrals, attach rates, and attributable paid customers. Lack of public corroboration does not disprove a private agreement.
- App-store availability proves distribution availability; ratings and download bands do not establish active users, unique people across channels, paid demand, or retention. Reconcile analytics to billing before using scale claims.

## Entity, capital, revenue, and cash reconciliation

Create a dated entity map for employer, contracting seller, merchant, IP owner, equity issuer, parent, affiliate, fund, manager, and general partner where relevant. Record exact legal names, identifiers, jurisdiction, ownership, and documented reorganizations.
Formation, public launch, brand adoption, registration renewal, and current good standing are different facts. A database identifier or expired identifier renewal does not establish solvency, dissolution, or regulatory approval.
Reconcile headline financing through the following bridge before discussing runway:

1. **Whose capital:** identify owner, legal vehicle, date, currency, and whether the amount is raised capital, a target, NAV, committed capital, client assets, debt, paper gains, or cash.
2. **Economic entitlement:** identify the operating company's legally documented ownership or claim; shared founders and branding are insufficient.
3. **Availability:** examine liquidity, restrictions, redemption rights, investor consents, covenants, taxes, currency controls, senior claims, and timing.
4. **Transfer:** distinguish intent, commitment, condition satisfaction, actual transfer, and ledger classification as equity, debt, fees, service revenue, or another instrument.
5. **Usable balance:** reconcile current bank cash to the legal entity's ledger, restricted balances, liabilities, and subsequent activity.
6. **Coverage:** apply forward operating spend, hiring, collections, capital expenditure, refunds, and obligations to that accessible balance.

- Related fund AUM, founder wealth, historical investment gains, or target returns are not operating cash, recurring revenue, or a binding subsidy. Identify exactly which entity earns fees and can legally distribute proceeds.
- Model finite affiliate support by enforceable cap, duration, conditions, transfer timing, and downside availability. Remove discretionary top-ups in a downside case; do not assume investment returns arrive smoothly or preserve principal.
- Reconcile revenue by stream and entity from contract → performance/delivery → invoice → recognition → collection → credit/refund. Determine principal versus agent presentation before comparing gross revenue or margins.
- Separate bookings, cancellable orders, refundable deposits, deferred revenue, recognized revenue, receivables, and receipts. Forecast bands, letters of intent, nominal reservations, and pipeline do not become enforceable backlog.
- Separate external customers from affiliates, internal purchases, barter, grants, credits, pilots, and subsidized users. Analyze related-party terms and recurring customer willingness to pay independently.
- Build a monthly bridge with beginning cash, operating receipts, operating payments, capex, financing, transfers, and ending cash. Reconcile balance sheet, income statement, and cash flow timing rather than treating profit as liquidity.
- Track payroll, taxes, debt, leases, supplier purchase commitments, refunds, warranties, customer prepayments, litigation exposures, guarantees, and callable related-party loans. Avoid counting the same liability twice.
- Model receivable aging, subsequent receipts, disputes, inventory aging, supplier credit, processor settlement delays, and merchant reserves. Cash collected in advance may fund an undelivered obligation.

Use these formulas with consistent periods and cost classifications:

- `Net operating cash burn = operating cash payments − operating cash receipts`; show financing and capex separately, then include all relevant flows in forward cash needs.
- `Cash_t = Cash_(t−1) + receipts_t + usable committed financing_t − operating payments_t − capex_t − debt/tax/other cash obligations_t`; avoid duplicate items already included in operating payments.
- `Runway = first period unrestricted cash falls below the required operating liquidity floor`; cash divided by burn is only a rough steady-state approximation when burn is positive and stable.
- `Contribution = realized net revenue − avoidable delivery and servicing costs`; show gross margin and contribution separately and document treatment of support, commissions, and infrastructure.
- `Break-even revenue = fixed operating costs / contribution margin ratio`, only when that ratio is positive and costs share the same period. Negative unit contribution worsens cash consumption as volume grows.
- `CAC = attributable fully loaded acquisition costs / new external paying customers`; match costs, conversion lag, and customer cohorts rather than dividing this month's spend by unrelated wins.
- `Payback = CAC / monthly customer contribution` only for stable positive contribution; otherwise model cohort cash flows. Do not extrapolate LTV from immature retention or assume perpetual life.
- `Free-user subsidy = sum(active free users by usage band × cash delivery/support cost per band)`. Include abuse, cloud fallback, retries, storage, observability, and expensive tail users when applicable.
- `Cash conversion cycle = inventory days + receivable days − payable days`; inspect actual deposit and settlement timing when averages obscure financing needs.
- `Required spendable capital = annual uncovered cash need / assumed net spendable yield` is a sensitivity, not guaranteed funding or runway; stress losses, distributions, taxes, illiquidity, and depletion.

For AI or usage-based products, inspect per-successful-workflow costs and p50/p95/p99 usage, not only average model fees. Include failed requests, retries, output review, local/cloud split, model changes, and customer-specific limits.
For hardware, include procurement, setup labor, freight, duties, payment fees, discounts, channel share, expected returns, warranty, repairs, and inventory financing. Verify the exact SKU and fulfilled order before inferring margin.
For compute or marketplace credits, separate issued credits, spendable balances, withdrawable cash, realized payouts, demand fill rate, utilization, fraud, service quality, and counterparty obligations. Token or credit issuance is not cash income.
Build downside/base/upside scenarios around specific drivers: collections delay, hiring, price, usage, churn, margin, inventory, and funding availability. Show cash trough, financing need, capacity constraints, and dates; do not label them forecasts without a basis.

## Thirty diligence metrics: definitions and proof

Use the applicable metrics as an evidence register. Record value or unknown, period, denominator, entity, source, confidence reason, limitation, and decision consequence. Do not average them into a company score; mark nonapplicable metrics with reasons.

### Liquidity

| # | Metric and definition | Evidence and proof test |
|---|---|---|
| 1 | Unrestricted operating cash: cash the operating/employing entity can use now. | Current bank statements and reconciliations by entity; subtract restricted funds and reconcile subsequent movement. |
| 2 | Monthly net cash burn: operating payments less operating receipts. | Trailing cash bridges and forward forecast; exclude financing from operating inflows and explain seasonality. |
| 3 | Runway: time until the liquidity floor under a specified funded plan. | Monthly cash model, hiring plan, and available financing terms; stress delays and exclude uncommitted raises. |
| 4 | Related-party funding dependency: affiliate support as a share of cash inflows. | Intercompany ledgers, agreements, approvals, and transfers; identify cap, duration, callability, and correlated downside. |
| 5 | Debt and contingent cash obligations: scheduled and triggered claims on cash. | Debt, tax/payroll, lease, guarantee, refund, and commitment schedules; reconcile due dates to the forecast. |

### Revenue quality

| # | Metric and definition | Evidence and proof test |
|---|---|---|
| 6 | Recognized revenue and collections: earned revenue and separately received cash by stream. | Contracts, ledger, invoices, fulfillment, bank receipts, and credits; trace samples end to end. |
| 7 | Recurring revenue/ARR: annualized eligible contractual recurring revenue at the measurement date. | Contract and billing ledger; exclude setup, hardware, GMV, speculative renewals, and ambiguous price intervals. |
| 8 | Enforceable bookings/backlog: signed remaining obligations with stated cancellation terms. | Executed orders, delivery schedules, cancellation/refund rights, and deposits; exclude illustrative forecasts. |
| 9 | Revenue concentration: largest and top customer shares of revenue and collections. | Customer schedules and renewal dates; resolve affiliates and common ownership and stress a major loss. |
| 10 | Collection quality: receivable aging, disputes, bad debt, and collection timing. | AR aging, subsequent receipts, credit notes, and DSO calculation; distinguish growth effects from deterioration. |

### Product demand and customer value

| # | Metric and definition | Evidence and proof test |
|---|---|---|
| 11 | Paying customers: unique external purchasing organizations or explicitly chosen buyer unit. | Billing-linked customer ledger; remove tests, internal accounts, duplicate entities, and unpaid trials. |
| 12 | Activation and sustained usage: completion and repetition of a valuable workflow by cohort. | Event definitions and analytics reconciled across channels; exclude bots/employees and show eligible cohorts. |
| 13 | Paid pilot conversion: matured eligible pilots converting to ordinary paid contracts. | Pilot register, start/end dates, outcomes, contracts, and receipts; show counts and pending/censored pilots. |
| 14 | Retention/GRR/NRR: same-cohort customer and recurring-revenue persistence. | Cohort billing: GRR excludes expansion; NRR includes it; both exclude new customers from the numerator. |
| 15 | Customer ROI: verified net benefit relative to total adoption and ongoing cost. | Baseline and post-adoption workflow measurements plus authorized references; include review and correction effort. |

### Sales and distribution

| # | Metric and definition | Evidence and proof test |
|---|---|---|
| 16 | Sales cycle and win rate: time and outcome of consistently qualified opportunities. | Dated CRM stages cross-checked to contracts/collections; report losses, segments, and still-open cohorts. |
| 17 | CAC and contribution payback: acquisition investment and time to recover it. | Fully loaded spend including founder labor and channel fees; match acquired cohorts and realized contribution. |
| 18 | Channel repeatability: repeated retained paying wins per channel without exceptional intervention. | Attribution, partner terms, cohort results, and account effort; distinguish access or credits from contracted demand. |

### Unit economics and working capital

| # | Metric and definition | Evidence and proof test |
|---|---|---|
| 19 | Software contribution: revenue less hosting, inference, direct delivery, and servicing costs. | Per-tenant/workflow metering, invoices, and support allocation; inspect usage tails and marginal cost. |
| 20 | Hardware contribution per fulfilled order: net proceeds less full avoidable delivery costs. | Exact SKU procurement, shipment, fees, labor, channel, returns, and warranty records; exclude unfulfilled reservations. |
| 21 | Free-user subsidy: cash cost of free cohorts and promised entitlements. | Active usage distribution, vendor bills, support, and execution split; reconcile source and duration of subsidy. |
| 22 | Working capital/cash conversion: cash tied in inventory and collections net of supplier terms. | Inventory aging, AR/AP, deposits, settlements, and reserves; identify peak funding needs before scaling. |
| 23 | Returns, warranty, and chargeback loss: cash loss and labor per mature fulfilled cohort. | Refund/repair logs, merchant settlements, reserve policy, and warranty agreements; account for reporting lag. |

### Governance and ownership

| # | Metric and definition | Evidence and proof test |
|---|---|---|
| 24 | Entity and IP chain: documented ownership of business, contracts, and product rights. | Dated structure, registry records, cap tables, assignments, and reorganizations; resolve names and jurisdictions. |
| 25 | Fund/affiliate cash access: enforceable operating-company entitlement to transferable money. | Definitive agreements, legal restrictions, approvals, and bank transfers; separate NAV, fees, gains, and usable cash. |
| 26 | Equity economics: issuer, fully diluted ownership, senior claims, and exercise terms. | Charter, cap table, convertibles, preferences, valuation, grant, vesting, strike, and exercise window; model dilution/waterfall. |
| 27 | Key-person concentration: dependence in funding, decisions, relationships, and operational control. | Delegations, board oversight, backup ownership, contracts, and succession arrangements; test absence of the key person. |

### Delivery and execution

| # | Metric and definition | Evidence and proof test |
|---|---|---|
| 28 | Production reliability and recovery: supported workflow success and restoration performance. | Customer acceptance, SLO measurements, incident records, restore exercises, and remediation; separate demos from service. |
| 29 | Buyer eligibility: requirements met for the chosen customer's deployment and procurement. | Current attestations with scope, security/legal review, integration requirements, and actual buyer acceptance. |
| 30 | Roadmap capacity and delivery cost: funded critical path to a sellable, maintainable outcome. | Costed plan, owners, dependencies, support load, explicit deferrals, and acceptance criteria; reconcile staffing to cash. |

## Decision gates and targeted data-room requests

Set gates before seeing results, tailored to the decision and reversible exposure. Do not invent universal retention, runway, conversion, or margin thresholds; connect thresholds to the required horizon, business model, and user constraints.

| Decision | Gate to resolve | Minimum useful evidence |
|---|---|---|
| Joining | Employer, role, dependable pay, mission, and resources fit the intended employment horizon. | Signed employing-entity terms, current cash/runway evidence, funded hiring plan, obligations, and explicit support commitment where needed. |
| Employee equity | The grant owns an understood claim with clear economic and exercise terms. | Issuer, grant documents, fully diluted cap table, preferences/convertibles, vesting, strike, dilution, and relevant valuation basis. |
| Investing | Ownership, rights, cash access, and economics support the proposed instrument and downside. | Entity/IP chain, financial statements and cash bridges, financing terms, debt/contingencies, customer cohorts, and unit economics. |
| Vendor selection | The service can meet the required workflow, continuity, support, and exit needs. | Scoped trial/acceptance, security and service evidence, contracting entity, support obligations, data portability, termination, and continuity arrangements. |
| Scaling a channel | Paid demand repeats with acceptable marginal acquisition cost and contribution. | Channel cohorts, funnel timing, receipts, retention, sales effort, partner rights, and capacity constraints. |
| Scaling free or hardware offers | Incremental growth is funded through delivery, support, and downside obligations. | Usage-tail costs or fulfilled-order economics, inventory/settlement timing, returns, subsidy limits, and cash-trough scenario. |

- Request documents in priority order tied to the unresolved gate, not as a generic exhaustive checklist. Ask for dated reconciliations and minimally necessary scoped evidence; do not request fund books for a vendor decision unless the dependency matters.
- A standard financial packet may include entity-level statements, current bank reconciliation, recent monthly cash bridges, a short-term cash forecast, forward hiring/capital plan, and executed financing/support agreements.
- A commercial packet may include billing-linked cohorts, signed contracts, invoice/receipt samples, deferred revenue and AR schedules, pilot outcomes, CRM stages, cost allocations, and authorized customer references.
- Proceed with bounded confidence when material identity/funding questions reconcile, the relevant plan is funded, and the buyer outcome has evidence. Identify which remaining risks are acceptable and why.
- A research-stage role or business may be viable with an explicit funded mandate despite unproven paid demand. Describe that operating model honestly; subsidy does not establish product-market fit or justify a recurring-revenue valuation.
- Pause the specific joining/investing/vendor commitment when a material gate remains unresolved after direct diligence. State the missing proof and how it could change the decision; do not substitute accusations for missing information.
- Revisit the product thesis when bounded tests repeatedly fail on net customer benefit, willingness to pay, reliable adoption, or positive contribution. Specify a narrower offer or alternative segment to test and the evidence that would reverse the recommendation.

Deliver the decision, strongest supporting evidence, strongest countercase, actuals-versus-assumptions boundary, key sensitivities, and prioritized proof requests. Numerical outputs must be reproducible from disclosed inputs; unavailable actuals remain unknown.
