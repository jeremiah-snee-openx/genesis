---
title: Claude Code
description: Genesis on Claude Code -- file paths, frontmatter dialect, and how /genesis resolves.
sidebar:
  order: 3
  label: Claude Code
---

Claude Code is Anthropic's terminal coding agent. Genesis runs as a skill bundle under `.claude/skills/`; personas live in `.claude/agents/`.

## File paths

| Primitive | Path |
|---|---|
| Module Entrypoint (skill folder) | `.claude/skills/<skill-name>/SKILL.md` |
| Persona Scoping File | `.claude/agents/*.md` |
| Scope-Attached Rule File | `CLAUDE.md` (project root or nested) |
| Child-Thread Spawn | the `Task` tool (built-in) |

## How `/genesis` resolves

After `npx skills add danielmeppiel/genesis`, the loader writes Genesis to `.claude/skills/genesis/`. In a Claude Code session, type:

```text
/genesis <what you want designed>
```

Claude Code's dispatcher matches the slash command against the skill folder name. The `SKILL.md` body lazy-loads. Asset files under `assets/` only load when the body cites them.

## Persona files

Claude subagents are markdown files at `.claude/agents/<name>.md` with YAML frontmatter:

```yaml
---
name: pr-tests-lens
description: Reviews a PR diff for missing test coverage on changed code paths.
tools: Read, Grep, Glob, Bash
---
```

Subagents are spawned via the `Task` tool, which Claude exposes as a primitive [CHILD-THREAD SPAWN](/genesis/reference/primitives/child-thread-spawn/) affordance. Each spawn is stateless; hand off via explicit artifacts written to [plan persistence](/genesis/reference/primitives/plan-persistence/).

## Scope-attached rules

`CLAUDE.md` files are loaded automatically by path. A `CLAUDE.md` at the project root applies to every session opened in that directory; nested `CLAUDE.md` files cascade for sub-trees. Use them for cross-cutting invariants, not capabilities.

## Tool surface

Claude Code preloads `Read`, `Write`, `Edit`, `Bash`, `Grep`, `Glob`, `WebFetch`, `WebSearch`, and `Task` (for child-thread spawn). MCP servers can be wired through `~/.config/claude/` or per-project MCP config to widen the surface.

## Official documentation

- [Claude Code overview (docs.claude.com)](https://docs.claude.com/en/docs/claude-code/overview) -- canonical authority for the Claude Code surface, subagents, MCP integration, and tool reference. (Verified 200 OK.)

## See also

- [Module Entrypoint](/genesis/reference/primitives/module-entrypoint/) -- the skill bundle Claude loads.
- [Child-Thread Spawn](/genesis/reference/primitives/child-thread-spawn/) -- the `Task` tool realizes this primitive.
- A full per-harness adapter (affordance table, portability rules) will be added by the catalogue agent.
