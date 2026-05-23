#!/usr/bin/env bash
# Run `python -m apps_rg` from WSL to avoid Windows Smart App Control blocking .pyd wheels.
set -eu

export PATH="${HOME}/.local/bin:${PATH}"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
VENV_DIR="${APPS_RG_WSL_VENV:-${HOME}/.cache/awf-venv-wsl}"
PY="${VENV_DIR}/bin/python"
cd "${REPO_ROOT}"

if [[ ! -x "${PY}" ]]; then
  echo "WSL venv missing at ${VENV_DIR}; run: bash tools/apps_rg/wsl_bootstrap.sh" >&2
  exit 2
fi

export APPS_RG_WINDOWS_SAC_DELEGATED=1
# Repo on PYTHONPATH (no slow editable install on /mnt/c).
export PYTHONPATH="${REPO_ROOT}${PYTHONPATH:+:${PYTHONPATH}}"
export AGENTIC_REPO_ROOT="${REPO_ROOT}"
export HF_HOME="${HF_HOME:-/mnt/c/Users/amita/.cache/huggingface}"
export CHROMA_PERSIST_DIR="${CHROMA_PERSIST_DIR:-${REPO_ROOT}/data/cache/chromadb}"
export VLLM_BASE_URL="${VLLM_BASE_URL:-http://localhost:8000/v1}"
export HF_HUB_OFFLINE="${HF_HUB_OFFLINE:-1}"
export TRANSFORMERS_OFFLINE="${TRANSFORMERS_OFFLINE:-1}"

BGE_SNAP="${APPS_RG_EMBEDDING_MODEL_PATH:-}"
if [[ -z "${BGE_SNAP}" ]]; then
  for d in "${HF_HOME}/hub/models--BAAI--bge-m3/snapshots"/*; do
    if [[ -f "${d}/config.json" || -f "${d}/modules.json" ]]; then
      export APPS_RG_EMBEDDING_MODEL_PATH="${d}"
      break
    fi
  done
fi

exec "${PY}" -m apps_rg "$@"
