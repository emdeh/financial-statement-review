## System Flow Overview
Imagine a financial statement is being reviewed. Here’s how the components interact:

### 1. Document Ingestion
1. A new financial statement (PDF) is uploaded to **Azure Blob Storage**.
2. **Event Grid** detects the new blob creation and routes the event to trigger the **Azure Function App**.

### 2. Document Processing & Validation
Once triggered, the Azure Function executes the following steps in sequence:

1. **PDF Validation**
   - Reads the first bytes of the blob to confirm the `%PDF-` header.
   - If invalid, logs `isPDF=false` to Cosmos DB and halts further processing.

2. **Page Count Extraction**
   - Uses PyPDF2 to count pages and records `pageCount`; reports anomalies (e.g. <5 or >50 pages) as warnings.

3. **Text Extraction**
   - **Embedded Text:** Attempts direct extraction via PyPDF2.
   - **OCR Fallback:** On failure or empty content, calls Azure Cognitive Services OCR.
   - Stores text in memory, segmented by page.

4. **ABN Detection**
   - Scans full text with a regex pattern for an 11‑digit Australian Business Number.
   - Records `hasABN=true` and the normalized `abn` value if found.

5. **Chunking & Embeddings Creation**
   - Splits each page into overlapping text chunks (~200–500 words) via a `ChunkService`.
   - Sends batches of chunk texts to Azure OpenAI embeddings endpoint.
   - Indexes each chunk with its vector embedding into Azure AI Search (vector index), alongside metadata (`documentName`, `page`, `chunkId`).

6. **Vector‐based Content Retrieval**
   - For each feature check (e.g. “Profit or Loss Statement”), converts the query into an embedding.
   - Runs a filtered vector search against the index, constrained by `documentName`, retrieving the top‑k most similar chunks.

7. **LLM Chat Completion**
   - Builds a prompt including the retrieved chunks and the YES/NO question.
   - Calls Azure OpenAI chat completion endpoint to obtain a precise YES/NO answer and cited page numbers.

### 3. Result Aggregation & Storage
- The Function compiles a JSON document with fields such as:
  - `isPDF`, `pageCount`, `extractionMethod`, `hasABN`, `abn`,
  - `isValidAFS`, `afsConfidence`, `hasProfitLoss`, `profitLossPages`, `blobUrl`, and timestamps.
- Securely upserts this document into **Azure Cosmos DB** using a Pydantic model for schema validation.
- Any errors or unusual metrics are emitted to **Application Insights** for monitoring.
- All secrets (keys, endpoints) are managed via **Azure Key Vault** with Managed Identity for access.

> For further information on the index schema pelase see [Creating the Search Index](/Documentation/Solution_Design/creating_the_search_index.md).

### 4. Monitoring, Feedback & Reporting
1. **Monitoring:** Application Insights captures function execution metrics (duration, failures, cold starts).
2. **Feedback Loop:** Case officers review flagged documents via a lightweight UI, providing overrides and comments.
3. **Model Retraining:** Feedback data is exported to Azure ML Workspace to retrain or fine‑tune classification models.
4. **Reporting:** Power BI dashboards connect to Cosmos DB to visualise:
   - Ingestion volumes, validation pass rates, ABN detection success,
   - AI classification accuracy over time and manual override counts.