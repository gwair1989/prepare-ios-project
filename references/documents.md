# Documents and preservation

## Canonical instructions

Use the portable filenames `README.md`, `AGENTS.md` and `CLAUDE.md`. Inspect case variants and symlinks before creating anything. Preserve unrelated content; resolve conflicting instructions with the user when the intended rule is unclear.

`CLAUDE.md -> AGENTS.md` is a relative link committed with the repository. Verify it resolves within the checkout and its bytes equal the canonical file. If an existing regular CLAUDE file contains unique rules, merge them into the appropriate canonical document before replacing it. On a host that cannot preserve symlinks, an ordinary CLAUDE file containing `@AGENTS.md` is a supported fallback, documented as such.

## Entry point content

Keep AGENTS brief enough to read at task start. Include the commands and non-obvious decisions that change agent behavior:

- Where the product scope, architecture and active specs live, with conditions for reading each.
- How to run the real build and verification, and where evidence is stored.
- Architecture boundaries and a real exemplary path when one exists.
- Ownership of shared files, local state and simulators.
- Completion criteria and excluded areas such as signing or production migrations when relevant.

Use nested instructions only when a subtree genuinely has different rules. Avoid full generated trees, tutorial prose, tool catalogs and duplicated policy. Instructions describe intent; scripts and tests enforce measurable rules.

README should help a new human start the project. Deeper documents hold product context, architecture, engineering choices, testing and troubleshooting. Prefer existing filenames and navigation. Empty speculative directories are not useful preparation.

## Saved decisions

The engineering profile records: architecture and evidence/confirmation, SDD choice, directory roles, deployment baseline, documentation language, CI provider, required gates, allowed setup scope, concurrency limit and deferred product decisions. Runtime UDIDs, logs and absolute host paths belong in ignored local state.

On rerun compare desired state with existing state before editing. Preserve manual additions. Never append a second rules block to avoid reconciling the first. A migration of the canonical spec location must leave a pointer, not two maintained copies.

## Ongoing maintenance

Preparation must leave a maintenance contract for subsequent agents, not only initial documents. Put a concise obligation in AGENTS and use existing documentation conventions for the detailed mapping. Preserve the user's language and established paths.

At task start identify affected documentation in the task plan, or explain no impact. During implementation record agreed decisions, new constraints and verified operational knowledge. Before completion compare the delivered change with canonical documents, repair relevant omissions/stale instructions, validate affected links/commands and record the documentation outcome in task evidence. A small task needs only a brief record; do not force a new document or a cosmetic edit.

Map behavior to the selected SDD specs; architecture to the architecture guide; setup/commands to README and development docs; verification policy to testing docs; durable choices to the engineering profile; agent rules to AGENTS. Update navigation after moving files. Avoid duplicate normative specs or a growing task diary in AGENTS.

When code and docs disagree, determine intended behavior from accepted requirements and user decisions. Do not rewrite a requirement merely to bless a bug. Mark unresolved assumptions and ask only about consequential ambiguity; do not declare that part complete while a material discrepancy remains.

Update current guides in place. Preserve historical research and verification scope, dates and results; create new evidence for new code, or append a dated correction for a factual error. Previous passing checks are not evidence for subsequent changes. Shared documentation and main specs need an agreed integrator during concurrent work; reread current content and preserve other contributors' edits.

Official references, when compatibility needs checking:

- https://agents.md
- https://code.claude.com/docs/en/memory
- https://agentskills.io/specification
