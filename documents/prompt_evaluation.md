# Prompt Evaluation Plan

## Goal
Check whether the monthly AI summary stays factual, useful, and concise across different finance scenarios.

## Test Set
Use at least 20 diverse monthly inputs:
- no transactions
- mostly income
- mostly expenses
- overspent budget
- under budget
- missing category
- missing note
- multiple categories with one dominant category
- recurring subscription-like spending
- travel-heavy month
- food-heavy month
- rent-dominant month
- irregular freelance income
- cash-only spending
- mixed payment methods
- month with many small transactions
- month with one large expense
- month with carry-forward budget enabled
- month with no overall budget
- month with empty or sparse notes

## Evaluation Criteria
- Accuracy: numbers in the summary match backend totals.
- Groundedness: the model does not invent spending or budget data.
- Relevance: the summary focuses on finance, not unrelated advice.
- Brevity: the response is short enough for a dashboard panel.
- Actionability: recommendations should give the user something useful to do next.

## Failure Modes
- Hallucinated totals or categories
- Recommendations that do not match the user's spending pattern
- Excessively long or vague responses
- Ignoring budget status when it is available

## Manual Review Notes
- Compare the generated text with the backend summary numbers.
- Check whether fallback output is acceptable when the LLM is unavailable.
- Record any repeated mistakes so the prompt can be revised.
