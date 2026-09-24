# Meal Prep Agent

`meal-prep-agent` is an Agent Skill for running a personal family meal-prep system with ChatGPT, Codex, or Claude. It keeps a recipe library, plans quick dinners, front-loads work into the weekend, tracks emergency freezer meals, consolidates shopping, guides cooking, and learns from lightweight feedback. Dietary patterns are household preferences, not restrictions built into the skill.

The skill includes a small [public starter cookbook](assets/shared-recipes/README.md). Your personal recipes and household data stay outside the public repository.

## Start here

Ask naturally, select the skill with `@` in ChatGPT when Skills are available, invoke `$meal-prep-agent` in Codex, or invoke `/meal-prep-agent` in Claude Code. A good first request is:

```text
Help me set up meal prep for my household. Ask only for the preferences that will
materially change the plan, then show me 10 dinner ideas for next week.
```

## Some useful things it can do

| Goal | Try asking |
| --- | --- |
| Turn a recipe page into a reusable family recipe | `Add this recipe to my library: <URL>. Keep the source and tell me what you normalized.` |
| Plan a low-stress week | `Show me 10 dinner options, choose five with me, keep weeknight assembly under 20 minutes, and reuse ingredients intelligently.` |
| Rescue produce before it spoils | `I have spinach, peppers, cilantro, and half a cabbage. Plan the fragile ingredients first.` |
| Convert Sunday effort into fast weeknights | `Give me a 90-minute Sunday prep session for this plan, grouped to minimize dishes.` |
| Maintain an emergency dinner buffer | `Check my freezer and make sure I will still have two emergency dinners after this week.` |
| Improvise when plans collapse | `Emergency dinner: I have 12 minutes, the vegetables may be bad, and I do not want to shop.` |
| Remix a favorite without losing it | `Give me a vegan version, a child-friendly version, and a freezer-friendly version of this recipe. Keep the original unchanged.` |
| Shop once for the whole plan | `Combine the selected meals into one aisle-sorted list, subtract confirmed inventory, and show which meals use each item.` |
| Cook without scrolling through a wall of text | `Start cooking mode for tonight. Give me two short steps at a time with quantities included.` |
| Learn what actually works for the family | `We liked the flavor, the child found it spicy, and it took 10 minutes longer than expected. Remember that without banning the dish.` |

You do not have to use every feature. The skill can help with one recipe, one emergency dinner, or the complete weekly loop: **collect → plan → prep → shop → cook → learn**.

## Start with household preferences

Tell the agent the details that materially affect planning. You can add or revise them over time.

For example, this project's household prefers vegetarian and vegan dinners:

```text
Use the meal prep agent. We are two adults and one child. Keep dinners vegetarian,
make at least half vegan, avoid mushrooms, and keep weekday hands-on work under
20 minutes. We can prep for 90 minutes on Sunday.
```

The skill keeps private household data separate from its public instructions. In a local Codex or Claude Code installation, the current default is:

```text
~/.meal-prep-agent/
```

It reports the resolved absolute path before the first write, and you can request another private location. Hosted ChatGPT and mobile sessions do not use this folder on the phone. They need a user-approved persistent source, such as a connected private drive, or the skill must return portable state files for the user to retain. It must never claim that inventory or feedback was saved when durable storage is unavailable.

## Add recipes

Give the agent a recipe URL:

```text
Add this recipe to my personal library: <URL>
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

The agent distinguishes hands-on weekday assembly from passive and total elapsed time. It uses personal recipes first, then the shared starter cookbook, and clearly labels new suggestions that have not been saved. Another household can specify omnivore, pescatarian, allergy-aware, religious, cultural, medical-professional-provided, or other constraints instead.

You can lock meals you already like and regenerate only the remaining slots. Leftover nights link back to the original meal, so their ingredients are not purchased or deducted twice. Simple sides can be added directly to a meal without creating unnecessary recipe records.

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

Checked items and manually added groceries remain in place when a plan change regenerates the list.

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

Cooked history is recorded separately from ratings, so the agent can remember when a meal was last served even when nobody leaves feedback. Corrections are reversible history events rather than silent deletion.

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

## Install from GitHub

The recommended setup is one local clone with a linked skill folder. A later `git pull` then updates the instructions and shared cookbook without touching private household data.

Clone the repository once:

```sh
git clone https://github.com/bhadrip/skills.git ~/src/bhadrip-skills
```

### ChatGPT on web or mobile

If the ChatGPT account or workspace offers Skills, upload the skill from **Plugins → Skills → Create → Upload from your computer**. Availability and syncing can differ by plan, workspace, and surface. Once the skill is available in a chat, select it with `@` or make a matching request naturally.

This repository currently ships a standalone skill folder. For predictable distribution to friends using ChatGPT on iPhone, iPad, Android, or the web, the next packaging step is a plugin: OpenAI documents plugins as the installable format that carries skills across ChatGPT web, desktop, and mobile. The plugin package is not included yet.

### Codex

Install it for every Codex project on this computer:

```sh
mkdir -p ~/.agents/skills
ln -s ~/src/bhadrip-skills/meal-prep-agent ~/.agents/skills/meal-prep-agent
```

For one repository only, link or copy the folder to `.agents/skills/meal-prep-agent` inside that repository instead. Codex recognizes linked skill folders. If it does not appear immediately, restart Codex. Invoke it as `$meal-prep-agent`, select it from `/skills`, or describe a matching meal-planning request naturally.

### Claude Code

Install it for every Claude Code project on this computer:

```sh
mkdir -p ~/.claude/skills
ln -s ~/src/bhadrip-skills/meal-prep-agent ~/.claude/skills/meal-prep-agent
```

For one repository only, link or copy the folder to `.claude/skills/meal-prep-agent` inside that repository and commit it if the whole team should receive it. Claude Code recognizes linked skill folders and watches installed `SKILL.md` files for changes. Invoke it as `/meal-prep-agent`, or ask for one of the workflows in plain language.

### Claude.ai

Claude.ai accepts a ZIP archive of the skill. Build one from the clone:

```sh
git -C ~/src/bhadrip-skills archive \
  --format=zip \
  --prefix=meal-prep-agent/ \
  --output "$HOME/Downloads/meal-prep-agent.zip" \
  HEAD:meal-prep-agent
```

In Claude.ai, open **Customize → Skills**, choose **Create skill**, and upload `meal-prep-agent.zip`. Uploaded skills are copies rather than links to GitHub, so rebuild and upload a fresh ZIP when you want a newer version. Claude.ai can use the workflow and shared cookbook, but its temporary execution environment is not the default home for long-lived household data. Give it an explicitly connected private storage location or download the generated records and provide them again in a later conversation.

## Keep the skill updated

For the recommended linked installation, update the checkout:

```sh
git -C ~/src/bhadrip-skills pull --ff-only
```

Both Codex and Claude Code then read the updated skill through the link. Start a new session if an active session does not pick up all changed reference or asset files. For a copied installation, pull the repository and copy the complete `meal-prep-agent` folder over the installed copy again.

The repository currently tracks updates on its default branch. To favor reproducibility over automatic updates, pin the clone to a reviewed commit and move it forward only after checking the changes. Versioned release tags can replace commit pinning once this repository begins publishing releases.

Skill updates affect only the public instructions, schemas, examples, and shared cookbook. Personal recipes, inventory, preferences, feedback, plans, and shopping lists live separately from the installed skill, so replacing or updating it does not overwrite them.

### Maintainer update checklist

When changing the public skill:

1. Make the change through a pull request and preserve backward compatibility for household JSON where practical.
2. Update the version in `SKILL.md` metadata and record user-visible changes in [CHANGELOG.md](CHANGELOG.md).
3. Validate `SKILL.md`, the JSON schemas, local links, and representative prompts before merging.
4. Publish a GitHub release tag for stable versions. Linked installations may follow the default branch; cautious users can pin a release tag.
5. Rebuild the Claude.ai ZIP from that tag. Friends using Claude Code or Codex can pull the tag or latest branch directly.

## Why this layout works in both agents

Codex and Claude Code both use the open Agent Skills folder pattern: a `SKILL.md` entry point with optional `references/`, `assets/`, `scripts/`, and agent metadata. This skill keeps portable behavior in `SKILL.md`; Codex-specific presentation metadata in `agents/openai.yaml` is optional and does not prevent Claude from using the core skill.

Useful official examples and documentation:

- [OpenAI: Build skills for Codex](https://developers.openai.com/codex/skills)
- [OpenAI: Skills in ChatGPT](https://help.openai.com/en/articles/20001066-skills-in-chatgpt)
- [OpenAI's current Codex plugin and skill examples](https://github.com/openai/plugins)
- [Anthropic: Extend Claude with skills](https://code.claude.com/docs/en/skills)
- [Anthropic's public example-skills repository](https://github.com/anthropics/skills)
- [Claude Help: upload and manage skills in Claude.ai](https://support.claude.com/en/articles/12512180-use-skills-in-claude)
