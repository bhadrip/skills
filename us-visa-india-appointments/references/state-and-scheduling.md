# Private state and scheduling

Keep configuration, mutable state, and evidence in a user-selected private
location outside the skill checkout. No real applicant data, credentials,
profile paths, screenshots, receipts, appointment dates, or session histories
belong in the published package. Do not copy live state to create an example.

Keep credentials separate. Use an approved secret store, or restrict a local
credential file if the user chooses one. Read it only for an authorized login.
Redact identifiers, government IDs, auth parameters, and security answers from
evidence. Avoid private details in filenames.

## State contract

Adapt to existing schemas rather than erasing/migrating evidence.

| Area | Meaning |
| --- | --- |
| Task policy | Booking/check scope; locations; cross-city permission; date basis/window; official/user gaps; payment authority. |
| Schedule | Requested targets/time zone, limits, spacing, and backoff. A target minute is not proof of a portal release time. |
| Active run | Stable ID, original target, actual active-work intervals, requests/submissions started and completed, cap, resume point. |
| Pending decision | Specific action, status, hostname, tab/evidence reference, observation time, and approval consumption. |
| Authentication | Flow events; credential submissions separately; verified completion; optional explicit local rolling budget; scoped exceptions. |
| Holds | Cause/message, start/expiry, source (site versus local), and whether browser work is prohibited. |
| Inventory | Location/date/time and original response timestamp; current versus cached/historical. |
| Booking | Selected versus reserved/confirmed stage; both final appointments and proof only after confirmation. |
| Observations | Direct navigation, responses, errors, challenges, and sign-in evidence; label hypotheses/unknowns. |
| Run history | Actual actions and outcomes, including zero-site-work skipped/deduplicated runs. |

Use aware UTC observation timestamps. Preserve appointment dates/times as India
local, separately from the user's notice-rule time zone. Write atomically with
private permissions and retain history. A selected row is not a confirmation.

## Scheduling and deduplication

Create recurring work only when requested. Update the matching automation
rather than duplicating it. Point it to private canonical state, read first.

- A late run can make one bounded pass if holds/budget permit; do not compensate
  for missed windows with extra passes.
- A pending decision blocks browser work, including challenge inspection.
  Skips increment neither calendar-error nor authentication counters.
- Evaluate timed holds against the current clock and mark them expired when
  appropriate. Do not let an old boolean block indefinitely.
- Resume ordinary cadence after backoff, without catch-up passes.
- Active work spanning a target blocks a duplicate run. Record overlap only
  after it actually occurs. Waiting for human approval is not continuous
  active work.
- After approval, resume the original interrupted run. Record its actual
  resumed interval and one fresh pass, without pre-servicing future targets.
- A manual city request or scoped exception changes that request/action only
  unless the user explicitly changes standing scope.

Historical consecutive errors and current timed backoff are distinct. A
successful server-backed calendar/time/no-slots response resets the calendar
error streak. Cloudflare alone neither increments it nor starts backoff.
Separate calendar, booking, and authentication errors.

## Limits and evidence

Keep three different claims separate: a documented portal restriction, an
observed count, and a local pacing or admission rule. Never turn the largest
observed count into a guaranteed allowance or an upper limit. Successful logins
beyond a proposed threshold contradict treating that threshold as universal;
they do not establish the portal's reset window, risk policy, or future behavior.

For a rolling-window observation, use precisely timestamped events and disclose
uncertain events excluded from the calculation. Count successful completions,
credential submissions, and sign-in flows separately. Callback failures are not
proof of credential rejection or a numeric account limit. Generic booking busy
responses alone do not identify whether account, session, IP, or backend load
caused them. Do not provoke a restriction to measure a ceiling.

When the user revises a local limit, update canonical policy, active hold fields,
and the recurring prompt consistently. Keep prior policy in history. A removed
numeric gate must not continue blocking runs through a stale eligibility date.

## Offline date/budget helper

[appointment_math.py](../scripts/appointment_math.py) uses only Python's standard
library. It makes no browser requests, reads no credentials, performs no
booking, and does not mutate state.

~~~sh
python3 scripts/appointment_math.py cutoff \
  --timezone "$DATE_BASIS_TIMEZONE" --days "$NOTICE_CALENDAR_DAYS"

python3 scripts/appointment_math.py auth-budget \
  --state "$PRIVATE_STATE_FILE" --ceiling "$FLOW_CEILING" \
  --window-hours "$ACCOUNTING_WINDOW_HOURS"
~~~

Run from the skill folder or resolve its script path. Optional --at accepts an
aware ISO timestamp for deterministic offline checks.

For budget calculation, the file can be an array of flow records or a state
object with an authentication.flow_events array. Each flow has id and
counted_at_utc. Keep its ID/original counting time when security or credentials
complete. Failed/SSO flows count; credential-only or Cloudflare-only
observations do not belong in that array.

The helper deduplicates identical IDs/timestamps and rejects conflicting,
naive, or future timestamps without printing payload values or event IDs.

With n events still in the window and ceiling L, admit a new flow only when
n is less than L. If over/at budget, eligibility begins when the chronological
event at zero-based index n - L expires. The oldest alone is insufficient after
an overrun. Recalculate after every new flow.

This is configured local accounting, not an official numeric allowance.
Completion of an admitted flow is not another new flow.

## Offline validation

~~~sh
python3 -m unittest discover -s scripts -p 'test_*.py'
~~~

Tests use synthetic dates/IDs only. Also review behavior: holds cause zero site
work; a sign-in flow is counted once; cached rows do not establish fresh
inventory or authorize a new batch; retries need current scoped authority;
success requires both confirmed qualifying appointments.
