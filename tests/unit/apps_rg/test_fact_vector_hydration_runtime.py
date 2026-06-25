from __future__ import annotations

import types
from pathlib import Path
from typing import Any

import pytest

from apps_rg.runtime import fact_vectors_bootstrap as fvhr


class _FakeCuda:
    def __init__(self, available: bool = True) -> None:
        self._available = available

    def is_available(self) -> bool:
        return self._available

    def get_device_name(self, index: int) -> str:
        assert index == 0
        return "Unit Test CUDA"


def _fake_imports(*, cuda_available: bool = True):
    modules: dict[str, Any] = {
        "redis": types.SimpleNamespace(),
        "yaml": types.SimpleNamespace(),
        "chromadb": types.SimpleNamespace(),
        "sentence_transformers": types.SimpleNamespace(),
        "torch": types.SimpleNamespace(cuda=_FakeCuda(cuda_available)),
    }

    def _fake_import_module(name: str) -> Any:
        if name not in modules:
            raise ModuleNotFoundError(name)
        return modules[name]

    return _fake_import_module


def test_hydration_runtime_blocks_missing_dependencies(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    model_dir = tmp_path / "model"
    model_dir.mkdir()

    def _raise_missing(name: str) -> Any:
        raise ModuleNotFoundError(name)

    monkeypatch.setattr(fvhr.importlib, "import_module", _raise_missing)

    receipt = fvhr.validate_fact_vector_hydration_runtime(
        embedding_model_path=str(model_dir),
        raise_on_block=False,
    )

    assert receipt["status"] == "BLOCKED"
    assert "missing_or_blocked_dependency:torch" in receipt["reasons"]
    assert receipt["block_code"] == fvhr.BLOCKED_FACT_VECTOR_HYDRATION_RUNTIME


def test_hydration_env_preparation_is_import_light(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    model_dir = tmp_path / "artifacts" / "models" / "BAAI" / "bge-m3"
    model_dir.mkdir(parents=True)
    (model_dir / "config.json").write_text("{}", encoding="utf-8")
    for name in (
        "AGENTIC_REPO_ROOT",
        "CHROMA_PERSIST_DIR",
        "EMBEDDING_ENABLED",
        "APPS_RG_EMBEDDING_ENABLED",
        "APPS_RG_EMBEDDING_MODEL_PATH",
        "APPS_RG_EMBEDDING_MODEL_NAME",
        "EMBEDDING_MODEL_ID",
    ):
        monkeypatch.delenv(name, raising=False)

    receipt = fvhr.prepare_fact_vector_hydration_env(repo_root=tmp_path)

    assert Path(receipt["chroma_path"]).parts[-3:] == ("data", "cache", "chromadb")
    assert receipt["embedding_enabled"] is True
    assert receipt["embedding_model_path"] == str(model_dir.resolve())
    assert receipt["embedding_model_source"] == "pre_provisioned"
    assert receipt["device"] == "cuda"


def test_hydration_runtime_requires_cuda_and_local_model(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    model_dir = tmp_path / "model"
    model_dir.mkdir()
    monkeypatch.setattr(fvhr.importlib, "import_module", _fake_imports(cuda_available=True))
    monkeypatch.setenv("APPS_RG_HYDRATION_DEVICE", "cuda")

    receipt = fvhr.validate_fact_vector_hydration_runtime(
        embedding_model_path=str(model_dir),
        raise_on_block=False,
    )

    assert receipt["status"] == "PASS"
    assert receipt["torch_cuda_available"] is True
    assert receipt["cuda_device_name"] == "Unit Test CUDA"
    assert receipt["embedding_model_path_present"] is True


def test_hydration_runtime_blocks_cpu_fallback(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    model_dir = tmp_path / "model"
    model_dir.mkdir()
    monkeypatch.setattr(fvhr.importlib, "import_module", _fake_imports(cuda_available=False))
    monkeypatch.setenv("APPS_RG_HYDRATION_DEVICE", "cuda")

    receipt = fvhr.validate_fact_vector_hydration_runtime(
        embedding_model_path=str(model_dir),
        raise_on_block=False,
    )

    assert receipt["status"] == "BLOCKED"
    assert "torch_cuda_unavailable" in receipt["reasons"]


def test_hydration_lock_blocks_concurrent_writer(tmp_path: Path) -> None:
    chroma_dir = tmp_path / "chroma"
    with fvhr.FactVectorHydrationLock(chroma_path=chroma_dir) as first:
        assert first["status"] == "ACQUIRED"
        with pytest.raises(fvhr.FactVectorHydrationRuntimeError) as exc:
            with fvhr.FactVectorHydrationLock(chroma_path=chroma_dir):
                pass
        assert exc.value.receipt["block_code"] == fvhr.BLOCKED_FACT_VECTOR_HYDRATION_LOCK
    assert not (chroma_dir / fvhr.HYDRATION_LOCK_FILENAME).exists()


def test_snapshot_copies_chroma_before_hydration(tmp_path: Path) -> None:
    chroma_dir = tmp_path / "chroma"
    chroma_dir.mkdir()
    (chroma_dir / "chroma.sqlite3").write_text("tiny", encoding="utf-8")
    receipt = fvhr.snapshot_chroma_before_hydration(
        chroma_path=chroma_dir,
        repo_root=tmp_path,
    )

    assert receipt["status"] == "PASS"
    snap = Path(receipt["snapshot_path"])
    assert (snap / "chroma.sqlite3").read_text(encoding="utf-8") == "tiny"
