# Launch Qwen2.5-14B-Instruct-AWQ vLLM Server in WSL2
# Run this from PowerShell to start the vLLM server

Write-Host "Starting Qwen2.5-14B-Instruct-AWQ vLLM server in WSL2..."
Write-Host "  Model:      Qwen/Qwen2.5-14B-Instruct-AWQ"
Write-Host "  GPU util:   0.88 (stable for RTX 5090 32GB under WSL2)"
Write-Host "  Context:    16384 tokens"
Write-Host ""

# Try localhost first; if it fails, use WSL2 IP
Write-Host "Try localhost first:"
Write-Host '  $env:VLLM_BASE_URL  = "http://localhost:8000/v1"'
Write-Host '  $env:VLLM_MODEL_NAME = "Qwen/Qwen2.5-14B-Instruct-AWQ"'
Write-Host ""
Write-Host "If localhost times out, get WSL2 IP and use that instead:"
Write-Host "  wsl -d Ubuntu-24.04 -- hostname -I"
Write-Host '  $env:VLLM_BASE_URL  = "http://<wsl-ip>:8000/v1"'
Write-Host ""
Write-Host "Press Ctrl+C to stop the server."
Write-Host ""

wsl -d Ubuntu-24.04 -- bash /mnt/c/Git/Agentic-Workflow/tools/start_vllm_server.sh
