---
title: Install
description: Add Genesis to any compatible agent harness in one command.
sidebar:
  order: 2
---

Genesis is a [skill](/genesis/reference/primitives/module-entrypoint/) bundle. It loads into any harness that implements the [agentskills.io](https://agentskills.io) container surface. There are two install paths.

## Path 1: npx skills (zero global install)

```bash
npx skills add danielmeppiel/genesis
```

This adds Genesis to your project's local skill folder. It works with Claude Code, Cursor, Codex, OpenCode, GitHub Copilot, and 41+ more agents -- the full list is at [skills.sh](https://skills.sh).

The loader detects your harness from the project layout (`.github/`, `.claude/`, `.cursor/`, `.opencode/`, `AGENTS.md`) and writes the skill to the right path. You do not need to know the harness-specific folder name.

## Path 2: apm (manifest + lockfile)

If your project already uses [apm](https://github.com/microsoft/apm) for agentic-primitive dependencies:

```bash
apm install danielmeppiel/genesis
```

This adds `danielmeppiel/genesis` to your `apm.yml` and pins the resolved version in `apm.lock.yaml`. Use this path when you need reproducible installs across CI and developer machines, or when you publish a meta-skill that depends on Genesis.

For details on the manifest and lockfile semantics, see the [apm repository](https://github.com/microsoft/apm).

## Verify the install

After install, the skill folder exists at the harness-specific path:

| Harness         | Skill path           |
|-----------------|----------------------|
| Claude Code     | `.claude/skills/`    |
| GitHub Copilot  | `.github/skills/`    |
| Cursor          | `.cursor/skills/`    |
| OpenCode        | `.opencode/skills/`  |
| Codex           | `~/.codex/skills/`   |

Open a fresh agent session and type `/genesis` -- if the dispatcher recognizes it, you are done. If not, see [Harness setup](/genesis/reference/harnesses/) for harness-specific dispatcher quirks.

## Update or remove

```bash
# update
npx skills update danielmeppiel/genesis

# remove
npx skills remove danielmeppiel/genesis
```

Apm users use `apm update` and `apm remove` respectively.
