import logging
import os
from typing import List

from tqdm import tqdm

from agent_logic_connectivity import CanonValidator

# Import our hardened infrastructure
from schemas_connectivity import CanonEntry, CanonMetadata

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='etl_ingestion.log'
)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
logging.getLogger('').addHandler(console)


class ETLPipeline:
    def __init__(self, source_directory: str, file_extensions: List[str] = ['.md', '.py', '.txt']):
        self.source_dir = source_directory
        self.extensions = file_extensions
        self.validator = CanonValidator(
            similarity_threshold=0.80)  # Production Threshold
        self.stats = {
            "processed": 0,
            "ingested": 0,
            "duplicates": 0,
            "errors": 0
        }

    def scan_files(self) -> List[str]:
        """Recursively finds all matching files in the source directory."""
        file_paths = []
        for root, _, files in os.walk(self.source_dir):
            for file in files:
                if any(file.endswith(ext) for ext in self.extensions):
                    file_paths.append(os.path.join(root, file))
        return file_paths

    def chunk_content(self, content: str, source_file: str) -> List[str]:
        """
        Splits monolithic files into atomic 'Thoughts'.
        Strategy: Split by double newlines (paragraphs) or function definitions.
        """
        # Basic strategy: Split by paragraphs for text, preserve functions for code
        # This is a simplified chunker. For production, use a more robust AST splitter.
        if source_file.endswith('.py'):
            # Simple split by class/def keywords (naive but effective for first pass)
            chunks = []
            current_chunk = []
            for line in content.split('\n'):
                if line.strip().startswith(('def ', 'class ')):
                    if current_chunk:
                        chunks.append('\n'.join(current_chunk))
                    current_chunk = [line]
                else:
                    current_chunk.append(line)
            if current_chunk:
                chunks.append('\n'.join(current_chunk))
            return [c for c in chunks if len(c.strip()) > 50]  # Filter noise
        else:
            # Split by double newlines for Markdown/Text
            return [c.strip() for c in content.split('\n\n') if len(c.strip()) > 50]

    def run(self):
        # print("🚀 STARTING ETL PIPELINE")  # [Security Fix]
        # print(f"📂 Source: {self.source_dir}")  # [Security Fix]

        files = self.scan_files()
        # print(f"📄 Found {len(files)} files to process.")  # [Security Fix]

        # Determine total work for progress bar (estimating 5 chunks per file)
        with tqdm(total=len(files), desc="Processing Files") as pbar:
            for file_path in files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        raw_content = f.read()

                    chunks = self.chunk_content(raw_content, file_path)

                    for chunk in chunks:
                        self.stats["processed"] += 1

                        # Create Candidate Entry
                        entry = CanonEntry(
                            code_snippet=chunk,
                            # Simple AST structure
                            ast_structure={"type": "module"},
                            embedding=[],  # Will be generated
                            metadata=CanonMetadata(
                                project_context=os.path.basename(file_path),
                                canon_rule_id="etl_ingestion"
                            )
                        )

                        # Pass through Validator (The Gatekeeper)
                        result = self.validator.check_and_learn(chunk, {
                            "project_context": os.path.basename(file_path),
                            "type": "etl_ingestion"
                        })

                        if result['status'] == 'ingested':
                            self.stats["ingested"] += 1
                        elif result['status'] in ['duplicate', 'similar']:
                            self.stats["duplicates"] += 1
                        else:
                            self.stats["errors"] += 1

                except Exception as e:
                    logging.error(f"Failed to process {file_path}: {e}")
                    self.stats["errors"] += 1

                pbar.update(1)

        self._print_summary()

    def _print_summary(self):
        # print("\n📊 ETL SUMMARY")  # [Security Fix]
        # print("=========================")  # [Security Fix]
        # print(f"Total Chunks Processed: {self.stats['processed']}")  # [Security Fix]
        # print(f"✅ Ingested (New):      {self.stats['ingested']}")  # [Security Fix]
        # print(f"♻️  Duplicates (Saved):  {self.stats['duplicates']}")  # [Security Fix]
        # print(f"❌ Errors:              {self.stats['errors']}")  # [Security Fix]
        # print("=========================")  # [Security Fix]
        pass


if __name__ == "__main__":
    # EXAMPLE USAGE:
    # Replace '.' with the path to your legacy data folder
    # e.g., source_dir = "./legacy_docs"

    # For testing, we can scan the current directory
    pipeline = ETLPipeline(source_directory="./")
    pipeline.run()

