"""Dueling-LLM eval-data synthesizer (W2.4 + F3 follow-up).

Generates multi-turn conversational eval data by pairing two LLM personas
(``user`` and ``agent_under_test``) per Google Cloud recommendation. LLM
calls are delegated to an injectable gateway port so the default CI mode
remains hermetic (no outbound calls) while production runs can wire the
real ``SovereignLLMGateway`` without changing the caller.

Modes:
  - ``--gateway-mode mock`` (default) — deterministic templated turns.
    Hermetic; safe for CI and for first-run dataset bootstrap.
  - ``--gateway-mode real`` — requires a ``GatewayPort`` implementation to
    be wired via ``--gateway-factory`` (Python dotted path). The factory
    must return an object satisfying ``GatewayPort.generate``. Capability
    tokens, budgets, circuit breakers, and telemetry all live inside the
    underlying ``SovereignLLMGateway``.

Invariants:
  - Deterministic given a seed + persona spec hash when in ``mock`` mode.
  - All generated conversations enter the golden queue with
    ``gold_outcome: "pending"``.
  - No live runtime state is touched; this tool only writes to
    ``data/eval/golden/**``.
  - ``real`` mode never runs without an explicit factory import path, so
    CI cannot accidentally issue outbound LLM calls.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import logging
import random
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Protocol

logger = logging.getLogger(__name__)


class GatewayPort(Protocol):
    """Minimal port for dueling-LLM generation.

    Implementations MUST be pure w.r.t. (system_prompt, user_prompt, seed,
    max_tokens, temperature) inputs — any IO-bound variation is the
    responsibility of the underlying gateway and its circuit breaker.
    """

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        *,
        seed: int,
        max_tokens: int = 512,
        temperature: float = 0.0,
    ) -> str: ...


class _MockGateway:
    """Deterministic mock; used whenever ``--gateway-mode mock``."""

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        *,
        seed: int,
        max_tokens: int = 512,
        temperature: float = 0.0,
    ) -> str:
        digest = hashlib.sha256(f"{system_prompt}|{user_prompt}|{seed}".encode("utf-8")).hexdigest()[:8]
        return f"[mock:{digest}] {user_prompt[:80]}"


def _load_gateway_factory(dotted: str) -> GatewayPort:
    """Import ``pkg.module:callable`` and call it to obtain a gateway."""
    if ":" not in dotted:
        raise ValueError(f"factory must be 'pkg.module:callable', got {dotted!r}")
    module_path, attr = dotted.split(":", 1)
    module = importlib.import_module(module_path)
    factory = getattr(module, attr)
    gateway = factory()
    if not hasattr(gateway, "generate"):
        raise TypeError(f"factory {dotted!r} returned object without .generate()")
    return gateway  # type: ignore[return-value]


@dataclass(frozen=True, slots=True)
class PersonaSpec:
    name: str
    style: str
    goal: str


@dataclass(frozen=True, slots=True)
class SynthesizedTurn:
    role: str
    content: str


def _persona_hash(user: PersonaSpec, agent: PersonaSpec) -> str:
    payload = json.dumps({"user": asdict(user), "agent": asdict(agent)}, sort_keys=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:12]


def _persona_system_prompt(persona: PersonaSpec) -> str:
    return (
        f"You are '{persona.name}'. Style: {persona.style}. "
        f"Goal: {persona.goal}. Stay in character and keep turns concise."
    )


def synthesize_conversation(
    user: PersonaSpec,
    agent: PersonaSpec,
    turns: int,
    seed: int,
    gateway: GatewayPort | None = None,
) -> list[SynthesizedTurn]:
    """Generate a multi-turn user↔agent conversation.

    The ``gateway`` parameter is the single seam for LLM calls. When None,
    a hermetic ``_MockGateway`` is used so CI and tests never hit the
    network. Callers running in production wire the real
    ``SovereignLLMGateway`` (via a factory) to get audited, capability-
    gated generations.
    """
    gw: GatewayPort = gateway or _MockGateway()
    rng = random.Random(seed)
    history: list[SynthesizedTurn] = []
    for turn_idx in range(turns):
        speaker = "user" if turn_idx % 2 == 0 else "agent"
        persona = user if speaker == "user" else agent
        turn_seed = rng.randint(0, 1_000_000)
        prior = " | ".join(f"{h.role}: {h.content}" for h in history[-4:])
        user_prompt = (
            f"Turn {turn_idx}. Prior (last 4): {prior or '(none)'}. "
            f"Advance the conversation toward the goal in one short message."
        )
        content = gw.generate(
            system_prompt=_persona_system_prompt(persona),
            user_prompt=user_prompt,
            seed=turn_seed,
            temperature=0.0,
        )
        history.append(SynthesizedTurn(role=speaker, content=content))
    return history


def write_conversation(
    conv: list[SynthesizedTurn],
    golden_root: Path,
    rubric_family: str,
    rubric_id: str,
    user: PersonaSpec,
    agent: PersonaSpec,
    now_iso: str,
) -> Path:
    item_id = f"synth-{rubric_id}-{_persona_hash(user, agent)}"
    target = golden_root / rubric_family / rubric_id / f"{item_id}.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "item_id": item_id,
        "rubric_id": rubric_id,
        "conversation": [asdict(t) for t in conv],
        "generator": "dueling_llm_synth",
        "personas": {"user": asdict(user), "agent": asdict(agent)},
        "human_labels": [],
        "gold_score": None,
        "gold_outcome": "pending",
        "created_at": now_iso,
    }
    with target.open("w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, sort_keys=True)
    return target


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rubric-family", required=True)
    parser.add_argument("--rubric-id", required=True)
    parser.add_argument("--turns", type=int, default=6)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--user-style", default="curious")
    parser.add_argument("--agent-style", default="concise")
    parser.add_argument("--user-goal", default="verify coverage of edge case")
    parser.add_argument("--agent-goal", default="answer grounded in context")
    parser.add_argument("--golden-root", type=Path, default=Path("data/eval/golden"))
    parser.add_argument("--now", default="2026-04-23T00:00:00Z")
    parser.add_argument("--gateway-mode", choices=["mock", "real"], default="mock",
                        help="'mock' (hermetic default) or 'real' (requires --gateway-factory)")
    parser.add_argument("--gateway-factory", default=None,
                        help="dotted path 'pkg.module:callable' returning a GatewayPort; required for real mode")
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, stream=sys.stderr, format="%(levelname)s %(name)s: %(message)s")

    gateway: GatewayPort
    if args.gateway_mode == "real":
        if not args.gateway_factory:
            logger.error("--gateway-mode real requires --gateway-factory pkg.module:callable")
            return 2
        gateway = _load_gateway_factory(args.gateway_factory)
        logger.info("loaded real gateway via %s", args.gateway_factory)
    else:
        gateway = _MockGateway()

    user = PersonaSpec(name="user", style=args.user_style, goal=args.user_goal)
    agent = PersonaSpec(name="agent", style=args.agent_style, goal=args.agent_goal)
    conv = synthesize_conversation(user, agent, args.turns, args.seed, gateway=gateway)
    out = write_conversation(conv, args.golden_root, args.rubric_family, args.rubric_id, user, agent, args.now)
    logger.info("wrote synthesized conversation to %s (mode=%s)", out, args.gateway_mode)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
