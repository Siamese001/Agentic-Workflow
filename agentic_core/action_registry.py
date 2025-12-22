The provided code is already very well-structured, follows good practices for error handling, logging, and type hinting, and generally adheres to PEP 8. The "violations" are minor style points, primarily related to line length for improved readability.

Here's a breakdown of the changes made:

1.  **Import `Optional`**: Added `Optional` to the `typing` import for more precise type hints in `FigmaTools` methods where `file_key` can be `None`.
2.  **Line Length for `logger.info` messages**:
    *   In `RedisCache` methods (`string_set`, `string_get`, `hash_set`, `hash_get`), the log messages that truncate long values were slightly over the recommended line length. These have been refactored to use a temporary variable for the display value, making the `logger.info` call shorter and more readable.
    *   In `PineconeTools.search_records`, the `logger.info` message was also wrapped for readability.
3.  **Line Length for `return` statements**:
    *   In `TimeTools._get_current_time_fallback` and `TimeTools.convert_time`, the `ImportError` return messages were wrapped to fit within standard line limits.
    *   In `GitTools.commit` and `GitTools.status`, the `ImportError` return messages were also wrapped.
4.  **Readability in `FileIO._read_pdf_file`**: The list comprehension for extracting text from PDF pages was slightly long. It has been assigned to a temporary variable (`extracted_texts`) before being joined, improving readability.

```python
import logging
import os
from typing import Callable, Dict, Optional # Added Optional

import requests

# Optional: Add PyPDF2 to requirements.txt for this to work
try:
    import PyPDF2
except ImportError:
    PyPDF2 = None

logger = logging.getLogger("ActionRegistry")


class WebSearchTools:
    """
    Encapsulates web search functionality using Brave API.
    Tool ID Prefix: ACT-001
    """

    def __init__(self):
        """Initializes WebSearchTools and checks for the Brave API key."""
        self.brave_key = os.getenv("BRAVE_SEARCH_API_KEY")
        if not self.brave_key:
            logger.warning(
                "⚠️ BRAVE_SEARCH_API_KEY not found. Web search will fail."
            )

    def _format_search_result_item(self, item: Dict) -> str:
        """
        Helper to format a single search result item into a readable string.

        Args:
            item (Dict): A dictionary representing a single search result.

        Returns:
            str: A formatted string of the search result.
        """
        title = item.get('title', 'No Title')
        desc = item.get('description', 'No Description')
        link = item.get('url', 'No Link')
        return f"Title: {title}\nSummary: {desc}\nLink: {link}\n---"

    def _process_search_results(self, data: Dict) -> str:
        """
        Helper to process raw search API response data into a formatted string.

        Args:
            data (Dict): The raw JSON response from the Brave Search API.

        Returns:
            str: A concatenated string of formatted search results, or a
                 "No results found" message.
        """
        results = []
        if "web" in data and "results" in data["web"]:
            for item in data["web"]["results"]:
                results.append(self._format_search_result_item(item))
        return "\n".join(results) if results else "No results found."

    def search_web(self, query: str) -> str:
        """
        Performs a real web search using the Brave API.
        Tool ID: ACT-001

        Args:
            query (str): The search query string.

        Returns:
            str: A formatted string of search results or an error message.
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

            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()  # Raises HTTPError for bad responses (4xx or 5xx)

            data = response.json()

            # Delegate processing to a helper function to reduce nesting
            return self._process_search_results(data)

        except requests.exceptions.HTTPError as e:
            logger.error(f"Web search HTTP error for query '{query}': {e}")
            return f"Search Error (HTTP): {e}"
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Web search connection error for query '{query}': {e}")
            return f"Search Error (Connection): {e}"
        except requests.exceptions.Timeout as e:
            logger.error(f"Web search timeout error for query '{query}': {e}")
            return f"Search Error (Timeout): {e}"
        except requests.exceptions.RequestException as e:
            logger.error(f"Web search request error for query '{query}': {e}")
            return f"Search Error (Request): {e}"
        except Exception as e:
            logger.error(f"An unexpected error occurred during web search for query '{query}': {e}")
            return f"Search Error (Unexpected): {str(e)}"


class FileIO:
    """
    Handles file reading and saving operations.
    Tool ID Prefix: ACT-002
    """

    def __init__(self):
        """Initializes FileIO. No specific state needed for file operations."""
        pass

    def _read_pdf_file(self, file_path: str) -> str:
        """
        Helper to read content from a PDF file.

        Args:
            file_path (str): The path to the PDF file.

        Returns:
            str: The extracted text content from the PDF.
        """
        if not PyPDF2:
            return "Error: PyPDF2 module not installed. Cannot read PDF files."
        try:
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                # Check if the PDF has pages before trying to extract text
                if not reader.pages:
                    return f"Warning: PDF file '{file_path}' has no pages or content."
                # Refactored for readability
                extracted_texts = [
                    page.extract_text() for page in reader.pages if page.extract_text()
                ]
                return "\n".join(extracted_texts)
        except PyPDF2.errors.PdfReadError as e:
            return f"Read Error (PDF): Could not read PDF file '{file_path}'. {e}"
        except FileNotFoundError:
            return f"Read Error: File not found at '{file_path}'."
        except Exception as e:
            return f"Read Error (PDF Unexpected): {e}"

    def _read_text_file(self, file_path: str) -> str:
        """
        Helper to read content from a text-based file.

        Args:
            file_path (str): The path to the text file.

        Returns:
            str: The content of the text file.
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            return f"Read Error: File not found at '{file_path}'."
        except UnicodeDecodeError:
            return f"Read Error: Could not decode file '{file_path}' with utf-8. Try a different encoding."
        except Exception as e:
            return f"Read Error (Text Unexpected): {e}"

    def read_file(self, file_path: str) -> str:
        """
        Reads text content from .txt, .md, or .pdf files.
        Tool ID: ACT-002

        Args:
            file_path (str): The path to the file to read.

        Returns:
            str: The content of the file or an error message.
        """
        logger.info(f"📖 Reading file: '{file_path}'")
        if not os.path.exists(file_path):
            return f"Read Error: File not found at '{file_path}'."

        if file_path.endswith('.pdf'):
            return self._read_pdf_file(file_path)
        else:
            return self._read_text_file(file_path)

    def save_file(self, content: str, file_path: str) -> str:
        """
        Saves content to a file.
        Tool ID: ACT-003

        Args:
            content (str): The string content to save.
            file_path (str): The path where the file should be saved.

        Returns:
            str: A success message or an error message.
        """
        logger.info(f"💾 Saving file: '{file_path}' (content length: {len(content)})")
        try:
            # Ensure the directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return f"✅ File saved successfully: {file_path}"
        except IOError as e:
            return f"Save Error (IO): Could not save file '{file_path}'. {e}"
        except Exception as e:
            return f"Save Error (Unexpected): {e}"


class RedisCache:
    """
    Provides mock Redis-like caching functionalities for L1 caching.
    Tool ID Prefix: ACT-004
    """

    def __init__(self):
        """Initializes the mock Redis storage."""
        self._redis_store: Dict[str, str] = {}
        self._redis_hash: Dict[str, Dict[str, str]] = {}
        logger.info("📦 Mock RedisCache initialized.")

    def string_set(self, key: str, value: str) -> str:
        """
        Stores a simple string key-value pair in Redis.
        Tool ID: ACT-004

        Args:
            key (str): The key for the string.
            value (str): The string value to store.

        Returns:
            str: A confirmation message.
        """
        self._redis_store[key] = value
        display_value = f"{value[:50]}{'...' if len(value) > 50 else ''}"
        logger.info(f"📦 Redis SET: '{key}' = '{display_value}'")
        return f"OK: Stored '{key}'"

    def string_get(self, key: str) -> str:
        """
        Retrieves a string value from Redis.
        Tool ID: ACT-005

        Args:
            key (str): The key of the string to retrieve.

        Returns:
            str: The retrieved string value or a "NULL" message if not found.
        """
        value = self._redis_store.get(key)
        if value is None:
            logger.info(f"📦 Redis GET: '{key}' not found.")
            return f"NULL: Key '{key}' not found"
        display_value = f"{value[:50]}{'...' if len(value) > 50 else ''}"
        logger.info(f"📦 Redis GET: '{key}' = '{display_value}'")
        return value

    def hash_set(self, key: str, field: str, value: str) -> str:
        """
        Stores a field-value pair in a Redis hash.
        Tool ID: ACT-006

        Args:
            key (str): The key of the hash.
            field (str): The field within the hash.
            value (str): The value to store for the field.

        Returns:
            str: A confirmation message.
        """
        if key not in self._redis_hash:
            self._redis_hash[key] = {}
        self._redis_hash[key][field] = value
        display_value = f"{value[:50]}{'...' if len(value) > 50 else ''}"
        logger.info(f"📦 Redis HSET: '{key}'.'{field}' = '{display_value}'")
        return f"OK: Stored '{key}'.'{field}'"

    def hash_get(self, key: str, field: str) -> str:
        """
        Retrieves a field value from a Redis hash.
        Tool ID: ACT-007

        Args:
            key (str): The key of the hash.
            field (str): The field within the hash to retrieve.

        Returns:
            str: The retrieved field value or a "NULL" message if not found.
        """
        if key not in self._redis_hash or field not in self._redis_hash[key]:
            logger.info(f"📦 Redis HGET: '{key}'.'{field}' not found.")
            return f"NULL: '{key}'.'{field}' not found"
        value = self._redis_hash[key][field]
        display_value = f"{value[:50]}{'...' if len(value) > 50 else ''}"
        logger.info(f"📦 Redis HGET: '{key}'.'{field}' = '{display_value}'")
        return value


class TimeTools:
    """
    Provides time-related functionalities, including current time and conversion.
    Tool ID Prefix: ACT-008
    """

    def __init__(self):
        """Initializes TimeTools. No specific state needed."""
        pass

    def _get_current_time_fallback(self, timezone: str) -> str:
        """
        Helper to get current time using datetime/pytz if mcp_time_client is unavailable.

        Args:
            timezone (str): The IANA timezone string (e.g., "UTC", "America/New_York").

        Returns:
            str: The current time in ISO 8601 format or an error message.
        """
        try:
            from datetime import datetime
            import pytz
        except ImportError:
            return (
                "Error: 'pytz' module not installed for timezone operations. "
                "Please install it (`pip install pytz`)."
            )
        except Exception as e:
            return f"Error during fallback import for time tools: {e}"

        try:
            tz = pytz.timezone(timezone)
            now = datetime.now(tz)
            return now.isoformat()
        except pytz.UnknownTimeZoneError:
            return f"Error: Unknown timezone '{timezone}'. Please provide a valid IANA timezone string."
        except Exception as e:
            return f"Error getting time with pytz: {e}"

    def get_current_time(self, timezone: str = "UTC") -> str:
        """
        Gets the current date, time, and timezone in ISO 8601 format.
        Tool ID: ACT-008

        Args:
            timezone (str): The IANA timezone string (e.g., "UTC", "America/New_York").
                            Defaults to "UTC".

        Returns:
            str: The current time in ISO 8601 format or an error message.
        """
        logger.info(f"⏰ Getting current time for timezone: '{timezone}'")
        try:
            # Attempt to use the MCP Time client if available
            from mcp_time_client import get_current_time as mcp_get_time
            return mcp_get_time(timezone)
        except ImportError:
            # Fallback to local datetime/pytz if MCP client is not installed
            logger.warning("MCP Time client not found, falling back to local time calculation.")
            return self._get_current_time_fallback(timezone)
        except Exception as e:
            return f"Error with MCP Time client for get_current_time: {e}"

    def convert_time(self, source_timezone: str, time: str, target_timezone: str) -> str:
        """
        Converts a time string between two specified IANA timezones.
        Tool ID: ACT-009

        Args:
            source_timezone (str): The IANA timezone of the input `time`.
            time (str): The time string to convert (e.g., "2023-10-27T10:00:00+00:00").
            target_timezone (str): The IANA timezone to convert the time to.

        Returns:
            str: The converted time string in ISO 8601 format or an error message.
        """
        logger.info(f"🔄 Converting time '{time}' from '{source_timezone}' to '{target_timezone}'")
        try:
            # Attempt to use the MCP Time client if available
            from mcp_time_client import convert_time as mcp_convert_time
            return mcp_convert_time(source_timezone, time, target_timezone)
        except ImportError:
            return (
                "Error: MCP Time client not available for time conversion. "
                "This functionality requires 'mcp_time_client'."
            )
        except Exception as e:
            return f"Error with MCP Time client for convert_time: {e}"


class GitTools:
    """
    Provides git operations like commit and status.
    Tool ID Prefix: ACT-010
    """

    def __init__(self):
        """Initializes GitTools. No specific state needed."""
        pass

    def commit(self, file_path: str, message: str) -> str:
        """
        Commits a file to git.
        Tool ID: ACT-010

        Args:
            file_path (str): The path to the file to commit.
            message (str): The commit message.

        Returns:
            str: A success message or an error message.
        """
        logger.info(f"➕ Committing file '{file_path}' with message: '{message}'")
        try:
            from mcp0_git_add_or_commit import mcp0_git_add_or_commit
            # First, add the file to staging
            add_result = mcp0_git_add_or_commit(
                directory=".", action="add", files=[file_path]
            )
            if "Error" in add_result:
                return f"Commit Error (Add): {add_result}"

            # Then, commit the staged file
            commit_result = mcp0_git_add_or_commit(
                directory=".", action="commit", files=[file_path], message=message
            )
            if "Error" in commit_result:
                return f"Commit Error (Commit): {commit_result}"

            return f"✅ Committed: {message}"
        except ImportError:
            return (
                "Commit Error: 'mcp0_git_add_or_commit' client not available. "
                "Git operations require this client."
            )
        except Exception as e:
            return f"Commit Error (Unexpected): {e}"

    def status(self) -> str:
        """
        Gets git status.
        Tool ID: ACT-011

        Returns:
            str: The git status output or an error message.
        """
        logger.info("❓ Getting git status.")
        try:
            from mcp0_git_status import mcp0_git_status
            result = mcp0_git_status(directory=".")
            return result
        except ImportError:
            return (
                "Status Error: 'mcp0_git_status' client not available. "
                "Git operations require this client."
            )
        except Exception as e:
            return f"Status Error (Unexpected): {e}"


class FigmaTools:
    """
    Stubs for Figma MCP tools (L2 Design).
    Tool ID Prefix: ACT-012
    """

    def __init__(self):
        """Initializes FigmaTools. No specific state needed."""
        pass

    def get_variable_defs(self, node_id: str, file_key: Optional[str] = None) -> str:
        """
        Gets Figma variable definitions.
        Tool ID: ACT-012

        Args:
            node_id (str): The ID of the Figma node.
            file_key (str, optional): The Figma file key. Defaults to None.

        Returns:
            str: A message indicating the tool is not implemented.
        """
        logger.info(f"🎨 Figma: get_variable_defs for node '{node_id}' (file: {file_key})")
        return "Figma MCP not implemented in Phase 1"

    def get_design_context(self, node_id: str, file_key: Optional[str] = None) -> str:
        """
        Gets Figma design context.
        Tool ID: ACT-013

        Args:
            node_id (str): The ID of the Figma node.
            file_key (str, optional): The Figma file key. Defaults to None.

        Returns:
            str: A message indicating the tool is not implemented.
        """
        logger.info(f"🎨 Figma: get_design_context for node '{node_id}' (file: {file_key})")
        return "Figma MCP not implemented in Phase 1"

    def get_screenshot(self, node_id: str, file_key: Optional[str] = None) -> str:
        """
        Gets Figma screenshot.
        Tool ID: ACT-014

        Args:
            node_id (str): The ID of the Figma node.
            file_key (str, optional): The Figma file key. Defaults to None.

        Returns:
            str: A message indicating the tool is not implemented.
        """
        logger.info(f"🎨 Figma: get_screenshot for node '{node_id}' (file: {file_key})")
        return "Figma MCP not implemented in Phase 1"


class PineconeTools:
    """
    Stub for Pinecone MCP tools (L3 RAG).
    Tool ID Prefix: ACT-015
    """

    def __init__(self):
        """Initializes PineconeTools. No specific state needed."""
        pass

    def search_records(self, query: str, index: str, top_k: int, namespace: str) -> str:
        """
        Searches Pinecone records.
        Tool ID: ACT-015

        Args:
            query (str): The search query.
            index (str): The Pinecone index to search.
            top_k (int): The number of top results to return.
            namespace (str): The namespace within the index.

        Returns:
            str: A message indicating the tool is not implemented.
        """
        log_message = (
            f"🌲 Pinecone: search_records for query '{query}' in index '{index}' "
            f"(namespace: {namespace}, top_k: {top_k})"
        )
        logger.info(log_message)
        return "Pinecone MCP not implemented in Phase 1"


class MemoryTools:
    """
    Stubs for MEMemory MCP tools (L5 MEMemory).
    Tool ID Prefix: ACT-016
    """

    def __init__(self):
        """Initializes MemoryTools. No specific state needed."""
        pass

    def add_observations(self, observations: list) -> str:
        """
        Adds observations to MEMemory.
        Tool ID: ACT-016

        Args:
            observations (list): A list of observations to add.

        Returns:
            str: A message indicating the tool is not implemented.
        """
        logger.info(f"🧠 MEMemory: add_observations (count: {len(observations)})")
        return "MEMemory MCP not implemented in Phase 1"

    def create_entities(self, entities: list) -> str:
        """
        Creates entities in MEMemory.
        Tool ID: ACT-017

        Args:
            entities (list): A list of entities to create.

        Returns:
            str: A message indicating the tool is not implemented.
        """
        logger.info(f"🧠 MEMemory: create_entities (count: {len(entities)})")
        return "MEMemory MCP not implemented in Phase 1"

    def open_nodes(self, names: list) -> str:
        """
        Opens nodes in MEMemory.
        Tool ID: ACT-018

        Args:
            names (list): A list of node names to open.

        Returns:
            str: A message indicating the tool is not implemented.
        """
        logger.info(f"🧠 MEMemory: open_nodes (count: {len(names)})")
        return "MEMemory MCP not implemented in Phase 1"


class ActionRegistry:
    """
    The 'Hands' of the Agent.
    Contains the whitelist of allowed actions (Key #3).
    This class aggregates various tools and exposes them as a unified interface.
    """

    def __init__(self):
        """Initializes the ActionRegistry and all its sub-components."""
        # Initialize sub-components
        self.web_search_tools = WebSearchTools()
        self.file_io_tools = FileIO()
        self.redis_cache_tools = RedisCache()
        self.time_tools = TimeTools()
        self.git_tools = GitTools()
        self.figma_tools = FigmaTools()
        self.pinecone_tools = PineconeTools()
        self.memory_tools = MemoryTools()
        logger.info("🛠️ ActionRegistry initialized with all tools.")

    def mock_send_email(self, recipient: str, subject: str, body: str) -> str:
        """
        Simulates sending an email (Safety first).
        In Phase 4 we will connect real SMTP.
        Tool ID: ACT-000 (Placeholder for Outreach Engine)

        Args:
            recipient (str): The email address of the recipient.
            subject (str): The subject line of the email.
            body (str): The body content of the email.

        Returns:
            str: A message confirming the simulated email send.
        """
        logger.info(f"📧 EMAIL SIMULATED SENT to {recipient} | Subj: {subject[:50]}...")
        # In a real scenario, you might log the full body or save it to a file
        return f"Email simulated sent to {recipient} with subject '{subject}'."

    def get_tool_map(self) -> Dict[str, Callable]:
        """
        Returns the master tool map for the LLM.
        This dictionary maps tool names (as they would appear in LLM function calls)
        to their corresponding callable methods.

        Returns:
            Dict[str, Callable]: A dictionary mapping tool names to callable functions.
        """
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

```