#!/usr/bin/env bash
# Download Qwen2.5-32B-Instruct-AWQ (~20 GB) into ~/models/ via huggingface-cli.
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

# Use the venv's huggingface-cli (Stack A's existing env)
HFCLI=$HOME/.vllm_env/bin/huggingface-cli
if [ ! -x "$HFCLI" ]; then
  echo "Installing huggingface-cli into ~/.vllm_env..." | tee -a "$LOG"
  $HOME/.vllm_env/bin/pip install -q huggingface_hub
fi

# huggingface-cli download with --local-dir lands files directly in DEST
# (bypasses the hub-cache symlink scheme that caused W3 woes earlier today)
HF_HUB_ENABLE_HF_TRANSFER=0 \
"$HFCLI" download \
  "$MODEL_REPO" \
  --local-dir "$DEST" \
  --max-workers 4 \
  >> "$LOG" 2>&1

echo "" >> "$LOG"
echo "Finished: $(date)" >> "$LOG"

# Verify all safetensors headers
$HOME/.vllm_env/bin/python <<PY 2>&1 | tee -a "$LOG"
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
