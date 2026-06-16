#!/usr/bin/env bash
# W2/W3 fresh canonical lane proof sweep (Brown & Brown targeting SSOT).
set -uo pipefail
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "${REPO}"
export PYTHONPATH="${REPO}${PYTHONPATH:+:${PYTHONPATH}}"
export AGENTIC_REPO_ROOT="${REPO}"
export HF_HOME="${HF_HOME:-/mnt/c/Users/amita/.cache/huggingface}"
export VLLM_BASE_URL="${VLLM_BASE_URL:-http://localhost:8000/v1}"
export CHROMA_PERSIST_DIR="${CHROMA_PERSIST_DIR:-${REPO}/data/cache/chromadb}"
BGE="${APPS_RG_EMBEDDING_MODEL_PATH:-}"
if [[ -z "${BGE}" ]]; then
  for d in "${HF_HOME}/hub/models--BAAI--bge-m3/snapshots"/*; do
    if [[ -f "${d}/config.json" || -f "${d}/modules.json" ]]; then
      BGE="${d}"
      break
    fi
  done
fi
export APPS_RG_EMBEDDING_MODEL_PATH="${BGE}"
# Canonical local-model lane: use already-downloaded BGE-M3 and WSL Docker vLLM.
export HF_HUB_OFFLINE="${HF_HUB_OFFLINE:-1}"
export TRANSFORMERS_OFFLINE="${TRANSFORMERS_OFFLINE:-1}"
PY="${APPS_RG_WSL_VENV:-${HOME}/.cache/awf-venv-wsl}/bin/python"
if [[ ! -x "${PY}" ]]; then
  PY=python3
fi

JD="apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_jd.txt"
BRIEF="apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_briefing.md"
LOG_DIR="${REPO}/artifacts/apps_rg/plans/w23_lane_sweep"
mkdir -p "${LOG_DIR}"
MANIFEST="${LOG_DIR}/w23_lane_sweep_manifest.json"
echo '{"lanes":[]}' > "${MANIFEST}"

run_lane() {
  local section="$1"
  local brief="$2"
  local log="${LOG_DIR}/${section}.log"
  echo "=== ${section} ===" | tee "${log}"
  set +e
  "${PY}" -m apps_rg \
    --section "${section}" \
    --target-company "Brown & Brown" \
    --target-role "SVP IT Strategy & Innovation" \
    --jd "${JD}" \
    --manual-brief "${brief}" \
    --provider qwen_vllm \
    --allow-non-allow-exit-zero \
    2>&1 | tee -a "${log}"
  local rc=$?
  set -e
  echo "${section} exit_code=${rc}" | tee -a "${log}"
  python3 -c "
import json, pathlib
m = pathlib.Path('${MANIFEST}')
doc = json.loads(m.read_text())
doc['lanes'].append({'section': '${section}', 'exit_code': ${rc}, 'log': '${log}'})
m.write_text(json.dumps(doc, indent=2) + '\n')
"
  return "${rc}"
}

OVERALL=0
run_lane unify_bullets "${BRIEF}" || OVERALL=$?
run_lane unify_narrative "${BRIEF}" || OVERALL=$?
run_lane headline "${BRIEF}" || OVERALL=$?
run_lane competencies "${BRIEF}" || OVERALL=$?
run_lane executive_summary "${BRIEF}" || OVERALL=$?
run_lane ibm_bullets "${BRIEF}" || OVERALL=$?
run_lane ibm_narrative "${BRIEF}" || OVERALL=$?

"${PY}" ops_scripts/apps_rg/proof_pool_c0_ssot_gap_audit.py | tee "${LOG_DIR}/audit.log"
exit "${OVERALL}"
echo "Manifest: ${MANIFEST}"
