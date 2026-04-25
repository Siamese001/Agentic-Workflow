#!/bin/bash
# Probe HF Hub connectivity + bandwidth for the 32B-AWQ shard download.
# Reads token from same location as Stack B's old .env if present, then ~/.cache/huggingface/token.
TOKEN=""
if [ -f ~/.cache/huggingface/token ]; then
  TOKEN=$(cat ~/.cache/huggingface/token)
fi
if [ -z "$TOKEN" ] && [ -f ~/.env ]; then
  TOKEN=$(grep '^HF_TOKEN=' ~/.env 2>/dev/null | cut -d= -f2-)
fi

URL='https://huggingface.co/Qwen/Qwen2.5-32B-Instruct-AWQ/resolve/main/model-00001-of-00005.safetensors'

echo "=== HEAD probe ==="
if [ -n "$TOKEN" ]; then
  echo "(using auth token)"
  curl -sf -I --max-time 10 -H "Authorization: Bearer $TOKEN" "$URL" 2>&1 | head -8
else
  echo "(no token — anonymous)"
  curl -sf -I --max-time 10 "$URL" 2>&1 | head -8
fi

echo ""
echo "=== Bandwidth probe (1 MB sample) ==="
T0=$(date +%s.%N)
if [ -n "$TOKEN" ]; then
  curl -sf --max-time 15 -r 0-1048576 -H "Authorization: Bearer $TOKEN" "$URL" -o /tmp/probe.bin 2>&1
else
  curl -sf --max-time 15 -r 0-1048576 "$URL" -o /tmp/probe.bin 2>&1
fi
RC=$?
T1=$(date +%s.%N)
SIZE=$(stat -c%s /tmp/probe.bin 2>/dev/null || echo 0)
ELAPSED=$(python3 -c "print(f'{$T1-$T0:.3f}')")
SPEED=$(python3 -c "print(f'{$SIZE/1024/1024/($T1-$T0):.2f}')")
echo "rc=$RC  size=${SIZE} bytes  elapsed=${ELAPSED}s  speed=${SPEED} MB/s"
rm -f /tmp/probe.bin

echo ""
echo "=== Existing 32B model? ==="
ls -la ~/models/Qwen2.5-32B-Instruct-AWQ/ 2>/dev/null | head -3 || echo "(no ~/models/Qwen2.5-32B-Instruct-AWQ yet)"
