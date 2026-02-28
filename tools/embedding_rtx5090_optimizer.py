#!/usr/bin/env python3
"""
RTX 5090 Optimized Embedding Pipeline
Maximizes GPU utilization for BGE-M3 with healing contexts dataset
"""

import json
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F
from sentence_transformers import SentenceTransformer


class RTX5090EmbeddingOptimizer:
    """Optimized embedding pipeline for RTX 5090 (32GB VRAM, sm_120)"""

    def __init__(
        self,
        model_name: str = "BAAI/bge-m3",
        seed_path: str = r"C:\AgenticEmbeddings\seed_packs\healing_contexts\5d94b5b12ec92312d0240be9984ff92b9478f74ed6f1335511a202c5351520d9",
        device: str = "cuda",
        batch_size: int = 128,  # Optimized for 32GB VRAM
        use_fp16: bool = True,  # Half precision for 2x speedup
        normalize_embeddings: bool = True,
    ):
        """
        Initialize optimizer with RTX 5090-specific settings

        Args:
            model_name: HuggingFace model identifier
            seed_path: Path to healing contexts seed pack
            device: 'cuda' for GPU, 'cpu' for fallback
            batch_size: Larger batches for RTX 5090's 32GB VRAM
            use_fp16: Enable half-precision (faster, less memory)
            normalize_embeddings: L2 normalize for cosine similarity
        """
        self.device = device
        self.batch_size = batch_size
        self.use_fp16 = use_fp16
        self.normalize_embeddings = normalize_embeddings
        self.seed_path = Path(seed_path)

        print("Initializing RTX 5090 optimizer...")
        print(f"Device: {device}")
        print(f"Batch size: {batch_size}")
        print(f"FP16: {use_fp16}")

        # Load model with optimizations
        self.model = self._load_optimized_model(model_name)

        # Load pre-computed embeddings onto GPU
        self.embeddings, self.embeddings_gpu, self.metadata = self._load_seed_embeddings()

        # GPU memory stats
        if torch.cuda.is_available():
            self._print_gpu_stats()

    def _load_optimized_model(self, model_name: str) -> SentenceTransformer:
        """Load model with RTX 5090 optimizations"""
        model = SentenceTransformer(model_name, device=self.device)

        # Enable half precision for 2x speedup on RTX 5090
        if self.use_fp16 and self.device == "cuda":
            model = model.half()
            print("✓ FP16 (half precision) enabled")

        # Enable CUDA optimizations
        if self.device == "cuda":
            torch.backends.cudnn.benchmark = True
            torch.backends.cuda.matmul.allow_tf32 = True
            torch.backends.cudnn.allow_tf32 = True
            print("✓ TF32 and cuDNN optimizations enabled")

        return model

    def _load_seed_embeddings(self) -> tuple[np.ndarray, list[dict]]:
        """Load pre-computed healing contexts embeddings"""
        embeddings_file = self.seed_path / "embeddings.f32"
        metadata_file = self.seed_path / "row_index.jsonl"

        print(f"Loading seed embeddings from {embeddings_file}...")

        # Load embeddings
        embeddings = np.fromfile(embeddings_file, dtype=np.float32)
        embeddings = embeddings.reshape(-1, 1024)

        # Load metadata
        metadata = []
        with open(metadata_file) as f:
            for line in f:
                metadata.append(json.loads(line))

        # Verify counts match
        if len(embeddings) != len(metadata):
            print(f"Warning: {len(embeddings):,} embeddings but {len(metadata):,} metadata entries")
            min_count = min(len(embeddings), len(metadata))
            embeddings = embeddings[:min_count]
            metadata = metadata[:min_count]

        # Move to GPU as FP16 tensor for fast matmul (~800MB VRAM)
        embeddings_gpu = torch.from_numpy(embeddings).half().to(self.device)
        # Pre-normalize for cosine similarity via dot product
        embeddings_gpu = F.normalize(embeddings_gpu, p=2, dim=1)

        print(
            f"✓ Loaded {len(embeddings):,} embeddings → GPU ({embeddings_gpu.element_size() * embeddings_gpu.nelement() / 1024**3:.2f} GB VRAM)"
        )
        return embeddings, embeddings_gpu, metadata

    def _print_gpu_stats(self):
        """Print GPU memory statistics"""
        if torch.cuda.is_available():
            gpu_name = torch.cuda.get_device_name(0)
            total_mem = torch.cuda.get_device_properties(0).total_memory / 1024**3
            allocated = torch.cuda.memory_allocated(0) / 1024**3
            reserved = torch.cuda.memory_reserved(0) / 1024**3

            print(f"\nGPU: {gpu_name}")
            print(f"Total VRAM: {total_mem:.1f} GB")
            print(f"Allocated: {allocated:.2f} GB")
            print(f"Reserved: {reserved:.2f} GB")
            print(f"Available: {total_mem - reserved:.2f} GB\n")

    def encode_batch(self, texts: list[str], show_progress: bool = True) -> np.ndarray:
        """
        Encode texts with RTX 5090 optimizations

        Args:
            texts: List of text strings to encode
            show_progress: Show progress bar

        Returns:
            numpy array of embeddings (N, 1024)
        """
        return self.model.encode(
            texts,
            batch_size=self.batch_size,
            show_progress_bar=show_progress,
            normalize_embeddings=self.normalize_embeddings,
            convert_to_numpy=True,
        )

    def search(self, query: str, top_k: int = 5, return_scores: bool = True) -> list[dict]:
        """
        Search healing contexts with GPU-accelerated similarity

        Args:
            query: Search query text
            top_k: Number of results to return
            return_scores: Include similarity scores

        Returns:
            List of matches with metadata and scores
        """
        # Encode query
        start = time.time()
        query_embedding = self.model.encode(
            query, normalize_embeddings=self.normalize_embeddings, convert_to_numpy=True
        )
        encode_time = time.time() - start

        # GPU-native similarity search via matmul (pre-normalized = cosine sim)
        start = time.time()
        q_tensor = torch.from_numpy(query_embedding).half().to(self.device)
        q_tensor = F.normalize(q_tensor.unsqueeze(0), p=2, dim=1)
        similarities = torch.matmul(q_tensor, self.embeddings_gpu.T).squeeze(0).cpu().numpy()
        search_time = time.time() - start

        # Get top K
        top_indices = np.argsort(similarities)[-top_k:][::-1]

        results = []
        for idx in top_indices:
            result = {
                "index": int(idx),
                "metadata": self.metadata[idx],
                "score": float(similarities[idx]) if return_scores else None,
            }
            results.append(result)

        if return_scores:
            print(f"Query encode: {encode_time * 1000:.1f}ms | Search: {search_time * 1000:.1f}ms")

        return results

    def batch_search(self, queries: list[str], top_k: int = 5) -> list[list[dict]]:
        """
        Batch search multiple queries (GPU optimized)

        Args:
            queries: List of query strings
            top_k: Number of results per query

        Returns:
            List of result lists (one per query)
        """
        print(f"Encoding {len(queries)} queries in batch...")
        start = time.time()

        # Batch encode all queries
        query_embeddings = self.encode_batch(queries, show_progress=True)
        encode_time = time.time() - start

        # GPU-native batch similarity via matmul
        start = time.time()
        q_tensor = torch.from_numpy(query_embeddings).half().to(self.device)
        q_tensor = F.normalize(q_tensor, p=2, dim=1)
        similarities = torch.matmul(q_tensor, self.embeddings_gpu.T).cpu().numpy()
        search_time = time.time() - start

        # Get top K for each query
        all_results = []
        for i, query_sims in enumerate(similarities):
            top_indices = np.argsort(query_sims)[-top_k:][::-1]
            results = [
                {"index": int(idx), "metadata": self.metadata[idx], "score": float(query_sims[idx])}
                for idx in top_indices
            ]
            all_results.append(results)

        total_time = encode_time + search_time
        per_query = total_time / len(queries)

        print(f"Batch encode: {encode_time:.2f}s | Search: {search_time:.2f}s")
        print(f"Total: {total_time:.2f}s ({per_query * 1000:.1f}ms per query)")

        return all_results

    def benchmark(self, num_queries: int = 100):
        """Run performance benchmark on RTX 5090"""
        print(f"\n{'=' * 60}")
        print(f"RTX 5090 BENCHMARK - {num_queries} queries")
        print(f"{'=' * 60}\n")

        # Generate test queries
        test_queries = [
            f"Healing context {i}: system recovery and fault tolerance" for i in range(num_queries)
        ]

        # Single query benchmark
        print("1. Single Query Performance:")
        single_start = time.time()
        for query in test_queries[:10]:
            self.search(query, top_k=5, return_scores=False)
        single_time = (time.time() - single_start) / 10
        print(f"   Average: {single_time * 1000:.1f}ms per query\n")

        # Batch query benchmark
        print("2. Batch Query Performance:")
        batch_start = time.time()
        self.batch_search(test_queries, top_k=5)
        batch_time = (time.time() - batch_start) / num_queries
        print(f"   Average: {batch_time * 1000:.1f}ms per query\n")

        # Speedup
        speedup = single_time / batch_time
        print(f"3. Batch Speedup: {speedup:.1f}x faster\n")

        # Throughput
        throughput = 1.0 / batch_time
        print(f"4. Throughput: {throughput:.0f} queries/second\n")

        # GPU utilization
        if torch.cuda.is_available():
            self._print_gpu_stats()

        print(f"{'=' * 60}\n")


def main():
    """Demo RTX 5090 optimized embedding pipeline"""

    # Initialize optimizer
    optimizer = RTX5090EmbeddingOptimizer(
        batch_size=128,  # Large batches for 32GB VRAM
        use_fp16=True,  # Half precision for 2x speedup
        normalize_embeddings=True,
    )

    # Example queries
    test_queries = [
        "system recovery after critical failure",
        "auto-healing mechanisms for microservices",
        "escalation procedures for system outages",
        "context restoration after service disruption",
        "fault tolerance in distributed systems",
    ]

    print("\n" + "=" * 60)
    print("SINGLE QUERY EXAMPLES")
    print("=" * 60 + "\n")

    for query in test_queries[:3]:
        print(f"Query: {query}")
        results = optimizer.search(query, top_k=3)
        for i, result in enumerate(results, 1):
            print(f"  {i}. Score: {result['score']:.4f} | Trace: {result['metadata']['trace_id']}")
        print()

    print("\n" + "=" * 60)
    print("BATCH QUERY EXAMPLE")
    print("=" * 60 + "\n")

    batch_results = optimizer.batch_search(test_queries, top_k=3)
    print(f"Processed {len(batch_results)} queries in batch\n")

    # Run benchmark
    optimizer.benchmark(num_queries=100)

    print("\n✅ RTX 5090 optimization complete!")
    print("   - FP16 enabled: 2x faster inference")
    print("   - Large batches: 128 queries at once")
    print("   - TF32 matmul: Hardware acceleration")
    print("   - Expected: 500-1000 queries/second")


if __name__ == "__main__":
    main()
