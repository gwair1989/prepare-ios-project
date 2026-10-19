# prepare-ios-project

A self-contained skill for **Codex** and **Claude Code** that prepares an existing iOS Swift/Xcode project for autonomous agent work and spec-driven development.

It discovers the project and installed tools, preserves your folders and architecture, resolves missing decisions, and sets up instructions, documentation, reproducible commands and isolated verification resources.

## What it prepares

- A practical `README.md`, compact `AGENTS.md`, and relative `CLAUDE.md → AGENTS.md` link after preserving existing instructions.
- An engineering profile and a documentation maintenance workflow.
- Your chosen architecture, SDD workflow and CI provider. Existing decisions are reused; missing architecture and workflow choices are discussed with you.
- Shared schemes, real test targets and repeatable bootstrap/build/test/verify entry points as needed.
- Separate build artifacts and owned simulators, with a machine lock for participating heavy jobs.
- Honest verification evidence, including failures, skipped checks and remaining questions.

The skill adapts to your repository; it does not impose TCA, OpenSpec or a particular CI provider. MCP servers and plugins are optional capabilities. The included probe and runner use Python's standard library.

## Install

### Codex

Clone the repository as a real directory in the personal skills location:

```sh
mkdir -p "$HOME/.agents/skills"
git clone https://github.com/gwair1989/prepare-ios-project.git "$HOME/.agents/skills/prepare-ios-project"
```

Start a new Codex session if the skill is not visible in the current one. In your iOS project's chat:

```text
Use $prepare-ios-project to prepare this project for agent work and SDD.
Preserve the existing folder structure and read our saved decisions first.
```

### Claude Code

For Claude Code alone, clone into its personal skills location:

```sh
mkdir -p "$HOME/.claude/skills"
git clone https://github.com/gwair1989/prepare-ios-project.git "$HOME/.claude/skills/prepare-ios-project"
```

For **both clients on one machine**, use the Codex installation above and expose the same directory to Claude Code:

```sh
mkdir -p "$HOME/.claude/skills"
ln -s "$HOME/.agents/skills/prepare-ios-project" "$HOME/.claude/skills/prepare-ios-project"
```

Choose one Claude Code installation method. These commands assume the destination does not already exist; preserve an existing installation and any local changes before reconciling it. Do not force replacement of another skill directory.

Open Claude Code in your iOS project and run:

```text
/prepare-ios-project Prepare this project for agent work and SDD, preserving its structure.
```

The shared installation keeps one source of truth. `agents/openai.yaml` supplies Codex UI metadata; Claude Code reads the same `SKILL.md` without a separate prompt or plugin. Standard `name` and `description` frontmatter are used, without host-specific dynamic substitutions or permission overrides.

## Workflow

1. Inspect the existing project, instructions, tools and verification gaps.
2. Resolve missing architecture, SDD, product scope and execution choices in short question rounds.
3. Record the change contract using the selected SDD workflow.
4. Prepare documentation and project commands while preserving existing work.
5. Run applicable verification, check resource ownership and record results.
6. Reconcile documentation and hand off the evidence.

Installation does not execute this workflow. Invoke the skill in the target project to start preparation. The agent operates within its session's permissions; discovery of a tool does not prove that the tool can complete an operation.

## Requirements and optional assets

iOS builds require macOS, a suitable Xcode installation and an available runtime for simulator tests. Python 3 is needed for the bundled helpers; the optional runner uses macOS/POSIX facilities. Other requirements depend on the project's selected workflow.

`scripts/probe.py` performs bounded, read-only discovery. The optional runner, tool installer, example manifest and tests are under `assets/harness/`. Their versions and device selector are examples to reconcile with the target environment, not instructions to change an existing deployment target or dependency lockfile.

```sh
python3 /path/to/prepare-ios-project/scripts/probe.py /path/to/ios-project
```

Participating wrappers serialize heavy jobs for the same user and isolate writable paths. They cannot coordinate tools that bypass the wrappers. Preparing CI configuration does not connect accounts or publish an app.

## Maintain and verify this skill

From this repository:

```sh
python3 scripts/validate.py
python3 -m unittest discover -s assets/harness/scripts/tests -v
```

The first command checks portable package metadata, local references, example JSON and a read-only discovery fixture. The second exercises the bundled runner's locking, cleanup and failure behavior. Neither command builds an iOS app or proves an agent can complete a full preparation task.

For updates, inspect `git status` and preserve any local customizations, then use `git pull --ff-only` in the installation. A shared Claude Code link sees the same update.

The [validation record](VALIDATION.md) states which checks and client discovery tests were actually performed.

## Format references

- [Codex skills](https://developers.openai.com/codex/skills)
- [Claude Code skills](https://code.claude.com/docs/en/skills)
- [Agent Skills specification](https://agentskills.io/specification)
- [Claude Code memory and imports](https://code.claude.com/docs/en/memory)

For task instructions, see [SKILL.md](SKILL.md). For behavioral evaluation scenarios, see [references/acceptance.md](references/acceptance.md).

## License

[MIT](LICENSE). Copyright (c) 2026 gwair1989.
