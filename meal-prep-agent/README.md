# Meal Prep Agent

`meal-prep-agent` is a Codex skill for running a personal vegetarian or vegan meal-prep system. It keeps a recipe library, plans quick dinners, front-loads work into the weekend, tracks emergency freezer meals, consolidates shopping, guides cooking, and learns from lightweight feedback.

The skill includes a small [public starter cookbook](assets/shared-recipes/README.md). Your personal recipes and household data stay outside the public repository.

## Install

Clone this repository and copy the skill folder into your Codex skills directory:

```sh
git clone https://github.com/bhadrip/skills.git
cp -R skills/meal-prep-agent "${CODEX_HOME:-$HOME/.codex}/skills/"
```

Restart or refresh Codex if the skill does not appear immediately. Invoke it as `$meal-prep-agent`, or describe a matching meal-planning request naturally.

## Start with household preferences

Tell the agent the details that materially affect planning. You can add or revise them over time.

```text
Use $meal-prep-agent. We are two adults and one child. Keep dinners vegetarian,
make at least half vegan, avoid mushrooms, and keep weekday hands-on work under
20 minutes. We can prep for 90 minutes on Sunday.
```

The skill stores private data in the user's Codex data directory, normally:

```text
~/.codex/data/meal-prep-agent/
```

It reports the resolved absolute path before the first write. You can request another private location.

## Add recipes

Give the agent a recipe URL:

```text
Use $meal-prep-agent to add this recipe to my personal library: <URL>
```

The agent extracts and normalizes the ingredients, instructions, yield, timing, dietary classification, and planning metadata while preserving the source URL and attribution. The imported record remains private unless you explicitly request publication.

External collections such as Wikibooks are lookup-only. The agent may search them, summarize relevant options, and link to the original pages, but it does not mirror or bulk-import them into this repository.

## Brainstorm variations

Variations never overwrite the original recipe.

```text
Show me three vegan variations of my paneer wraps. One should be freezer-friendly
and all should stay under 20 minutes of weekday assembly. Do not save them yet.
```

After choosing one:

```text
Save variation 2 as a new recipe in my personal library.
```

The saved variation receives its own ID and retains a link to the original recipe.

## Plan the week

```text
Plan five dinners for next week. Give me at least 10 vegetarian or vegan options
first, use the spinach and peppers early, reuse ingredients without making every
meal taste alike, and leave two emergency dinners in the freezer.
```

The agent distinguishes hands-on weekday assembly from passive and total elapsed time. It uses personal recipes first, then the shared starter cookbook, and clearly labels new suggestions that have not been saved.

## Prepare on Saturday or Sunday

```text
Turn the selected meals into a Sunday prep session. Group tasks to reduce cleanup,
show active and passive time, and tell me how to cool, label, and store each component.
```

The plan can front-load chopping, sauces, grains, beans, measured kits, and freezer batches while leaving quality-sensitive work for the weeknight.

## Manage emergency meals

```text
I froze four servings of chickpea curry today. Add it to my freezer inventory.
```

```text
Emergency dinner: I have 15 minutes and the fresh vegetables may have spoiled.
What should we eat?
```

Freezer records track servings, freeze date, best-use guidance and its basis, plus thawing or reheating notes. Inventory changes are recorded only after you confirm what was frozen, used, or discarded.

## Build the shopping list

```text
Make the consolidated shopping list for the selected plan. Subtract only inventory
that I confirmed, group the list by store section, and show which meals use each item.
```

The skill keeps structured totals for future edits and produces a concise Markdown checklist for shopping.

## Use cooking mode

```text
Start cooking mode for tonight's tofu noodles. Give me no more than two steps at a time.
```

Cooking mode loads the exact recipe and variation, puts quantities and timing inside each step, and tracks parallel work without showing the entire recipe at once unless requested.

## Record feedback

```text
The dal was a 4 out of 5. Adults liked the heat, but it was too spicy for the child.
It took 24 minutes instead of 15. We would make it again with less chili.
```

The raw event is appended to feedback history. Preference learning remains cautious: one reaction can adjust future rankings or timing estimates without becoming a permanent household ban.

## Public and private recipes

- The [shared cookbook](assets/shared-recipes/README.md) is public, version-controlled, and read-only during normal use.
- Imported recipes, custom variations, feedback, preferences, inventory, plans, and shopping lists stay in private household storage.
- A shared recipe is copied into the personal library before customization.
- Publishing a recipe is a separate, explicit operation. Only recipes created for this project or explicitly contributed for publication belong in the public cookbook.

## Included references

The implementation guidance is split by responsibility:

- [recipe library operations](references/recipe-library.md)
- [planning and shopping](references/planning-and-shopping.md)
- [cooking and feedback](references/cooking-and-feedback.md)
- [storage model](references/storage-model.md)
- [external lookup sources](references/open-recipe-sources.md)
- [schemas](references/schemas) and [examples](references/examples.md)
