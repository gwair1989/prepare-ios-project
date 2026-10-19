#!/usr/bin/env python3
"""Reuse exact installed versions or install checksum-verified local binaries."""
import hashlib
import io
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import tempfile
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def version(binary, name):
    return subprocess.check_output(
        [str(binary), "version" if name == "swiftlint" else "--version"], text=True
    ).strip()


def verified_binary(payload, expected_hash, name):
    if hashlib.sha256(payload).hexdigest() != expected_hash:
        raise ValueError(f"Checksum mismatch for {name}")
    with zipfile.ZipFile(io.BytesIO(payload)) as archive:
        matches = [i for i in archive.infolist() if not i.is_dir() and Path(i.filename).name == name]
        if len(matches) != 1:
            raise ValueError(f"Expected exactly one {name} executable in release")
        # Select one member by basename; never extract archive paths to the filesystem.
        return archive.read(matches[0])


def main():
    releases = json.loads((ROOT / "config/tool-downloads.json").read_text())
    required = json.loads((ROOT / "config/agent-build.json").read_text())["tools"]
    destination = ROOT / ".agent-local/tools/bin"
    for name, expected in required.items():
        release = releases[name]
        if release["version"] != expected:
            raise ValueError(f"Conflicting version pins for {name}")
        local = destination / name
        existing = local if local.exists() else shutil.which(name)
        if existing and version(existing, name) == expected:
            print(f"Reuse {name} {expected}: {existing}")
            continue
        if platform.system() != "Darwin" or platform.machine() != "arm64":
            raise RuntimeError("Pinned downloads target Apple Silicon macOS; use matching installed tools on other hosts")
        with urllib.request.urlopen(release["url"], timeout=120) as response:
            executable = verified_binary(response.read(), release["sha256"], name)
        destination.mkdir(parents=True, exist_ok=True)
        temporary = None
        try:
            with tempfile.NamedTemporaryFile(dir=destination, delete=False) as handle:
                temporary = Path(handle.name)
                handle.write(executable)
            temporary.chmod(0o755)
            if version(temporary, name) != expected:
                raise ValueError(f"Release version mismatch for {name}")
            os.replace(temporary, local)
            print(f"Installed {name} {expected}: {local}")
        finally:
            if temporary and temporary.exists():
                temporary.unlink()


if __name__ == "__main__":
    main()
