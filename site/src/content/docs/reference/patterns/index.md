---
title: Pattern catalogue
description: 37 named patterns across three tiers -- architectural (A1-A10), design (C1-C6 / S1-S7 / B1-B10), and refactor (R1-R4). Pick one Tier-3 shape; compose Tier-2 patterns inside it; restructure with Tier-4 refactors when the module graph fights back.
---

The Genesis catalogue names 37 patterns across three tiers. Each pattern carries a verbatim WHEN clause, a MECHANISM, and a list of ANTI-PATTERNS. Cite the WHEN clause in your handoff packet so reviewers can tell whether your selection is justified or arbitrary.

```
TIER 3 (10) - macro shape of one capability
TIER 2 (23) - composes inside Tier 3
TIER 4 (4)  - source-time refactors that re-shape the module graph
```

## Tier 3 -- Architectural patterns

Macro shapes a capability takes. Pick one (sometimes two) per non-trivial design. Each composes several Tier-2 patterns plus substrate primitives. See [Architectural patterns (A1-A10)](/genesis/reference/patterns/architectural/).

| AI-native name        | Classical analog                            | One-line tagline |
|-----------------------|---------------------------------------------|------------------|
| [A1. PANEL](/genesis/reference/patterns/a1-panel/) | Microservices + Gateway | N specialized lenses + one synthesizer; the workhorse of multi-perspective deliberation. |
| A2. PIPELINE          | Pipes-and-Filters                           | Linear stages with verifiable hand-offs; the canonical PLAN / TASKS / IMPLEMENT spine. |
| A3. ORCHESTRATOR-SAGA | Saga                                        | Long-lived multi-step transaction with per-step compensation across triggers. |
| A4. STAFFED PLAN      | Workflow Engine                             | Each todo names the persona / skill the executor must load. |
| A5. WAVE EXECUTION    | Build Pipeline (CI stages)                  | Topologically-sorted tasks gated wave-by-wave; re-plan from the failed wave. |
| A6. EVENT-DRIVEN      | Event-Driven Architecture                   | Triggers fire handlers; loose coupling; cadence is event-shaped. |
| A7. ADVERSARIAL REVIEW | Code Review + Red Team                     | Cold-context reviewers whose job is to break the artifact, not bless it. |
| A8. ALIGNMENT LOOP    | Iteration with stop-condition + steward     | Bounded round body + B9 steward; converges on goal alignment, not byte equality. |
| A9. SUPERVISED EXECUTION | Plan-Execute-Verify with controller      | Plan, run via S7 deterministic bridge, verify via another tool call. Two enforcement forms (weak / strong). |
| [A10. GOVERNED OUTER LOOP](/genesis/reference/patterns/a10-governed-outer-loop/) | CI/CD + capability-bounded service account | Sandboxed event-driven A6 + strong-form A9 + audit; agent never holds the write token. |

## Tier 2 -- Design patterns

The 23-pattern catalogue an architect picks from when shaping ONE piece of work. Cut on the Gang-of-Four axes so a classical software architect lands on familiar ground. See [Design patterns (C1-C6, S1-S7, B1-B10)](/genesis/reference/patterns/design/).

### Creational (6) -- how primitives come into being

| ID | Name | Tagline |
|----|------|---------|
| C1 | LAZY ASSET | Defer asset load until the step that needs it. |
| C2 | PERSONA PRELOAD | Load a stable lens at session start (with GROUNDED EXPERT BRIEFING sub-rule). |
| C3 | THREAD SPAWN | Fork a fresh context window for an isolated unit of work. |
| C4 | DESCRIPTION DISPATCH | Dispatcher LLM picks the module by frontmatter description (signature match). |
| C5 | PERSONA PROTOTYPE | Base persona + thin variant deltas; avoid persona copy-paste. |
| C6 | EXTERNAL CORPUS GROUNDING | Lazy fetch from a named, authoritative source with a bounded scope sub-rule. |

### Structural (7) -- how primitives compose at rest

| ID | Name | Tagline |
|----|------|---------|
| S1 | COMPOSED MODULE | Orchestrator depends on leaf modules; no content duplication. |
| S2 | DEPENDENCY ADAPTER | Architect persona ignorant of concrete syntax; adapter file translates. |
| S3 | ORCHESTRATOR FACADE | One callable signature in front of an internally complex topology. |
| S4 | VALIDATION DECORATOR | Wrap a producing step with a deterministic pass/revise gate. |
| S5 | LAZY PROXY | Path reference materialized on demand by the runtime. |
| S6 | RULE BRIDGE | Voice in personas, constraints in scope-attached rule files; vary independently. |
| S7 | DETERMINISTIC TOOL BRIDGE | Cross the LLM/CPU boundary explicitly via tools; do not regenerate the artifact in prose. |

### Behavioral (10) -- how primitives interact at run

| ID | Name | Tagline |
|----|------|---------|
| B1  | FAN-OUT + SYNTHESIZER | Master-Worker; engine inside A1 PANEL. |
| B2  | CONDITIONAL DISPATCH | Strategy; pick the branch by input class. |
| B3  | SUPERVISOR | Bounded supervision tree; workers do not spawn workers. |
| B4  | PLAN MEMENTO | Externalize plan state; reload at every re-grounding boundary. |
| B5  | ACCEPTANCE OBSERVER | Read the criterion before reading the implementation; mismatch is drift. |
| B6  | PROMPT TEMPLATE | Template Method; shared skeleton, slot-filling content. |
| B7  | TODO COMMAND | Each todo is a serialized, dispatchable command. |
| [B8](/genesis/reference/patterns/b8-attention-anchor/) | ATTENTION ANCHOR | Re-inject goal + hard constraints at scheduled boundaries. The dominant cure for goal drift. |
| B9  | GOAL STEWARD | Named owner of "alignment to original intent". |
| B10 | HUMAN CHECKPOINT | Approval gate at irrecoverable / drifted / unauthorized boundaries. |

## Tier 4 -- Refactor patterns

Source-time restructurings of the module graph. Run BEFORE re-picking a Tier-2 / Tier-3 pattern; restructuring often dissolves the need for a more elaborate runtime topology. See [Refactor patterns (R1-R4)](/genesis/reference/patterns/refactor/).

| ID | Name | Tagline |
|----|------|---------|
| R1 | SPLIT   | Decompose an over-broad module along a natural seam. |
| R2 | FUSE    | Merge siblings whose descriptions collide or that are always co-invoked. |
| R3 | EXTRACT | Promote inlined content to its own primitive when reuse / lens / cadence justifies it. |
| R4 | INLINE  | Collapse a thin proxy that exists only to forward to one target. |

## How to use this catalogue

1. Read the [architectural patterns page](/genesis/reference/patterns/architectural/) and find the Tier-3 shape that matches your capability's macro topology. Cite its WHEN clause.
2. List the Tier-2 patterns that compose inside that shape (each Tier-3 entry names them explicitly).
3. Run the Tier-4 refactor triggers across the existing module graph. Apply any that fire BEFORE you finalize the Tier-3 / Tier-2 selection.
4. When two patterns from the same tier fit equally, name the matrix that cut your choice in the handoff packet.

## Dedicated deep-dives

Three patterns earn their own focus pages because they carry outsized weight in real designs:

- [A1 PANEL](/genesis/reference/patterns/a1-panel/) -- the multi-lens deliberation workhorse.
- [A10 GOVERNED OUTER LOOP](/genesis/reference/patterns/a10-governed-outer-loop/) -- the substrate-bound, audit-surfaced realization for any work that externalizes state.
- [B8 ATTENTION ANCHOR](/genesis/reference/patterns/b8-attention-anchor/) -- the LLM-physics-native cure for goal drift.

## Further reading

- [Agentic SDLC Handbook, Chapter 11 -- Context Engineering](https://danielmeppiel.github.io/agentic-sdlc-handbook/handbook/ch11-context-engineering.html) -- the LLM-physics theory motivating B4 + B8.
- [Agentic SDLC Handbook, Chapter 12 -- Multi-Agent Orchestration](https://danielmeppiel.github.io/agentic-sdlc-handbook/handbook/ch12-multi-agent-orchestration.html) -- the long-form companion for A1 / A4 / A5 / A8.
- [Agentic SDLC Handbook, Chapter 14 -- Anti-Patterns and Failure Modes](https://danielmeppiel.github.io/agentic-sdlc-handbook/handbook/ch14-anti-patterns-and-failure-modes.html) -- a deeper inventory of the failures these patterns prevent.
