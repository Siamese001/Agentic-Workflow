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

echo "==> CPU-only torch (smaller; BGE inference does not need CUDA in WSL)"
uv pip install --python "${VENV_DIR}/bin/python" torch --index-url https://download.pytorch.org/whl/cpu

echo "==> import probe"
"${VENV_DIR}/bin/python" "${REPO_ROOT}/tools/apps_rg/wsl_verify_import.py"
