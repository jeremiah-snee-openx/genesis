---
title: External corpus
description: Three external bodies of work genesis composes with -- APM (microsoft/apm), agentskills.io, and the Agentic SDLC Handbook. Each has a bounded scope; importing one's framing into questions it does not own is AUTHORITY OVERREACH.
---

Genesis grounds itself in three external sources. Each is authoritative for a NARROW surface. Knowing the boundary is the difference between citing them correctly and committing the AUTHORITY OVERREACH anti-pattern named in [C6 EXTERNAL CORPUS GROUNDING](/genesis/reference/patterns/design/#c6-external-corpus-grounding).

## APM (`microsoft/apm`)

**Repository:** [github.com/microsoft/apm](https://github.com/microsoft/apm)

**What it is:** Agent Package Manager. A package manager for agent primitives -- skills, agents, instructions, gh-aw workflows -- under a `.apm/` directory in any repo. Provides an install / init / run lifecycle, a manifest format, a lockfile, dependency resolution, and authentication for fetching primitives from public + private remotes (GitHub, ADO).

**Authoritative for:**

- The dependency / lockfile schema for agent primitives.
- The install / init / run command surface.
- The marketplace / package addressing format.
- Integration with gh-aw workflows.

**NOT authoritative for:**

- The DESIGN of an individual primitive (skill structure, persona scoping, rule layout) -- that is the genesis catalogue's surface.
- The runtime topology of multi-thread agent work -- that is the [Tier-3 architectural patterns](/genesis/reference/patterns/architectural/) surface.

**How it composes with genesis:** APM ships agent primitives that genesis-designed packages would publish. A genesis design produces a primitive plan; APM is one shipping target for the result. Genesis-shaped output is APM-publishable but not APM-specific.

## agentskills.io

**Site:** [agentskills.io](https://agentskills.io)

**What it is:** Industry-standard convention for the SKILL.md container surface across multiple harness vendors. Defines the frontmatter shape (name, description, model, tools), body budget guidance, layout conventions, scripts directory conventions, and evals patterns.

**Authoritative for:**

- The SKILL.md container surface (frontmatter, body budget, layout, scripts conventions, evals).
- Harness-portable conventions for the SKILL primitive.

**NOT authoritative for** (this is the bounded-scope sub-rule of C6, applied):

- The genesis primitive taxonomy (genesis names six primitives -- persona scoping file, module entrypoint, scope-attached rule file, child-thread spawn, trigger orchestrator, plan persistence -- of which SKILL is one realization of MODULE ENTRYPOINT).
- The architectural ([Tier-3](/genesis/reference/patterns/architectural/)) and design ([Tier-2](/genesis/reference/patterns/design/)) pattern catalogues.
- The refactor ([Tier-4](/genesis/reference/patterns/refactor/)) discipline.

**How it composes with genesis:** A genesis-designed MODULE ENTRYPOINT, when realized as a SKILL.md, follows the agentskills.io container surface. Genesis owns the "is this one primitive or N? what shape does the work need?" decisions; agentskills.io owns the "what does the SKILL.md file look like?" decisions. The two compose; neither subsumes the other.

If a genesis design ships a MODULE ENTRYPOINT, it MUST conform to the agentskills.io container surface. If a SKILL.md has been authored without a genesis design, it has skipped the architecture step -- that is a smell, not a contradiction.

## Agentic SDLC Handbook

**Site:** [danielmeppiel.github.io/agentic-sdlc-handbook](https://danielmeppiel.github.io/agentic-sdlc-handbook/)

**What it is:** A long-form companion book covering the Agentic SDLC: how teams plan, build, review, ship, and maintain software whose work is increasingly performed by LLM-driven agents. Where genesis is a tactical skill (one architect, one design, one capability), the handbook is the strategic complement (how the practice scales across teams, programs, and time).

**Authoritative for:**

- The full theory of LLM context engineering, attention decay, multi-agent orchestration, and why the Tier-2 patterns work the way they do.
- Anti-pattern catalogues at scale (program-level, not just primitive-level).
- The lifecycle of agent-authored artifacts (review, evaluation, observability, maintenance).
- The vendor / harness landscape and the tradeoffs between them.

**NOT authoritative for:**

- The exact mechanical procedure of a single design session (genesis owns that -- the eight-step process in SKILL.md).
- The exact pattern names and verbatim WHEN clauses (genesis is the canonical name registry; the handbook explains the patterns at greater depth and refers to the genesis names).

**How it composes with genesis:**

- Genesis is the tactical skill: load SKILL.md, apply the eight-step process, produce a design.
- The handbook is the strategic companion: read once for theory, dip in for chapter-level deep dives.

Recommended chapters for genesis users:

- [Chapter 11 -- Context Engineering](https://danielmeppiel.github.io/agentic-sdlc-handbook/handbook/ch11-context-engineering.html) -- the LLM-physics theory motivating [B4 PLAN MEMENTO](/genesis/reference/patterns/design/#b4-plan-memento) + [B8 ATTENTION ANCHOR](/genesis/reference/patterns/b8-attention-anchor/).
- [Chapter 12 -- Multi-Agent Orchestration](https://danielmeppiel.github.io/agentic-sdlc-handbook/handbook/ch12-multi-agent-orchestration.html) -- long-form companion for [A1 PANEL](/genesis/reference/patterns/a1-panel/), [A4 STAFFED PLAN](/genesis/reference/patterns/architectural/#a4-staffed-plan), [A5 WAVE EXECUTION](/genesis/reference/patterns/architectural/#a5-wave-execution), [A8 ALIGNMENT LOOP](/genesis/reference/patterns/architectural/#a8-alignment-loop-bounded-iteration-with-goal-steward).
- [Chapter 14 -- Anti-Patterns and Failure Modes](https://danielmeppiel.github.io/agentic-sdlc-handbook/handbook/ch14-anti-patterns-and-failure-modes.html) -- extended inventory of the failures these patterns prevent.

## How to cite an external source correctly

Every external grounding declaration in a genesis design MUST state explicitly what the corpus is authoritative FOR. Examples of correct citations:

- "Per agentskills.io's frontmatter convention, the description field is a function signature and not marketing copy."
- "Per APM's lockfile schema, the package address pins both source and integrity hash."
- "Per the Agentic SDLC Handbook, Chapter 11, attention decays over distance, motivating B8 ATTENTION ANCHOR."

Examples of AUTHORITY OVERREACH (incorrect):

- "Per agentskills.io, the architecture should fan out into N personas." (agentskills.io does not own architecture.)
- "Per APM, this primitive should compose with B1." (APM does not own pattern selection.)
- "Per the Agentic SDLC Handbook, the SKILL.md frontmatter must include `model: claude-sonnet-4`." (the handbook does not own the SKILL container surface.)

When in doubt, name the surface and cite the boundary.
