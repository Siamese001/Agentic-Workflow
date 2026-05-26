#!/usr/bin/env bash
# Governed spine E2E: one section lane + whole apps_rg, then artifact verification.
set -euo pipefail
REPO="/mnt/c/Git/Agentic-Workflow-FRESH"
VENV="${HOME}/.cache/awf-venv-wsl"
BGE="/mnt/c/Users/amita/.cache/huggingface/hub/models--BAAI--bge-m3/snapshots/5617a9f61b028005a4858fdac845db406aefb181"
export APPS_RG_EMBEDDING_MODEL_PATH="${APPS_RG_EMBEDDING_MODEL_PATH:-$BGE}"
export CHROMA_PERSIST_DIR="${CHROMA_PERSIST_DIR:-$REPO/data/cache/chromadb}"
export VLLM_BASE_URL="${VLLM_BASE_URL:-http://localhost:8000/v1}"
export VLLM_MAX_MODEL_LEN="${VLLM_MAX_MODEL_LEN:-24576}"
export QWEN_VLLM_MODEL="${QWEN_VLLM_MODEL:-Qwen/Qwen2.5-32B-Instruct-AWQ}"
export APPS_RG_QWEN_TIMEOUT_SECONDS="${APPS_RG_QWEN_TIMEOUT_SECONDS:-120}"
export APPS_RG_VLLM_AUTO_START="${APPS_RG_VLLM_AUTO_START:-1}"
export PYTEST_DISABLE_PLUGIN_AUTOLOAD=1
cd "$REPO"
PY="${VENV}/bin/python"
if [[ ! -x "$PY" ]]; then
  export UV_CACHE_DIR="${UV_CACHE_DIR:-/tmp/uv-cache-wsl-isolated}"
  export UV_PROJECT_ENVIRONMENT="$VENV"
  uv sync --python 3.12
fi
TS="$(date -u +%Y%m%d_%H%M%S)"
PROOF_ROOT="$REPO/artifacts/apps_rg/governed_spine_e2e/$TS"
mkdir -p "$PROOF_ROOT"
COMMON=(
  --target-company "Brown & Brown"
  --target-role "SVP IT Strategy & Innovation"
  --jd apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_jd.txt
  --manual-brief apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_briefing.md
  --provider qwen_vllm
  --allow-non-allow-exit-zero
)

_run_cli() {
  # Product lanes often exit non-zero on X3 review/block; still collect artifacts.
  local log_path="$1"
  shift
  set +o pipefail
  "$@" 2>&1 | tee "$log_path"
  CLI_EXIT=${PIPESTATUS[0]}
  set -o pipefail
  return "$CLI_EXIT"
}

echo "=== [1/4] Static single-spine gate (advisory) ==="
if ! "$PY" ops_scripts/ci/check_apps_rg_single_spine.py; then
  echo "WARN: single-spine static scan reported findings (see artifacts/ci/apps_rg_single_spine_gate.json)" >&2
fi

echo "=== [2/4] Section lane: headline ==="
CLI_EXIT=0
_run_cli "$PROOF_ROOT/headline_cli.log" "$PY" -m apps_rg --section headline "${COMMON[@]}" || CLI_EXIT=$?
HEADLINE_CLI_EXIT=$CLI_EXIT
echo "headline_cli_exit=$HEADLINE_CLI_EXIT"
HEADLINE_DIR="$(
  "$PY" -c "
from pathlib import Path
root = Path('artifacts/apps_rg/runtime_proofs/headline/real')
dirs = sorted([p for p in root.iterdir() if p.is_dir()], key=lambda p: p.stat().st_mtime)
print(dirs[-1] if dirs else '')
"
)"
if [[ -z "$HEADLINE_DIR" || ! -d "$HEADLINE_DIR" ]]; then
  echo "FAIL: no headline artifact dir" >&2
  exit 1
fi
echo "headline_artifact_dir=$HEADLINE_DIR"
HEADLINE_VERIFY_EXIT=0
if ! "$PY" ops_scripts/apps_rg/verify_governed_spine_e2e.py \
  --section-dir "$HEADLINE_DIR" \
  --report "$PROOF_ROOT/headline_spine_verify.json"; then
  HEADLINE_VERIFY_EXIT=$?
  echo "headline_spine_verify_exit=$HEADLINE_VERIFY_EXIT" >&2
fi
echo "headline_spine_verify_exit=$HEADLINE_VERIFY_EXIT"

echo "=== [3/4] Whole apps_rg (integrated R4) ==="
INTEGRATED_STEP_START="$(date +%s)"
CLI_EXIT=0
_run_cli "$PROOF_ROOT/integrated_cli.log" "$PY" -m apps_rg "${COMMON[@]}" || CLI_EXIT=$?
INTEGRATED_CLI_EXIT=$CLI_EXIT
echo "integrated_cli_exit=$INTEGRATED_CLI_EXIT"
INTEGRATED_DIR="$(
  INTEGRATED_STEP_START="$INTEGRATED_STEP_START" "$PY" -c "
import os
from pathlib import Path

since = float(os.environ.get('INTEGRATED_STEP_START', '0')) - 2.0

def _newest_since(parent: Path, pattern: str) -> Path | None:
    dirs = [
        p
        for p in parent.glob(pattern)
        if p.is_dir() and p.stat().st_mtime >= since
    ]
    if not dirs:
        return None
    return max(dirs, key=lambda p: p.stat().st_mtime)

rp = Path('artifacts/apps_rg/runtime_proofs')
hit = _newest_since(rp, 'full_resume_*')
if hit:
    print(hit)
    raise SystemExit(0)
runs = Path('artifacts/apps_rg/runs')
hit = _newest_since(runs, 'cli_*')
print(hit if hit else '')
"
)"
if [[ -z "$INTEGRATED_DIR" || ! -d "$INTEGRATED_DIR" ]]; then
  echo "FAIL: no integrated run dir (expected runtime_proofs/full_resume_* or runs/cli_*)" >&2
  exit 1
fi
echo "integrated_run_dir=$INTEGRATED_DIR"
INTEGRATED_VERIFY_EXIT=0
if ! "$PY" ops_scripts/apps_rg/verify_governed_spine_e2e.py \
  --integrated-dir "$INTEGRATED_DIR" \
  --report "$PROOF_ROOT/integrated_spine_verify.json"; then
  INTEGRATED_VERIFY_EXIT=$?
fi
echo "integrated_spine_verify_exit=$INTEGRATED_VERIFY_EXIT"

echo "=== [4/4] Receipt ==="
HEADLINE_CLI_EXIT="$HEADLINE_CLI_EXIT" \
HEADLINE_VERIFY_EXIT="$HEADLINE_VERIFY_EXIT" \
INTEGRATED_CLI_EXIT="$INTEGRATED_CLI_EXIT" \
INTEGRATED_VERIFY_EXIT="$INTEGRATED_VERIFY_EXIT" \
PROOF_ROOT="$PROOF_ROOT" \
HEADLINE_DIR="$HEADLINE_DIR" \
INTEGRATED_DIR="$INTEGRATED_DIR" \
"$PY" -c "
import json
import os
from datetime import datetime, timezone
from pathlib import Path

proof = Path(os.environ['PROOF_ROOT'])
headline_verify = json.loads((proof / 'headline_spine_verify.json').read_text(encoding='utf-8'))
integrated_verify = json.loads((proof / 'integrated_spine_verify.json').read_text(encoding='utf-8'))
out = {
    'schema_version': 'governed_spine_e2e_receipt_v2',
    'generated_at_utc': datetime.now(timezone.utc).isoformat(),
    'headline_artifact_dir': os.environ['HEADLINE_DIR'].replace('\\\\', '/'),
    'integrated_run_dir': os.environ['INTEGRATED_DIR'].replace('\\\\', '/'),
    'headline_cli_exit': int(os.environ['HEADLINE_CLI_EXIT']),
    'integrated_cli_exit': int(os.environ['INTEGRATED_CLI_EXIT']),
    'headline_spine_verify_exit': int(os.environ['HEADLINE_VERIFY_EXIT']),
    'integrated_spine_verify_exit': int(os.environ['INTEGRATED_VERIFY_EXIT']),
    'headline_verify': headline_verify,
    'integrated_verify': integrated_verify,
}
spine_pass = (
    headline_verify.get('status') == 'PASS'
    and integrated_verify.get('status') == 'PASS'
)
artifacts_ok = bool(out['headline_artifact_dir']) and bool(out['integrated_run_dir'])
if spine_pass:
    out['status'] = 'PASS'
elif artifacts_ok:
    out['status'] = 'PARTIAL'
else:
    out['status'] = 'FAIL'
path = proof / 'governed_spine_e2e_receipt.json'
path.write_text(json.dumps(out, indent=2) + chr(10), encoding='utf-8')
print(path)
print('STATUS:', out['status'])
raise SystemExit(0 if out['status'] == 'PASS' else 1)
"
