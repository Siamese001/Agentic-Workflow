import subprocess

result = subprocess.run(
    [
        "wsl",
        "-d",
        "Ubuntu-24.04",
        "--",
        "/root/.vllm_env/bin/python",
        "-c",
        "import torch; "
        "from transformers import AutoModelForCausalLM; "
        "m = AutoModelForCausalLM.from_pretrained('/root/models/Qwen2.5-14B-Instruct', torch_dtype=torch.bfloat16, device_map='cuda'); "
        "free = torch.cuda.mem_get_info()[0]/1024**3; "
        "total = torch.cuda.mem_get_info()[1]/1024**3; "
        "used = total - free; "
        "print(f'Model VRAM used: {used:.2f}GB'); "
        "print(f'Free after load: {free:.2f}GB'); "
        "print(f'Total: {total:.2f}GB')",
    ],
    capture_output=True,
    text=True,
    timeout=120,  # guardian: allow-magic_configuration
)
print(result.stdout)
if result.stderr:
    # just last few lines of stderr for the key numbers
    lines = result.stderr.strip().splitlines()
    for l in lines[-10:]:
        print(l)
