# Cooking mode and feedback

## Cooking mode

Load the exact recipe record, planned batch size, relevant prepared components, and selected variation. Do not silently switch to a similarly named recipe.

Start with a compact readiness line: ingredients or components to retrieve, equipment, and any thawing or preheating that must happen first. Then present short numbered steps in execution order. Put quantities, heat level, time, and doneness cue in the step where they are used.

For interactive cooking, show one to three steps at a time and wait when the user asks to proceed stepwise. Track timers and parallel tasks explicitly. Surface substitutions only when an ingredient is missing or the user asks; state any changed timing or texture.

Finish with storage or freezer directions for planned leftovers and identify the inventory updates that should be confirmed, not assumed.

When the user confirms that the meal was cooked, append a cooked-history event even if they provide no rating. Use that durable history for “last cooked,” repetition avoidance, and later planning. If the user corrects a mistaken log, append a reversing event rather than silently deleting the original.

## Record lightweight feedback

After a meal, favor a small prompt rather than a survey. Capture whichever signals the user supplies, such as:

- overall result or 1–5 rating;
- who liked or disliked it;
- too spicy, bland, dry, rich, repetitive, or time-consuming;
- actual weekday effort;
- substitution or method used;
- whether to repeat, vary, or avoid;
- leftover and freezer outcome.

Append one event conforming to [schemas/feedback-event.schema.json](schemas/feedback-event.schema.json). Link it to both `recipe_id` and `plan_id` when known.

## Learn without overreacting

Hard constraints require explicit user intent. One negative meal does not create a permanent ban, and one positive meal does not erase an established dislike.

Update soft preferences using evidence count, recency, household member, context, and confidence. Keep the raw feedback event immutable. Examples:

- “Too spicy for the kids” updates the children's heat preference, not the adults' preference for that cuisine.
- “Great, but Tuesday took 35 minutes” lowers confidence in the recorded assembly time and suggests moving more work to weekend prep.
- “Do not serve mushrooms again” may become a hard exclusion after confirming whether it applies to the whole household.

State the inference separately from the recorded fact. When confidence is low, use the signal to diversify future options rather than exclude a recipe or ingredient.

## Close the loop

Use feedback in later plans to adjust rankings, portions, prep estimates, variation ideas, and repetition frequency. Prefer measurable corrections: update the observed assembly-time estimate, record the successful substitution, or change the serving yield. Do not rewrite the original imported method merely to reflect a one-time outcome.
