"""apps_research.engines.judges — W9 LLM-as-judge and calibrated heuristic graders.

W9 Judges:
- claim_support_judge → G10 (Factual Grounding)
- citation_quality_judge → G09 (Source Quality)
- coverage_depth_judge → G22 (Answer Completeness)
- contradiction_resolution_judge → G10 (Factual Grounding)
- source_authority_judge → G09 (Source Quality)
- cache_compatibility_judge → G25 (Cache Consistency)
- briefing_injection_judge → G22 (Answer Completeness)
- downstream_relevance_judge → G25 (Cache Consistency)
"""

from apps_research.engines.judges.claim_support_judge import (
    ClaimSupportJudge,
    IS_STUB as claim_support_IS_STUB,
    IS_CALIBRATED as claim_support_IS_CALIBRATED,
    GRADER_ID as claim_support_GRADER_ID,
)
from apps_research.engines.judges.citation_quality_judge import (
    CitationQualityJudge,
    IS_STUB as citation_quality_IS_STUB,
    IS_CALIBRATED as citation_quality_IS_CALIBRATED,
    GRADER_ID as citation_quality_GRADER_ID,
)
from apps_research.engines.judges.coverage_depth_judge import (
    CoverageDepthJudge,
    IS_STUB as coverage_depth_IS_STUB,
    IS_CALIBRATED as coverage_depth_IS_CALIBRATED,
    GRADER_ID as coverage_depth_GRADER_ID,
)
from apps_research.engines.judges.contradiction_resolution_judge import (
    ContradictionResolutionJudge,
    IS_STUB as contradiction_resolution_IS_STUB,
    IS_CALIBRATED as contradiction_resolution_IS_CALIBRATED,
    GRADER_ID as contradiction_resolution_GRADER_ID,
)
from apps_research.engines.judges.source_authority_judge import (
    SourceAuthorityJudge,
    IS_STUB as source_authority_IS_STUB,
    IS_CALIBRATED as source_authority_IS_CALIBRATED,
    GRADER_ID as source_authority_GRADER_ID,
)
from apps_research.engines.judges.cache_compatibility_judge import (
    CacheCompatibilityJudge,
    IS_STUB as cache_compatibility_IS_STUB,
    IS_CALIBRATED as cache_compatibility_IS_CALIBRATED,
    GRADER_ID as cache_compatibility_GRADER_ID,
)
from apps_research.engines.judges.briefing_injection_judge import (
    BriefingInjectionJudge,
    IS_STUB as briefing_injection_IS_STUB,
    IS_CALIBRATED as briefing_injection_IS_CALIBRATED,
    GRADER_ID as briefing_injection_GRADER_ID,
)
from apps_research.engines.judges.downstream_relevance_judge import (
    DownstreamRelevanceJudge,
    IS_STUB as downstream_relevance_IS_STUB,
    IS_CALIBRATED as downstream_relevance_IS_CALIBRATED,
    GRADER_ID as downstream_relevance_GRADER_ID,
)

__all__ = [
    # Judge classes
    "ClaimSupportJudge",
    "CitationQualityJudge",
    "CoverageDepthJudge",
    "ContradictionResolutionJudge",
    "SourceAuthorityJudge",
    "CacheCompatibilityJudge",
    "BriefingInjectionJudge",
    "DownstreamRelevanceJudge",
    # Stub/Calibrated flags
    "claim_support_IS_STUB",
    "claim_support_IS_CALIBRATED",
    "citation_quality_IS_STUB",
    "citation_quality_IS_CALIBRATED",
    "coverage_depth_IS_STUB",
    "coverage_depth_IS_CALIBRATED",
    "contradiction_resolution_IS_STUB",
    "contradiction_resolution_IS_CALIBRATED",
    "source_authority_IS_STUB",
    "source_authority_IS_CALIBRATED",
    "cache_compatibility_IS_STUB",
    "cache_compatibility_IS_CALIBRATED",
    "briefing_injection_IS_STUB",
    "briefing_injection_IS_CALIBRATED",
    "downstream_relevance_IS_STUB",
    "downstream_relevance_IS_CALIBRATED",
    # Grader IDs
    "claim_support_GRADER_ID",
    "citation_quality_GRADER_ID",
    "coverage_depth_GRADER_ID",
    "contradiction_resolution_GRADER_ID",
    "source_authority_GRADER_ID",
    "cache_compatibility_GRADER_ID",
    "briefing_injection_GRADER_ID",
    "downstream_relevance_GRADER_ID",
]
