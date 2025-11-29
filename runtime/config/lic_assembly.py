#!/usr/bin/env python3
"""
Outreach Engine K-Node Assembly - Lift & Shift + Enhanced from LIC
Message assembly engine for K1-K5 components
"""

from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

from ..models import (
    Route, Archetype, MessageAssembly, ValidationResult, ValidationSeverity
)


class MessageAssembler:
    """K-node message assembler - Lift & Shift from LIC"""
    
    def __init__(self, lic_capabilities: Dict[str, Any]):
        self.lic_capabilities = lic_capabilities
        self.templates = lic_capabilities.get("message_templates", {})
        self.routing_rules = lic_capabilities.get("routing_rules", {})
    
    def assemble_message(
        self,
        k1_greeting: str,
        k2_subject_line: Optional[str],
        k3_message_body: str,
        k4_cta: str,
        k5_signature: str,
        route: Route
    ) -> MessageAssembly:
        """Assemble K1-K5 components into complete message"""
        assembly = MessageAssembly(
            k1_greeting=k1_greeting,
            k2_subject_line=k2_subject_line,
            k3_message_body=k3_message_body,
            k4_cta=k4_cta,
            k5_signature=k5_signature
        )
        
        return assembly
    
    def validate_k_node_structure(self, assembly: MessageAssembly, route: Route) -> List[ValidationResult]:
        """Validate K-node structure against route requirements"""
        validation_results = []
        
        # Get route constraints
        route_config = self.routing_rules.get("routing_rules", {}).get(route.value, {})
        constraints = route_config.get("constraints", {})
        
        # Validate subject line requirement
        subject_required = constraints.get("subject_line_enabled", False)
        if subject_required and not assembly.k2_subject_line:
            validation_results.append(ValidationResult(
                rule_id="SUBJECT_LINE_REQUIRED",
                passed=False,
                severity=ValidationSeverity.CRITICAL,
                message=f"Route {route.value} requires subject line",
                details={"route": route.value}
            ))
        
        # Validate component completeness
        if not assembly.k1_greeting:
            validation_results.append(ValidationResult(
                rule_id="MISSING_GREETING",
                passed=False,
                severity=ValidationSeverity.HIGH,
                message="K1 greeting component is missing",
                details={}
            ))
        
        if not assembly.k3_message_body:
            validation_results.append(ValidationResult(
                rule_id="MISSING_MESSAGE_BODY",
                passed=False,
                severity=ValidationSeverity.CRITICAL,
                message="K3 message body component is missing",
                details={}
            ))
        
        if not assembly.k4_cta:
            validation_results.append(ValidationResult(
                rule_id="MISSING_CTA",
                passed=False,
                severity=ValidationSeverity.HIGH,
                message="K4 CTA component is missing",
                details={}
            ))
        
        if not assembly.k5_signature:
            validation_results.append(ValidationResult(
                rule_id="MISSING_SIGNATURE",
                passed=False,
                severity=ValidationSeverity.MEDIUM,
                message="K5 signature component is missing",
                details={}
            ))
        
        return validation_results
    
    def format_assembled_message(self, assembly: MessageAssembly, route: Route) -> str:
        """Format assembled message according to route requirements"""
        message_parts = []
        
        # K1: Greeting
        message_parts.append(assembly.k1_greeting)
        
        # K2: Subject line (if required)
        if assembly.k2_subject_line:
            message_parts.append(f"Subject: {assembly.k2_subject_line}")
        
        # Add spacing between header and body
        if assembly.k2_subject_line:
            message_parts.append("")
        
        # K3: Message body
        message_parts.append(assembly.k3_message_body)
        
        # K4: CTA
        message_parts.append("")
        message_parts.append(assembly.k4_cta)
        
        # K5: Signature
        message_parts.append("")
        message_parts.append(assembly.k5_signature)
        
        return "\n".join(message_parts)
    
    def validate_message_format(self, formatted_message: str, route: Route) -> List[ValidationResult]:
        """Validate formatted message against route constraints"""
        validation_results = []
        
        # Check overall structure
        lines = formatted_message.split("\n")
        
        # Validate greeting is first
        if lines and not self._is_greeting(lines[0]):
            validation_results.append(ValidationResult(
                rule_id="INVALID_GREETING_POSITION",
                passed=False,
                severity=ValidationSeverity.MEDIUM,
                message="Message should start with greeting",
                details={"first_line": lines[0]}
            ))
        
        # Validate subject line format
        subject_line = self._find_subject_line(formatted_message)
        if subject_line and not subject_line.startswith("Subject: "):
            validation_results.append(ValidationResult(
                rule_id="INVALID_SUBJECT_FORMAT",
                passed=False,
                severity=ValidationSeverity.MEDIUM,
                message="Subject line should start with 'Subject: '",
                details={"subject_line": subject_line}
            ))
        
        # Validate CTA presence
        if not self._has_cta(formatted_message):
            validation_results.append(ValidationResult(
                rule_id="MISSING_CTA_IN_FORMATTED",
                passed=False,
                severity=ValidationSeverity.HIGH,
                message="Formatted message should contain CTA",
                details={}
            ))
        
        return validation_results
    
    def _is_greeting(self, line: str) -> bool:
        """Check if line is a greeting"""
        line = line.strip()
        greeting_patterns = ["Hi", "Hello", "Dear", "Good morning", "Good afternoon"]
        return any(line.startswith(pattern) for pattern in greeting_patterns)
    
    def _find_subject_line(self, message: str) -> Optional[str]:
        """Find subject line in message"""
        for line in message.split("\n"):
            if "subject:" in line.lower():
                return line.strip()
        return None
    
    def _has_cta(self, message: str) -> bool:
        """Check if message contains CTA"""
        cta_indicators = ["?", "call", "chat", "discuss", "connect", "available", "interested"]
        message_lower = message.lower()
        return any(indicator in message_lower for indicator in cta_indicators)


class KNodeAssemblyEngine:
    """Main K-node assembly engine - Lift & Shift + Enhanced from LIC"""
    
    def __init__(self, lic_capabilities: Dict[str, Any]):
        self.lic_capabilities = lic_capabilities
        self.message_assembler = MessageAssembler(lic_capabilities)
        self.routing_rules = lic_capabilities.get("routing_rules", {})
    
    def execute_k_node_assembly(
        self,
        route: Route,
        archetype: Archetype,
        components: Dict[str, str],
        sender_profile: Dict[str, Any],
        recipient_profile: Dict[str, Any]
    ) -> Tuple[MessageAssembly, List[ValidationResult]]:
        """Execute complete K-node assembly process"""
        validation_results = []
        
        # Extract components
        k1_greeting = components.get("greeting", "")
        k2_subject_line = components.get("subject_line")
        k3_message_body = components.get("message_body", "")
        k4_cta = components.get("cta", "")
        k5_signature = components.get("signature", "")
        
        # Validate component inputs
        component_validations = self._validate_component_inputs(
            k1_greeting, k2_subject_line, k3_message_body, k4_cta, k5_signature
        )
        validation_results.extend(component_validations)
        
        # Assemble message
        assembly = self.message_assembler.assemble_message(
            k1_greeting, k2_subject_line, k3_message_body, k4_cta, k5_signature, route
        )
        
        # Validate K-node structure
        structure_validations = self.message_assembler.validate_k_node_structure(assembly, route)
        validation_results.extend(structure_validations)
        
        # Apply final formatting and validation
        formatted_message = self.message_assembler.format_assembled_message(assembly, route)
        format_validations = self.message_assembler.validate_message_format(formatted_message, route)
        validation_results.extend(format_validations)
        
        return assembly, validation_results
    
    def _validate_component_inputs(
        self,
        greeting: str,
        subject_line: Optional[str],
        message_body: str,
        cta: str,
        signature: str
    ) -> List[ValidationResult]:
        """Validate individual component inputs"""
        validation_results = []
        
        # Validate greeting
        if not greeting.strip():
            validation_results.append(ValidationResult(
                rule_id="EMPTY_GREETING",
                passed=False,
                severity=ValidationSeverity.HIGH,
                message="Greeting component cannot be empty",
                details={}
            ))
        elif len(greeting.strip()) < 3:
            validation_results.append(ValidationResult(
                rule_id="GREETING_TOO_SHORT",
                passed=False,
                severity=ValidationSeverity.MEDIUM,
                message="Greeting appears too short",
                details={"greeting": greeting}
            ))
        
        # Validate message body
        if not message_body.strip():
            validation_results.append(ValidationResult(
                rule_id="EMPTY_MESSAGE_BODY",
                passed=False,
                severity=ValidationSeverity.CRITICAL,
                message="Message body cannot be empty",
                details={}
            ))
        elif len(message_body.strip()) < 20:
            validation_results.append(ValidationResult(
                rule_id="MESSAGE_BODY_TOO_SHORT",
                passed=False,
                severity=ValidationSeverity.HIGH,
                message="Message body appears too short",
                details={"body_length": len(message_body)}
            ))
        
        # Validate CTA
        if not cta.strip():
            validation_results.append(ValidationResult(
                rule_id="EMPTY_CTA",
                passed=False,
                severity=ValidationSeverity.HIGH,
                message="CTA component cannot be empty",
                details={}
            ))
        
        # Validate signature
        if not signature.strip():
            validation_results.append(ValidationResult(
                rule_id="EMPTY_SIGNATURE",
                passed=False,
                severity=ValidationSeverity.MEDIUM,
                message="Signature component cannot be empty",
                details={}
            ))
        
        return validation_results
    
    def get_assembly_guidance(self, route: Route, archetype: Archetype) -> Dict[str, Any]:
        """Get guidance for K-node assembly"""
        route_config = self.routing_rules.get("routing_rules", {}).get(route.value, {})
        constraints = route_config.get("constraints", {})
        
        return {
            "route": route.value,
            "archetype": archetype.value,
            "k_sequence": [
                "K1: Greeting",
                "K2: Subject Line (if required)",
                "K3: Message Body",
                "K4: Call-to-Action",
                "K5: Signature"
            ],
            "subject_line_required": constraints.get("subject_line_enabled", False),
            "attachment_enabled": constraints.get("attachments_enabled", False),
            "signature_format": constraints.get("signature_format", "standard"),
            "cta_format": constraints.get("cta_format", "standard"),
            "word_constraints": constraints.get("word_range"),
            "char_limit": constraints.get("char_limit")
        }
    
    def preview_assembly(
        self,
        components: Dict[str, str],
        route: Route
    ) -> Dict[str, Any]:
        """Preview assembly without full validation"""
        k1_greeting = components.get("greeting", "")
        k2_subject_line = components.get("subject_line")
        k3_message_body = components.get("message_body", "")
        k4_cta = components.get("cta", "")
        k5_signature = components.get("signature", "")
        
        # Create temporary assembly
        temp_assembly = MessageAssembly(
            k1_greeting=k1_greeting,
            k2_subject_line=k2_subject_line,
            k3_message_body=k3_message_body,
            k4_cta=k4_cta,
            k5_signature=k5_signature
        )
        
        # Format for preview
        formatted_preview = self.message_assembler.format_assembled_message(temp_assembly, route)
        
        # Calculate metrics
        word_count = len(formatted_preview.split())
        char_count = len(formatted_preview)
        
        return {
            "formatted_message": formatted_preview,
            "word_count": word_count,
            "char_count": char_count,
            "has_subject_line": k2_subject_line is not None,
            "component_count": sum(1 for comp in [k1_greeting, k2_subject_line, k3_message_body, k4_cta, k5_signature] if comp)
        }





