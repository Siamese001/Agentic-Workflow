import logging
import os
from typing import Callable, Dict

import requests

# Optional: Add PyPDF2 to requirements.txt for this to work
try:
    import PyPDF2
except ImportError:
    PyPDF2 = None

logger = logging.getLogger("ActionRegistry")


class WebSearchTools:
    """Encapsulates web search functionality using Brave API."""

    def __init__(self):
        self.brave_key = os.getenv("BRAVE_SEARCH_API_KEY")
        if not self.brave_key:
            logger.warning(
                "⚠️ BRAVE_SEARCH_API_KEY not found. Web search will fail.")

    def _format_search_result_item(self, item: Dict) -> str:
        """Helper to format a single search result item."""
        title = item.get('title', 'No Title')
        desc = item.get('description', 'No Description')
        link = item.get('url', 'No Link')
        return f"Title: {title}\nSummary: {desc}\nLink: {link}\n---"

    def _process_search_results(self, data: Dict) -> str:
        """Helper to process raw search API response data into a formatted string."""
        results = []
        if "web" in data and "results" in data["web"]:
            for item in data["web"]["results"]:
                results.append(self._format_search_result_item(item))
        return "\n".join(results) if results else "No results found."

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
            # Limit to top 3 results for cost/speed
            params = {"q": query, "count": 3}

            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()

            data = response.json()

            # Delegate processing to a helper function to reduce nesting
            return self._process_search_results(data)

        except Exception as e:
            logger.error(f"Search failed: {e}")
            return f"Search Error: {str(e)}"


class FileIO:
    """Handles file reading and saving operations."""

    def __init__(self):
        pass # No specific state needed for file operations

    def _read_pdf_file(self, file_path: str) -> str:
        """Helper to read content from a PDF file."""
        if not PyPDF2:
            return "Error: PyPDF2 module not installed."
        with open(file_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            return "\n".join([page.extract_text() for page in reader.pages])

    def _read_text_file(self, file_path: str) -> str:
        """Helper to read content from a text-based file."""
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()

    def read_file(self, file_path: str) -> str:
        """Reads text from .txt, .md, or .pdf files."""
        try:
            if file_path.endswith('.pdf'):
                return self._read_pdf_file(file_path)
            else:
                return self._read_text_file(file_path)
        except Exception as e:
            return f"Read Error: {e}"

    def save_file(self, content: str, file_path: str) -> str:
        """Saves content to a file."""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return f"✅ File saved successfully: {file_path}"
        except Exception as e:
            return f"Save Error: {e}"


class RedisCache:
    """Provides mock Redis-like caching functionalities."""

    def __init__(self):
        # Mock Redis storage for L1 caching
        self._redis_store: Dict[str, str] = {}
        self._redis_hash: Dict[str, Dict[str, str]] = {}

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


class TimeTools:
    """Provides time-related functionalities, including current time and conversion."""

    def __init__(self):
        pass # No specific state needed

    def _get_current_time_fallback(self, timezone: str) -> str:
        """Helper to get current time using datetime/pytz if mcp_time_client is unavailable."""
        try:
            from datetime import datetime
            import pytz
        except ImportError:
            return "Error: pytz module not installed for timezone operations."
        except Exception as e:
            return f"Error during fallback import: {e}"

        try:
            tz = pytz.timezone(timezone)
            now = datetime.now(tz)
            return now.isoformat()
        except Exception as e:
            return f"Error getting time with pytz: {e}"

    def get_current_time(self, timezone: str = "UTC") -> str:
        """Gets the current date, time, and timezone in ISO 8601 format."""
        try:
            from mcp_time_client import get_current_time as mcp_get_time
            return mcp_get_time(timezone)
        except ImportError:
            return self._get_current_time_fallback(timezone)

    def convert_time(self, source_timezone: str, time: str, target_timezone: str) -> str:
        """Converts a time string between two specified IANA timezones."""
        try:
            from mcp_time_client import convert_time as mcp_convert_time
            return mcp_convert_time(source_timezone, time, target_timezone)
        except ImportError:
            return f"Error: MCP Time client not available for conversion"


class GitTools:
    """Provides git operations like commit and status."""

    def __init__(self):
        pass # No specific state needed

    def commit(self, file_path: str, message: str) -> str:
        """Commits a file to git."""
        try:
            from mcp0_git_add_or_commit import mcp0_git_add_or_commit
            mcp0_git_add_or_commit(
                directory=".", action="add", files=[file_path])
            result = mcp0_git_add_or_commit(directory=".", action="commit", files=[
                                            file_path], message=message)
            return f"✅ Committed: {message}"
        except Exception as e:
            return f"Commit Error: {e}"

    def status(self) -> str:
        """Gets git status."""
        try:
            from mcp0_git_status import mcp0_git_status
            result = mcp0_git_status(directory=".")
            return result
        except Exception as e:
            return f"Status Error: {e}"


class FigmaTools:
    """Stubs for Figma MCP tools (L2 Design)."""

    def __init__(self):
        pass

    def get_variable_defs(self, node_id: str, file_key: str = None) -> str:
        """Gets Figma variable definitions."""
        return "Figma MCP not implemented in Phase 1"

    def get_design_context(self, node_id: str, file_key: str = None) -> str:
        """Gets Figma design context."""
        return "Figma MCP not implemented in Phase 1"

    def get_screenshot(self, node_id: str, file_key: str = None) -> str:
        """Gets Figma screenshot."""
        return "Figma MCP not implemented in Phase 1"


class PineconeTools:
    """Stub for Pinecone MCP tools (L3 RAG)."""

    def __init__(self):
        pass

    def search_records(self, query: str, index: str, top_k: int, namespace: str) -> str:
        """Searches Pinecone records."""
        return "Pinecone MCP not implemented in Phase 1"


class MemoryTools:
    """Stubs for MEMemory MCP tools (L5 MEMemory)."""

    def __init__(self):
        pass

    def add_observations(self, observations: list) -> str:
        """Adds observations to MEMemory."""
        return "MEMemory MCP not implemented in Phase 1"

    def create_entities(self, entities: list) -> str:
        """Creates entities in MEMemory."""
        return "MEMemory MCP not implemented in Phase 1"

    def open_nodes(self, names: list) -> str:
        """Opens nodes in MEMemory."""
        return "MEMemory MCP not implemented in Phase 1"


class ActionRegistry:
    """
    The 'Hands' of the Agent.
    Contains the whitelist of allowed actions (Key #3).
    """

    def __init__(self):
        # Initialize sub-components
        self.web_search_tools = WebSearchTools()
        self.file_io_tools = FileIO()
        self.redis_cache_tools = RedisCache()
        self.time_tools = TimeTools()
        self.git_tools = GitTools()
        self.figma_tools = FigmaTools()
        self.pinecone_tools = PineconeTools()
        self.memory_tools = MemoryTools()

    # --- OUTREACH ENGINE TOOLS ---
    def mock_send_email(self, recipient: str, subject: str, body: str) -> str:
        """Simulates sending an email (Safety first)."""
        # In Phase 4 we will connect real SMTP
        logger.info(f"📧 EMAIL SENT to {recipient} | Subj: {subject}")
        return f"Email simulated sent to {recipient}"

    def get_tool_map(self) -> Dict[str, Callable]:
        """Returns the master tool map for the LLM."""
        return {
            # --- LAYER 1: FILESYSTEM & I/O ---
            "read_file": self.file_io_tools.read_file,
            "save_file": self.file_io_tools.save_file,
            "send_email": self.mock_send_email,

            # --- LAYER 2: DESIGN & CONTEXT ---
            "get_variable_defs": self.figma_tools.get_variable_defs,
            "get_design_context": self.figma_tools.get_design_context,
            "get_screenshot": self.figma_tools.get_screenshot,

            # --- LAYER 3: RAG & WISDOM ---
            "search_records": self.pinecone_tools.search_records,
            "search_web": self.web_search_tools.search_web,

            # --- LAYER 4: STATE & TEMPORAL ---
            "string_set": self.redis_cache_tools.string_set,
            "string_get": self.redis_cache_tools.string_get,
            "hash_set": self.redis_cache_tools.hash_set,
            "hash_get": self.redis_cache_tools.hash_get,
            "get_current_time": self.time_tools.get_current_time,
            "convert_time": self.time_tools.convert_time,

            # --- LAYER 5: MEMORY & AUDIT ---
            "add_observations": self.memory_tools.add_observations,
            "create_entities": self.memory_tools.create_entities,
            "open_nodes": self.memory_tools.open_nodes,

            # --- GIT OPERATIONS ---
            "commit": self.git_tools.commit,
            "status": self.git_tools.status,
        }