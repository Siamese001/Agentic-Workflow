import time
import json
import logging
from typing import List, Dict, Any

# Import infrastructure
from connection_manager import ConnectionManager
from redisvl.query import VectorQuery
from llm_client import LLMClient

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("CognitiveNode")

class CognitiveNode:
    """
    The 'Brain' of the Agent.
    Uses Tiered Thinking Protocol to route to appropriate LLM tier.
    """
    
    def __init__(self):
        # 1. Connect to Memory
        self.cm = ConnectionManager()
        self.redis_index = self.cm.get_redis_index()
        self.pinecone_index = self.cm.get_pinecone_index()
        self.embedding_fn = self.cm.get_embedding
        
        # 2. Connect to Intelligence (Universal LLM Client)
        self.llm = LLMClient()
        
        # 3. Define Canon-Compliant Persona
        self.system_prompt_template = """
You are a Subatomic Architect Agent.
You do not guess. You follow the Canon explicitly.

CONTEXT FROM MEMORY (Canon):
{context_block}

AVAILABLE TOOLS:
- write_file(filename, content): Create or overwrite code files.
- read_file(filename): Read contents.
- list_files(subdir): Check workspace.

TASK:
Create a step-by-step execution plan to achieve the User Goal.
If the Context contains a function or rule, you MUST use it exactly as it appears.
"""

    def retrieve_context(self, query: str, top_k: int = 3) -> List[str]:
        """Queries the Canon (Hot + Cold) for relevant patterns."""
        logger.info(f"🤔 Thinking... Searching Canon for: '{query}'")
        context_matches = []
        
        try:
            vector = self.embedding_fn(query)
            
            # Check Cold Memory (Pinecone)
            pc_results = self.pinecone_index.query(vector=vector, top_k=top_k, include_metadata=True)
            for match in pc_results.get('matches', []):
                if match['score'] > 0.70:
                    meta = match.get('metadata', {})
                    context_matches.append(f"[SOURCE: {meta.get('source', 'unknown')}] {meta.get('content', '')}")
                    
            # Check Hot Memory (Redis)
            v_query = VectorQuery(
                vector=vector,
                vector_field_name="embedding", 
                return_fields=["code_snippet", "project_context"],
                num_results=top_k
            )
            redis_results = self.redis_index.query(v_query)
            for match in redis_results:
                context_matches.append(f"[SOURCE: {match.get('project_context', 'hot_cache')}] {match.get('code_snippet')}")
                
        except Exception as e:
            logger.error(f"Retrieval failed: {e}")
            
        return list(set(context_matches))

    def think(self, user_goal: str, complexity: str = "high") -> Dict[str, Any]:
        """
        The Thinking Loop with Tiered Architecture.
        Args:
            complexity: 'high' (Consensus) or 'low' (Mini)
        """
        # 1. Retrieve
        relevant_context = self.retrieve_context(user_goal)
        context_block = "\n---\n".join(relevant_context) if relevant_context else "NO RELEVANT PRECEDENTS FOUND."
        
        # 2. Construct System Context
        system_prompt = self.system_prompt_template.format(
            context_block=context_block
        )
        
        # 3. Execute via Tiered LLM Client
        result = self.llm.generate_plan(system_context=system_prompt, user_goal=user_goal, complexity=complexity)
        result["retrieved_items"] = len(relevant_context)
        
        return result

    def generate_plan(self, user_goal: str) -> Dict[str, Any]:
        """Legacy method - defaults to high complexity."""
        return self.think(user_goal, complexity="high")

if __name__ == "__main__":
    # Test Tiered Thinking
    print("🧠 Testing High Complexity (Consensus):")
    brain = CognitiveNode()
    res_high = brain.think("Write a complex enterprise system with microservices", complexity="high")
    print(f"High Complexity Plan Steps: {len(res_high.get('plan', {}).get('steps', []))}")
    
    print("\n⚡ Testing Low Complexity (Mini):")
    res_low = brain.think("Write a hello world python file", complexity="low")
    print(f"Low Complexity Plan Steps: {len(res_low.get('plan', {}).get('steps', []))}")
