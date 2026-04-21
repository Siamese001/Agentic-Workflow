#!/usr/bin/env bash
# Health probe for the local vLLM server.
# Returns exit 0 iff /v1/models responds with at least one model.
# Usage: bash tools/vllm/check_vllm.sh [base_url]

set -u

BASE_URL="${1:-${VLLM_BASE_URL:-http://localhost:8000/v1}}"
TIMEOUT="${VLLM_HEALTH_TIMEOUT:-5}"

response=$(curl -sS --max-time "$TIMEOUT" "${BASE_URL}/models" 2>&1) || {
  echo "FAIL: ${BASE_URL}/models unreachable: $response" >&2
  exit 1
}

if ! echo "$response" | grep -q '"id"'; then
  echo "FAIL: response missing model id: $response" >&2
  exit 1
fi

model=$(echo "$response" | python3 -c 'import json,sys; print(json.load(sys.stdin)["data"][0]["id"])' 2>/dev/null)
if [ -z "$model" ]; then
  echo "FAIL: could not parse model id from response" >&2
  exit 1
fi

echo "OK: vLLM serving $model at $BASE_URL"
exit 0
