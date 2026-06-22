# AI Spending Summary Spec

## Problem Statement
Generate a monthly spending summary that explains income, expenses, budget status, and practical recommendations in plain English.

## AI Capability
- Text generation
- Summarization
- Recommendation drafting

## Success Metrics
- Factual accuracy: numeric values in the summary must match the backend transaction and budget data.
- Groundedness: the summary must stay within the provided monthly context and not invent transactions or amounts.
- Latency: the summary should return quickly enough for interactive dashboard use.
- Usefulness: the output should include a clear summary plus 2 to 3 actionable recommendations.

## Bad Output Examples
- Hallucinated numbers or categories
- Off-topic advice not related to spending or budgets
- Overly verbose text that is hard to scan
- Recommendations that ignore the current budget status

## Scope Boundary
This AI feature summarizes and explains the user's financial data. It does not replace accounting, forecasting, tax advice, or payment processing.

## Evaluation Notes
- Test the feature with months that have no transactions, low spending, high spending, and overspent budgets.
- Check that the response matches the computed totals from the backend.
- Verify that fallback output still works when the API key is missing.

## Current Implementation
- Backend endpoint: `POST /api/reports/ai-summary`
- Prompt template: `backend/prompts/monthly_spending_summary.txt`
- Model: OpenAI `gpt-4o-mini` by default, with environment override through `OPENAI_MODEL`
