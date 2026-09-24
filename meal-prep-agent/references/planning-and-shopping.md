# Planning and shopping

## Build dinner options

Inspect the recipe library, household preferences, freezer and on-hand inventory, recent feedback, recent plans, serving needs, and date-sensitive ingredients. If one of these is unavailable, name the gap and make a conservative assumption.

Produce at least 10 distinct options. Library recipes should be the default source; clearly mark any new suggestion as `proposed` and do not add it to the library until the user asks. Each option should include:

- recipe ID or `proposed` status;
- title and vegetarian/vegan label;
- weekday hands-on assembly minutes, passive minutes, and total elapsed minutes;
- weekend preparation it depends on;
- ingredients already on hand, ingredients to buy, and a confidence note when inventory is stale;
- perishable ingredients it uses and when they should be eaten;
- leftovers or planned reuse;
- freezer suitability and a simple household-friendly adjustment when relevant.

An option meets the quick-dinner constraint only when weekday hands-on assembly is no more than 20 minutes after its declared prep. Do not hide chopping, thawing, marinating, pressure release, cleanup-heavy blending, or appliance preheating. If an exception is valuable, label it and explain why; do not count it toward the compliant minimum.

## Select and schedule meals

If the user has not selected meals, make a clearly labeled draft selection based on their requested number of dinners. Schedule the most fragile produce first, account for leftovers, vary cuisines and textures, and avoid placing meals that depend on the same unfinished component too far apart.

Record ingredient reuse as intentional links rather than merely repeating ingredients. For each reused ingredient, show which meals consume it and the planned quantity when known.

Use known `best_use_by`, opened, ripe, or purchase dates to calculate spoilage priority. If dates are absent, use qualitative perishability and label the inference. Never imply that appearance or a date alone establishes food safety.

## Weekend prep plan

Group work into Saturday and/or Sunday sessions according to the user's availability. Order tasks to share equipment and reduce cleanup. Include:

- exact component and amount;
- recipes served;
- hands-on and passive time;
- equipment;
- cooling, storage container, storage location, and label;
- safe stopping point and weekday finish;
- use-by guidance and its basis when known.

Do not pre-chop or pre-cook merely to move work out of the 20-minute window when doing so will noticeably harm quality. Keep dressings separate when appropriate. Cool cooked foods promptly and avoid unsafe room-temperature holding; use authoritative current guidance if the user asks for exact safety limits.

## Emergency meals and freezer inventory

Count complete dinner equivalents, not containers. Default to leaving at least two complete emergency dinners after the planned week. Prefer older suitable stock first, while respecting quality, preferences, allergens, thaw time, and uncertainty.

If the reserve falls short, add a freezer-friendly batch to weekend prep or propose a pantry-stable fallback. Each freezer entry must track item, quantity or servings, frozen date when known, best-use guidance, guidance basis, thaw/reheat notes, and linked recipe ID when applicable.

An `Emergency dinner` request should return the best usable option in this order:

1. a complete freezer dinner that fits the time available;
2. a pantry-stable meal;
3. a fast meal using at-risk fresh ingredients.

Explain why the option was chosen and what inventory change to record after the user confirms it was used.

## Consolidate the shopping list

Build the list only after meals and batch sizes are selected or clearly labeled as a draft. Scale recipe ingredients to servings, subtract confirmed usable inventory, and combine equivalent ingredients across recipes without collapsing materially different forms such as fresh ginger and ground ginger.

Preserve both normalized totals and recipe-level traceability. Group the shopper view by produce, refrigerated, pantry, frozen, bakery, and other useful store sections. Mark:

- already on hand, but only when recently confirmed;
- optional garnish or substitution;
- package-size or unit-conversion assumptions;
- ingredients shared by multiple meals;
- ingredients with a likely remainder and a plan to use or freeze it.

Save structured JSON for regeneration and a concise Markdown checklist for use in the store.
