import unittest

from profile_coverage import build_report, format_markdown, validate_scope
from profile_schema import validate


SLACK = validate_scope(("slack", "teammate", "request"))
EMAIL = validate_scope(("email", "new_client", "request"))


def rule(scope, choice, status):
    return {**scope, "feature": "message_order", "choice": choice, "status": status}


def report(*rules):
    profile = {"version": 1, "rules": list(rules)}
    validate(profile)
    return build_report({"revision": 7, "profile": profile}, [SLACK, EMAIL], ["message_order", "request_form"])


class CoverageTests(unittest.TestCase):
    def test_empty_profile_keeps_gaps_in_all_requested_scopes(self):
        result = build_report({"revision": None, "profile": None}, [SLACK, EMAIL], ["message_order"])
        for context in result["contexts"]:
            cell = context["features"]["message_order"]
            self.assertEqual(cell, {"status": "missing", "choice": None, "sources": []})
        self.assertIn("| Message order | Needs example | Needs example |", format_markdown(result))

    def test_narrow_evidence_wins_and_citation_identifies_the_actual_rule(self):
        broad = {"channel": "any", "audience": "any", "purpose": "request"}
        result = report(
            rule(broad, "context_then_point", "confirmed"),
            rule(SLACK, "ask_then_reason", "observed"),
        )
        slack, email = [context["features"]["message_order"] for context in result["contexts"]]
        self.assertEqual((slack["status"], slack["choice"]), ("observed", "ask_then_reason"))
        self.assertEqual([source["id"] for source in slack["sources"]], ["P7/slack/teammate/request/message_order"])
        self.assertEqual((email["status"], email["choice"]), ("default", "context_then_point"))
        self.assertEqual([source["id"] for source in email["sources"]], ["P7/any/any/request/message_order"])
        output = format_markdown(result)
        self.assertTrue(output.startswith("**Language** English"))
        self.assertIn("| Message order | Observed · ask then reason | Broad default · context then point |", output)

    def test_other_context_and_other_feature_do_not_inherit_the_observation(self):
        result = report(rule(SLACK, "ask_then_reason", "observed"))
        slack, email = [context["features"] for context in result["contexts"]]
        self.assertEqual(slack["request_form"]["status"], "missing")
        self.assertEqual(email["message_order"]["sources"], [])

    def test_equally_specific_conflict_cites_both_rules_and_selects_neither(self):
        result = report(
            rule({**SLACK, "channel": "any"}, "context_then_point", "confirmed"),
            rule({**SLACK, "audience": "any"}, "ask_then_reason", "confirmed"),
        )
        cell = result["contexts"][0]["features"]["message_order"]
        self.assertEqual((cell["status"], cell["choice"]), ("conflict", None))
        self.assertEqual([source["id"] for source in cell["sources"]], [
            "P7/any/teammate/request/message_order",
            "P7/slack/any/request/message_order",
        ])
        self.assertIn("Needs confirmation", format_markdown(result))

    def test_scope_requires_concrete_allowlisted_labels(self):
        for values in (("any", "teammate", "request"), ("slack", "example person", "request")):
            with self.subTest(values=values), self.assertRaises(ValueError):
                validate_scope(values)


if __name__ == "__main__":
    unittest.main()
