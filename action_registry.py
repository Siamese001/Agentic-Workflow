import os
import requests
import json
import logging
from typing import Dict, Any, Callable

# Optional: Add PyPDF2 to requirements.txt for this to work
try:
    import PyPDF2
except ImportError:
    PyPDF2 = None

logger = logging.getLogger("ActionRegistry")

class ActionRegistry:
    """
    The 'Hands' of the Agent.
    Contains the whitelist of allowed actions (Key #3).
    """
    
    def __init__(self):
        self.brave_key = os.getenv("BRAVE_SEARCH_API_KEY")
        if not self.brave_key:
            logger.warning("⚠️ BRAVE_SEARCH_API_KEY not found. Web search will fail.")
        
        # Mock Redis storage for L1 caching
        self._redis_store: Dict[str, str] = {}
        self._redis_hash: Dict[str, Dict[str, str]] = {}

    # --- CORE TOOLS (Canon Validator) ---
    def search_web(self, query: str) -> str:
        """
        Performs a real web search using Brave API.
        Tool ID: ACT-001
        """
        if not self.brave_key:
            return "Error: No Search API Key configured."
            
        logger.info(f"🌐 Searching Web: '{query}'")
        try:
            url = "https://api.search.brave.com/res/v1/web/search"
            headers = {
                "X-Subscription-Token": self.brave_key,
                "Accept": "application/json"
            }
            params = {"q": query, "count": 3}  # Limit to top 3 results for cost/speed
            
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            # Parse the results into a clean string
            results = []
            if "web" in data and "results" in data["web"]:
                for item in data["web"]["results"]:
                    title = item.get('title', 'No Title')
                    desc = item.get('description', 'No Description')
                    link = item.get('url', 'No Link')
                    results.append(f"Title: {title}\nSummary: {desc}\nLink: {link}\n---")
            
            return "\n".join(results) if results else "No results found."
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return f"Search Error: {str(e)}"

    # --- RESUME ENGINE TOOLS ---
    def read_file(self, file_path: str) -> str:
        """Reads text from .txt, .md, or .pdf files."""
        try:
            if file_path.endswith('.pdf'):
                if not PyPDF2: return "Error: PyPDF2 module not installed."
                with open(file_path, 'rb') as f:
                    reader = PyPDF2.PdfReader(f)
                    return "\n".join([page.extract_text() for page in reader.pages])
            else:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
        except Exception as e: return f"Read Error: {e}"

    def save_file(self, content: str, file_path: str) -> str:
        """Saves content to a file."""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return f"✅ File saved successfully: {file_path}"
        except Exception as e: return f"Save Error: {e}"

    # --- OUTREACH ENGINE TOOLS ---
    def mock_send_email(self, recipient: str, subject: str, body: str) -> str:
        """Simulates sending an email (Safety first)."""
        # In Phase 4 we will connect real SMTP
        logger.info(f"📧 EMAIL SENT to {recipient} | Subj: {subject}")
        return f"Email simulated sent to {recipient}"
    
    # --- REDIS MCP TOOLS (L1 Caching) ---
    def string_set(self, key: str, value: str) -> str:
        """Stores a simple string key-value pair in Redis."""
        self._redis_store[key] = value
        logger.info(f"📦 Redis SET: {key} = {value[:20]}...")
        return f"OK: Stored {key}"
    
    def string_get(self, key: str) -> str:
        """Retrieves a string value from Redis."""
        value = self._redis_store.get(key)
        if value is None:
            return f"NULL: Key '{key}' not found"
        logger.info(f"📦 Redis GET: {key} = {value[:20]}...")
        return value
    
    def hash_set(self, key: str, field: str, value: str) -> str:
        """Stores a field-value pair in a Redis hash."""
        if key not in self._redis_hash:
            self._redis_hash[key] = {}
        self._redis_hash[key][field] = value
        logger.info(f"📦 Redis HSET: {key}.{field} = {value[:20]}...")
        return f"OK: Stored {key}.{field}"
    
    def hash_get(self, key: str, field: str) -> str:
        """Retrieves a field value from a Redis hash."""
        if key not in self._redis_hash or field not in self._redis_hash[key]:
            return f"NULL: {key}.{field} not found"
        value = self._redis_hash[key][field]
        logger.info(f"📦 Redis HGET: {key}.{field} = {value[:20]}...")
        return value

    # --- TIME MCP TOOLS (L4 Temporal Awareness) ---
    def get_current_time(self, timezone: str = "UTC") -> str:
        """Gets the current date, time, and timezone in ISO 8601 format."""
        try:
            from mcp_time_client import get_current_time as mcp_get_time
            return mcp_get_time(timezone)
        except ImportError:
            from datetime import datetime
            import pytz
            try:
                tz = pytz.timezone(timezone)
                now = datetime.now(tz)
                return now.isoformat()
            except Exception as e:
                return f"Error getting time: {e}"
    
    def convert_time(self, source_timezone: str, time: str, target_timezone: str) -> str:
        """Converts a time string between two specified IANA timezones."""
        try:
            from mcp_time_client import convert_time as mcp_convert_time
            return mcp_convert_time(source_timezone, time, target_timezone)
        except ImportError:
            return f"Error: MCP Time client not available for conversion"

    def commit(self, file_path: str, message: str) -> str:
        """Commits a file to git."""
        try:
            from mcp0_git_add_or_commit import mcp0_git_add_or_commit
            mcp0_git_add_or_commit(directory=".", action="add", files=[file_path])
            result = mcp0_git_add_or_commit(directory=".", action="commit", files=[file_path], message=message)
            return f"✅ Committed: {message}"
        except Exception as e: return f"Commit Error: {e}"
    
    def status(self) -> str:
        """Gets git status."""
        try:
            from mcp0_git_status import mcp0_git_status
            result = mcp0_git_status(directory=".")
            return result
        except Exception as e: return f"Status Error: {e}"
    
    # --- FIGMA MCP TOOLS (L2 Design) - Stubs for Phase 1 ---
    def get_variable_defs(self, node_id: str, file_key: str = None) -> str:
        """Gets Figma variable definitions."""
        return "Figma MCP not implemented in Phase 1"
    
    def get_design_context(self, node_id: str, file_key: str = None) -> str:
        """Gets Figma design context."""
        return "Figma MCP not implemented in Phase 1"
    
    def get_screenshot(self, node_id: str, file_key: str = None) -> str:
        """Gets Figma screenshot."""
        return "Figma MCP not implemented in Phase 1"
    
    # --- PINECONE MCP TOOLS (L3 RAG) - Stubs for Phase 1 ---
    def search_records(self, query: str, index: str, top_k: int, namespace: str) -> str:
        """Searches Pinecone records."""
        return "Pinecone MCP not implemented in Phase 1"
    
    # --- MEMORY MCP TOOLS (L5 MEMemory) - Stubs for Phase 1 ---
    def add_observations(self, observations: list) -> str:
        """Adds observations to MEMemory."""
        return "MEMemory MCP not implemented in Phase 1"
    
    def create_entities(self, entities: list) -> str:
        """Creates entities in MEMemory."""
        return "MEMemory MCP not implemented in Phase 1"
    
    def open_nodes(self, names: list) -> str:
        """Opens nodes in MEMemory."""
        return "MEMemory MCP not implemented in Phase 1"

    def get_tool_map(self) -> Dict[str, Callable]:
        """Returns the master tool map for the LLM."""
        return {
            # --- LAYER 1: FILESYSTEM & I/O ---
            "read_file": self.read_file,
            "save_file": self.save_file,
            "send_email": self.mock_send_email,
            
            # --- LAYER 2: DESIGN & CONTEXT ---
            "get_variable_defs": self.get_variable_defs,
            "get_design_context": self.get_design_context,
            "get_screenshot": self.get_screenshot,
            
            # --- LAYER 3: RAG & WISDOM ---
            "search_records": self.search_records,
            "search_web": self.search_web,
            
            # --- LAYER 4: STATE & TEMPORAL ---
            "string_set": self.string_set,
            "string_get": self.string_get,
            "hash_set": self.hash_set,
            "hash_get": self.hash_get,
            "get_current_time": self.get_current_time,
            "convert_time": self.convert_time,
            
            # --- LAYER 5: MEMORY & AUDIT ---
            "add_observations": self.add_observations,
            "create_entities": self.create_entities,
            "open_nodes": self.open_nodes,
            
            # --- GIT OPERATIONS ---
            "commit": self.commit,
            "status": self.status,
        }
