"""apps_lic LLM-judge registry.

STUB: real judge implementations are deferred to a calibration-backed
plan. See individual judge modules for full status.
"""

from apps_lic.engines.judges.response_likelihood_judge import (
    ResponseLikelihoodJudge,
    IS_STUB as response_likelihood_judge_is_stub,
)
from apps_lic.engines.judges.brand_voice_judge import (
    BrandVoiceJudge,
    IS_STUB as brand_voice_judge_is_stub,
)
from apps_lic.engines.judges.narrative_coherence_judge import (
    NarrativeCoherenceJudge,
    IS_STUB as narrative_coherence_judge_is_stub,
)
from apps_lic.engines.judges.tone_register_fit_judge import (
    ToneRegisterFitJudge,
    IS_STUB as tone_register_fit_judge_is_stub,
)

__all__ = [
    "ResponseLikelihoodJudge",
    "BrandVoiceJudge",
    "NarrativeCoherenceJudge",
    "ToneRegisterFitJudge",
    "response_likelihood_judge_is_stub",
    "brand_voice_judge_is_stub",
    "narrative_coherence_judge_is_stub",
    "tone_register_fit_judge_is_stub",
]
