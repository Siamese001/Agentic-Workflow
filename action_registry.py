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

    def get_tool_map(self) -> Dict[str, Callable]:
        """
        Returns the dictionary of safe tools to inject into the Agent's scope.
        """
        return {
            "search_web": self.search_web,
            "read_file": self.read_file,
            "save_file": self.save_file,
            "send_email": self.mock_send_email,
            # Redis MCP Tools
            "string_set": self.string_set,
            "string_get": self.string_get,
            "hash_set": self.hash_set,
            "hash_get": self.hash_get
        }
