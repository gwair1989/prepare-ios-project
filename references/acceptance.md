# Behavioral acceptance scenarios

Use isolated temporary repositories and fake tool processes for infrastructure checks. Use an owned simulator for a real end-to-end project check. Do not test against another agent's working files.

1. **New skeleton:** architecture is unspecified. The workflow asks with a recommendation and alternatives, preserves the source folders, then produces commands that actually build and test the agreed example.
2. **Existing decisions:** a documented architecture, CI provider and SDD choice are reused. No repeated questionnaire or unrequested framework migration occurs.
3. **Dirty repository:** staged and unstaged edits remain intact. No automatic reset, stash, force checkout, commit or move to an incomplete HEAD worktree occurs.
4. **Existing instructions:** unique CLAUDE content survives consolidation. The resulting relative link resolves after the repository directory is moved.
5. **Missing tools:** optional MCP absence uses a suitable available CLI; mandatory toolchain absence is reported without a false pass. No unrelated global installation happens.
6. **Concurrency:** a contender cannot enter an occupied heavy-job lock; termination releases it; logs, writable build paths and simulator ownership do not collide.
7. **Failure:** a failing producer retains its exit status through formatting; zero tests cannot become a successful test run; timeout cleans owned child processes and preserves logs.
8. **Rerun:** preparation with unchanged inputs produces no new semantic diff and preserves manual documentation additions.
9. **SDD completion:** planning-ready is not implementation-done. Archive requires actual evidence; concurrent changes do not overwrite shared specs.
10. **Codex and Claude Code:** each host discovers the same `prepare-ios-project` entry point in its supported skill location. Helpers resolve from the skill directory even when the project path contains spaces. No host-specific UI metadata, MCP name or question tool is required to execute the workflow. A discovery check confirms loading only; it is not an end-to-end iOS preparation test.

The frontmatter validator checks package shape only. These scenarios assess the behavior that matters to a user; tailor the executed subset to the change and record what was actually exercised.
