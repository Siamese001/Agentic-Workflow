#!/usr/bin/env bash
set -e
mkdir -p ~/models
~/.vllm_env/bin/pip install huggingface_hub hf_transfer -q
HF_HUB_ENABLE_HF_TRANSFER=1 ~/.vllm_env/bin/huggingface-cli download \
    Qwen/Qwen2.5-14B-Instruct \
    --local-dir ~/models/Qwen2.5-14B-Instruct \
    --exclude "*.pt" "*.bin" \
    --quiet
echo "DOWNLOAD_COMPLETE"
