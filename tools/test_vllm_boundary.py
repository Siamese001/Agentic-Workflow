import os
import subprocess
import sys
import urllib.request

sys.path.insert(0, r"C:\Git\Agentic-Workflow")

MODEL_NAME = "Qwen/Qwen2.5-14B-Instruct-AWQ"


def _probe(url):
    try:
        urllib.request.urlopen(url + "/models", timeout=3)  # noqa: S310
        return True
    except Exception:
        return False


def resolve_base_url():
    if _probe("http://localhost:8000/v1"):
        return "http://localhost:8000/v1"
    # Fallback: resolve WSL2 IP
    result = subprocess.run(
        ["wsl", "-d", "Ubuntu-24.04", "--", "hostname", "-I"], capture_output=True, text=True, timeout=10
    )
    wsl_ip = result.stdout.strip().split()[0]
    url = f"http://{wsl_ip}:8000/v1"
    if _probe(url):
        return url
    raise RuntimeError(f"vLLM server not reachable at localhost or {wsl_ip}:8000")


base_url = resolve_base_url()
print(f"Connecting to: {base_url}")
os.environ["VLLM_BASE_URL"] = base_url
os.environ["VLLM_MODEL_NAME"] = MODEL_NAME

from tools.vllm_boundary_client import generate_proposal

config = {
    "routing_version": 1,
    "temperature": 0,
    "top_p": 1,
}

result = generate_proposal("What is 2+2? Answer in one word.", config)
print("text:          ", result["text"])
print("proposal_hash: ", result["proposal_hash"])
print("routing_ver:   ", result["routing_version"])
print("config_hash:   ", result["config_hash"])
print("\nSUCCESS: boundary client connected to Qwen2.5-14B-Instruct-AWQ via vLLM")
