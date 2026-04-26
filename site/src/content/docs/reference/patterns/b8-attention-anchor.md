---
title: B8. ATTENTION ANCHOR
description: The behavioral pattern with no classical analog. Re-inject goal, hard constraints, and acceptance criterion at scheduled boundaries to fight LLM attention decay. The dominant cure for goal drift in agentic work past trivial scope.
---

B8 ATTENTION ANCHOR is the single most important behavioral pattern for any non-trivial agent task. It has no faithful classical counterpart -- it is induced by LLM physics (attention decay over distance / over turns) rather than by software-engineering structure.

## Verbatim definition

> CLASSICAL ANALOG: NONE. This pattern has no faithful classical counterpart -- it is induced by LLM physics (attention decay over distance / over turns) rather than by software-engineering structure. It is, however, the single most important behavioral pattern for any non-trivial agent task.
>
> WHEN: any session that will exceed roughly a few dozen turns, or any plan whose acceptance criterion / hard constraints were established at turn 0 and must still hold at turn N. Long-running tasks WITHOUT periodic re-injection of the goal and hard constraints DRIFT silently from initial intent. This is the dominant failure mode of agentic work past trivial scope.
>
> MECHANISM: the goal, the hard constraints, and the acceptance criterion are RE-INJECTED into context at scheduled boundaries:
>
> - start of every meaningful step,
> - before any spawn,
> - after any spawn returns,
> - after any tool failure or error recovery,
> - at any natural pause in execution.
>
> The re-injection draws from PLAN MEMENTO (B4) -- the anchor's source of truth lives outside the context window so it cannot itself decay.

## Schedule

```
turn 0    [GOAL + CONSTRAINTS injected, fresh context]
   |
turn 5    do work...
   |
turn 10   <-- re-inject GOAL + CONSTRAINTS from plan
   |
turn 15   do work, spawn child
   |
turn 16   <-- re-inject before spawn (child gets anchor in its task)
   |
turn 20   spawn returns
   |
turn 21   <-- re-inject after spawn (parent recovers focus)
   |
turn 30   acceptance check (B5 reads the same anchor)
```

The anchor is NOT the full plan body. It is GOAL + HARD CONSTRAINTS + ACCEPTANCE CRITERION. Anything more dilutes the savings of the original decomposition. Anything less is not an anchor.

## Composition

> COMPOSES WITH:
> - [PLAN MEMENTO (B4)](/genesis/reference/patterns/design/#b4-plan-memento) is the storage substrate.
> - [ACCEPTANCE OBSERVER (B5)](/genesis/reference/patterns/design/#b5-acceptance-observer) reads the same anchor at the end.
> - [SUPERVISOR (B3)](/genesis/reference/patterns/design/#b3-supervisor) re-injects the anchor on every dynamic re-plan.

The triangle B4 + B5 + B8 is the smallest recipe that gives a long-running agent task any chance of staying aligned:

- B4 owns durable state.
- B8 re-grounds the running session against B4 at every meaningful boundary.
- B5 reads B4 at the end and verifies that the implementation matches the criterion stored at turn 0, without inheriting the executor's state.

When you also have multi-thread orchestration, [B3 SUPERVISOR](/genesis/reference/patterns/design/#b3-supervisor) is responsible for re-injecting the anchor on every re-plan event, and [B9 GOAL STEWARD](/genesis/reference/patterns/design/#b9-goal-steward) owns the role of "named arbiter of alignment" -- B9 is the procedural counterpart to B8's token-budget cure.

## Anti-patterns (verbatim)

> - **ANCHOR DRIFT** -- silently rewriting the anchor mid-session to match emerging results. The anchor is now a description, not a constraint. Only revise via an explicit re-plan event (mirror of ACCEPTANCE-DRIFT).
> - **OVER-ANCHORING** -- re-injecting the entire plan on every turn. The anchor is meant to be the GOAL + the hard constraints, not the full plan body. Re-injecting too much defeats the savings of the original decomposition.
> - **IMPLICIT-ANCHOR** -- assuming the model "remembers" the goal because it was stated at turn 0. Attention decays over distance; the early tokens lose influence. Explicit re-injection or no anchor.

### Why IMPLICIT-ANCHOR is the dominant failure

Senior engineers tend to assume the LLM "has" the goal once it has been stated. It does not. The goal token sequence loses attention weight as the context window fills with execution-time tokens. By turn 50 the early goal statement competes for attention with 49 turns of intermediate output and tool results -- usually it loses. The execution thread starts solving a NEAR-NEIGHBOUR problem (the most recently-discussed subtask) instead of the original problem (the goal stated at turn 0).

The cure is not "remind the LLM more politely". The cure is structural: ALWAYS persist goal + criterion in [B4](/genesis/reference/patterns/design/#b4-plan-memento), and re-inject them at the scheduled boundaries above. The persistence is what makes the anchor immune to its own decay.

### Why OVER-ANCHORING is the second-order failure

Once an architect understands B8, the next failure mode is to inject the FULL plan at every boundary. The per-turn cost of injecting the full plan defeats the savings the decomposition was meant to give. The anchor is the GOAL + HARD CONSTRAINTS + ACCEPTANCE CRITERION, not the plan. Sub-task detail belongs in the per-task spawn payload, not in every parent re-injection.

## Why this is first-class

> WHY THIS IS FIRST-CLASS. Every other behavioral pattern assumes the agent stays aligned with the original intent across the work. Without ATTENTION ANCHOR, that assumption is false on any task long enough to matter. It is the cure for the deepest LLM failure mode in multi-step execution.

In short: B4 is the storage substrate; B5 is the closing gate; B8 is the discipline that keeps every step in between aligned. Without B8 you have artifacts and a final check around an executor that drifts.

## Cross-references

- [Design patterns catalogue (B series)](/genesis/reference/patterns/design/)
- [B4 PLAN MEMENTO](/genesis/reference/patterns/design/#b4-plan-memento) -- the storage substrate
- [B5 ACCEPTANCE OBSERVER](/genesis/reference/patterns/design/#b5-acceptance-observer) -- the closing gate that reads the same anchor
- [B9 GOAL STEWARD](/genesis/reference/patterns/design/#b9-goal-steward) -- the procedural counterpart (named owner of alignment)
- [Agentic SDLC Handbook, Chapter 11 -- Context Engineering](https://danielmeppiel.github.io/agentic-sdlc-handbook/handbook/ch11-context-engineering.html) -- the LLM-physics theory
- [Agentic SDLC Handbook, Chapter 14 -- Anti-Patterns and Failure Modes](https://danielmeppiel.github.io/agentic-sdlc-handbook/handbook/ch14-anti-patterns-and-failure-modes.html) -- broader inventory of drift failures
