---
title: 2. Module Entrypoint
description: A bundled, self-contained capability with assets and a contract. The unit of REUSE.
sidebar:
  order: 3
  label: Module Entrypoint
---

A bundled, self-contained capability with its own assets and a contract (frontmatter description = function signature; body = process; assets = lazy-loaded knowledge). The unit of REUSE.

**INDUSTRY TERMS:** "skill" ([agentskills.io](https://agentskills.io)), "plugin", "command bundle".

## Canonical spec, bounded

The agentskills.io project is the canonical authority for the SKILL.md CONTAINER SURFACE -- and ONLY that. Cite its rules for what it owns; do NOT promote its framing into Genesis ontology.

**What agentskills.io owns** (cite verbatim, fetch live):

- SKILL.md frontmatter fields and limits
- body size budget
- the canonical directory layout (`scripts/` + `references/` + `assets/`)
- script conventions
- the evaluation discipline (content evals, trigger evals, with-skill vs without-skill baseline)

**What agentskills.io does NOT own** (Genesis is authoritative): the broader primitive taxonomy. The agentskills.io corpus uses "skill" as the unit, conflating the container surface with the agent's whole behavior. Genesis treats MODULE ENTRYPOINT as ONE primitive type among PERSONA SCOPING, SCOPE-ATTACHED RULE, CHILD-THREAD SPAWN, ORCHESTRATOR, ASSET. Do not let the spec's unit framing erase the other primitive types when designing.

**Conflict resolution rule:** where the two corpora disagree, the container surface follows agentskills.io; the primitive taxonomy and Genesis pattern catalogues stay Genesis-owned. If you are uncertain which side a question lands on, ask: "is this about how the SKILL.md file is shaped" (agentskills.io) or "is this about what kinds of primitives exist and how they compose" (Genesis).

### Authority pages (load-bearing for the container surface)

- [agentskills.io/skill-creation/best-practices](https://agentskills.io/skill-creation/best-practices) -- body content, gotchas, output templates, calibrating prescriptiveness, procedures over declarations, refine-with-execution, real-expertise sourcing.
- [agentskills.io/skill-creation/optimizing-descriptions](https://agentskills.io/skill-creation/optimizing-descriptions) -- imperative phrasing, user-intent framing, indirect-trigger ("be pushy") clauses, 1024-character hard cap on `description`, trigger-eval split (~20 queries 60/40 train/val).
- [agentskills.io/skill-creation/evaluating-skills](https://agentskills.io/skill-creation/evaluating-skills) -- `evals/evals.json` schema, with-skill vs without-skill baseline, iteration workspace, when assertions land.
- [agentskills.io/skill-creation/using-scripts](https://agentskills.io/skill-creation/using-scripts) -- `scripts/` directory conventions, version pinning, non-interactive shell requirement, `--help` doc, structured stdout vs diagnostic stderr.
- [agentskills.io/specification](https://agentskills.io/specification) -- `name` regex (1-64 chars, `[a-z0-9-]`, must equal parent dir), directory layout (`scripts/` + `references/` + `assets/`), SKILL.md body budget (<= 500 lines AND <= 5000 tokens; overflow to `references/` with explicit load-trigger phrasing).

## When to use

A capability that needs its own dispatch trigger, may be invoked discoverably by the harness's dispatcher, and bundles assets that should not pollute the parent context until needed.

## Key property

The frontmatter description is preloaded by the harness into every session. It is the function signature the dispatcher LLM matches against. **Treat it as code, not as marketing copy.**

## Binding modes

A MODULE ENTRYPOINT can be bound into a thread two distinct ways. Same primitive shape (markdown + frontmatter + body + lazy assets); different binding determines the substrate fields in play.

### 1. Agent-invoked (default; the agentskills.io case)

The harness's dispatcher LLM matches the entrypoint's `description` against the live session and lazy-loads the body as ADDITIVE context mid-session. The session was rooted by something else (operator prompt, slash command, prior turn). The KEY PROPERTY above governs: description is a function signature, dispatcher matches it.

### 2. Substrate-invoked (the trigger-orchestrator case)

A [TRIGGER ORCHESTRATOR](/genesis/reference/primitives/trigger-orchestrator/) instantiates the entrypoint as the session ROOT in response to an external event. The body is the initial task; the dispatcher does not match anything -- the trigger surface IS the matcher (event filter, slash command, schedule). Substrate fields like SANDBOXING, CAPABILITY_GATING, AUDIT_SURFACE may apply (when the trigger surface provides them; see per-trigger-surface adapters).

The substrate-invoked binding is the corpus mechanism that lets architectural patterns A6 EVENT-DRIVEN and A10 GOVERNED OUTER LOOP reuse the entrypoint primitive instead of inventing a new "workflow file" type. When you design an entrypoint for substrate invocation, the per-trigger-surface adapter (e.g. `runtime-affordances/per-trigger-surface/gh-aw.md`) prescribes the frontmatter shape; the body still follows the same authoring discipline as any other entrypoint.

## See also

- [Persona Scoping File](/genesis/reference/primitives/persona-scoping-file/) -- can be loaded together with an entrypoint into the same thread.
- [Child-Thread Spawn](/genesis/reference/primitives/child-thread-spawn/) -- the affordance that lets an entrypoint run in context isolation.
- [Trigger Orchestrator](/genesis/reference/primitives/trigger-orchestrator/) -- substrate-invoked binding lives here.
