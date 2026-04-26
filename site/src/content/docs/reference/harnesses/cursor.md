---
title: Cursor
description: Genesis on Cursor -- file paths, frontmatter dialect, and how /genesis resolves.
sidebar:
  order: 4
  label: Cursor
---

Cursor is the AI-first IDE from Anysphere. Genesis runs as a skill bundle under `.cursor/skills/`; rules live in `.cursor/rules/`.

## File paths

| Primitive | Path |
|---|---|
| Module Entrypoint (skill folder) | `.cursor/skills/<skill-name>/SKILL.md` |
| Persona Scoping File | `.cursor/rules/*.mdc` (with persona-shaped frontmatter) |
| Scope-Attached Rule File | `.cursor/rules/*.mdc` (with `globs:` frontmatter) |

## How `/genesis` resolves

After `npx skills add danielmeppiel/genesis`, the loader writes Genesis to `.cursor/skills/genesis/`. In a Cursor agent session, type:

```text
/genesis <what you want designed>
```

Cursor's agent surface picks up the skill via the slash dispatcher.

## The `.mdc` rule format

Cursor uses a single rule file shape with frontmatter that toggles between persona-style and rule-style behavior:

```yaml
---
description: Lens for reviewing missing tests in a PR diff.
globs:
  - "**/*.test.ts"
alwaysApply: false
---
```

- `globs` + `alwaysApply: false` -> behaves as a [SCOPE-ATTACHED RULE FILE](/genesis/reference/primitives/scope-attached-rule-file/) (path-matched).
- `alwaysApply: true` (no globs) -> behaves as a session-wide rule.
- Used as a sub-agent description without globs -> behaves more like a [PERSONA SCOPING FILE](/genesis/reference/primitives/persona-scoping-file/).

This single-file overloading is a Cursor-specific concession. Genesis primitives stay distinct in the design layer; the `.mdc` shape is the runtime adapter.

## Tool surface

Cursor exposes the editor's file / search / shell affordances to the agent. MCP servers are configured via Cursor's settings UI or `~/.cursor/mcp.json`.

## Official documentation

- [Cursor docs (cursor.com/docs)](https://cursor.com/docs) -- canonical authority for the Cursor agent, rules, MCP, and skill loading. (Verified 200 OK.)
- Mirror: [docs.cursor.com](https://docs.cursor.com/) (also live).

## See also

- [Scope-Attached Rule File](/genesis/reference/primitives/scope-attached-rule-file/) -- the `globs:`-bearing `.mdc` shape.
- [Persona Scoping File](/genesis/reference/primitives/persona-scoping-file/) -- the no-globs description-bearing `.mdc` shape.
- A full per-harness adapter will be added by the catalogue agent.
