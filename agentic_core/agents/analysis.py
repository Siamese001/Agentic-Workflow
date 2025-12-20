from agentic_core.agents.base import SubAtomicAgent
import ast
import logging

# Configure logging for the module
logger = logging.getLogger(__name__)
# Set default logging level to INFO. This can be overridden by the main application.
logger.setLevel(logging.INFO)
# If no handlers are configured, add a default one to print to console
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(levelname)s: %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)


"""
Analysis agents for code quality and semantic consistency.

Contains:
- SemanticMapper: Analyzes 'God Files' and proposes logical splits based on call graphs
- TruthKeeper: Ensures docstrings match code logic using Gemini
"""


class SemanticMapper(SubAtomicAgent):
    """
    ROLE: The Architect. Analyzes 'God Files' and proposes logical splits based on call graphs.
    """

    def can_run(self) -> bool:
        """
        Determines if the SemanticMapper agent can run.
        Requires the 'AST_VALID' signal to be present in the context.

        Returns:
            bool: True if the agent can run, False otherwise.
        """
        return "AST_VALID" in self.ctx.signals

    async def execute(self):
        """
        Executes the SemanticMapper agent's logic.
        Analyzes Python files for refactoring opportunities based on AST parsing.

        NOTE: The current implementation primarily checks for valid AST parsing
        and contains placeholder logic for actual dependency graph analysis
        and proposing logical splits.
        """
        logger.info(f"[>>>] {self.name} ACTIVATED: Calculating Dependency Graphs...")
        # Removed asyncio.sleep(0) as it's generally not necessary for yielding control here.

        # Analyze large files for refactoring opportunities
        # NOTE: The current implementation only processes the first 3 files.
        # A more robust approach might involve filtering by file size, complexity,
        # or a configurable limit from self.ctx.
        analysis_performed = False
        files_to_analyze = self.ctx.python_files[:3] # Consider making this configurable or iterating all
        if not files_to_analyze:
            logger.info("   ℹ No Python files found in context to analyze.")
            return

        for file_path in files_to_analyze:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    # Just parsing the AST. The core logic for proposing logical splits
                    # based on call graphs or other metrics is a placeholder.
                    ast.parse(f.read())

                logger.info(f"   🧠 Analyzing Logic Flow: {file_path}...")
                # Placeholder for actual dependency graph analysis and cluster identification
                logger.info(f"      ℹ No significant clusters found in {file_path} (analysis logic not yet implemented)")
                analysis_performed = True
            except SyntaxError as se:
                logger.error(f"      ❌ Failed to parse {file_path} due to syntax error: {se}")
            except Exception as e:
                logger.error(f"      ❌ Failed to analyze {file_path}: {e}")

        if not analysis_performed:
            logger.info("\n   ℹ No Python files were successfully processed for refactoring analysis.")
        else:
            logger.info("\n   ℹ No refactoring opportunities identified (based on current placeholder logic).")


class TruthKeeper(SubAtomicAgent):
    """
    ROLE: Semantic Consistency. Ensures docstrings match code logic.
    Uses Gemini to detect and fix mismatches.
    """

    async def execute(self):
        """
        Executes the TruthKeeper agent's logic.
        Iterates through Python files, skipping test files, to check docstring consistency.
        """
        logger.info(f"[>>>] {self.name} ACTIVATED: Checking Docstring Consistency...")
        # Removed asyncio.sleep(0) as it's generally not necessary for yielding control here.

        for file_path in self.ctx.python_files:
            if 'test' in file_path.lower():
                logger.debug(f"   ⏩ Skipping test file: {file_path}")
                continue

            await self._check_docstring_consistency(file_path)

    async def _check_docstring_consistency(self, file_path: str):
        """
        Checks if docstrings match the actual code logic for a given file.
        This method orchestrates file reading, AST parsing, and node processing.

        Args:
            file_path: The path to the Python file to check.
        """
        try:
            content = await self._read_file_content(file_path)
            tree = ast.parse(content)
            await self._iterate_and_process_nodes(file_path, tree, content)
        except SyntaxError as se:
            logger.error(f"   ❌ Failed to parse {file_path} due to syntax error: {se}")
        except Exception as e:
            logger.error(f"   ❌ Failed to check {file_path}: {e}")

    async def _read_file_content(self, file_path: str) -> str:
        """
        Reads the content of a file.

        Note: `open()` is a blocking operation. For true asynchronous file I/O
        in an `async` context, `aiofiles` or `loop.run_in_executor` should be used.
        This implementation will block the event loop during file reading.

        Args:
            file_path: The path to the file.

        Returns:
            str: The content of the file as a string.
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()

    async def _iterate_and_process_nodes(self, file_path: str, tree: ast.AST, content: str):
        """
        Iterates through AST nodes and processes them for docstring consistency.

        Args:
            file_path: The path to the file being processed.
            tree: The AST root node of the file.
            content: The full content of the file.
        """
        for node in ast.walk(tree):
            await self._process_node_for_docstring_consistency(file_path, node, content)

    async def _process_node_for_docstring_consistency(self, file_path: str, node: ast.AST, content: str):
        """
        Helper to process a single AST node for docstring consistency.

        Args:
            file_path: The path to the file being processed.
            node: The current AST node to check (e.g., FunctionDef, AsyncFunctionDef, ClassDef).
            content: The full content of the file.
        """
        # Only process functions, async functions, and classes
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            return

        docstring = ast.get_docstring(node)

        if not docstring:
            logger.debug(f"      ℹ No docstring found for '{node.name}' in {file_path}")
            return

        if self.ctx.intelligence_enabled:
            await self._run_intelligence_check(file_path, node.name, docstring, content)
        else:
            logger.debug(f"      ⏩ Intelligence disabled, skipping docstring check for '{node.name}' in {file_path}")

    async def _run_intelligence_check(self, file_path: str, node_name: str, docstring: str, content: str):
        """
        Runs the Gemini intelligence check for docstring consistency.

        Args:
            file_path: The path to the file.
            node_name: The name of the function/class.
            docstring: The extracted docstring.
            content: The full content of the file.
        """
        is_consistent = await self._verify_docstring_consistency(
            file_path, node_name, docstring, content
        )
        if not is_consistent:
            await self._perform_inconsistent_docstring_actions(file_path, node_name, content)
        else:
            logger.info(f"   ✅ Docstring for '{node_name}' in {file_path} is consistent.")

    async def _perform_inconsistent_docstring_actions(self, file_path: str, node_name: str, content: str):
        """
        Performs actions when a docstring is found to be inconsistent.

        Args:
            file_path: The path to the file.
            node_name: The name of the function/class with the inconsistent docstring.
            content: The full content of the file.
        """
        logger.warning(f"   📝 Docstring mismatch detected for '{node_name}' in {file_path}")
        # Auto-fix the docstring
        await self._fix_docstring(file_path, node_name, content)

    async def _verify_docstring_consistency(self, file_path: str, name: str, docstring: str, content: str) -> bool:
        """
        Asks Gemini if a docstring accurately matches the code implementation.

        Args:
            file_path: The path to the file containing the code.
            name: The name of the function or class.
            docstring: The docstring to verify.
            content: The full code content of the file.

        Returns:
            bool: True if Gemini deems the docstring consistent, False otherwise.
                  Assumes consistent on API errors to prevent blocking.
        """
        try:
            # Truncate content to avoid sending excessively large prompts,
            # but be aware this might reduce accuracy for very long functions/classes.
            # A more sophisticated approach might extract only the relevant node's code.
            code_snippet = content[:4000] # Increased limit for more context

            prompt = f"""
            Role: Code Reviewer
            Task: Verify if docstring matches code implementation

            Function/Class: {name}
            Docstring: {docstring}
            Code:
            ```python
            {code_snippet}
            ```

            Answer ONLY "YES" if docstring accurately describes the code, or "NO" if it doesn't.
            """

            response = self.ctx.client.models.generate_content(model=self.ctx.model_id, contents=prompt)

            # Ensure response text is not empty before stripping and comparing
            if response and response.text:
                return response.text.strip().upper() == "YES"
            else:
                logger.warning(
                    f"      ⚠️ Gemini returned empty response for consistency check of '{name}' in {file_path}. "
                    "Assuming consistent."
                )
                return True # Assume consistent on empty response

        except Exception as e:
            logger.error(
                f"      ❌ Error verifying docstring consistency for '{name}' in {file_path}: {e}. "
                "Assuming consistent to prevent blocking."
            )
            return True  # Assume consistent on error to prevent blocking the agent

    async def _fix_docstring(self, file_path: str, name: str, content: str):
        """
        Auto-fixes a docstring using Gemini by generating a new one.

        Args:
            file_path: The path to the file containing the code.
            name: The name of the function or class.
            content: The full code content of the file.
        """
        try:
            # Truncate content, similar to _verify_docstring_consistency
            code_snippet = content[:4000] # Increased limit for more context

            prompt = f"""
            Role: Technical Writer
            Task: Rewrite the docstring for {name} to accurately match the code.

            Rules:
            - Use proper Google-style docstring format
            - Describe all parameters and return values
            - Mention any exceptions raised
            - Keep it concise but complete

            Code:
            ```python
            {code_snippet}
            ```

            Return ONLY the corrected docstring.
            """

            response = self.ctx.client.models.generate_content(model=self.ctx.model_id, contents=prompt)

            if response and response.text:
                new_docstring = response.text.strip()
                # In a full implementation, we would parse the AST again,
                # locate the specific node (function/class), update its docstring,
                # and then write the modified AST back to the file. This requires
                # careful AST manipulation or source code transformation libraries
                # (e.g., `libcst` or `astunparse` for basic cases, or more advanced tools).
                logger.info(f"   ✅ Generated new docstring for '{name}'. (File update logic not implemented)")
                logger.debug(f"      Generated docstring for '{name}': \n{new_docstring}")
            else:
                logger.warning(
                    f"      ⚠️ Gemini returned empty response for docstring fix of '{name}' in {file_path}."
                )

        except Exception as e:
            logger.error(f"   ❌ Failed to fix docstring for '{name}' in {file_path}: {e}")