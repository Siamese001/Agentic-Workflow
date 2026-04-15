"""Step 5: Embedding model load proof — time only the model load, no query."""

import os
import sys
import time

os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TQDM_DISABLE"] = "1"

MODEL_NAME = "BAAI/bge-m3"

print(f"Model: {MODEL_NAME}")
print(f"HF_HUB_OFFLINE: {os.environ.get('HF_HUB_OFFLINE')}")
print(f"Loading (local_files_only=True)...", flush=True)

t0 = time.perf_counter()
try:
    from sentence_transformers import SentenceTransformer

    model = SentenceTransformer(MODEL_NAME, local_files_only=True)
    t1 = time.perf_counter()
    print(f"Model loaded in {t1 - t0:.2f}s")
    dim = model.get_sentence_embedding_dimension()
    print(f"Dimension: {dim}")
    print(f"max_seq_length: {model.max_seq_length}")
    print("PASS")
except (OSError, ValueError, RuntimeError) as exc:
    t1 = time.perf_counter()
    print(f"FAIL after {t1 - t0:.2f}s: {exc}", file=sys.stderr)
    sys.exit(1)
