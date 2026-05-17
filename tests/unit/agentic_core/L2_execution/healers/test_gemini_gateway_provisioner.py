"""G6 — Gemini gateway provisioner tests.

Plan ref: ``.windsurf/plans/qwen-confidence-routing-hardening-d4e7b1.md`` G6.
"""

from __future__ import annotations

import asyncio
import os
import unittest
from dataclasses import dataclass

from agentic_core.L2_execution.healers.gemini_gateway_provisioner import (
    ENV_GEMINI_API_KEY_LEGACY,
    ENV_GOOGLE_API_KEY,
    ENV_GEMINI_FLASH_OVERRIDE,
    GeminiGatewayConfig,
    MinimalGeminiGateway,
    provision_router,
)
from agentic_core.L2_execution.healers.healing_router import HealingRouter


@dataclass
class _Req:
    prompt: str = "hi"
    model: str = "gemini-3-flash-preview"
    max_tokens: int = 100


class GeminiConfigFromEnvTest(unittest.TestCase):
    def setUp(self) -> None:
        keys = (
            ENV_GOOGLE_API_KEY,
            ENV_GEMINI_API_KEY_LEGACY,
            ENV_GEMINI_FLASH_OVERRIDE,
        )
        self._saved = {k: os.environ.get(k) for k in keys}
        for k in keys:
            os.environ.pop(k, None)

    def tearDown(self) -> None:
        for k, v in self._saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v

    def test_returns_none_when_api_key_unset(self) -> None:
        self.assertIsNone(GeminiGatewayConfig.from_env())

    def test_returns_config_when_google_api_key_set(self) -> None:
        os.environ[ENV_GOOGLE_API_KEY] = "test-key-xyz"
        cfg = GeminiGatewayConfig.from_env()
        self.assertIsNotNone(cfg)
        self.assertEqual(cfg.api_key, "test-key-xyz")
        self.assertTrue(cfg.flash_model)  # default from model_registry
        self.assertTrue(cfg.pro_model)

    def test_returns_config_when_legacy_gemini_alias_set(self) -> None:
        os.environ[ENV_GEMINI_API_KEY_LEGACY] = "legacy-key"
        cfg = GeminiGatewayConfig.from_env()
        self.assertIsNotNone(cfg)
        self.assertEqual(cfg.api_key, "legacy-key")

    def test_env_override_for_flash_model(self) -> None:
        os.environ[ENV_GOOGLE_API_KEY] = "k"
        os.environ[ENV_GEMINI_FLASH_OVERRIDE] = "gemini-flash-test"
        cfg = GeminiGatewayConfig.from_env()
        self.assertEqual(cfg.flash_model, "gemini-flash-test")

    def test_invalid_timeout_falls_back_to_default(self) -> None:
        os.environ[ENV_GOOGLE_API_KEY] = "k"
        os.environ["GEMINI_TIMEOUT_SECONDS"] = "not-a-number"
        try:
            cfg = GeminiGatewayConfig.from_env()
            self.assertEqual(cfg.timeout_seconds, 60)
        finally:
            del os.environ["GEMINI_TIMEOUT_SECONDS"]

    def test_whitespace_only_key_treated_as_unset(self) -> None:
        os.environ[ENV_GOOGLE_API_KEY] = "   "
        self.assertIsNone(GeminiGatewayConfig.from_env())


class MinimalGeminiGatewayTest(unittest.TestCase):
    def test_returns_error_envelope_when_sdk_missing(self) -> None:
        # The default test environment has no API key configured; even
        # when google.generativeai *is* importable, configuring with an
        # empty key should not crash the gateway. We bypass _load_sdk to
        # simulate the missing-SDK path deterministically.
        gw = MinimalGeminiGateway(
            GeminiGatewayConfig(
                api_key="x",
                flash_model="m",
                pro_model="p",
                timeout_seconds=5,
                max_output_tokens=100,
            )
        )
        gw._load_sdk = lambda: None  # type: ignore[method-assign]
        result = asyncio.run(gw.route_generation(_Req()))
        self.assertIsNone(result.content)
        self.assertEqual(result.error, "gemini_sdk_unavailable")
        self.assertEqual(result.model, "gemini-3-flash-preview")


class ProvisionRouterTest(unittest.TestCase):
    def setUp(self) -> None:
        self._saved_google = os.environ.get(ENV_GOOGLE_API_KEY)
        self._saved_legacy = os.environ.get(ENV_GEMINI_API_KEY_LEGACY)
        os.environ.pop(ENV_GOOGLE_API_KEY, None)
        os.environ.pop(ENV_GEMINI_API_KEY_LEGACY, None)

    def tearDown(self) -> None:
        for k, v in (
            (ENV_GOOGLE_API_KEY, self._saved_google),
            (ENV_GEMINI_API_KEY_LEGACY, self._saved_legacy),
        ):
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v

    def test_provision_returns_false_when_no_api_key(self) -> None:
        router = HealingRouter()
        attached = provision_router(router)
        self.assertFalse(attached)
        self.assertIsNone(getattr(router, "_gemini_gateway", None))

    def test_provision_attaches_gateway_when_key_present(self) -> None:
        os.environ[ENV_GOOGLE_API_KEY] = "test-key"
        router = HealingRouter()
        self.assertTrue(provision_router(router))
        self.assertIsInstance(router._gemini_gateway, MinimalGeminiGateway)
        self.assertEqual(router._gemini_gateway.config.api_key, "test-key")

    def test_provision_with_explicit_config(self) -> None:
        cfg = GeminiGatewayConfig(
            api_key="explicit",
            flash_model="f",
            pro_model="p",
            timeout_seconds=30,
            max_output_tokens=512,
        )
        router = HealingRouter()
        self.assertTrue(provision_router(router, cfg))
        self.assertEqual(router._gemini_gateway.config.api_key, "explicit")


if __name__ == "__main__":
    unittest.main()
