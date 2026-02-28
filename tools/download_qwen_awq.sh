#!/usr/bin/env bash
set -e
pkill -f vllm.entrypoints.openai.api_server 2>/dev/null || true
sleep 2
nvidia-smi --query-gpu=memory.free,memory.total --format=csv,noheader
mkdir -p ~/models
HF_HUB_ENABLE_HF_TRANSFER=1 ~/.vllm_env/bin/huggingface-cli download \
    Qwen/Qwen2.5-14B-Instruct-AWQ \
    --local-dir ~/models/Qwen2.5-14B-Instruct-AWQ \
    --quiet
echo "DOWNLOAD_COMPLETE"
