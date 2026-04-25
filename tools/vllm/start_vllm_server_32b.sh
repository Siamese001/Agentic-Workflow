#!/usr/bin/env bash
# vLLM Server Startup Script for RTX 5090 + Qwen2.5-32B-Instruct-AWQ
# 32B variant of start_vllm_server.sh. Drops max_model_len from 32k to 16k
# to leave VRAM headroom for the larger weights (~20 GB vs ~10 GB).
#
# To switch the systemd unit to this:
#   1. Stop current: systemctl --user stop vllm
#   2. Edit ~/.config/systemd/user/vllm.service:
#        ExecStart=/bin/bash /mnt/c/Git/Agentic-Workflow/tools/vllm/start_vllm_server_32b.sh
#   3. systemctl --user daemon-reload
#   4. systemctl --user start vllm

set -e

MODEL_DIR="$HOME/models/Qwen2.5-32B-Instruct-AWQ"
VENV="$HOME/.vllm_env"
PORT=8000
HOST="0.0.0.0"
GPU_UTIL=0.92        # 0.92 * 31.84 GB = 29.3 GB; 32B-AWQ weights ~20 GB + KV at 16k ~5 GB = ~26 GB used, ~3 GB headroom
MAX_MODEL_LEN=16384  # Halved from 14B's 32k to fit larger weights
DTYPE="float16"      # AWQ requires float16

if [ ! -d "$MODEL_DIR" ]; then
    echo "ERROR: Model not found at $MODEL_DIR"
    echo "Run: bash tools/vllm/download_qwen_32b_awq.sh"
    exit 1
fi

echo "Starting vLLM server (32B-AWQ)..."
echo "  Model:     $MODEL_DIR"
echo "  Port:      $PORT"
echo "  GPU util:  $GPU_UTIL"
echo "  dtype:     $DTYPE"
echo "  Context:   $MAX_MODEL_LEN tokens"
echo ""

WSL_IP=$(hostname -I | awk '{print $1}')
echo "Boundary client env vars (set in Windows):"
echo "  VLLM_BASE_URL=http://localhost:$PORT/v1  (or  http://${WSL_IP}:${PORT}/v1)"
echo "  VLLM_MODEL_NAME=Qwen/Qwen2.5-32B-Instruct-AWQ"
echo ""

$VENV/bin/python -m vllm.entrypoints.openai.api_server \
    --model "$MODEL_DIR" \
    --served-model-name "Qwen/Qwen2.5-32B-Instruct-AWQ" \
    --host "$HOST" \
    --port "$PORT" \
    --quantization awq \
    --dtype "$DTYPE" \
    --gpu-memory-utilization "$GPU_UTIL" \
    --max-model-len "$MAX_MODEL_LEN" \
    --max-num-seqs 24 \
    --enable-chunked-prefill \
    --max-num-batched-tokens 8192 \
    --disable-log-requests
