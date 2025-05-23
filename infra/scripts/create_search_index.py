"""
infra/scripts/create_search_index.py
"""

import os
from dotenv import load_dotenv
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex,
    SimpleField,
    SearchFieldDataType,
    SearchableField,
    SearchField,
    VectorSearch,
    VectorSearchProfile,
    HnswAlgorithmConfiguration,
)

# Load environment variables from .env file
load_dotenv()
endpoint = os.environ["SEARCH_ENDPOINT"]
admin_key = os.environ["SEARCH_ADMIN_KEY"]
index_name = os.environ["SEARCH_INDEX"]

client = SearchIndexClient(endpoint, credential=AzureKeyCredential(admin_key))

# 1) Delete existing index if it exists
if index_name in client.list_index_names():
    client.delete_index(index_name)  # Deletes the index and all its documents :contentReference[oaicite:2]{index=2}

# 2) Define fields and VectorSearch exactly as before
fields = [
    SimpleField(name="id",            type=SearchFieldDataType.String, key=True),
    SimpleField(name="documentName",  type=SearchFieldDataType.String, filterable=True),
    SimpleField(name="createdAt",     type=SearchFieldDataType.String, filterable=True),
    SimpleField(name="page",          type=SearchFieldDataType.Int32,  filterable=True, sortable=True), # added sortable=True
    SimpleField(name="tokens",       type=SearchFieldDataType.Int32,  filterable=True, sortable=True), # added
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
        VectorSearchProfile(
            name="hnsw-config",
            algorithm_configuration_name="hnsw-config"
        )
    ],
    algorithms=[
        HnswAlgorithmConfiguration(name="hnsw-config")
        ]
    )

index = SearchIndex(
    name=index_name,
    fields=fields,
    vector_search=vector_search
)

client = SearchIndexClient(endpoint, credential=AzureKeyCredential(admin_key))
client.create_or_update_index(index)
print(f"Index '{index_name}' is ready.")
