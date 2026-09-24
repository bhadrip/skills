# Storage model

Use human-readable JSON for durable records and Markdown for cook- and shopper-facing views. JSON is the source of truth; Markdown outputs are regenerable.

The installed skill's `assets/shared-recipes/` cookbook is public, version-controlled, read-only seed data. Personal imports, copies, variants, ratings, inventory, and plans belong in the data root below. This separation lets the public cookbook evolve without exposing household information or overwriting personal changes.

## Default location and layout

Use the product-neutral user data directory `~/.meal-prep-agent/` unless the user chooses another location. Resolve and report the absolute path before the first write. This directory is local, can be shared by Codex and Claude on the same computer, and is not part of the public `skills` repository. A user who wants sync should choose a separate private repository or another private storage provider; never infer that public GitHub is acceptable for household data.

```text
meal-prep-agent/
|-- library/
|   |-- recipes/
|   |   `-- <recipe-id>.json
|   |-- index.json
|   `-- ingredient-aliases.json
|-- inventory/
|   |-- freezer.json
|   `-- on-hand.json
|-- preferences/
|   `-- household.json
|-- feedback/
|   `-- events.jsonl
|-- history/
|   `-- cooked-events.jsonl
|-- plans/
|   `-- <week-start>-plan.json
`-- shopping/
    |-- <week-start>-shopping.json
    `-- <week-start>-shopping.md
```

Create `library/index.json` as a rebuildable catalog of recipe ID, title, dietary tags, cuisines, main ingredients, source domain, and updated timestamp. The recipe files remain canonical.

## Schemas

Validate records against the schemas when a validator is available:

- [schemas/household-profile.schema.json](schemas/household-profile.schema.json) for confirmed onboarding answers and stable preferences;
- [schemas/recipe.schema.json](schemas/recipe.schema.json) for normalized recipes and separately stored variations;
- [schemas/inventory.schema.json](schemas/inventory.schema.json) for freezer and on-hand stock;
- [schemas/weekly-plan.schema.json](schemas/weekly-plan.schema.json) for candidates, selected meals, prep work, reuse, and emergency coverage;
- [schemas/shopping-list.schema.json](schemas/shopping-list.schema.json) for consolidated quantities with recipe traceability;
- [schemas/feedback-event.schema.json](schemas/feedback-event.schema.json) for each append-only feedback line.
- [schemas/cooked-event.schema.json](schemas/cooked-event.schema.json) for durable cooking history and explicit corrections.

Keep `preferences/household.json` small, reviewable, and valid against the household-profile schema:

```json
{
  "schema_version": "1.0",
  "status": "confirmed",
  "household": {"description": "2 adults and 1 child", "default_servings": 4},
  "hard_constraints": {
    "dietary_rules": ["vegetarian"],
    "allergies_or_intolerances": [],
    "other_exclusions": [],
    "uncertainties": []
  },
  "planning": {
    "dinners_per_cycle": 5,
    "planned_days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
    "weekday_hands_on_minutes_max": 20,
    "weekend_prep": {"available": true, "preferred_days": ["Sunday"], "hands_on_minutes_max": 90}
  },
  "primary_goal": "Reduce evening stress",
  "biggest_difficulties": ["Decision fatigue", "Fresh vegetables spoil before use"],
  "optional_preferences": {"likes": [], "dislikes": [], "cuisines": [], "spice_preferences": [], "planning_preferences": ["At least half of dinners vegan"]},
  "confirmed_at": "2026-09-23T14:00:00-07:00",
  "updated_at": "2026-09-23T14:00:00-07:00"
}
```

## Persistence rules

- Use lowercase, stable slug IDs with a short disambiguator when needed, such as `chickpea-spinach-wraps-a13f`.
- Never change a recipe ID because its title changes.
- A variation is a new recipe record with `derived_from.recipe_id`; the source recipe stays intact.
- When adopting a shared recipe, copy it into `library/recipes/`, retain its shared recipe ID and catalog version, assign a personal stable ID, and customize only the personal copy.
- Do not embed feedback or inventory mutations inside recipe records. Join them by `recipe_id`.
- Append feedback as one valid JSON object per line. Do not rewrite history merely because preferences changed.
- Record a confirmed cooked meal separately from optional feedback so recency and repetition still work when nobody rates dinner. Undo mistakes with a new reversing event rather than deleting history.
- Normalize ingredient aliases through `library/ingredient-aliases.json`, while retaining the user's display wording. Never merge similarly named ingredients when their culinary form differs.
- Update inventory quantities only after the user confirms purchase, consumption, freezing, thawing, discard, or correction. A proposed plan is not proof of an inventory change.
- Save a household profile only after the user confirms the onboarding summary. Treat an explicit `none` as an empty array and preserve `not sure` details in `hard_constraints.uncertainties` rather than guessing.
- Before overwriting a plan or shopping output for the same week, preserve user selections and manual edits or write a clearly versioned replacement.
- Use `null` for unknown values. Do not invent exact quantities, dates, nutrition, or shelf life.

## Date and freezer guidance

For a freezer item, store `frozen_on` when known and `best_use_by` only when a label, source, user statement, or cited storage guideline supports it. Also store `guidance_basis` and `guidance_note`. Treat best-use dates as quality guidance, not an assertion of safety. Flag temperature abuse, thaw/refreeze uncertainty, damaged packaging, mold, off odors, or other safety concerns for user judgment or authoritative guidance.
