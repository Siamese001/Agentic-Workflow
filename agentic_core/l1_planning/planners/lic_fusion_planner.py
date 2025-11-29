"""LIC Fusion Planner - L1 pure planning for resume→message fusion.

Implements nuclear prompt requirements for deterministic fusion planning:
- Fuses resume achievements + LIC research signals into value propositions
- Creates structured message section plans (opening, body, CTA)
- Determines archetype-specific CTA styles and tone guidance
- Pure L1 planning with no external calls or execution
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


@dataclass
class LICValueProposition:
    """A single value proposition combining resume achievement + research signal."""
    id: str                              # stable identifier (e.g. "vp_1")
    achievement_snippet: str             # concise resume-derived snippet
    signal_snippet: str                  # concise research signal snippet
    archetype_target: str                # e.g. "EXECUTIVE" | "SENIOR_TA" | "RECRUITER"
    priority: int                        # 1 = highest priority
    angle: str                           # e.g. "strategic", "operational", "technical"
    expected_impact: str                 # short description of why this matters
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LICMessageSectionPlan:
    """Structured plan for one section of an outreach message."""
    section_type: str                    # "opening" | "body" | "cta"
    archetype_target: str
    value_proposition_ids: List[str]     # which LICValueProposition IDs to use
    tone_guidance: str                   # e.g. "concise and executive", "signal-aware", etc.
    cta_guidance: Optional[str]          # for "cta" sections, explicit CTA guidance
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LICFusionPlan:
    """Full LIC fusion blueprint from resume + signals → message."""
    role_title: str
    company_name: str
    archetype: str                       # primary archetype for this contact
    value_propositions: List[LICValueProposition]
    sections: List[LICMessageSectionPlan]
    primary_cta_style: str               # e.g. "light_touch", "exploratory_call", "direct"
    fallback_cta_style: str              # used by L3 meta-loop if CTA deemed too strong
    metadata: Dict[str, Any] = field(default_factory=dict)


class LICFusionPlanner:
    """L1 pure planner for resume→message fusion.
    
    Generates deterministic fusion plans that combine resume achievements
    with research signals into structured message blueprints.
    """
    
    def __init__(
        self,
        *,
        max_value_props: int = 5,
        max_body_sections: int = 2,
        enable_exec_strict_cta: bool = True,
        telemetry_bus: Optional[Any] = None,
    ) -> None:
        """Initialize LIC fusion planner with configuration."""
        self.max_value_props = max_value_props
        self.max_body_sections = max_body_sections
        self.enable_exec_strict_cta = enable_exec_strict_cta
        self.telemetry_bus = telemetry_bus
        
        logger.debug(f"LIC Fusion Planner initialized: max_value_props={max_value_props}")
    
    def plan(
        self,
        *,
        role_title: str,
        company_name: str,
        archetype: str,
        resume_features: Dict[str, Any],
        research_signals: Dict[str, Any],
        outreach_context: Dict[str, Any],
    ) -> LICFusionPlan:
        """Generate a deterministic fusion plan from resume + signals.
        
        Args:
            role_title: Target role title
            company_name: Target company name
            archetype: Primary archetype for this contact
            resume_features: Pre-computed resume signals (achievements, metrics, themes)
            research_signals: LIC research outputs (company, market, product, funding)
            outreach_context: Context data for planning (treated as opaque)
            
        Returns:
            Complete LIC fusion plan with value propositions and message sections
        """
        # 1. Extract and normalize achievements + signals
        achievements = self._extract_achievements(resume_features)
        signals = self._extract_signals(research_signals)
        
        # 2. Generate candidate value propositions
        value_props = self._pair_achievements_and_signals(
            achievements, signals, archetype
        )
        
        # 3. Rank and trim to max_value_props
        value_props = self._rank_and_trim_value_props(value_props)
        
        # 4. Build opening/body/cta section plans
        sections = self._build_sections(value_props, archetype)
        
        # 5. Determine CTA styles
        primary_cta_style, fallback_cta_style = self._determine_cta_styles(
            archetype, self.enable_exec_strict_cta
        )
        
        # 6. Build metadata
        metadata = {
            "archetype": archetype,
            "role_title": role_title,
            "company_name": company_name,
            "value_prop_count": len(value_props),
            "primary_cta_style": primary_cta_style,
            "fallback_cta_style": fallback_cta_style,
        }
        
        # 7. Create fusion plan
        plan = LICFusionPlan(
            role_title=role_title,
            company_name=company_name,
            archetype=archetype,
            value_propositions=value_props,
            sections=sections,
            primary_cta_style=primary_cta_style,
            fallback_cta_style=fallback_cta_style,
            metadata=metadata,
        )
        
        # 8. Record telemetry (best-effort)
        self._safe_record_telemetry(plan)
        
        return plan
    
    def _extract_achievements(self, resume_features: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract achievements from resume features."""
        achievements = resume_features.get("achievements", [])
        
        # Normalize and validate achievement structure
        normalized = []
        for i, achievement in enumerate(achievements):
            if isinstance(achievement, dict):
                normalized.append({
                    "id": achievement.get("id", f"achievement_{i}"),
                    "text": achievement.get("text", ""),
                    "impact_type": achievement.get("impact_type", "general"),
                    "seniority_signal": achievement.get("seniority_signal", "ic"),
                })
        
        return normalized
    
    def _extract_signals(self, research_signals: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
        """Extract signals from research data."""
        return {
            "company_signals": research_signals.get("company_signals", []),
            "role_signals": research_signals.get("role_signals", []),
            "strategic_themes": research_signals.get("strategic_themes", []),
        }
    
    def _pair_achievements_and_signals(
        self,
        achievements: List[Dict[str, Any]],
        signals: Dict[str, List[Dict[str, Any]]],
        archetype: str,
    ) -> List[LICValueProposition]:
        """Generate value propositions by pairing achievements with signals."""
        value_props = []
        strategic_themes = signals.get("strategic_themes", [])
        
        for i, achievement in enumerate(achievements):
            # Create value props for each relevant signal
            for signal_type, signal_list in signals.items():
                if signal_type == "strategic_themes":
                    continue  # Handle themes separately
                
                for j, signal in enumerate(signal_list[:3]):  # Limit signal pairings
                    vp_id = f"vp_{len(value_props) + 1}"
                    
                    # Determine archetype target
                    archetype_target = self._determine_archetype_target(
                        achievement, signal, archetype
                    )
                    
                    # Determine angle based on content
                    angle = self._determine_angle(achievement, signal, strategic_themes)
                    
                    # Create snippets
                    achievement_snippet = self._truncate_text(achievement.get("text", ""), 100)
                    signal_snippet = self._truncate_text(
                        signal.get("text", signal.get("description", "")), 80
                    )
                    
                    # Determine expected impact
                    expected_impact = self._determine_expected_impact(
                        achievement.get("impact_type", ""), signal_type
                    )
                    
                    # Create metadata
                    metadata = {
                        "impact_type": achievement.get("impact_type"),
                        "source_achievement_id": achievement.get("id"),
                        "source_signal_id": signal.get("id"),
                    }
                    
                    value_prop = LICValueProposition(
                        id=vp_id,
                        achievement_snippet=achievement_snippet,
                        signal_snippet=signal_snippet,
                        archetype_target=archetype_target,
                        priority=999,  # Will be assigned during ranking
                        angle=angle,
                        expected_impact=expected_impact,
                        metadata=metadata,
                    )
                    
                    value_props.append(value_prop)
        
        return value_props
    
    def _determine_archetype_target(
        self,
        achievement: Dict[str, Any],
        signal: Dict[str, Any],
        default_archetype: str,
    ) -> str:
        """Determine the best archetype target for a value proposition."""
        seniority = achievement.get("seniority_signal", "ic")
        
        # Executive seniority targets EXECUTIVE
        if seniority == "executive":
            return "EXECUTIVE"
        
        # Technical themes target SENIOR_TA
        signal_text = signal.get("text", signal.get("description", "")).lower()
        achievement_text = achievement.get("text", "").lower()
        
        technical_keywords = ["technical", "architecture", "engineering", "stack", "code"]
        if any(keyword in signal_text or keyword in achievement_text for keyword in technical_keywords):
            return "SENIOR_TA"
        
        # Process/throughput themes target RECRUITER or SENIOR_TA
        process_keywords = ["process", "pipeline", "throughput", "hiring", "recruitment"]
        if any(keyword in signal_text or keyword in achievement_text for keyword in process_keywords):
            return "RECRUITER" if default_archetype == "RECRUITER" else "SENIOR_TA"
        
        return default_archetype.upper()
    
    def _determine_angle(
        self,
        achievement: Dict[str, Any],
        signal: Dict[str, Any],
        strategic_themes: List[str],
    ) -> str:
        """Determine the angle of a value proposition."""
        signal_text = signal.get("text", signal.get("description", "")).lower()
        achievement_text = achievement.get("text", "").lower()
        combined_text = f"{signal_text} {achievement_text}"
        
        # Strategic angle for strategy/funding/market/product themes
        strategic_keywords = [
            "strategy", "funding", "market", "product", "roadmap", "growth",
            "revenue", "business", "competitive"
        ]
        if any(keyword in combined_text for keyword in strategic_keywords):
            return "strategic"
        
        # Operational angle for process/throughput improvements
        operational_keywords = [
            "process", "throughput", "pipeline", "efficiency", "workflow",
            "hiring", "recruitment", "team", "operations"
        ]
        if any(keyword in combined_text for keyword in operational_keywords):
            return "operational"
        
        # Technical angle for stack/architecture/IC contributions
        technical_keywords = [
            "technical", "architecture", "engineering", "stack", "code",
            "development", "software", "system", "infrastructure"
        ]
        if any(keyword in combined_text for keyword in technical_keywords):
            return "technical"
        
        # Default to strategic if no clear match
        return "strategic"
    
    def _determine_expected_impact(self, impact_type: str, signal_type: str) -> str:
        """Generate expected impact description."""
        impact_map = {
            "revenue": "Revenue growth impact",
            "cost": "Cost optimization impact", 
            "team": "Team scaling impact",
            "product": "Product innovation impact",
            "general": "Business value impact",
        }
        
        base_impact = impact_map.get(impact_type, "Business value impact")
        
        if signal_type == "company_signals":
            return f"{base_impact} aligned with company strategy"
        elif signal_type == "role_signals":
            return f"{base_impact} aligned with role requirements"
        else:
            return base_impact
    
    def _rank_and_trim_value_props(self, value_props: List[LICValueProposition]) -> List[LICValueProposition]:
        """Rank value propositions by priority and trim to max_value_props."""
        if not value_props:
            return []
        
        # Calculate priority scores (higher score = higher priority)
        for vp in value_props:
            score = 0
            
            # Priority 1: Match to strategic themes (simplified check)
            if vp.angle == "strategic":
                score += 10
            
            # Priority 2: Presence of numeric impact
            achievement_text = vp.achievement_snippet.lower()
            if any(char in achievement_text for char in ["%", "$", "m", "k", "x"]):
                score += 5
            
            # Priority 3: Seniority alignment (EXECUTIVE gets bonus)
            if vp.archetype_target == "EXECUTIVE":
                score += 3
            
            vp.priority = score
        
        # Sort by priority (higher score = higher priority)
        value_props.sort(key=lambda x: -x.priority)
        
        # Assign sequential priorities and trim
        ranked = []
        for i, vp in enumerate(value_props[:self.max_value_props]):
            vp.priority = i + 1
            ranked.append(vp)
        
        return ranked
    
    def _build_sections(
        self,
        value_props: List[LICValueProposition],
        archetype: str,
    ) -> List[LICMessageSectionPlan]:
        """Build opening, body, and CTA section plans."""
        sections = []
        
        if not value_props:
            return sections
        
        # 1. Opening section
        opening_section = self._build_opening_section(value_props, archetype)
        sections.append(opening_section)
        
        # 2. Body sections
        body_sections = self._build_body_sections(value_props, archetype)
        sections.extend(body_sections)
        
        # 3. CTA section
        cta_section = self._build_cta_section(value_props, archetype)
        sections.append(cta_section)
        
        return sections
    
    def _build_opening_section(
        self,
        value_props: List[LICValueProposition],
        archetype: str,
    ) -> LICMessageSectionPlan:
        """Build the opening section plan."""
        # Select 1-2 top-priority strategic or market VPs
        strategic_vps = [
            vp for vp in value_props[:3] 
            if vp.angle in ["strategic", "market"]
        ]
        
        selected_vps = strategic_vps[:2] if strategic_vps else value_props[:2]
        vp_ids = [vp.id for vp in selected_vps]
        
        # Determine tone guidance
        tone_guidance = {
            "EXECUTIVE": "concise, strategic, signal-aware",
            "SENIOR_TA": "clear, technically grounded, concise",
            "RECRUITER": "clear, human, easy to skim",
        }.get(archetype.upper(), "clear and professional")
        
        metadata = {
            "section_index": 0,
            "is_terminal_section": False,
        }
        
        return LICMessageSectionPlan(
            section_type="opening",
            archetype_target=archetype.upper(),
            value_proposition_ids=vp_ids,
            tone_guidance=tone_guidance,
            cta_guidance=None,
            metadata=metadata,
        )
    
    def _build_body_sections(
        self,
        value_props: List[LICValueProposition],
        archetype: str,
    ) -> List[LICMessageSectionPlan]:
        """Build body section plans."""
        sections = []
        
        # Group remaining VPs by angle or theme
        remaining_vps = value_props[2:]  # Skip opening VPs
        
        # Create up to max_body_sections body sections
        for i in range(min(self.max_body_sections, len(remaining_vps))):
            start_idx = i * 2
            end_idx = start_idx + 2
            section_vps = remaining_vps[start_idx:end_idx]
            
            if not section_vps:
                break
            
            vp_ids = [vp.id for vp in section_vps]
            
            metadata = {
                "section_index": i + 1,
                "is_terminal_section": False,
            }
            
            section = LICMessageSectionPlan(
                section_type="body",
                archetype_target=archetype.upper(),
                value_proposition_ids=vp_ids,
                tone_guidance="evidence-based, clear, signal-aligned",
                cta_guidance=None,
                metadata=metadata,
            )
            
            sections.append(section)
        
        return sections
    
    def _build_cta_section(
        self,
        value_props: List[LICValueProposition],
        archetype: str,
    ) -> LICMessageSectionPlan:
        """Build the CTA section plan."""
        # Use top 1-3 VPs with strongest impact
        top_vps = value_props[:3]
        vp_ids = [vp.id for vp in top_vps]
        
        # Determine CTA guidance based on archetype
        cta_guidance_map = {
            "EXECUTIVE": "ask for 15 minutes to explore strategic alignment, not a formal interview",
            "SENIOR_TA": "propose brief technical discussion to explore fit and challenges",
            "RECRUITER": "express interest in role alignment and request brief conversation",
        }
        
        cta_guidance = cta_guidance_map.get(archetype.upper(), "request brief exploratory conversation")
        
        # Tone guidance reflects CTA style
        tone_guidance = {
            "EXECUTIVE": "respectful, concise, value-focused",
            "SENIOR_TA": "direct, technically relevant, clear",
            "RECRUITER": "warm, clear, role-focused",
        }.get(archetype.upper(), "professional and clear")
        
        # Calculate section index correctly
        section_index = 1 + len([s for s in [] if s.section_type in ["opening", "body"]])
        
        metadata = {
            "section_index": section_index,
            "is_terminal_section": True,
        }
        
        return LICMessageSectionPlan(
            section_type="cta",
            archetype_target=archetype.upper(),
            value_proposition_ids=vp_ids,
            tone_guidance=tone_guidance,
            cta_guidance=cta_guidance,
            metadata=metadata,
        )
    
    def _determine_cta_styles(self, archetype: str, enable_exec_strict_cta: bool) -> Tuple[str, str]:
        """Determine primary and fallback CTA styles based on archetype."""
        archetype_upper = archetype.upper()
        
        if archetype_upper == "EXECUTIVE":
            primary = "light_touch" if enable_exec_strict_cta else "exploratory_call"
            fallback = "exploratory_call"
        elif archetype_upper == "SENIOR_TA":
            primary = "exploratory_call"
            fallback = "light_touch"
        elif archetype_upper == "RECRUITER":
            primary = "direct"
            fallback = "light_touch"
        else:
            primary = "exploratory_call"
            fallback = "light_touch"
        
        return primary, fallback
    
    def _truncate_text(self, text: str, max_length: int) -> str:
        """Truncate text to maximum length with ellipsis if needed."""
        if len(text) <= max_length:
            return text
        
        return text[:max_length - 3].rstrip() + "..."
    
    def _safe_record_telemetry(self, plan: LICFusionPlan) -> None:
        """Record telemetry event safely without breaking planning."""
        if not self.telemetry_bus:
            return
        
        try:
            self.telemetry_bus.record_event(
                "lic_fusion_plan_created",
                layer="L1",
                payload={
                    "archetype": plan.archetype,
                    "role_title": plan.role_title,
                    "company_name": plan.company_name,
                    "value_prop_count": len(plan.value_propositions),
                    "section_count": len(plan.sections),
                    "primary_cta_style": plan.primary_cta_style,
                },
            )
        except Exception:
            # Telemetry failures should never break planning logic
            logger.debug("Failed to record telemetry for LIC fusion plan")
