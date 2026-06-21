# RAG Plan for the Finance Assistant

## What RAG Means Here
RAG means the AI summary can retrieve grounded context from saved financial data before generating the final answer.

## What Would Change
- Add embeddings for finance text or monthly transaction summaries.
- Store those embeddings in a vector database.
- Retrieve the most relevant chunks for a user question or monthly summary.
- Inject the retrieved context into the prompt before calling the model.
- Show sources or citations in the UI when possible.

## Why It Matters
- Reduces hallucinations.
- Makes the summary easier to trust.
- Helps the model stay tied to the user's actual financial data.

## Suggested MVP Path
1. Chunk monthly transaction data into short text records.
2. Generate embeddings for those records.
3. Store the embeddings in a local vector store such as Chroma or FAISS.
4. Retrieve the top matching records for the current month.
5. Feed the retrieved records into the monthly summary prompt.
6. Display the resulting AI summary and the source records used to build it.

## Good First Data Source
- Monthly transactions
- Budget records
- Category names
- Recent trend summaries

## Notes
- The current app already computes the totals in code.
- RAG would improve grounding, but it is optional for the current MVP.
- If needed later, the same flow can be extended to support chat-style questions.
