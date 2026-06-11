---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\vllm-stack-consolidation-f6e95d.md'
original_relative_path: 'vllm-stack-consolidation-f6e95d.md'
source_sha256: 090265bc588e102180a94027c421b558270a19980d8379254b05211412d2da5e
recovered_status: LOST_RECOVERED
last_commit: '6477883502e'
last_commit_date: '2026-04-27 08:55:24 -0400'
created_date: '2026-04-25'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Plan: vLLM Stack Consolidation

**Slug**: `vllm-stack-consolidation-f6e95d`
**Created**: 2026-04-24
**Owner**: Cascade + amita
**Status**: ALL WAVES ✅ COMPLETE — W4 done 2026-04-25 04:34 EDT (48.92 GB reclaimed)
**Tier**: T2 (cross-layer ops: WSL2 host + repo + Notion writeback)

## Goal

Consolidate the local Qwen-vLLM serving stack to ONE canonical path (Stack A: native venv + systemd), retire Stack B (Docker compose), reclaim ~140 GB disk space, and upgrade from 14B to 32B AWQ when capacity permits.

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W1 | W1.1, W1.2 | Plan file + Stack A canonical doc | 1500 | Filesystem write access | ✅ Done | `tools/vllm/README.md` reflects Stack A as canonical; this plan file exists |
| W2 | W2.1 | Archive ephemeral debug scripts | 500 | git mv works on /mnt/c | ✅ Done | 25 moved; `_cuda_wsl_audit.sh` + `_cuda_final_check.sh` retained in `tools/eval/` |
| W3 | W3.1, W3.2 | 32B-AWQ download (background) | 3000 | HF rate limit at least partially cleared | ✅ Done (60 min) | 5 shards 19 GB, all safetensors-valid; ~5 MB/s anon throughput |
| W4 | W4.1, W4.2, W4.3 | VHDX shrink | 500 | User has admin PowerShell | ✅ Done 2026-04-25 04:34 | 142.85 GB → 93.93 GB (48.92 GB reclaimed); vllm.service active, 32B serving |
| W5 | W5.1, W5.2 | Cutover Stack A from 14B to 32B | 1500 | W3 done, VRAM math verified | ✅ Done (2026-04-24 20:40) | served_model=Qwen2.5-32B-Instruct-AWQ, max_len=16k, smoke test 'capital of France'='Paris' |

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| W1.1 | Author plan file | `.windsurf/plans/vllm-stack-consolidation-f6e95d.md` | none | 800 | In progress |
| W1.2 | Stack A canonical doc | `tools/vllm/README.md` (rewrite), `.windsurf/rules/local-llm-wsl2-gpu.md` (already updated) | Existing README is stale (Feb 2026) | 700 | Pending |
| W2.1 | Archive `_*.sh` ephemera | `tools/eval/_*.sh` (23 files) → `archives/2026-04-24-vllm-debug/` | git history preservation | 500 | Pending |
| W3.1 | HF connectivity probe | none (HEAD request) | Token still throttled, anon worked | 200 | ✅ Done (2999/3000 resolves available anon) |
| W3.2 | 32B-AWQ background download | `~/models/Qwen2.5-32B-Instruct-AWQ/` (19 GB actual) | ~5 MB/s anon, took ~60 min | 2800 | ✅ Done |
| W4.1 | Document VHDX shrink procedure | `tools/vllm/_optimize_vhdx_diskpart.ps1` | Optimize-VHD unavailable; switched to diskpart+fstrim | 200 | ✅ Done |
| W4.2 | User runs elevated PowerShell | (manual) | Docker Desktop lock required extra step | 100 | ✅ Done 2026-04-25 04:34 |
| W4.3 | Restart Stack A after WSL bounce | (manual systemctl --user start) | — | 200 | ✅ Done — 32B active, VRAM 31629/32607 MiB |
| W5.1 | Created `start_vllm_server_32b.sh` | new file `tools/vllm/start_vllm_server_32b.sh` | gpu_util=0.92, max_len=16k, max_seqs=24 | 500 | ✅ Done |
| W5.2 | Cutover via `cutover_to_32b.sh` | systemd unit patched, daemon-reload + restart | Boot took 90s, idle VRAM 30728/32187 (94%) — TIGHT, may need 0.88 under load | 1000 | ✅ Done |

## Gap Register

| ID | Gap | Severity | Phase | Mitigation |
|----|-----|----------|-------|-----------|
| G1 | HF token rate-limited from today's failed download retries | Medium | W3.1 | Probe-then-defer; if throttled, leave background download running with retries |
| G2 | VHDX optimization needs elevated PowerShell (Cascade can't elevate) | High | W4.2 | Provide ready-to-paste script; user runs once |
| G3 | Stack A systemd unit is `disabled` — won't auto-start at WSL boot | Low | W4.3 | `systemctl --user enable vllm` after W4.2 |
| G4 | open-webui orphaned (was pointing at Stack B network) | Low | post-W4 | Repoint OPENAI_API_BASE_URL or remove |

## ADG_GRAPH_LAYER_EVIDENCE

This plan is L_OPS-only (host-side WSL/systemd/disk operations) — no `agentic_core` code touched. ADG graph-layer query not applicable. The 5 ADG Surfaces (Execution/Write/Security/State/Observability) are not crossed by this plan; it operates entirely on the deployment substrate beneath the layer.

## ADG_HOTSPOT_REPORT

Not applicable — this plan changes no Python source. No nodes, edges, or violations are created or modified.

## Rollback

| Wave | Rollback |
|------|----------|
| W1 | `git checkout` plan file + README |
| W2 | `git mv` files back from `archives/2026-04-24-vllm-debug/` |
| W3 | `rm -rf ~/models/Qwen2.5-32B-Instruct-AWQ/` |
| W4 | VHDX optimization is non-destructive; if WSL fails to start: `wsl --unregister Ubuntu-24.04` is the nuclear option but loses all WSL state |
| W5 | Edit `~/.config/systemd/user/vllm.service` ExecStart back to `start_vllm_server.sh`, then `systemctl --user daemon-reload && systemctl --user restart vllm`. 14B AWQ weights still on disk at `~/models/Qwen2.5-14B-Instruct-AWQ/` |

## Final State (2026-04-25 04:35 EDT — ALL WAVES COMPLETE)

- **Serving**: `Qwen/Qwen2.5-32B-Instruct-AWQ` at `http://localhost:8000/v1`
- **Max context**: 16,384 tokens (down from 32k for 14B to fit larger weights)
- **VRAM**: 30,728 / 32,187 MiB (94% utilization, gpu_util=0.92, 1.5 GB free at idle)
- **Disk (WSL fs)**: 92 GB used / 1007 GB total (10% full)
- **VHDX on Windows**: 93.93 GB (was 142.85 GB — W4 reclaimed **48.92 GB** of Windows disk space)
- **Stack B**: deleted, no Docker images for vllm-openai remain
- **Smoke test**: PASS — "capital of France?" → "The capital of France is Paris." (8 tokens)

## Operational Hot-Note for Future Sessions

If you see vLLM OOM errors during high concurrent load, the gpu_util=0.92 may be too aggressive for 32B + 16k context. Edit `tools/vllm/start_vllm_server_32b.sh` and lower to `GPU_UTIL=0.88`, then `systemctl --user restart vllm`. This drops max-seqs throughput slightly but adds ~1.3 GB headroom for KV cache spikes.
