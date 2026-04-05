#!/usr/bin/env python3
"""
Enhanced production-ready Python ingestion pipeline for web-based RAG using BGE embeddings and ChromaDB.

Ingests URLs from data/rag_seeds/agentic_best_practices_urls.txt, extracts clean text,
chunks it, generates embeddings using BAAI/bge-m3, and stores results in ChromaDB
with source-type metadata categorization for improved retrieval filtering.
"""

import hashlib
import logging
import time
import uuid
from pathlib import Path
from urllib.parse import urlparse

import chromadb
import requests
from bs4 import BeautifulSoup
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from tqdm import tqdm

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class EnhancedWebRAGIngestionPipeline:
    """Enhanced pipeline for ingesting web content into ChromaDB with source-type categorization."""

    # Source type categorization mapping
    SOURCE_TYPE_MAPPING = {
        # Framework docs
        "docs.trychroma.com": "framework",
        "microsoft.github.io": "framework",
        "modelcontextprotocol.io": "framework",

        # Vendor docs
        "huggingface.co": "vendor_docs",
        "docs.anthropic.com": "vendor_docs",

        # Governance sources
        "nist.gov": "governance",
        "nvlpubs.nist.gov": "governance",

        # Embedding model docs
        "huggingface.co/BAAI": "embedding_model",

        # Agent runtime docs
        "microsoft.github.io/autogen": "agent_runtime",

        # Default categorization
        "python.langchain.com": "framework",
        "paulgraham.com": "blog"
    }

    def __init__(self,
                 urls_file: str = "data/rag_seeds/agentic_best_practices_urls.txt",
                 chroma_path: str = "artifacts/chromadb",
                 collection_name: str = "agentic_best_practices",
                 model_name: str = "BAAI/bge-m3"):
        """
        Initialize the enhanced RAG ingestion pipeline.

        Args:
            urls_file: Path to file containing URLs (one per line)
            chroma_path: Path to store ChromaDB
            collection_name: Name of ChromaDB collection
            model_name: Name of sentence transformer model
        """
        self.urls_file = Path(urls_file)
        self.chroma_path = Path(chroma_path)
        self.collection_name = collection_name
        self.model_name = model_name

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
            "source_types": {}
        }

    def initialize(self):
        """Initialize embedding model and ChromaDB client."""
        logger.info(f"Loading embedding model: {self.model_name}")
        self.embedding_model = SentenceTransformer(self.model_name)

        logger.info(f"Initializing ChromaDB at: {self.chroma_path}")
        self.chroma_client = chromadb.PersistentClient(
            path=str(self.chroma_path),
            settings=Settings(anonymized_telemetry=False)
        )

        # Get or create collection
        try:
            self.collection = self.chroma_client.get_collection(self.collection_name)
            logger.info(f"Using existing collection: {self.collection_name}")
        except chromadb.errors.NotFoundError:
            self.collection = self.chroma_client.create_collection(self.collection_name)
            logger.info(f"Created new collection: {self.collection_name}")

    def determine_source_type(self, url: str) -> str:
        """
        Determine the source type for a URL based on domain patterns.

        Args:
            url: URL to categorize

        Returns:
            Source type string
        """
        domain = urlparse(url).netloc.lower()

        # Check exact domain matches first
        for pattern, source_type in self.SOURCE_TYPE_MAPPING.items():
            if pattern in domain:
                return source_type

        # Check for broader patterns
        if "docs." in domain:
            return "framework"
        elif "github.io" in domain:
            return "framework"
        elif "huggingface.co" in domain:
            return "vendor_docs"
        elif "nist.gov" in domain:
            return "governance"
        elif "anthropic.com" in domain:
            return "vendor_docs"

        # Default fallback
        return "other"

    def read_urls_with_metadata(self) -> list[tuple[str, dict]]:
        """
        Read URLs from the input file with source type metadata.

        Returns:
            List of tuples containing (url, metadata_dict)
        """
        if not self.urls_file.exists():
            raise FileNotFoundError(f"URLs file not found: {self.urls_file}")

        url_entries = []
        with open(self.urls_file, encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if line and not line.startswith('#'):  # Skip empty lines and comments
                    url = line
                    source_type = self.determine_source_type(url)

                    # Extract additional metadata from comments if present
                    metadata = {
                        "source_type": source_type,
                        "line_number": line_num
                    }

                    url_entries.append((url, metadata))

        logger.info(f"Loaded {len(url_entries)} URLs from {self.urls_file}")
        return url_entries

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
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
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
        soup = BeautifulSoup(html, 'lxml')

        # Remove unwanted elements
        for element in soup(['script', 'style', 'nav', 'footer', 'header', 'aside', 'iframe']):
            element.decompose()

        # Extract title
        title_tag = soup.find('title')
        title = title_tag.get_text().strip() if title_tag else urlparse(url).netloc

        # Try to find main content areas
        main_content = None
        for selector in ['main', 'article', '[role="main"]', '.content', '#content']:
            main_content = soup.select_one(selector)
            if main_content:
                break

        # If no main content found, use body
        if not main_content:
            main_content = soup.find('body') or soup

        # Extract text from priority elements
        text_parts = []

        # Headings and paragraphs
        for element in main_content.find_all(['h1', 'h2', 'h3', 'p', 'div']):
            text = element.get_text().strip()
            if text and len(text) > 10:  # Skip very short text
                text_parts.append(text)

        # Join and normalize text
        full_text = '\n\n'.join(text_parts)

        # Normalize whitespace
        lines = [line.strip() for line in full_text.split('\n') if line.strip()]
        clean_text = '\n'.join(lines)

        return clean_text, title

    def chunk_text(self, text: str, chunk_size: int = 700, overlap: int = 100) -> list[str]:
        """
        Split text into overlapping chunks.

        Args:
            text: Input text
            chunk_size: Target chunk size in tokens (approximate)
            overlap: Overlap between chunks in tokens

        Returns:
            List of text chunks
        """
        # Simple word-based chunking (approximate token count)
        words = text.split()
        chunks = []

        start = 0
        while start < len(words):
            end = start + chunk_size
            chunk_words = words[start:end]
            chunk = ' '.join(chunk_words)

            if len(chunk.strip()) > 50:  # Skip very short chunks
                chunks.append(chunk.strip())

            if end >= len(words):
                break

            start = end - overlap

        return chunks

    def generate_content_hash(self, content: str) -> str:
        """Generate SHA256 hash of content for deduplication."""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()

    def process_url(self, url: str, url_metadata: dict) -> int:
        """
        Process a single URL and store chunks in ChromaDB with enhanced metadata.

        Args:
            url: URL to process
            url_metadata: Metadata for the URL (source_type, etc.)

        Returns:
            Number of chunks stored for this URL
        """
        logger.info(f"Processing URL: {url} (source_type: {url_metadata.get('source_type', 'unknown')})")

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

        # Chunk text
        chunks = self.chunk_text(clean_text)
        if not chunks:
            logger.warning(f"No chunks generated from {url}")
            return 0

        # Process chunks
        stored_count = 0
        domain = urlparse(url).netloc
        fetched_at = int(time.time())
        source_type = url_metadata.get('source_type', 'other')

        # Update source type statistics
        self.stats["source_types"][source_type] = self.stats["source_types"].get(source_type, 0) + 1

        # Generate embeddings for all chunks
        logger.info(f"Generating embeddings for {len(chunks)} chunks...")
        embeddings = self.embedding_model.encode(chunks, convert_to_numpy=True)

        # Prepare batch data
        documents = []
        embeddings_list = []
        metadatas = []
        ids = []

        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            # Generate content hash for deduplication
            content_hash = self.generate_content_hash(chunk)

            # Check if chunk already exists
            existing = self.collection.get(
                where={"content_hash": content_hash},
                limit=1
            )

            if existing['ids']:
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
                "source_type": source_type,
                "line_number": url_metadata.get('line_number', 0)
            }

            # Add to batch
            documents.append(chunk)
            embeddings_list.append(embedding.tolist())
            metadatas.append(metadata)
            ids.append(f"{url}_{i}_{content_hash[:8]}")
            stored_count += 1

        # Store in ChromaDB (batch)
        if documents:
            self.collection.add(
                documents=documents,
                embeddings=embeddings_list,
                metadatas=metadatas,
                ids=ids
            )
            logger.info(f"Stored {stored_count} chunks from {url}")

        return stored_count

    def run(self):
        """Run the complete enhanced ingestion pipeline."""
        logger.info("Starting enhanced RAG ingestion pipeline with source-type categorization...")

        # Initialize components
        self.initialize()

        # Read URLs with metadata
        url_entries = self.read_urls_with_metadata()
        if not url_entries:
            logger.error("No URLs to process")
            return

        # Process URLs with progress bar
        with tqdm(url_entries, desc="Processing URLs") as pbar:
            for url, metadata in pbar:
                self.stats["urls_processed"] += 1

                try:
                    chunks_stored = self.process_url(url, metadata)
                    self.stats["chunks_stored"] += chunks_stored
                    self.stats["urls_successful"] += 1

                    pbar.set_postfix({
                        "Success": self.stats["urls_successful"],
                        "Failed": self.stats["urls_failed"],
                        "Chunks": self.stats["chunks_stored"]
                    })

                except Exception as e:
                    logger.error(f"Error processing {url}: {e}")
                    self.stats["urls_failed"] += 1

        # Print final statistics
        self.print_summary()

    def print_summary(self):
        """Print enhanced processing summary."""
        logger.info("=" * 60)
        logger.info("ENHANCED INGESTION SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Processed URLs: {self.stats['urls_processed']}")
        logger.info(f"Successful: {self.stats['urls_successful']}")
        logger.info(f"Failed: {self.stats['urls_failed']}")
        logger.info(f"Chunks stored: {self.stats['chunks_stored']}")
        logger.info(f"Chunks skipped (duplicates): {self.stats['chunks_skipped']}")

        logger.info("\nSource Type Breakdown:")
        for source_type, count in self.stats["source_types"].items():
            logger.info(f"  {source_type}: {count} URLs")

        # Get collection stats
        if self.collection:
            count = self.collection.count()
            logger.info(f"\nTotal chunks in collection: {count}")

    def query_chroma(self, query: str, n_results: int = 5, source_type: str | None = None):
        """
        Query the ChromaDB collection with optional source type filtering.

        Args:
            query: Query string
            n_results: Number of results to return
            source_type: Optional source type filter
        """
        if not self.embedding_model or not self.collection:
            logger.error("Pipeline not initialized. Call run() first.")
            return

        logger.info(f"Querying: {query}" + (f" (source_type: {source_type})" if source_type else ""))

        # Generate query embedding
        query_embedding = self.embedding_model.encode([query], convert_to_numpy=True)

        # Prepare where clause for source type filtering
        where_clause = {"source_type": source_type} if source_type else None

        # Query ChromaDB
        results = self.collection.query(
            query_embeddings=query_embedding.tolist(),
            n_results=n_results,
            where=where_clause
        )

        # Display results
        logger.info(f"Found {len(results['documents'][0])} results:")
        print("\n" + "=" * 50)

        for i, (doc, metadata) in enumerate(zip(results['documents'][0], results['metadatas'][0])):
            print(f"\nResult {i+1}:")
            print(f"Source: {metadata.get('source_url', 'Unknown')}")
            print(f"Source Type: {metadata.get('source_type', 'Unknown')}")
            print(f"Title: {metadata.get('document_title', 'Unknown')}")
            print(f"Content: {doc[:300]}...")
            print("-" * 30)

    def get_source_type_stats(self):
        """Get statistics by source type from the collection."""
        if not self.collection:
            logger.error("Pipeline not initialized. Call run() first.")
            return

        logger.info("Collection statistics by source type:")

        # Get all chunks and group by source type
        all_results = self.collection.get()
        source_type_counts = {}

        for metadata in all_results['metadatas']:
            source_type = metadata.get('source_type', 'unknown')
            source_type_counts[source_type] = source_type_counts.get(source_type, 0) + 1

        for source_type, count in sorted(source_type_counts.items()):
            logger.info(f"  {source_type}: {count} chunks")


def main():
    """Main entry point."""
    pipeline = EnhancedWebRAGIngestionPipeline()
    pipeline.run()

    # Optional: Test query with source type filtering
    print("\n" + "=" * 50)
    print("TEST QUERY - ALL SOURCES")
    print("=" * 50)
    pipeline.query_chroma("What are the best practices for vector databases?")

    print("\n" + "=" * 50)
    print("TEST QUERY - FRAMEWORK DOCS ONLY")
    print("=" * 50)
    pipeline.query_chroma("What are the best practices for vector databases?", source_type="framework")

    # Show source type statistics
    print("\n" + "=" * 50)
    print("SOURCE TYPE STATISTICS")
    print("=" * 50)
    pipeline.get_source_type_stats()


if __name__ == "__main__":
    main()
