#!/bin/bash
echo '=== nvidia-smi (live, with vLLM serving) ==='
nvidia-smi --query-gpu=name,driver_version,memory.used,memory.free,memory.total,utilization.gpu --format=csv

echo
echo '=== Compute processes ==='
nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv

echo
echo '=== torch + CUDA from inside Stack A venv ==='
~/.vllm_env/bin/python <<'PY'
import torch
print("torch=" + torch.__version__)
print("cuda_runtime=" + str(torch.version.cuda))
print("cuda_available=" + str(torch.cuda.is_available()))
print("device=" + torch.cuda.get_device_name(0))
print("CC=" + str(torch.cuda.get_device_capability(0)))
print("device_total_mem_GB=" + f"{torch.cuda.get_device_properties(0).total_memory/1e9:.2f}")
PY

echo
echo '=== End-to-end inference latency ==='
T0=$(date +%s.%N)
RESP=$(curl -sf http://localhost:8000/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{"model":"Qwen/Qwen2.5-14B-Instruct-AWQ","messages":[{"role":"user","content":"Reply with exactly: OK"}],"max_tokens":8,"temperature":0.0}')
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
