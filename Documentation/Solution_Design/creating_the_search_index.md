# AI Search Index Schema

This document details the Azure AI Search index structure used to store and retrieve text chunk embeddings and associated metadata for financial statement validation.

---

## 1. Index Definition Script
The [`create_search_index.py`](/infra/scripts/create_search_index.py) script defines the index.

The key steps are:

```python
from azure.search.documents.indexes.models import (
    SearchIndex, SimpleField, SearchFieldDataType,
    SearchableField, SearchField, VectorSearch,
    VectorSearchProfile, HnswAlgorithmConfiguration
)

fields = [
    SimpleField(name="id", type=SearchFieldDataType.String, key=True),
    SimpleField(name="documentName", type=SearchFieldDataType.String, filterable=True),
    SimpleField(name="createdAt", type=SearchFieldDataType.String, filterable=True),
    SimpleField(name="page", type=SearchFieldDataType.Int32, filterable=True),
    SearchableField(name="chunkText", type=SearchFieldDataType.String),
    SearchField(
        name="embedding",
        type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
        searchable=True,
        vector_search_dimensions=1536,
        vector_search_profile_name="hnsw-config",
    )
]

vector_search = VectorSearch(
    profiles=[
        VectorSearchProfile(name="hnsw-config", algorithm_configuration_name="hnsw-config")
    ],
    algorithms=[
        HnswAlgorithmConfiguration(name="hnsw-config")
    ]
)

index = SearchIndex(name=index_name, fields=fields, vector_search=vector_search)
client.create_or_update_index(index)
```

---

## 2. Field Schema
| Field Name      | Type                                | Role                         | Description                                                                                       |
|-----------------|-------------------------------------|------------------------------|---------------------------------------------------------------------------------------------------|
| **id**          | `String`                            | Key                          | Unique chunk identifier (e.g. `6__394` for page 6, chunk sequence 394).                           |
| **documentName**| `String`                            | Filterable                   | Original blob path or file name; scopes searches to a single document.                           |
| **createdAt**   | `String` (ISO 8601 timestamp)       | Filterable                   | UTC timestamp when the chunk was indexed.                                                         |
| **page**        | `Int32`                             | Filterable                   | Page number within the source PDF where the chunk originates.                                     |
| **chunkText**   | `String`                            | Searchable (full-text)       | Text content of the chunk for both keyword and semantic queries.                                  |
| **embedding**   | `Collection(Single)` (float array)  | Vector-searchable            | 1536-dimensional vector representing the semantic meaning of `chunkText` (OpenAI embedding size). |

---

## 3. Vector Search Configuration
- **Algorithm:** HNSW (Hierarchical Navigable Small World)
- **Dimensions:** 1536 (must match the embedding model output)
- **Profile Name:** `hnsw-config`

Enables fast, approximate nearest-neighbor searches over high-dimensional vector data.

---

## 4. Indexing Workflow
1. **Chunk Generation:** The Function App’s `ChunkService` splits raw PDF text into overlapping chunks (200–500 words).
2. **Embedding Creation:** Chunks are batched to the Azure OpenAI embeddings endpoint, returning a 1536-dim vector per chunk.
3. **Document Indexing:** Each chunk is uploaded to AI Search with:
   - `id`, `documentName`, `page`, `chunkText`, `embedding`, `createdAt`.

---

## 5. Retrieval Workflow
1. **Query Embedding:** A query (e.g., “profit or loss statement”) is sent to the same embeddings endpoint to produce a vector.
2. **Filtered Vector Search:** Execute:

```python
results = search_client.search(
    search_text="*",  # wildcard disables lexical text ranking
    vector_queries=[vquery],
    filter=f"documentName eq '{escaped_name}'",
    top=k,
    select=["id","page","chunkText"]
)
chunks = list(results)
```

3. **Usage:** Returned chunks feed into the LLM prompt builder, enabling precise YES/NO answers with page citations.

---

This schema and workflows ensure scalable, accurate, and performant retrieval of semantically relevant text for AI-driven validation of financial statements.
