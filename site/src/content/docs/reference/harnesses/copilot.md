---
title: GitHub Copilot
description: Genesis on GitHub Copilot CLI -- file paths, frontmatter dialect, and how /genesis resolves.
sidebar:
  order: 2
  label: GitHub Copilot
---

GitHub Copilot CLI is the GitHub-hosted agent harness. Genesis runs as a skill bundle under `.github/skills/`; personas live in `.github/agents/`.

## File paths

| Primitive | Path |
|---|---|
| Module Entrypoint (skill folder) | `.github/skills/<skill-name>/SKILL.md` |
| Persona Scoping File | `.github/agents/*.agent.md` |
| Scope-Attached Rule File | `.github/instructions/*.instructions.md` (path-globbed) |
| Trigger Orchestrator | `.github/workflows/*.yml` (with [gh-aw](https://github.com/githubnext/gh-aw) for agentic workflows) |

## How `/genesis` resolves

After `npx skills add danielmeppiel/genesis`, the loader writes Genesis to `.github/skills/genesis/`. In a Copilot CLI session, type:

```text
/genesis <what you want designed>
```

The dispatcher recognizes the slash command and lazy-loads `SKILL.md` into the session. Lazy assets under `assets/` only load when the body explicitly references them.

## Persona files

Copilot agents are markdown files at `.github/agents/<name>.agent.md` with YAML frontmatter:

```yaml
---
name: pr-tests-lens
description: Reviews a PR diff for missing test coverage on changed code paths.
---
```

The agent is invoked through Copilot's `task` tool / sub-agent mechanism, which spawns a [child thread](/genesis/reference/primitives/child-thread-spawn/) with a fresh context window.

## Tool surface

Copilot CLI preloads the terminal (shell command execution) and a structured set of file / search / git tools by default. MCP servers can be wired through Copilot's MCP configuration to widen the tool surface.

## Triggers (gh-aw)

For [TRIGGER ORCHESTRATOR](/genesis/reference/primitives/trigger-orchestrator/) workloads, GitHub Agentic Workflows ([gh-aw](https://github.com/githubnext/gh-aw)) provide the substrate-invoked binding: a workflow file under `.github/workflows/` declares the event filter, capability gates (`safe-outputs`), and the entrypoint to dispatch.

## Official documentation

- [GitHub Copilot docs](https://docs.github.com/en/copilot) -- canonical authority for the Copilot CLI surface, agent framework, and MCP integration. (Verified 200 OK.)

## See also

- [Module Entrypoint](/genesis/reference/primitives/module-entrypoint/) -- the skill bundle Copilot loads.
- [Persona Scoping File](/genesis/reference/primitives/persona-scoping-file/) -- what `.github/agents/*.agent.md` realizes.
- A full per-harness adapter (affordance table, portability rules) will be added by the catalogue agent.
