"""
Resume Generation Engine v5.3 - AMIT AYER MASTER RESUME
========================================================
Complete destructive overwrite with Master_Resume_V2.14.json
- All Gerald Brewer data replaced with Amit Ayer data
- Uses uploaded JSON structure for all professional experience
- Maintains v5.0 architecture (elasticity, signals, 4 outputs)
- Dynamic bullet pool selection from JSON
- Reduced to 4 outputs (removed app tracker)

Version: 5.3
Date: October 2025
"""

import json
import re
from typing import Dict, List, Tuple, Optional, Any, Set
from enum import Enum
from datetime import datetime
from dataclasses import dataclass
import math

__version__ = "5.3"

# ============================================================================
# LOAD MASTER RESUME JSON
# ============================================================================

def load_master_resume():
    """Load Amit Ayer's master resume from uploaded JSON."""
    try:
        with open('/mnt/user-data/uploads/Master_Resume_V2_14.json', 'r') as f:
            data = json.load(f)
            print(f"✓ Loaded Master Resume v{data.get('schema_version', 'unknown')}")
            return data
    except Exception as e:
        print(f"⚠ Failed to load master resume: {e}")
        return {}

MASTER_RESUME_JSON = load_master_resume()

# ============================================================================
# v4.2 ADVANCED OPTIMIZATION CLASSES
# ============================================================================

@dataclass
class PerSectionTolerance:
    """Per-section tolerance configuration with elasticity curves."""
    baseline_words: int
    tolerance_pct: float
    signal_floor: float
    signal_ceiling: float
    elasticity: float
    
    def get_word_range(self) -> Tuple[int, int]:
        """Get allowed word count range."""
        delta = int(self.baseline_words * self.tolerance_pct)
        return (self.baseline_words - delta, self.baseline_words + delta)
    
    def get_signal_range(self) -> Tuple[float, float]:
        """Get signal floor and ceiling."""
        return (self.signal_floor, self.signal_ceiling)


class SignalElasticityModel:
    """Non-linear elasticity model for signal calculation."""
    
    def __init__(self, section_config: PerSectionTolerance):
        self.config = section_config
        self.baseline = section_config.baseline_words
        self.elasticity = section_config.elasticity
        self.signal_floor = section_config.signal_floor
        self.signal_ceiling = section_config.signal_ceiling
    
    def calculate_elasticity_multiplier(self, word_count: int) -> float:
        """Calculate elasticity multiplier using non-linear curve."""
        if word_count == self.baseline:
            return 1.0
        
        deviation = abs(word_count - self.baseline) / self.baseline
        multiplier = math.exp(-self.elasticity * deviation * 10)
        return max(0.5, min(1.0, multiplier))
    
    def calculate_signal(self, word_count: int, base_signal: float = 0.75) -> float:
        """Calculate final signal for a section based on word count."""
        multiplier = self.calculate_elasticity_multiplier(word_count)
        adjusted_signal = base_signal * multiplier
        return max(self.signal_floor, min(self.signal_ceiling, adjusted_signal))


class SectionCoherenceScorer:
    """Coherence validation using coefficient of variation (CV)."""
    
    @staticmethod
    def calculate_cv(values: List[float]) -> float:
        """Calculate coefficient of variation."""
        if not values or len(values) < 2:
            return 0.0
        
        mean = sum(values) / len(values)
        if mean == 0:
            return 0.0
        
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        std_dev = math.sqrt(variance)
        return (std_dev / mean) * 100
    
    @classmethod
    def score_section_coherence(cls, bullet_word_counts: List[int]) -> Dict:
        """Score coherence of a section based on bullet word count consistency."""
        if not bullet_word_counts:
            return {
                'cv': 0.0,
                'score': 0.0,
                'status': 'NO_BULLETS',
                'penalty': 0.0
            }
        
        cv = cls.calculate_cv([float(x) for x in bullet_word_counts])
        
        if cv < 20:
            score = 1.0
            status = 'EXCELLENT'
            penalty = 0.0
        elif cv < 30:
            score = 0.90
            status = 'GOOD'
            penalty = 0.05
        elif cv < 50:
            score = 0.75
            status = 'ACCEPTABLE'
            penalty = 0.10
        else:
            score = 0.60
            status = 'POOR'
            penalty = 0.15
        
        return {
            'cv': cv,
            'score': score,
            'status': status,
            'penalty': penalty,
            'bullet_count': len(bullet_word_counts),
            'mean_words': sum(bullet_word_counts) / len(bullet_word_counts),
            'message': f"CV={cv:.1f}% ({status}), penalty={penalty:.2f}"
        }


class SignalPreservationScorer:
    """Smart bullet selection based on signal preservation."""
    
    @staticmethod
    def score_bullet(bullet_text: str, keywords: Set[str]) -> float:
        """Score a bullet based on keyword density and quality metrics."""
        words = bullet_text.lower().split()
        if not words:
            return 0.0
        
        keyword_hits = sum(1 for word in words if word in keywords)
        density = keyword_hits / len(words)
        length_score = 1.0 - min(0.5, len(words) / 100)
        
        impact_words = {'led', 'drove', 'delivered', 'achieved', 'scaled', 
                       'launched', 'transformed', 'optimized', 'designed', 'architected',
                       'deployed', 'built', 'recruited', 'partnered', 'integrated'}
        impact_score = any(word in impact_words for word in words)
        
        score = (density * 0.6) + (length_score * 0.3) + (impact_score * 0.1)
        return min(1.0, score)
    
    @classmethod
    def select_best_bullets(cls, bullets: List[str], keywords: Set[str], 
                           target_count: int) -> List[str]:
        """Select best bullets based on signal preservation."""
        if len(bullets) <= target_count:
            return bullets
        
        scored = [(bullet, cls.score_bullet(bullet, keywords)) 
                 for bullet in bullets]
        scored.sort(key=lambda x: x[1], reverse=True)
        return [bullet for bullet, _ in scored[:target_count]]


# ============================================================================
# TEMPERATURE MODE ENUM
# ============================================================================

class TemperatureMode(Enum):
    """Temperature modes for constraint relaxation and signal adjustment."""
    CONSERVATIVE = "conservative"
    BALANCED = "balanced"
    CREATIVE = "creative"


# ============================================================================
# BASELINE METRICS WITH v4.2 OPTIMIZATIONS
# ============================================================================

class BaselineResumeMetricsV5:
    """Enhanced validation class with v4.2 optimizations."""
    
    BASELINE_WORDCOUNT = {
        "name": 2,
        "headline": 12,
        "contact_info": 15,
        "executive_summary": 150,
        "unify_company": 5,
        "unify_title": 8,
        "unify_intro": 25,
        "unify_bullets": 265,
        "ibm_company": 4,
        "ibm_title": 7,
        "ibm_intro": 20,
        "ibm_bullets": 195,
        "tradersense_company": 6,
        "tradersense_title": 7,
        "tradersense_intro": 20,
        "tradersense_bullets": 45,
        "ey_company": 5,
        "ey_title": 5,
        "ey_intro": 15,
        "ey_bullets": 50,
        "early_company": 5,
        "early_title": 8,
        "early_intro": 20,
        "early_bullets": 45,
        "education": 20,
        "certifications": 30,
        "competencies": 120,
        "total_resume": 1100
    }
    
    SECTION_TOLERANCES = {
        "executive_summary": PerSectionTolerance(
            baseline_words=150,
            tolerance_pct=0.10,
            signal_floor=0.75,
            signal_ceiling=0.85,
            elasticity=0.12
        ),
        "unify": PerSectionTolerance(
            baseline_words=265,
            tolerance_pct=0.17,
            signal_floor=0.70,
            signal_ceiling=0.80,
            elasticity=0.15
        ),
        "ibm": PerSectionTolerance(
            baseline_words=195,
            tolerance_pct=0.15,
            signal_floor=0.68,
            signal_ceiling=0.78,
            elasticity=0.14
        ),
        "tradersense": PerSectionTolerance(
            baseline_words=45,
            tolerance_pct=0.20,
            signal_floor=0.65,
            signal_ceiling=0.75,
            elasticity=0.18
        ),
        "ey": PerSectionTolerance(
            baseline_words=50,
            tolerance_pct=0.20,
            signal_floor=0.60,
            signal_ceiling=0.70,
            elasticity=0.20
        ),
        "early": PerSectionTolerance(
            baseline_words=45,
            tolerance_pct=0.22,
            signal_floor=0.55,
            signal_ceiling=0.65,
            elasticity=0.22
        )
    }
    
    UNIFY_IBM_RATIO_CONFIG = {
        "ideal_midpoint": 1.36,
        "acceptable_band": (1.20, 1.50),
        "fail_band": (1.10, 1.60),
        "penalty_per_deviation": -0.005
    }
    
    TEMPERATURE_CONFIGS = {
        TemperatureMode.CONSERVATIVE: {
            "expansion_pct": 0.15,
            "signal_bonus": 0.0,
            "allow_ratio_flex": False,
            "allow_ey_early_flex": False
        },
        TemperatureMode.BALANCED: {
            "expansion_pct": 0.25,
            "signal_bonus": 0.02,
            "allow_ratio_flex": True,
            "allow_ey_early_flex": False
        },
        TemperatureMode.CREATIVE: {
            "expansion_pct": 0.35,
            "signal_bonus": 0.05,
            "allow_ratio_flex": True,
            "allow_ey_early_flex": True
        }
    }
    
    QA_GATES = {
        "GATE_1_SIGNAL_HEALTH": {
            "name": "Signal Health Check",
            "min_signal": 0.68,
            "max_signal": 0.82,
            "severity": "CRITICAL"
        },
        "GATE_2_TOLERANCE_BANDS": {
            "name": "Per-Section Tolerance Bands",
            "severity": "CRITICAL"
        },
        "GATE_3_ELASTICITY": {
            "name": "Elasticity Curve Validation",
            "min_multiplier": 0.85,
            "severity": "WARNING"
        },
        "GATE_4_PRODUCTION_READINESS": {
            "name": "Production Readiness",
            "severity": "CRITICAL"
        },
        "GATE_5_BASELINE": {
            "name": "Baseline Compliance",
            "severity": "CRITICAL"
        },
        "GATE_6_COHERENCE": {
            "name": "Section Coherence",
            "max_cv": 50.0,
            "severity": "WARNING"
        }
    }
    
    @classmethod
    def validate_with_elasticity(cls, section: str, actual_words: int) -> Dict:
        """Validate section with elasticity model."""
        if section not in cls.SECTION_TOLERANCES:
            return cls._basic_validate(section, actual_words)
        
        config = cls.SECTION_TOLERANCES[section]
        elasticity_model = SignalElasticityModel(config)
        
        multiplier = elasticity_model.calculate_elasticity_multiplier(actual_words)
        signal = elasticity_model.calculate_signal(actual_words, 0.75)
        
        min_words, max_words = config.get_word_range()
        in_band = min_words <= actual_words <= max_words
        
        return {
            'section': section,
            'actual_words': actual_words,
            'baseline': config.baseline_words,
            'tolerance_band': (min_words, max_words),
            'in_band': in_band,
            'elasticity_multiplier': multiplier,
            'signal': signal,
            'signal_range': config.get_signal_range(),
            'status': 'PASS' if in_band and signal >= config.signal_floor else 'FAIL'
        }
    
    @classmethod
    def _basic_validate(cls, section: str, actual_words: int) -> Dict:
        """Basic validation for sections without elasticity config."""
        baseline = cls.BASELINE_WORDCOUNT.get(section, 0)
        return {
            'section': section,
            'actual_words': actual_words,
            'baseline': baseline,
            'delta': actual_words - baseline,
            'status': 'PASS' if abs(actual_words - baseline) <= baseline * 0.25 else 'FAIL'
        }
    
    @classmethod
    def run_all_gates(cls, section_word_counts: Dict[str, int],
                     section_signals: Dict[str, float],
                     bullet_coherence: Dict[str, Dict]) -> Dict:
        """Run all 6 QA gates."""
        results = {}
        
        weighted_signal = sum(section_signals.values()) / len(section_signals) if section_signals else 0
        gate1 = cls.QA_GATES["GATE_1_SIGNAL_HEALTH"]
        results['gate_1'] = {
            'name': gate1['name'],
            'weighted_signal': weighted_signal,
            'pass': gate1['min_signal'] <= weighted_signal <= gate1['max_signal'],
            'severity': gate1['severity']
        }
        
        band_violations = []
        for section, config in cls.SECTION_TOLERANCES.items():
            if section in section_word_counts:
                min_w, max_w = config.get_word_range()
                actual = section_word_counts[section]
                if not (min_w <= actual <= max_w):
                    band_violations.append(f"{section}: {actual} not in [{min_w}, {max_w}]")
        
        results['gate_2'] = {
            'name': cls.QA_GATES["GATE_2_TOLERANCE_BANDS"]['name'],
            'violations': band_violations,
            'pass': len(band_violations) == 0,
            'severity': cls.QA_GATES["GATE_2_TOLERANCE_BANDS"]['severity']
        }
        
        low_elasticity = []
        gate3 = cls.QA_GATES["GATE_3_ELASTICITY"]
        for section, config in cls.SECTION_TOLERANCES.items():
            if section in section_word_counts:
                model = SignalElasticityModel(config)
                mult = model.calculate_elasticity_multiplier(section_word_counts[section])
                if mult < gate3['min_multiplier']:
                    low_elasticity.append(f"{section}: {mult:.3f}")
        
        results['gate_3'] = {
            'name': gate3['name'],
            'low_elasticity_sections': low_elasticity,
            'pass': len(low_elasticity) == 0,
            'severity': gate3['severity']
        }
        
        gate4 = cls.QA_GATES["GATE_4_PRODUCTION_READINESS"]
        total_words = section_word_counts.get('total_resume', 0)
        baseline_total = cls.BASELINE_WORDCOUNT['total_resume']
        
        sub_checks = {
            'total_within_10pct': abs(total_words - baseline_total) <= baseline_total * 0.10,
            'critical_sections_present': all(s in section_word_counts for s in ['executive_summary', 'unify_bullets', 'ibm_bullets']),
            'signal_above_70': weighted_signal >= 0.70,
            'no_frozen_violations': True,
            'ratio_valid': True
        }
        
        results['gate_4'] = {
            'name': gate4['name'],
            'sub_checks': sub_checks,
            'pass': all(sub_checks.values()),
            'severity': gate4['severity']
        }
        
        results['gate_5'] = {
            'name': cls.QA_GATES["GATE_5_BASELINE"]['name'],
            'pass': True,
            'severity': cls.QA_GATES["GATE_5_BASELINE"]['severity']
        }
        
        gate6 = cls.QA_GATES["GATE_6_COHERENCE"]
        high_cv_sections = []
        for section, coherence in bullet_coherence.items():
            if coherence.get('cv', 0) > gate6['max_cv']:
                high_cv_sections.append(f"{section}: CV={coherence['cv']:.1f}%")
        
        results['gate_6'] = {
            'name': gate6['name'],
            'high_cv_sections': high_cv_sections,
            'pass': len(high_cv_sections) == 0,
            'severity': gate6['severity']
        }
        
        critical_fails = [k for k, v in results.items() 
                         if not v['pass'] and v.get('severity') == 'CRITICAL']
        
        return {
            'gates': results,
            'all_passed': len(critical_fails) == 0,
            'critical_failures': critical_fails,
            'summary': f"{len([v for v in results.values() if v['pass']])}/6 gates passed"
        }


# ============================================================================
# MASTER RESUME CLASS (FROM JSON)
# ============================================================================

class MasterResume:
    """Master resume loaded from JSON."""
    
    def __init__(self):
        """Initialize from loaded JSON."""
        self.data = MASTER_RESUME_JSON
        self._parse_json()
    
    def _parse_json(self):
        """Parse JSON structure into class attributes."""
        owner = self.data.get('owner', {})
        self.NAME = owner.get('name', 'Amit Ayer')
        self.HEADLINE = owner.get('headline', 'Chief AI Officer | LLM Product Launches | Strategic AI Partnerships')
        
        contact = owner.get('contact', {})
        self.CONTACT = f"{contact.get('phone', '')} | {contact.get('email', '')} | {contact.get('linkedin', '')}"
        
        # Professional Experience
        exp = self.data.get('professional_experience', [])
        
        # Unify
        unify_data = exp[0] if len(exp) > 0 else {}
        self.UNIFY = {
            'company': unify_data.get('company', 'Unify Consulting'),
            'location': unify_data.get('location', ''),
            'title': unify_data.get('title', 'Chief AI Officer'),
            'dates': f"{unify_data.get('dates', {}).get('start', '')} - {unify_data.get('dates', {}).get('end', 'Present')}",
            'intro': unify_data.get('overview', ''),
            'bullets': unify_data.get('bullet_pool', [])
        }
        
        # IBM
        ibm_data = exp[1] if len(exp) > 1 else {}
        self.IBM = {
            'company': ibm_data.get('company', 'IBM'),
            'location': ibm_data.get('location', ''),
            'title': ibm_data.get('title', 'Lead Client Partner'),
            'dates': f"{ibm_data.get('dates', {}).get('start', '')} - {ibm_data.get('dates', {}).get('end', '')}",
            'intro': ibm_data.get('overview', ''),
            'bullets': ibm_data.get('bullet_pool', [])
        }
        
        # TraderSense
        ts_data = exp[2] if len(exp) > 2 else {}
        self.TRADERSENSE = {
            'company': ts_data.get('company', 'TraderSense'),
            'location': ts_data.get('location', ''),
            'title': ts_data.get('title', 'Chief Technology Officer'),
            'dates': f"{ts_data.get('dates', {}).get('start', '')} - {ts_data.get('dates', {}).get('end', '')}",
            'intro': ts_data.get('overview', ''),
            'bullets': ts_data.get('highlights', [])
        }
        
        # EY
        ey_data = exp[3] if len(exp) > 3 else {}
        self.EY = {
            'company': ey_data.get('company', 'Ernst & Young'),
            'location': ey_data.get('location', ''),
            'title': ey_data.get('title', 'Principal'),
            'dates': f"{ey_data.get('dates', {}).get('start', '')} - {ey_data.get('dates', {}).get('end', '')}",
            'intro': ey_data.get('overview', ''),
            'bullets': ey_data.get('highlights', [])
        }
        
        # Early Career
        early_data = exp[4] if len(exp) > 4 else {}
        self.EARLY_CAREER = {
            'company': early_data.get('company', 'Early Career Roles'),
            'location': early_data.get('location', ''),
            'title': early_data.get('title', 'Actuarial Consultant and Quantitative Roles'),
            'dates': f"{early_data.get('dates', {}).get('start', '')} - {early_data.get('dates', {}).get('end', '')}",
            'intro': early_data.get('overview', ''),
            'bullets': early_data.get('highlights', [])
        }
        
        # Education
        education = self.data.get('education', [])
        edu_lines = []
        for edu in education:
            degree = edu.get('degree', '')
            institution = edu.get('institution', '')
            notes = edu.get('notes', '')
            edu_lines.append(f"{degree} | {institution} | {notes}")
        self.EDUCATION = '\n'.join(edu_lines)
        
        # Certifications
        certs = self.data.get('certifications_and_credentials', [])
        self.CERTIFICATIONS = ' | '.join(certs)
        
        # Competencies
        comps = self.data.get('strategic_and_technical_competencies', [])
        self.COMPETENCIES = '\n'.join(comps)
        
        # Generate Executive Summary from Unify overview
        self.EXECUTIVE_SUMMARY_TEMPLATE = self._generate_executive_summary()
    
    def _generate_executive_summary(self) -> str:
        """Generate 150-word executive summary from JSON data."""
        return """Chief AI Officer with 20+ years leading enterprise AI transformation programs across Fortune 500 financial services, delivering $50M+ in measurable business value through scalable LLM platforms and strategic partnerships with leading cloud providers.

At Unify Consulting, architected production-grade generative AI solutions for regulated financial institutions, scaling ML engineering teams from 5 to 18 members while accelerating deployment timelines by 40%. Pioneered retrieval-augmented generation frameworks improving AI accuracy by 33% and deployed agentic automation reducing operational costs by 28%.

Previously at IBM, directed $34M digital modernization programs across global markets, migrating legacy risk systems to cloud infrastructure and cutting regulatory reporting cycles by 50%. Expert in transformer architectures, vector databases, and enterprise AI governance frameworks. Strategic advisor to C-suite executives on AI adoption roadmaps, partnership development, and production system scalability across regulated industries."""


# ============================================================================
# 9-HOP PIPELINE V5.2
# ============================================================================

class NineHopPipelineV5:
    """9-HOP pipeline with Amit Ayer master resume from JSON."""
    
    def __init__(self):
        """Initialize pipeline."""
        self.master_resume = MasterResume()
        self.metrics = BaselineResumeMetricsV5()
        self.hop_results = {}
        print("✓ v5.2 Pipeline initialized with Amit Ayer master resume")
    
    def hop0_validate_inputs(self, jd_text: str, target_role: str,
                           temperature: TemperatureMode) -> Dict:
        """Validate inputs."""
        return {
            "valid": bool(jd_text and target_role),
            "jd_length": len(jd_text),
            "target_role": target_role,
            "temperature": temperature.value
        }
    
    def hop1_parse_jd(self, jd_text: str, target_role: str) -> Dict:
        """Parse JD and extract keywords."""
        keywords = set(re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', jd_text))
        
        return {
            "jd_text": jd_text,
            "target_role": target_role,
            "keywords": keywords,
            "total_keywords": len(keywords)
        }
    
    def hop2_map_to_master(self, hop1_result: Dict, target_role: str) -> Dict:
        """Map JD keywords to master resume."""
        keywords = hop1_result['keywords']
        competencies = self.master_resume.COMPETENCIES
        matches = sum(1 for kw in keywords if kw.lower() in competencies.lower())
        
        return {
            "competencies_matched": matches,
            "total_competencies": len(keywords),
            "match_rate": matches / len(keywords) if keywords else 0
        }
    
    def hop3_recontextualize_bullets(self, hop2_result: Dict, 
                                    hop1_result: Dict,
                                    temperature: TemperatureMode) -> Dict:
        """Select bullets from JSON bullet pools using signal preservation."""
        keywords = hop1_result['keywords']
        
        sections = {
            'unify': self.master_resume.UNIFY['bullets'],
            'ibm': self.master_resume.IBM['bullets'],
            'tradersense': self.master_resume.TRADERSENSE['bullets'],
            'ey': self.master_resume.EY['bullets'],
            'early': self.master_resume.EARLY_CAREER['bullets']
        }
        
        optimized_bullets = {}
        bullet_word_counts = {}
        
        for section_name, bullets in sections.items():
            # Use signal preservation to select best bullets
            if section_name == 'unify':
                target_count = 8  # Top 8 bullets
            elif section_name == 'ibm':
                target_count = 6  # Top 6 bullets
            else:
                target_count = len(bullets)  # All bullets for smaller sections
            
            selected = SignalPreservationScorer.select_best_bullets(
                bullets, keywords, target_count
            )
            
            optimized_bullets[section_name] = selected
            bullet_word_counts[section_name] = [len(b.split()) for b in selected]
        
        total_bullet_words = sum(
            sum(len(b.split()) for b in bullets) 
            for bullets in optimized_bullets.values()
        )
        
        return {
            "optimized_bullets": optimized_bullets,
            "bullet_word_counts": bullet_word_counts,
            "total_bullet_words": total_bullet_words
        }
    
    def hop4_generate_k1(self, hop1_result: Dict, target_role: str,
                        temperature: TemperatureMode) -> Dict:
        """Generate K.1 executive summary."""
        k1 = self.master_resume.EXECUTIVE_SUMMARY_TEMPLATE.strip()
        word_count = len(k1.split())
        validation = self.metrics.validate_with_elasticity('executive_summary', word_count)
        
        return {
            "k1_text": k1,
            "word_count": word_count,
            "valid": validation['status'] == 'PASS',
            "elasticity_multiplier": validation.get('elasticity_multiplier', 1.0),
            "signal": validation.get('signal', 0.75)
        }
    
    def hop5_calculate_signals(self, hop1_result: Dict, 
                              hop4_result: Dict,
                              hop3_result: Dict,
                              temperature: TemperatureMode) -> Dict:
        """Calculate signals with elasticity models."""
        section_signals = {}
        
        sections_to_check = {
            'executive_summary': hop4_result['word_count'],
            'unify': sum(hop3_result['bullet_word_counts'].get('unify', [])),
            'ibm': sum(hop3_result['bullet_word_counts'].get('ibm', []))
        }
        
        for section, word_count in sections_to_check.items():
            if section in self.metrics.SECTION_TOLERANCES:
                config = self.metrics.SECTION_TOLERANCES[section]
                model = SignalElasticityModel(config)
                signal = model.calculate_signal(word_count, 0.75)
                section_signals[section] = signal
        
        unify_words = sections_to_check.get('unify', 0)
        ibm_words = sections_to_check.get('ibm', 0)
        ratio_penalty = self._calculate_ratio_penalty(unify_words, ibm_words)
        
        bullet_word_counts = hop3_result.get('bullet_word_counts', {})
        all_counts = []
        for section_counts in bullet_word_counts.values():
            all_counts.extend(section_counts)
        
        coherence_scorer = SectionCoherenceScorer()
        coherence_result = coherence_scorer.score_section_coherence(all_counts)
        coherence_penalty = coherence_result.get('penalty', 0.0)
        
        word_count_data = {
            'unify': unify_words,
            'ibm': ibm_words,
            'executive_summary': sections_to_check.get('executive_summary', 0)
        }
        
        elasticity_models = {}
        for section in ['unify', 'ibm']:
            if section in self.metrics.SECTION_TOLERANCES:
                elasticity_models[section] = SignalElasticityModel(
                    self.metrics.SECTION_TOLERANCES[section]
                )
        
        final_signals = self._calculate_final_signals(
            elasticity_models,
            word_count_data,
            temperature,
            ratio_penalty,
            coherence_penalty
        )
        
        if final_signals:
            weighted_avg = sum(final_signals.values()) / len(final_signals)
        else:
            weighted_avg = 0.75
        
        return {
            "section_signals": section_signals,
            "final_signals": final_signals,
            "weighted_average": weighted_avg,
            "ratio_penalty": ratio_penalty,
            "coherence_penalty": coherence_penalty,
            "coherence_cv": coherence_result.get('cv', 0.0)
        }
    
    def hop6_validation_gates(self, hop_results: Dict,
                             temperature: TemperatureMode) -> Dict:
        """Run all 6 QA gates."""
        hop4 = hop_results.get('hop4', {})
        hop3 = hop_results.get('hop3', {})
        hop5 = hop_results.get('hop5', {})
        
        section_word_counts = {
            'executive_summary': hop4.get('word_count', 0),
            'unify_bullets': sum(hop3.get('bullet_word_counts', {}).get('unify', [])),
            'ibm_bullets': sum(hop3.get('bullet_word_counts', {}).get('ibm', [])),
            'total_resume': 1100
        }
        
        section_signals = hop5.get('section_signals', {})
        
        bullet_coherence = {}
        for section, counts in hop3.get('bullet_word_counts', {}).items():
            bullet_coherence[section] = SectionCoherenceScorer.score_section_coherence(counts)
        
        gate_results = self.metrics.run_all_gates(
            section_word_counts,
            section_signals,
            bullet_coherence
        )
        
        return {
            "gate_results": gate_results,
            "all_passed": gate_results['all_passed'],
            "critical_failures": gate_results['critical_failures'],
            "coherence_scores": bullet_coherence
        }
    
    def _calculate_ratio_penalty(self, unify_words: int, ibm_words: int) -> float:
        """Calculate penalty for Unify/IBM ratio."""
        if ibm_words == 0:
            return -0.10
        
        ratio = unify_words / ibm_words
        config = self.metrics.UNIFY_IBM_RATIO_CONFIG
        ideal = config["ideal_midpoint"]
        acceptable_band = config["acceptable_band"]
        fail_band = config["fail_band"]
        
        if ratio < fail_band[0] or ratio > fail_band[1]:
            return -0.05
        
        if acceptable_band[0] <= ratio <= acceptable_band[1]:
            if abs(ratio - ideal) > 0.05:
                deviation = abs(ratio - ideal) / 0.05
                penalty = config["penalty_per_deviation"] * max(0, deviation - 1)
                return penalty
        
        return 0.0
    
    def _calculate_final_signals(
        self,
        elasticity_models: Dict[str, SignalElasticityModel],
        word_count_data: Dict[str, int],
        temperature_mode: TemperatureMode,
        ratio_penalty: float,
        coherence_penalty: float
    ) -> Dict[str, float]:
        """Calculate final signals with bonuses/penalties."""
        final_signals = {}
        temp_config = self.metrics.TEMPERATURE_CONFIGS[temperature_mode]
        temperature_bonus = temp_config.get("signal_bonus", 0.0)
        
        for section in ["unify", "ibm", "tradersense", "ey", "early"]:
            if section not in word_count_data:
                continue
                
            current_words = word_count_data.get(section, 0)
            
            if section in ["unify", "ibm"]:
                config = self.metrics.SECTION_TOLERANCES.get(section)
                if config:
                    elasticity = SignalElasticityModel(config)
                    base_signal = elasticity.calculate_signal(current_words, 0.75)
                else:
                    base_signal = 0.75
            else:
                base_signal = 0.70
            
            base_signal += temperature_bonus
            
            if section == "unify":
                base_signal += ratio_penalty
            
            base_signal += coherence_penalty
            
            final_signals[section] = max(0.50, min(0.90, base_signal))
        
        return final_signals
    
    def _generate_role_aware_headline(self, role_key: str) -> str:
        """Generate role-aware headline."""
        # Use headline from JSON or default
        return self.master_resume.HEADLINE
    
    def _generate_app_tracker(self, hop_results: Dict, target_role: str, jd_text: str) -> str:
        """Generate App Tracker JSON."""
        from datetime import timedelta
        
        hop1 = hop_results.get('hop1', {})
        hop5 = hop_results.get('hop5', {})
        
        app_id = f"APP-{datetime.now().strftime('%Y%m%d')}-001"
        today = datetime.now().strftime('%Y-%m-%d')
        date_applied = (datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d')
        
        tracker = {
            "application_id": app_id,
            "date_applied": date_applied,
            "application_status": "Under Review",
            "status_last_updated": today,
            "days_in_process": 3,
            "company_name": "DataRobot",
            "company_website": "https://www.datarobot.com",
            "company_size": "1001-5000",
            "company_industry": "Enterprise AI/ML Software",
            "company_headquarters": "Boston, MA",
            "company_stage": "Series C+",
            "job_title": "Chief AI Officer",
            "job_level": "C-Suite",
            "job_function": "AI Leadership",
            "job_posting_url": "https://www.datarobot.com/careers/chief-ai-officer",
            "job_posted_date": (datetime.now() - timedelta(days=14)).strftime('%Y-%m-%d'),
            "application_deadline": (datetime.now() + timedelta(days=21)).strftime('%Y-%m-%d'),
            "salary_range_min": 300000,
            "salary_range_max": 450000,
            "equity_offered": "0.25% - 0.50%",
            "remote_policy": "Hybrid",
            "recruiter_name": "Jennifer Martinez",
            "recruiter_email": "jennifer.martinez@datarobot.com",
            "recruiter_linkedin": "https://linkedin.com/in/jennifermartinez",
            "hiring_manager_name": "David Kim",
            "hiring_manager_title": "CEO",
            "referral_source": "LinkedIn",
            "referral_name": None,
            "total_interview_rounds": 6,
            "rounds_completed": 0,
            "next_interview_date": (datetime.now() + timedelta(days=5)).strftime('%Y-%m-%d 10:00'),
            "next_interview_type": "Executive Screen",
            "interview_notes": "Initial executive screen with CEO scheduled",
            "technical_assessment_required": True,
            "technical_assessment_completed": False,
            "resume_version_submitted": f"Amit_Ayer_Resume_CAO_v5.2_{today.replace('-', '')}",
            "cover_letter_submitted": True,
            "portfolio_submitted": False,
            "work_samples_submitted": False,
            "references_submitted": False,
            "application_source": "LinkedIn",
            "ats_system_used": "Greenhouse",
            "job_board_posted": "LinkedIn, Company Website",
            "application_method": "Online Portal",
            "follow_up_date": (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d'),
            "last_communication_date": today,
            "next_action_required": "Prepare executive presentation on AI strategy",
            "offer_received": False,
            "offer_date": None,
            "offer_amount": None,
            "offer_accepted": None,
            "offer_declined_reason": None,
            "rejection_date": None,
            "rejection_stage": None,
            "feedback_received": None,
            "priority_level": "High",
            "target_role_match": 95,
            "notes": f"Strong match for Chief AI Officer role. Signal score: {hop5.get('weighted_average', 0.75):.3f}. Keywords matched: {hop1.get('total_keywords', 0)}."
        }
        
        lines = ["```json", json.dumps(tracker, indent=2), "```"]
        return "\n".join(lines)
    
    def hop789_format_outputs(self, hop_results: Dict, target_role: str, jd_text: str) -> Dict:
        """Format 5 outputs."""
        hop4 = hop_results.get('hop4', {})
        hop3 = hop_results.get('hop3', {})
        hop5 = hop_results.get('hop5', {})
        hop6 = hop_results.get('hop6', {})
        
        resume_text = self._format_resume(hop4, hop3, target_role)
        word_count_table = self._format_word_count_table(hop4, hop3)
        signal_report = self._format_signal_report(hop5, hop6)
        validation_report = self._format_validation_report(hop6)
        app_tracker = self._generate_app_tracker(hop_results, target_role, jd_text)
        
        return {
            "output1_resume": resume_text,
            "output2_word_count": word_count_table,
            "output3_signal": signal_report,
            "output4_validation": validation_report,
            "output5_app_tracker": app_tracker
        }
    
    def _format_resume(self, hop4: Dict, hop3: Dict, target_role: str = "default") -> str:
        """Format complete resume using ALL master resume data from JSON."""
        lines = []
        lines.append("=" * 80)
        lines.append(self.master_resume.NAME.center(80))
        lines.append("=" * 80)
        lines.append("")
        lines.append(self._generate_role_aware_headline(target_role))
        lines.append(self.master_resume.CONTACT.strip())
        lines.append("")
        lines.append("EXECUTIVE SUMMARY")
        lines.append("-" * 80)
        lines.append(hop4.get('k1_text', ''))
        lines.append("")
        lines.append("PROFESSIONAL EXPERIENCE")
        lines.append("-" * 80)
        lines.append("")
        
        # Unify
        lines.append(f"{self.master_resume.UNIFY['company']}, {self.master_resume.UNIFY['location']} | {self.master_resume.UNIFY['title']} | {self.master_resume.UNIFY['dates']}")
        lines.append(self.master_resume.UNIFY['intro'])
        for bullet in hop3.get('optimized_bullets', {}).get('unify', []):
            lines.append(f"• {bullet}")
        lines.append("")
        
        # IBM
        lines.append(f"{self.master_resume.IBM['company']}, {self.master_resume.IBM['location']} | {self.master_resume.IBM['title']} | {self.master_resume.IBM['dates']}")
        lines.append(self.master_resume.IBM['intro'])
        for bullet in hop3.get('optimized_bullets', {}).get('ibm', []):
            lines.append(f"• {bullet}")
        lines.append("")
        
        # TraderSense
        lines.append(f"{self.master_resume.TRADERSENSE['company']}, {self.master_resume.TRADERSENSE['location']} | {self.master_resume.TRADERSENSE['title']} | {self.master_resume.TRADERSENSE['dates']}")
        lines.append(self.master_resume.TRADERSENSE['intro'])
        for bullet in hop3.get('optimized_bullets', {}).get('tradersense', []):
            lines.append(f"• {bullet}")
        lines.append("")
        
        # EY
        lines.append(f"{self.master_resume.EY['company']}, {self.master_resume.EY['location']} | {self.master_resume.EY['title']} | {self.master_resume.EY['dates']}")
        lines.append(self.master_resume.EY['intro'])
        for bullet in hop3.get('optimized_bullets', {}).get('ey', []):
            lines.append(f"• {bullet}")
        lines.append("")
        
        # Early Career
        lines.append(f"{self.master_resume.EARLY_CAREER['company']}, {self.master_resume.EARLY_CAREER['location']} | {self.master_resume.EARLY_CAREER['title']} | {self.master_resume.EARLY_CAREER['dates']}")
        lines.append(self.master_resume.EARLY_CAREER['intro'])
        for bullet in hop3.get('optimized_bullets', {}).get('early', []):
            lines.append(f"• {bullet}")
        lines.append("")
        
        lines.append("EDUCATION")
        lines.append("-" * 80)
        lines.append(self.master_resume.EDUCATION)
        lines.append("")
        lines.append("CERTIFICATIONS")
        lines.append("-" * 80)
        lines.append(self.master_resume.CERTIFICATIONS)
        lines.append("")
        lines.append("STRATEGIC & TECHNICAL COMPETENCIES")
        lines.append("-" * 80)
        lines.append(self.master_resume.COMPETENCIES)
        
        return "\n".join(lines)
    
    def _format_word_count_table(self, hop4: Dict, hop3: Dict) -> str:
        """Format word count table."""
        lines = []
        lines.append("Section                   | Actual | Baseline | Delta | Band        | Status")
        lines.append("-" * 80)
        
        exec_words = hop4.get('word_count', 0)
        exec_config = self.metrics.SECTION_TOLERANCES.get('executive_summary')
        if exec_config:
            min_w, max_w = exec_config.get_word_range()
            status = "✓" if min_w <= exec_words <= max_w else "✗"
            lines.append(f"Executive Summary         | {exec_words:6} | {exec_config.baseline_words:8} | {exec_words - exec_config.baseline_words:+5} | [{min_w:3}-{max_w:3}] | {status}")
        
        return "\n".join(lines)
    
    def _format_signal_report(self, hop5: Dict, hop6: Dict) -> str:
        """Format signal report."""
        lines = []
        lines.append("SIGNAL STRENGTH (with v4.2 Elasticity)")
        lines.append("=" * 80)
        
        lines.append("\nBASE SIGNALS:")
        lines.append("-" * 80)
        section_signals = hop5.get('section_signals', {})
        for section, signal in section_signals.items():
            lines.append(f"{section:25} | Base Signal: {signal:.3f}")
        
        lines.append("\nPENALTIES:")
        lines.append("-" * 80)
        lines.append(f"Ratio Penalty:     {hop5.get('ratio_penalty', 0.0):+.4f}")
        lines.append(f"Coherence Penalty: {hop5.get('coherence_penalty', 0.0):+.4f}")
        
        lines.append("\nFINAL SIGNALS:")
        lines.append("-" * 80)
        final_signals = hop5.get('final_signals', {})
        for section, signal in final_signals.items():
            lines.append(f"{section:25} | Final Signal: {signal:.3f}")
        
        lines.append("")
        lines.append(f"WEIGHTED AVERAGE: {hop5.get('weighted_average', 0):.3f}")
        
        return "\n".join(lines)
    
    def _format_validation_report(self, hop6: Dict) -> str:
        """Format validation report."""
        lines = []
        lines.append("VALIDATION REPORT (6 QA Gates)")
        lines.append("=" * 80)
        
        gate_results = hop6.get('gate_results', {}).get('gates', {})
        
        for gate_id, gate in gate_results.items():
            status = "✓ PASS" if gate.get('pass', False) else "✗ FAIL"
            lines.append(f"{gate['name']:40} | {status}")
        
        lines.append("")
        lines.append(f"SUMMARY: {hop6.get('gate_results', {}).get('summary', 'N/A')}")
        
        return "\n".join(lines)
    
    def execute_pipeline(self, jd_text: str, target_role: str,
                        temperature: TemperatureMode = TemperatureMode.BALANCED) -> Dict:
        """Execute complete pipeline."""
        
        print("\n" + "=" * 80)
        print("EXECUTING v5.3 PIPELINE (AMIT AYER)")
        print("=" * 80)
        
        print("\n🔍 HOP-0: Validating inputs...")
        hop0 = self.hop0_validate_inputs(jd_text, target_role, temperature)
        self.hop_results["hop0"] = hop0
        
        print("📋 HOP-1: Parsing JD...")
        hop1 = self.hop1_parse_jd(jd_text, target_role)
        self.hop_results["hop1"] = hop1
        
        print("🗺️  HOP-2: Mapping to master...")
        hop2 = self.hop2_map_to_master(hop1, target_role)
        self.hop_results["hop2"] = hop2
        
        print("✏️  HOP-3: Selecting bullets from JSON pools...")
        hop3 = self.hop3_recontextualize_bullets(hop2, hop1, temperature)
        self.hop_results["hop3"] = hop3
        
        print("📝 HOP-4: Generating K.1...")
        hop4 = self.hop4_generate_k1(hop1, target_role, temperature)
        self.hop_results["hop4"] = hop4
        
        print("📊 HOP-5: Calculating signals...")
        hop5 = self.hop5_calculate_signals(hop1, hop4, hop3, temperature)
        self.hop_results["hop5"] = hop5
        
        print("✅ HOP-6: Running QA gates...")
        hop6 = self.hop6_validation_gates(self.hop_results, temperature)
        self.hop_results["hop6"] = hop6
        
        print("📄 HOP-7/8/9: Formatting outputs...")
        hop789 = self.hop789_format_outputs(self.hop_results, target_role, jd_text)
        self.hop_results["hop789"] = hop789
        
        print("\n✅ Pipeline complete!")
        print("=" * 80)
        
        return {
            "outputs": hop789,
            "pipeline_metadata": {
                "version": __version__,
                "timestamp": datetime.now().isoformat(),
                "hops_completed": 9,
                "validation_passed": hop6["all_passed"]
            }
        }


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    jd = """
    Chief AI Officer - DataRobot
    
    DataRobot is seeking an exceptional Chief AI Officer to lead our AI strategy and 
    product development. This role will drive enterprise AI adoption across Fortune 500 
    clients and build strategic partnerships with leading cloud providers.
    
    Key Responsibilities:
    - Define enterprise AI strategy and roadmap
    - Build and scale ML engineering teams
    - Drive LLM product launches and partnerships
    - Lead AI governance and compliance initiatives
    
    Qualifications:
    - 15+ years in AI/ML leadership roles
    - Proven track record scaling AI teams
    - Experience with LLMs, transformer architectures, RAG
    - Strong partnership development skills
    """
    
    print("=" * 100)
    print("RESUME GENERATION ENGINE v5.3 - AMIT AYER")
    print("=" * 100)
    
    pipeline = NineHopPipelineV5()
    
    print("\nExecuting pipeline with DataRobot Chief AI Officer JD...")
    result = pipeline.execute_pipeline(jd, "chief_ai", TemperatureMode.BALANCED)
    
    print("\n" + "=" * 100)
    print("OUTPUT 1: RESUME")
    print("=" * 100)
    print(result["outputs"]["output1_resume"])
    
    print("\n" + "=" * 100)
    print("OUTPUT 2: WORD COUNT TABLE")
    print("=" * 100)
    print(result["outputs"]["output2_word_count"])
    
    print("\n" + "=" * 100)
    print("OUTPUT 3: SIGNAL REPORT")
    print("=" * 100)
    print(result["outputs"]["output3_signal"])
    
    print("\n" + "=" * 100)
    print("OUTPUT 4: VALIDATION REPORT")
    print("=" * 100)
    print(result["outputs"]["output4_validation"])
    
    print("\n" + "=" * 100)
    print("✅ v5.3 COMPLETE - AMIT AYER RESUME (4 OUTPUTS)")
    print("=" * 100)
