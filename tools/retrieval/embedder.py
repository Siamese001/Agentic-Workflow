"""Embedding runtime for the retrieval service."""

from __future__ import annotations

import logging
import os
from typing import Any

from tools.mcp.mcp_deferred_loader import DeferredLoader

from .vector_config import (
    ALLOW_MODEL_DOWNLOAD,
    DEFAULT_EMBEDDING_MODEL,
    EMBEDDING_ENCODE_TIMEOUT,
    EMBEDDING_QUEUE_WAIT_TIMEOUT,
    KNOWN_MODEL_DIMS,
    MODEL_LOAD_TIMEOUT,
    VECTOR_DB_DEVICE,
)
from .vector_errors import VectorUnavailableError

logger = logging.getLogger("vector_service")


class EmbeddingRuntime:
    """Owns model lifecycle and embedding calls for retrieval workloads."""

    def __init__(
        self,
        *,
        model_name: str = DEFAULT_EMBEDDING_MODEL,
        allow_model_download: bool = ALLOW_MODEL_DOWNLOAD,
        model_load_timeout: float = MODEL_LOAD_TIMEOUT,
        queue_wait_timeout: float = EMBEDDING_QUEUE_WAIT_TIMEOUT,
        encode_timeout: float = EMBEDDING_ENCODE_TIMEOUT,
        model_override: Any | None = None,
        device: str = VECTOR_DB_DEVICE,
    ) -> None:
        self.model_name = model_name
        self.allow_model_download = allow_model_download
        self.model_load_timeout = model_load_timeout
        self.queue_wait_timeout = queue_wait_timeout
        self.encode_timeout = encode_timeout
        self._model_override = model_override
        self.device = device
        self._loader = DeferredLoader(
            "embedding-model",
            self._load_model,
            timeout=self.model_load_timeout,
        )

    @property
    def model_override(self) -> Any | None:
        return self._model_override

    @model_override.setter
    def model_override(self, value: Any | None) -> None:
        self._model_override = value

    def is_loaded(self) -> bool:
        return self._model_override is not None or self._loader.is_loaded()

    def is_loading(self) -> bool:
        if self._model_override is not None:
            return False
        return self._loader.is_loading()

    def ensure_ready(self) -> Any:
        if self._model_override is not None:
            return self._model_override
        model = self._loader.get(wait_timeout=self.model_load_timeout)
        if model is None:
            if self._loader.is_loading():
                raise VectorUnavailableError(
                    "Embedding model is still initializing. Retry shortly and check stderr for DEFERRED_LOAD logs."
                )
            raise VectorUnavailableError("Embedding model is unavailable.")
        return model

    def get_dimension(self) -> int | None:
        if not self.is_loaded():
            return None
        model = self.ensure_ready()
        get_dim = getattr(model, "get_sentence_embedding_dimension", None)
        if callable(get_dim):
            try:
                return int(get_dim())
            except (TypeError, ValueError):
                return None
        return KNOWN_MODEL_DIMS.get(self.model_name)

    def encode(self, texts: list[str], *, batch_size: int | None = None) -> Any:
        if not texts:
            raise VectorUnavailableError("No texts supplied for embedding.")

        if self._model_override is not None:
            kwargs: dict[str, Any] = {}
            if batch_size is not None:
                kwargs["batch_size"] = batch_size
            return self._model_override.encode(texts, **kwargs)

        def _run_encode(model: Any) -> Any:
            kwargs: dict[str, Any] = {}
            if batch_size is not None:
                kwargs["batch_size"] = batch_size
            return model.encode(texts, **kwargs)

        try:
            return self._loader.call_serialized(
                _run_encode,
                wait_timeout=self.model_load_timeout,
                call_timeout=self.encode_timeout,
                queue_wait_timeout=self.queue_wait_timeout,
                op_name="embedding-encode",
            )
        except TimeoutError as exc:
            raise VectorUnavailableError(
                f"embedding-encode timed out after {self.encode_timeout:.1f}s"
            ) from exc
        except RuntimeError as exc:
            msg = str(exc)
            if "still loading" in msg or "unavailable" in msg or "could not start" in msg:
                raise VectorUnavailableError(msg) from exc
            raise

    def _apply_fp16_if_cuda(self, model: Any) -> None:
        """Convert model to fp16 when device is cuda; log outcome."""
        if self.device != "cuda":
            return
        try:
            model.half()
            logger.info(
                "MODEL_FP16: model=%r converted to fp16 on device=%r",
                self.model_name,
                self.device,
            )
        except (AttributeError, RuntimeError) as exc:
            logger.warning(
                "MODEL_FP16_SKIP: fp16 unavailable for model=%r — %s",
                self.model_name,
                exc,
            )

    def _load_model(self) -> Any:
        _old_tqdm_disable = os.environ.get("TQDM_DISABLE")
        os.environ["TQDM_DISABLE"] = "1"
        try:
            from sentence_transformers import SentenceTransformer
        finally:
            if _old_tqdm_disable is None:
                os.environ.pop("TQDM_DISABLE", None)
            else:
                os.environ["TQDM_DISABLE"] = _old_tqdm_disable

        if not self.allow_model_download:
            os.environ["HF_HUB_OFFLINE"] = "1"

        import time

        t0 = time.monotonic()
        try:
            model = SentenceTransformer(self.model_name, device=self.device, local_files_only=True)
            self._apply_fp16_if_cuda(model)
            logger.info(
                "MODEL_LOAD_CACHE: model=%r loaded from local cache in %.2fs",
                self.model_name,
                time.monotonic() - t0,
            )
            return model
        except (OSError, ValueError):
            if not self.allow_model_download:
                logger.error(
                    "MODEL_LOAD_BLOCKED: model=%r not in local cache and VECTOR_DB_ALLOW_MODEL_DOWNLOAD=0",
                    self.model_name,
                )
                raise RuntimeError(
                    f"model {self.model_name!r} not in local cache; "
                    "set VECTOR_DB_ALLOW_MODEL_DOWNLOAD=1 to allow online download"
                )
            logger.warning(
                "MODEL_LOAD_ONLINE: model=%r not in local cache — downloading from HuggingFace",
                self.model_name,
            )
            model = SentenceTransformer(self.model_name, device=self.device)
            self._apply_fp16_if_cuda(model)
            logger.info(
                "MODEL_LOAD_ONLINE: model=%r download complete in %.2fs",
                self.model_name,
                time.monotonic() - t0,
            )
            return model
