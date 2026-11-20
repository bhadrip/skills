"""Allowed values for a saved English writing-style profile."""

VERSION = 1
SCOPE = {
    "channel": ("any", "slack", "whatsapp", "email", "sms"),
    "audience": (
        "any", "friend", "family", "partner", "teammate", "manager", "direct_report",
        "new_client", "existing_client", "external_contact", "group",
    ),
    "purpose": (
        "any", "request", "follow_up", "logistics", "update", "feedback",
        "disagreement", "apology", "decline", "thanks", "introduction", "announcement",
    ),
}
CHOICES = {
    "opening": ("none", "greeting", "acknowledgment", "thanks", "main_point"),
    "message_order": ("ask_then_reason", "main_point_then_detail", "context_then_point", "chronological"),
    "context_amount": ("minimal", "brief", "detailed"),
    "request_form": ("direct_instruction", "can_you", "could_you", "would_you", "lets", "hint"),
    "formality": ("casual", "neutral", "formal"),
    "warmth": ("reserved", "friendly", "expressive"),
    "uncertainty": ("brief_hedge", "explicit_assumptions", "conditional", "state_confidence"),
    "word_choice": ("plain", "technical", "colloquial", "mixed"),
    "contractions": ("frequent", "occasional", "rare"),
    "sentence_shape": ("mostly_complete", "mix_with_fragments", "mostly_fragments"),
    "sentence_length": ("short", "varied", "long"),
    "capitalization": ("standard", "mostly_lowercase"),
    "final_punctuation": ("usually_omit", "standard", "expressive"),
    "emoji": ("none", "occasional", "frequent"),
    "layout": ("single_block", "short_paragraphs", "line_breaks", "bullets"),
    "closing": ("none", "thanks", "sign_off", "next_step", "question"),
    "acknowledgment": ("brief", "restates_point", "thanks", "usually_omitted"),
    "support": ("one_reason", "examples", "analogies", "numbers", "step_by_step"),
    "humor": ("rare", "occasional", "frequent"),
}
STATUSES = ("confirmed", "observed")


def schema():
    return {"version": VERSION, "language": "english", "scope": SCOPE, "choices": CHOICES, "statuses": STATUSES}


def validate(profile):
    if (
        not isinstance(profile, dict)
        or profile.keys() != {"version", "rules"}
        or type(profile["version"]) is not int
        or profile["version"] != VERSION
        or not isinstance(profile["rules"], list)
    ):
        raise ValueError("Use the versioned style-rule object from the schema command.")

    seen = set()
    for rule in profile["rules"]:
        if not isinstance(rule, dict) or rule.keys() != {*SCOPE, "feature", "choice", "status"}:
            raise ValueError("Save only the standard style-rule fields from the schema command.")
        if not all(isinstance(value, str) for value in rule.values()):
            raise ValueError("Use the listed style labels for every rule field.")
        scope = tuple(rule[field] for field in SCOPE)
        if any(rule[field] not in allowed for field, allowed in SCOPE.items()):
            raise ValueError("Use only the listed channels, audiences, and purposes.")
        feature = rule["feature"]
        if rule["choice"] not in CHOICES.get(feature, ()) or rule["status"] not in STATUSES:
            raise ValueError("Use only the listed features, choices, and evidence statuses.")
        if "any" in scope and rule["status"] != "confirmed":
            raise ValueError("Use a broad scope only for a rule the user confirmed in that scope.")
        key = (*scope, feature)
        if key in seen:
            raise ValueError("Keep one choice per feature and scope.")
        seen.add(key)
