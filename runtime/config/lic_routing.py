#!/usr/bin/env python3
"""
Outreach Engine Routing - Lift & Shift from LIC
Route determination and constraint application
"""

from typing import Dict, List, Optional, Tuple, Any
import re

from ..models import (
    Route, Archetype, RouteConstraints, MessageContext,
    RoutingError, ValidationResult, ValidationSeverity
)


class RouteClassifier:
    """Route classifier based on connection status and message history - Lift & Shift"""
    
    def __init__(self, routing_rules: Dict[str, Any]):
        self.routing_rules = routing_rules.get("routing_rules", {})
    
    def classify_route(self, recipient_profile: Dict, prior_messages: List[Dict]) -> Route:
        """Determine the appropriate route based on recipient context"""
        connection_status = recipient_profile.get("connection_status", "not_connected")
        prior_message_count = len(prior_messages)
        
        # Check route conditions from LIC specifications
        for route_name, route_config in self.routing_rules.items():
            conditions = route_config.get("conditions", {})
            
            # Evaluate connection status condition
            if "connection_status" in conditions:
                if connection_status != conditions["connection_status"]:
                    continue
            
            # Evaluate prior message count conditions
            if "prior_message_count" in conditions:
                if prior_message_count != conditions["prior_message_count"]:
                    continue
            
            if "prior_message_count_gt" in conditions:
                if prior_message_count <= conditions["prior_message_count_gt"]:
                    continue
                    
            if "prior_message_count_gte" in conditions:
                if prior_message_count < conditions["prior_message_count_gte"]:
                    continue
            
            # Route matches conditions
            return Route(route_name)
        
        # Default fallback
        return Route.SHORT_NEW
    
    def get_route_constraints(self, route: Route) -> RouteConstraints:
        """Get constraints for a specific route"""
        route_name = route.value
        route_config = self.routing_rules.get(route_name, {})
        constraints = route_config.get("constraints", {})
        
        return RouteConstraints(
            char_limit=constraints.get("char_limit"),
            word_range=constraints.get("word_range"),
            signature_format=constraints.get("signature_format", "standard"),
            subject_line_enabled=constraints.get("subject_line_enabled", False),
            attachments_enabled=constraints.get("attachments_enabled", False),
            cta_format=constraints.get("cta_format", "standard"),
            cta_max_words=constraints.get("cta_max_words"),
            greeting_format=constraints.get("greeting_format", "Hi {first_name},")
        )


class RoutingEngine:
    """Main routing engine - Lift & Shift from LIC"""
    
    def __init__(self, routing_rules: Dict[str, Any]):
        self.routing_rules = routing_rules
        self.classifier = RouteClassifier(routing_rules)
    
    def determine_route(self, recipient_profile: Dict, prior_messages: List[Dict]) -> Route:
        """Determine the optimal route for message delivery"""
        try:
            return self.classifier.classify_route(recipient_profile, prior_messages)
        except Exception as e:
            raise RoutingError(f"Failed to determine route: {str(e)}")
    
    def apply_route_constraints(self, route: Route, message_content: str) -> List[ValidationResult]:
        """Apply route-specific constraints to message content"""
        constraints = self.classifier.get_route_constraints(route)
        validation_results = []
        
        # Validate word count
        word_count = len(message_content.split())
        if not constraints.validate_word_count(word_count):
            validation_results.append(ValidationResult(
                rule_id="WORD_COUNT_VIOLATION",
                passed=False,
                severity=ValidationSeverity.HIGH,
                message=f"Word count {word_count} violates route constraints {constraints.word_range}",
                details={"word_count": word_count, "expected_range": constraints.word_range}
            ))
        
        # Validate character limit
        char_count = len(message_content)
        if not constraints.validate_char_limit(char_count):
            validation_results.append(ValidationResult(
                rule_id="CHAR_LIMIT_VIOLATION",
                passed=False,
                severity=ValidationSeverity.HIGH,
                message=f"Character count {char_count} exceeds limit {constraints.char_limit}",
                details={"char_count": char_count, "limit": constraints.char_limit}
            ))
        
        # Validate subject line requirement
        if constraints.subject_line_enabled:
            subject_match = re.search(r'Subject:\s*(.+)', message_content, re.IGNORECASE)
            if not subject_match:
                validation_results.append(ValidationResult(
                    rule_id="SUBJECT_LINE_MISSING",
                    passed=False,
                    severity=ValidationSeverity.CRITICAL,
                    message="Subject line required but not found",
                    details={"route": route.value}
                ))
            else:
                subject = subject_match.group(1).strip()
                subject_words = len(subject.split())
                if subject_words < 4 or subject_words > 10:
                    validation_results.append(ValidationResult(
                        rule_id="SUBJECT_LINE_LENGTH",
                        passed=False,
                        severity=ValidationSeverity.MEDIUM,
                        message=f"Subject line word count {subject_words} outside range 4-10",
                        details={"subject_words": subject_words, "subject": subject}
                    ))
        
        return validation_results
    
    def create_message_context(
        self, 
        sender_profile: Dict, 
        recipient_profile: Dict, 
        job_description: Optional[Dict] = None,
        prior_messages: Optional[List[Dict]] = None
    ) -> MessageContext:
        """Create complete message context with routing information"""
        if prior_messages is None:
            prior_messages = []
        
        # Determine route
        route = self.determine_route(recipient_profile, prior_messages)
        
        # Get route constraints
        constraints = self.classifier.get_route_constraints(route)
        
        # Determine archetype (will be enhanced by seniority engine)
        archetype = self._determine_archetype(recipient_profile)
        
        return MessageContext(
            route=route,
            archetype=archetype,
            sender_profile=sender_profile,
            recipient_profile=recipient_profile,
            job_description=job_description,
            prior_messages=prior_messages,
            constraints=constraints
        )
    
    def _determine_archetype(self, recipient_profile: Dict) -> Archetype:
        """Determine recipient archetype - basic implementation"""
        title = recipient_profile.get("title", "").lower()
        
        # Basic title-based classification
        if any(keyword in title for keyword in ["ceo", "cto", "cfo", "chief", "president"]):
            return Archetype.C_LEVEL
        elif any(keyword in title for keyword in ["vp", "vice president", "director", "head"]):
            return Archetype.EXECUTIVE
        elif any(keyword in title for keyword in ["recruiter", "talent", "sourcer", "hr"]):
            return Archetype.RECRUITER
        elif any(keyword in title for keyword in ["engineer", "developer", "architect", "technical"]):
            return Archetype.SENIOR_TA
        else:
            return Archetype.EXECUTIVE  # Default fallback
    
    def validate_route_compatibility(self, route: Route, archetype: Archetype) -> List[ValidationResult]:
        """Validate that route and archetype are compatible"""
        validation_results = []
        
        # Basic compatibility checks
        if route == Route.CONNECTION_REQ and archetype == Archetype.C_LEVEL:
            validation_results.append(ValidationResult(
                rule_id="ROUTE_ARCHETYPE_MISMATCH",
                passed=False,
                severity=ValidationSeverity.MEDIUM,
                message="Connection request to C-level may have low success rate",
                details={"route": route.value, "archetype": archetype.value}
            ))
        
        return validation_results
