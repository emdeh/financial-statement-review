# Chunking Approach

## Overview
heading‑agnostic chunking approach that stays robust even when financial statements use non‑standard section titles. The core idea is to split on layout and linguistic cues (page breaks → blank lines → sentence ends) and size every chunk by tokens, not characters, so it flexes automatically with different fonts or wording. This strategy is backed by recent RAG research, Azure Search guidance, and vector‑DB benchmarks.

## why

## Practical settings for 15‑20‑page PDFs
Setting	Recommended value	Rationale
chunk_tokens	300 ± 50	balances context & index size 
milvus.io
chunk_overlap	10 % (30 tokens)	prevents boundary loss without high duplication 
restack.io
Max chunks per page	4–6	keeps total vectors < 120 for 20‑page report; lowers cost ‹turn0search3›
Fallback page vectors	1 × 3072 tokens	good for rough retrieval; reduces latency 
pixion.co