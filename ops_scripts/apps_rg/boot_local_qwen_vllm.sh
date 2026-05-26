#!/usr/bin/env bash
# Boot local-qwen-vllm via docker-compose.qwen.yml from WSL (correct bind mount).
# Usage (from Windows): wsl bash /mnt/c/Git/Agentic-Workflow-FRESH/ops_scripts/apps_rg/boot_local_qwen_vllm.sh
# Usage (from WSL):     bash ops_scripts/apps_rg/boot_local_qwen_vllm.sh
set -euo pipefail

REPO="${REPO_ROOT:-/mnt/c/Git/Agentic-Workflow-FRESH}"
COMPOSE_FILE="${REPO}/docker-compose.qwen.yml"
CONTAINER="${APPS_RG_QWEN_VLLM_CONTAINER_NAME:-local-qwen-vllm}"
VLLM_BASE_URL="${VLLM_BASE_URL:-http://localhost:8000/v1}"
MODEL_HOST="${QWEN_MODEL_HOST_PATH:-/home/amita/models/Qwen2.5-32B-Instruct-AWQ}"
WAIT_SECS="${QWEN_BOOT_WAIT_SECONDS:-420}"
POLL_SECS="${QWEN_BOOT_POLL_SECONDS:-5}"

echo "== boot local-qwen-vllm =="
echo "REPO=$REPO"
echo "MODEL_HOST=$MODEL_HOST"
echo "VLLM=$VLLM_BASE_URL"

if [[ ! -f "${MODEL_HOST}/config.json" ]]; then
  echo "FAIL: model weights missing at ${MODEL_HOST}/config.json" >&2
  echo "Set QWEN_MODEL_HOST_PATH or download AWQ shards to ~/models/Qwen2.5-32B-Instruct-AWQ" >&2
  exit 1
fi

cd "$REPO"
export QWEN_MODEL_HOST_PATH="$MODEL_HOST"

if docker inspect "$CONTAINER" >/dev/null 2>&1; then
  state="$(docker inspect "$CONTAINER" --format '{{.State.Status}}')"
  if [[ "$state" == "running" ]]; then
    if docker exec "$CONTAINER" test -f /models/qwen/config.json 2>/dev/null; then
      if curl -fsS "${VLLM_BASE_URL%/}/models" | grep -q Qwen; then
        echo "OK: $CONTAINER already running and healthy"
        exit 0
      fi
      echo "Container running; waiting for /v1/models ..."
    else
      echo "WARN: $CONTAINER running but /models/qwen empty — recreating via compose"
      docker stop "$CONTAINER" >/dev/null || true
      docker rm "$CONTAINER" >/dev/null || true
      docker compose -f "$COMPOSE_FILE" up -d qwen-vllm
    fi
  else
    echo "Starting existing $CONTAINER ..."
    docker start "$CONTAINER" >/dev/null
  fi
else
  echo "Creating $CONTAINER via compose ..."
  docker compose -f "$COMPOSE_FILE" up -d qwen-vllm
fi

deadline=$((SECONDS + WAIT_SECS))
while (( SECONDS < deadline )); do
  if docker exec "$CONTAINER" test -f /models/qwen/config.json 2>/dev/null; then
    if curl -fsS "${VLLM_BASE_URL%/}/models" 2>/dev/null | grep -q Qwen; then
      echo "OK: /models/qwen mounted and /v1/models lists Qwen"
      docker inspect "$CONTAINER" --format 'Restart={{.HostConfig.RestartPolicy.Name}} Shm={{.HostConfig.ShmSize}}'
      exit 0
    fi
  fi
  sleep "$POLL_SECS"
done

echo "FAIL: $CONTAINER not healthy within ${WAIT_SECS}s" >&2
echo "Check: docker logs $CONTAINER --tail 40" >&2
exit 1
