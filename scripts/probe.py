#!/usr/bin/env python3
"""Read-only, bounded discovery for an iOS repository; prints JSON to stdout."""
import argparse
import json
from pathlib import Path
import shutil
import subprocess


def command(args, root):
    try:
        result = subprocess.run(args, cwd=root, text=True, capture_output=True, timeout=30)
    except (OSError, subprocess.TimeoutExpired) as error:
        return {"exit_code": None, "error": str(error)}
    return {"exit_code": result.returncode, "output": result.stdout.strip()[:12000],
            "error": result.stderr.strip()[:2000] if result.returncode else None}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repository")
    root = Path(parser.parse_args().repository).resolve()
    if not root.is_dir():
        parser.error("Repository directory does not exist")
    ignored = {".git", ".agent-local", ".worktrees", "node_modules", "DerivedData", ".build", "Pods"}
    projects, docs, folders, schemes = [], [], [], []
    stack = [(root, 0)]
    while stack:
        directory, depth = stack.pop()
        for entry in sorted(directory.iterdir()):
            if entry.name in ignored or entry.is_symlink():
                continue
            relative = str(entry.relative_to(root))
            if entry.is_dir():
                if entry.suffix in (".xcodeproj", ".xcworkspace"):
                    projects.append(relative)
                if depth < 3:
                    folders.append(relative)
                if depth < 6:
                    stack.append((entry, depth + 1))
            elif entry.suffix == ".xcscheme" and "xcshareddata" in entry.parts:
                schemes.append(relative)
            elif entry.suffix in (".md", ".xctestplan") or entry.name in ("Package.swift", "Package.resolved", "codemagic.yaml", "Makefile"):
                docs.append(relative)
    report = {"root": str(root), "containers": projects, "shared_schemes": schemes,
              "directories": folders, "context_files": docs[:120],
              "tools": {name: shutil.which(name) for name in (
                  "xcodebuild", "xcrun", "swiftformat", "swiftlint", "xcbeautify", "python3",
                  "git", "node", "npm", "openspec", "xcodebuildmcp", "mobilebuildmcp")}}
    report["git"] = command(["git", "status", "--short", "--branch"], root)
    report["instruction_files"] = {}
    for name in ("AGENTS.md", "agent.md", "CLAUDE.md", "README.md"):
        path = root / name
        report["instruction_files"][name] = {
            "exists": path.exists(), "symlink": path.is_symlink(),
            "resolved": str(path.resolve()) if path.is_symlink() else None}
    if report["tools"]["xcodebuild"]:
        report["xcode"] = command(["xcodebuild", "-version"], root)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
