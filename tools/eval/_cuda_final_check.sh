#!/bin/bash
echo '=== nvidia-smi (live, with vLLM serving) ==='
nvidia-smi --query-gpu=name,driver_version,memory.used,memory.free,memory.total,utilization.gpu --format=csv

echo
echo '=== Compute processes ==='
nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv

echo
echo '=== Docker vLLM container ==='
docker ps --filter name=local-qwen-vllm --format '{{.Names}} {{.Status}}'

echo
echo '=== End-to-end inference latency ==='
T0=$(date +%s.%N)
RESP=$(curl -sf http://localhost:8000/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{"model":"Qwen/Qwen2.5-32B-Instruct-AWQ","messages":[{"role":"user","content":"Reply with exactly: OK"}],"max_tokens":8,"temperature":0.0}')
T1=$(date +%s.%N)
echo "$RESP" | python3 -c "
import json, sys
r = json.loads(sys.stdin.read())
print('reply:', repr(r['choices'][0]['message']['content']))
print('completion_tokens:', r['usage']['completion_tokens'])
print('prompt_tokens:', r['usage']['prompt_tokens'])
"
ELAPSED=$(python3 -c "print(f'{${T1}-${T0}:.3f}')")
echo "wall-clock: ${ELAPSED} s"
