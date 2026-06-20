# Local LLM Runtime (WSL2/Docker) — pointer stub

> Reference-only (no enforcement hook). Demoted from the always-on surface to cut context
> (plan `always-on-rule-surface-cut-c7f3a1`). The full hardware / VRAM-budget / boot-runbook /
> known-quirks reference moved to
> [docs/reference/local-llm-wsl2-gpu-runtime.md](../../docs/reference/local-llm-wsl2-gpu-runtime.md)
> — load on demand when reasoning about the local Qwen vLLM stack.

**One-line invariant:** frame local-Qwen VRAM / model-size feasibility as **WSL2 + Docker with CUDA
passthrough** (RTX 5090, ~32 GB; 32B-AWQ is the production fit) — never from a "Windows desktop
overhead" baseline. Canonical runtime = Docker container `local-qwen-vllm` (`docker-compose.qwen.yml`).
