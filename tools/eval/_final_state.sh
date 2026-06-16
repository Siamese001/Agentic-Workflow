#!/bin/bash
echo "=== FINAL STATE $(date) ==="
echo
echo "--- SERVING ---"
curl -sf http://localhost:8000/v1/models 2>/dev/null > /tmp/m.json
python3 <<'PY'
import json
with open("/tmp/m.json") as f:
    m = json.load(f)["data"][0]
print(f"  {m['id']}  (max_model_len={m['max_model_len']})")
PY
echo
echo "--- VRAM ---"
nvidia-smi --query-gpu=memory.used,memory.free,memory.total --format=csv,noheader
echo
echo "--- DISK ---"
df -hT ~ | tail -1
echo
echo "--- MODELS ---"
du -sh ~/models/Qwen2.5-*/ 2>/dev/null
echo
echo "--- INFERENCE LATENCY (32B-AWQ) ---"
T0=$(date +%s.%N)
curl -sf http://localhost:8000/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{"model":"Qwen/Qwen2.5-32B-Instruct-AWQ","messages":[{"role":"user","content":"In one short sentence: what is the speed of light?"}],"max_tokens":32,"temperature":0.0}' \
  > /tmp/r.json
T1=$(date +%s.%N)
python3 <<'PY'
import json
with open("/tmp/r.json") as f:
    r = json.load(f)
print(f"  reply: {r['choices'][0]['message']['content']!r}")
print(f"  completion_tokens: {r['usage']['completion_tokens']}")
PY
python3 -c "print(f'  wall_clock: {$T1 - $T0:.3f} s')"
