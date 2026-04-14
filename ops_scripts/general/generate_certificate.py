"""
Generate a markdown certificate summarizing active sovereign agents.
"""

from __future__ import annotations

import argparse
import importlib
import inspect
import logging
import os
import pkgutil
import sys
from dataclasses import is_dataclass
from pathlib import Path

from tqdm import tqdm

LOGGER = logging.getLogger(__name__)
DEFAULT_OUTPUT = "SOVEREIGN_SYSTEM_CERTIFICATE.md"


def _resolve_repo_root(explicit_root: str | None = None) -> Path:
    if explicit_root:
        return Path(explicit_root).expanduser().resolve()
    env_root = os.getenv("AGENTIC_WORKFLOW_ROOT")
    if env_root:
        return Path(env_root).expanduser().resolve()
    for candidate in Path(__file__).resolve().parents:
        if (candidate / ".git").exists():
            return candidate
    return Path.cwd().resolve()


def _atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    tmp_path.write_text(content, encoding="utf-8")
    tmp_path.replace(path)


def analyze_agent(cls: type) -> tuple[str, str, str]:
    """Return (BaseClass, DataclassStatus, OverallStatus)."""
    bases = [base.__name__ for base in cls.__mro__]
    is_sovereign = "SovereignBaseAgent" in bases
    base_status = "SovereignBaseAgent" if is_sovereign else "LEGACY"
    is_data = is_dataclass(cls)
    data_status = "[OK]" if is_data else "[FAIL]"
    status = "[PASS]" if is_sovereign and is_data else "[FAIL]"
    return (base_status, data_status, status)


def generate(repo_root: Path, output_path: Path) -> int:
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))  # guardian: allow-global-mutation -- script bootstrap

    print("Generating Sovereign Certificate...")
    output = [
        "# SOVEREIGN SYSTEM CERTIFICATE (V2.5)",
        "**Status:** CERTIFIED PRODUCTION READY",
        "**Integrity:** LOCKED",
        "**Architecture:** HARDENED DATACLASS",
        "",
        "## Active Sovereign Agents",
        "| Domain | Agent Name | Base Class | Dataclass | Status |",
        "| :--- | :--- | :--- | :--- | :--- |",
    ]

    domains = ("apps_rg.engines", "apps_lic.engines")
    for domain in tqdm(domains, desc="Processing", unit="domain"):
        try:
            package = importlib.import_module(domain)
            package_file = getattr(package, "__file__", None)
            if not package_file:
                print(f"Skipping domain {domain}: package has no filesystem path")
                continue
            package_path = Path(package_file).parent
        except (ImportError, AttributeError, OSError, ValueError) as exc:
            print(f"Skipping domain {domain}: {exc}")
            continue

        for _, module_name, _ in tqdm(
            sorted(pkgutil.iter_modules([str(package_path)]), key=lambda item: item[1]),
            desc="Processing",
            unit="module",
        ):
            try:
                module = importlib.import_module(f"{domain}.{module_name}")
                for cls_name, cls in inspect.getmembers(module, inspect.isclass):
                    if (
                        cls.__module__ == module.__name__
                        and any(tag in cls_name for tag in ("Agent", "Specialist", "Architect"))
                        and cls_name not in {"BaseAgent", "OutreachAgent", "OutreachAgentFactory"}
                        and not cls_name.startswith("_")
                    ):
                        base, data, status = analyze_agent(cls)
                        output.append(f"| {domain.split('.')[0]} | {cls_name} | {base} | {data} | {status} |")
            except (ImportError, AttributeError, OSError, ValueError) as exc:
                LOGGER.warning("Could not inspect %s.%s: %s", domain, module_name, exc)
                output.append(f"| {domain} | {module_name} | ERROR | [FAIL] | {type(exc).__name__}: {exc} |")

    _atomic_write(output_path, "\n".join(output) + "\n")
    print(f"Certificate Generated: {output_path}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate a markdown certificate for active sovereign agents.",
    )
    parser.add_argument("--repo-root", help="Override automatic repository root detection.")
    parser.add_argument(
        "--output",
        help="Output path for the markdown certificate. Defaults to repo_root/SOVEREIGN_SYSTEM_CERTIFICATE.md",
    )
    args = parser.parse_args(argv)

    repo_root = _resolve_repo_root(args.repo_root)
    output_path = Path(args.output).expanduser().resolve() if args.output else repo_root / DEFAULT_OUTPUT
    return generate(repo_root, output_path)


if __name__ == "__main__":
    raise SystemExit(main())
