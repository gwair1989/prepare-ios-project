# Validation record

Checked on 2026-10-19, on macOS. This record covers the renamed skill package and its installation compatibility.

| Check | Result |
| --- | --- |
| Portable SKILL.md metadata and Codex UI prompt | Passed; name is `prepare-ios-project` |
| Package validation | Passed: Markdown targets, Python syntax, example JSON, executable helper permissions |
| Read-only probe fixture | Passed: project path with spaces, shared scheme, CLAUDE symlink, ignored dependencies, staged/unstaged preservation and identical rerun |
| Bundled harness tests | 9 passed: ownership/cleanup, process lock contention, failed commands, timeout cleanup, fingerprint, runtime selection and tool downloads |
| Codex CLI 0.163.0 discovery | `skills/list` returned `prepare-ios-project`, user scope, enabled; previous name absent |
| Claude Code 2.1.289 discovery | Initialization returned the user command `prepare-ios-project` through the shared directory link |

Both clients used one real skill directory. Claude Code discovery enabled the user settings source, disabled MCP loading for the check and sent only an initialization control request. Codex likewise received initialization and skill-list requests. No model task or project preparation was started by these discovery checks.

Reproduce the package and harness checks from the repository root:

```sh
python3 scripts/validate.py
python3 -m unittest discover -s assets/harness/scripts/tests -v
```

Client discovery proves that the installed versions recognize the skill. A complete preparation run in an iOS project, a simulator build/test and a cloud CI run were not performed for this packaging change. Future behavior checks should use the [acceptance scenarios](references/acceptance.md) and record their own evidence.
