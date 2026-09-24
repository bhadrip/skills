# Examples

These examples show record shape, not a mandatory menu.

## Confirmed household profile

```json
{
  "schema_version": "1.0",
  "status": "confirmed",
  "household": {
    "description": "2 adults and 1 child",
    "default_servings": 4,
    "member_preferences": []
  },
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
    "weekend_prep": {
      "available": true,
      "preferred_days": ["Sunday"],
      "hands_on_minutes_max": 90
    }
  },
  "primary_goal": "Reduce evening stress",
  "biggest_difficulties": ["Decision fatigue", "Fresh vegetables spoil before use"],
  "optional_preferences": {
    "likes": [],
    "dislikes": ["mushrooms"],
    "cuisines": ["Indian", "Mexican", "Mediterranean"],
    "spice_preferences": ["Mild for child; medium for adults"],
    "planning_preferences": ["At least half of dinners vegan"],
    "equipment": ["stovetop", "oven", "pressure cooker"],
    "freezer_notes": "Space for about four dinner containers",
    "budget_notes": null
  },
  "confirmed_at": "2026-09-23T14:00:00-07:00",
  "updated_at": "2026-09-23T14:00:00-07:00"
}
```

## Imported recipe and saved variation

```json
{
  "schema_version": "1.0",
  "id": "tomato-chickpea-pasta-7c21",
  "title": "Tomato chickpea pasta",
  "status": "active",
  "source": {
    "type": "url",
    "url": "https://example.org/recipes/tomato-chickpea-pasta",
    "canonical_url": "https://example.org/recipes/tomato-chickpea-pasta",
    "title": "Tomato Chickpea Pasta",
    "author": "Example Kitchen",
    "site_name": "Example Kitchen",
    "retrieved_at": "2026-09-23T14:00:00-07:00",
    "attribution": "Adapted from Example Kitchen"
  },
  "metadata": {
    "servings": 4,
    "dietary_tags": ["vegan"],
    "cuisines": ["Italian-inspired"],
    "source_total_minutes": 30
  },
  "ingredients": [
    {
      "original_text": "12 oz short pasta",
      "name": "short pasta",
      "normalized_name": "pasta, short",
      "quantity": 12,
      "unit": "oz",
      "preparation": null,
      "optional": false
    }
  ],
  "instructions": [
    {"step": 1, "text": "Boil the pasta in salted water until al dente.", "active_minutes": 2},
    {"step": 2, "text": "Warm the prepared tomato-chickpea sauce and combine with the drained pasta.", "active_minutes": 5}
  ],
  "planning": {
    "weekday_assembly_minutes": 12,
    "passive_minutes": 10,
    "total_elapsed_minutes": 22,
    "weekend_prep": ["Make and chill the tomato-chickpea sauce"],
    "freezer_suitability": "Freeze the sauce, not the cooked pasta"
  },
  "created_at": "2026-09-23T14:05:00-07:00",
  "updated_at": "2026-09-23T14:05:00-07:00"
}
```

A chosen spinach variation is a separate file with a new ID:

```json
{
  "id": "tomato-chickpea-spinach-pasta-63aa",
  "title": "Tomato chickpea spinach pasta",
  "derived_from": {
    "recipe_id": "tomato-chickpea-pasta-7c21",
    "relationship": "variation",
    "variation_summary": "Adds spinach during the weekday finish to use fragile produce"
  }
}
```

The full saved variation must still conform to the recipe schema; the abbreviated example only highlights lineage.

## Dinner option

```text
Tomato chickpea spinach pasta — vegan — 12 min hands-on
Weekend dependency: tomato-chickpea sauce
Use first: spinach, Monday
Reuse: sauce batch also supplies Thursday's stuffed peppers
Buy: short pasta, spinach
On hand: chickpeas (confirm count)
Freezer: freeze two sauce portions; do not freeze assembled pasta
```

## Weekend prep block

```text
Sunday · Tomato-chickpea sauce · 15 min hands-on + 25 min simmer
Makes: 8 servings for Monday pasta, Thursday peppers, and 2 freezer servings
Store: cool, then refrigerate two labeled containers and freeze one
Weeknight finish: boil pasta; wilt spinach into reheated sauce; combine
```

## Lightweight feedback

```json
{"schema_version":"1.0","event_id":"fb-20260928-001","recorded_at":"2026-09-28T19:40:00-07:00","recipe_id":"tomato-chickpea-spinach-pasta-63aa","plan_id":"2026-09-28","rating":4,"repeat":"yes_with_changes","actual_weekday_assembly_minutes":18,"signals":[{"member":"children","type":"texture","value":"preferred chickpeas partly mashed"}],"notes":"Used one extra handful of spinach."}
```

Possible inference: raise the family's confidence in this recipe, retain the observed 18-minute estimate, and prefer partly mashed chickpeas for children. Do not infer a general dislike of whole chickpeas from one meal.
