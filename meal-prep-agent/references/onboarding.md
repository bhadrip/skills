# Onboarding and household profile

Use onboarding to learn enough for a realistic personalized plan without turning the first interaction into a survey. A confirmed profile is required before saving a personalized weekly plan. It is not required for safe one-off help such as importing a recipe, brainstorming an unsaved variation, or explaining a cooking method.

## Detect first use

1. Look for `preferences/household.json` in the resolved private data location.
2. If a confirmed profile exists, summarize only relevant details and continue. Do not repeat onboarding.
3. If the profile is absent or marked draft, extract answers already present in the conversation and ask only for missing required fields.
4. If durable storage is unavailable, complete the conversation but return the confirmed profile as a portable JSON artifact and state that it was not persisted.

## Required fields

Collect these seven items before producing and saving a personalized plan:

1. **Household and usual servings:** who the meals serve and the normal recipe yield. Member names are unnecessary; use neutral labels when individual preferences matter.
2. **Hard constraints:** dietary rules, allergies or intolerances, and non-negotiable exclusions. Require an explicit answer, including `none` or `not sure`; never assume there are no allergies.
3. **Planning scope:** how many dinners to plan and, when relevant, which days.
4. **Weeknight limit:** maximum hands-on assembly time. Store passive and total elapsed limits separately only when the user supplies them.
5. **Weekend prep capacity:** whether advance prep is possible, preferred Saturday/Sunday timing, and maximum hands-on minutes. `No weekend prep` is a valid answer.
6. **Primary goal:** the outcome to optimize first, such as lower stress, lower cost, less waste, more variety, simpler shopping, nutrition guidance supplied by a professional, or building cooking confidence.
7. **Biggest difficulty:** the practical failure point, such as decision fatigue, produce spoilage, conflicting preferences, picky eaters, shopping friction, limited equipment, inconsistent schedules, or prep plans that are not completed.

The user may answer in prose. Normalize their meaning without forcing them to select fixed labels. Ask in one concise batch when that is convenient, or split the questions across at most two short turns. Never ask again for a value already supplied.

## Optional enrichment

Do not block the first plan on optional details. Ask only when they will materially change the result, or learn them from later feedback:

- favorite and disliked ingredients or cuisines;
- spice and texture preferences by household member;
- budget target and preferred stores;
- nutrition preferences that are not medical prescriptions;
- kitchen equipment and storage or freezer capacity;
- pantry staples, current inventory, and produce that should be used soon;
- preferred units, locale, and shopping-list grouping;
- repetition tolerance, leftover preferences, and preferred emergency meals.

Treat allergy, medical, religious, and ethical constraints as hard only when the user identifies them that way. Do not convert a dislike or a single feedback event into a permanent exclusion.

## Confirm and create the first win

Before saving, show a compact summary under these headings:

- Household
- Must follow
- Plan shape
- Time available
- Optimize for
- Biggest obstacles
- Optional preferences captured
- Unknowns or assumptions

Ask for confirmation or corrections. After confirmation:

1. Save `preferences/household.json` using [schemas/household-profile.schema.json](schemas/household-profile.schema.json).
2. Report where it was saved, or clearly state that it was returned but not persisted.
3. Offer at least 10 distinct dinner options matching the profile unless the user requested a different immediate next action.

## Update without re-onboarding

Treat statements such as “we no longer eat dairy,” “Fridays are takeout,” or “Sunday prep is too ambitious” as profile-update candidates. Show the proposed change and its planning impact, then confirm before changing a hard constraint or stable default. Record lightweight meal reactions as feedback first; promote them into stable preferences only with sufficient evidence or explicit instruction.

