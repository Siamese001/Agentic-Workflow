#!/bin/bash
# Full CUDA/WSL2/Docker GPU stack audit. Reports what's installed, what's
# detected, and any mismatches. Read-only.
echo "================================================================"
echo "                    CUDA / WSL2 / Docker GPU AUDIT"
echo "================================================================"

echo ""
echo "==================== [1] WSL distro + kernel ===================="
cat /etc/os-release | grep -E "PRETTY_NAME|VERSION_ID"
echo "kernel: $(uname -a)"
echo "wsl-version-info:"
cat /proc/version

echo ""
echo "==================== [2] NVIDIA driver (from WSL view) ===================="
nvidia-smi 2>&1 | head -20

echo ""
echo "==================== [3] nvidia-smi -q (selected fields) ===================="
nvidia-smi -q | grep -E "^(Driver Version|CUDA Version|Product Name|Persistence Mode|Compute Mode|Display Mode|Display Active|MIG Mode|Total|Used|Free)" | head -30

echo ""
echo "==================== [4] CUDA toolkit in WSL (host side) ===================="
which nvcc 2>/dev/null && nvcc --version || echo "(no nvcc on WSL host - OK, vLLM uses container's CUDA)"
ls -d /usr/local/cuda* 2>/dev/null || echo "(no /usr/local/cuda* - OK)"

echo ""
echo "==================== [5] Container CUDA via vLLM image ===================="
docker run --rm --gpus all --entrypoint bash vllm/vllm-openai:v0.11.0 -c '
echo "container cuda libs:"
ls /usr/local/cuda/lib64/libcudart.so* 2>/dev/null | head -3
echo ""
echo "nvidia-smi from inside container:"
nvidia-smi 2>&1 | head -10
echo ""
echo "torch + cuda from inside container:"
python3 -c "
import torch
print(f\"torch={torch.__version__}  cuda_available={torch.cuda.is_available()}\")
print(f\"cuda_runtime={torch.version.cuda}  device_count={torch.cuda.device_count()}\")
if torch.cuda.is_available():
    for i in range(torch.cuda.device_count()):
        p = torch.cuda.get_device_properties(i)
        print(f\"  device[{i}]: {p.name}  CC={p.major}.{p.minor}  total_mem={p.total_memory/1e9:.2f} GB\")
"
'

echo ""
echo "==================== [6] WSL .wslconfig (Windows-side) ===================="
WSL_CONF="/mnt/c/Users/$(whoami)/.wslconfig"
ALT_CONF="/mnt/c/Users/amita/.wslconfig"
for f in "$WSL_CONF" "$ALT_CONF"; do
  if [ -f "$f" ]; then
    echo "found: $f"
    cat "$f"
    break
  fi
done
[ ! -f "$WSL_CONF" ] && [ ! -f "$ALT_CONF" ] && echo "(no .wslconfig found - using defaults: 50% RAM, all cores, 25% swap)"

echo ""
echo "==================== [7] WSL2 resources (current view) ===================="
echo "CPU cores: $(nproc)"
echo "RAM (host visible to WSL):"
free -h | head -3
echo "Disk free:"
df -h ~/llm-stack 2>/dev/null | head -2

echo ""
echo "==================== [8] Docker daemon GPU support ===================="
docker info 2>&1 | grep -iE "runtimes|nvidia|gpu" | head -5
docker version --format 'docker={{.Server.Version}} api={{.Server.APIVersion}}'

echo ""
echo "==================== [9] Currently running GPU processes ===================="
nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv 2>&1 | head -10

echo ""
echo "==================== [10] vLLM container live state ===================="
docker ps --filter name=vllm --format "{{.Names}} | {{.Status}} | {{.Image}}" 2>&1 | head -3
docker logs --tail 3 vllm 2>&1 | tail -3

echo ""
echo "================================================================"
echo "                    AUDIT COMPLETE"
echo "================================================================"
