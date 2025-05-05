#### [Back Home](/README.md)

# RAG + LLM Check Pipeline — How It Works  
*(financial‑statement‑review / Azure Functions)*

This document explains how YES/NO checks (Profit‑&‑Loss, Balance Sheet, etc.)
are executed against each uploaded PDF, references source files, and highlights
optimisation opportunities.

---

## Overview

- `main.py` calls `run_llm_checks(document_name, system_prompt)`, which loops over every `chk` in the `CHECKS` list. 
- For each check it invokes `RetrievalService.ask_with_citations`, passing the current *document name, check name, question, query, k, and system prompt*. 
- Inside `ask_with_citations`, the query is embedded and sent to `retrieve_chunks`, which prefilters the Azure AI Search index on `documentName` and performs a **100 % semantic vector search**. 
- The top‑*k* chunks returned are concatenated into a prompt together with `chk.question` (derived from the `question` in the `chk` within the `CHECKS` list).
- This prompt is sent to ChatCompletion, yielding a single YES/NO answer plus cited pages. 
`run_llm_checks` converts that reply into fields like `hasProfitLoss` and `profitLossPages`, aggregates all checks into `llm_flags`, and hands the result back to `main.py`.

---

## 1 Key Source Files

| File | Purpose |
|------|---------|
| [`AzureFunctions/ProcessPDF/main.py`](/AzureFunctions/ProcessPDF/main.py) | Entry‑point; orchestrates full PDF processing. |
| [`AzureFunctions/services/rag_llm/checks_runner.py`](/AzureFunctions/services/rag_llm/check_runner.py) | Runs all checks via `run_llm_checks`. |
| [`AzureFunctions/services/rag_llm/retrieval_service.py`](/AzureFunctions/services/rag_llm/retrieval_service.py) | Retrieves chunks + builds prompts. |
| [`AzureFunctions/services/rag_llm/chunk_service.py`](/AzureFunctions/services/rag_llm/chunk_service.py) | `DynamicChunker` (300‑token splits). |
| [`AzureFunctions/services/rag_llm/embedding_service.py`](/AzureFunctions/services/rag_llm/embedding_service.py) | Embeds chunks → AI Search vectors. |

---

## 2 Logic Flow

```mermaid
graph TD
    A[Blob Trigger<br>main.py] --> B[PDF sanity checks]
    B --> C[EmbeddingService<br>DynamicChunker]
    C --> D[Azure AI Search (index)]
    D --> E[run_llm_checks]
    E --> F[retrieve_chunks]
    F --> G[ask_with_citations<br>ChatCompletion]
    G --> H[Cosmos DB save]
```

---

## 3 Step‑by‑Step Detail

### 3.1 Trigger & pre‑flight (`main.py`)

```python
llm_flags = run_llm_checks(document_name=myblob.name)
```

> Stops early for non‑PDFs or abnormal page counts.

### 3.2 Embedding

* `DynamicChunker` → ~300‑token chunks.  
* Batched (20) calls to embeddings endpoint.  
* Upload `{id, documentName, page, tokens, chunkText, embedding}` to AI Search.

### 3.3 `run_llm_checks`

Loops over `CHECKS`. For each:

1. **Vector retrieval**  
   `retrieve_chunks(document_name, chk.query, k)`<br>
   *Filter*: `documentName eq '{name}'`  
   *Search*: 100 % vector similarity on query embedding.

2. **Prompt build** (`ask_with_citations`)  
   Concatenate all returned chunks + `chk.question`.  
   Ask ChatCompletion → YES/NO + cited pages.

3. **Results**  
   Map to `hasProfitLoss`, `profitLossPages`, etc., return to `main.py`.

---

## 4 Current Query vs Question Roles

| Field in `CheckDef` | Used for | Effect |
|---------------------|----------|--------|
| `query` | Embedding + vector search | Determines **which chunks** are retrieved. |
| `question` | Chat prompt | Tells LLM **what to decide** given those chunks. |

Only the vector search uses `query`; there is **no keyword OR Boolean parsing**.

---

#### [Back Home](/README.md)