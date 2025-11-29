#!/usr/bin/env python3
"""
Outreach Engine CTA - Lift & Shift + Enhanced from LIC
Call-to-action engine and date window processing
"""

from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import re

from ..models import (
    Route, Archetype, CTATemplate, ValidationResult, ValidationSeverity
)


class DateWindowEngine:
    """Date window engine for CTA scheduling - Enhanced from LIC"""
    
    def __init__(self, cta_patterns: Dict[str, Any]):
        self.date_config = cta_patterns.get("date_window_engine", {})
        self.business_day_rules = self.date_config.get("business_day_rules", {})
        self.buffer_map = self.date_config.get("business_day_buffer_map", {})
        self.output_format = self.date_config.get("output_format", {})
    
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
            # Skip weekends and holidays
            if self._is_business_day(candidate_date):
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
    
    def _is_business_day(self, date: datetime) -> bool:
        """Check if date is a business day (not weekend or holiday)"""
        # Skip weekends
        if date.weekday() >= 5:  # Saturday, Sunday
            return False
        
        # Skip US federal holidays (simplified list)
        holidays = [
            (1, 1),   # New Year's Day
            (7, 4),   # Independence Day
            (12, 25), # Christmas
            # Add more holidays as needed
        ]
        
        for month, day in holidays:
            if date.month == month and date.day == day:
                return False
        
        return True
    
    def validate_date_window(self, date_window: str) -> List[ValidationResult]:
        """Validate generated date window"""
        validation_results = []
        
        # Check if date window contains actual dates
        date_pattern = r'\d{1,2}\/\d{1,2}'
        dates_found = re.findall(date_pattern, date_window)
        
        if not dates_found:
            validation_results.append(ValidationResult(
                rule_id="NO_DATES_IN_WINDOW",
                passed=False,
                severity=ValidationSeverity.MEDIUM,
                message="Date window should contain specific dates",
                details={"date_window": date_window}
            ))
        
        # Check format compliance
        expected_format = self.output_format.get("natural_language", "")
        if expected_format and "on" not in date_window.lower():
            validation_results.append(ValidationResult(
                rule_id="DATE_WINDOW_FORMAT",
                passed=False,
                severity=ValidationSeverity.LOW,
                message="Date window should follow expected format",
                details={"date_window": date_window, "expected_format": expected_format}
            ))
        
        return validation_results


class ArchetypeCTA:
    """Archetype-specific CTA generation - Lift & Shift from LIC"""
    
    def __init__(self, cta_patterns: Dict[str, Any]):
        self.archetype_config = cta_patterns.get("archetype_specific", {})
        self.date_engine = DateWindowEngine(cta_patterns)
    
    def get_archetype_cta_template(self, archetype: Archetype, context: Dict[str, Any]) -> str:
        """Get CTA template specific to archetype"""
        archetype_key = archetype.value
        if archetype_key not in self.archetype_config:
            return "Would you be open to a brief chat?"
        
        config = self.archetype_config[archetype_key]
        base_template = config.get("example", "")
        
        # Customize based on context
        if "{business_impact}" in base_template and "business_impact" in context:
            base_template = base_template.replace("{business_impact}", context["business_impact"])
        
        if "{strategic_topic}" in base_template and "strategic_topic" in context:
            base_template = base_template.replace("{strategic_topic}", context["strategic_topic"])
        
        if "{topic}" in base_template and "topic" in context:
            base_template = base_template.replace("{topic}", context["topic"])
        
        if "{company}" in base_template and "company" in context:
            base_template = base_template.replace("{company}", context["company"])
        
        return base_template
    
    def get_cta_variables(self, archetype: Archetype, route: Route, context: Dict[str, Any]) -> Dict[str, str]:
        """Get variables needed for CTA template"""
        variables = {}
        
        # Date window for routes that need it
        if route in [Route.INMAIL, Route.SHORT_NEW, Route.LONG_NEW]:
            variables["date_window"] = self.date_engine.generate_date_window()
        
        # Duration options
        if "{duration}" in str(context):
            variables["duration"] = "15-minute, 20-minute, or 30-minute"
        
        # Topic extraction
        if "job_description" in context:
            jd = context["job_description"]
            variables["specific_topic"] = self._extract_topic_from_jd(jd)
        
        return variables
    
    def _extract_topic_from_jd(self, job_description: Dict[str, Any]) -> str:
        """Extract specific topic from job description"""
        # Simple topic extraction - in practice would be more sophisticated
        title = job_description.get("title", "").lower()
        
        if "engineer" in title:
            return "engineering challenges and opportunities"
        elif "manager" in title:
            return "team leadership and operational excellence"
        elif "director" in title:
            return "strategic initiatives and department goals"
        elif "analyst" in title:
            return "data-driven insights and analytics"
        else:
            return "the role and team objectives"
    
    def validate_archetype_cta(self, cta: str, archetype: Archetype) -> List[ValidationResult]:
        """Validate CTA against archetype requirements"""
        validation_results = []
        
        archetype_key = archetype.value
        if archetype_key not in self.archetype_config:
            return validation_results
        
        config = self.archetype_config[archetype_key]
        expected_style = config.get("style", "")
        expected_verbs = config.get("verbs", [])
        expected_focus = config.get("focus", "")
        
        # Check for expected verbs
        cta_lower = cta.lower()
        found_verbs = [verb for verb in expected_verbs if verb in cta_lower]
        
        if expected_verbs and not found_verbs:
            validation_results.append(ValidationResult(
                rule_id="EXPECTED_VERB_MISSING",
                passed=False,
                severity=ValidationSeverity.MEDIUM,
                message=f"CTA should include verbs like: {', '.join(expected_verbs)}",
                details={"expected_verbs": expected_verbs, "cta": cta}
            ))
        
        # Check word count limits
        word_count = len(cta.split())
        if word_count > 20:  # Reasonable upper limit for CTAs
            validation_results.append(ValidationResult(
                rule_id="CTA_TOO_LONG",
                passed=False,
                severity=ValidationSeverity.MEDIUM,
                message=f"CTA word count {word_count} exceeds reasonable limit",
                details={"word_count": word_count, "cta": cta}
            ))
        
        return validation_results


class CTAEngine:
    """Main CTA engine - Lift & Shift + Enhanced from LIC"""
    
    def __init__(self, lic_capabilities: Dict[str, Any]):
        self.cta_patterns = lic_capabilities.get("cta_patterns", {})
        self.message_templates = lic_capabilities.get("message_templates", {})
        self.archetype_cta = ArchetypeCTA(self.cta_patterns)
        self.date_engine = DateWindowEngine(self.cta_patterns)
    
    def generate_cta(
        self,
        route: Route,
        archetype: Archetype,
        context: Dict[str, Any]
    ) -> Tuple[str, List[ValidationResult]]:
        """Generate appropriate CTA for route and archetype"""
        validation_results = []
        
        # Try route-specific templates first
        route_templates = self.message_templates.get("cta_templates", {})
        
        if route.value in route_templates:
            template_config = route_templates[route.value]
            template = template_config.get("template", "")
            
            # Handle template variables
            variables = self.archetype_cta.get_cta_variables(archetype, route, context)
            
            for var_name, var_value in variables.items():
                template = template.replace(f"{{{var_name}}}", var_value)
            
            # Validate route-specific constraints
            max_words = template_config.get("word_limit")
            if max_words:
                word_count = len(template.split())
                if word_count > max_words:
                    validation_results.append(ValidationResult(
                        rule_id="CTA_WORD_COUNT_EXCEEDED",
                        passed=False,
                        severity=ValidationSeverity.HIGH,
                        message=f"CTA word count {word_count} exceeds limit {max_words}",
                        details={"word_count": word_count, "limit": max_words, "cta": template}
                    ))
        else:
            # Fallback to archetype-specific template
            template = self.archetype_cta.get_archetype_cta_template(archetype, context)
        
        # Validate against archetype requirements
        archetype_validations = self.archetype_cta.validate_archetype_cta(template, archetype)
        validation_results.extend(archetype_validations)
        
        # Validate date window if present
        if "{date_window}" in template or "on" in template.lower():
            date_validations = self.date_engine.validate_date_window(template)
            validation_results.extend(date_validations)
        
        return template, validation_results
    
    def get_cta_examples(self, route: Route, archetype: Archetype) -> List[str]:
        """Get example CTAs for route and archetype"""
        examples = []
        
        # Route-specific examples
        route_templates = self.message_templates.get("cta_templates", {})
        if route.value in route_templates:
            template_config = route_templates[route.value]
            examples.extend(template_config.get("examples", []))
        
        # Archetype-specific examples
        archetype_config = self.cta_patterns.get("archetype_specific", {}).get(archetype.value, {})
        if "example" in archetype_config:
            examples.append(archetype_config["example"])
        
        return examples
    
    def validate_cta_compliance(self, cta: str, route: Route, archetype: Archetype) -> List[ValidationResult]:
        """Comprehensive CTA validation"""
        all_validations = []
        
        # Route-specific validation
        route_templates = self.message_templates.get("cta_templates", {})
        if route.value in route_templates:
            template_config = route_templates[route.value]
            max_words = template_config.get("word_limit")
            
            if max_words:
                word_count = len(cta.split())
                if word_count > max_words:
                    all_validations.append(ValidationResult(
                        rule_id="CTA_WORD_COUNT_EXCEEDED",
                        passed=False,
                        severity=ValidationSeverity.HIGH,
                        message=f"CTA word count {word_count} exceeds limit {max_words}",
                        details={"word_count": word_count, "limit": max_words}
                    ))
        
        # Archetype-specific validation
        archetype_validations = self.archetype_cta.validate_archetype_cta(cta, archetype)
        all_validations.extend(archetype_validations)
        
        # General CTA validation
        if not cta.strip().endswith('?'):
            all_validations.append(ValidationResult(
                rule_id="CTA_NOT_QUESTION",
                passed=False,
                severity=ValidationSeverity.LOW,
                message="CTA should typically be phrased as a question",
                details={"cta": cta}
            ))
        
        return all_validations
    
    def get_cta_guidance(self, route: Route, archetype: Archetype) -> Dict[str, Any]:
        """Get guidance for CTA generation"""
        archetype_config = self.cta_patterns.get("archetype_specific", {}).get(archetype.value, {})
        
        return {
            "route": route.value,
            "archetype": archetype.value,
            "style": archetype_config.get("style", "professional"),
            "focus": archetype_config.get("focus", "value"),
            "formality": archetype_config.get("formality", "medium"),
            "preferred_verbs": archetype_config.get("verbs", []),
            "examples": self.get_cta_examples(route, archetype),
            "date_window_required": route in [Route.INMAIL, Route.SHORT_NEW, Route.LONG_NEW]
        }





