#!/usr/bin/env bash
# Download Qwen2.5-32B-Instruct-AWQ (~20 GB) into ~/models/.
# Anonymous download (no token required for public AWQ repo).
# Idempotent: hf_hub_download verifies blob hashes and resumes partial files.
set -e

MODEL_REPO=Qwen/Qwen2.5-32B-Instruct-AWQ
DEST=$HOME/models/Qwen2.5-32B-Instruct-AWQ
LOG=/tmp/dl_32b_awq.log

mkdir -p "$DEST"

echo "Downloading $MODEL_REPO -> $DEST" | tee -a "$LOG"
echo "Started: $(date)" | tee -a "$LOG"
echo "" >> "$LOG"

python3 - <<PY 2>&1 | tee -a "$LOG"
import importlib.util
import subprocess
import sys

if importlib.util.find_spec("huggingface_hub") is None:
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "--user", "huggingface_hub"],
        check=True,
        timeout=300,
    )
PY

HF_HUB_ENABLE_HF_TRANSFER=0 python3 - <<PY 2>&1 | tee -a "$LOG"
from huggingface_hub import snapshot_download

path = snapshot_download(
    repo_id="$MODEL_REPO",
    local_dir="$DEST",
    max_workers=4,
)
print(f"snapshot_download={path}")
PY

echo "" >> "$LOG"
echo "Finished: $(date)" >> "$LOG"

# Verify all safetensors headers
python3 <<PY 2>&1 | tee -a "$LOG"
import struct, json, glob, os
ok = True
for p in sorted(glob.glob("$DEST/*.safetensors")):
    try:
        with open(p, "rb") as f:
            n = struct.unpack("<Q", f.read(8))[0]
            json.loads(f.read(n))
        print(f"OK  {os.path.basename(p)}  ({os.path.getsize(p)//(1024*1024)} MB)")
    except Exception as e:
        ok = False
        print(f"BAD {os.path.basename(p)}: {e}")
print("ALL_HEADERS_VALID" if ok else "VALIDATION_FAILED")
PY
