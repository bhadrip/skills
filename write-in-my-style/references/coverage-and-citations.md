# Coverage and citations

## Show the style coverage map

Use a Markdown matrix with style choices down the rows and concrete writing situations across the columns. Name the language. Label each column with the channel, audience relationship, and purpose, using generic audience labels such as teammate. Start with the situations the user writes in or wants to practice. When offering starter situations, label them as examples. Focus the rows on decisions that would affect those messages, such as opening, message order, request form, amount of context, formality, and closing.

Use the saved `coverage` report for English and add applicable evidence from the current session. Show the label and a short description of the choice when known.

| Label | Evidence |
| --- | --- |
| **Confirmed** | The user confirmed this specific choice and scope. |
| **Observed** | The choice recurs in independent, comparable examples. |
| **Broad default** | A user-confirmed preference covers this situation through a broader scope. A comparable example could tell us whether it holds here. |
| **Tentative** | One comparable sample suggests a choice. A second sample or explicit confirmation would strengthen it. |
| **Needs confirmation** | Equally relevant evidence supports different choices. |
| **Needs example** | The available evidence leaves this relevant choice open. |
| **Unavailable** | The saved store could not be read and the session supplies too little evidence to tell. |
| **—** | This choice is irrelevant for the situation. |

Prefer specific evidence to broad defaults. Display a choice from a single sample as tentative even when the user asks you to match that sample for the current draft. After the matrix, identify the next gap that matters for a message the user actually wants to write. Give one fictional scenario that would help fill it. For a conflict, ask whether the choice changes with a specific condition, such as starting a new thread. Recheck the affected cells when the user adds evidence. Report categorical coverage without an overall confidence percentage.

### Fictional coverage example

**Language** English

| Style choice | Slack · teammate · request | Email · new client · request |
| --- | --- | --- |
| Message order | **Observed** · ask then reason | **Needs example** |
| Request form | **Tentative** · could you | **Needs example** |
| Formality | **Broad default** · neutral | **Broad default** · neutral |

**Next example.** Write a short email to a fictional new client asking whether they can review a draft by Friday. Use your usual opening and put the request wherever it feels natural.

## Explain a draft

Keep the message copy-ready. Place a short **Why this wording** section below it and name the sentence, phrase, or whole-message choice each note explains. Combine related choices from the same evidence. For a sentence-by-sentence explanation, label the notes by sentence and identify any sentence shaped solely by facts or instructions in the brief.

- **Saved profile.** Cite the ID from `coverage`, such as `[P7/slack/teammate/request/message_order]`. Say what the rule records, whether it was observed or confirmed, and why the scope applies. The ID includes the revision and the rule's stored scope, which may be broader than the target context. For a situation outside the schema, use the same ID format for any applicable broad rule actually read from the profile. The store keeps the latest revision. Treat its status as the available provenance.
- **Session evidence.** Assign short IDs such as `E1` and `E2` to examples or confirmations actually used in this session. Explain the style pattern they support at the level of a rule. A single example chosen as a model can support a choice for this draft. If a provisional choice draws on an undesignated single sample, label that evidence as tentative.
- **Brief or gap.** Credit a current instruction or fact to the brief. If the user asks for a provisional draft, mark consequential unsupported choices as provisional and name what example would clarify them. Attribute specific phrasing and decisions only to sources that support them.

Use style-level summaries in notes and maps. Keep conversation content, message links, and sample IDs in the current session. The helper generates saved profile IDs from the allowed rule labels and the revision at read time.

### Fictional citation example

**Draft**

> Could you review the mockup by Thursday? I need it for Friday’s handoff.

**Why this wording**

- The request comes before the reason because that order recurred in comparable Slack requests to teammates. `[P7/slack/teammate/request/message_order]`
- “Could you” follows the wording pattern the user chose for this draft. `[E1]`
