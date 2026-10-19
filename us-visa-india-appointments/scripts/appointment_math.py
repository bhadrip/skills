#!/usr/bin/env python3
"""Offline calendar-date and caller-configured authentication-budget math."""

import argparse
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


def utc_timestamp(value):
    if not isinstance(value, str):
        raise ValueError("timestamp must be an aware ISO string")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        raise ValueError("invalid ISO timestamp") from None
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError("timestamp must include a timezone offset")
    return parsed.astimezone(timezone.utc)


def aware_utc(now):
    if now.tzinfo is None or now.utcoffset() is None:
        raise ValueError("current time must include a timezone offset")
    return now.astimezone(timezone.utc)


def calendar_cutoff(now, timezone_name, days):
    now = aware_utc(now)
    if isinstance(days, bool) or not isinstance(days, int) or days < 0:
        raise ValueError("calendar-day offset must be a nonnegative integer")
    try:
        basis = now.astimezone(ZoneInfo(timezone_name)).date()
    except (ZoneInfoNotFoundError, ValueError, TypeError):
        raise ValueError("unknown date-basis timezone") from None
    return {
        "basis_date": basis.isoformat(),
        "date_basis_timezone": timezone_name,
        "calendar_days": days,
        "earliest_appointment_date_inclusive": (basis + timedelta(days=days)).isoformat(),
    }


def flow_events(payload):
    if isinstance(payload, dict):
        auth = payload.get("authentication")
        payload = auth.get("flow_events") if isinstance(auth, dict) else None
    if not isinstance(payload, list):
        raise ValueError("expected a flow-event array or authentication.flow_events")
    result = {}
    for event in payload:
        if not isinstance(event, dict):
            raise ValueError("each flow event must be an object")
        event_id = event.get("id")
        if not isinstance(event_id, str) or not event_id.strip():
            raise ValueError("each flow event needs a nonempty id")
        counted = utc_timestamp(event.get("counted_at_utc"))
        if event_id in result and result[event_id] != counted:
            raise ValueError("a flow id has conflicting counting timestamps")
        result[event_id] = counted
    return list(result.values())


def authentication_budget(payload, now, ceiling, window_hours):
    now = aware_utc(now)
    if isinstance(ceiling, bool) or not isinstance(ceiling, int) or ceiling < 1:
        raise ValueError("flow ceiling must be a positive integer")
    if isinstance(window_hours, bool) or not isinstance(window_hours, int) or window_hours < 1:
        raise ValueError("window hours must be a positive integer")
    window = timedelta(hours=window_hours)
    events = flow_events(payload)
    if any(event > now for event in events):
        raise ValueError("future flow timestamps require clock/state review")
    recent = sorted(event for event in events if now - window < event <= now)
    count = len(recent)
    next_time = recent[count - ceiling] + window if count >= ceiling else None
    return {
        "basis": "caller_configured_local_budget",
        "window_hours": window_hours,
        "flow_ceiling": ceiling,
        "rolling_flow_count": count,
        "new_flow_allowed": count < ceiling,
        "remaining_new_flows": max(0, ceiling - count),
        "next_new_flow_at_utc": next_time.isoformat().replace("+00:00", "Z")
        if next_time else None,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    cutoff = commands.add_parser("cutoff", help="Add calendar days in a chosen timezone")
    cutoff.add_argument("--timezone", required=True)
    cutoff.add_argument("--days", required=True, type=int)
    cutoff.add_argument("--at", help="Aware ISO current time; defaults to now")
    budget = commands.add_parser("auth-budget", help="Review a configured local flow budget")
    budget.add_argument("--state", required=True, type=Path)
    budget.add_argument("--ceiling", required=True, type=int)
    budget.add_argument("--window-hours", required=True, type=int)
    budget.add_argument("--at", help="Aware ISO current time; defaults to now")
    args = parser.parse_args(argv)
    try:
        now = utc_timestamp(args.at) if args.at else datetime.now(timezone.utc)
        if args.command == "cutoff":
            result = calendar_cutoff(now, args.timezone, args.days)
        else:
            try:
                payload = json.loads(args.state.read_text(encoding="utf-8"))
            except (OSError, UnicodeError, json.JSONDecodeError):
                raise ValueError("unable to read valid JSON state") from None
            result = authentication_budget(payload, now, args.ceiling, args.window_hours)
    except (ValueError, OverflowError) as error:
        print("Error: " + str(error), file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
