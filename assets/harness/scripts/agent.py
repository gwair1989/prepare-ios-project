#!/usr/bin/env python3
"""Reproducible iOS checks; resources belong to a checkout and one invocation."""

import argparse
import contextlib
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import sys
import time
import uuid


ROOT = Path(__file__).resolve().parents[1]


class CheckFailed(RuntimeError):
    pass


@contextlib.contextmanager
def build_slot(path, timeout, owner):
    """Kernel releases the lock after crashes; never unlink the lock inode."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a+") as handle:
        deadline = time.monotonic() + timeout
        waiting = False
        while True:
            try:
                fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except BlockingIOError:
                if not waiting:
                    print("Waiting for the machine build/test slot…", flush=True)
                    waiting = True
                if time.monotonic() >= deadline:
                    raise CheckFailed("Build/test slot timed out; its owner was not interrupted")
                time.sleep(0.2)
        try:
            handle.seek(0)
            handle.truncate()
            json.dump(owner, handle)
            handle.flush()
            yield
        finally:
            fcntl.flock(handle, fcntl.LOCK_UN)


def capture(args, cwd=ROOT):
    return subprocess.check_output(args, cwd=cwd, text=True, stderr=subprocess.PIPE).strip()


def version_tuple(value):
    return tuple(int(x) for x in value.split("."))


def choose_runtime(runtimes, minimum, requested=None):
    available = [r for r in runtimes if r.get("isAvailable")
                 and ".iOS-" in r["identifier"]
                 and version_tuple(r["version"]) >= version_tuple(minimum)]
    if requested:
        available = [r for r in available if requested in (r["identifier"], r["version"])]
    if not available:
        raise CheckFailed(f"No available iOS runtime >= {minimum} matching {requested or 'latest'}")
    return max(available, key=lambda r: version_tuple(r["version"]))


def source_fingerprint(root):
    digest = hashlib.sha256()
    paths = capture(["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"], root)
    for name in sorted(set(paths.split("\0"))):
        p = root / name
        if name and p.suffix.lower() != ".md":
            digest.update(name.encode())
            digest.update(p.read_bytes() if p.is_file() else b"MISSING")
    return digest.hexdigest()


class Runner:
    def __init__(self, root=ROOT):
        self.root = Path(root).resolve()
        self.config = json.loads((self.root / "config/agent-build.json").read_text())
        self.run_id = time.strftime("%Y%m%d-%H%M%S") + "-" + uuid.uuid4().hex[:10]
        self.output = self.root / ".agent-local/runs" / self.run_id
        self.output.mkdir(parents=True)
        xcode = capture(["xcodebuild", "-version"])
        cache_key = hashlib.sha256(xcode.encode()).hexdigest()[:12]
        self.cache = self.root / ".agent-local/cache" / cache_key
        self.cache.mkdir(parents=True, exist_ok=True)
        self.simulator = None
        try:
            revision = capture(["git", "rev-parse", "--verify", "HEAD"], self.root)
        except subprocess.CalledProcessError:
            revision = "unborn"
        self.report = {
            "run_id": self.run_id, "checkout": str(self.root), "pid": os.getpid(),
            "revision": revision,
            "source_fingerprint": source_fingerprint(self.root), "xcode": xcode,
            "commands": [], "status": "running",
        }

    def save(self):
        (self.output / "manifest.json").write_text(json.dumps(self.report, indent=2) + "\n")

    def run(self, name, args, timeout=None):
        log = self.output / f"{name}.log"
        print(f"START {name}\nLOG {log}", flush=True)
        started = time.monotonic()
        with log.open("w") as stream:
            process = subprocess.Popen(args, cwd=self.root, stdout=stream,
                                       stderr=subprocess.STDOUT, start_new_session=True)
            outcome = "completed"
            try:
                code = process.wait(timeout=timeout or self.config["command_timeout_seconds"])
            except BaseException as error:
                outcome = "timed_out" if isinstance(error, subprocess.TimeoutExpired) else "interrupted"
                with contextlib.suppress(ProcessLookupError):
                    os.killpg(process.pid, signal.SIGTERM)
                with contextlib.suppress(subprocess.TimeoutExpired):
                    process.wait(timeout=10)
                # A parent can exit before its children; still kill our remaining group.
                with contextlib.suppress(ProcessLookupError):
                    os.killpg(process.pid, signal.SIGKILL)
                process.wait()
                raise
            finally:
                self.report["commands"].append({"name": name, "argv": args,
                    "exit_code": process.returncode, "status": outcome,
                    "seconds": round(time.monotonic() - started, 2), "log": str(log)})
                self.save()
        if args[0] == "xcodebuild" and shutil.which("xcbeautify"):
            with log.open() as source, (self.output / f"{name}.readable.log").open("w") as target:
                # Presentation is separate; it cannot replace the producer's exit status.
                subprocess.run(["xcbeautify"], stdin=source, stdout=target,
                               stderr=subprocess.STDOUT, check=False)
        print(f"END {name}: exit {code}", flush=True)
        if code:
            lines = log.read_text(errors="replace").splitlines()
            useful = [l for l in lines if re.search(r"error:|failed|Error|must be enabled", l)]
            print("\n".join((useful or lines[-30:])[-40:]), flush=True)
            raise CheckFailed(f"{name} failed ({code}); see {log}")

    def xcode(self, action):
        cfg = self.config
        container = ["-workspace", cfg["workspace"]] if cfg.get("workspace") else ["-project", cfg["project"]]
        args = ["xcodebuild", *container, "-scheme", cfg["scheme"],
                "-configuration", cfg["configuration"], "-derivedDataPath", str(self.cache / "DerivedData"),
                "-clonedSourcePackagesDirPath", str(self.cache / "SourcePackages"),
                "-onlyUsePackageVersionsFromResolvedFile"]
        if cfg.get("trust_locked_macros"):
            args.append("-skipMacroValidation")
        if action == "resolve":
            self.run("resolve", args + ["-resolvePackageDependencies"])
            return
        args += ["-jobs", str(cfg["xcode_jobs"]), "CODE_SIGNING_ALLOWED=NO"]
        if action == "build":
            self.run("build", args + ["-destination", "generic/platform=iOS Simulator", "build"])
            return
        if not cfg.get("test_targets"):
            raise CheckFailed("No configured test targets; test success cannot be claimed")
        runtimes = json.loads(capture(["xcrun", "simctl", "list", "runtimes", "-j"]))["runtimes"]
        runtime = choose_runtime(runtimes, cfg["minimum_ios"], os.getenv("IOS_TEST_RUNTIME"))
        candidate = capture(["xcrun", "simctl", "create", "Agent-" + self.run_id,
                             cfg["simulator_device_type"], runtime["identifier"]])
        try:
            uuid.UUID(candidate)
        except ValueError:
            raise CheckFailed("simctl did not return a simulator UUID")
        self.simulator = candidate
        self.report["simulator"] = {"id": self.simulator, "runtime": runtime["version"], "owned": True}
        self.save()
        self.run("simulator-boot", ["xcrun", "simctl", "bootstatus", self.simulator, "-b"], timeout=240)
        result = self.output / "tests.xcresult"
        args += ["-destination", "platform=iOS Simulator,id=" + self.simulator,
                 "-destination-timeout", "120", "-resultBundlePath", str(result),
                 "-parallel-testing-enabled", "NO",
                 "-maximum-concurrent-test-simulator-destinations", "1", "test"]
        args += ["-only-testing:" + target for target in cfg["test_targets"]]
        self.run("test", args)
        summary = json.loads(capture(["xcrun", "xcresulttool", "get", "test-results", "summary",
                                      "--path", str(result), "--format", "json"]))
        (self.output / "test-summary.json").write_text(json.dumps(summary, indent=2) + "\n")
        self.report["test_summary"] = summary
        total = summary.get("totalTestCount", 0)
        if not total or summary.get("failedTests", 0) or summary.get("skippedTests", 0):
            raise CheckFailed("Required tests were absent, failed, or skipped; inspect test-summary.json")
        print(f"TESTS: {total} total; {summary.get('passedTests')} passed", flush=True)

    def verify(self):
        dirs = self.config["source_directories"]
        self.run("format-check", ["swiftformat", *dirs, "--lint"])
        self.run("lint", ["swiftlint", "lint", "--strict", "--quiet", "--no-cache", "--config", ".swiftlint.yml"])
        self.run("harness-tests", [sys.executable, "-m", "unittest", "discover", "-s", "scripts/tests", "-v"])
        if self.config.get("spec_command"):
            self.run("specs", self.config["spec_command"])
        change = os.getenv("OPENSPEC_CHANGE")
        if change and self.config.get("sdd") == "openspec":
            self.run("change", ["scripts/spec", "validate", change, "--type", "change", "--strict", "--json", "--no-interactive"])
        self.xcode("build")
        self.xcode("test")

    def cleanup(self):
        if not self.simulator:
            return
        # This UUID was returned by our own successful create; never use 'all'.
        for operation in ("shutdown", "delete"):
            result = subprocess.run(["xcrun", "simctl", operation, self.simulator],
                                    capture_output=True, text=True, timeout=60)
            self.report.setdefault("cleanup", {})[operation] = result.returncode
        if self.report["cleanup"]["delete"]:
            raise CheckFailed(f"Could not remove owned simulator {self.simulator}")


def doctor():
    cfg = json.loads((ROOT / "config/agent-build.json").read_text())
    missing = []
    for name in ("xcodebuild", "xcrun", *cfg.get("prerequisites", []), *cfg["tools"]):
        path = shutil.which(name)
        print(f"{name}: {path or 'MISSING'}")
        if not path:
            missing.append(name)
    for name, expected in cfg["tools"].items():
        if shutil.which(name):
            actual = capture([name, "version" if name == "swiftlint" else "--version"])
            print(f"{name} version: {actual} (expected {expected})")
            if actual != expected:
                missing.append(f"{name} version mismatch")
    for name in (cfg.get("workspace") or cfg["project"], cfg["scheme_path"]):
        if not (ROOT / name).exists():
            missing.append(name)
    print(capture(["xcodebuild", "-version"]))
    if missing:
        raise CheckFailed("Prerequisites: " + ", ".join(missing))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("doctor", "resolve", "build", "test", "verify"))
    action = parser.parse_args().action
    if action == "doctor":
        doctor()
        return
    runner = Runner()
    coordination = Path(os.environ.get("IOS_AGENT_COORDINATION_DIR", Path.home() / "Library/Caches/ios-agent-harness"))
    print(f"RUN {runner.output}", flush=True)
    try:
        with build_slot(coordination / "build.lock", runner.config["lock_timeout_seconds"],
                        {"pid": os.getpid(), "run_id": runner.run_id, "checkout": str(ROOT)}):
            try:
                if action == "verify":
                    runner.verify()
                else:
                    runner.xcode(action)
                if source_fingerprint(ROOT) != runner.report["source_fingerprint"]:
                    raise CheckFailed("Inputs changed during verification; rerun after edits finish")
                runner.report["status"] = "passed"
            finally:
                runner.cleanup()
    except BaseException as error:
        runner.report["status"] = "failed"
        runner.report["error"] = str(error)
        raise
    finally:
        runner.save()
        print(f"REPORT {runner.output / 'manifest.json'}", flush=True)


if __name__ == "__main__":
    signal.signal(signal.SIGTERM, lambda *_: sys.exit(143))
    try:
        main()
    except (CheckFailed, subprocess.SubprocessError) as error:
        print(str(error), file=sys.stderr)
        sys.exit(1)
