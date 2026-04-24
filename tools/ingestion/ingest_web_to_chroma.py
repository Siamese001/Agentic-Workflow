#!/usr/bin/env python3
"""
Production-ready Python ingestion pipeline for web-based RAG using BGE embeddings and ChromaDB.

Ingests URLs from data/rag_seeds/agentic_best_practices_urls.txt, extracts clean text,
chunks it, generates embeddings using BAAI/bge-m3, and stores results in ChromaDB.
"""

import hashlib
import logging
import re
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

import chromadb
import requests
from bs4 import BeautifulSoup
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from tqdm import tqdm
from agentic_core.L4_state.config.chroma_paths import canonical_persist_dir_str

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


@dataclass
class DocumentStructure:
    """Represents the hierarchical structure of a document."""

    title: str
    sections: list["Section"]


@dataclass
class Section:
    """Represents a document section with hierarchical content."""

    level: int  # 1 for h1, 2 for h2, 3 for h3
    title: str
    content_blocks: list["ContentBlock"]
    subsections: list["Section"]


@dataclass
class ContentBlock:
    """Represents a block of content (paragraph, list, code, etc.)."""

    block_type: str  # 'paragraph', 'list', 'code', 'heading'
    content: str
    raw_html: str | None = None


@dataclass
class SemanticChunk:
    """Represents a semantic chunk with context and metadata."""

    chunk_id: str
    section_title: str
    subsection_title: str | None
    chunk_type: str
    content: str
    context_header: str
    token_estimate: int


class WebRAGIngestionPipeline:
    """Production-ready pipeline for ingesting web content into ChromaDB with BGE embeddings."""

    def __init__(
        self,
        urls_file: str = "data/rag_seeds/agentic_best_practices_urls.txt",
        chroma_path: str = canonical_persist_dir_str(),
        collection_name: str = "agentic_best_practices",
        model_name: str = "BAAI/bge-m3",
        debug_chunks: bool = False,
    ):
        """
        Initialize the RAG ingestion pipeline.

        Args:
            urls_file: Path to file containing URLs (one per line)
            chroma_path: Path to store ChromaDB
            collection_name: Name of ChromaDB collection
            model_name: Name of sentence transformer model
            debug_chunks: Enable chunk debugging output
        """
        self.urls_file = Path(urls_file)
        self.chroma_path = Path(chroma_path)
        self.collection_name = collection_name
        self.model_name = model_name
        self.debug_chunks = debug_chunks

        # Ensure directories exist
        self.chroma_path.mkdir(parents=True, exist_ok=True)

        # Initialize components
        self.embedding_model = None
        self.chroma_client = None
        self.collection = None

        # Statistics
        self.stats = {
            "urls_processed": 0,
            "urls_successful": 0,
            "urls_failed": 0,
            "chunks_stored": 0,
            "chunks_skipped": 0,
        }

    def initialize(self):
        """Initialize embedding model and ChromaDB client."""
        logger.info(f"Loading embedding model: {self.model_name}")
        self.embedding_model = SentenceTransformer(self.model_name)

        logger.info(f"Initializing ChromaDB at: {self.chroma_path}")
        self.chroma_client = chromadb.PersistentClient(
            path=str(self.chroma_path),
            settings=Settings(anonymized_telemetry=False),
        )

        # Get or create collection
        try:
            self.collection = self.chroma_client.get_collection(self.collection_name)
            logger.info(f"Using existing collection: {self.collection_name}")
        except chromadb.errors.NotFoundError:
            self.collection = self.chroma_client.create_collection(self.collection_name)
            logger.info(f"Created new collection: {self.collection_name}")

    def read_urls(self) -> list[str]:
        """Read URLs from the input file."""
        if not self.urls_file.exists():
            raise FileNotFoundError(f"URLs file not found: {self.urls_file}")

        urls = []
        with open(self.urls_file, encoding="utf-8") as f:
            for line in f:
                url = line.strip()
                if url and not url.startswith("#"):  # Skip empty lines and comments
                    urls.append(url)

        logger.info(f"Loaded {len(urls)} URLs from {self.urls_file}")
        return urls

    def fetch_content(self, url: str, retry_once: bool = True) -> str | None:
        """
        Fetch HTML content from a URL with retry logic.

        Args:
            url: URL to fetch
            retry_once: Whether to retry once on failure

        Returns:
            HTML content or None if failed
        """
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        }

        try:
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            return response.text
        except Exception as e:
            logger.warning(f"Failed to fetch {url}: {e}")
            if retry_once:
                logger.info(f"Retrying {url}...")
                time.sleep(2)
                return self.fetch_content(url, retry_once=False)
            return None

    def extract_clean_text(self, html: str, url: str) -> tuple[str, str]:
        """
        Extract clean text content from HTML.

        Args:
            html: HTML content
            url: Source URL

        Returns:
            Tuple of (clean_text, document_title)
        """
        soup = BeautifulSoup(html, "lxml")

        # Remove unwanted elements
        for element in soup(["script", "style", "nav", "footer", "header", "aside", "iframe"]):
            element.decompose()

        # Extract title
        title_tag = soup.find("title")
        title = title_tag.get_text().strip() if title_tag else urlparse(url).netloc

        # Try to find main content areas
        main_content = None
        for selector in ["main", "article", '[role="main"]', ".content", "#content"]:
            main_content = soup.select_one(selector)
            if main_content:
                break

        # If no main content found, use body
        if not main_content:
            main_content = soup.find("body") or soup

        # Extract text from priority elements
        text_parts = []

        # Headings and paragraphs
        for element in main_content.find_all(["h1", "h2", "h3", "p", "div"]):
            text = element.get_text().strip()
            if text and len(text) > 10:  # Skip very short text
                text_parts.append(text)

        # Join and normalize text
        full_text = "\n\n".join(text_parts)

        # Normalize whitespace
        lines = [line.strip() for line in full_text.split("\n") if line.strip()]
        clean_text = "\n".join(lines)

        return clean_text, title

    def extract_document_structure(self, html: str, url: str) -> DocumentStructure:
        """
        Extract hierarchical structure from HTML document.

        Args:
            html: HTML content
            url: Source URL

        Returns:
            DocumentStructure with hierarchical sections
        """
        soup = BeautifulSoup(html, "lxml")

        # Remove unwanted elements
        for element in soup(["script", "style", "nav", "footer", "header", "aside", "iframe"]):
            element.decompose()

        # Extract document title
        title_tag = soup.find("title")
        doc_title = title_tag.get_text().strip() if title_tag else urlparse(url).netloc

        # Find main content area
        main_content = None
        for selector in ["main", "article", '[role="main"]', ".content", "#content"]:
            main_content = soup.select_one(selector)
            if main_content:
                break

        if not main_content:
            main_content = soup.find("body") or soup

        # Extract structure
        sections = []
        current_section = None
        current_subsection = None

        # Get all elements in order - expanded to catch more content
        elements = main_content.find_all(
            ["h1", "h2", "h3", "h4", "p", "ul", "ol", "pre", "div", "span", "li", "section", "article"],
        )

        if self.debug_chunks:
            print(f"Found {len(elements)} elements to process")

        for element in elements:
            tag_name = element.name.lower()

            # Handle headings
            if tag_name in ["h1", "h2", "h3"]:
                heading_text = element.get_text().strip()
                if not heading_text:
                    continue

                level = int(tag_name[1])

                if self.debug_chunks:
                    print(f"Found H{level}: {heading_text}")

                if level == 1 or level == 2:
                    # New main section
                    current_section = Section(
                        level=level,
                        title=heading_text,
                        content_blocks=[],
                        subsections=[],
                    )
                    sections.append(current_section)
                    current_subsection = None
                elif level == 3 and current_section:
                    # New subsection
                    current_subsection = Section(
                        level=level,
                        title=heading_text,
                        content_blocks=[],
                        subsections=[],
                    )
                    current_section.subsections.append(current_subsection)

            # Handle content blocks
            elif tag_name in ["p", "ul", "ol", "pre", "div", "section", "article"]:
                content_text = element.get_text().strip()
                if not content_text or len(content_text) < 10:
                    continue

                # Skip if this is just a container for other elements
                if (
                    tag_name in ["div", "section", "article"]
                    and len(element.find_all(["h1", "h2", "h3", "p", "ul", "ol", "pre"])) > 0
                ):
                    if self.debug_chunks:
                        print(f"Skipping container {tag_name} with nested elements")
                    continue

                if self.debug_chunks:
                    print(f"Found {tag_name}: {content_text[:50]}...")

                block_type = (
                    "paragraph"
                    if tag_name == "p"
                    else (
                        "list" if tag_name in ["ul", "ol"] else ("code" if tag_name == "pre" else "content")
                    )
                )
                content_block = ContentBlock(
                    block_type=block_type,
                    content=content_text,
                    raw_html=str(element),
                )

                # Add to appropriate section
                if current_subsection:
                    current_subsection.content_blocks.append(content_block)
                elif current_section:
                    current_section.content_blocks.append(content_block)
                else:
                    # Create default section if no headings found
                    if not sections:
                        current_section = Section(
                            level=1,
                            title="Introduction",
                            content_blocks=[],
                            subsections=[],
                        )
                        sections.append(current_section)
                        if self.debug_chunks:
                            print("Created default 'Introduction' section")
                    current_section.content_blocks.append(content_block)

        if self.debug_chunks:
            print(f"Created {len(sections)} sections")
            for i, section in enumerate(sections):
                print(
                    f"  Section {i + 1}: {section.title} ({len(section.content_blocks)} blocks, {len(section.subsections)} subsections)",
                )

        return DocumentStructure(title=doc_title, sections=sections)

    def estimate_tokens(self, text: str) -> int:
        """
        Lightweight token estimation using word count approximation.

        Args:
            text: Input text

        Returns:
            Estimated token count
        """
        word_count = len(text.split())
        return int(word_count * 1.3)  # Approximate tokens per word

    def classify_chunk_type(self, content: str) -> str:
        """
        Classify chunk type using simple keyword heuristics.

        Args:
            content: Chunk content

        Returns:
            Chunk type classification
        """
        content_lower = content.lower()

        # Check for code
        if any(
            indicator in content_lower
            for indicator in ["```", "def ", "class ", "import ", "function(", "var ", "const "]
        ):
            return "code"

        # Check for examples
        if any(
            indicator in content_lower
            for indicator in ["example", "for instance", "such as", "e.g.", "sample"]
        ):
            return "example"

        # Check for procedures
        if any(
            indicator in content_lower
            for indicator in ["step", "procedure", "how to", "first,", "second,", "finally", "follow"]
        ):
            return "procedure"

        # Check for definitions
        if any(
            indicator in content_lower
            for indicator in ["definition", "defined as", "refers to", "means", "is a"]
        ):
            return "definition"

        # Default to concept
        return "concept"

    def split_sentences(self, text: str) -> list[str]:
        """
        Split text into sentences using simple punctuation-based splitting.

        Args:
            text: Input text

        Returns:
            List of sentences
        """
        # Handle common abbreviations to avoid incorrect splits
        abbreviations = {"mr.", "mrs.", "dr.", "prof.", "sr.", "jr.", "vs.", "etc.", "e.g.", "i.e."}

        for abbr in abbreviations:
            text = text.replace(abbr, abbr.replace(".", "<DOT>"))

        # Split on sentence endings
        sentences = re.split(r"[.!?]+", text)

        # Restore abbreviations and clean up
        clean_sentences = []
        for sentence in sentences:
            sentence = sentence.replace("<DOT>", ".").strip()
            if sentence and len(sentence) > 5:
                clean_sentences.append(sentence)

        return clean_sentences

    def build_semantic_chunks(self, structure: DocumentStructure, url: str) -> list[SemanticChunk]:
        """
        Build semantic chunks from document structure.

        Args:
            structure: Document structure
            url: Source URL

        Returns:
            List of semantic chunks
        """
        chunks = []
        domain = urlparse(url).netloc

        def process_section(section: Section, parent_section: str | None = None):
            """Recursively process sections and create chunks."""
            section_title = section.title
            subsection_title = parent_section if parent_section else None

            # Group content blocks into semantic units - merge small blocks
            semantic_units = []
            current_unit_blocks = []
            current_tokens = 0

            for block in section.content_blocks:
                block_tokens = self.estimate_tokens(block.content)

                # If this is a very small block, try to merge with previous
                if block_tokens < 20 and current_unit_blocks:
                    # Add to current unit to build up content
                    current_unit_blocks.append(block)
                    current_tokens += block_tokens
                    continue

                # Check if adding this block would exceed target size (relaxed)
                if current_tokens + block_tokens > 1200 and current_unit_blocks:  # Increased from 800
                    # Save current unit and start new one
                    semantic_units.append(current_unit_blocks)
                    current_unit_blocks = [block]
                    current_tokens = block_tokens
                else:
                    current_unit_blocks.append(block)
                    current_tokens += block_tokens

            # Add the last unit if it exists
            if current_unit_blocks:
                semantic_units.append(current_unit_blocks)

            # If we have very small units, merge them
            if len(semantic_units) > 1:
                merged_units = []
                current_merged = semantic_units[0]
                current_tokens = sum(self.estimate_tokens(block.content) for block in current_merged)

                for unit in semantic_units[1:]:
                    unit_tokens = sum(self.estimate_tokens(block.content) for block in unit)

                    # Merge if current unit is small and combined size is reasonable
                    if current_tokens < 30 and current_tokens + unit_tokens < 200:
                        current_merged.extend(unit)
                        current_tokens += unit_tokens
                    else:
                        merged_units.append(current_merged)
                        current_merged = unit
                        current_tokens = unit_tokens

                merged_units.append(current_merged)
                semantic_units = merged_units

            # Create chunks from semantic units
            for i, unit_blocks in enumerate(semantic_units):
                # Combine content from blocks
                unit_content = "\n\n".join(block.content for block in unit_blocks)

                # Skip if too short (relaxed threshold)
                unit_tokens = self.estimate_tokens(unit_content)
                if self.debug_chunks:
                    print(f"Unit {i}: {unit_tokens} tokens, {len(unit_blocks)} blocks")
                    print(f"Content preview: {unit_content[:100]}...")

                if unit_tokens < 20:  # Further reduced from 50
                    if self.debug_chunks:
                        print(f"Skipping unit {i}: too short ({unit_tokens} tokens)")
                    continue

                # Skip if mostly boilerplate (more specific check)
                content_lower = unit_content.lower()
                boilerplate_indicators = [
                    "navigation",
                    "menu",
                    "footer",
                    "header",
                    "copyright",
                    "all rights reserved",
                ]
                if any(indicator in content_lower for indicator in boilerplate_indicators):
                    # Only skip if it's primarily boilerplate (>50% boilerplate indicators)
                    boilerplate_count = sum(
                        1 for indicator in boilerplate_indicators if indicator in content_lower
                    )
                    if boilerplate_count > 2:  # More than 2 boilerplate indicators
                        if self.debug_chunks:
                            print(f"Skipping unit {i}: too much boilerplate ({boilerplate_count} indicators)")
                        continue

                # Create context header
                context_header = f"[SECTION]: {section_title}"
                if subsection_title:
                    context_header += f"\n[SUBSECTION]: {subsection_title}"
                context_header += f"\n[SOURCE]: {domain}"

                # Classify chunk type
                chunk_type = self.classify_chunk_type(unit_content)

                # Generate chunk ID
                chunk_id = hashlib.sha256(f"{section_title}_{i}_{unit_content[:100]}".encode()).hexdigest()[
                    :12
                ]

                # Create semantic chunk
                chunk = SemanticChunk(
                    chunk_id=chunk_id,
                    section_title=section_title,
                    subsection_title=subsection_title,
                    chunk_type=chunk_type,
                    content=unit_content,
                    context_header=context_header,
                    token_estimate=unit_tokens,
                )

                chunks.append(chunk)

                # Debug output if enabled
                if self.debug_chunks:
                    print(f"\n--- CHUNK {chunk_id} ---")
                    print(f"Type: {chunk_type}")
                    print(f"Tokens: {unit_tokens}")
                    print(f"Context:\n{context_header}")
                    print(f"Content:\n{unit_content[:200]}...")
                    print("-" * 40)

            # Process subsections
            for subsection in section.subsections:
                process_section(subsection, section_title)

        # Process all sections
        for section in structure.sections:
            process_section(section)

        return chunks

    def chunk_text(
        self,
        text: str,
        chunk_size: int = 700,
        overlap: int = 100,
        html: str = "",
        url: str = "",
    ) -> list[tuple[str, dict]]:
        """
        Split text into semantic chunks using structure-aware approach.

        Args:
            text: Input text (legacy parameter, not used in new implementation)
            chunk_size: Target chunk size (legacy parameter)
            overlap: Overlap (legacy parameter)
            html: HTML content for structure extraction
            url: Source URL

        Returns:
            List of tuples containing (chunk_text, metadata)
        """
        if not html:
            # Fallback to simple chunking if no HTML provided
            return self._fallback_chunking(text, chunk_size, overlap)

        # Extract document structure
        structure = self.extract_document_structure(html, url)

        # Build semantic chunks
        semantic_chunks = self.build_semantic_chunks(structure, url)

        # Debug logging
        if self.debug_chunks:
            print("\n=== DOCUMENT STRUCTURE DEBUG ===")
            print(f"Document: {structure.title}")
            print(f"Total sections: {len(structure.sections)}")
            print(f"Total chunks created: {len(semantic_chunks)}")

            if semantic_chunks:
                avg_tokens = sum(chunk.token_estimate for chunk in semantic_chunks) / len(semantic_chunks)
                print(f"Average chunk size: {avg_tokens:.1f} tokens")

            print("=" * 40)

        # Convert to legacy format (text, metadata)
        result = []
        for chunk in semantic_chunks:
            # Combine context header with content
            full_chunk_text = f"{chunk.context_header}\n\n{chunk.content}"

            metadata = {
                "chunk_id": chunk.chunk_id,
                "section_title": chunk.section_title,
                "subsection_title": chunk.subsection_title or "",
                "chunk_type": chunk.chunk_type,
                "token_estimate": int(chunk.token_estimate),
            }

            result.append((full_chunk_text, metadata))

        return result

    def _fallback_chunking(
        self,
        text: str,
        chunk_size: int = 700,
        overlap: int = 100,
    ) -> list[tuple[str, dict]]:
        """
        Fallback chunking method for when HTML is not available.

        Args:
            text: Input text
            chunk_size: Target chunk size in tokens (approximate)
            overlap: Overlap between chunks in tokens

        Returns:
            List of tuples containing (chunk_text, metadata)
        """
        # Simple word-based chunking (approximate token count)
        words = text.split()
        chunks = []

        start = 0
        chunk_index = 0
        while start < len(words):
            end = start + chunk_size
            chunk_words = words[start:end]
            chunk = " ".join(chunk_words)

            if len(chunk.strip()) > 50:  # Skip very short chunks
                metadata = {
                    "chunk_id": f"fallback_{chunk_index}",
                    "section_title": "Unknown",
                    "subsection_title": None,
                    "chunk_type": "concept",
                    "token_estimate": self.estimate_tokens(chunk),
                }
                chunks.append((chunk.strip(), metadata))
                chunk_index += 1

            if end >= len(words):
                break

            start = end - overlap

        return chunks

    def generate_content_hash(self, content: str) -> str:
        """Generate SHA256 hash of content for deduplication."""
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    def process_url(self, url: str) -> int:
        """
        Process a single URL and store chunks in ChromaDB.

        Args:
            url: URL to process

        Returns:
            Number of chunks stored for this URL
        """
        logger.info(f"Processing URL: {url}")

        # Fetch content
        html = self.fetch_content(url)
        if not html:
            logger.error(f"Failed to fetch content for {url}")
            return 0

        # Extract clean text
        clean_text, title = self.extract_clean_text(html, url)
        if not clean_text or len(clean_text.strip()) < 100:
            logger.warning(f"Insufficient content extracted from {url}")
            return 0

        # Filter out loading/placeholder content
        if "Loading..." in clean_text or clean_text.count("Loading") > len(clean_text) * 0.1:
            logger.warning(f"Content appears to be loading placeholders for {url}")
            return 0

        # Use semantic chunking
        chunk_results = self.chunk_text(clean_text, html=html, url=url)
        if not chunk_results:
            logger.warning(f"No chunks generated from {url}")
            logger.warning(f"Clean text length: {len(clean_text)}")
            logger.warning(f"Clean text preview: {clean_text[:500]}...")
            return 0

        # Process chunks
        stored_count = 0
        domain = urlparse(url).netloc
        fetched_at = int(time.time())

        # Generate embeddings for all chunks
        chunk_texts = [chunk_text for chunk_text, _ in chunk_results]
        logger.info(f"Generating embeddings for {len(chunk_texts)} chunks...")
        embeddings = self.embedding_model.encode(chunk_texts, convert_to_numpy=True)

        # Prepare batch data
        documents = []
        embeddings_list = []
        metadatas = []
        ids = []

        for i, ((chunk_text, chunk_metadata), embedding) in enumerate(zip(chunk_results, embeddings)):
            # Generate content hash for deduplication
            content_hash = self.generate_content_hash(chunk_text)

            # Check if chunk already exists
            existing = self.collection.get(where={"content_hash": content_hash}, limit=1)

            if existing["ids"]:
                logger.debug(f"Skipping duplicate chunk: {content_hash[:8]}...")
                self.stats["chunks_skipped"] += 1
                continue

            # Prepare enhanced metadata
            metadata = {
                "source_url": url,
                "domain": domain,
                "document_title": title,
                "chunk_id": str(uuid.uuid4()),
                "chunk_index": i,
                "fetched_at": fetched_at,
                "content_hash": content_hash,
                # Enhanced semantic metadata
                "semantic_chunk_id": chunk_metadata.get("chunk_id", f"chunk_{i}"),
                "section_title": chunk_metadata.get("section_title", "Unknown"),
                "subsection_title": chunk_metadata.get("subsection_title", ""),
                "chunk_type": chunk_metadata.get("chunk_type", "concept"),
                "token_estimate": int(chunk_metadata.get("token_estimate", 0)),
            }

            # Add to batch
            documents.append(chunk_text)
            embeddings_list.append(embedding.tolist())
            metadatas.append(metadata)
            ids.append(f"{url}_{i}_{content_hash[:8]}")
            stored_count += 1

        # Store in ChromaDB (batch)
        if documents:
            self.collection.add(documents=documents, embeddings=embeddings_list, metadatas=metadatas, ids=ids)
            logger.info(f"Stored {stored_count} chunks from {url}")

        return stored_count

    def run(self):
        """Run the complete ingestion pipeline."""
        logger.info("Starting RAG ingestion pipeline...")

        # Initialize components
        self.initialize()

        # Read URLs
        urls = self.read_urls()
        if not urls:
            logger.error("No URLs to process")
            return

        # Process URLs with progress bar
        with tqdm(urls, desc="Processing URLs") as pbar:
            for url in pbar:
                self.stats["urls_processed"] += 1

                try:
                    chunks_stored = self.process_url(url)
                    self.stats["chunks_stored"] += chunks_stored
                    self.stats["urls_successful"] += 1

                    pbar.set_postfix(
                        {
                            "Success": self.stats["urls_successful"],
                            "Failed": self.stats["urls_failed"],
                            "Chunks": self.stats["chunks_stored"],
                        },
                    )

                except Exception as e:
                    logger.error(f"Error processing {url}: {e}")
                    self.stats["urls_failed"] += 1

        # Print final statistics
        self.print_summary()

    def print_summary(self):
        """Print processing summary."""
        logger.info("=" * 50)
        logger.info("INGESTION SUMMARY")
        logger.info("=" * 50)
        logger.info(f"Processed URLs: {self.stats['urls_processed']}")
        logger.info(f"Successful: {self.stats['urls_successful']}")
        logger.info(f"Failed: {self.stats['urls_failed']}")
        logger.info(f"Chunks stored: {self.stats['chunks_stored']}")
        logger.info(f"Chunks skipped (duplicates): {self.stats['chunks_skipped']}")

        # Get collection stats
        if self.collection:
            count = self.collection.count()
            logger.info(f"Total chunks in collection: {count}")

    def query_chroma(self, query: str, n_results: int = 5):
        """
        Query the ChromaDB collection.

        Args:
            query: Query string
            n_results: Number of results to return
        """
        if not self.embedding_model or not self.collection:
            logger.error("Pipeline not initialized. Call run() first.")
            return

        logger.info(f"Querying: {query}")

        # Generate query embedding
        query_embedding = self.embedding_model.encode([query], convert_to_numpy=True)

        # Query ChromaDB
        results = self.collection.query(query_embeddings=query_embedding.tolist(), n_results=n_results)

        # Display results
        logger.info(f"Found {len(results['documents'][0])} results:")
        print("\n" + "=" * 50)

        for i, (doc, metadata) in enumerate(zip(results["documents"][0], results["metadatas"][0])):
            print(f"\nResult {i + 1}:")
            print(f"Source: {metadata.get('source_url', 'Unknown')}")
            print(f"Title: {metadata.get('document_title', 'Unknown')}")
            print(f"Content: {doc[:300]}...")
            print("-" * 30)


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Web RAG Ingestion Pipeline with Semantic Chunking")
    parser.add_argument("--debug-chunks", action="store_true", help="Enable chunk debugging output")
    args = parser.parse_args()

    pipeline = WebRAGIngestionPipeline(debug_chunks=args.debug_chunks)
    pipeline.run()

    # Optional: Test query
    print("\n" + "=" * 50)
    print("TEST QUERY")
    print("=" * 50)
    pipeline.query_chroma("What are the best practices for prompt engineering?")


if __name__ == "__main__":
    main()
