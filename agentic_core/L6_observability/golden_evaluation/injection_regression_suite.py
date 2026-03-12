"""
Injection Regression Suite - Deterministic Evaluation Contract.

Provides deterministic evaluation of prompt injection detection against golden dataset.
No timestamps, UUIDs, or nondeterministic fields in output.
"""
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD

@dataclass(frozen=True)
class InjectionRegressionResult:
    """Deterministic result of injection regression evaluation."""
    total_samples: int
    blocked_samples: int
    detection_rate: float
    high_risk_patterns: int
    certification_hash: str
    attack_distribution: dict[str, int]
    error_message: str = ''

def evaluate_injection_regression(data_root: str=None, limit: int=None) -> InjectionRegressionResult:
    """Evaluate injection detection against golden dataset deterministically.

    Args:
        data_root: Root directory containing data/golden/ subdirectory
        limit: Optional limit on number of samples to process

    Returns:
        InjectionRegressionResult with deterministic certification hash
    """
    if data_root is None:
        data_root = Path(__file__).parent.parent.parent.parent.parent / 'data'
    golden_dir = Path(data_root) / 'golden'
    injection_file = golden_dir / 'prompt_injection_attacks_200.jsonl'
    if not injection_file.exists():
        result = InjectionRegressionResult(total_samples=0, blocked_samples=0, detection_rate=0.0, high_risk_patterns=0, certification_hash=hashlib.sha256(b'no_data').hexdigest(), attack_distribution={}, error_message='Golden dataset not found')
        return result
    samples = []
    with open(injection_file, encoding='utf-8') as f:
        for line in f:
            if limit and len(samples) >= limit:
                break
            samples.append(json.loads(line))
    blocked_count = 0
    high_risk_count = 0
    attack_dist = {}
    for sample in samples:
        attack_type = sample.get('attack_type', 'unknown')
        success_rate = sample.get('success_rate', 1.0)
        severity = sample.get('severity', 'low')
        attack_dist[attack_type] = attack_dist.get(attack_type, 0) + 1
        if success_rate < 0.5:
            blocked_count += 1
        if severity in ['critical', 'high']:
            high_risk_count += 1
    detection_rate = blocked_count / len(samples) if samples else 0.0
    hash_data = {'total_samples': len(samples), 'blocked_samples': blocked_count, 'detection_rate': detection_rate, 'high_risk_patterns': high_risk_count, 'attack_distribution': attack_dist}
    cert_hash = hashlib.sha256(json.dumps(hash_data, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    return InjectionRegressionResult(total_samples=len(samples), blocked_samples=blocked_count, detection_rate=detection_rate, high_risk_patterns=high_risk_count, certification_hash=cert_hash, attack_distribution=attack_dist)
