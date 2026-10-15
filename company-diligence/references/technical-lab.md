# Technical diligence and failure lab

Read this when evaluating implementation, reliability, security, embedded systems, hardware claims, or the customer experience under failure.
The unit of evidence is a pinned implementation exercised at a named boundary, or a clearly labeled source-only argument.

## Map the product to executable code

Create a compact map before choosing experiments:

| Product promise or customer task | Repository and revision | Entry point and runtime path | Dependencies and authority | Observable outcome | Mapping confidence |
| --- | --- | --- | --- | --- | --- |
| A concrete supported workflow | Full commit SHA | Route, worker, native adapter, or component | Identity, storage, provider, device | Durable result and user-visible state | Verified, supported, or unresolved |

Trace imports, caller wiring, feature flags, platform branches, deployment manifests, and persistence adapters.
Distinguish active code, examples, generated output, abandoned prototypes, vendored code, and research branches.
Check repository ownership and whether a public repository actually corresponds to the current product.
A website claim, merged PR, release tag, and deployed revision are different evidence; record missing links.
Prioritize paths that control customer value, authority, resource cost, data durability, or recovery.

## Architecture, performance, and customer workflow

Trace one valuable task end to end: onboarding → input/consent → processing → durable result → repeated use → export/deletion. Identify the actual buyer, operator, approver and recipient rather than assuming they are one person.
Evaluate time to first useful outcome, mandatory account/cloud steps, empty states, discoverability, permission comprehension, cross-device continuity, accessibility and recoverable errors. Record observed friction separately from assumed abandonment; a single expert walkthrough is not user research.
Check keyboard/focus behavior and relevant assistive semantics; test latency and failure messages against actual operation state. Propose user studies for comprehension or willingness-to-adopt claims that a local walkthrough cannot establish.
Map service/data boundaries, consistency guarantees, schema migrations, integration contracts, upgrade compatibility, observability, backup/restore and rollback. Distinguish intentional simplicity from architecture that blocks the next proven customer requirement.
Inspect build/release provenance, dependency and license obligations, update ownership and known upstream fixes. Counts of files, tests or dependencies do not measure maintainability; sample the risk-bearing changes and their acceptance evidence.
Measure performance with representative synthetic workloads, a stated baseline, warm/cold runs, resource limits, latency distributions, throughput and error rates. Separate host/toolchain contention from product bottlenecks; a laptop microbenchmark is not a production capacity forecast.
Relate bottlenecks to a declared service objective and useful completed work, including review and retry cost. Make proposed scale tests bounded; preserve workload parameters and repetitions so results can be challenged.

## Freeze a reproducible baseline

Record clone origin, full commit SHA, submodules, acquisition time, local changes, and the file locations inspected.
Use immutable source permalinks for findings; retain the exact source snapshot used by the harness.
Preserve lockfiles, resolved dependency versions, Dockerfile, image ID/digest, host architecture, runtime versions, and relevant resource limits.
Separate requested dependency versions from resolved versions; a later registry rebuild may not be identical.
Record the command, environment variable names, synthetic configuration, exit status, stdout/stderr, and elapsed time for each run.
Do not retain secrets or customer content in logs; use deliberately synthetic identifiers and fixtures.
Keep upstream snapshots unchanged; place harnesses, patches, caches, and evidence in task-owned directories.

## Bound the local execution environment

Inspect installation and startup scripts before executing unfamiliar code.
Separate dependency acquisition from test execution: allow only necessary build-time access, then run failure experiments without external network access.
Use Docker with a read-only source mount, a read-only root filesystem where compatible, and a dedicated writable output directory or temporary filesystem.
Drop capabilities, enable no-new-privileges, bound memory/CPU/processes, and give every run an explicit timeout.
Do not mount host credentials, the Docker socket, unrelated home directories, or real device interfaces into the test container.
Use synthetic services on an isolated internal network when multiple containers are necessary; publish previews only to loopback.
Name task-owned containers and volumes so teardown cannot affect unrelated workloads.
Record necessary deviations, such as a writable compiler cache, and keep them narrow.
Avoid real sign-ins, provider provisioning, billing, outbound messages, or production writes unless independently authorized by the task.
Stop on unexpected external effects, unbounded resource growth, or a scope/approval rejection; narrow the work rather than rerouting a blocked action.
If Docker is unavailable, use a suitable bounded isolation alternative for tests that support it. Mark container-dependent tests as unexecuted and preserve their harness; never label source review as an executed lab.

## Design an experiment that can disprove the concern

1. State the customer contract and a falsifiable expectation before writing a test.
2. Exercise actual repository modules at the narrowest useful seam; do not merely reimplement the suspected algorithm in a test.
3. Prove the normal path works with a positive control using the same harness and dependencies.
4. Inject one named failure, ordering change, or boundary condition; bound retries and concurrency.
5. Observe both the returned value and durable state, provider calls, outstanding resources, and user-visible status.
6. Restore the dependency and check recovery, replay, cleanup, and duplicate handling.
7. Preserve the raw receipt and explain which real-world boundaries the harness replaced.

A mock must model the relevant contract, including partial completion and ambiguous acknowledgments; a simplistic mock can invent a failure.
Use selected existing tests as baseline controls, but verify that they exercise the relevant implementation and record the subset run.
An observation test can pass because it successfully demonstrates a defect; distinguish assertion outcome from product outcome.
Distinguish a compile failure in the source from an unsupported host toolchain, missing credentials, or unavailable proprietary dependency.
Label a proposed experiment as proposed until its command has run and its evidence has been inspected.

## Choose failure cases from the product contract

| Boundary | Controlled scenario | Evidence to inspect |
| --- | --- | --- |
| Dependency outage | Timeout, unavailable service, malformed or partial response | Typed failure, deadline, useful UI state, preserved last good data |
| Retry and replay | Lost acknowledgment after success; duplicate request | Stable idempotency key, deduplicated effects, bounded backoff and cost |
| Concurrency | Two ordinary updates or decisions interleaved | Transaction/lease/CAS behavior, final state, conflict handling |
| Lifecycle | Disconnect, cancel, crash, restart, or shutdown mid-task | Durable job identity, ownership, recoverable intermediate states |
| Provisioning | Provider succeeds, persistence fails | Reconciliation record, orphan detection, retryable cleanup |
| Cleanup | Delete/release times out or fails | Pending cleanup remains visible; completion is not falsely reported |
| Recovery | Stale record, alternate region, expired lease | Recovery targets the correct resource and cannot duplicate work |
| Cost | Repeated retries, idle allocation, abandoned session | Call/allocation counts and duration; priced scenarios with assumptions |
| Consent and account lifecycle | Ordinary revoke, expiry, logout, deletion, or switch | Current authority, cache invalidation, durable state and truthful UX |
| Offline mode | Clean startup, real service queries, reconnect | Supported SQL/API behavior, queue durability, conflict resolution |
| Storage and capacity | Full store, write failure, boundary payload size | No silent loss, actionable limit, preservation of prior data |
| UX and accessibility | Partial success, slow operation, retry/back navigation | Correct status language, focus/keyboard behavior, continuity and recovery |

Use this as a selection menu, not a requirement to execute every case.
For cost, report measured local counts separately from modeled provider spend; mocks cannot demonstrate an actual bill or leak.
For offline claims, test real callers and documented startup paths; a basic database test does not establish service parity.
For consent, distinguish UI preference, persisted grant, token authority, cache state, and third-party data already delivered.
Keep ordinary resilience tests separate from adversarial security execution; permission for one does not establish permission for the other.

## Defensive security review

Trace entry points, principals, trust boundaries, owner/tenant checks, token validation, scopes, expiry, revocation, key handling, exports, logs, and persistence semantics.
Inspect canonical contracts, middleware, callers, and adjacent tests before treating a suspicious helper as reachable.
Record existing safeguards and counterexamples, including checks that occur before or after the suspicious code.
Separate missing documentation, insecure defaults, reachable source defects, and deployment-dependent hypotheses.
For each concern, state required preconditions, affected data or authority, supporting source lines, and the nearest protective controls.
Use source-only review when execution is outside the authorized scope; do not imply a working exploit or runtime confirmation.
Check known issues and newer fixes before calling a concern new; preserve historical lessons separately from active findings.
Do not publish credentials or weaponized payloads as diligence evidence; provide a defensive regression expectation and remediation direction.
Severity must follow plausible impact and reachable prerequisites, not scary terminology or an unproven production assumption.

## Software, embedded, and hardware boundaries

Maintain a qualification matrix for source build, packaged app, native integration, physical device, and deployed service.
For native software, distinguish compilation, linking, signed installation, startup, permissions, driver availability, and real runner wiring.
For local inference or accelerators, verify model identity, precision, context, batch size, warmup, concurrency, and the actual compute backend before reporting performance.
Closing a transport or process handle does not establish that the inference engine, memory, or accelerator allocation was released.
Container tests cannot qualify battery life, thermals, radio behavior, sensors, acoustics, enclosure durability, or manufacturing consistency.
Use real supported hardware for power-cycle recovery, firmware update/rollback, boot trust, background contention, connectivity loss, and long-duration behavior.
Mark hardware work as unverified when no device is available; propose acceptance gates and required equipment instead of inventing measurements.
Tie hardware launch plans to sourcing, lead times, yield, repairability, certification needs, support burden, and per-unit economics with explicit evidence gaps.
Where relevant, inspect BOM substitutions, supplier concentration, minimum orders, end-of-life dependencies, firmware signing/update ownership and factory provisioning. Identify applicable physical qualification questions; software evidence cannot certify radio, electrical or environmental compliance.

## Convert observations into decisions

For each finding, record ID, affected promise, source location/revision when available, impact, evidence grade and scope. A reproduction additionally needs trigger, expected and observed behavior, run receipt and control result.
Use “not executed,” “unknown” or “not applicable” for unavailable runtime or platform fields in source-only findings; never manufacture a receipt or control. Add reproducibility command for executed tests, harness substitutions, production-reachability status, existing issue/fix status, proposed owner, acceptance test, and residual uncertainty.
Use distinct labels: executed reproduction; source-supported concern; public claim; inference; unknown; proposed test.
An executed local defect establishes behavior in that harness, not current production exposure or customer incidence.
Report strengths and failed hypotheses alongside defects; retire claims contradicted by controls or newer evidence.
Prioritize by customer harm, frequency assumptions, authority/data risk, operational cost, and effort to verify or repair.
Make release gates concrete: which outcome must hold, on which revision and platform, with whose acceptance and what recovery evidence.
