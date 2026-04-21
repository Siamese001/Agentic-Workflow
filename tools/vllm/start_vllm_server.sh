#!/usr/bin/env bash
# vLLM Server Startup Script for RTX 5090 + Qwen2.5-14B-Instruct
# Exposes OpenAI-compatible API at http://localhost:8000/v1
# Connects to existing tools/vllm_boundary_client.py (VLLM_BASE_URL=http://localhost:8000/v1)

set -e

MODEL_DIR="$HOME/models/Qwen2.5-14B-Instruct-AWQ"
VENV="$HOME/.vllm_env"
PORT=8000
HOST="0.0.0.0"
GPU_UTIL=0.90        # 0.90 * 31.84GB = 28.7GB — optimized for RTX 5090
MAX_MODEL_LEN=32768  # AWQ 4-bit: expand context window, still fits in VRAM
DTYPE="float16"      # AWQ quantization requires float16 (bfloat16 unsupported)

if [ ! -d "$MODEL_DIR" ]; then
    echo "ERROR: Model not found at $MODEL_DIR"
    echo "Run download_qwen.sh first"
    exit 1
fi

echo "Starting vLLM server..."
echo "  Model:     $MODEL_DIR"
echo "  Port:      $PORT"
echo "  GPU util:  $GPU_UTIL"
echo "  dtype:     $DTYPE"
echo "  Context:   $MAX_MODEL_LEN tokens"
echo ""
echo "Boundary client env vars (set in Windows):"
echo "  VLLM_BASE_URL=http://localhost:$PORT/v1"
echo "  VLLM_MODEL_NAME=Qwen/Qwen2.5-14B-Instruct-AWQ"
echo ""

WSL_IP=$(hostname -I | awk '{print $1}')
echo "Windows access URL: http://${WSL_IP}:${PORT}/v1"
echo "Set env: VLLM_BASE_URL=http://${WSL_IP}:${PORT}/v1"
echo ""

$VENV/bin/python -m vllm.entrypoints.openai.api_server \
    --model "$MODEL_DIR" \
    --served-model-name "Qwen/Qwen2.5-14B-Instruct-AWQ" \
    --host "$HOST" \
    --port "$PORT" \
    --quantization awq \
    --dtype "$DTYPE" \
    --gpu-memory-utilization "$GPU_UTIL" \
    --max-model-len "$MAX_MODEL_LEN" \
    --max-num-seqs 32 \
    --enable-chunked-prefill \
    --max-num-batched-tokens 8192 \
    --disable-log-requests
