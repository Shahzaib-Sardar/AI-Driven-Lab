# Model Comparison and Justification

## Goal
Choose a language model that can generate short monthly spending summaries with low latency and manageable cost.

## Compared Options

### GPT-4o / GPT-4.1
- Strengths: strongest reasoning, best instruction following, very good writing quality.
- Tradeoffs: higher cost and usually more latency than smaller models.
- Best for: high-stakes reports, complex analysis, or polished final outputs.

### GPT-4o-mini
- Strengths: low latency, lower cost, good quality for structured summaries and recommendations.
- Tradeoffs: slightly weaker reasoning than the larger GPT-4 family.
- Best for: dashboard assistants, short summaries, and interactive MVP features.

### Claude Sonnet / Opus
- Strengths: strong long-form writing and safety behavior.
- Tradeoffs: different vendor integration and pricing profile.
- Best for: long, nuanced responses or safety-focused workflows.

### Gemini
- Strengths: large context and multimodal capabilities.
- Tradeoffs: extra integration choices and pricing considerations.
- Best for: large-context tasks or multimodal applications.

### Open-source models like Llama or Mistral
- Strengths: self-hosting and more control over data.
- Tradeoffs: more infrastructure work and usually more setup effort.
- Best for: offline or privacy-heavy deployments.

## Justification for GPT-4o-mini
- The feature only needs a concise monthly summary, not deep multi-step reasoning.
- The dashboard should respond quickly, so latency matters more than using a very large model.
- The app already computes the financial totals in code, so the model mainly turns structured context into natural language.
- The lower cost makes it practical to test and demo repeatedly.
- A fallback summary is already available if the API key is missing, which makes the feature more reliable during development.

## Final Choice
Use OpenAI `gpt-4o-mini` as the default model for the monthly spending summary feature, with the option to override it through `OPENAI_MODEL`.
