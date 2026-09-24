# Recipe library operations

## Use or publish shared recipes

Read [../assets/shared-recipes/README.md](../assets/shared-recipes/README.md) to browse the public starter cookbook. Its individual Markdown files are intentionally readable on GitHub and use consistent metadata. Treat the installed catalog as immutable seed content.

Shared recipes can be suggested directly. Before recording feedback, changing ingredients, or saving a variation, copy the full recipe into the personal library, give it a personal stable ID, and retain its shared recipe ID and catalog version as provenance. Rank personal-library recipes above shared recipes when both fit equally well, because personal recipes carry household history.

Publishing a personal recipe to the public catalog is a separate operation requiring an explicit user request. Before publishing:

- remove names, feedback, inventory, schedules, and other household data;
- use original concise wording or content the user has the right to redistribute;
- do not republish instructions copied from an imported URL merely because attribution exists;
- retain source attribution and license when a source permits redistribution;
- assign a stable shared ID, validate required metadata, add a readable recipe file, and update the shared index.

Do not promote recipes looked up in Wikibooks or another external collection into the shared catalog. Link to their original pages instead. When redistribution rights are unclear, keep a user-requested import personal and private.

## Add a recipe from a URL

1. Open the exact URL. Prefer recipe JSON-LD (`Recipe`) and then reconcile it with the visible page. Use visible content when structured data is absent or incomplete.
2. Capture the canonical URL, page title, recipe title, author or organization, site name, retrieval timestamp, and any stated yield, timing, cuisine, diet, or allergen information.
3. Normalize ingredients into structured entries while retaining the source wording in `original_text`. Separate quantity, unit, ingredient, preparation, and optionality only when supported by the page.
4. Rewrite the method as concise, complete steps. Preserve required temperatures, timings, dependencies, and doneness cues, but do not copy article prose, personal stories, or more wording than needed to cook the recipe.
5. Classify vegetarian or vegan from the actual ingredients, including garnishes and sauces. If unclear, use `dietary_tags: ["needs-review"]` and explain the ambiguity.
6. Estimate planning fields only when useful. Mark estimates and state their basis; do not silently replace the source's timing.
7. Check for duplicates by canonical URL, source URL, and closely matching title/ingredient signatures. Prefer updating attribution metadata or creating a revision over silently adding a duplicate.
8. Save the recipe record, update the rebuildable library index, validate it, and report its ID and source attribution.

Do not bypass access controls. If the recipe is blocked, incomplete, video-only, or requires a login, save no guessed recipe. Ask the user to provide the missing text or another accessible source.

The source URL and attribution must remain attached to imported recipes. Do not store an entire source article or unrelated page content.

## Add a recipe supplied directly by the user

Use `source.type: "user"`, record the supplied title or a neutral descriptive title, and set unknown fields to `null`. Confirm ambiguities that materially affect the ability to cook or classify the recipe; otherwise preserve them in `notes`.

## Brainstorm variations

Load the original recipe and relevant preferences or constraints. Generate variations against a clear goal such as vegan conversion, different cuisine, higher protein, less heat, freezer suitability, seasonal produce, or a shorter weeknight finish.

For every proposed variation:

- explain what changes and why;
- identify ingredient substitutions and method changes;
- flag flavor, texture, allergen, cost, prep, or freezing tradeoffs;
- keep it vegetarian or vegan as requested;
- calculate the revised weekday assembly estimate rather than copying the original;
- do not claim a substitution is equivalent when it changes structure or cooking behavior.

Brainstorming alone does not change the library. When the user chooses a variation, save it as a new recipe with its own ID and:

```json
"derived_from": {
  "recipe_id": "original-id",
  "relationship": "variation",
  "variation_summary": "Vegan version using cashew cream and white beans"
}
```

Retain source attribution from the original under `source`, and state that the variation was adapted by the household unless another source was used. Never overwrite the original recipe file.

## Revise or correct a recipe

Distinguish factual import corrections from creative variations. Correct extraction errors in place while recording `updated_at` and a short `revision_note`. For material method or ingredient changes, create a derived recipe instead. Keep user ratings and observed outcomes in feedback records, not the recipe file.
