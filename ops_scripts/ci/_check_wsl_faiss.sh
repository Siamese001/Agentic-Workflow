#!/bin/bash
python3 -c "import faiss; print('faiss', faiss.__version__, hasattr(faiss, 'StandardGpuResources'))" 2>&1 || echo "faiss not found in WSL python3"
which python3
pip3 index versions faiss-gpu-cu12 2>&1 | head -3
