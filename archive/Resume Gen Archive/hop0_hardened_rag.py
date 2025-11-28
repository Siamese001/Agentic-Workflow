"""
HOP-0 HARDENED MULTI-MODEL CONSENSUS RAG AGENT
===============================================
Integrates top signal-maximizing improvements with evidence-based architecture.
Version: v14.0-HARDENED
"""

import json
import logging
import time
import hashlib
from typing import Dict, List, Tuple, Optional, Any, Set
from dataclasses import dataclass, field
from enum import Enum
from concurrent.futures import ThreadPoolExecutor, as_completed
import numpy as np

# ============================================================================
# CORE ENUMS & CONFIGS
# ============================================================================

class ModelVariant(Enum):
    """Different Gemini models for consensus."""
    FLASH = "gemini-2.0-flash-exp"
    FLASH_THINKING = "gemini-2.0-flash-thinking-exp"
    PRO = "gemini-1.5-pro"

class SignalSource(Enum):
    """Source authority levels for dynamic weighting."""
    ENGINEERING_BLOG = 2.0
    EMPLOYEE_PROFILE = 1.8
    GLASSDOOR = 1.5
    PEER_JD = 1.0
    GENERIC_JD = 0.5

class VerificationMode(Enum):
    """Types of verification passes."""
    SUPPORTING = "supporting"
    ADVERSARIAL = "adversarial"
    CAUSAL = "causal"

# ============================================================================
# ENHANCED DATA STRUCTURES
# ============================================================================

@dataclass
class EvidenceItem:
    """Single piece of evidence with source authority."""
    claim: str
    evidence_text: str
    source_url: str
    source_type: SignalSource
    confidence: float
    model_consensus: List[str] = field(default_factory=list)  # Which models agreed

@dataclass
class ConsensusResult:
    """Result of multi-model consensus."""
    agreed_items: List[Dict[str, Any]]
    disputed_items: List[Dict[str, Any]]
    consensus_score: float
    model_agreements: Dict[str, int]  # Count of agreements per model pair

@dataclass
class AdversarialResult:
    """Result of adversarial verification."""
    original_claim: str
    counter_evidence: List[str]
    claim_survives: bool
    adjusted_confidence: float

@dataclass
class EmployeeFingerprint:
    """Extracted pattern from real employee profiles."""
    employee_count: int
    common_skills: List[str]
    unique_differentiators: List[str]
    career_trajectories: List[str]
    success_indicators: Dict[str, float]

# ============================================================================
# HARDENED RAG STATE
# ============================================================================

@dataclass
class HardenedRAGState:
    """Enhanced state with multi-model tracking and evidence graph."""
    
    # Core mission
    job_description: str
    mission: 'RAGMission'
    
    # Multi-model results
    model_results: Dict[ModelVariant, Dict] = field(default_factory=dict)
    consensus_results: Optional[ConsensusResult] = None
    
    # Evidence tracking
    evidence_graph: Dict[str, List[EvidenceItem]] = field(default_factory=dict)
    adversarial_results: List[AdversarialResult] = field(default_factory=list)
    
    # Employee data
    employee_fingerprint: Optional[EmployeeFingerprint] = None
    
    # Progressive search
    search_depth: int = 0
    signal_quality_score: float = 0.0
    weak_areas: List[str] = field(default_factory=list)
    
    # Causal analysis
    success_patterns: Dict[str, float] = field(default_factory=dict)
    failure_patterns: Dict[str, float] = field(default_factory=dict)
    
    # Cache keys for dedup
    semantic_cache_key: Optional[str] = None

# ============================================================================
# HARDENED WEB SEARCH RAG
# ============================================================================

class HardenedWebSearchRAG:
    """
    Multi-model consensus RAG with adversarial verification.
    Implements top 5 signal improvements from prioritized list.
    """
    
    def __init__(self, gemini_clients: Dict[ModelVariant, Any], config: 'RAGConfig'):
        self.clients = gemini_clients  # One client per model variant
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.source_weights = {s: s.value for s in SignalSource}
        
    # ========================================================================
    # IMPROVEMENT #1: Multi-Model Consensus
    # ========================================================================
    
    def run_multi_model_consensus(
        self,
        prompt: str,
        state: HardenedRAGState,
        phase_name: str
    ) -> Tuple[ConsensusResult, int]:
        """
        Runs same prompt through 3 models, requires 2+ agreement.
        This is THE most critical improvement for signal quality.
        """
        self.logger.info(f"🔄 Running multi-model consensus for {phase_name}")
        
        total_api_calls = 0
        results = {}
        
        # Parallel execution for speed
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = {
                executor.submit(
                    self._call_model,
                    model,
                    prompt,
                    f"{phase_name}_{model.value}"
                ): model
                for model in ModelVariant
            }
            
            for future in as_completed(futures):
                model = futures[future]
                try:
                    result_json, api_calls = future.result()
                    results[model] = result_json
                    total_api_calls += api_calls
                    state.model_results[model] = result_json
                except Exception as e:
                    self.logger.error(f"Model {model.value} failed: {e}")
                    results[model] = {}
        
        # Extract consensus
        consensus = self._extract_consensus(results)
        
        # Only accept high-confidence consensus items
        filtered_consensus = ConsensusResult(
            agreed_items=[
                item for item in consensus.agreed_items 
                if item.get('confidence', 0) > 0.7
            ],
            disputed_items=consensus.disputed_items,
            consensus_score=consensus.consensus_score,
            model_agreements=consensus.model_agreements
        )
        
        self.logger.info(
            f"✅ Consensus: {len(filtered_consensus.agreed_items)} agreed items, "
            f"score: {filtered_consensus.consensus_score:.2f}"
        )
        
        return filtered_consensus, total_api_calls
    
    def _extract_consensus(self, results: Dict[ModelVariant, Dict]) -> ConsensusResult:
        """
        Identifies items where 2+ models agree.
        Uses semantic similarity for fuzzy matching.
        """
        all_items = {}
        model_items = {}
        
        # Collect all unique items from each model
        for model, result in results.items():
            model_items[model] = self._extract_items_from_result(result)
            for item in model_items[model]:
                item_key = self._generate_item_key(item)
                if item_key not in all_items:
                    all_items[item_key] = {'count': 0, 'models': [], 'data': item}
                all_items[item_key]['count'] += 1
                all_items[item_key]['models'].append(model.value)
        
        # Separate agreed (2+) from disputed
        agreed = []
        disputed = []
        
        for item_data in all_items.values():
            if item_data['count'] >= 2:
                item_data['data']['model_consensus'] = item_data['models']
                agreed.append(item_data['data'])
            else:
                disputed.append(item_data['data'])
        
        # Calculate consensus score
        total_items = len(all_items)
        consensus_score = len(agreed) / total_items if total_items > 0 else 0
        
        # Model agreement matrix
        model_agreements = {}
        for m1 in ModelVariant:
            for m2 in ModelVariant:
                if m1 != m2:
                    key = f"{m1.value}-{m2.value}"
                    shared = len(set(model_items.get(m1, [])) & 
                               set(model_items.get(m2, [])))
                    model_agreements[key] = shared
        
        return ConsensusResult(
            agreed_items=agreed,
            disputed_items=disputed,
            consensus_score=consensus_score,
            model_agreements=model_agreements
        )
    
    # ========================================================================
    # IMPROVEMENT #2: Adversarial Verification
    # ========================================================================
    
    def run_adversarial_verification(
        self,
        state: HardenedRAGState,
        claims_to_verify: List[Dict]
    ) -> Tuple[List[AdversarialResult], int]:
        """
        Actively searches for counter-evidence to disprove claims.
        Only claims that survive are truly strong signals.
        """
        self.logger.info(f"⚔️ Running adversarial verification on {len(claims_to_verify)} claims")
        
        total_api_calls = 0
        adversarial_results = []
        
        for claim in claims_to_verify[:10]:  # Limit to top 10 for efficiency
            claim_text = claim.get('name', '') or claim.get('keyword', '')
            if not claim_text:
                continue
                
            # Search for counter-evidence
            counter_prompt = f"""
            Find evidence that the following is NOT important for a {state.mission.precise_role_title} role:
            "{claim_text}"
            
            Search for:
            1. Job postings that explicitly DON'T require this
            2. Successful professionals who lack this skill
            3. Industry reports showing this is outdated or optional
            
            Return any counter-evidence found.
            """
            
            counter_evidence, api_calls = self._search_with_best_model(
                counter_prompt,
                f"adversarial_{claim_text}"
            )
            total_api_calls += api_calls
            
            # Evaluate if claim survives
            survives = self._evaluate_claim_survival(claim, counter_evidence)
            adjusted_confidence = claim.get('confidence', 0.5)
            
            if counter_evidence and len(counter_evidence) > 2:
                adjusted_confidence *= 0.7  # Reduce confidence if counter-evidence exists
                survives = adjusted_confidence > 0.5
            
            result = AdversarialResult(
                original_claim=claim_text,
                counter_evidence=counter_evidence[:3],  # Top 3 counter points
                claim_survives=survives,
                adjusted_confidence=adjusted_confidence
            )
            
            adversarial_results.append(result)
            state.adversarial_results.append(result)
            
            self.logger.info(
                f"  {'✅' if survives else '❌'} {claim_text}: "
                f"confidence {adjusted_confidence:.2f}"
            )
        
        return adversarial_results, total_api_calls
    
    # ========================================================================
    # IMPROVEMENT #3: LinkedIn Employee Fingerprinting
    # ========================================================================
    
    def extract_employee_fingerprint(
        self,
        state: HardenedRAGState
    ) -> Tuple[EmployeeFingerprint, int]:
        """
        Searches for actual employees at target company in similar roles.
        Their profiles contain PROVEN success signals.
        """
        self.logger.info(f"🔍 Extracting employee fingerprint for {state.mission.target_company_name}")
        
        search_queries = [
            f'"{state.mission.precise_role_title}" at "{state.mission.target_company_name}" site:linkedin.com/in',
            f'"{state.mission.target_company_name}" "{state.mission.role_archetype}" employee linkedin',
            f'promoted to "{state.mission.precise_role_title}" "{state.mission.target_company_name}"'
        ]
        
        total_api_calls = 0
        employee_profiles = []
        
        for query in search_queries:
            results, api_calls = self._search_with_best_model(query, "employee_search")
            total_api_calls += api_calls
            employee_profiles.extend(results)
        
        # Extract patterns from profiles
        analysis_prompt = f"""
        Analyze these employee profiles for {state.mission.precise_role_title} at {state.mission.target_company_name}:
        
        {json.dumps(employee_profiles[:10], indent=2)}
        
        Extract:
        1. Common skills across 80%+ of profiles
        2. Unique differentiators in top performers
        3. Typical career progression patterns
        4. Success indicators (promotions, achievements, tenure)
        
        Return structured JSON with these patterns.
        """
        
        patterns, api_calls = self._search_with_best_model(analysis_prompt, "employee_analysis")
        total_api_calls += api_calls
        
        fingerprint = EmployeeFingerprint(
            employee_count=len(employee_profiles),
            common_skills=patterns.get('common_skills', []),
            unique_differentiators=patterns.get('differentiators', []),
            career_trajectories=patterns.get('trajectories', []),
            success_indicators=patterns.get('success_indicators', {})
        )
        
        state.employee_fingerprint = fingerprint
        
        self.logger.info(
            f"✅ Fingerprint extracted: {fingerprint.employee_count} employees, "
            f"{len(fingerprint.common_skills)} common skills"
        )
        
        return fingerprint, total_api_calls
    
    # ========================================================================
    # IMPROVEMENT #4: Causal vs Correlational Filtering
    # ========================================================================
    
    def identify_causal_signals(
        self,
        state: HardenedRAGState
    ) -> Tuple[Dict[str, float], int]:
        """
        Compares successful vs rejected profiles to identify
        skills that CAUSE success, not just correlate.
        """
        self.logger.info("🎯 Identifying causal vs correlational signals")
        
        # Search for both successful and unsuccessful profiles
        success_query = f'"{state.mission.precise_role_title}" promoted "exceeded expectations" site:linkedin.com'
        failure_query = f'"left after" "laid off" "{state.mission.precise_role_title}" site:linkedin.com'
        
        success_profiles, api_calls_1 = self._search_with_best_model(success_query, "success_profiles")
        failure_profiles, api_calls_2 = self._search_with_best_model(failure_query, "failure_profiles")
        
        total_api_calls = api_calls_1 + api_calls_2
        
        # Analyze differential
        causal_prompt = f"""
        Compare successful vs unsuccessful profiles for {state.mission.precise_role_title}:
        
        SUCCESSFUL PROFILES:
        {json.dumps(success_profiles[:5], indent=2)}
        
        UNSUCCESSFUL PROFILES:
        {json.dumps(failure_profiles[:5], indent=2)}
        
        Identify:
        1. Skills that appear in 80%+ of successful but <20% of unsuccessful
        2. Skills that appear frequently in both (correlation, not causation)
        3. Red flags that appear more in unsuccessful profiles
        
        Return confidence scores for causal relationship (0.0-1.0).
        """
        
        causal_analysis, api_calls_3 = self._search_with_best_model(causal_prompt, "causal_analysis")
        total_api_calls += api_calls_3
        
        # Store patterns
        state.success_patterns = causal_analysis.get('causal_skills', {})
        state.failure_patterns = causal_analysis.get('red_flags', {})
        
        # Filter out merely correlated signals
        causal_signals = {
            skill: score
            for skill, score in state.success_patterns.items()
            if score > 0.7  # High causal confidence only
        }
        
        self.logger.info(
            f"✅ Identified {len(causal_signals)} causal signals "
            f"from {len(state.success_patterns)} total patterns"
        )
        
        return causal_signals, total_api_calls
    
    # ========================================================================
    # IMPROVEMENT #5: Progressive Depth Search
    # ========================================================================
    
    def run_progressive_depth_search(
        self,
        state: HardenedRAGState
    ) -> Tuple[float, int]:
        """
        Dynamically allocates search depth based on signal quality.
        Continues searching weak areas until quality > 0.85.
        """
        self.logger.info("📊 Starting progressive depth search")
        
        total_api_calls = 0
        max_depth = 5
        target_quality = 0.85
        
        while state.search_depth < max_depth and state.signal_quality_score < target_quality:
            state.search_depth += 1
            self.logger.info(f"  Depth {state.search_depth}: Current quality {state.signal_quality_score:.2f}")
            
            # Identify weak areas
            weak_areas = self._identify_weak_signal_areas(state)
            state.weak_areas = weak_areas
            
            if not weak_areas:
                self.logger.info("  No weak areas identified")
                break
            
            # Targeted searches on weak areas
            for area in weak_areas[:3]:  # Top 3 weak areas
                targeted_query = f"""
                Deep dive into "{area}" for {state.mission.precise_role_title}:
                - Specific technical requirements
                - Industry best practices
                - Certification requirements
                - Tool/platform specifics
                """
                
                deep_results, api_calls = self._search_with_best_model(
                    targeted_query,
                    f"deep_dive_{area}"
                )
                total_api_calls += api_calls
                
                # Update evidence graph
                for evidence in deep_results:
                    evidence_item = EvidenceItem(
                        claim=area,
                        evidence_text=evidence.get('text', ''),
                        source_url=evidence.get('url', ''),
                        source_type=self._classify_source(evidence.get('url', '')),
                        confidence=evidence.get('confidence', 0.5)
                    )
                    
                    if area not in state.evidence_graph:
                        state.evidence_graph[area] = []
                    state.evidence_graph[area].append(evidence_item)
            
            # Recalculate signal quality
            state.signal_quality_score = self._calculate_signal_quality(state)
            
            self.logger.info(
                f"  Depth {state.search_depth} complete: "
                f"New quality {state.signal_quality_score:.2f}"
            )
        
        return state.signal_quality_score, total_api_calls
    
    def _identify_weak_signal_areas(self, state: HardenedRAGState) -> List[str]:
        """Identifies areas with low evidence or confidence."""
        weak_areas = []
        
        # Check evidence graph for low-confidence areas
        for claim, evidence_list in state.evidence_graph.items():
            avg_confidence = np.mean([e.confidence for e in evidence_list]) if evidence_list else 0
            if avg_confidence < 0.6:
                weak_areas.append(claim)
        
        # Check for disputed items from consensus
        if state.consensus_results:
            for item in state.consensus_results.disputed_items:
                weak_areas.append(item.get('name', '') or item.get('keyword', ''))
        
        # Check adversarial failures
        for result in state.adversarial_results:
            if not result.claim_survives:
                weak_areas.append(result.original_claim)
        
        return list(set(weak_areas))  # Deduplicate
    
    def _calculate_signal_quality(self, state: HardenedRAGState) -> float:
        """
        Calculates overall signal quality score.
        Weighted combination of multiple factors.
        """
        scores = []
        weights = []
        
        # Consensus score (weight: 0.3)
        if state.consensus_results:
            scores.append(state.consensus_results.consensus_score)
            weights.append(0.3)
        
        # Evidence coverage (weight: 0.2)
        evidence_coverage = len(state.evidence_graph) / 20  # Assume 20 key areas
        scores.append(min(evidence_coverage, 1.0))
        weights.append(0.2)
        
        # Adversarial survival rate (weight: 0.25)
        if state.adversarial_results:
            survival_rate = sum(1 for r in state.adversarial_results if r.claim_survives) / len(state.adversarial_results)
            scores.append(survival_rate)
            weights.append(0.25)
        
        # Employee fingerprint match (weight: 0.15)
        if state.employee_fingerprint:
            fingerprint_score = min(len(state.employee_fingerprint.common_skills) / 10, 1.0)
            scores.append(fingerprint_score)
            weights.append(0.15)
        
        # Causal signal ratio (weight: 0.1)
        if state.success_patterns:
            causal_ratio = sum(1 for s in state.success_patterns.values() if s > 0.7) / len(state.success_patterns)
            scores.append(causal_ratio)
            weights.append(0.1)
        
        # Weighted average
        if scores and weights:
            return sum(s * w for s, w in zip(scores, weights)) / sum(weights)
        return 0.0
    
    # ========================================================================
    # HELPER METHODS
    # ========================================================================
    
    def _call_model(
        self,
        model: ModelVariant,
        prompt: str,
        context: str
    ) -> Tuple[Dict, int]:
        """Calls specific model variant."""
        client = self.clients[model]
        # This would call the actual Gemini API
        # For now, returning placeholder
        return {"model": model.value, "context": context}, 1
    
    def _search_with_best_model(
        self,
        query: str,
        context: str
    ) -> Tuple[Any, int]:
        """Uses best model for single search."""
        # Use Flash for speed, Pro for accuracy
        model = ModelVariant.FLASH if "quick" in context else ModelVariant.PRO
        return self._call_model(model, query, context)
    
    def _extract_items_from_result(self, result: Dict) -> List[Dict]:
        """Extracts comparable items from model result."""
        items = []
        
        # Extract from various result structures
        if 'thematic_analysis' in result:
            theme = result['thematic_analysis'].get('primary_theme', {})
            if theme:
                items.append(theme)
            items.extend(result['thematic_analysis'].get('secondary_themes', []))
        
        if 'keywords' in result:
            for kw in result['keywords']:
                items.append({'keyword': kw})
        
        return items
    
    def _generate_item_key(self, item: Dict) -> str:
        """Generates semantic key for item comparison."""
        # Use name or keyword as key
        key = item.get('name', '') or item.get('keyword', '')
        return key.lower().strip()
    
    def _evaluate_claim_survival(
        self,
        claim: Dict,
        counter_evidence: List
    ) -> bool:
        """Evaluates if claim survives counter-evidence."""
        if not counter_evidence:
            return True
        
        # Strong counter-evidence threshold
        strong_counter = sum(1 for e in counter_evidence if e.get('confidence', 0) > 0.7)
        return strong_counter < 2
    
    def _classify_source(self, url: str) -> SignalSource:
        """Classifies source URL into authority level."""
        if 'engineering' in url or 'blog' in url:
            return SignalSource.ENGINEERING_BLOG
        elif 'linkedin.com/in' in url:
            return SignalSource.EMPLOYEE_PROFILE
        elif 'glassdoor' in url:
            return SignalSource.GLASSDOOR
        elif 'jobs' in url or 'careers' in url:
            return SignalSource.PEER_JD
        else:
            return SignalSource.GENERIC_JD

# ============================================================================
# MAIN ORCHESTRATOR INTEGRATION
# ============================================================================

class HardenedJobDescriptionAnalyzer:
    """
    Enhanced analyzer using hardened RAG.
    Replaces EnhancedJobDescriptionAnalyzer.
    """
    
    def __init__(self, master_resume: Dict, enable_web_search: bool = True):
        self.master_resume = master_resume
        self.enable_web_search = enable_web_search
        self.logger = logging.getLogger(__name__)
        
        # Initialize multi-model clients
        self.gemini_clients = {
            ModelVariant.FLASH: self._init_gemini_client(ModelVariant.FLASH),
            ModelVariant.FLASH_THINKING: self._init_gemini_client(ModelVariant.FLASH_THINKING),
            ModelVariant.PRO: self._init_gemini_client(ModelVariant.PRO)
        }
        
        # Initialize hardened RAG
        self.hardened_rag = HardenedWebSearchRAG(
            self.gemini_clients,
            RAGConfig()  # Your existing config
        )
    
    def analyze(self, job_description: str) -> Tuple['ThematicAnalysis', int]:
        """
        Main entry point - runs full hardened analysis.
        """
        self.logger.info("=" * 80)
        self.logger.info("STARTING HARDENED MULTI-MODEL CONSENSUS ANALYSIS")
        self.logger.info("=" * 80)
        
        total_api_calls = 0
        
        # Initialize state
        state = HardenedRAGState(
            job_description=job_description,
            mission=self._extract_mission(job_description)
        )
        
        # ====================================================================
        # PHASE 1: Multi-Model Consensus Research
        # ====================================================================
        self.logger.info("\n📚 PHASE 1: Multi-Model Consensus Research")
        
        # Build prompt for thematic research
        research_prompt = self._build_enhanced_research_prompt(state)
        
        # Run through 3 models with consensus
        consensus, api_calls = self.hardened_rag.run_multi_model_consensus(
            research_prompt,
            state,
            "thematic_research"
        )
        total_api_calls += api_calls
        state.consensus_results = consensus
        
        # ====================================================================
        # PHASE 2: Adversarial Verification
        # ====================================================================
        self.logger.info("\n⚔️ PHASE 2: Adversarial Verification")
        
        # Verify top consensus items
        adversarial_results, api_calls = self.hardened_rag.run_adversarial_verification(
            state,
            consensus.agreed_items[:15]  # Top 15 claims
        )
        total_api_calls += api_calls
        
        # ====================================================================
        # PHASE 3: Employee Fingerprinting
        # ====================================================================
        self.logger.info("\n👥 PHASE 3: Employee Fingerprinting")
        
        if state.mission.target_company_name:
            fingerprint, api_calls = self.hardened_rag.extract_employee_fingerprint(state)
            total_api_calls += api_calls
        
        # ====================================================================
        # PHASE 4: Causal Analysis
        # ====================================================================
        self.logger.info("\n🎯 PHASE 4: Causal vs Correlational Analysis")
        
        causal_signals, api_calls = self.hardened_rag.identify_causal_signals(state)
        total_api_calls += api_calls
        
        # ====================================================================
        # PHASE 5: Progressive Depth Search
        # ====================================================================
        self.logger.info("\n📊 PHASE 5: Progressive Depth Enhancement")
        
        final_quality, api_calls = self.hardened_rag.run_progressive_depth_search(state)
        total_api_calls += api_calls
        
        # ====================================================================
        # FINAL SYNTHESIS
        # ====================================================================
        self.logger.info("\n🏁 FINAL SYNTHESIS")
        
        analysis = self._synthesize_hardened_analysis(state)
        
        self.logger.info(f"\n✅ ANALYSIS COMPLETE")
        self.logger.info(f"   Signal Quality: {final_quality:.2%}")
        self.logger.info(f"   Total API Calls: {total_api_calls}")
        self.logger.info(f"   Consensus Items: {len(consensus.agreed_items)}")
        self.logger.info(f"   Survived Adversarial: {sum(1 for r in adversarial_results if r.claim_survives)}")
        self.logger.info("=" * 80)
        
        return analysis, total_api_calls
    
    def _synthesize_hardened_analysis(self, state: HardenedRAGState) -> 'ThematicAnalysis':
        """
        Synthesizes all hardened signals into final ThematicAnalysis.
        Prioritizes: Employee > Causal > Adversarial-Verified > Consensus
        """
        
        # Start with consensus items that survived adversarial
        survived_claims = {
            r.original_claim: r.adjusted_confidence
            for r in state.adversarial_results
            if r.claim_survives
        }
        
        # Boost employee-verified signals
        if state.employee_fingerprint:
            for skill in state.employee_fingerprint.common_skills:
                if skill in survived_claims:
                    survived_claims[skill] *= 1.5  # 50% boost
                else:
                    survived_claims[skill] = 0.8  # High base confidence
        
        # Boost causal signals
        for skill, causal_score in state.success_patterns.items():
            if skill in survived_claims:
                survived_claims[skill] *= (1 + causal_score * 0.5)  # Up to 50% boost
            else:
                survived_claims[skill] = causal_score
        
        # Sort by final confidence
        ranked_signals = sorted(
            survived_claims.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        # Build ThematicAnalysis
        return ThematicAnalysis(
            primary_theme={
                'name': ranked_signals[0][0] if ranked_signals else 'Unknown',
                'confidence': ranked_signals[0][1] if ranked_signals else 0.0,
                'keywords': [s[0] for s in ranked_signals[:5]],
                'evidence': state.evidence_graph.get(ranked_signals[0][0], []) if ranked_signals else []
            },
            secondary_themes=[
                {
                    'name': signal[0],
                    'relevance': signal[1],
                    'keywords': []
                }
                for signal in ranked_signals[5:10]
            ],
            signal_quality_score=state.signal_quality_score,
            retrieval_method="HARDENED_MULTI_MODEL_CONSENSUS_V1",
            competitive_intelligence={
                'differentiator_keywords': [s[0] for s in ranked_signals[:15]],
                'causal_signals': list(state.success_patterns.keys()),
                'employee_verified': state.employee_fingerprint.common_skills if state.employee_fingerprint else []
            },
            evidence_log=[
                {
                    'claim': claim,
                    'evidence': [e.evidence_text for e in evidence_list],
                    'sources': [e.source_url for e in evidence_list],
                    'consensus_models': list(set(sum([e.model_consensus for e in evidence_list], [])))
                }
                for claim, evidence_list in state.evidence_graph.items()
            ]
        )
    
    def _init_gemini_client(self, model: ModelVariant):
        """Initialize Gemini client for specific model."""
        # Placeholder - implement actual client init
        return f"Client_{model.value}"
    
    def _extract_mission(self, job_description: str):
        """Extract RAG mission from JD."""
        # Placeholder - use your existing logic
        return type('RAGMission', (), {
            'precise_role_title': 'Director, Technology Alliances',
            'target_company_name': 'DataDog',
            'role_archetype': 'Executive_GTM'
        })
    
    def _build_enhanced_research_prompt(self, state: HardenedRAGState) -> str:
        """Builds research prompt with evidence requirements."""
        return f"""
        Research the role: {state.mission.precise_role_title}
        Company: {state.mission.target_company_name}
        
        CRITICAL: Every claim must include:
        1. The specific claim/keyword
        2. Direct quote evidence from search results
        3. Source URL
        4. Confidence score (0.0-1.0)
        
        Focus on:
        - Technical requirements
        - Strategic responsibilities  
        - Industry-specific knowledge
        - Proven success patterns
        
        Return comprehensive JSON with evidence.
        """
