import ast
import importlib
import inspect
import os
from dataclasses import MISSING, fields, is_dataclass
from pathlib import Path
from typing import Any, get_args, get_origin

import pytest

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.domain.CoreIntegrityVerifier import CoreIntegrityVerifier
from agentic_core.utils.ssot_discovery import get_agent_paths


def _project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _safe_patch_core_integrity(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        CoreIntegrityVerifier,
        "verify_core_integrity",
        classmethod(lambda cls: True),
        raising=True,
    )


def _module_name_from_path(project_root: Path, file_path: Path) -> str:
    rel = file_path.relative_to(project_root).with_suffix("")
    return ".".join(rel.parts)


def _import_discovered_modules(project_root: Path) -> tuple[list[Any], list[tuple[str, BaseException]]]:
    modules: list[Any] = []
    errors: list[tuple[str, BaseException]] = []

    # SSOT discovery returns agent file paths only (canonical registry)
    agent_paths = get_agent_paths(
        project_root=project_root,
        exclude_patterns=["tests/", "archives/", ".backup/"],
    )

    for path in agent_paths:
        if path.suffix != ".py":
            continue

        mod_name = _module_name_from_path(project_root, path)
        try:
            modules.append(importlib.import_module(mod_name))
        except Exception as e:
            # Phase 2 covers import safety; Phase 1 is MRO-focused.
            errors.append((mod_name, e))

    return modules, errors


def _iter_defined_classes(module: Any) -> list[type]:
    classes: list[type] = []
    for obj in vars(module).values():
        if inspect.isclass(obj) and getattr(obj, "__module__", None) == module.__name__:
            classes.append(obj)
    return classes


def _iter_sba_subclasses(modules: list[Any]) -> list[type[SovereignBaseAgent]]:
    out: list[type[SovereignBaseAgent]] = []
    for module in modules:
        for cls in _iter_defined_classes(module):
            if cls is SovereignBaseAgent:
                continue
            if issubclass(cls, SovereignBaseAgent):
                out.append(cls)
    return out


def _placeholder_for_annotation(annotation: Any) -> Any:
    if annotation is inspect._empty:
        return None

    origin = get_origin(annotation)
    if origin is None:
        if annotation in (str,):
            return "test"
        if annotation in (int,):
            return 0
        if annotation in (float,):
            return 0.0
        if annotation in (bool,):
            return False
        if annotation is Path:
            return Path.cwd()
        return None

    if origin in (list,):
        return []
    if origin in (dict,):
        return {}
    if origin in (set,):
        return set()

    if origin is tuple:
        return ()

    # Optional[T] / Union
    args = get_args(annotation)
    if args and type(None) in args:
        return None

    return None


def _fuzz_dataclass_init_kwargs(cls: type) -> dict[str, Any]:
    kwargs: dict[str, Any] = {}

    for f in fields(cls):
        if not f.init:
            continue

        has_default = f.default is not MISSING
        has_factory = f.default_factory is not MISSING  # type: ignore[attr-defined]

        if has_default or has_factory:
            continue

        kwargs[f.name] = _placeholder_for_annotation(f.type)

    return kwargs


def test_redundant_mixin_check():
    project_root = _project_root()
    modules, _errors = _import_discovered_modules(project_root)

    subclasses = _iter_sba_subclasses(modules)

    failures: list[str] = []
    for cls in subclasses:
        parent = next(
            (
                b
                for b in cls.__bases__
                if inspect.isclass(b)
                and issubclass(b, SovereignBaseAgent)
                and b is not SovereignBaseAgent
            ),
            None,
        )
        if parent is None:
            continue

        parent_mro = set(parent.mro())
        for base in cls.__bases__:
            if base is parent or base is object:
                continue

            if base in parent_mro:
                failures.append(
                    f"{cls.__module__}.{cls.__name__} redundantly re-inherits {base.__name__} "
                    f"which is already present in parent MRO ({parent.__name__})."
                )

    assert not failures, "\n".join(failures)


def test_dataclass_initialization_fuzz(monkeypatch: pytest.MonkeyPatch):
    _safe_patch_core_integrity(monkeypatch)

    project_root = _project_root()
    modules, _errors = _import_discovered_modules(project_root)
    subclasses = _iter_sba_subclasses(modules)

    failures: list[str] = []

    for cls in subclasses:
        if not is_dataclass(cls):
            continue

        kwargs = _fuzz_dataclass_init_kwargs(cls)
        try:
            cls(**kwargs)
        except Exception as e:
            failures.append(
                f"Dataclass init failed for {cls.__module__}.{cls.__name__} with kwargs={kwargs}: "
                f"{type(e).__name__}: {e}"
            )

    assert not failures, "\n".join(failures)


def test_diamond_resolution_synthetic():
    calls: dict[str, int] = {}

    class _Base:
        def __init__(self) -> None:
            calls["_Base"] = calls.get("_Base", 0) + 1
            super().__init__()

    class _Left(_Base):
        def __init__(self) -> None:
            calls["_Left"] = calls.get("_Left", 0) + 1
            super().__init__()

    class _Right(_Base):
        def __init__(self) -> None:
            calls["_Right"] = calls.get("_Right", 0) + 1
            super().__init__()

    class _Diamond(_Left, _Right):
        def __init__(self) -> None:
            calls["_Diamond"] = calls.get("_Diamond", 0) + 1
            super().__init__()

    _Diamond()

    assert calls.get("_Diamond") == 1
    assert calls.get("_Left") == 1
    assert calls.get("_Right") == 1
    assert calls.get("_Base") == 1, (
        "Diamond resolution failure: shared base __init__ executed more than once. "
        f"Observed calls={calls}"
    )


def test_mixin_naming_convention_and_inheritance():
    project_root = _project_root()

    failures: list[str] = []

    for root, dirs, files in os.walk(project_root):
        rel_root = os.path.relpath(root, project_root)

        # Skip non-source / historical folders
        if rel_root.startswith("archives") or rel_root.startswith("tests") or rel_root.startswith(".git"):
            dirs[:] = []
            continue

        for file in files:
            if not file.endswith(".py"):
                continue

            if "mixin" not in file.lower():
                continue

            path = Path(root) / file
            try:
                tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            except SyntaxError as e:
                failures.append(f"Cannot parse {path}: SyntaxError: {e}")
                continue

            for node in tree.body:
                if not isinstance(node, ast.ClassDef):
                    continue

                class_name = node.name

                if "mixin" in class_name.lower() and not class_name.endswith("Mixin"):
                    failures.append(
                        f"Mixin naming violation in {path}: class '{class_name}' contains 'mixin' "
                        "but does not end with 'Mixin'."
                    )

    # Second check: any *Mixin class must not inherit SovereignBaseAgent directly.
    # We only enforce this for classes that can be imported without errors.
    modules, _errors = _import_discovered_modules(project_root)
    for module in modules:
        for cls in _iter_defined_classes(module):
            if not cls.__name__.endswith("Mixin"):
                continue
            if issubclass(cls, SovereignBaseAgent):
                failures.append(
                    f"Mixin inheritance violation: {cls.__module__}.{cls.__name__} inherits "
                    "SovereignBaseAgent directly (risk of circularity)."
                )

    assert not failures, "\n".join(failures)


def test_abc_implementation_for_concrete_agents():
    project_root = _project_root()
    modules, _errors = _import_discovered_modules(project_root)
    subclasses = _iter_sba_subclasses(modules)

    failures: list[str] = []
    for cls in subclasses:
        if inspect.isabstract(cls):
            continue

        abstract_methods = getattr(cls, "__abstractmethods__", set())
        if abstract_methods:
            failures.append(
                f"Concrete agent {cls.__module__}.{cls.__name__} has unimplemented abstract methods: "
                f"{sorted(abstract_methods)}"
            )

    assert not failures, "\n".join(failures)


def test_sovereign_seal_integrity(monkeypatch: pytest.MonkeyPatch):
    _safe_patch_core_integrity(monkeypatch)

    sealed_instances: list[tuple[str, Any]] = []

    # Prefer known sealed agents if present.
    try:
        from apps_lic.engines.HOP1ProfileAnalysisAgent import HOP1ProfileAnalysisAgent

        sealed_instances.append(("apps_lic.engines.HOP1ProfileAnalysisAgent", HOP1ProfileAnalysisAgent()))
    except Exception:
        pass

    try:
        from apps_lic.engines.HOP2ResearchAgent import HOP2ResearchAgent

        sealed_instances.append(("apps_lic.engines.HOP2ResearchAgent", HOP2ResearchAgent()))
    except Exception:
        pass

    assert sealed_instances, (
        "No sealed agent instances could be created for verification. "
        "Expected at least one agent with a post-init sovereign seal."
    )

    failures: list[str] = []

    for name, agent in sealed_instances:
        if not getattr(agent, "_sealed", False):
            failures.append(f"{name}: _sealed flag not engaged after initialization")
            continue

        try:
            agent._guardian_mutation_probe = "mutation_attempt"
            failures.append(f"{name}: Sovereign seal failed to block new attribute assignment")
        except AttributeError:
            pass

        if hasattr(agent, "config"):
            try:
                agent.config = None
                failures.append(f"{name}: Sovereign seal failed to block existing attribute mutation")
            except AttributeError:
                pass

    assert not failures, "\n".join(failures)
