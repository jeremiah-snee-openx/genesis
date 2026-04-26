---
title: Codex
description: Genesis on OpenAI Codex -- file paths, frontmatter dialect, and how /genesis resolves.
sidebar:
  order: 5
  label: Codex
---

Codex is OpenAI's coding agent (CLI and cloud). Genesis runs as a skill bundle under `~/.codex/skills/`; personas are declared via `AGENTS.md` files.

## File paths

| Primitive | Path |
|---|---|
| Module Entrypoint (skill folder) | `~/.codex/skills/<skill-name>/SKILL.md` |
| Persona Scoping File | `AGENTS.md` (project root or nested) |
| Scope-Attached Rule File | `AGENTS.md` sections (path-scoped by directory) |

## How `/genesis` resolves

After `npx skills add danielmeppiel/genesis`, the loader writes Genesis to `~/.codex/skills/genesis/`. In a Codex session, type:

```text
/genesis <what you want designed>
```

The dispatcher matches the slash command against the user-level skill folder.

## `AGENTS.md` -- the universal persona format

Codex follows the cross-vendor `AGENTS.md` convention: a markdown file at the project root that scopes the agent's voice, expertise, and constraints. Nested `AGENTS.md` files cascade for sub-trees, providing path-scoped behavior without a separate rule-file primitive.

```markdown
# AGENTS.md

You are reviewing a PR. Your lens is missing-test coverage.
Hard constraint: never approve, never auto-merge.
```

This single-file approach is the Codex concession. In Genesis terms, an `AGENTS.md` file simultaneously realizes [PERSONA SCOPING FILE](/genesis/reference/primitives/persona-scoping-file/) and [SCOPE-ATTACHED RULE FILE](/genesis/reference/primitives/scope-attached-rule-file/) -- the harness does not separate them, but the design layer should.

## Tool surface

Codex CLI preloads shell command execution and file / search tools. The cloud-hosted variant additionally exposes a sandboxed network and code-execution surface. MCP support is documented at the link below.

## Official documentation

- [OpenAI Codex (developers.openai.com/codex)](https://developers.openai.com/codex/) -- canonical authority for the Codex CLI and cloud surface. (Verified 200 OK.)
- Note: the older `platform.openai.com/docs/codex` returned `403` on automated `HEAD` requests during URL verification; `developers.openai.com/codex/` is the current canonical landing page and resolves cleanly.

## See also

- [Persona Scoping File](/genesis/reference/primitives/persona-scoping-file/) -- `AGENTS.md` realizes this primitive.
- [Scope-Attached Rule File](/genesis/reference/primitives/scope-attached-rule-file/) -- nested `AGENTS.md` sections also realize this primitive.
- A full per-harness adapter will be added by the catalogue agent.
