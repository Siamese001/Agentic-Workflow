#!/usr/bin/env python3
"""
Outreach Engine Templates - Lift & Shift from LIC
CTA, greeting, signature, and system templates
"""

from typing import Dict, List, Optional, Any
import re
from datetime import datetime, timedelta

from .models import (
    Route, Archetype, CTATemplate, GreetingTemplate, 
    SignatureTemplate, ValidationResult, ValidationSeverity
)


class CTATemplates:
    """Call-to-action templates - Lift & Shift from LIC"""
    
    def __init__(self, cta_patterns: Dict[str, Any]):
        self.cta_patterns = cta_patterns.get("cta_patterns", {})
        self.archetype_ctas = self.cta_patterns.get("archetype_specific", {})
        self.date_engine = DateWindowEngine(self.cta_patterns.get("date_window_engine", {}))
    
    def get_cta_template(self, route: Route, archetype: Archetype, context: Dict[str, Any]) -> str:
        """Get appropriate CTA template for route and archetype"""
        # Route-specific templates take precedence
        route_templates = self.cta_patterns.get("cta_templates", {})
        if route.value in route_templates:
            template_config = route_templates[route.value]
            template = template_config.get("template", "")
            
            # Handle date window variables
            if "{date_window}" in template:
                date_window = self.date_engine.generate_date_window()
                template = template.replace("{date_window}", date_window)
            
            # Handle other variables
            if "{specific_topic}" in template and "specific_topic" in context:
                template = template.replace("{specific_topic}", context["specific_topic"])
            
            if "{topic}" in template and "topic" in context:
                template = template.replace("{topic}", context["topic"])
            
            return template
        
        # Fallback to archetype-specific templates
        if archetype.value in self.archetype_ctas:
            archetype_config = self.archetype_ctas[archetype.value]
            return archetype_config.get("example", "Would you be open to a brief chat?")
        
        # Default fallback
        return "Would you be open to a brief chat?"
    
    def validate_cta(self, cta: str, route: Route) -> List[ValidationResult]:
        """Validate CTA against route constraints"""
        validation_results = []
        
        # Check word count limits
        route_config = self.cta_patterns.get("cta_templates", {}).get(route.value, {})
        max_words = route_config.get("word_limit")
        
        if max_words:
            word_count = len(cta.split())
            if word_count > max_words:
                validation_results.append(ValidationResult(
                    rule_id="CTA_WORD_COUNT_EXCEEDED",
                    passed=False,
                    severity=ValidationSeverity.HIGH,
                    message=f"CTA word count {word_count} exceeds limit {max_words}",
                    details={"cta": cta, "word_count": word_count, "limit": max_words}
                ))
        
        return validation_results


class GreetingTemplates:
    """Greeting templates - Lift & Shift from LIC"""
    
    def __init__(self, message_templates: Dict[str, Any]):
        self.templates = message_templates.get("message_templates", {}).get("greeting_templates", {})
        self.validation_rules = self.templates.get("validation", {})
    
    def get_greeting(self, route: Route, recipient_name: str) -> str:
        """Get appropriate greeting for route"""
        template_config = self.templates.get(route.value, {})
        template = template_config.get("template", "Hi {first_name},")
        
        return template.replace("{first_name}", recipient_name.split()[0])
    
    def validate_greeting(self, greeting: str) -> List[ValidationResult]:
        """Validate greeting format"""
        validation_results = []
        
        # Check forbidden greetings
        forbidden = self.validation_rules.get("never_use", [])
        for forbidden_greeting in forbidden:
            if forbidden_greeting.lower() in greeting.lower():
                validation_results.append(ValidationResult(
                    rule_id="FORBIDDEN_GREETING",
                    passed=False,
                    severity=ValidationSeverity.HIGH,
                    message=f"Using forbidden greeting: {forbidden_greeting}",
                    details={"greeting": greeting, "forbidden": forbidden_greeting}
                ))
        
        # Check required elements
        required = self.validation_rules.get("always_include", [])
        if "Comma after name" in required and not greeting.strip().endswith(','):
            validation_results.append(ValidationResult(
                rule_id="MISSING_COMMA_GREETING",
                passed=False,
                severity=ValidationSeverity.MEDIUM,
                message="Greeting should end with comma",
                details={"greeting": greeting}
            ))
        
        return validation_results


class SignatureTemplates:
    """Signature templates - Lift & Shift from LIC"""
    
    def __init__(self, message_templates: Dict[str, Any]):
        self.templates = message_templates.get("message_templates", {}).get("signature_templates", {})
    
    def get_signature(self, route: Route, sender_profile: Dict[str, Any]) -> str:
        """Get appropriate signature for route and sender"""
        # Determine signature format from route constraints
        signature_format = "standard"  # This would come from routing constraints
        
        signature_config = self.templates.get(signature_format, {})
        template = signature_config.get("template", "Best regards,\n{name}")
        
        # Fill in sender information
        name = sender_profile.get("name", "")
        title = sender_profile.get("title", "")
        company = sender_profile.get("company", "")
        
        signature = template.replace("{name}", name)
        if title:
            signature = signature.replace("{title}", title)
        if company:
            signature = signature.replace("{company}", company)
        
        return signature
    
    def validate_signature(self, signature: str, sender_profile: Dict[str, Any]) -> List[ValidationResult]:
        """Validate signature content"""
        validation_results = []
        
        # Check if sender name is present
        sender_name = sender_profile.get("name", "")
        if sender_name and sender_name not in signature:
            validation_results.append(ValidationResult(
                rule_id="MISSING_SENDER_NAME",
                passed=False,
                severity=ValidationSeverity.MEDIUM,
                message="Signature should include sender name",
                details={"signature": signature, "sender_name": sender_name}
            ))
        
        return validation_results


class DateWindowEngine:
    """Date window engine for CTA scheduling - Enhanced from LIC"""
    
    def __init__(self, date_config: Dict[str, Any]):
        self.business_day_rules = date_config.get("business_day_rules", {})
        self.buffer_map = date_config.get("business_day_buffer_map", {})
        self.output_format = date_config.get("output_format", {})
    
    def generate_date_window(self, current_date: Optional[datetime] = None) -> str:
        """Generate a date window for CTA scheduling"""
        if current_date is None:
            current_date = datetime.now()
        
        # Get day of week
        day_name = current_date.strftime("%A")
        
        # Get buffer rules for this day
        buffer_rules = self.buffer_map.get(day_name, {"min_buffer_days": 2, "suggested_pattern": "Wed-Thu"})
        min_buffer = buffer_rules.get("min_buffer_days", 2)
        
        # Generate potential dates
        potential_dates = []
        for i in range(min_buffer, min_buffer + 3):
            candidate_date = current_date + timedelta(days=i)
            # Skip weekends
            if candidate_date.weekday() < 5:  # Monday-Friday
                potential_dates.append(candidate_date.strftime(self.output_format.get("date_format", "MM/DD")))
        
        # Format output
        if len(potential_dates) >= 3:
            return self.output_format.get("natural_language", "on {date1}, {date2}, or {date3}").format(
                date1=potential_dates[0], date2=potential_dates[1], date3=potential_dates[2]
            )
        elif len(potential_dates) == 2:
            return f"on {potential_dates[0]} or {potential_dates[1]}"
        elif len(potential_dates) == 1:
            return f"on {potential_dates[0]}"
        else:
            return "next week"


class SystemTemplates:
    """System prompt templates - Lift & Shift from LIC"""
    
    def __init__(self, message_templates: Dict[str, Any]):
        self.system_prompt = message_templates.get("message_templates", {}).get("generation_system_prompt", {})
    
    def get_system_prompt(self, archetype: Archetype, route: Route) -> str:
        """Get system prompt for message generation"""
        core_identity = self.system_prompt.get("core_identity", "")
        core_principles = self.system_prompt.get("core_principles", [])
        forbidden_patterns = self.system_prompt.get("forbidden_patterns", [])
        required_patterns = self.system_prompt.get("required_patterns", [])
        
        prompt_parts = [core_identity]
        
        if core_principles:
            prompt_parts.append("\nCore Principles:")
            prompt_parts.extend(f"- {principle}" for principle in core_principles)
        
        if forbidden_patterns:
            prompt_parts.append("\nForbidden Patterns:")
            prompt_parts.extend(f"- {pattern}" for pattern in forbidden_patterns)
        
        if required_patterns:
            prompt_parts.append("\nRequired Patterns:")
            prompt_parts.extend(f"- {pattern}" for pattern in required_patterns)
        
        # Add archetype-specific guidance
        archetype_guidance = self._get_archetype_guidance(archetype)
        if archetype_guidance:
            prompt_parts.append(f"\nArchetype Guidance ({archetype.value}):")
            prompt_parts.append(archetype_guidance)
        
        return "\n".join(prompt_parts)
    
    def _get_archetype_guidance(self, archetype: Archetype) -> str:
        """Get archetype-specific guidance"""
        guidance_map = {
            Archetype.C_LEVEL: "Focus on strategic impact and business outcomes. Be concise and outcome-oriented.",
            Archetype.EXECUTIVE: "Emphasize team objectives and operational value. Keep it high-level and professional.",
            Archetype.SENIOR_TA: "Use technical peer language but explain business impact. Focus on implementation challenges.",
            Archetype.RECRUITER: "Be warm and efficient. Focus on skill-to-role alignment with clear metrics."
        }
        return guidance_map.get(archetype, "")


class TemplateEngine:
    """Main template engine - Lift & Shift from LIC"""
    
    def __init__(self, lic_capabilities: Dict[str, Any]):
        message_templates = lic_capabilities.get("message_templates", {})
        cta_patterns = lic_capabilities.get("cta_patterns", {})
        
        self.cta_templates = CTATemplates(cta_patterns)
        self.greeting_templates = GreetingTemplates(message_templates)
        self.signature_templates = SignatureTemplates(message_templates)
        self.system_templates = SystemTemplates(message_templates)
    
    def assemble_template_components(
        self, 
        route: Route, 
        archetype: Archetype, 
        sender_profile: Dict[str, Any],
        recipient_profile: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, str]:
        """Assemble all template components for message generation"""
        recipient_name = recipient_profile.get("name", "Recipient")
        
        return {
            "greeting": self.greeting_templates.get_greeting(route, recipient_name),
            "cta": self.cta_templates.get_cta_template(route, archetype, context),
            "signature": self.signature_templates.get_signature(route, sender_profile),
            "system_prompt": self.system_templates.get_system_prompt(archetype, route)
        }
    
    def validate_template_components(self, components: Dict[str, str]) -> List[ValidationResult]:
        """Validate all template components"""
        validation_results = []
        
        # Validate greeting
        if "greeting" in components:
            validation_results.extend(self.greeting_templates.validate_greeting(components["greeting"]))
        
        # Validate CTA
        if "cta" in components and "route" in components:
            # Note: route would need to be passed separately
            pass
        
        # Validate signature
        if "signature" in components and "sender_profile" in components:
            # Note: sender_profile would need to be passed separately
            pass
        
        return validation_results
