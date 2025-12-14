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
    Selects the best model for the job (Claude 4.5, GPT-5.1, or Gemini 3).
    """
    
    def __init__(self, provider: str = "anthropic"):
        # 1. Connect to Memory
        self.cm = ConnectionManager()
        self.redis_index = self.cm.get_redis_index()
        self.pinecone_index = self.cm.get_pinecone_index()
        self.embedding_fn = self.cm.get_embedding
        
        # 2. Connect to Intelligence
        # Options: "anthropic" (Claude 4.5), "openai" (GPT-5.1), "google" (Gemini 3)
        self.llm = LLMClient(provider=provider)
        
        # 3. Define Canon-Compliant Persona
        self.system_prompt_template = """
You are a Subatomic Architect Agent (Model: {model_name}).
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

    def generate_plan(self, user_goal: str) -> Dict[str, Any]:
        """The Core Loop: Retrieve -> Prompt -> Plan."""
        # 1. Retrieve
        relevant_context = self.retrieve_context(user_goal)
        context_block = "\n---\n".join(relevant_context) if relevant_context else "NO RELEVANT PRECEDENTS FOUND."
        
        # 2. Construct System Context
        system_prompt = self.system_prompt_template.format(
            model_name=self.llm.model,
            context_block=context_block
        )
        
        # 3. Call LLM
        result = self.llm.generate_plan(system_context=system_prompt, user_goal=user_goal)
        result["retrieved_items"] = len(relevant_context)
        
        return result

if __name__ == "__main__":
    # Test switching brains
    print("🧠 Testing GPT-5.1 Brain:")
    brain_gpt = CognitiveNode(provider="openai")
    res_gpt = brain_gpt.generate_plan("Write a hello world python file")
    print(f"GPT Plan Steps: {len(res_gpt.get('plan', {}).get('steps', []))}")
    
    print("\n🧠 Testing Claude 4.5 Brain:")
    brain_claude = CognitiveNode(provider="anthropic")
    res_claude = brain_claude.generate_plan("Write a hello world python file")
    print(f"Claude Plan Steps: {len(res_claude.get('plan', {}).get('steps', []))}")
