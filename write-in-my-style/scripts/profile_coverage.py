"""Resolve saved style rules for concrete writing situations."""

from profile_schema import SCOPE


LABELS = {
    "confirmed": "Confirmed",
    "observed": "Observed",
    "default": "Broad default",
    "conflict": "Needs confirmation",
    "missing": "Needs example",
}


def validate_scope(values):
    if len(values) != len(SCOPE) or any(
        value == "any" or value not in allowed
        for value, allowed in zip(values, SCOPE.values())
    ):
        raise ValueError("Choose a concrete channel, audience, and purpose from the schema command.")
    return dict(zip(SCOPE, values))


def feature_coverage(rules, feature, scope, revision):
    matches = []
    best_specificity = -1
    for rule in rules:
        if rule["feature"] != feature or any(rule[field] not in ("any", value) for field, value in scope.items()):
            continue
        specificity = sum(rule[field] == value for field, value in scope.items())
        if specificity < best_specificity:
            continue
        if specificity > best_specificity:
            matches.clear()
            best_specificity = specificity
        matches.append(rule)

    if not matches:
        return {"status": "missing", "choice": None, "sources": []}

    sources = [
        {"id": "/".join((f"P{revision}", *(rule[field] for field in SCOPE), feature)), **rule}
        for rule in sorted(matches, key=lambda rule: tuple(rule[field] for field in SCOPE))
    ]
    choices = {rule["choice"] for rule in matches}
    if len(choices) > 1:
        return {"status": "conflict", "choice": None, "sources": sources}

    status = matches[0]["status"] if best_specificity == len(scope) else "default"
    return {"status": status, "choice": matches[0]["choice"], "sources": sources}


def build_report(record, scopes, features):
    revision = record["revision"]
    profile = record["profile"]
    rules = profile["rules"] if profile else []
    return {
        "revision": revision,
        "language": "english",
        "contexts": [
            {
                "scope": scope,
                "features": {
                    feature: feature_coverage(rules, feature, scope, revision)
                    for feature in features
                },
            }
            for scope in scopes
        ],
    }


def format_markdown(report):
    contexts = report["contexts"]
    channel_labels = {"slack": "Slack", "whatsapp": "WhatsApp", "sms": "SMS", "email": "Email"}
    headings = ["Style choice"]
    for context in contexts:
        scope = context["scope"]
        headings.append(" · ".join((
            channel_labels[scope["channel"]],
            scope["audience"].replace("_", " "),
            scope["purpose"].replace("_", " "),
        )))
    rows = [headings, ["---"] * len(headings)]
    for feature in contexts[0]["features"]:
        cells = [feature.replace("_", " ").capitalize()]
        for context in contexts:
            cell = context["features"][feature]
            label = LABELS[cell["status"]]
            if cell["choice"] is not None:
                label += " · " + cell["choice"].replace("_", " ")
            cells.append(label)
        rows.append(cells)
    table = "\n".join("| " + " | ".join(row) + " |" for row in rows)
    return f"**Language** {report['language'].capitalize()}\n\n{table}"
