import time
import logging
import sys
from llm_client import LLMClient
from canon_validator import CanonValidator
from action_registry import ActionRegistry
from cognitive_node import CognitiveNode # <--- NEW IMPORT

# Setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("Orchestrator")

def run_agentic_loop(user_goal: str):
    print(f"\n🚀 SUBATOMIC AGENT STARTING: {user_goal}")
    print("="*60)
    
    # 1. INITIALIZE COMPONENTS
    validator = CanonValidator()
    llm = LLMClient()
    actions = ActionRegistry()
    cognitive = CognitiveNode() # <--- NEW COMPONENT
    
    # 2. DEFINE TOOLBOX (The fully unified and accurate toolset)
    toolbox_desc = """
    AVAILABLE TOOLS (You MUST use these for your tasks):

    [FILESYSTEM MCP - L0 Secure I/O]
    - read_text_file(path: str) -> string : Reads complete contents of a file as text (e.g., resumes, source code).
    - write_file(path: str, content: str) -> string : Creates a new file or overwrites existing content (exercise caution).
    - edit_file(path: str, edits: array) -> string : Makes selective edits using advanced pattern matching and formatting (Ideal for Canon Validator repair).
    - list_directory(path: str) -> string : Lists contents of a directory (used for project introspection).

    [MEMORY MCP - L3 Knowledge Graph/User Profile]
    - create_entities(entities: array) -> string : Creates new nodes (people, organizations, concepts) in the graph.
    - add_observations(observations: array) -> string : Adds specific facts (strings) to existing entities.
    - create_relations(relations: array) -> string : Links two entities with a directed relation (e.g., 'John_Smith', 'works_at', 'Anthropic').
    - search_nodes(query: str) -> string : Searches across entity names, types, and observations for relevant context.

    [PINECONE MCP - L2 RAG/Wisdom (The Canonical Memory)]
    - search_records(query: str, index: str, top_k: integer, namespace: str) -> string : Searches the Pinecone index for records similar to the query text (L2 Wisdom). Use for retrieving code patterns, successful resume templates, or outreach knowledge.
    - upsert_records(records: string) -> string : Inserts or updates a JSON list of records into the index (How you save new knowledge/validated code/successful templates).
    - describe_index_stats() -> string : Provides statistics on index content (useful for planning).

    [GITKRAKEN MCP - Code Operations, Issues, and PRs (Source of Truth)]
    - git_add_or_commit(files: string, message: string, action: string) -> string : Adds file contents to the index OR records changes to the repository.
    - git_checkout(branch_or_file: string) : Switches branches or restores working tree files.
    - git_status() -> string : Shows the working tree status.
    - pull_request_create(repo: str, title: str, body: str, head: str, base: str) -> string : Creates a new pull request.
    - issues_get_detail(id: string) -> string : Retrieves detailed information about a specific issue by its unique ID.
    - repository_get_file_content(path: string) -> string : Gets file content from the repository (replaces GitHub's read_file).

    [FIGMA MCP - L0 Design Context & Code Generation]
    - get_design_context(node_id: string) -> string : Gets structural design data for a selected Figma node/frame.
    - get_variable_defs(node_id: string) -> string : Retrieves the design tokens (variables, styles) used in the selection.
    - get_code_connect_map(node_id: string) -> string : Retrieves the codebase path for a linked component.

    [PLAYWRIGHT MCP - L1 Browser Automation]
    - browser_navigate(url: string) : Navigates the browser to a URL.
    - browser_snapshot() -> string : Captures the accessibility snapshot of the current page (MUST be called before interaction).
    - browser_type(element: string, ref: string, text: string) : Types text into an editable element.
    - browser_click(element: string, ref: string) : Performs a click on a web page element.

    [FETCH MCP - L1 Live External Content]
    - fetch(url: str, max_length: integer) -> string : Fetches a URL and extracts its contents as clean Markdown (e.g., job descriptions, documentation).

    [REDIS MCP - L1 Cache & Session State]
    - string_set(key: str, value: str) : Stores simple session state or caching keys.
    - string_get(key: str) -> str : Retrieves simple session state or caching keys.
    - hash_set(key: str, field: str, value: str) : Stores field-value pairs (e.g., user profiles, complex cache objects).
    - hash_get(key: str, field: str) -> str : Retrieves a field from a hash key.
    
    [TIME MCP - L4 Temporal Awareness]
    - get_current_time(timezone: str) -> string: Gets the current date, time, and timezone in ISO 8601 format. Accepts IANA timezone name (e.g., 'America/New_York').
    - convert_time(source_timezone: str, time: str, target_timezone: str) -> string: Converts a time string (HH:MM) between two specified IANA timezones.
    
    [ACTION TOOLS]
    - send_email(recipient: str, subject: str, body: str) -> str : Simulates sending an email (Mock).
    """
    
    # 3. THINK SEQUENTIALLY (Generate Draft using the Cognitive Node)
    # The Cognitive Node manages the entire thought process
    try:
        raw_code = cognitive.think(user_goal, toolbox_desc) 
    except TimeoutError as e:
        logger.error(f"❌ Sequential thinking timed out: {e}")
        return
    except RuntimeError as e:
        logger.error(f"❌ Sequential thinking failed: {e}")
        return
    except Exception as e:
        logger.error(f"❌ Unexpected error in Cognitive Node: {e}")
        return 
    
    if not raw_code:
        logger.error("❌ Generation failed in Cognitive Node.")
        return

    print(f"\n📄 DRAFT CODE RECEIVED:\n{'-'*20}\n{raw_code}\n{'-'*20}")

    # 4. AUDIT & REPAIR (The "Golden Loop")
    result = validator.validate(raw_code, auto_repair=True)
    
    final_code = raw_code
    status = result.get("status")
    
    if status == "repaired":
        print(f"\n🔧 AUTO-REPAIR APPLIED!")
        print(f"📝 Reason: {result.get('reasoning')}")
        final_code = result.get("repaired_code")
        print(f"✨ NEW CODE:\n{'-'*20}\n{final_code}\n{'-'*20}")
    elif status == "rejected":
        logger.error("❌ Code rejected.")
        return

    # 5. EXECUTE (Action Plane)
    logger.info("⚡ Executing Final Code...")
    try:
        # INJECT ALL TOOLS (Web, File I/O, Mock Email)
        # Tools must be in global scope to be accessible inside function definitions
        exec_globals = actions.get_tool_map()
        exec_globals['__name__'] = '__main__'
        local_scope = {}
        
        # Execute the code - this defines all functions
        exec(final_code, exec_globals, local_scope)
        
        # Merge local_scope back into exec_globals so helper functions are accessible
        exec_globals.update(local_scope)
        
        # Auto-run entry point (find the last defined function that's not a tool)
        tool_names = set(actions.get_tool_map().keys())
        keys = [k for k in local_scope.keys() if k not in tool_names and "__" not in k and callable(local_scope[k])]
        if keys:
            func_name = keys[-1]
            print(f"▶️ Running function: {func_name}...")
            
            # Simple Injection Logic for Logger
            import inspect
            sig = inspect.signature(local_scope[func_name])
            kwargs = {}
            if "logger" in sig.parameters:
                class MockLogger:
                    def __call__(self, msg): print(f"[LOG] {msg}")
                    def info(self, msg): print(f"[LOG] {msg}")
                kwargs["logger"] = MockLogger()
                
            res = local_scope[func_name](**kwargs)
            print(f"✅ RESULT: {res}")
            
    except Exception as e:
        logger.error(f"Runtime Error: {e}")

if __name__ == "__main__":
    # The final strategic task for the L3 Agent
    user_goal = """
    I have integrated 9 core MCP Servers (MEMemory, Pinecone, Redis, GitKraken, Figma, Filesystem, Fetch, Playwright, Send Email) into my L3 Agent architecture.

    Perform an **Architectural Strategy Review** of this unified platform to maximize the utility across the three functional engines: **Canon Validator**, **Resume Engine**, and **Outreach Engine**.

    ### INSTRUCTIONS (Sequential Thinking):

    1.  **Analyze the Toolset:** Review the final, comprehensive list of MCP servers and their core capabilities.
    2.  **Define Core Strategy per Engine:** For each of the three engines, synthesize a single, defining strategic goal that is only possible now that all MCPs are integrated.
    3.  **Propose Synergistic Use Cases (Required Table):** For each engine, create a table listing three **novel, multi-step use cases** that require the combined use of **at least three distinct MCP Servers**.

    ### Output Format Requirements:

    1.  **Strategic Goal Summary:** A short, bolded sentence defining the new, maximum capability of each engine.
    2.  **Use Case Table:** A markdown table summarizing the proposals.

    ### The Unified MCP Toolset for Reference:
    | MCP Server | Category | Core Capability |
    | :--- | :--- | :--- |
    | **MEMemory** | L3 Memory | Knowledge Graph (Relationships, User Profile) |
    | **Pinecone** | L2 RAG/Wisdom | Vector Search (Semantic Templates, Code Patterns) |
    | **Redis** | L1 Cache/State | High-Speed Cache (Prompt Responses, Session State) |
    | **GitKraken** | L0 Code Ops | Git & Issue Management (Commit, Checkout, PR, Issues) |
    | **Figma** | L0 Design Context | Design System Context (Variables, Components, Layout) |
    | **Filesystem** | L0 Secure I/O | Secure File Read/Write/Edit (Resumes, Reports) |
    | **Fetch** | L1 Web Content | URL Fetching and Markdown Conversion |
    | **Playwright** | L1 Automation | Browser Automation (Snapshot, Type, Click) |
    | **Send Email** | Action Tool | External Communication (Mock) |
    """
    
    # Run the agent with the strategic goal
    run_agentic_loop(user_goal)
