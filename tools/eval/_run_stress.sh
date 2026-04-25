#!/bin/bash
# Run stress test in background; print PID; exit immediately.
rm -f /tmp/stress.log /tmp/stress.json
nohup ~/.vllm_env/bin/python /mnt/c/Git/Agentic-Workflow/tools/eval/stress_test_vllm.py \
  --max-concurrency 24 --json-out /tmp/stress.json \
  > /tmp/stress.log 2>&1 < /dev/null &
PID=$!
disown
echo "stress_pid=$PID"
sleep 3
ps -p $PID -o pid,etime,cmd 2>/dev/null || echo "ALREADY_EXITED"
