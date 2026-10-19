# Reproducible iOS commands and resource ownership

## Discovery and configuration

Inspect the project/workspace, effective scheme, shared scheme file, test targets, test plan, deployment minimum, package lockfiles and Xcode version. Do not equate a Tests directory with a runnable test target. Do not infer architecture from imports alone.

Filesystem-synchronized Xcode groups can include documentation or directory markers as resources. If retaining empty directories with markers, exclude those markers from target membership; repeated filenames can cause duplicate bundle outputs. For app-hosted unit tests inspect the framework's official example: linking the same SwiftPM product independently into app and test targets may change dynamic linkage or duplicate symbols. Verify the actual test build instead of assuming the app build covers it.

The optional `assets/harness/scripts/agent.py` provides a Python-standard-library runner. Read its supported manifest before copying it, then generate `config/agent-build.json` from the actual repository. It expects project or workspace, scheme and scheme_path, configuration, minimum_ios, test_targets, source_directories, simulator_device_type, xcode_jobs, lock/command timeouts and required tool versions. `spec_command` is optional and must match the selected SDD workflow; `sdd: openspec` enables targeted change checking. Tests for the runner are bundled beside it.

Provide doctor/bootstrap/build/test/verify entry points. Keep a single implementation used by local work and CI. If an existing runner already provides the required behavior, adapt it instead of introducing a competing one.

The example manifest is illustrative: replace every Example path and inspect device/runtime availability. For a workspace replace `project` with `workspace`; retain the actual `scheme_path` even when the shared scheme lives inside a project. The runner requires a Git checkout and records `unborn` when there is no HEAD; never make a commit merely to satisfy a template. It runs SwiftFormat and SwiftLint with repository-owned configuration, and Python tests from `scripts/tests`. Generate those configs and entry points from existing conventions. Optional `install_tools.py` and `tool-downloads.json` provide pinned Apple Silicon downloads; verify release metadata when changing versions. Export `.agent-local/tools/bin` in the entry points before invoking installed tools. Ignore `.agent-local/`.

Choose an available simulator device type and runtime during setup/run. Commit a portable selector; record actual UDIDs only in local state. Compile-only builds can target a generic simulator and do not need Simulator.app.

## Isolation

- Separate worktree/branch per independent editing task. If operating in a dirty authorized checkout, preserve its working state rather than pretending a new HEAD checkout is equivalent.
- Namespace DerivedData and writable SwiftPM checkouts by checkout and toolchain; concurrent writers need separate paths or a lock.
- Give logs, xcresult and other artifacts a unique run ID.
- Create a dedicated simulator or use a real atomic lease. A name or a text note is not a lease. A global active MCP profile may be shared; verify scope before relying on it.
- Serialize or bound heavy jobs with a machine-level mechanism shared by participating wrappers. Python `fcntl.flock` works on macOS; keep its inode rather than deleting the lock file after release. Kernel locks release after crashes. Set a bounded waiting policy and avoid killing an owner.
- Clean only recorded owned IDs/paths. Never use shutdown/erase-all, global process killing or global DerivedData deletion.
- Preserve evidence after failures. A SIGKILL or power failure cannot run cleanup; leave ownership metadata and require inspection before removing an orphan.

The default bundled runner permits one heavy invocation across participating repositories for the same user. Scripts outside the protocol are not controlled. Isolated storage is necessary even if execution is serialized.

## Tests and build output

Use behavior tests at stable boundaries. For TCA, test state transitions/effects with injected clients. Isolate defaults suites, files, clocks, UUIDs and service doubles. Add a small UI smoke only for a meaningful agreed user flow. Swift Testing parallelism inside one process is distinct from Xcode workers and separate agents.

Keep raw xcodebuild output and its actual status. xcbeautify is presentation; it cannot turn a failed build green. Save xcresult, inspect a nonzero executed test count and report skipped/failed required tests. Record the tested revision and a fingerprint when the checkout is dirty. Re-run if relevant inputs change during verification.

Preserve signing configuration. Command-local simulator signing overrides are sufficient for ordinary simulator checks. If a locked dependency's macro requires trust, investigate the exact error and use an explicit documented, command-scoped policy; avoid changing global Xcode validation preferences.

## CI

Use only the selected provider. Pin a documented Xcode image compatible with the project format. Install required missing tooling in an owned directory with pinned versions and integrity checks; reuse compatible installed binaries. Call the same repository verify command and upload raw logs/xcresult even on failure. Only label a file JUnit when valid JUnit XML is actually produced.

Preparing CI YAML is different from connecting a repository, provisioning credentials, publishing an app or observing a remote run. Report this distinction accurately.
