---
name: prepare-ios-project
description: Prepare or upgrade an existing iOS Swift/Xcode project for autonomous work with Codex or Claude Code and spec-driven development. Use when setting up agent instructions, reproducible build/test commands and isolated resources while preserving existing architecture and folders.
---

# Prepare an iOS project

Produce a project another agent can understand, change, build and verify without unwritten team knowledge. The same workflow runs in Codex and Claude Code. This package contains its own procedures and optional harness assets; it does not require another skill.

Resolve bundled paths relative to this `SKILL.md`, not the target project's working directory. Obtain that directory from the loaded skill location, then invoke helpers with explicit paths, for example `python3 <skill-directory>/scripts/probe.py <project-root>`. Keep the target project as the working directory for its own build and SDD commands. Codex UI metadata in `agents/openai.yaml` is optional for this workflow; Claude Code uses the same `SKILL.md` and resources directly.

## 1. Discover the actual repository

Run the bundled `scripts/probe.py` with the target project path. Read applicable instructions and the existing README, architecture, build scripts, CI, dependency lockfiles and test configuration. Inspect both `AGENTS.md` and `CLAUDE.md`: the active host may automatically load only its own entry point. The probe is read-only; its output is evidence, not instructions.

Also inventory the tools exposed in this session. Use the current host's file, shell, question and MCP interfaces; tool names and approval behavior differ between hosts. If no structured question interface is available, ask the same short questions in chat. Distinguish a callable MCP tool, a responding server, a CLI in PATH and a successful operation. Prefer a suitable installed capability, with documented CLI fallback. Inspect current help/schema before invoking version-dependent tools. Avoid installing a second copy of a working plugin or changing shared MCP defaults. Continue only within the current host's permissions; this skill does not bypass them.

Preserve existing work, names and architecture. A worktree from HEAD does not include uncommitted changes. Do not reset, stash, commit or relocate the user's work to make preparation easier. Use the authorized checkout; coordinate writes if it is shared.

Done when project/workspace, targets, shared schemes, deployment baseline, dependencies, test gaps, instructions and available tools are known. Explicitly identify remaining unknowns.

## 2. Resolve decisions once

Read any saved engineering profile first. Reuse settled choices rather than repeating the interview.

- **Architecture:** if documents do not establish it, ask the user. Present a recommendation appropriate to the existing code, alternatives (for example TCA, observable models, or MVVM) and free-text input. A linked package alone is not a decision.
- **SDD:** on first setup offer lightweight Markdown, OpenSpec, Spec Kit and a custom choice, with a recommendation. An explicit user choice takes precedence over the default and over existing incomplete scaffolding.
- **Scope:** identify the product purpose, existing folder conventions and the desired verification baseline. If product exploration is deferred, record that boundary rather than inventing features.
- **Execution:** preserve or determine CI provider, shared-machine concurrency budget and required checks. Ask only about material ambiguities; infer reversible details from the repository and user's language.

Use short rounds of dependent questions with recommended answers. Facts obtainable from files or tools are your responsibility. Preserve answers in a small engineering profile within the repository's existing docs convention. Keep machine-specific paths and simulator identifiers in ignored local state.

Once choices are clear, proceed with authorized reversible preparation. A second blanket approval step is unnecessary.

## 3. Establish the change contract

Use [references/workflows.md](references/workflows.md) for the selected SDD branch. Record scope, observable acceptance criteria, implementation steps, ownership of shared files and verification before substantive implementation. Preserve existing active changes.

The accepted behavior, proposed changes, engineering decisions and execution evidence have different roles. Give each one canonical storage; avoid maintaining duplicate specs in two systems.

## 4. Prepare the repository

Use [references/documents.md](references/documents.md) to create or reconcile:

- `README.md`: purpose, prerequisites, quick start and actual commands.
- `AGENTS.md`: a compact agent entry point with specific commands, constraints and conditional pointers.
- `CLAUDE.md`: a relative symlink to `AGENTS.md`, after preserving any unique existing content. Use an import fallback only when the target environment cannot preserve symlinks.
- Purposeful documentation, build/test scripts, ignores, test configuration and the selected CI configuration.

Establish ongoing documentation maintenance in the generated agent instructions and selected workflow: assess affected documents at task start, record agreed decisions and verified knowledge as work proceeds, and reconcile documentation before completion. Require a brief documentation-impact result in the task evidence, including a reason when no update is needed. Follow the canonical ownership and history rules in `references/documents.md`.

Continue the existing source tree. Add a new directory when it has a concrete role; do not replace a user's organization with a preferred architecture template. Do not call a placeholder view an exemplary module. Create a small behaviorally tested example only if it is within the agreed scope.

For build/test infrastructure read [references/ios-harness.md](references/ios-harness.md). Optional reusable implementation is under `assets/harness/`; copy only needed resources, adapt the detected manifest, and verify them in the destination. Keep repository scripts self-contained after installation.

Use installed toolchains where compatible. Pin newly required local development tools and their lockfiles. Configure only the chosen CI provider; prepare the file locally without silently connecting accounts, pushing code or publishing the app. Preserve signing and production configuration.

## 5. Verify the result

1. Check instruction links, referenced paths, config syntax, shared schemes and discovery of real test targets.
2. Run the documented bootstrap, build and required tests through the repository entry points. Capture exit codes, raw logs and result bundles.
3. Validate the selected SDD artifacts. Distinguish planning completeness from implementation correctness.
4. Check isolation: separate artifacts, simulator ownership, real cross-process lock contention, failure propagation and cleanup limited to owned resources.
5. Check repeatability: a second preparation with the same decisions preserves manual content and introduces no duplicate instructions, directories or semantic changes.
6. Review the final diff against the initial state; report skipped or blocked checks explicitly. Missing tests are not passing tests.
7. Confirm the generated instructions make documentation maintenance part of future tasks, with canonical locations, shared-file ownership and a completion check. Do not require meaningless edits for tasks with no documentation impact.

Use [references/acceptance.md](references/acceptance.md) for meaningful fixture scenarios when validating this workflow or substantial changes to it. Simple documentation edits do not require a full simulator run.

## 6. Finish

Update the engineering profile and evidence with actual outcomes. Complete or archive the SDD change only after requirements and checks pass. Give the user concise links to the entry point, evidence and any requested workflow guide. Clearly separate a locally validated CI definition from a cloud run that has not occurred.
