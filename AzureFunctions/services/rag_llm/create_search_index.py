# scripts/create_search_index.py
import os
from azure.identity import DefaultAzureCredential
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex,
    SimpleField,
    SearchFieldDataType,
    SearchableField,
    SearchField,
    VectorSearch,
    VectorSearchAlgorithmConfiguration
)


endpoint   = os.getenv("SEARCH_ENDPOINT")
index_name = os.getenv("SEARCH_INDEX")

fields = [
    SimpleField(name="id",            type=SearchFieldDataType.String, key=True),
    SimpleField(name="documentName",  type=SearchFieldDataType.String, filterable=True),
    SimpleField(name="page",          type=SearchFieldDataType.Int32,  filterable=True),
    SearchableField(name="chunkText", type=SearchFieldDataType.String),
    SearchField(
        name="embedding",
        type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
        searchable=False,
        filterable=False,
        sortable=False,
        facetable=False,
        dimensions=1536  # match your embedding model
    )
]

vector_search = VectorSearch(
    algorithm_configurations=[
        VectorSearchAlgorithmConfiguration(name="hnsw-config", kind="hnsw")
    ]
)

index = SearchIndex(
    name=index_name,
    fields=fields,
    vector_search=vector_search
)

client = SearchIndexClient(endpoint, credential=DefaultAzureCredential())
client.create_or_update_index(index)
print(f"Index '{index_name}' is ready.")
