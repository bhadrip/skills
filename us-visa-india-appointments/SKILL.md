---
name: us-visa-india-appointments
description: Check, monitor, and book authorized U.S. visa OFC/VAC and consular appointments in India through the official scheduling portal. Use for availability searches, scheduled checks, interrupted-session recovery, or completing a qualifying pair; keep applicant configuration and evidence in private task state.
---

# U.S. visa appointments in India

Use https://www.usvisascheduling.com and the user's existing authorized browser
profile. Optimize the ordinary staged UI workflow: a selected row or submitted
request is not a confirmed appointment.

This skill contains reusable procedure. It grants no booking, login, payment,
recurring-task, or CAPTCHA authority by itself.

## Establish the task contract

Read current user instructions and private saved state before browser work.
Reuse existing configuration; ask only for missing decisions that prevent
progress. Establish:

- Check-only versus complete-pair booking authority, applicant/category scope,
  acceptable locations in preference order, and cross-city permission.
- The date rule for **both** appointments: explicit window or minimum date,
  inclusive boundaries, date-basis time zone, and any upper bound.
- Current official appointment-ordering/gap requirements, relevant holidays and
  portal restrictions, and any stricter user travel buffer. Verify official
  instructions when these are not already established.
- Existing receipt/payment authority and treatment of unexpected appointments.
- User-requested schedule, bounded request/submission limits, spacing,
  technical-error backoff, and any explicitly configured local login-flow budget.

Do not import another task's dates, city preference, retry exception, schedule,
login ceiling, credential path, or booking consent. A named-city manual request
does not silently narrow future monitoring.

For a relative date rule, compute today in the configured date-basis time zone
and add calendar days. Compare that cutoff with each **India-local appointment
date**, inclusively. Recompute at every check and immediately before booking.
Calendar days are not a rolling number of elapsed hours.

## Resume from private state

Read [state and scheduling](references/state-and-scheduling.md) when creating,
resuming, or updating monitoring state. Evaluate holds before browser work:

- Specific pending CAPTCHA/agreement decision: preserve the tab; wait without
  touching the challenge or repeating the same question.
- Timed restriction/backoff: skip browser work until expiry. Keep requested
  monitoring available; do not add catch-up passes for skipped windows.
- Active bounded run or serviced target: resume or deduplicate it.
- Confirmed qualifying complete pair or user stop: end monitoring.

Use current explicit instructions over historical consumed approvals. Permission
for one current action or batch does not become standing authority.
Do not invent a numeric login allowance or preserve a superseded local ceiling.
Record observed counts separately from current policy and unknown portal limits.

## Perform one bounded pass

Read [the portal workflow](references/portal-workflow.md) for readiness,
authentication, errors, and interrupted-action recovery.

1. Reuse the existing session. Inspect actual application/appointment state
   through normal UI; preserve unexpected existing appointments.
2. Wait for the applicant group to finish loading.
3. Request each configured location once, sequentially. Let its response finish
   before changing shared city/date/time state. Add a fixed city-to-city pause
   only when the task policy requires one.
4. When a calendar appears, inspect visible month/year controls from the current
   cutoff onward. An empty initial month does not prove no eligible dates.
   Do not invent a fixed upper search bound.
5. Select a candidate date once. Require an actual current eligible time row,
   its matching checked radio, and enabled Submit. If rows are ready, proceed;
   otherwise allow one bounded passive wait and inspect/scroll the time section.
   Do not repeatedly reselect the date.
6. Submit within current authority and the run cap. Keep submissions sequential,
   spaced by the configured policy, and inspect each finished result before
   another submission.
7. If the staged flow advances, prioritize the authorized qualifying pair.
   Recheck dates, locations, official/user gaps, and any final agreement.

Supported JavaScript may orchestrate normal semantic controls and read visible
DOM readiness. Let ordinary handlers manage tokens. Do not call booking
endpoints/page functions directly, replay requests/tokens, force-enable
controls, modify cookies/session state, create alternate profiles, or run
parallel booking flows.

If a candidate city was left during the pass, restore it once through the normal
dropdown, count the extra request, and require newly returned dates/time rows.
This method is not a portal-limit exemption.

## Interpret outcomes and finish

- Explicit no-slots response: record the location and response time.
- PSE0501: end the calendar pass and follow configured technical backoff. It
  proves neither no slots nor an expired login or account ban.
- Generic busy / PSE0504: record the exact visible result and unknown cause.
  Retry only when current task policy permits bounded retries.
- Selected time no longer available: stop retrying that stale row.
- New CAPTCHA or covered agreement: save a specific pending decision and
  preserve the page. Earlier completed approvals do not apply.
- Explicit account/access restriction or site-required wait: stop, preserve the
  exact message, and honor the site period plus any stricter configured
  cooldown. Do not try alternate routes.

An error response does not refresh retained time rows. Enabled Submit alone is
insufficient; a visible availability count is not a reservation.
An explicitly permitted retry may reuse the retained selection within that
same bounded batch if it has not been declared unavailable. A later batch
requires fresh inventory; the retained row grants no new retry authority.

Only completed confirmation showing **both** qualifying appointments counts as
success. Verify India-local dates, times, locations, and required spacing; save
redacted proof, report the pair, and stop the monitor. Do not introduce a fee,
cancel an unexpected appointment, or change identity/category without separate
authority.

After every run, save actual actions, results, timestamps, holds, counters, and
the exact resume point. Distinguish observations from hypotheses and unknowns.
Keep all live state and evidence outside the skill repository.
