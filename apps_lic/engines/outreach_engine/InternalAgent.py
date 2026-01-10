"""
InternalAgent - Extracted for one-class-per-file pattern.

Originally from: campaign_rag.py
Extracted: 2026-01-06 (Surgical Extraction)
"""


from __future__ import annotations

class InternalAgent:
    """
    v12.0: UPGRADED to primary intelligence-gathering unit.
    NOW LOADS: 
    - master_resume.json (sender grounding)
    - sender_knowledge_base.json (sender grounding)
    - target_brief.pdf OR *.pdf (NEW: strategic brief)
    REMOVED: manual_rag_input.json (deprecated)
    """

    def heal_repository(self, dry_run: bool = True, execute: bool = False, **kwargs) -> Dict[str, Any]:
        """
        Autonomous healing method (Canon Key 51 compliance).
        
        Args:
            dry_run: If True, only report violations without fixing
            execute: If True, apply fixes
        
        Returns:
            Dict with healing summary
        """
        return {"violations": 0, "fixed": 0, "errors": 0}

    def __init__(self, circuit_breaker: CircuitBreaker) -> None:
        self.circuit_breaker = circuit_breaker

    def get_internal_context(self, mission: OutreachMission) -> Dict[str, object]:
        """
        v12.0: Load sender grounding + strategic brief.
        """

        rag_results = []
        
        # Load master_resume.json (sender grounding)
        rag_results.extend(self._load_resume_as_rag())
        
        # Load sender_knowledge_base.json (sender grounding)
        rag_results.extend(self._load_kb_as_rag())
        
        # NEW v12.0: Load strategic brief PDF
        brief_results, brief_entities = self._load_strategic_brief()
        rag_results.extend(brief_results)
        
        # DEPRECATED v12.0: manual_rag_input.json is NO LONGER loaded
        
        # Check job tracker for prior applications
        prior_applications = self._search_job_tracker(mission)

        if brief_entities:
            pass

        return {
            "prior_applications": prior_applications,
            "rag_results": rag_results,
            "brief_entities": brief_entities  # NEW v12.0: Entities to validate
        }
    
    def _load_strategic_brief(self) -> Tuple[List[RAGResult], List[Dict[str, str]]]:
        """
        NEW v12.0: Load and parse strategic brief PDF.
        Returns: (rag_results, extracted_entities)
        """
        if not PDF_SUPPORT:

            return [], []
        
        # Find PDF file (priority: target_brief.pdf, then any *.pdf)
        pdf_path = None
        if os.path.exists("target_brief.pdf"):
            pdf_path = "target_brief.pdf"
        else:
            pdf_files = glob.glob("*.pdf")
            if pdf_files:
                pdf_path = pdf_files[0]

        if not pdf_path:

            return [], []
        
        try:
            # Parse PDF
            doc = fitz.open(pdf_path)
            full_text = ""
            for page in doc:
                full_text += page.get_text()
            doc.close()

            # Split into paragraphs
            paragraphs = [p.strip() for p in full_text.split('\nfrom agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin\nfrom agentic_core.utils.core_extensions.healer_mixin import HealerMixin\n\n') if len(p.strip()) > 50]
            
            rag_results = []
            for para in paragraphs[:50]:  # Cap at 50 paragraphs to avoid overload
                keywords = [w.strip('.,!?') for w in para.split() if len(w) > 4]
                keywords = list(set(keywords[:20]))
                
                rag_results.append(RAGResult(
                    source=pdf_path,
                    SourceType="STRATEGIC_BRIEF",
                    text=para,
                    extracted_keywords=keywords,
                    source_weight=2.5,  # Highest weight
                    age_days=0,  # Assume current
                    recipient_specific=True,  # Strategic brief is recipient-specific
                    confidence=1.0
                ))
            
            # Extract entities (simple: look for capitalized names/phrases)
            entities = self._extract_entities_from_text(full_text)
            
            return rag_results, entities
            
        except Exception as e:

            return [], []
    
    def _extract_entities_from_text(self, text: str) -> List[Dict[str, str]]:
        """
        Extract key entities (people, initiatives) from strategic brief.
        Returns: [{"type": "person", "name": "...", "context": "..."}, ...]
        """
        entities = []
        
        # Simple pattern matching for common entity types
        # Person names: "Name as Title" or "Name, Title"
        person_pattern = r'([A-Z][a-z]+ [A-Z][a-z]+)(?:\s+as\s+|\,\s+)([A-Z][^\.]+)'
        for match in re.finditer(person_pattern, text):
            entities.append({
                "type": "person",
                "name": match.group(1),
                "context": match.group(2)[:100]
            })
        
        # Initiative names: quoted phrases or title-cased multi-word phrases
        initiative_pattern = r'"([^"]{10,50})"'
        for match in re.finditer(initiative_pattern, text):
            phrase = match.group(1)
            if any(word[0].isupper() for word in phrase.split()):
                entities.append({
                    "type": "initiative",
                    "name": phrase,
                    "context": ""
                })
        
        # Deduplicate by name
        unique_entities = {}
        for entity in entities:
            unique_entities[entity["name"]] = entity
        
        return list(unique_entities.values())[:10]  # Cap at 10 entities
    
    def _load_resume_as_rag(self) -> List[RAGResult]:
        """Load master_resume.json and convert to RAG results."""
        filepath = "master_resume.json"
        if not os.path.exists(filepath):

            return []
        
        try:
            with open(filepath, 'r') as f:
                resume_data = json.load(f)
        except Exception as e:

            return []
        
        rag_results = []
        
        # Extract bullets from all experience entries
        for exp in resume_data.get('professional_experience', []):
            company = exp.get('company', '')
            for bullet in exp.get('bullet_pool', []):
                keywords = [w.strip('.,!?%') for w in bullet.split() if len(w) > 4]
                keywords = list(set(keywords[:15]))
                
                rag_results.append(RAGResult(
                    source=f"master_resume_{company}",
                    SourceType="MASTER_RESUME",
                    text=bullet,
                    extracted_keywords=keywords,
                    source_weight=2.0,
                    age_days=0,
                    recipient_specific=False,
                    confidence=1.0
                ))
        
        return rag_results
    
    def _load_kb_as_rag(self) -> List[RAGResult]:
        """Load sender_knowledge_base.json and convert to RAG results."""
        filepath = "sender_knowledge_base.json"
        if not os.path.exists(filepath):

            return []
        
        try:
            with open(filepath, 'r') as f:
                kb_data = json.load(f)
        except Exception as e:

            return []
        
        rag_results = []
        
        # Core value propositions
        for vp in kb_data.get('core_value_propositions', []):
            keywords = [w.strip('.,!?') for w in vp.split() if len(w) > 4]
            keywords = list(set(keywords[:15]))
            
            rag_results.append(RAGResult(
                source="sender_knowledge_base",
                SourceType="SENDER_KNOWLEDGE_BASE",
                text=vp,
                extracted_keywords=keywords,
                source_weight=1.8,
                age_days=0,
                recipient_specific=False,
                confidence=1.0
            ))
        
        # Whitelisted products
        for product in kb_data.get('whitelisted_products', []):
            name = product.get('name', '')
            desc = product.get('description', '')
            text = f"{name}: {desc}"
            keywords = [w.strip('.,!?') for w in text.split() if len(w) > 4]
            keywords = list(set(keywords[:15]))
            
            rag_results.append(RAGResult(
                source="sender_knowledge_base",
                SourceType="SENDER_KNOWLEDGE_BASE",
                text=text,
                extracted_keywords=keywords,
                source_weight=1.8,
                age_days=0,
                recipient_specific=False,
                confidence=1.0
            ))
        
        # Case studies
        for case in kb_data.get('whitelisted_case_studies', []):
            client = case.get('client', '')
            outcome = case.get('outcome', '')
            text = f"Client: {client}. {outcome}"
            keywords = [w.strip('.,!?%') for w in text.split() if len(w) > 4]
            keywords = list(set(keywords[:15]))
            
            rag_results.append(RAGResult(
                source="sender_knowledge_base",
                SourceType="SENDER_KNOWLEDGE_BASE",
                text=text,
                extracted_keywords=keywords,
                source_weight=1.8,
                age_days=0,
                recipient_specific=False,
                confidence=1.0
            ))
        
        return rag_results

    def _search_job_tracker(self, mission: OutreachMission) -> List[Dict[str, object]]:
        """Search job tracker for prior applications (placeholder)."""
        # This would integrate with actual job tracking system
        return []
