from typing import Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class DraftOutput:
    greeting: str
    subject_line: Optional[str]
    message_body: str
    cta_draft: str
    signature: str
    word_count: int
    archetype_applied: str

class LIC_K3_Draft:
    def __init__(self, template_plan: Dict[str, Any], tone_plan: Dict[str, Any]):
        self.templates = template_plan
        self.tone = tone_plan
        
    def generate_greeting(self, recipient: Dict[str, Any]) -> str:
        if recipient.get("first_name"):
            greeting = f"Hi {recipient['first_name']},"
        else:
            greeting = "Hello,"
            
        return greeting
    
    def generate_subject_line(self, recipient: Dict[str, Any], message_type: str, tone_profile: Dict[str, Any]) -> Optional[str]:
        if message_type not in ["INMAIL", "LONG_NEW"]:
            return None
            
        title = recipient.get("title", "")
        company = recipient.get("company", "")
        
        subject_templates = [
            f"Strategic discussion about {company}",
            f"Exploring synergies in {title} role",
            f"Value alignment opportunities",
            f"Growth initiatives at {company}"
        ]
        
        selected_template = subject_templates[0]
        
        if len(selected_template.split()) > 10:
            words = selected_template.split()
            selected_template = " ".join(words[:10])
            
        return selected_template
    
    def apply_tone_adaptation(self, base_text: str, archetype: str, recipient: Dict[str, Any]) -> str:
        if archetype == "C_LEVEL":
            adaptations = [
                "strategic impact",
                "organizational transformation", 
                "business outcomes",
                "market leadership"
            ]
        elif archetype == "EXECUTIVE":
            adaptations = [
                "team objectives",
                "operational excellence",
                "collaborative value",
                "mutual success"
            ]
        elif archetype == "SENIOR_TA":
            adaptations = [
                "technical excellence",
                "architectural decisions",
                "innovation opportunities",
                "scalable solutions"
            ]
        else:  # RECRUITER
            adaptations = [
                "role alignment",
                "career growth",
                "skill development",
                "team fit"
            ]
            
        adapted_text = base_text
        
        for adaptation in adaptations[:2]:
            if adaptation not in adapted_text:
                adapted_text += f" with focus on {adaptation}"
                
        return adapted_text
    
    def generate_message_body(self, research_output: Dict[str, Any], archetype: str, recipient: Dict[str, Any]) -> str:
        sources = research_output.get("rag_sources", [])
        
        key_insights = []
        for source in sources[:3]:
            content = source.get("content", "")
            if "initiative" in content.lower():
                key_insights.append("strategic initiatives")
            elif "growth" in content.lower():
                key_insights.append("growth opportunities")
            elif "technology" in content.lower():
                key_insights.append("technology innovation")
                
        title = recipient.get("title", "")
        company = recipient.get("company", "")
        
        base_body = f"I noticed your work as {title} at {company}. "
        
        if key_insights:
            base_body += f"Given the focus on {', '.join(key_insights[:2])}, "
        else:
            base_body += "Given your leadership role, "
            
        base_body += "I believe there could be valuable alignment in our approaches to driving organizational success. "
        base_body += "My experience in building high-performing teams and delivering measurable results could complement your current objectives."
        
        adapted_body = self.apply_tone_adaptation(base_body, archetype, recipient)
        
        word_count_targets = {
            "C_LEVEL": [190, 230],
            "EXECUTIVE": [160, 220], 
            "SENIOR_TA": [150, 190],
            "RECRUITER": [140, 170]
        }
        
        target_range = word_count_targets.get(archetype, [160, 220])
        current_words = len(adapted_body.split())
        
        if current_words < target_range[0]:
            additional_content = " This could create significant value through shared expertise and strategic partnership."
            adapted_body += additional_content
        elif current_words > target_range[1]:
            words = adapted_body.split()
            adapted_body = " ".join(words[:target_range[1]])
            
        return adapted_body
    
    def generate_cta_draft(self, archetype: str, date_window: Optional[str] = None) -> str:
        if archetype == "C_LEVEL":
            return "Would you have 15 minutes to discuss strategic alignment opportunities?"
        elif archetype == "EXECUTIVE":
            return f"Would {date_window or 'next week'} work for a brief discussion on mutual objectives?"
        elif archetype == "SENIOR_TA":
            return "Would you have time to explore technical collaboration opportunities?"
        else:  # RECRUITER
            return "Would you be open to a brief chat about potential alignment?"
    
    def generate_signature(self, message_type: str, sender_info: Dict[str, Any]) -> str:
        if message_type == "CONNECTION_REQ":
            return f"Best regards,\n{sender_info.get('first_name', 'Regards')}"
        elif message_type in ["INMAIL", "LONG_NEW"]:
            return f"{sender_info.get('first_name', '')} {sender_info.get('last_name', '')}\n{sender_info.get('title', '')}\n{sender_info.get('linkedin_url', '')}"
        else:
            return f"Warm regards,\n{sender_info.get('first_name', '')}"
    
    def execute(self, research_output: Dict[str, Any], message_context: Dict[str, Any], sender_info: Dict[str, Any]) -> DraftOutput:
        recipient = message_context.get("recipient", {})
        message_type = message_context.get("type", "SHORT_NEW")
        archetype = message_context.get("recipient_type", "EXECUTIVE")
        
        greeting = self.generate_greeting(recipient)
        
        subject_line = self.generate_subject_line(recipient, message_type, self.tone["archetype_mappings"].get(archetype, {}))
        
        message_body = self.generate_message_body(research_output, archetype, recipient)
        
        date_window = message_context.get("date_window")
        cta_draft = self.generate_cta_draft(archetype, date_window)
        
        signature = self.generate_signature(message_type, sender_info)
        
        full_message = f"{greeting} {message_body} {cta_draft} {signature}"
        word_count = len(full_message.split())
        
        return DraftOutput(
            greeting=greeting,
            subject_line=subject_line,
            message_body=message_body,
            cta_draft=cta_draft,
            signature=signature,
            word_count=word_count,
            archetype_applied=archetype
        )
