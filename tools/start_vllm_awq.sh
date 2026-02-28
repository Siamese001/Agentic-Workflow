#!/usr/bin/env bash
set -e
pkill -f vllm.entrypoints.openai.api_server 2>/dev/null || true
sleep 2
nvidia-smi --query-gpu=memory.free,memory.total --format=csv,noheader

/home/amita/.vllm_env/bin/python -m vllm.entrypoints.openai.api_server \
  --model /home/amita/models/Qwen2.5-14B-Instruct-AWQ \
  --served-model-name Qwen/Qwen2.5-14B-Instruct-AWQ \
  --host 0.0.0.0 --port 8000 \
  --quantization awq \
  --gpu-memory-utilization 0.88 \
  --enforce-eager \
  --max-num-seqs 16 \
  --max-model-len 16384
