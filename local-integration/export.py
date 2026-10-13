#!/usr/bin/env python3
"""Export the reviewed selection to a NEW directory; never update a consumer."""

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def sha(data):
    return hashlib.sha256(data).hexdigest()


def export(destination, root=ROOT):
    config_dir = root / "local-integration"
    config = json.loads((config_dir / "selection.json").read_text())
    overrides = json.loads((config_dir / "overrides.json").read_text())
    policy = (config_dir / "POLICY.md").read_bytes()
    selected = config["skills"]
    for name, spec in selected.items():
        if not set(spec["requires"]).issubset(selected):
            raise ValueError(f"Missing dependency for {name}")
    actual = {}
    files = {}
    for name, spec in selected.items():
        source = root / spec["path"]
        if source.is_symlink() or not source.is_dir():
            raise ValueError(f"Missing or linked skill: {name}")
        for path in sorted(source.rglob("*")):
            if path.is_symlink():
                raise ValueError(f"Symlink not allowed: {path}")
            if path.is_file():
                data = path.read_bytes()
                actual[str(path.relative_to(root))] = sha(data)
                files[str(Path(name) / path.relative_to(source))] = data
    if actual != config["source_sha256"]:
        raise ValueError("Selected upstream files changed; review and refresh selection.json before export")
    for rule in overrides:
        path = rule["path"]
        text = files[path].decode()
        if not rule["before"] or text.count(rule["before"]) != 1:
            raise ValueError(f"Override must match exactly once: {path}: {rule['before']!r}")
        files[path] = text.replace(rule["before"], rule["after"], 1).encode()
    for name in selected:
        path = f"{name}/SKILL.md"
        front, body = files[path].decode().split("\n---\n", 1)
        if not front.startswith("---\n") or f"name: {name}\n" not in front + "\n":
            raise ValueError(f"Invalid skill metadata: {name}")
        if "disable-model-invocation:" in front:
            raise ValueError(f"Implicit invocation disabled: {name}")
        if "allow_implicit_invocation: false" in files[f"{name}/agents/openai.yaml"].decode():
            raise ValueError(f"Codex implicit invocation disabled: {name}")
        notice = "\nRead [LOCAL-INTEGRATION.md](LOCAL-INTEGRATION.md) first. Its integration contract overrides conflicting upstream defaults.\n"
        files[path] = (front + "\n---\n" + notice + body).encode()
        files[f"{name}/LOCAL-INTEGRATION.md"] = policy
    license_path = root / "LICENSE"
    if license_path.is_file():
        files["LICENSE"] = license_path.read_bytes()
    manifest = {
        "upstream": config["upstream"], "fork": config["fork"],
        "source_commit": config["source_commit"], "skills": selected,
        "integration_sha256": {
            name: sha((config_dir / name).read_bytes())
            for name in ("selection.json", "overrides.json", "POLICY.md", "export.py")
        },
        "files_sha256": {name: sha(data) for name, data in sorted(files.items())},
    }
    destination = Path(destination).absolute()
    if destination.exists() or destination.is_symlink():
        raise FileExistsError(f"Refusing to overwrite {destination}")
    # Validate everything before creating output; remove partial output on I/O failure.
    destination.mkdir(parents=True)
    try:
        for name, data in files.items():
            target = destination / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        (destination / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    except Exception:
        shutil.rmtree(destination)
        raise
    return manifest


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", nargs="?", help="New export directory; omit to validate only")
    args = parser.parse_args()
    if args.destination:
        export(args.destination)
        print(f"Exported 5 selected skills to {args.destination}")
    else:
        with tempfile.TemporaryDirectory(prefix="matt-validate-") as temp:
            export(Path(temp) / "bundle")
        print("Selected skills and overrides validated")
