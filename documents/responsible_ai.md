# Responsible AI and Deployment Notes

## Responsible AI
- The AI summary is based on computed financial data, not free-form conversation.
- The app uses a fallback summary if the API key is missing or the model call fails.
- The model should not be trusted for accounting, taxes, or legal advice.
- The UI should clearly label the feature as AI-generated.
- API keys must stay in environment variables and never be committed to source control.

## Main Limitations
- The model can still hallucinate if the prompt is weak.
- The current feature does not use RAG citations yet.
- The app uses in-memory data, so it is not production-ready for real user accounts.

## Deployment Notes
- Keep `OPENAI_API_KEY`, `OPENAI_MODEL`, and `OPENAI_BASE_URL` in local environment settings.
- Run the backend and frontend separately during development.
- Add Docker and hosted deployment later if the project needs a public demo.

## Monitoring Ideas
- Track response latency.
- Log whether the summary came from the LLM or the fallback path.
- Record prompt failures and repeated hallucination patterns.
