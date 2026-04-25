#!/bin/bash
# Poll the 32B-AWQ download for up to N minutes.
PID=${1:-9183}
MAX_MIN=${2:-10}
for i in $(seq 1 $MAX_MIN); do
  if ! ps -p $PID > /dev/null 2>&1; then
    echo "DONE_AT_min=$i"
    break
  fi
  T=$(date +%T)
  S=$(du -sh ~/models/Qwen2.5-32B-Instruct-AWQ/ 2>/dev/null | cut -f1)
  N=$(ls ~/models/Qwen2.5-32B-Instruct-AWQ/*.safetensors 2>/dev/null | wc -l)
  printf "[poll %2d/%d] %s size=%s shards=%d\n" $i $MAX_MIN "$T" "$S" "$N"
  sleep 60
done
echo "--- final ---"
ps -p $PID -o pid,etime= 2>/dev/null || echo "PROCESS_EXITED"
du -sh ~/models/Qwen2.5-32B-Instruct-AWQ/ 2>/dev/null
ls ~/models/Qwen2.5-32B-Instruct-AWQ/*.safetensors 2>/dev/null
