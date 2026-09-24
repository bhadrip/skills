# Open recipe sources

Use external collections as lookup sources. Search them when a user wants broader cultural coverage, a traditional dish, or more ideas, then summarize relevant options and link to the original pages.

Do not vendor, mirror, scrape into the repository, or bulk-import recipes from these collections—even when their licenses permit reuse. The point of these references is to help the agent know where to look, not to create a second copy.

## Recommended starting points

- **[Wikibooks Cookbook](https://en.wikibooks.org/wiki/Cookbook:Recipes)** — thousands of community recipes across cuisines, diets, ingredients, and techniques. Search it on demand, summarize what looks useful, and send the user to the exact recipe page. Do not copy its catalog or recipe text into this repository.
- **[Recipe Commons OpenRecipe](https://github.com/recipecommons/openrecipe-spec)** — a public-domain Markdown specification and schema for portable, Git-friendly recipe books. It is a format, not a large recipe collection. Consider exporting the public cookbook to this format when interoperability matters.
- **[TheMealDB](https://themealdb.com/docs_api_guide.php)** — a structured API with recipes and area categories. Use official API endpoints, preserve attribution, and re-check its [usage terms](https://themealdb.com/terms_of_use.php) before redistributing or building a published app.
- **[World Wide Dishes](https://github.com/oxai/world-wide-dishes)** — a research dataset centered on culturally grounded dish knowledge and geographic coverage. It is valuable for discovering representation gaps and dish names, but entries may link to third-party recipes and media with different licenses. Treat linked content separately.

## Sources requiring caution

Large GitHub recipe dumps often contain material scraped from commercial sites. A repository's code license does not automatically license the recipe text or images it contains. Do not bulk-copy a collection unless each record has usable provenance and publication rights.

Prefer records that include source URL, author or organization, content license, retrieval date, and stable ID. Keep `discovery source`, `recipe source`, and `image source` distinct because their licenses may differ.

## Lookup policy

For discovery requests, return dish names, a short reason each result may fit, and direct source links. Load and normalize a full external recipe only when the user explicitly invokes the separate personal “add this URL to my library” feature. That personal import stays in private household storage and is never promoted automatically to the public cookbook.

The public shared cookbook accepts only recipes created specifically for this project or explicitly contributed for publication. Never publish source photos without explicit reusable-image rights.
