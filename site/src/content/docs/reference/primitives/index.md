---
title: Primitives
description: The six substrate concepts every agent harness implements.
sidebar:
  order: 1
  label: Overview
---

The six concepts every agent harness implements under different folder names and frontmatter dialects. Genesis names them once so the vocabulary outlives any one tool.

A primitive is a FILE the runtime loads into a thread to bias inference, or a RUNTIME AFFORDANCE that creates / coordinates threads. Primitives are the substrate. Tier-2 design patterns and Tier-3 architectural patterns are built ON TOP of these.

## The six primitives

| # | Primitive | What it is | Common terms |
|---|---|---|---|
| 1 | [Persona Scoping File](/genesis/reference/primitives/persona-scoping-file/) | A document loaded at session start to scope WHO the agent is. | "agent file", "subagent definition", "mode", `AGENTS.md` |
| 2 | [Module Entrypoint](/genesis/reference/primitives/module-entrypoint/) | A bundled, self-contained capability with assets and a contract. | "skill", "plugin", "command bundle" |
| 3 | [Scope-Attached Rule File](/genesis/reference/primitives/scope-attached-rule-file/) | A constraint that auto-applies to a path or context. | "instruction file", "rule", "memory", "always-load" |
| 4 | [Child-Thread Spawn](/genesis/reference/primitives/child-thread-spawn/) | A runtime affordance that creates a fresh-context execution unit. | "subagent thread", "Task tool", "background agent" |
| 5 | [Trigger Orchestrator](/genesis/reference/primitives/trigger-orchestrator/) | A declarative pipeline that spawns sessions on events. | "workflow", "hook", "automation", "trigger" |
| 6 | [Plan Persistence](/genesis/reference/primitives/plan-persistence/) | A stable artifact holding the active plan across turns and spawns. | "plan.md", "TODO state", "checkpoints", "session store" |

These names are deliberately generic. The architecture must outlive any one tool.

## How the substrate composes

```text
TRIGGER ORCHESTRATOR
        |
        v  spawns
  CHILD-THREAD SPAWN ----- spawns more child threads ----+
        |                                                |
        | loads at startup                               |
        |   PERSONA SCOPING FILE                         |
        |   MODULE ENTRYPOINT (entrypoint + lazy assets) |
        |   SCOPE-ATTACHED RULE FILE (path-matched)      |
        |                                                |
        v                                                v
   reads + writes                              reads + writes
        |                                                |
        +--------> PLAN PERSISTENCE (single source of truth)
```

Each primitive earns its keep against PROSE ([danielmeppiel.github.io/awesome-ai-native](https://danielmeppiel.github.io/awesome-ai-native/)):

| Primitive | PROSE axis it satisfies |
|---|---|
| MODULE ENTRYPOINT (lazy assets) | Progressive Disclosure |
| CHILD-THREAD SPAWN | Reduced Scope |
| Module composition (inline / sibling / external) | Orchestrated Composition |
| TRIGGER ORCHESTRATOR + validation gates | Safety Boundaries |
| Cascading SCOPE-ATTACHED RULE FILEs | Explicit Hierarchy |

## Primitives vs Modules (the disambiguation you enforce)

**PRIMITIVE:** a file the runtime loads (skill, persona, rule, orchestrator workflow). The unit of REASONING.

**MODULE:** a unit of DISTRIBUTION. One or more primitives + declared dependencies + version + identity. One primitive may itself be a module. Conflating primitive with module hides composition: leaf files get duplicated across projects instead of depended on as modules.

A module's dependencies are surfaced AT ITS DISTRIBUTION SURFACE (manifest dep entry; or, when no manifest exists for that distribution mechanism, an explicit companion-module recommendation in the body + a tool-call probe at the use-site). Naming a dependency in prose without declaring it at a loader-visible surface is **PHANTOM DEPENDENCY** -- the coupling is visible to humans reading the markdown but invisible to the harness loader, so the dependency cannot be supplied.

## Tool-call affordance (NOT a primitive type)

Beyond the six primitive FILES above, every modern harness exposes a TOOL-CALL AFFORDANCE: a runtime mechanism by which the LLM emits a structured invocation (name + arguments) that the harness executes deterministically on a CPU and returns to the next inference step. This is a RUNTIME PROPERTY of the harness, not a new primitive type. It does not ship as a markdown file you author; it is exposed by the harness to the model via the tool-call protocol.

Without this affordance the LLM has no impact on real systems -- it can only emit text. Harnesses therefore PRELOAD a primitive tool surface so an agent is useful from turn one. The TERMINAL (shell command execution) is the universal preloaded tool and the highest-leverage one, because the LLM can synthesize any command across any installed CLI.

The pattern that names this seam between the LLM (probabilistic, frozen, hallucination-prone) and deterministic substrate (CLI, scripts, MCP servers, HTTP APIs) is **S7 Deterministic Tool Bridge**. The architectural pattern that USES it is **A9 Supervised Execution**. These will be cross-linked from the design-patterns and architectural-patterns pages once published.

The Model Context Protocol ([modelcontextprotocol.io](https://modelcontextprotocol.io)) is the authoritative specification for ONE concrete realization of the tool-call affordance: the protocol layer between an MCP-aware harness and an MCP server. Cite it for the protocol surface; do NOT promote its framing into the genesis primitive taxonomy. MCP is a transport for the tool-call affordance, not a new primitive type.

## Source

These six primitives are lifted verbatim from `skills/genesis/assets/primitives.md` in the [Genesis repository](https://github.com/danielmeppiel/genesis). Each detail page below preserves the original definition, INDUSTRY TERMS, WHEN TO USE, and KEY PROPERTY blocks.
