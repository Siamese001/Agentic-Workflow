from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from ops_scripts.ci.check_apps_research_rg_e2e_contract_freeze import (
    CONTRACT_PATH,
    REPO_ROOT,
    validate_contract,
    validate_contract_document,
)


class TestAppsResearchRgE2EContractFreeze(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.document = json.loads((REPO_ROOT / CONTRACT_PATH).read_text(encoding="utf-8"))

    def _errors_for(self, document: dict) -> list[str]:
        return validate_contract_document(copy.deepcopy(document), Path(REPO_ROOT))

    def test_frozen_contract_and_repository_surfaces_pass(self) -> None:
        self.assertEqual(validate_contract(), [])

    def test_product_success_alias_is_rejected(self) -> None:
        document = copy.deepcopy(self.document)
        document["x3_taxonomy"]["product_success_codes"] = ["ALLOW"]

        errors = self._errors_for(document)

        self.assertTrue(
            any("product success must be exactly X3D_ALLOW_FINISH" in error for error in errors),
            errors,
        )

    def test_unknown_transition_is_rejected(self) -> None:
        document = copy.deepcopy(self.document)
        document["stages"][0]["allowed_next"].append("SECOND_AUTHORITY_MODEL")

        errors = self._errors_for(document)

        self.assertTrue(any("unknown allowed_next stages" in error for error in errors), errors)

    def test_current_run_product_entrypoint_cannot_drop_authority_contract(self) -> None:
        document = copy.deepcopy(self.document)
        document["entrypoints"][0]["product_authority"] = False

        errors = self._errors_for(document)

        self.assertTrue(
            any("current-run product path needs product authority" in error for error in errors),
            errors,
        )

    def test_post_boundary_observer_cannot_claim_product_authority(self) -> None:
        document = copy.deepcopy(self.document)
        observer = next(
            row
            for row in document["entrypoints"]
            if row["entrypoint_id"] == "apps_eval_live_adapter"
        )
        observer["product_authority"] = True

        errors = self._errors_for(document)

        self.assertTrue(
            any("non-authority path cannot claim product authority" in error for error in errors),
            errors,
        )

    def test_duplicate_entrypoint_is_rejected(self) -> None:
        document = copy.deepcopy(self.document)
        document["entrypoints"].append(copy.deepcopy(document["entrypoints"][0]))

        errors = self._errors_for(document)

        self.assertTrue(any("duplicate entrypoint IDs" in error for error in errors), errors)


if __name__ == "__main__":
    unittest.main()
