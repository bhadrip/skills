# Codex skills

Public Codex skills maintained by [bhadrip](https://github.com/bhadrip).

## Meal Prep Agent

`meal-prep-agent` manages a persistent household recipe library and the full weekly loop: importing attributed recipes from URLs, creating non-destructive variations, proposing quick dinners, planning weekend prep and freezer reserves, consolidating shopping, guiding cooking, and learning from lightweight feedback. Each family defines its own dietary preferences and constraints.

It keeps recipe, inventory, planning, shopping, cooking, and feedback concerns modular. A public, human-readable starter cookbook provides shared recipes, while personal recipes and household data remain separate. The included reference schemas define portable JSON records while shopper- and cook-facing views remain concise Markdown.

Read the [usage guide](meal-prep-agent/README.md), browse the [shared starter cookbook](meal-prep-agent/assets/shared-recipes/README.md), invoke the skill as `$meal-prep-agent`, or ask naturally for a meal plan, recipe import, freezer check, shopping list, cooking guidance, or post-meal feedback update.

## Golu Padi Designer

`golu-padi-designer` has two capabilities: create or edit a connector-aware Blender design, and plan the physical build. It generates:

- an editable Blender file;
- a portable GLB;
- a connector-aware bill of materials;
- tailored, level-by-level assembly instructions;
- an exact connector orientation map;
- a stock-pipe shopping list and optimized cut plan;
- a reusable design manifest for later edits;
- a complete tools list, including the correct PVC cutter capacity;
- four inspection renders;
- dimensional QA and export re-import validation.

The included `examples/four-step-pvc` artifact uses exact 12-inch and 36-inch tube cuts with a documented generic socket allowance.

To install only this skill, copy `golu-padi-designer` into your Codex skills directory:

```sh
git clone https://github.com/bhadrip/skills.git
cp -R skills/golu-padi-designer "${CODEX_HOME:-$HOME/.codex}/skills/"
```

Then invoke it as `$golu-padi-designer` or describe a PVC Golu display design request naturally.

## Example render

![Four-step PVC Golu padi](examples/four-step-pvc/renders/01_perspective.png)

## License

MIT. Physical builds require manufacturer-specific fitting measurements and independent structural/safety review.
