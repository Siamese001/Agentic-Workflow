#!/bin/bash
# Wait for download PID 9183 to finish, then run cutover_to_32b.sh.
# All output to /tmp/wait_cutover.log so the IDE doesn't truncate.
PID=9183
LOG=/tmp/wait_cutover.log
: > "$LOG"

echo "$(date +%T) Waiting for PID $PID..." | tee -a "$LOG"

# Wait up to 90 minutes
for i in $(seq 1 90); do
  if ! ps -p $PID > /dev/null 2>&1; then
    echo "$(date +%T) [min $i] PID $PID exited — download done" | tee -a "$LOG"
    break
  fi
  S=$(du -sh ~/models/Qwen2.5-32B-Instruct-AWQ/ 2>/dev/null | cut -f1)
  N=$(ls ~/models/Qwen2.5-32B-Instruct-AWQ/*.safetensors 2>/dev/null | wc -l)
  printf "%s [min %2d] size=%s shards=%d/5\n" "$(date +%T)" $i "$S" "$N" >> "$LOG"
  sleep 60
done

if ps -p $PID > /dev/null 2>&1; then
  echo "$(date +%T) TIMEOUT — PID still alive after 90 min, leaving alone" | tee -a "$LOG"
  exit 2
fi

echo "$(date +%T) === Download finished, running cutover ===" | tee -a "$LOG"
ls -la ~/models/Qwen2.5-32B-Instruct-AWQ/*.safetensors 2>/dev/null | tee -a "$LOG"
echo "" | tee -a "$LOG"

# Run cutover, capture full output
bash /mnt/c/Git/Agentic-Workflow/tools/vllm/cutover_to_32b.sh >> "$LOG" 2>&1
RC=$?
echo "$(date +%T) cutover RC=$RC" | tee -a "$LOG"
exit $RC
