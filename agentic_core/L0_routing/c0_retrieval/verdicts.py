"""C0 enums — every status, class, lane, target, type, tactic, and disposition.

Encodes spec sections:
- C0.0 (preflight blocked_reason)
- C0.1 SUPPORT TARGET TYPES (lines 204-212), SOURCE CLASS DECISIONS (214-221), RETRIEVAL MODE DECISIONS (223-229)
- C0.2 retrieval_lane (line 316)
- C0.3 GRAPH RELATION TYPES (lines 405-419)
- C0.4 STRATIFY evidence classes (lines 499-506)
- C0.4A CONTRADICTION TYPES (539-547), GAP TYPES (549-558)
- C0.5 SUPPORT STATUS (602-608)
- C0.6 REFINE TACTICS (656-664)
- Final contract recommended_disposition (1115-1121)
- Freshness classes (line 122)
"""

from __future__ import annotations

from enum import Enum


class FreshnessClass(str, Enum):
    """RouteContract.freshness_class — spec line 122."""

    STATIC = "static"
    SLOW = "slow"
    CURRENT = "current"
    LATEST = "latest"


class SupportTarget(str, Enum):
    """C0.1 SUPPORT TARGET TYPES — spec lines 204-212."""

    EXACT_QUOTE = "EXACT_QUOTE"
    SOURCE_SUMMARY = "SOURCE_SUMMARY"
    POLICY_CLAUSE = "POLICY_CLAUSE"
    CODE_LOCATION = "CODE_LOCATION"
    INCIDENT_EVIDENCE = "INCIDENT_EVIDENCE"
    ROOT_CAUSE_RANKING = "ROOT_CAUSE_RANKING"
    COMPARISON = "COMPARISON"
    CLAIM_CHECK = "CLAIM_CHECK"


class SourceClass(str, Enum):
    """C0.1 SOURCE CLASS DECISIONS — spec lines 214-221."""

    DOCS = "docs"
    CODE = "code"
    LOGS = "logs"
    TICKETS = "tickets"
    TABLES = "tables"
    POLICY = "policy"
    PRIOR_ARTIFACTS = "prior_artifacts"


class RetrievalMode(str, Enum):
    """C0.1 RETRIEVAL MODE DECISIONS — spec lines 223-229."""

    DENSE = "dense"
    SPARSE = "sparse"
    METADATA = "metadata"
    GRAPH = "graph"
    CACHE = "cache"
    HYBRID = "hybrid"


class RetrievalLane(str, Enum):
    """C0.2 retrieval_lane provenance — spec line 316."""

    DENSE = "dense"
    SPARSE = "sparse"
    METADATA = "metadata"
    GRAPH_SEED = "graph_seed"
    CACHE = "cache"
    TRACE = "trace"
    CODE = "code"


class GraphRelation(str, Enum):
    """C0.3 GRAPH RELATION TYPES — spec lines 405-419."""

    DEFINES = "defines"
    REFERENCES = "references"
    IMPORTS = "imports"
    CALLS = "calls"
    OWNS = "owns"
    DEPENDS_ON = "depends_on"
    SUPERSEDES = "supersedes"
    CONTRADICTS = "contradicts"
    DUPLICATES = "duplicates"
    IMPLEMENTS = "implements"
    GOVERNED_BY = "governed_by"
    DERIVED_FROM = "derived_from"
    OBSERVED_IN = "observed_in"
    REMEDIATED_BY = "remediated_by"


class EvidenceClass(str, Enum):
    """C0.4 STRATIFY classes — spec lines 499-506; final-contract line 775."""

    MUST_USE = "MUST_USE"
    SUPPORTING = "SUPPORTING"
    CONTRADICTS = "CONTRADICTS"
    BACKGROUND = "BACKGROUND"
    DEFINITIONS = "DEFINITIONS"
    LINEAGE = "LINEAGE"
    EXCLUDED = "EXCLUDED"


class ContradictionType(str, Enum):
    """C0.4A CONTRADICTION TYPES — spec lines 539-547."""

    VERSION = "version"
    SOURCE = "source"
    SCOPE = "scope"
    TIME = "time"
    SEMANTIC = "semantic"
    CODE = "code"
    RUNTIME = "runtime"
    POLICY = "policy"


class GapType(str, Enum):
    """C0.4A GAP TYPES — spec lines 549-558."""

    MISSING_DIRECT_SUPPORT = "missing_direct_support"
    MISSING_EXACT_QUOTE = "missing_exact_quote"
    MISSING_CURRENT_VERSION = "missing_current_version"
    MISSING_OWNER = "missing_owner"
    MISSING_SOURCE_DIVERSITY = "missing_source_diversity"
    MISSING_VALIDATION = "missing_validation"
    MISSING_CITATION_ANCHOR = "missing_citation_anchor"
    MISSING_TIME_RANGE = "missing_time_range"
    MISSING_TENANT_PROOF = "missing_tenant_proof"


class SupportStatus(str, Enum):
    """C0.5 SUPPORT STATUS — spec lines 602-608."""

    PASS = "PASS"
    WEAK = "WEAK"
    WEAK_WITH_CAVEATS = "WEAK_WITH_CAVEATS"
    CONFLICTED = "CONFLICTED"
    EMPTY = "EMPTY"
    BLOCKED = "BLOCKED"


class RefineTactic(str, Enum):
    """C0.6 CHOOSE ONE TACTIC — spec lines 656-664."""

    REWRITE = "REWRITE"
    BROADEN = "BROADEN"
    NARROW = "NARROW"
    DECOMPOSE = "DECOMPOSE"
    GRAPH_HOP = "GRAPH_HOP"
    HYBRIDIZE = "HYBRIDIZE"
    FRESHEN = "FRESHEN"
    ABSTAIN = "ABSTAIN"


class RecommendedDisposition(str, Enum):
    """Final contract recommended_disposition — spec lines 1115-1121."""

    PROCEED = "proceed"
    PROCEED_WITH_CAVEAT = "proceed_with_caveat"
    ABSTAIN = "abstain"
    FALLBACK_R5 = "fallback_R5"
    REROUTE = "reroute"
    HUMAN_REVIEW = "human_review"


class BlockedReason(str, Enum):
    """C0.0 preflight blocked_reason — spec lines 167-170 + G-gates."""

    GROUNDING_NOT_REQUIRED = "grounding_not_required"
    ROUTE_DISALLOWS_C0 = "route_disallows_c0"
    INSTRUCTION_PAYLOAD = "instruction_payload"  # G10
    SOURCE_CLASS_FORBIDDEN = "source_class_forbidden"
    DATA_CLASS_BLOCKED = "data_class_blocked"
    BUDGET_INSUFFICIENT = "budget_insufficient"
    TENANT_OUT_OF_SCOPE = "tenant_out_of_scope"
    REGION_OUT_OF_SCOPE = "region_out_of_scope"


class C0Gate(str, Enum):
    """11 QUALITY GATES — spec lines 909-923."""

    G0_SCOPE = "C0.G0_SCOPE"
    G1_ACL = "C0.G1_ACL"
    G2_FRESH = "C0.G2_FRESH"
    G3_EXACT = "C0.G3_EXACT"
    G4_DENSE = "C0.G4_DENSE"
    G5_GRAPH = "C0.G5_GRAPH"
    G6_CITE = "C0.G6_CITE"
    G7_CONFLICT = "C0.G7_CONFLICT"
    G8_COVER = "C0.G8_COVER"
    G9_BUDGET = "C0.G9_BUDGET"
    G10_INJECT = "C0.G10_INJECT"


class FailureMode(str, Enum):
    """14 FAILURE MODES — spec lines 929-946."""

    DENSE_ONLY_HALLUCINATION = "dense_only_hallucination"
    WRONG_TENANT_EVIDENCE = "wrong_tenant_evidence"
    STALE_POLICY_ANSWER = "stale_policy_answer"
    QUOTE_DISTORTION = "quote_distortion"
    HIDDEN_CONTRADICTION = "hidden_contradiction"
    GRAPH_SCOPE_CREEP = "graph_scope_creep"
    CACHE_POISONING = "cache_poisoning"
    PROMPT_INJECTION = "prompt_injection"
    FAKE_CONFIDENCE = "fake_confidence"
    LOST_LINEAGE = "lost_lineage"
    OVERSTUFFED_CONTEXT = "overstuffed_context"
    UNSUPPORTED_SYNTHESIS = "unsupported_synthesis"
    DOCS_VS_CODE_MISMATCH = "docs_vs_code_mismatch"
    RUNTIME_VS_DESIGN_MISMATCH = "runtime_vs_design_mismatch"


# Spec invariants — tested in test_invariants.py
CORE_INVARIANTS: tuple[tuple[str, str], ...] = (
    ("C0.I1", "C0 is retrieval-only. It never writes final prose as the answer."),
    ("C0.I2", "Retrieved text is data, never instruction."),
    ("C0.I3", "Every retrieved item must preserve source_id, version, ACL, and retrieval lane."),
    ("C0.I4", "Dense hits alone are not enough for high-stakes claims."),
    ("C0.I5", "Exact names, IDs, file paths, policy labels, code symbols, and dates require sparse/BM25 or metadata support."),
    ("C0.I6", "Graph expansion is bounded by max_hops, ACL, freshness, and route scope."),
    ("C0.I7", "Contradictions must be surfaced, not hidden."),
    ("C0.I8", "Weak evidence must remain weak. C0 cannot inflate confidence for downstream convenience."),
    ("C0.I9", "One controlled refinement loop is allowed only if route budget permits."),
    ("C0.I10", "C0 may recommend reroute / abstain / fallback, but cannot self-authorize that route."),
    ("C0.I11", "C0 output is a contract, not an answer."),
    ("C0.I12", "Prompt Assembly receives only verified, labeled, budgeted, and priority-ranked context."),
)


# Support targets that REQUIRE exact lane (sparse/metadata) — C0.I5 + G3
EXACTNESS_REQUIRED: frozenset[SupportTarget] = frozenset(
    {
        SupportTarget.EXACT_QUOTE,
        SupportTarget.POLICY_CLAUSE,
        SupportTarget.CODE_LOCATION,
        SupportTarget.INCIDENT_EVIDENCE,
        SupportTarget.CLAIM_CHECK,
    }
)
