"""Fail closed when privileged workflows depend on mutable remote Actions code."""

from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
WORKFLOWS = ROOT / ".github" / "workflows"
ACTION = re.compile(r"^\s*-?\s*uses:\s*([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)@([^\s#]+)", re.M)
IMMUTABLE_SHA = re.compile(r"[0-9a-f]{40}\Z")


class WorkflowSupplyChainTests(unittest.TestCase):
    def test_all_external_actions_are_commit_pinned(self) -> None:
        for path in sorted(WORKFLOWS.glob("*.yml")):
            content = path.read_text(encoding="utf-8")
            with self.subTest(workflow=path.name):
                actions = ACTION.findall(content)
                self.assertTrue(actions, "Expected at least one external action")
                for repository, revision in actions:
                    self.assertRegex(
                        revision,
                        IMMUTABLE_SHA,
                        f"{path.name}: {repository}@{revision} is mutable",
                    )

    def test_release_write_permission_is_job_scoped(self) -> None:
        release = (WORKFLOWS / "release.yml").read_text(encoding="utf-8")
        self.assertRegex(release, r"(?m)^permissions:\n  contents: read\s*$")
        self.assertRegex(
            release,
            r"(?m)^  create-release:\n    permissions:\n      contents: write\s*$",
        )

    def test_pypi_token_permission_is_publish_job_scoped(self) -> None:
        pypi = (WORKFLOWS / "pypi.yml").read_text(encoding="utf-8")
        self.assertNotRegex(pypi, r"(?m)^permissions:\n\s+id-token: write")
        self.assertIn("\n  publish:\n", pypi)
        publish_job = pypi.split("\n  publish:\n", 1)[1]
        self.assertIn("\n    permissions:\n      id-token: write\n", publish_job)
        self.assertEqual(pypi.count("id-token: write"), 1)


if __name__ == "__main__":
    unittest.main()
