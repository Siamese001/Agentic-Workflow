import os
import time
import json
import logging
from typing import List, Dict, Any

# Import our hardened infrastructure
from connection_manager import ConnectionManager
from redisvl.query import VectorQuery

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("CognitiveNode")

class CognitiveNode:
    """
    The 'Brain' of the Agent.
    Responsibility: Retrieve context -> Formulate Plan -> Hand off to Action Plane.
    """
    
    def __init__(self):
        self.cm = ConnectionManager()
        self.redis_index = self.cm.get_redis_index()
        self.pinecone_index = self.cm.get_pinecone_index()
        self.embedding_fn = self.cm.get_embedding
        
        # System Prompt that enforces the usage of retrieved context
        self.system_prompt_template = """
You are a Subatomic Architect Agent. 
You do not guess. You follow the Canon.

CONTEXT FROM MEMORY (Canon):
{context_block}

USER GOAL:
{user_goal}

TASK:
Create a step-by-step execution plan to achieve the User Goal.
Your plan must explicitly reference the patterns found in the Context.
If the Context contains a function or rule, you MUST use it.
"""

    def retrieve_context(self, query: str, top_k: int = 3) -> List[str]:
        """
        Queries the Canon (Hot + Cold) for relevant patterns.
        """
        logger.info(f"🤔 Thinking... Searching Canon for: '{query}'")
        context_matches = []
        
        try:
            vector = self.embedding_fn(query)
            
            # 1. Check Cold Memory (Pinecone) - Best for semantic depth
            pc_results = self.pinecone_index.query(
                vector=vector,
                top_k=top_k,
                include_metadata=True
            )
            
            for match in pc_results.get('matches', []):
                if match['score'] > 0.60: # Lowered threshold for better recall
                    meta = match.get('metadata', {})
                    content = meta.get('content', '')
                    source = meta.get('source', 'unknown')
                    context_matches.append(f"[SOURCE: {source}] {content}")
                    
            # 2. Check Hot Memory (Redis) - Best for recent/exact interactions
            # FIX: Using 'embedding' field based on your schema
            v_query = VectorQuery(
                vector=vector,
                vector_field_name="embedding", 
                return_fields=["code_snippet", "project_context"],
                num_results=top_k
            )
            redis_results = self.redis_index.query(v_query)
            
            for match in redis_results:
                # RedisVL returns distance; we assume it's relevant if returned
                context_matches.append(f"[SOURCE: {match.get('project_context', 'hot_cache')}] {match.get('code_snippet')}")
                
        except Exception as e:
            logger.error(f"Retrieval failed: {e}")
            # Fallback: Proceed without context rather than crashing
            pass
            
        return list(set(context_matches)) # Deduplicate

    def generate_plan(self, user_goal: str) -> Dict[str, Any]:
        """
        The core loop: Retrieve -> Prompt -> Plan.
        """
        start_time = time.time()
        
        # 1. Retrieve
        relevant_context = self.retrieve_context(user_goal)
        context_block = "\n---\n".join(relevant_context) if relevant_context else "NO RELEVANT PRECEDENTS FOUND."
        
        # 2. Construct Prompt
        full_prompt = self.system_prompt_template.format(
            context_block=context_block,
            user_goal=user_goal
        )
        
        # 3. Call LLM (Mocked for Connectivity Check)
        # In production, this would be: response = openai.chat.completions.create(...)
        logger.info("🤖 Synthesizing Plan with LLM...")
        
        # --- MOCK LLM RESPONSE START ---
        # This simulates the LLM reading your context and generating a valid plan
        mock_plan = {
            "goal": user_goal,
            "reasoning": "Based on the retrieved context, I must separate concerns.",
            "steps": [
                {"step": 1, "action": "Define Cognitive State", "detail": "Use variable 'cognitive_state'"},
                {"step": 2, "action": "Define Action State", "detail": "Use variable 'action_state'"},
                {"step": 3, "action": "Validate Separation", "detail": "Ensure logic matches 'validate_cognitive_action_separation' pattern"}
            ],
            "context_used": len(relevant_context) > 0
        }
        # --- MOCK LLM RESPONSE END ---
        
        logger.info(f"✅ Plan Generated in {time.time() - start_time:.2f}s")
        return {
            "prompt_used": full_prompt,
            "plan": mock_plan,
            "retrieved_items": len(relevant_context)
        }

if __name__ == "__main__":
    # Test the Brain
    brain = CognitiveNode()
    
    # Give it a task that requires the knowledge we just ingested
    result = brain.generate_plan("I need to write a function that prevents hallucinations by separating thinking from doing.")
    
    print("\n🧠 GENERATED PROMPT (What the LLM sees):")
    print("="*60)
    print(result['prompt_used'])
    print("="*60)
    
    print("\n📋 GENERATED PLAN:")
    print(json.dumps(result['plan'], indent=2))
