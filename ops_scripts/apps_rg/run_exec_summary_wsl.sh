#!/usr/bin/env bash
set -euo pipefail
REPO="/mnt/c/Git/Agentic-Workflow-FRESH"
VENV="${HOME}/.cache/awf-venv-wsl"
BGE="/mnt/c/Users/amita/.cache/huggingface/hub/models--BAAI--bge-m3/snapshots/5617a9f61b028005a4858fdac845db406aefb181"
export APPS_RG_EMBEDDING_MODEL_PATH="${APPS_RG_EMBEDDING_MODEL_PATH:-$BGE}"
export CHROMA_PERSIST_DIR="${CHROMA_PERSIST_DIR:-$REPO/data/cache/chromadb}"
export VLLM_BASE_URL="${VLLM_BASE_URL:-http://localhost:8000/v1}"
cd "$REPO"
exec "${VENV}/bin/python" -m apps_rg \
  --section executive_summary \
  --target-company "Brown & Brown" \
  --target-role "SVP IT Strategy & Innovation" \
  --jd apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_jd.txt \
  --manual-brief apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_briefing.md
