"""W10 — RCA Synthesizer (Core-Owned)

Synthesizes root cause analysis from completed run evidence.
Produces inert RCAPacket (observational only, no repairs).

Hard Rules:
- Observational analysis only
- No current-run repair attempts
- Hypotheses are explanatory, not prescriptive
"""
from typing import Any, Dict, List
from dataclasses import dataclass

from agentic_core.L6_learning import RCAPacket


@dataclass(frozen=True)
class RCAInput:
    """Input for RCA synthesis."""
    gate_mesh_result: Dict[str, Any]
    judge_evidence_results: List[Dict[str, Any]]
    exit_disposition: Dict[str, Any]


class RCASynthesizer:
    """Synthesizes root cause analysis from runtime evidence.
    
    Core owns synthesis logic. Apps provide RCA policy config.
    """
    
    def synthesize(self, rca_input: RCAInput) -> RCAPacket:
        """Synthesize RCA from completed run evidence.
        
        Args:
            rca_input: Aggregated runtime evidence
            
        Returns:
            RCAPacket with observational analysis
        """
        run_id = rca_input.exit_disposition.get('run_id', 'unknown')
        
        # Identify gate failure patterns
        gate_failures = self._identify_gate_failures(
            rca_input.gate_mesh_result
        )
        
        # Identify judge disagreement patterns
        judge_disagreements = self._identify_judge_disagreements(
            rca_input.judge_evidence_results
        )
        
        # Identify cache anomalies
        cache_anomalies = self._identify_cache_anomalies(
            rca_input.gate_mesh_result
        )
        
        # Synthesize root cause hypotheses
        hypotheses = self._synthesize_hypotheses(
            gate_failures, judge_disagreements, cache_anomalies
        )
        
        # Identify contributing factors
        contributing = self._identify_contributing_factors(
            rca_input.gate_mesh_result,
            rca_input.judge_evidence_results
        )
        
        return RCAPacket(
            run_id=run_id,
            rca_id=f"rca-{run_id}",
            gate_failure_patterns=gate_failures,
            judge_disagreement_patterns=judge_disagreements,
            cache_hit_anomaly_patterns=cache_anomalies,
            root_cause_hypotheses=hypotheses,
            contributing_factors=contributing,
            evidence_refs=(
                f"gate_mesh://{run_id}",
                f"judge_evidence://{run_id}",
                f"exit://{run_id}",
            ),
        )
    
    def _identify_gate_failures(
        self,
        gate_mesh: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Identify gate failure patterns."""
        failures = []
        verdicts = gate_mesh.get('verdicts', {})
        
        for gate_id, verdict in verdicts.items():
            if verdict.get('result') == 'FAIL':
                failures.append({
                    'gate_id': gate_id,
                    'result': verdict.get('result'),
                    'reason': verdict.get('reason', ''),
                    'severity': verdict.get('severity', 'unknown'),
                })
        
        return failures
    
    def _identify_judge_disagreements(
        self,
        judge_results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Identify judge disagreement patterns."""
        disagreements = []
        
        # Group by dimension
        by_dimension: Dict[str, List[float]] = {}
        for result in judge_results:
            dim = result.get('dimension')
            score = result.get('score')
            if dim and score is not None:
                by_dimension.setdefault(dim, []).append(score)
        
        # Detect high variance
        for dim, scores in by_dimension.items():
            if len(scores) > 1:
                variance = max(scores) - min(scores)
                if variance > 0.3:
                    disagreements.append({
                        'dimension': dim,
                        'score_spread': variance,
                        'scores': scores,
                    })
        
        return disagreements
    
    def _identify_cache_anomalies(
        self,
        gate_mesh: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Identify cache hit anomalies."""
        anomalies = []
        
        cache_metrics = gate_mesh.get('cache_metrics', {})
        hit_rate = cache_metrics.get('hit_rate', 0.0)
        
        if hit_rate < 0.3:
            anomalies.append({
                'type': 'low_cache_hit_rate',
                'hit_rate': hit_rate,
                'threshold': 0.3,
            })
        elif hit_rate > 0.95:
            anomalies.append({
                'type': 'suspiciously_high_hit_rate',
                'hit_rate': hit_rate,
                'threshold': 0.95,
            })
        
        return anomalies
    
    def _synthesize_hypotheses(
        self,
        gate_failures: List[Dict[str, Any]],
        judge_disagreements: List[Dict[str, Any]],
        cache_anomalies: List[Dict[str, Any]]
    ) -> List[str]:
        """Synthesize root cause hypotheses."""
        hypotheses = []
        
        if gate_failures:
            g10_failures = [f for f in gate_failures if f['gate_id'].startswith('G10')]
            if g10_failures:
                hypotheses.append(
                    "Factual grounding failures suggest source quality or citation completeness issues"
                )
            
            g22_failures = [f for f in gate_failures if f['gate_id'].startswith('G22')]
            if g22_failures:
                hypotheses.append(
                    "Answer completeness failures suggest coverage depth or briefing injection issues"
                )
        
        if judge_disagreements:
            hypotheses.append(
                f"Judge disagreement on {len(judge_disagreements)} dimensions "
                "suggests calibration drift or ambiguous rubric criteria"
            )
        
        if cache_anomalies:
            for anomaly in cache_anomalies:
                if anomaly['type'] == 'low_cache_hit_rate':
                    hypotheses.append(
                        "Low cache hit rate suggests semantic mismatch or TTL misconfiguration"
                    )
        
        if not hypotheses:
            hypotheses.append("No clear root cause identified from available evidence")
        
        return hypotheses
    
    def _identify_contributing_factors(
        self,
        gate_mesh: Dict[str, Any],
        judge_results: List[Dict[str, Any]]
    ) -> List[str]:
        """Identify contributing factors."""
        factors = []
        
        # Check for unknown verdicts
        unknown_count = sum(
            1 for v in gate_mesh.get('verdicts', {}).values()
            if v.get('result') == 'UNKNOWN'
        )
        if unknown_count > 0:
            factors.append(f"{unknown_count} gates with UNKNOWN verdicts")
        
        # Check for low confidence judges
        low_conf_judges = [
            r for r in judge_results
            if r.get('confidence', 1.0) < 0.7
        ]
        if low_conf_judges:
            factors.append(f"{len(low_conf_judges)} judges with confidence < 0.7")
        
        return factors
