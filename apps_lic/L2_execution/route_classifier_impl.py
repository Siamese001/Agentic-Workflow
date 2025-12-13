"""Implementation for route_classifier."""

from typing import Any, Dict, List, Optional
from .route_classifier_types import *

class RouteClassifier:
    """
    K.1 - Routing & Archetype Classification
    
    Precedence Rules:
    - CXO Precedence: ['Chief', 'Head of', 'VP'] → force C_LEVEL
    - Premium Gate: If Premium=False, BLOCK INMAIL, force CONNECTION_REQ
    """
    CXO_TITLE_PATTERNS = ['Chief', 'CEO', 'CFO', 'CTO', 'COO', 'CMO', 'CISO', 'CIO', 'CPO', 'Head of', 'VP', 'Vice President', 'SVP', 'EVP']
    RECRUITER_TITLE_PATTERNS = ['Recruiter', 'Talent Acquisition', 'Talent Partner', 'Hiring Manager', 'HR', 'Human Resources', 'People Operations', 'Staffing']

    def __init__(self, config: Optional[RouteClassifierConfig]=None, gate_executor: Optional[IntegrityGateExecutor]=None):
        self.config = config or RouteClassifierConfig()
        self.gate_executor = gate_executor or IntegrityGateExecutor()

    def classify(self, profile: Dict[str, Any]) -> ClassificationResult:
        """
        Classify route and archetype for LinkedIn profile.
        
        Args:
            profile: Profile data including title, premium status, etc.
            
        Returns:
            ClassificationResult with route, archetype, and validation
        """
        validation_results = []
        title = profile.get('title', '')
        is_premium = profile.get('premium', False)
        connection_degree = profile.get('connection_degree', 3)
        archetype = self._detect_archetype(title)
        route = self._determine_route(archetype=archetype, is_premium=is_premium, connection_degree=connection_degree)
        premium_gate_result = self._validate_premium_gate(route, is_premium)
        validation_results.append(premium_gate_result)
        if not premium_gate_result.passed:
            route = RouteType.CONNECTION_REQ
            override_result = ValidationResult(gate_id='VG_ROUTE_OVERRIDE', passed=True, severity='INFO', message=f'Route overridden to CONNECTION_REQ due to premium gate failure', details={'original_route': route.value, 'new_route': 'CONNECTION_REQ'})
            validation_results.append(override_result)
        cxo_precedence_result = self._validate_cxo_precedence(title, archetype)
        validation_results.append(cxo_precedence_result)
        self.gate_executor.results = validation_results
        return ClassificationResult(route=route, archetype=archetype, confidence=0.95 if archetype != ArchetypeType.UNKNOWN else 0.5, validation_results=validation_results, success=True, details={'title': title, 'is_premium': is_premium, 'connection_degree': connection_degree})

    def _detect_archetype(self, title: str) -> ArchetypeType:
        """
        Detect archetype from title with CXO precedence.
        CXO patterns take absolute precedence.
        """
        title_lower = title.lower()
        for pattern in self.CXO_TITLE_PATTERNS:
            if pattern.lower() in title_lower:
                if any((vp in pattern.lower() for vp in ['vp', 'vice president'])):
                    return ArchetypeType.VP_LEVEL
                return ArchetypeType.C_LEVEL
        for pattern in self.RECRUITER_TITLE_PATTERNS:
            if pattern.lower() in title_lower:
                return ArchetypeType.RECRUITER
        if 'director' in title_lower:
            return ArchetypeType.DIRECTOR
        if 'manager' in title_lower:
            return ArchetypeType.MANAGER
        return ArchetypeType.UNKNOWN

    def _determine_route(self, archetype: ArchetypeType, is_premium: bool, connection_degree: int) -> RouteType:
        """
        Determine optimal route based on archetype and premium status.
        Premium gate enforced separately.
        """
        if archetype == ArchetypeType.C_LEVEL and is_premium:
            return RouteType.INMAIL
        if archetype == ArchetypeType.RECRUITER:
            return RouteType.SHORT_NEW
        if connection_degree <= 2:
            return RouteType.CONNECTION_REQ
        if is_premium:
            return RouteType.INMAIL
        return RouteType.CONNECTION_REQ

    def _validate_premium_gate(self, route: RouteType, is_premium: bool) -> ValidationResult:
        """
        Validate premium gate constraint.
        BLOCKS INMAIL if Premium=False.
        """
        if route == RouteType.INMAIL and (not is_premium):
            return ValidationResult(gate_id='VG_PREMIUM_GATE', passed=False, severity='BLOCK', message='BLOCKED: INMAIL route requires premium account', details={'route': route.value, 'is_premium': is_premium})
        return ValidationResult(gate_id='VG_PREMIUM_GATE', passed=True, severity='INFO', message=f'Premium gate passed for route {route.value}', signature=f'PREMIUM:OK:{route.value}')

    def _validate_cxo_precedence(self, title: str, archetype: ArchetypeType) -> ValidationResult:
        """
        Validate CXO precedence rule enforcement.
        Ensures executive titles map to C_LEVEL/VP_LEVEL.
        """
        title_lower = title.lower()
        has_cxo_pattern = any((pattern.lower() in title_lower for pattern in self.CXO_TITLE_PATTERNS))
        if has_cxo_pattern:
            if archetype not in [ArchetypeType.C_LEVEL, ArchetypeType.VP_LEVEL]:
                return ValidationResult(gate_id='VG_CXO_PRECEDENCE', passed=False, severity='BLOCK', message=f"BLOCKED: CXO title '{title}' mapped to non-executive archetype {archetype.value}", details={'title': title, 'archetype': archetype.value})
        return ValidationResult(gate_id='VG_CXO_PRECEDENCE', passed=True, severity='INFO', message='CXO precedence rule satisfied', signature=f'CXO:OK:{archetype.value}')

def create_route_classifier(config: Optional[RouteClassifierConfig]=None) -> RouteClassifier:
    """Factory function to create RouteClassifier instance"""
    return RouteClassifier(config=config)

