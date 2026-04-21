# tools/vllm — Local Qwen/vLLM Server

Scripts to run the Qwen2.5-14B-Instruct-AWQ model via vLLM on a local GPU
(tested on RTX 5090 in WSL2 Ubuntu-24.04). Serves an OpenAI-compatible API
on `http://localhost:8000/v1` that all `apps_*` orchestrators consume via
`agentic_core.L3_orchestration.inference.qwen_vllm`.

## Contents

| File | Purpose |
|---|---|
| `start_vllm_server.sh` | Canonical startup (RTX 5090 tuned, float16 AWQ, 32k ctx) |
| `start_vllm_awq.sh` | Minimal AWQ config, `--enforce-eager` for debugging |
| `start_vllm_minimal.sh` | Non-quantized fallback (14B bfloat16) |
| `download_qwen_awq.sh` | Pull `Qwen/Qwen2.5-14B-Instruct-AWQ` weights from HF |
| `download_qwen.sh` | Pull `Qwen/Qwen2.5-14B-Instruct` (non-quantized) weights |
| `check_vllm.sh` | Health probe — exit 0 iff `/v1/models` returns a model |
| `vllm.service` | systemd user unit for WSL autostart |

## First-time setup

Run once inside WSL Ubuntu:

```bash
# 1. Create venv + install vLLM
python3.12 -m venv ~/.vllm_env
~/.vllm_env/bin/pip install vllm huggingface_hub hf_transfer

# 2. Download AWQ weights (~8 GiB)
bash tools/vllm/download_qwen_awq.sh

# 3. Smoke-start the server
bash tools/vllm/start_vllm_server.sh
```

## Autostart on WSL boot (optional)

```bash
mkdir -p ~/.config/systemd/user
cp tools/vllm/vllm.service ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable --now vllm.service
journalctl --user -u vllm.service -f    # tail logs
```

## Environment overrides

Code-level defaults are `http://localhost:8000/v1` and
`Qwen/Qwen2.5-14B-Instruct-AWQ`. Override via `.env`:

```
VLLM_BASE_URL=http://<wsl-ip>:8000/v1
VLLM_MODEL_NAME=Qwen/Qwen2.5-14B-Instruct-AWQ
```

All four gateway/client constructors read these env vars when no explicit
argument is passed. See `.env.example`.

## Health check

```bash
bash tools/vllm/check_vllm.sh
# → OK: vLLM serving Qwen/Qwen2.5-14B-Instruct-AWQ at http://localhost:8000/v1
```

Exit code 0 = healthy, 1 = unreachable / malformed response. Suitable for
CI smoke tests and pre-flight gates in `apps_*` orchestrators.

## Model

- **Canonical**: `Qwen/Qwen2.5-14B-Instruct-AWQ`
- Quantization: AWQ 4-bit (requires `float16`, not `bfloat16`)
- Context: 32,768 tokens
- GPU mem target: 0.90 × VRAM (≈28 GiB on RTX 5090)

Referenced from:
- `docs/architecture/qwen-vllm-topology.md`
- `agentic_core/L3_orchestration/inference/qwen_vllm/` (all four client constructors)
