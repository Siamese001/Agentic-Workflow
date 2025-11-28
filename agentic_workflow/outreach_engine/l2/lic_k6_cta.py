from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta

@dataclass
class CTAOutput:
    final_cta: str
    date_window: str
    cta_style: str
    word_count: int

class LIC_K6_CTA:
    def __init__(self, cta_plan: Dict[str, Any]):
        self.plan = cta_plan
        
    def generate_date_window(self) -> str:
        date_config = self.plan["date_window_rules"]
        buffer_map = date_config["business_day_buffer_map"]
        
        today = datetime.now()
        current_day = today.strftime("%A")
        
        buffer_info = buffer_map.get(current_day, buffer_map["Monday"])
        min_buffer = buffer_info["min_buffer_days"]
        
        dates = []
        for i in range(3):
            future_date = today + timedelta(days=min_buffer + i*2)
            
            while future_date.weekday() >= 5:
                future_date += timedelta(days=1)
                
            dates.append(future_date.strftime("%m/%d"))
            
        output_format = date_config["output_format"]["natural_language"]
        return output_format.replace("[date1]", dates[0]).replace("[date2]", dates[1]).replace("[date3]", dates[2])
    
    def apply_archetype_cta_style(self, archetype: str, date_window: str, message_context: Dict[str, Any]) -> str:
        archetype_styles = self.plan["archetype_styles"]
        
        style_config = archetype_styles.get(archetype, archetype_styles["EXECUTIVE"])
        
        if archetype == "C_LEVEL":
            base_cta = "Would you have 15 minutes to discuss strategic alignment opportunities?"
        elif archetype == "EXECUTIVE":
            base_cta = f"Would {date_window} work for a brief discussion on mutual objectives?"
        elif archetype == "SENIOR_TA":
            recipient = message_context.get("recipient", {})
            company = recipient.get("company", "")
            base_cta = f"Would you have time to explore how technical innovation could support {company}?"
        else:  # RECRUITER
            base_cta = "Would you be open to a quick chat about potential alignment?"
            
        return base_cta
    
    def validate_cta_constraints(self, cta_text: str, archetype: str) -> List[str]:
        violations = []
        
        word_count = len(cta_text.split())
        
        word_limits = {
            "C_LEVEL": [15, 20],
            "EXECUTIVE": [15, 20],
            "SENIOR_TA": [10, 15],
            "RECRUITER": [10, 15]
        }
        
        target_range = word_limits.get(archetype, [10, 20])
        
        if word_count < target_range[0]:
            violations.append(f"CTA too short: {word_count} < {target_range[0]}")
        elif word_count > target_range[1]:
            violations.append(f"CTA too long: {word_count} > {target_range[1]}")
            
        if "?" not in cta_text:
            violations.append("CTA must be a question")
            
        forbidden_phrases = ["let me know", "feel free", "don't hesitate"]
        for phrase in forbidden_phrases:
            if phrase in cta_text.lower():
                violations.append(f"CTA contains forbidden phrase: {phrase}")
                
        return violations
    
    def refine_cta_based_on_violations(self, cta_text: str, violations: List[str], archetype: str) -> str:
        refined = cta_text
        
        for violation in violations:
            if "too short" in violation:
                if archetype == "C_LEVEL":
                    refined += " to explore strategic synergies"
                elif archetype == "EXECUTIVE":
                    refined += " to discuss collaborative opportunities"
                else:
                    refined += " to explore mutual interests"
                    
            elif "too long" in violation:
                words = refined.split()
                if archetype in ["C_LEVEL", "EXECUTIVE"]:
                    refined = " ".join(words[:20])
                else:
                    refined = " ".join(words[:15])
                    
            elif "must be a question" in violation:
                if not refined.endswith("?"):
                    refined = refined.rstrip(".") + "?"
                    
        return refined
    
    def execute(self, message_context: Dict[str, Any], archetype: str) -> CTAOutput:
        date_window = self.generate_date_window()
        
        initial_cta = self.apply_archetype_cta_style(archetype, date_window, message_context)
        
        violations = self.validate_cta_constraints(initial_cta, archetype)
        
        final_cta = initial_cta
        if violations:
            final_cta = self.refine_cta_based_on_violations(initial_cta, violations, archetype)
        
        cta_style = self.plan["archetype_styles"][archetype]["style"]
        
        return CTAOutput(
            final_cta=final_cta,
            date_window=date_window,
            cta_style=cta_style,
            word_count=len(final_cta.split())
        )
