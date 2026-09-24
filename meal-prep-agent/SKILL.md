---
name: meal-prep-agent
description: Manage a persistent household recipe library, import recipes from URLs, create recipe variations, plan quick dinners and weekend prep, maintain freezer inventory, consolidate shopping, guide cooking, and learn from meal feedback. Use for family meal-prep workflows across dietary patterns; do not treat it as clinical nutrition or allergy advice.
metadata:
  version: "0.1.0"
  compatibility: Codex, Claude Code, and Claude.ai; URL imports need web access, and durable household storage needs persistent file access.
---

# Meal Prep Agent

Build an evolving household meal system around a first-class recipe library. Keep five capabilities modular: library, planning, shopping, cooking, and feedback.

The skill includes a public, read-only starter cookbook at [assets/shared-recipes/README.md](assets/shared-recipes/README.md). Use it when the personal library is small or the user asks for shared recipes. Copy a selected recipe into personal storage before customizing it; never write household state into the installed skill.

## Resolve storage before writing

Store household data outside this installed skill. Use a location the user provides; otherwise use the product-neutral user data directory `~/.meal-prep-agent/`, and tell the user the resolved absolute path before the first write. Create only the directories needed for the current operation. This shared default lets Codex and Claude use the same private household records without putting them inside either agent's installation. If that location is unavailable, use `meal-prep-data/` in the current workspace only after ensuring it is excluded from public version control.

Read [references/storage-model.md](references/storage-model.md) before creating or changing persistent data. Preserve stable IDs and source records. Never overwrite an original recipe to create a variation.

If durable storage is unavailable, return the proposed records as JSON or Markdown artifacts and clearly say they have not been persisted.

## Route the request

Use only the references needed for the requested operation:

- To add, find, update, vary, or publish recipes, read [references/recipe-library.md](references/recipe-library.md).
- To discover recipes from external open collections, read [references/open-recipe-sources.md](references/open-recipe-sources.md). Consult those collections on demand and link users to them; do not mirror or bulk-import them into this skill.
- To propose dinners, build a weekly plan, prepare on Saturday/Sunday, manage freezer meals, reduce spoilage, or consolidate shopping, read [references/planning-and-shopping.md](references/planning-and-shopping.md).
- To guide a live cooking session or record feedback and update preferences, read [references/cooking-and-feedback.md](references/cooking-and-feedback.md).
- For representative records and outputs, read [references/examples.md](references/examples.md).

When a request spans modes, perform them in dependency order: inspect or update the library and household state, generate options, confirm or infer the selected meals, persist the plan, build the shopping list, then support cooking and feedback.

## Shared defaults

Apply these defaults unless household data or the user says otherwise:

- Offer at least 10 genuinely distinct dinner options that satisfy the household's current dietary preferences and constraints. Label each option's relevant dietary classification accurately.
- Treat `weekday_assembly_minutes` as hands-on evening effort after planned weekend prep, not misleading total time. Keep it at or below 20 minutes. Surface passive heating, thawing, and total elapsed time separately.
- Prefer plans that reuse ingredients deliberately, consume fragile produce before durable produce, and do not repeat the same flavor profile merely to reuse an ingredient.
- Front-load safe, quality-preserving work into Saturday or Sunday: washing, chopping, sauces, cooked grains or beans, measured kits, and freezer batches.
- Maintain a configurable emergency reserve; default to at least two complete dinners after the planned week. Use freezer stock before adding a new batch when dates and preferences support it.
- Treat allergies and hard exclusions as constraints. Verify ambiguous packaged ingredients and cross-contamination concerns instead of inferring safety from a broad dietary label.
- Keep quantities, servings, units, dates, and assumptions explicit. Use ISO `YYYY-MM-DD` dates and local time with an offset for timestamps.

## Finish each operation

Report what changed, where it was saved, and any unresolved assumptions. For plans, summarize the selected meals, weekend prep burden, emergency coverage, ingredients reused across meals, and perishable items intentionally used first. For imports, give the recipe ID and attribution. For feedback, distinguish the recorded event from any preference inference.
