"""
P3.5 + P3.6 — Spine Restructure Notices for BriefAssemblyEngine and StyleGate.

P3.5 — BriefAssemblyEngine Split
---------------------------------
apps_exec.engines.BriefAssemblyEngine performed both:
  (a) Prompt slot composition (section ordering, headings, evidence injection)
  (b) Narrative fill with LLM_FILL placeholders

In the canonical spine these two responsibilities are SEPARATED:

  (a) Prompt slot composition → PA layer (RepoBriefPACompiler)
      Owned by: apps_repo_brief/prompt_assembly/repo_brief_pa_compiler.py
      Output: CompiledPromptArtifact (fully rendered slots S0-R0)
      No model calls; no retrieval.

  (b) Narrative synthesis/render → L2 layer (governed gateway)
      Owned by: agentic_core L2 execution
      Input: CompiledPromptArtifact from PA
      Output: governed_repo_brief_packet

apps_repo_brief does NOT have its own L2 synthesis engine.
apps_exec.engines.BriefAssemblyEngine is retained in apps_exec until W5 shim sunset.

P3.6 — StyleGateValidator Split
--------------------------------
apps_exec.engines.StyleGateValidator (HOP4) ran as a pre-C0 release gate.
This violated the spine: apps cannot own final release authority before C0/PA/L2/Exit.

In the canonical spine StyleGate is SPLIT:

  (a) Same-authority repair → L2.E4 heal pass
      The L2 layer may repair style violations using the same evidence contract.
      Templates: brief_length_and_structure_repair_v1.yaml,
                 caveat_and_confidence_repair_v1.yaml,
                 repo_citation_alignment_repair_v1.yaml
      No new retrieval; no new evidence; same authority.

  (b) Persistent violation gate → Exit v6 check (W4.P4.4)
      If a style violation persists after L2.E4 repair, Exit v6 emits
      BLOCK_COMMIT or SAFE_FALLBACK — it does NOT retry.
      Exit is the release authority, not apps_repo_brief.

Plan: .windsurf/plans/apps-repo-brief-plan3-zero-loss-overwrite.md §P3.5, §P3.6
"""

BRIEF_ASSEMBLY_ENGINE_OWNER = "PA (prompt) + L2 (render)"
BRIEF_ASSEMBLY_ENGINE_SPLIT_AT = "W3"

STYLE_GATE_VALIDATOR_OWNER = "L2.E4 heal + Exit v6 gate"
STYLE_GATE_VALIDATOR_SPLIT_AT = "W3 (L2.E4) + W4 (Exit gate)"


def brief_assembly_engine_retired() -> None:
    """Hard guard — apps_repo_brief must not instantiate BriefAssemblyEngine."""
    raise RuntimeError(
        "[apps_repo_brief] BriefAssemblyEngine is retired. "
        "Prompt slot composition: RepoBriefPACompiler. "
        "Narrative rendering: L2 governed gateway. See P3.5."
    )


def style_gate_validator_retired() -> None:
    """Hard guard — apps_repo_brief must not instantiate StyleGateValidator as pre-C0 gate."""
    raise RuntimeError(
        "[apps_repo_brief] StyleGateValidator as pre-C0 gate is retired. "
        "Same-authority repair: L2.E4 heal pass. "
        "Persistent violation gate: Exit v6 (W4). See P3.6."
    )
