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
cd "$REPO"
if [[ ! -x "${VENV}/bin/python" ]]; then
  export UV_CACHE_DIR="${UV_CACHE_DIR:-/tmp/uv-cache-wsl-isolated}"
  export UV_PROJECT_ENVIRONMENT="$VENV"
  uv sync --python 3.12
fi
exec "${VENV}/bin/python" -m apps_rg \
  --section headline \
  --target-company "Brown & Brown" \
  --target-role "SVP IT Strategy & Innovation" \
  --jd apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_jd.txt \
  --manual-brief apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_briefing.md
