#!/bin/bash
PID=9183
echo "Waiting for PID $PID (download_qwen_32b_awq.sh)..."
for i in $(seq 1 60); do
  if ! ps -p $PID > /dev/null 2>&1; then
    echo "[min $i] process exited"
    break
  fi
  SIZE=$(du -sh ~/models/Qwen2.5-32B-Instruct-AWQ/ 2>/dev/null | cut -f1)
  SHARDS=$(ls ~/models/Qwen2.5-32B-Instruct-AWQ/*.safetensors 2>/dev/null | wc -l)
  printf "[min %2d] size=%s shards_visible=%d/5\n" $i "$SIZE" $SHARDS
  sleep 60
done
echo
echo "=== FINAL STATE ==="
ls -la ~/models/Qwen2.5-32B-Instruct-AWQ/*.safetensors 2>/dev/null
du -sh ~/models/Qwen2.5-32B-Instruct-AWQ/ 2>/dev/null
echo
echo "=== Last 20 nohup lines ==="
tail -20 /tmp/dl_32b_awq.nohup 2>/dev/null
