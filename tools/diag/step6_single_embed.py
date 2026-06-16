"""Step 6: Single embedding proof — time one encode call only."""

from agentic_core.config.model_catalog import (
    BGE_M3_MODEL_ID,
)

import os
import time

os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TQDM_DISABLE"] = "1"

MODEL_NAME = BGE_M3_MODEL_ID
QUERY = "How do AI systems implement deterministic response caching with policy-key short-circuit routing to avoid redundant LLM inference?"

from sentence_transformers import SentenceTransformer

print(f"Loading {MODEL_NAME}...", flush=True)
t0 = time.perf_counter()
model = SentenceTransformer(MODEL_NAME, local_files_only=True)
t_load = time.perf_counter() - t0
print(f"Model loaded in {t_load:.2f}s", flush=True)

print(f"\nEncoding single query ({len(QUERY)} chars)...", flush=True)
t1 = time.perf_counter()
emb = model.encode([QUERY], normalize_embeddings=True, show_progress_bar=False)
t_encode = time.perf_counter() - t1

dim = emb.shape[1] if len(emb.shape) > 1 else len(emb[0])
print(f"Encode time: {t_encode:.3f}s")
print(f"Output shape: {emb.shape}")
print(f"Dimension: {dim}")
print(f"dim_match_1024: {dim == 1024}")
print(f"First 5 values: {emb[0][:5].tolist()}")
print("PASS" if dim == 1024 else "FAIL: wrong dimension")
