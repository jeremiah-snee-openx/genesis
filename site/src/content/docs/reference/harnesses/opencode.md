---
title: OpenCode
description: Genesis on OpenCode -- file paths, frontmatter dialect, and how /genesis resolves.
sidebar:
  order: 6
  label: OpenCode
---

OpenCode is the open-source terminal AI coding agent from SST. Genesis runs as a skill bundle under `.opencode/skills/`; personas live in `.opencode/agent/`.

## File paths

| Primitive | Path |
|---|---|
| Module Entrypoint (skill folder) | `.opencode/skills/<skill-name>/SKILL.md` |
| Persona Scoping File | `.opencode/agent/*.md` |
| Scope-Attached Rule File | `AGENTS.md` (project root) |

## How `/genesis` resolves

After `npx skills add danielmeppiel/genesis`, the loader writes Genesis to `.opencode/skills/genesis/`. In an OpenCode session, type:

```text
/genesis <what you want designed>
```

The dispatcher matches the slash command and lazy-loads `SKILL.md`.

## Persona files

OpenCode agents are markdown files at `.opencode/agent/<name>.md`. Frontmatter follows the cross-vendor agent convention:

```yaml
---
description: Lens for reviewing missing tests in a PR diff.
mode: subagent
---
```

OpenCode honors the `AGENTS.md` convention for cross-cutting rules at the project root, so a project that targets both Codex and OpenCode can share one `AGENTS.md`.

## Tool surface

OpenCode preloads shell, file, and search tools. MCP servers are configured per-project; see the official docs for the configuration shape.

## Official documentation

- [OpenCode (opencode.ai)](https://opencode.ai) -- official landing page. (Verified 200 OK.)
- [OpenCode docs (opencode.ai/docs)](https://opencode.ai/docs/) -- documentation index. (Verified 200 OK.)
- [Source repository (github.com/sst/opencode)](https://github.com/sst/opencode) -- canonical source of truth for the agent file shape and skill loading. (Verified 200 OK.)

## See also

- [Module Entrypoint](/genesis/reference/primitives/module-entrypoint/) -- the skill bundle OpenCode loads.
- [Persona Scoping File](/genesis/reference/primitives/persona-scoping-file/) -- `.opencode/agent/*.md` realizes this primitive.
- A full per-harness adapter will be added by the catalogue agent.
