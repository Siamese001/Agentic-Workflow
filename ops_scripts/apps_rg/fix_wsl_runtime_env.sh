#!/usr/bin/env bash
set -euo pipefail
REPO="/mnt/c/Git/Agentic-Workflow-FRESH"
VENV="${HOME}/.cache/awf-venv-wsl"
BGE="/mnt/c/Users/amita/.cache/huggingface/hub/models--BAAI--bge-m3/snapshots/5617a9f61b028005a4858fdac845db406aefb181"
export APPS_RG_EMBEDDING_MODEL_PATH="${APPS_RG_EMBEDDING_MODEL_PATH:-$BGE}"
export CHROMA_PERSIST_DIR="${CHROMA_PERSIST_DIR:-$REPO/data/cache/chromadb}"
export VLLM_BASE_URL="${VLLM_BASE_URL:-http://localhost:8000/v1}"
export VLLM_MAX_MODEL_LEN="${VLLM_MAX_MODEL_LEN:-16384}"
export QWEN_VLLM_MODEL="${QWEN_VLLM_MODEL:-Qwen/Qwen2.5-32B-Instruct-AWQ}"
export APPS_RG_QWEN_TIMEOUT_SECONDS="${APPS_RG_QWEN_TIMEOUT_SECONDS:-120}"
export APPS_RG_VLLM_AUTO_START="${APPS_RG_VLLM_AUTO_START:-1}"
export APPS_RG_PARALLEL_PHASE1_LANES="${APPS_RG_PARALLEL_PHASE1_LANES:-1}"
export APPS_RG_PHASE1_MAX_PARALLEL="${APPS_RG_PHASE1_MAX_PARALLEL:-3}"

echo "== apps_rg WSL runtime fix =="
echo "REPO=$REPO"
echo "VENV=$VENV"
echo "BGE=$APPS_RG_EMBEDDING_MODEL_PATH"
echo "CHROMA=$CHROMA_PERSIST_DIR"
echo "VLLM=$VLLM_BASE_URL"

if [[ ! -d "$APPS_RG_EMBEDDING_MODEL_PATH" ]]; then
  echo "FAIL: BGE model path missing" >&2
  exit 1
fi

if ! curl -fsS "${VLLM_BASE_URL%/}/models" >/dev/null; then
  echo "FAIL: vLLM not healthy at $VLLM_BASE_URL (run: docker start local-qwen-vllm)" >&2
  exit 1
fi
echo "OK: vLLM /v1/models"

cd "$REPO"
if [[ ! -x "${VENV}/bin/python" ]]; then
  echo "Creating WSL venv via uv sync (first run may take several minutes)..."
  export UV_CACHE_DIR="${UV_CACHE_DIR:-/tmp/uv-cache-wsl-isolated}"
  export UV_PROJECT_ENVIRONMENT="$VENV"
  uv sync --python 3.12
fi

"${VENV}/bin/python" -c "
import torch
from sentence_transformers import SentenceTransformer
import httpx
r = httpx.get('${VLLM_BASE_URL%/}/models', timeout=10)
assert r.status_code == 200, r.status_code
print('OK: torch', torch.__version__)
print('OK: sentence_transformers import')
print('OK: apps_rg fix complete — use \$HOME/.cache/awf-venv-wsl/bin/python -m apps_rg ...')
"
