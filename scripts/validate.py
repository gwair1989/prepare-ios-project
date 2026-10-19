#!/usr/bin/env python3
"""Validate this portable skill and exercise read-only discovery in a fixture."""
import ast
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
NAME = "prepare-ios-project"
IGNORED = {".git", "__pycache__", ".agent-local", ".venv", ".pytest_cache"}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def run(args, cwd):
    result = subprocess.run(args, cwd=cwd, capture_output=True, text=True, timeout=45)
    require(result.returncode == 0, f"{args[0]} failed: {result.stderr[:600]}")
    return result.stdout


def snapshot(root):
    return {
        str(p.relative_to(root)): (
            os.readlink(p) if p.is_symlink() else hashlib.sha256(p.read_bytes()).hexdigest()
        )
        for p in root.rglob("*")
        if p.is_file() and ".git" not in p.relative_to(root).parts
    }


def check_probe():
    with tempfile.TemporaryDirectory(prefix="ios-skill-validation-") as temporary:
        project = Path(temporary) / "Existing App With Spaces"
        scheme = project / "Example.xcodeproj/xcshareddata/xcschemes/Example.xcscheme"
        scheme.parent.mkdir(parents=True)
        scheme.write_text('<Scheme version="1.7"/>\n')
        (project / "AGENTS.md").write_text("Keep the existing folders and decisions.\n")
        (project / "CLAUDE.md").symlink_to("AGENTS.md")
        (project / "README.md").write_text("Manual project documentation.\n")
        (project / "Sources").mkdir()
        source = project / "Sources/Example.swift"
        source.write_text("// Staged user work.\n")
        run(["git", "init", "--quiet"], project)
        run(["git", "add", "Sources/Example.swift"], project)
        source.write_text("// Staged user work.\n// Additional unstaged work.\n")
        (project / "node_modules").mkdir()
        (project / "node_modules/ignored.md").write_text("Ignored dependency context.\n")
        before = snapshot(project)
        index = (project / ".git/index").read_bytes()
        status = run(["git", "status", "--porcelain"], project)
        results = [
            json.loads(run([sys.executable, str(ROOT / "scripts/probe.py"), str(project)], project))
            for _ in range(2)
        ]
        require(results[0] == results[1], "Probe rerun changed its report")
        report = results[0]
        require(report["containers"] == ["Example.xcodeproj"], "Project was not discovered")
        require(report["shared_schemes"] == [str(scheme.relative_to(project))], "Scheme missing")
        require(report["instruction_files"]["CLAUDE.md"]["symlink"], "CLAUDE symlink not detected")
        require(not any("node_modules" in x for x in report["context_files"]), "Probe traversed dependencies")
        require(snapshot(project) == before, "Probe changed fixture files")
        require((project / ".git/index").read_bytes() == index, "Probe changed the Git index")
        require(run(["git", "status", "--porcelain"], project) == status, "Probe changed Git status")


def main():
    skill = (ROOT / "SKILL.md").read_text()
    frontmatter = re.match(r"\A---\n(.*?)\n---\n", skill, re.S)
    require(frontmatter is not None, "Missing SKILL.md frontmatter")
    # This package deliberately uses only plain scalar name/description fields.
    fields = dict(line.split(": ", 1) for line in frontmatter[1].splitlines())
    require(set(fields) == {"name", "description"}, "Unexpected frontmatter shape")
    require(fields["name"] == NAME, "Skill name mismatch")
    require(0 < len(fields["description"]) <= 1024, "Invalid description length")
    require("Codex" in fields["description"] and "Claude Code" in fields["description"], "Host description missing")
    ui = (ROOT / "agents/openai.yaml").read_text()
    require(f"${NAME}" in ui, "Codex prompt uses a different skill name")
    files = [p for p in ROOT.rglob("*") if p.is_file() and not set(p.relative_to(ROOT).parts) & IGNORED]
    links = 0
    for path in files:
        if path.suffix == ".py":
            ast.parse(path.read_text(), filename=str(path))
        if path.suffix == ".json":
            json.loads(path.read_text())
        if path.suffix != ".md":
            continue
        text = re.sub(r"```.*?```", "", path.read_text(), flags=re.S)
        for raw in re.findall(r"\[[^\]\n]+\]\(([^)]+)\)", text):
            target = raw.strip().strip("<>")
            if urlsplit(target).scheme or target.startswith("#"):
                continue
            links += 1
            require((path.parent / unquote(target.split("#")[0])).exists(), f"Broken link in {path.name}: {target}")
    for relative in ["scripts/probe.py", "assets/harness/scripts/agent.py", "assets/harness/scripts/install_tools.py"]:
        require(os.access(ROOT / relative, os.X_OK), f"Missing executable bit: {relative}")
    check_probe()
    print(json.dumps({"result": "PASS", "name": NAME, "files_checked": len(files), "local_links": links,
                      "fixture": "paths with spaces; staged/unstaged preservation; symlink; read-only rerun"}, indent=2))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, subprocess.TimeoutExpired) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        raise SystemExit(1)
