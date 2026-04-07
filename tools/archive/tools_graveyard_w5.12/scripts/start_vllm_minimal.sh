#!/usr/bin/env bash
pkill -f vllm.entrypoints.openai.api_server 2>/dev/null || true
sleep 2

VLLM_USE_V1=0 CUDA_VISIBLE_DEVICES=0 \
  /home/amita/.vllm_env/bin/python -m vllm.entrypoints.openai.api_server \
  --model /home/amita/models/Qwen2.5-14B-Instruct \
  --served-model-name Qwen/Qwen2.5-14B-Instruct \
  --host 0.0.0.0 --port 8000 \
  --dtype bfloat16 \
  --gpu-memory-utilization 0.98 \
  --enforce-eager \
  --max-num-seqs 1 \
  --max-model-len 2048
