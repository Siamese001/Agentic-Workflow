#!/bin/bash
date +%T
echo "PID 9183 state:"
ps -p 9183 -o pid,etime,stat 2>/dev/null || echo "  PROCESS_DEAD"
echo
echo "Sub-processes:"
pstree -p 9183 2>/dev/null | head -20
echo
echo "Network connections (curl/wget/python downloading):"
ss -tnp 2>/dev/null | grep -E "huggingface|xethub|cas-bridge" | head -10 || echo "  (no obvious HF connections)"
echo
echo ".incomplete file sizes:"
for f in ~/models/Qwen2.5-32B-Instruct-AWQ/.cache/huggingface/download/*.incomplete; do
  if [ -f "$f" ]; then
    SZ=$(stat -c%s "$f")
    SZ_MB=$((SZ / 1048576))
    BN=$(basename "$f" | cut -c1-30)
    echo "  ${SZ_MB} MB  ${BN}..."
  fi
done
echo
echo "Visible safetensors files:"
ls -la ~/models/Qwen2.5-32B-Instruct-AWQ/*.safetensors 2>/dev/null
