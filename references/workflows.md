# Select and initialize the SDD workflow

All branches link intent → acceptance scenarios → bounded implementation → evidence. Keep a quick path for a small fix; a large PRD is not required for a typo.

For every branch include documentation impact in task planning and completion: list affected canonical docs and update them with the implementation, or briefly record why no update is required. Evidence must state the result. Keep accepted behavior, current guides and historical verification distinct, following `documents.md`.

## Lightweight Markdown

Preserve existing conventions, otherwise use a small change directory with spec, optional design/plan, tasks and verification. State scope/non-goals and concrete success scenarios. Give parallel tasks explicit dependencies and file ownership. Store durable architecture separately. Validate links and required acceptance coverage with a small check rather than inventing a framework.

## OpenSpec

Prefer an already pinned compatible version. If absent, inspect current stable documentation/help, choose a version and install it locally with a lockfile. Avoid a moving `npx ...@latest` dependency in everyday commands. A repository wrapper makes the chosen binary explicit and runs at the repo root. Disable telemetry per process if the project requires local-only tooling behavior.

The CLI workflow below was checked against 1.14.1; inspect installed help before assuming newer flags. For a new setup without additional agent integrations:

```sh
openspec init --tools none --profile core --no-animation
openspec new change <change-id> --schema spec-driven --json
openspec status --change <change-id> --json
openspec instructions proposal --change <change-id> --json
openspec instructions specs --change <change-id> --json
openspec instructions design --change <change-id> --json
openspec instructions tasks --change <change-id> --json
openspec validate <change-id> --type change --strict --json --no-interactive
openspec instructions apply --change <change-id> --json
```

Use returned artifact paths/dependencies. Instructions are a template and context, not an implementation result. Follow the discovered schema, not a hardcoded number of artifacts. Preserve structural headings and SHALL/MUST/WHEN/THEN syntax while using the selected documentation language.

- `openspec/specs/` contains accepted current behavior.
- `openspec/changes/<id>/` contains proposed changes and implementation work.
- Engineering docs remain in the established docs directory; no second normative `docs/specs/` tree.
- A small `verification.md` in the change can map requirements to commands and evidence, but the CLI does not enforce it automatically.

`isPlanningComplete` (and compatible `isComplete`) only means planning files exist. After actual implementation checks, separately confirm completed tasks and evidence, inspect `instructions archive`, then archive and validate main specs and archived tasks. `archive --yes` may skip the incomplete-task warning; never treat it as a quality gate or use `--no-validate` routinely.

Scope validation to the current change during parallel work; another agent may legitimately have an incomplete draft. Coordinate updates to shared main specs and archive operations through one integrator. Keep open change IDs explicit.

`openspec update` refreshes installed integrations and is not a required step for every feature. Do not install additional agent workflows merely to make bootstrap function; this procedure works through CLI commands and bundled knowledge.

Official documentation: https://github.com/Fission-AI/OpenSpec/tree/main/docs

## Spec Kit

Inspect any existing `.specify` configuration and the installed CLI's help first. Preserve the established constitution and workflow. For a new setup, present available normal/lean presets with a recommendation; use current official installation instructions and a pinned version where supported. Do not guess old slash-command syntax.

Carry the agreed scope through specification, plan and tasks, using the tool's current consistency checks. Keep implementation verification in repository commands. Generated assistant integrations are optional delivery mechanisms; the bootstrap procedure must not depend on invoking a separate workflow package. If a requested integration cannot operate under the user's constraints, state the limitation and offer the compatible CLI/artifact path.

Official documentation: https://github.com/github/spec-kit

## Custom workflow

Use the user's selected format and current documentation. Map its artifacts to the same intent/acceptance/implementation/evidence roles, preserve its conventions and verify its commands. Ask only where the custom workflow leaves a consequential ambiguity.
