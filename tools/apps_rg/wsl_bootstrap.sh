#!/usr/bin/env bash
# Bootstrap Linux venv for apps_rg when Windows Smart App Control blocks torch/.pyd.
# Uses an isolated venv on WSL ext4 (not repo .venv) so Windows uv/.venv stays untouched.
set -eu

export PATH="${HOME}/.local/bin:${PATH}"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
VENV_DIR="${APPS_RG_WSL_VENV:-${HOME}/.cache/awf-venv-wsl}"
export UV_PROJECT_ENVIRONMENT="${VENV_DIR}"

cd "${REPO_ROOT}"

if ! command -v uv >/dev/null 2>&1; then
  curl -LsSf https://astral.sh/uv/install.sh | sh
  export PATH="${HOME}/.local/bin:${PATH}"
fi

echo "==> uv sync deps only (skip editable project build on /mnt/c)"
uv sync --python 3.12 --no-install-project

TORCH_DEVICE="$(printf '%s' "${APPS_RG_WSL_TORCH_DEVICE:-auto}" | tr '[:upper:]' '[:lower:]')"
TORCH_CPU_INDEX_URL="${APPS_RG_WSL_TORCH_CPU_INDEX_URL:-https://download.pytorch.org/whl/cpu}"
TORCH_CUDA_INDEX_URL="${APPS_RG_WSL_TORCH_CUDA_INDEX_URL:-https://download.pytorch.org/whl/cu128}"

case "${TORCH_DEVICE}" in
  cpu)
    TORCH_INDEX_URL="${TORCH_CPU_INDEX_URL}"
    TORCH_LABEL="CPU"
    ;;
  cuda)
    TORCH_INDEX_URL="${TORCH_CUDA_INDEX_URL}"
    TORCH_LABEL="CUDA"
    ;;
  auto|"")
    if command -v nvidia-smi >/dev/null 2>&1; then
      TORCH_INDEX_URL="${TORCH_CUDA_INDEX_URL}"
      TORCH_LABEL="CUDA"
    else
      TORCH_INDEX_URL="${TORCH_CPU_INDEX_URL}"
      TORCH_LABEL="CPU"
    fi
    ;;
  *)
    echo "Unsupported APPS_RG_WSL_TORCH_DEVICE=${APPS_RG_WSL_TORCH_DEVICE}; expected auto, cuda, or cpu" >&2
    exit 2
    ;;
esac

echo "==> ${TORCH_LABEL} torch (override with APPS_RG_WSL_TORCH_DEVICE=cpu|cuda|auto)"
uv pip install --python "${VENV_DIR}/bin/python" torch --index-url "${TORCH_INDEX_URL}"

echo "==> import probe"
"${VENV_DIR}/bin/python" "${REPO_ROOT}/tools/apps_rg/wsl_verify_import.py"
