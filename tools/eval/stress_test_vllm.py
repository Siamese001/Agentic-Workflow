#!/usr/bin/env python3
"""
Stress test for the local Qwen2.5-32B-Instruct-AWQ via vLLM OpenAI API.

Measures:
  - Throughput (tokens/sec) at increasing concurrency
  - p50 / p95 / p99 first-token latency (TTFT)
  - p50 / p95 / p99 total latency
  - Output tokens/sec per stream
  - VRAM peak via nvidia-smi sampling
  - OOM detection

Run inside WSL with the venv:
  ~/.vllm_env/bin/python /mnt/c/Git/Agentic-Workflow/tools/eval/stress_test_vllm.py
"""

from __future__ import annotations

from agentic_core.config.model_catalog import (
    QWEN_LOCAL_MODEL_ID,
)

import argparse
import asyncio
import json
import statistics
import subprocess
import sys
import time
from dataclasses import dataclass, field
from typing import Any

import aiohttp


BASE_URL = "http://localhost:8000/v1"
MODEL = QWEN_LOCAL_MODEL_ID

# Three prompt classes: short / medium / long, each with a target output size.
PROMPT_CLASSES = [
    (
        "short",
        "What is 2+2? Reply with just the number.",
        16,
    ),
    (
        "medium",
        "Explain in 3 sentences why the sky appears blue during the day but red at sunset. "
        "Be precise about Rayleigh scattering and wavelength.",
        128,
    ),
    (
        "long",
        "Write a clear technical explanation (about 400 tokens) of how a GPU executes a "
        "transformer attention layer: include matmul shapes for Q/K/V, softmax stability, "
        "KV-cache layout, and how AWQ 4-bit quantization changes the GEMM kernel choice.",
        512,
    ),
]


@dataclass
class StreamResult:
    klass: str
    ok: bool
    ttft_s: float = 0.0
    total_s: float = 0.0
    out_tokens: int = 0
    error: str = ""


@dataclass
class GpuSample:
    t: float
    used_mib: int
    util_pct: int


def sample_gpu_once() -> GpuSample:
    p = subprocess.run(
        [
            "nvidia-smi",
            "--query-gpu=memory.used,utilization.gpu",
            "--format=csv,noheader,nounits",
        ],
        capture_output=True,
        text=True,
        timeout=5,
        check=False,
    )
    line = p.stdout.strip().split("\n")[0]
    used, util = (int(x.strip()) for x in line.split(","))
    return GpuSample(time.time(), used, util)


async def gpu_sampler(stop_evt: asyncio.Event, samples: list[GpuSample]) -> None:
    while not stop_evt.is_set():
        try:
            samples.append(sample_gpu_once())
        except (subprocess.TimeoutExpired, ValueError, OSError) as exc:
            print(f"  [gpu] sample failed: {exc}", file=sys.stderr)
        await asyncio.sleep(0.5)


async def one_stream(
    session: aiohttp.ClientSession,
    klass: str,
    prompt: str,
    max_tokens: int,
) -> StreamResult:
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": 0.0,
        "stream": True,
    }
    t0 = time.time()
    ttft = 0.0
    out_toks = 0
    try:
        async with session.post(
            f"{BASE_URL}/chat/completions",
            json=payload,
            timeout=aiohttp.ClientTimeout(total=300),
        ) as resp:
            if resp.status != 200:
                body = await resp.text()
                return StreamResult(klass, False, error=f"HTTP {resp.status}: {body[:120]}")
            async for raw in resp.content:
                if not raw:
                    continue
                line = raw.decode("utf-8", errors="ignore").strip()
                if not line.startswith("data: "):
                    continue
                data = line[6:]
                if data == "[DONE]":
                    break
                try:
                    chunk = json.loads(data)
                except json.JSONDecodeError:
                    continue
                delta = chunk.get("choices", [{}])[0].get("delta", {})
                if delta.get("content"):
                    if ttft == 0.0:
                        ttft = time.time() - t0
                    out_toks += 1
        total = time.time() - t0
        return StreamResult(klass, True, ttft, total, out_toks)
    except (aiohttp.ClientError, asyncio.TimeoutError) as exc:
        return StreamResult(klass, False, error=f"{type(exc).__name__}: {exc}")


async def run_wave(concurrency: int, label: str) -> dict[str, Any]:
    print(f"\n=== Wave: {label}  concurrency={concurrency} ===")
    samples: list[GpuSample] = []
    stop_evt = asyncio.Event()
    sampler_task = asyncio.create_task(gpu_sampler(stop_evt, samples))

    async with aiohttp.ClientSession() as session:
        tasks = []
        for i in range(concurrency):
            klass, prompt, max_tok = PROMPT_CLASSES[i % len(PROMPT_CLASSES)]
            tasks.append(one_stream(session, klass, prompt, max_tok))
        t0 = time.time()
        results = await asyncio.gather(*tasks)
        wall = time.time() - t0

    stop_evt.set()
    await sampler_task

    ok = [r for r in results if r.ok]
    bad = [r for r in results if not r.ok]
    total_out = sum(r.out_tokens for r in ok)
    if ok:
        ttfts = sorted(r.ttft_s for r in ok)
        totals = sorted(r.total_s for r in ok)
        per_stream_tps = [r.out_tokens / r.total_s for r in ok if r.total_s > 0]

        def pct(arr: list[float], q: float) -> float:
            if not arr:
                return 0.0
            idx = max(0, min(len(arr) - 1, int(round(q * (len(arr) - 1)))))
            return arr[idx]

        agg: dict[str, Any] = {
            "wall_s": round(wall, 3),
            "ok": len(ok),
            "fail": len(bad),
            "out_tokens_total": total_out,
            "agg_tok_per_s": round(total_out / wall, 1) if wall > 0 else 0,
            "ttft_p50_s": round(pct(ttfts, 0.50), 3),
            "ttft_p95_s": round(pct(ttfts, 0.95), 3),
            "ttft_p99_s": round(pct(ttfts, 0.99), 3),
            "total_p50_s": round(pct(totals, 0.50), 3),
            "total_p95_s": round(pct(totals, 0.95), 3),
            "per_stream_tok_per_s_mean": (round(statistics.mean(per_stream_tps), 1) if per_stream_tps else 0),
        }
    else:
        agg = {"wall_s": round(wall, 3), "ok": 0, "fail": len(bad)}

    if samples:
        used_peak = max(s.used_mib for s in samples)
        used_mean = round(statistics.mean(s.used_mib for s in samples))
        util_peak = max(s.util_pct for s in samples)
        util_mean = round(statistics.mean(s.util_pct for s in samples))
        agg["vram_peak_mib"] = used_peak
        agg["vram_mean_mib"] = used_mean
        agg["gpu_util_peak_pct"] = util_peak
        agg["gpu_util_mean_pct"] = util_mean
    else:
        agg["vram_peak_mib"] = 0
        agg["gpu_util_peak_pct"] = 0

    if bad:
        agg["errors_sample"] = [b.error for b in bad[:3]]

    print(f"  ok={agg.get('ok', 0)} fail={agg.get('fail', 0)}  wall={agg['wall_s']}s")
    print(
        f"  agg_throughput={agg.get('agg_tok_per_s', 0)} tok/s   "
        f"per_stream_mean={agg.get('per_stream_tok_per_s_mean', 0)} tok/s"
    )
    print(
        f"  TTFT  p50={agg.get('ttft_p50_s', 0)}s  "
        f"p95={agg.get('ttft_p95_s', 0)}s  p99={agg.get('ttft_p99_s', 0)}s"
    )
    print(f"  total p50={agg.get('total_p50_s', 0)}s  p95={agg.get('total_p95_s', 0)}s")
    print(
        f"  VRAM peak={agg.get('vram_peak_mib', 0)} MiB   "
        f"GPU util peak={agg.get('gpu_util_peak_pct', 0)}%   "
        f"util mean={agg.get('gpu_util_mean_pct', 0)}%"
    )
    if bad:
        print(f"  errors: {agg['errors_sample']}")
    return {"label": label, "concurrency": concurrency, **agg}


async def main_async(args: argparse.Namespace) -> None:
    print("=== Pre-flight ===")
    pre = sample_gpu_once()
    print(f"  idle VRAM={pre.used_mib} MiB  util={pre.util_pct}%")

    waves = [
        (1, "warmup_c1"),
        (2, "low_c2"),
        (4, "med_c4"),
        (8, "high_c8"),
        (16, "stress_c16"),
        (24, "max_c24"),
    ]
    if args.max_concurrency:
        waves = [w for w in waves if w[0] <= args.max_concurrency]

    all_results = [{"label": "idle", "vram_idle_mib": pre.used_mib}]
    for c, lbl in waves:
        try:
            r = await run_wave(c, lbl)
            all_results.append(r)
        except (aiohttp.ClientError, OSError) as exc:
            print(f"  WAVE FAILED: {exc}", file=sys.stderr)
            all_results.append({"label": lbl, "concurrency": c, "wave_failed": str(exc)})
        await asyncio.sleep(2)  # cooldown

    print("\n=== Settling ===")
    await asyncio.sleep(5)
    post = sample_gpu_once()
    print(f"  post-test VRAM={post.used_mib} MiB  util={post.util_pct}%")
    all_results.append({"label": "post", "vram_post_mib": post.used_mib})

    if args.json_out:
        with open(args.json_out, "w", encoding="utf-8") as f:
            json.dump(all_results, f, indent=2)
        print(f"\nResults written to {args.json_out}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-concurrency", type=int, default=24)
    ap.add_argument("--json-out", default="/tmp/stress_results.json", help="JSON output path")
    args = ap.parse_args()

    try:
        asyncio.run(main_async(args))
    except KeyboardInterrupt:
        print("\nInterrupted.", file=sys.stderr)
        return 130
    return 0


if __name__ == "__main__":
    sys.exit(main())
