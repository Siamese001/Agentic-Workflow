#!/bin/bash
date +%T
echo
echo "=== Cutover monitor PID 11574 ==="
ps -p 11574 -o pid,etime,stat 2>/dev/null || echo "  CUTOVER_DONE"
echo
echo "=== systemd vllm ==="
systemctl --user is-active vllm
echo
echo "=== /v1/models response ==="
curl -sf --max-time 5 http://localhost:8000/v1/models 2>/dev/null > /tmp/models.json
if [ -s /tmp/models.json ]; then
  $HOME/.vllm_env/bin/python <<'PY'
import json
with open("/tmp/models.json") as f:
    r = json.load(f)
m = r["data"][0]
print("served_model: ", m["id"])
print("max_model_len:", m["max_model_len"])
PY
else
  echo "  /v1/models not responding yet"
fi
echo
echo "=== cutover log tail ==="
tail -20 /tmp/wait_cutover.log
echo
echo "=== nvidia-smi VRAM ==="
nvidia-smi --query-gpu=memory.used,memory.free --format=csv,noheader
