---
title: Worked examples
description: Five complete designs produced by the genesis skill. Each cites the architectural pattern it realizes, the design patterns it composes, and the patterns it considered and rejected with WHEN-clause grounding.
---

Five designs produced by the genesis skill, in recommended reading order. Each is the verbatim output of an architect session that loaded SKILL.md and applied the eight-step process. Numbers 03-05 are cold-load runs from a fresh agent context (no prior conversation, no human cleanup).

| # | Example | What it shows |
|---|---------|---------------|
| 01 | [README iteration with an alignment loop](/genesis/resources/examples/01-readme-iteration/) | A8 ALIGNMENT LOOP applied to README iteration. Single skill, single goal-steward thread. |
| 02 | [Re-architecting a review panel](/genesis/resources/examples/02-review-panel-architecture/) | Re-architecture lesson: a multi-lens panel anti-pattern (everything in one thread) and the corrected design. |
| 03 | [Release notes (minimum viable single skill)](/genesis/resources/examples/03-release-notes-single-skill/) | Minimal output: 1 skill + 2 assets + 3 scripts. A9 SUPERVISED EXECUTION + S7 + S4. A1 PANEL considered and rejected (lens-count gate did not fire). |
| 04 | [PR review (advisory panel)](/genesis/resources/examples/04-pr-review-advisory/) | Multi-primitive panel: 6 personas + 4 assets + 3 scripts + trigger + entrypoint + rule + evals. A6 EVENT + A1 PANEL + DISSENT-WEIGHTED arbiter. R1 SPLIT considered, applied at lens content as R3 EXTRACT. |
| 05 | [PR review (verdict regime)](/genesis/resources/examples/05-pr-review-verdict/) | Same prompt as 04 with one constraint removed (verdict required). Regime change: deterministic bridges, schema gate, post-emit verifier loop, graceful tool probes. A8 ALIGNMENT LOOP, B5 ESCALATION, R1 SPLIT considered and rejected with WHEN-clause grounding. |

## How 03-05 were produced

A general-purpose agent received only:

1. Path to SKILL.md
2. The operator prompt verbatim (no genesis vocabulary)
3. Instructions to load assets per progressive disclosure
4. Constraints: cite patterns with WHEN-clause quotes, render mermaid, apply W6 / W6.2 / W6.3, ASCII-only, stop at step 6 handoff packet

No prior genesis context was carried in. The output is what the skill, cold-loaded, produced.

## Why ship them

The examples answer two questions the README cannot:

- **Does the skill produce the same output every time?** No. It is prompt-sensitive in a disciplined way. Compare 03 (single skill) to 04 (17 primitives) to 05 (regime change with hardened pipeline).
- **Can I trust the design choices?** Each example shows patterns CONSIDERED and REJECTED with WHEN-clause grounding. Most prompt engineering tools never show their rejection logic, so you cannot tell whether a design is justified or arbitrary.

## How to read them

Each example follows the same eight-step shape:

1. Operator prompt (verbatim).
2. Goal restated; success criteria pinned to [B4 PLAN MEMENTO](/genesis/reference/patterns/design/#b4-plan-memento).
3. Architectural pattern selection with WHEN-clause quote (the [Tier-3 catalogue](/genesis/reference/patterns/architectural/)).
4. Design pattern composition (the [Tier-2 catalogue](/genesis/reference/patterns/design/)).
5. Refactor passes considered ([Tier-4](/genesis/reference/patterns/refactor/)) -- applied or rejected with reasoning.
6. Handoff packet: primitives, dependencies, deterministic gates, anti-patterns to watch.
7. (Cut at step 6 for the cold-load runs.)

Read 01 first for the smallest viable composition, then 02 for the cautionary tale that anchors most architects' intuition for why [A1 PANEL](/genesis/reference/patterns/a1-panel/) needs fan-out across threads. After that, 03-04-05 in order shows the same architect facing escalating prompt complexity.
