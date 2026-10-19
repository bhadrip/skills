"""Synthetic offline tests. No live accounts, appointment records, or requests."""

import contextlib
import io
import tempfile
import unittest
from datetime import timedelta
from pathlib import Path

from appointment_math import authentication_budget, calendar_cutoff, main, utc_timestamp


def event(index, timestamp):
    return {"id": "synthetic-flow-" + str(index), "counted_at_utc": timestamp}


class AppointmentMathTests(unittest.TestCase):
    def setUp(self):
        self.now = utc_timestamp("2040-06-10T12:00:00Z")

    def test_date_basis_is_not_utc_date(self):
        result = calendar_cutoff(
            utc_timestamp("2040-01-02T01:00:00Z"), "America/New_York", 2
        )
        self.assertEqual(result["basis_date"], "2040-01-01")
        self.assertEqual(result["earliest_appointment_date_inclusive"], "2040-01-03")

    def test_calendar_days_across_dst(self):
        cases = [("2030-03-10T04:30:00Z", "2030-03-10"),
                 ("2030-11-03T04:30:00Z", "2030-11-04")]
        for at, expected in cases:
            result = calendar_cutoff(utc_timestamp(at), "America/New_York", 1)
            self.assertEqual(result["earliest_appointment_date_inclusive"], expected)

    def test_leap_day_and_year_boundary(self):
        cases = [("2040-02-28T12:00:00Z", "2040-02-29"),
                 ("2040-12-31T12:00:00Z", "2041-01-01")]
        for at, expected in cases:
            result = calendar_cutoff(utc_timestamp(at), "UTC", 1)
            self.assertEqual(result["earliest_appointment_date_inclusive"], expected)

    def test_invalid_date_configuration(self):
        for zone, days in [("Invalid/Timezone", 1), ("UTC", -1), ("UTC", True)]:
            with self.assertRaises(ValueError):
                calendar_cutoff(self.now, zone, days)
        with self.assertRaises(ValueError):
            utc_timestamp("2040-01-01T00:00:00")

    def test_exact_window_boundary_expires(self):
        result = authentication_budget(
            [event(1, "2040-06-09T12:00:00Z")], self.now, 1, 24
        )
        self.assertEqual(result["rolling_flow_count"], 0)
        self.assertTrue(result["new_flow_allowed"])

    def test_overrun_needs_more_than_oldest_expiry(self):
        payload = [event(i, (self.now - timedelta(hours=age)).isoformat())
                   for i, age in enumerate([23, 22, 21, 20, 19, 18])]
        result = authentication_budget(payload, self.now, 5, 24)
        self.assertEqual(result["rolling_flow_count"], 6)
        self.assertFalse(result["new_flow_allowed"])
        self.assertEqual(result["next_new_flow_at_utc"], "2040-06-10T14:00:00Z")
        permitted = authentication_budget(
            payload, utc_timestamp(result["next_new_flow_at_utc"]), 5, 24
        )
        self.assertTrue(permitted["new_flow_allowed"])
        self.assertEqual(permitted["rolling_flow_count"], 4)

    def test_same_flow_completion_not_counted_twice(self):
        first = event(1, "2040-06-10T11:00:00Z")
        finished = {**first, "outcome": "completed", "credential_submissions": 1}
        result = authentication_budget(
            {"authentication": {"flow_events": [first, finished]}}, self.now, 2, 24
        )
        self.assertEqual(result["rolling_flow_count"], 1)
        self.assertEqual(result["remaining_new_flows"], 1)

    def test_new_flow_moves_next_eligibility(self):
        payload = [event(i, (self.now - timedelta(hours=age)).isoformat())
                   for i, age in enumerate([23, 22, 21, 20, 19])]
        before = authentication_budget(payload, self.now, 5, 24)
        after = authentication_budget(
            payload + [event(9, self.now.isoformat())], self.now, 5, 24
        )
        self.assertEqual(before["next_new_flow_at_utc"], "2040-06-10T13:00:00Z")
        self.assertEqual(after["next_new_flow_at_utc"], "2040-06-10T14:00:00Z")

    def test_bad_or_ambiguous_events_fail_closed(self):
        cases = [
            [event(1, "2040-06-10T13:00:00Z")],
            [event(1, "2040-06-10T10:00:00Z"), event(1, "2040-06-10T11:00:00Z")],
            [{"counted_at_utc": "2040-06-10T11:00:00Z"}],
            {"unrelated_private_field": "SYNTHETIC_NOT_A_CREDENTIAL"},
        ]
        for payload in cases:
            with self.assertRaises(ValueError):
                authentication_budget(payload, self.now, 5, 24)

    def test_cli_does_not_echo_invalid_payload(self):
        marker = "SYNTHETIC_NOT_A_CREDENTIAL"
        with tempfile.TemporaryDirectory() as folder:
            state = Path(folder) / "synthetic.json"
            state.write_text('[{"id":"x","counted_at_utc":"' + marker + '"}]')
            out, err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                code = main(["auth-budget", "--state", str(state), "--ceiling", "5",
                             "--window-hours", "24", "--at", self.now.isoformat()])
            self.assertEqual(code, 2)
            self.assertEqual(out.getvalue(), "")
            self.assertNotIn(marker, err.getvalue())


if __name__ == "__main__":
    unittest.main()
