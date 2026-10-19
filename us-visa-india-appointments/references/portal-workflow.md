# Portal workflow and evidence

Use the installed browser tool's current documentation and existing authorized
profile/tab. Ground semantic locators in current UI. Inspect the resulting page
after an action before deciding what to do next.

## Fresh inventory and readiness

The observed staged OFC flow is:

1. Location change clears calendar/time selection and requests available days.
2. Date selection requests time rows and associated server state.
3. Time radio stores the selected row and enables Submit; it reserves nothing.
4. Ordinary Submit runs the booking handler. Only server acceptance advances
   the staged booking.

This is observed client behavior, not a supported public API contract. Recheck
the live UI when it changes. Shared city/date/row/token state is a reason to
serialize operations; concurrent handlers could mix selections. Direct handler
calls would still require server acceptance and are not an approved shortcut.

- Wait for group members, selected location, and loading completion.
  A previous city's message is not a new response.
- An initially empty pair of months may have eligible dates later. Inspect
  current selectable dates through visible controls and record the months
  inspected. Do not infer global absence from a narrow scan.
- A selectable date is only a candidate. If rows are initially absent, allow
  one bounded passive wait (roughly 15–20 seconds when appropriate) and inspect
  or scroll the time section before concluding no times. Do not add that wait
  when actual rows are already ready.
- Require a current eligible row, matching checked radio, and enabled Submit.
  Enabled Submit can persist on a page with no time rows.
- After failed Submit, retained rows/counts are cached. A permitted retry keeps
  the original inventory-response timestamp; it is not new inventory.
- Selecting an already selected dropdown value may not request anything.
  A deliberately authorized fresh retry may use a visible blank option to
  clear stale selection, then request the desired location once. Count the
  actual location request. Do not toggle dropdowns as keepalive.

A tool wait timeout is not a portal error or no-slots response. Use one bounded
passive inspection rather than resending a request before its result is known.

## Authentication and CAPTCHA

Count each new normal sign-in flow once, including automatic SSO redirects,
failures, and flows without credential entry. Record a stable flow ID when
first observed. Credentials/security completion for that same flow is not
another flow. A Cloudflare page alone is not a credential login.

Apply a rolling flow budget only when current task policy explicitly configures
one. Label a self-imposed ceiling as local policy, not a verified portal
allowance. A general warning that attempts are limited establishes no numeric
allowance. If the user revises a local ceiling, update active rules and scheduled
instructions; preserve old counts and exceptions as history, not current holds.
A current explicit exception is scoped to that action/run; completing its
admitted flow does not authorize another flow. Without a numeric budget, follow
the authorized bounded sign-in policy; do not create a login retry loop.

For an authorized login:

- Verify the official portal's expected identity-provider destination reached
  through normal navigation. Record an origin only, never full auth URLs.
- Read the configured private credential source only when needed. Do not print
  its object, username, input values, answers, or authentication parameters.
- Use the current normal form; an aged callback/form is not a reliable new
  login starting point.
- Submit username/password at most once per bounded run; stop on rejection.
  Match visible security questions privately to saved answers and continue
  within the same flow.
- Inspect headings, button state, and field-filled booleans without exposing
  values. Even a read-only username field can disclose the account identifier.
- Verify normal application Home and subsequent server-backed interactions.
  Cached applicant names do not establish session validity.
- Clear credentials and derived answer mappings after the flow. Do not
  screenshot filled authentication forms.

For Cloudflare:

- A DOM/AX snapshot may show security verification while a screenshot reveals
  the interactive checkbox. Inspect without bypassing it.
- Obtain action-time approval for a new interactive challenge under the browser
  tool's policy. Save the action, hostname, tab, evidence, observed/recorded
  times, and available challenge identifier.
- Preserve the page and skip later browser work while the decision is pending.
  If the user is away, leave one concise notification; do not repeat questions.
- After current approval, inspect the visible control. An untouched widget can
  renew its identifier; record that renewal. Approval covers the specified
  current action/destination, not future challenges.
- Click once, allow completion, then inspect the actual post-challenge page.
  A separate callback challenge needs a new decision. Cloudflare success alone
  does not prove visa authentication succeeded.

## Errors and partial actions

| Visible outcome | Meaning and response |
| --- | --- |
| No Slots Available | Location-specific result after the current request completes. |
| PSE0501 | Calendar retrieval failed: follow the task's continuation/backoff policy. An authorized all-location pass can continue to remaining locations once. Not proof of no slots, ban, or expiry. |
| Generic processing-too-many-requests message | Booking rejected/busy; cause and HTTP status remain unknown from this alone. |
| PSE0504 | Booking failed; no specific HTTP status or account/authentication cause is established. |
| Selected time no longer available | Stop retrying that stale row; require a valid newly offered alternative. |
| Actual sign-in/expiry redirect | Record direct evidence and elapsed times; apply the flow budget. |
| Explicit access restriction or waiting period | Stop and honor site/configured cooldown. |
| Tool timeout or detached operation | Inspect actual UI and the local attempt record before deciding what remains. |

Busy/PSE0504 authorizes no unlimited retry loop and proves no account-specific
ban by itself. Follow current bounded retry authority. Read/dismiss a known
ordinary error alert; do not treat an unknown confirmation or binding agreement
as an alert. An error's instruction to contact support does not authorize
sending a message.

When the user authorizes completing all locations despite ordinary calendar
errors, record and dismiss each known error and continue sequentially without
repeating the failed location. Evaluate configured between-pass technical
backoff after that bounded pass finishes. Fresh confirmation holds and actual
access restrictions still stop work.

Record submission start before clicking: the click may finish even if the next
snapshot fails. Fills can also finish before a detached-operation error.
Inspect filled-state booleans, buttons, current stage, and the local attempt
record before retrying. Never duplicate a booking or credential submission
solely to recover tool output.

Use documented recovery in the selected browser. A stale tab/helper does not
prove browser disconnection. Do not switch profiles or unrelated controllers.

## Session observations

Timestamp authentication start/completion, credentials, successful calendar/time
responses, ordinary navigation, Cloudflare, and actual sign-in redirects
separately.

When sign-in becomes required, record time since authentication and since the
last successful server-backed interaction, plus idle/active and challenge-hold
periods. Do not infer fixed/sliding expiry from framework defaults, cached
names, a single interval, or a successful login after technical errors. Compare
ordinary comparable sessions; do not send keepalive traffic or provoke a
restriction to test a theory.
