# Prompt Engineering Notes

## Goal
Turn structured monthly finance data into a concise, accurate summary with recommendations.

## Prompt Approach Used
- Role prompt: the model acts as a careful personal finance assistant.
- Structured output: the model must return JSON with `summary`, `recommendations`, and `flags`.
- Negative prompt: do not invent transactions, amounts, or budgets.
- Context-limited prompt: only use the provided monthly JSON context.

## Prompt Variants to Try

### v1: Basic zero-shot prompt
- Ask the model to summarize the month and give recommendations.
- Good for a quick first pass.

### v2: Structured output prompt
- Require JSON output with exact keys.
- Better for dashboard rendering and predictable parsing.

### v3: Context-heavy prompt
- Include month totals, budget usage, and top category in the prompt.
- Better grounding and fewer hallucinations.

## Current Version
- The current prompt is stored in `backend/prompts/monthly_spending_summary.txt`.
- It already uses a role instruction, safety constraints, and a JSON output format.

## Versioning Plan
- Keep future prompt changes in the same file with a small changelog comment, or duplicate files as `v1`, `v2`, and `v3`.
- Track which prompt version performs best on the evaluation test set.

## Example Improvements
- Add a short example of a good output JSON block.
- Add a stricter instruction that each recommendation must connect to the current budget or spending pattern.
- Tune tone based on whether the month is under budget or overspent.
