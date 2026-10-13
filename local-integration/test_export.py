import importlib.util
import json
from pathlib import Path
import re
import shutil
import tempfile
import unittest

spec = importlib.util.spec_from_file_location("bundle_export", Path(__file__).with_name("export.py"))
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class BundleTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "source"
        shutil.copytree(module.ROOT / "local-integration", self.root / "local-integration", ignore=shutil.ignore_patterns("__pycache__"))
        config = json.loads((self.root / "local-integration/selection.json").read_text())
        for item in config["skills"].values():
            shutil.copytree(module.ROOT / item["path"], self.root / item["path"])
        if (module.ROOT / "LICENSE").exists():
            shutil.copyfile(module.ROOT / "LICENSE", self.root / "LICENSE")
        self.dest = Path(self.temp.name) / "bundle"

    def test_complete_bundle_and_local_links(self):
        manifest = module.export(self.dest, self.root)
        self.assertEqual(len(manifest["skills"]), 5)
        for name, digest in manifest["files_sha256"].items():
            self.assertEqual(module.sha((self.dest / name).read_bytes()), digest)
        for path in self.dest.rglob("*.md"):
            # Templates show hypothetical project links inside fenced examples.
            prose = re.sub(r"```.*?```", "", path.read_text(), flags=re.S)
            for target in re.findall(r"\]\(([^)]+)\)", prose):
                if "://" not in target and not target.startswith("#"):
                    self.assertTrue((path.parent / target.split("#")[0]).exists(), (path, target))
        for name in manifest["skills"]:
            self.assertIn("LOCAL-INTEGRATION.md", (self.dest / name / "SKILL.md").read_text())

    def test_preserve_existing_destination(self):
        self.dest.mkdir()
        marker = self.dest / "user-file"
        marker.write_text("keep")
        with self.assertRaises(FileExistsError):
            module.export(self.dest, self.root)
        self.assertEqual(marker.read_text(), "keep")

    def test_upstream_drift_fails_before_write(self):
        path = self.root / "skills/engineering/codebase-design/DEEPENING.md"
        path.write_text(path.read_text() + "\nChanged upstream\n")
        with self.assertRaisesRegex(ValueError, "upstream files changed"):
            module.export(self.dest, self.root)
        self.assertFalse(self.dest.exists())

    def test_missing_dependency_fails(self):
        path = self.root / "local-integration/selection.json"
        config = json.loads(path.read_text())
        del config["skills"]["grilling"]
        path.write_text(json.dumps(config))
        with self.assertRaisesRegex(ValueError, "Missing dependency"):
            module.export(self.dest, self.root)

    def test_stale_override_fails(self):
        path = self.root / "local-integration/overrides.json"
        rules = json.loads(path.read_text())
        rules[0]["before"] = "upstream text that no longer exists"
        path.write_text(json.dumps(rules))
        with self.assertRaisesRegex(ValueError, "exactly once"):
            module.export(self.dest, self.root)
        self.assertFalse(self.dest.exists())


if __name__ == "__main__":
    unittest.main()
