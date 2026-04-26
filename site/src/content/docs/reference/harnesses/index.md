---
title: Harness setup
description: Per-harness file paths, dispatcher quirks, and how /genesis resolves on each runtime.
sidebar:
  order: 1
  label: Overview
---

The [primitives](/genesis/reference/primitives/) are the same on every harness. Only the file names and frontmatter dialects change. This index page is for skim-and-deep-link: find your row, jump to the detail page.

## Harness matrix

| Harness            | Persona file path             | Skill folder        | Detail page |
|--------------------|-------------------------------|---------------------|-------------|
| GitHub Copilot CLI | `.github/agents/*.agent.md`   | `.github/skills/`   | [Details](/genesis/reference/harnesses/copilot/) |
| Claude Code        | `.claude/agents/*.md`         | `.claude/skills/`   | [Details](/genesis/reference/harnesses/claude-code/) |
| Cursor             | `.cursor/rules/*.mdc`         | `.cursor/skills/`   | [Details](/genesis/reference/harnesses/cursor/) |
| Codex              | `AGENTS.md` files             | `~/.codex/skills/`  | [Details](/genesis/reference/harnesses/codex/) |
| OpenCode           | `.opencode/agent/*.md`        | `.opencode/skills/` | [Details](/genesis/reference/harnesses/opencode/) |
| Gemini             | _coming soon_                 | _coming soon_       | [Status](/genesis/reference/harnesses/gemini/) |

The primitive vocabulary is identical across rows. The differences are local: where the harness reads files from, what frontmatter it accepts, what the dispatcher pre-loads into every session.

## How `/genesis` resolves

`/genesis` is a [MODULE ENTRYPOINT](/genesis/reference/primitives/module-entrypoint/) that the harness's dispatcher matches against the operator prompt. The match-and-load mechanism is harness-specific:

- **Slash-style harnesses** (Claude Code, Cursor, Copilot CLI): the literal `/genesis` token is recognized by the dispatcher and the skill body is loaded.
- **Description-match harnesses** (Codex, OpenCode): the dispatcher matches the entrypoint's frontmatter `description` against the prompt; type `/genesis ...` and the description match fires.

In both cases the `description` field is the function signature the dispatcher matches. Treat it as code, not as marketing copy.

## What goes in each detail page

- **Persona scoping file path and frontmatter dialect.**
- **Skill folder path and dispatcher behavior.**
- **Tool surface preloaded by the harness.**
- **Known gotchas** (path traversal, frontmatter validation, plan-persistence quirks).
- **Official documentation link** (verified live).

A more comprehensive per-harness reference (full affordance tables, portability rules, module-system adapter behavior) will be added by the catalogue agent under `/reference/harness-adapters/<harness>/`.

## See also

- [Primitives](/genesis/reference/primitives/) -- the substrate concepts that every row in the matrix implements.
- [Quick start](/genesis/guides/quick-start/) -- the five-minute path to your first invocation, harness-agnostic.
