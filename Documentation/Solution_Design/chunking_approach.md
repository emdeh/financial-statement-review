#### [Back Home](/README.md)
#### [Back to System Flow Overview](/Documentation/Solution_Design/system-flow-overview.md)

# Chunking Strategy

## Overview

The `EmbeddingService` now uses a chunking approach (`DynamicChunker`) that is **layout‑ and language‑aware, heading‑agnostic**.

The [DynamicChunker](/AzureFunctions/services/rag_llm/chunk_service.py) will chunk financial reports based on:

1. **Page breaks** (supplied by the PDF extractor)  
2. **Visual and whitespace cues**  
   * _blank‑line gaps_ that mark paragraphs  
   * _short, centred ALL‑CAPS lines_ that usually denote headings  
3. **Sentence boundaries** – handled by an adaptive, token‑based recursive splitter

Chunks are sized by **tokens, not characters**.  
The default target is **≈ 300 tokens** (≈ 220 English words) with **10 % overlap**.  
This makes the splitter resilient to font changes, layout quirks, and alternative wording (e.g.  
“Income & Expenditure” vs “Profit and Loss”).

The design is aligned with recent RAG‑search research, Microsoft guidance for Azure AI Search,
and vector‑database benchmarks.

---

## Change

| Aspect | **Old 500‑char&nbsp;/ 100‑char overlap splitter** | **New DynamicChunker** |
|--------|--------------------------------------------------|------------------------|
| Section detection | No section detection intelligence | Layout cues + sentence recursion<br>(heading‑agnostic) |
| Unit size | ~75 tokens (500 chars) – **too small**, context diluted | 300 ± 50 tokens – preserves semantic unit |
| Overlap | Fixed 100 chars regardless of chunk size | 10 % of chunk size (adaptive) |
| Metadata | `page` only | `page`, `tokens` (+ `section` optional) |
| Retrieval cost | More chunks, higher Azure Search bill | Fewer, richer chunks (≈ 30 % fewer vectors) |
| Precision / recall | Good, but prone to cut headings from tables | **Higher** – more likely to keep relevant sections in specific chunks |
| Extensibility | | Works unchanged for future naming styles |

---

## Practical Settings for 15–20‑page PDFs

| Setting | Recommended value | Rationale |
|---------|------------------|-----------|
| `CHUNK_TOKENS` | **300 ± 50** | Balances context with index size |
| `CHUNK_OVERLAP` | **0.1** (10 % overlap → ≈ 30 tokens) | Prevents boundary loss without heavy duplication |
| Max chunks per page | **4 – 6** | Keeps total vectors **\< 120** for a 20‑page report |
| Fallback page vector | **1 × 3072 tokens** | Fast coarse recall; chunk search used if score < 0.35 |

---

## Implementation Highlights

```python
chunker = DynamicChunker()              # reads env vars
for page, text in page_texts.items():
    chunks.extend(chunker.chunk_page(text, page))
```

* **Environment variables**

| Variable | Default | Purpose |
|----------|---------|---------|
| `CHUNK_TOKENS` | `300` | Target tokens per chunk |
| `CHUNK_OVERLAP` | `0.1` | Fractional overlap |
| `AZURE_OPENAI_EMBEDDING_MODEL` | `text-embedding-3-small` | Tokeniser reference |

> `CHUNK_TOKENS` and `CHUNK_OVERLAP` defined in `local.settings.json` (For development)

* **Index fields**

```
id  | documentName | page | tokens | chunkText | embedding
```

To guarantee isolation per PDF, all queries are still filtered with:  
```odata
filter=documentName eq '{escaped_name}'
```

---

### References

* Microsoft Learn – *Vector search filters & multitenancy patterns*  
* Databricks blog – *Optimal chunk sizes for RAG*  
* LangChain docs – `RecursiveCharacterTextSplitter`  

---

#### [Back to System Flow Overview](/Documentation/Solution_Design/system-flow-overview.md)
#### [Back Home](/README.md)
