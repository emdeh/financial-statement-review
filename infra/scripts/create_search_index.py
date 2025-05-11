"""
infra/scripts/create_search_index.py
"""

import os
from dotenv import load_dotenv
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex,
    ScoringProfile,
    TextWeights,
    TagScoringFunction,
    ScoringFunctionInterpolation,
    TagScoringParameters,
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
    SearchableField(name="chunkText", type=SearchFieldDataType.String, filterable=True,),
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

# Scoring profiles
scoring_profiles = [
    ScoringProfile(
        name="materialUncertaintyBoost",
        text_weights=TextWeights(weights={"chunkText": 1.0}),
        functions=[
            TagScoringFunction(
                field_name="chunkText",
                boost=5.0,
                interpolation=ScoringFunctionInterpolation.LINEAR,
                # The name of the scoring-parameter to supply at query time
                parameters=TagScoringParameters(tags_parameter="tags")
            )
        ]
    )
]

index = SearchIndex(
    name=index_name,
    fields=fields,
    vector_search=vector_search,
    scoring_profiles=scoring_profiles,
)

client = SearchIndexClient(endpoint, credential=AzureKeyCredential(admin_key))
client.create_or_update_index(index)
print(f"Index '{index_name}' is ready.")
