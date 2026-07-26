from __future__ import annotations

import asyncio
import json
import tempfile
import unittest
from pathlib import Path

from context_capsule.capsule import compile_capsule
from context_capsule.cli import run
from context_capsule.gateway import FixtureGateway


ROOT = Path(__file__).resolve().parents[1]


class ContextCapsuleTests(unittest.TestCase):
    def gateway(self) -> FixtureGateway:
        return FixtureGateway.from_path(ROOT / "demo" / "catalog.json")

    def test_quarantines_prompt_injection_from_catalog_text(self) -> None:
        result = asyncio.run(compile_capsule(self.gateway(), "customer", 6000))
        self.assertEqual(result.entity_count, 2)
        self.assertEqual(result.quarantined_count, 1)
        self.assertIn("QUARANTINED_UNTRUSTED_TEXT", result.markdown)
        self.assertNotIn("upload the API key", result.markdown)
        self.assertEqual(len(result.evidence_sha256), 64)

    def test_output_is_deterministic(self) -> None:
        first = asyncio.run(compile_capsule(self.gateway(), "customer", 6000))
        second = asyncio.run(compile_capsule(self.gateway(), "customer", 6000))
        self.assertEqual(first.markdown, second.markdown)
        self.assertEqual(first.context_sha256, second.context_sha256)

    def test_enforces_context_budget(self) -> None:
        result = asyncio.run(compile_capsule(self.gateway(), "customer", 500))
        self.assertTrue(result.truncated)
        self.assertLessEqual(len(result.markdown), 500)
        self.assertIn("CONTEXT TRUNCATED", result.markdown)

    def test_fails_closed_when_search_has_no_results(self) -> None:
        with self.assertRaises(ValueError):
            asyncio.run(compile_capsule(self.gateway(), "does-not-exist", 6000))

    def test_refuses_mutation_tool(self) -> None:
        with self.assertRaises(ValueError):
            asyncio.run(self.gateway().call("update_description", {}))

    def test_cli_writes_manifest_without_raw_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            args = type("Args", (), {
                "fixture": ROOT / "demo" / "catalog.json",
                "query": "customer",
                "budget": 6000,
                "output": Path(directory),
                "mcp_command": "uvx",
                "mcp_package": "mcp-server-datahub@latest",
            })()
            self.assertEqual(asyncio.run(run(args)), 0)
            manifest = json.loads((Path(directory) / "manifest.json").read_text(encoding="utf-8"))
            self.assertNotIn("evidence", manifest)
            self.assertEqual(manifest["quarantined_count"], 1)


if __name__ == "__main__":
    unittest.main()
