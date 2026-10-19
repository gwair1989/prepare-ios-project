import importlib.util
import multiprocessing
from pathlib import Path
import tempfile
import time
import unittest
from unittest.mock import patch
import subprocess
import os
import sys


spec = importlib.util.spec_from_file_location("agent", Path(__file__).parents[1] / "agent.py")
agent = importlib.util.module_from_spec(spec)
spec.loader.exec_module(agent)


def hold_slot(path, ready):
    with agent.build_slot(Path(path), 2, {"owner": "child"}):
        ready.set()
        time.sleep(30)


class CoordinationTests(unittest.TestCase):
    def test_second_process_waits_and_crash_releases_slot(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "slot"
            context = multiprocessing.get_context("fork")
            ready = context.Event()
            process = context.Process(target=hold_slot, args=(str(path), ready))
            process.start()
            try:
                self.assertTrue(ready.wait(3))
                with self.assertRaises(agent.CheckFailed):
                    with agent.build_slot(path, 0.1, {"owner": "contender"}):
                        self.fail("A second process entered the occupied slot")
                process.terminate()
                process.join(3)
                with agent.build_slot(path, 1, {"owner": "next"}):
                    self.assertIn('"next"', path.read_text())
            finally:
                if process.is_alive():
                    process.kill()
                process.join()

    def test_runtime_selection_honors_minimum_and_explicit_version(self):
        runtimes = [
            {"identifier": "com.apple.CoreSimulator.SimRuntime.iOS-18-5", "version": "18.5", "isAvailable": True},
            {"identifier": "com.apple.CoreSimulator.SimRuntime.iOS-27-0", "version": "27.0", "isAvailable": True},
            {"identifier": "com.apple.CoreSimulator.SimRuntime.iOS-99-0", "version": "99.0", "isAvailable": False},
        ]
        self.assertEqual(agent.choose_runtime(runtimes, "18.0")["version"], "27.0")
        self.assertEqual(agent.choose_runtime(runtimes, "18.0", "18.5")["version"], "18.5")
        with self.assertRaises(agent.CheckFailed):
            agent.choose_runtime(runtimes, "27.0", "18.5")

    def test_failed_command_keeps_failure_and_raw_log(self):
        with tempfile.TemporaryDirectory() as directory:
            runner = agent.Runner.__new__(agent.Runner)
            runner.root = Path(directory)
            runner.output = Path(directory)
            runner.config = {"command_timeout_seconds": 5}
            runner.report = {"commands": []}
            with self.assertRaises(agent.CheckFailed):
                runner.run("failure", ["/bin/sh", "-c", "echo deliberate-failure; exit 7"])
            self.assertEqual(runner.report["commands"][0]["exit_code"], 7)
            self.assertIn("deliberate-failure", (Path(directory) / "failure.log").read_text())

    def test_cleanup_only_uses_owned_uuid(self):
        runner = agent.Runner.__new__(agent.Runner)
        runner.simulator = "EF420D33-9E28-4B7B-9F62-EE2C4BA93DC2"
        runner.report = {}
        with patch.object(agent.subprocess, "run", return_value=subprocess.CompletedProcess([], 0)) as run:
            runner.cleanup()
        self.assertEqual([call.args[0] for call in run.call_args_list], [
            ["xcrun", "simctl", "shutdown", runner.simulator],
            ["xcrun", "simctl", "delete", runner.simulator],
        ])
        runner.simulator = None
        with patch.object(agent.subprocess, "run") as run:
            runner.cleanup()
        run.assert_not_called()

    def test_cleanup_failure_is_not_silently_ignored(self):
        runner = agent.Runner.__new__(agent.Runner)
        runner.simulator = "EF420D33-9E28-4B7B-9F62-EE2C4BA93DC2"
        runner.report = {}
        with patch.object(agent.subprocess, "run", return_value=subprocess.CompletedProcess([], 1)):
            with self.assertRaises(agent.CheckFailed):
                runner.cleanup()

    def test_timeout_records_command_and_kills_surviving_child(self):
        with tempfile.TemporaryDirectory() as directory:
            runner = agent.Runner.__new__(agent.Runner)
            runner.root = runner.output = Path(directory)
            runner.config = {"command_timeout_seconds": 1}
            runner.report = {"commands": []}
            child_code = "import signal,time; signal.signal(signal.SIGTERM, signal.SIG_IGN); print('ready',flush=True); time.sleep(30)"
            parent_code = (
                "import subprocess,sys,time,pathlib; "
                f"p=subprocess.Popen([sys.executable,'-c',{child_code!r}],stdout=subprocess.PIPE,text=True); "
                "p.stdout.readline(); pathlib.Path('child.pid').write_text(str(p.pid)); time.sleep(30)"
            )
            try:
                with self.assertRaises(subprocess.TimeoutExpired):
                    runner.run("timeout", [sys.executable, "-c", parent_code])
                self.assertEqual(runner.report["commands"][0]["status"], "timed_out")
                child = int((Path(directory) / "child.pid").read_text())
                deadline = time.monotonic() + 3
                while time.monotonic() < deadline:
                    state = subprocess.run(["ps", "-o", "stat=", "-p", str(child)], capture_output=True, text=True)
                    if not state.stdout.strip() or state.stdout.strip().startswith("Z"):
                        break
                    time.sleep(0.1)
                else:
                    self.fail("A child survived timeout cleanup")
            finally:
                pidfile = Path(directory) / "child.pid"
                if pidfile.exists():
                    try:
                        os.kill(int(pidfile.read_text()), 9)
                    except ProcessLookupError:
                        pass

    def test_fingerprint_detects_plist_and_xcconfig_changes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            subprocess.run(["git", "init", "-q", str(root)], check=True)
            for name in ("Info.plist", "Debug.xcconfig"):
                path = root / name
                path.write_text("first")
                before = agent.source_fingerprint(root)
                path.write_text("second")
                self.assertNotEqual(before, agent.source_fingerprint(root))


if __name__ == "__main__":
    unittest.main()
