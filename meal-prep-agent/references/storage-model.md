# Storage model

Use human-readable JSON for durable records and Markdown for cook- and shopper-facing views. JSON is the source of truth; Markdown outputs are regenerable.

The installed skill's `assets/shared-recipes/` cookbook is public, version-controlled, read-only seed data. Personal imports, copies, variants, ratings, inventory, and plans belong in the data root below. This separation lets the public cookbook evolve without exposing household information or overwriting personal changes.

## Default location and layout

Use the user's Codex data directory, normally `~/.codex/data/meal-prep-agent/`, unless the user chooses another location. Resolve and report the absolute path before the first write. This directory is local and is not part of the public `skills` repository. A user who wants sync should choose a separate private repository or another private storage provider; never infer that public GitHub is acceptable for household data.

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

- [schemas/recipe.schema.json](schemas/recipe.schema.json) for normalized recipes and separately stored variations;
- [schemas/inventory.schema.json](schemas/inventory.schema.json) for freezer and on-hand stock;
- [schemas/weekly-plan.schema.json](schemas/weekly-plan.schema.json) for candidates, selected meals, prep work, reuse, and emergency coverage;
- [schemas/shopping-list.schema.json](schemas/shopping-list.schema.json) for consolidated quantities with recipe traceability;
- [schemas/feedback-event.schema.json](schemas/feedback-event.schema.json) for each append-only feedback line.
- [schemas/cooked-event.schema.json](schemas/cooked-event.schema.json) for durable cooking history and explicit corrections.

Preferences do not need a rigid schema. Keep `preferences/household.json` small and reviewable:

```json
{
  "schema_version": "1.0",
  "household": {"adults": 2, "children": 1},
  "hard_constraints": ["vegetarian"],
  "soft_preferences": [
    {
      "subject": "broccoli",
      "signal": "dislike",
      "weight": 0.4,
      "evidence_count": 2,
      "last_observed_at": "2026-09-20T19:30:00-07:00"
    }
  ],
  "planning_defaults": {
    "weekday_assembly_minutes_max": 20,
    "minimum_dinner_options": 10,
    "emergency_dinners_target": 2
  }
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
- Before overwriting a plan or shopping output for the same week, preserve user selections and manual edits or write a clearly versioned replacement.
- Use `null` for unknown values. Do not invent exact quantities, dates, nutrition, or shelf life.

## Date and freezer guidance

For a freezer item, store `frozen_on` when known and `best_use_by` only when a label, source, user statement, or cited storage guideline supports it. Also store `guidance_basis` and `guidance_note`. Treat best-use dates as quality guidance, not an assertion of safety. Flag temperature abuse, thaw/refreeze uncertainty, damaged packaging, mold, off odors, or other safety concerns for user judgment or authoritative guidance.
