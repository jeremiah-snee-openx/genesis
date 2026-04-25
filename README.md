<p align="center">
  <img src="assets/branding/logo.svg" alt="genesis" width="180" />
</p>

<h1 align="center">genesis</h1>

<p align="center">
  <strong>Markdown that steers an LLM is code. Design it before you write it.</strong>
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/github/license/danielmeppiel/genesis?style=flat" alt="License"></a>
  <a href="https://github.com/danielmeppiel/genesis/commits/main"><img src="https://img.shields.io/github/last-commit/danielmeppiel/genesis?style=flat" alt="Last Commit"></a>
</p>

Genesis ports the software architect's role to agentic systems -- decomposition, contracts, and
cross-cutting concerns applied to workflows where LLMs are the runtime -- plus two patterns
classical architecture never needed, because attention degrades over distance and context windows
are not memory.

Install via [apm](https://github.com/microsoft/apm) (a package manager for AI agent primitives):

```bash
apm install danielmeppiel/genesis
```

---

## Does this match anything you ship?

- **The agent file that grew teeth.** Your `CLAUDE.md` (or `.cursor/rules`, or `.github/copilot-instructions.md`) was forty lines. It is now four hundred. The agent ignores half of it and you cannot tell which half. *(God Module: Single Responsibility violated from the first commit. No seam was named before writing began.)*
- **Great at turn one, confidently wrong by turn twenty.** The early constraints slid out of attention as the later notes piled up. Re-pasting holds for two turns, then drifts again. *(Attention decay: the failure mode with no classical analog. Tokens far from focus lose influence on inference; the constraint is in the file but no longer steers the output.)*
- **The same paragraph in four places.** A convention copy-pasted across a skill, an instruction file, and a slash command. You edited one of them last week. The agent now contradicts itself depending on which one fires. *(Shotgun Surgery from hidden coupling. R3 EXTRACT -- promotes shared text to a module; dependents link to it. See [refactor-patterns.md](assets/refactor-patterns.md).)*

If two of these landed, keep reading.

---

## Quick Start

After install, open the AI tool you use (Claude Code, Cursor, GitHub Copilot, etc.) and paste this prompt verbatim:

```
Use the genesis-architect persona to design a skill that reviews my pull requests for missing
tests, undocumented public API, and unsafe migrations. Apply the full architect's loop: goal,
primitives, pattern, UML, acceptance, plan.
```

You will get a structured design output: a named pattern, a description of the execution shape, and an acceptance criterion. That output is what genesis produces. The skill file comes after.

> **Claude Code shortcut:** `@genesis-architect Use genesis to design...`  For other harnesses, see [Runtimes](#runtimes).

<details>
<summary>What does the genesis-architect persona look like?</summary>

[Read the source: genesis-architect.agent.md](agents/genesis-architect.agent.md). A role declaration, the six loop steps as standing instructions, and a severity rubric per step -- not a vague "you are an expert" prompt.

</details>

---

## The architect's role, ported

The six decisions a software architect makes map to agentic systems row for row. The code is Markdown; the runtime is an LLM; the structural failure modes are the same.

| Classical concern | Agent-architect equivalent | Genesis deliverable |
|---|---|---|
| Greenfield design | Partition a goal into agents, skills, and instruction scopes; define execution boundaries | Skill dependency graph + handoff packet + plan.md |
| Service decomposition | Identify where one agent ends and another begins; prevent skill coupling | Primitive dependency graph + R1 SPLIT (decompose oversized skill) when seams drift |
| Integration and contracts | Design skill inputs, outputs, and agent-to-agent handoffs | Interface sketch (trigger, inputs, outputs) + sequence diagram |
| Cross-cutting concerns | Auth context, safety rails, encoding rules that apply across all agents | Shared SCOPE-ATTACHED RULE FILEs + RULE BRIDGE pattern |
| Refactoring strategy | Identify drifted skills and conflicting instruction files; pay prompt debt | Skill refactor plan using R1-R4 patterns (see [refactor-patterns.md](assets/refactor-patterns.md)) |
| Architecture review | Evaluate proposed designs for consistency; prevent prompt sprawl | PANEL pattern (multi-lens review) + severity-rubric compliance check |

---

## What it produces

A common ask:

> *"Use the genesis-architect persona to design a skill that reviews my PRs -- checking for missing tests, undocumented public API, and unsafe migrations."*

Genesis produces this **before** writing any file.

**GOAL.** One reviewer that flags missing tests, undocumented public API, and unsafe migrations on a PR diff.

**PRIMITIVES.**
- `MODULE ENTRYPOINT` -- the `pr-review` skill itself.
- `CHILD-THREAD SPAWN` x 3 -- one per lens (tests, docs, migrations), each in a fresh context window.
- `PLAN PERSISTENCE` -- findings written to `pr-review.md` so a re-run on the same PR is comparable.

**PATTERN.** **Master-Worker** (genesis name: FAN-OUT + SYNTHESIZER). The parent spawns one worker per lens, each in a fresh context window. Independent inquiries with no shared state should never compete in the same window -- later lenses inherit attention drift from earlier ones.

The PR diff fans out to three threads (tests, docs, migrations), each in its own context window, then synthesizes back into `pr-review.md`.

**ACCEPTANCE.** On a PR with one missing test, one undocumented export, and a benign migration: the output names exactly two findings (no false positive on the migration), each citing the file path.

**PLAN.** `pr-review.md` written first. Only then does the agent author the skill, the persona, and the rule files.

This output is what the architecture buys you. The file you eventually write is the easy part.

---

## Primitives

Every harness implements the same six concepts under different folder names. Genesis names them once so the vocabulary outlives any one tool.

| Concept | What it is | Common terms |
|---|---|---|
| **PERSONA SCOPING FILE** | A document loaded at session start to scope who the agent is. | "agent file", "subagent", "mode" |
| **MODULE ENTRYPOINT** | A bundled, self-contained capability with assets and a contract. | "skill", "module" |
| **SCOPE-ATTACHED RULE FILE** | A constraint that auto-applies to a path or context. | "instruction", "rule", "memory" |
| **CHILD-THREAD SPAWN** | A primitive that creates a new context window running in parallel. | "subagent thread", "Task tool" |
| **TRIGGER ORCHESTRATOR** | A declarative pipeline that runs primitives on events. | "workflow", "hook", "automation" |
| **PLAN PERSISTENCE** | A stable artifact (file or DB) holding the active plan across turns. | "plan.md", "TODO state", "checkpoints" |

These names are deliberately generic. The architecture must outlive any one tool.

---

## Patterns

Genesis maps the Gang-of-Four onto agent design. The classical name is your Rosetta Stone; the AI-native name encodes the LLM-physics specifics (context isolation, attention decay).

| GoF axis | Classical | AI-native | When |
|---|---|---|---|
| Creational | Factory Method | THREAD SPAWN | Work benefits from a fresh context window |
| Structural | Facade | ORCHESTRATOR FACADE | A multi-step capability needs to look like one signature |
| Behavioral | Master-Worker | FAN-OUT + SYNTHESIZER | >=3 independent lenses, no shared state |
| Behavioral | *(no analog)* | **ATTENTION ANCHOR** | Re-inject goal + constraints at every re-grounding boundary |

**ATTENTION ANCHOR is the LLM-physics-native pattern with no classical counterpart**: without periodic re-injection of goal and hard constraints, long sessions silently drift from the original intent. It is the highest-leverage behavioral pattern for any non-trivial agent task.

Full catalogue (19 design patterns + 6 architectural patterns + 4 refactor patterns): [`assets/design-patterns.md`](assets/design-patterns.md), [`assets/architectural-patterns.md`](assets/architectural-patterns.md), [`assets/refactor-patterns.md`](assets/refactor-patterns.md).

---

## The architect's loop

```
1.  STATE GOAL          --> one sentence, observable outcome
2.  NAME PRIMITIVES     --> which substrate concepts will you use?
3.  PICK PATTERN        --> architectural shape, then design patterns; justify in one line
3.5 COMPOSE OR BUILD?   --> can an existing module satisfy this?
4.  DRAW UML            --> mermaid, validate it renders
5.  ACCEPTANCE          --> what proves it works?
6.  PERSIST PLAN        --> write plan.md (or equivalent) BEFORE coding
7.  IMPLEMENT           --> author files; commit
7b. RELOAD PLAN         --> on every meaningful turn, re-read the plan
8.  STOP CONDITION      --> ship, or stop the design
```

Steps 6 and 7b are non-negotiable. They realize **PLAN MEMENTO** (state outside the context window) and **ATTENTION ANCHOR** (re-inject goal + constraints on every meaningful turn). Together they defeat the silent drift that ends most long agent sessions.

---

## Runtimes

| Harness | Persona file format | Skill folder | Adapter |
|---|---|---|---|
| **Claude Code** | `.claude/agents/*.md` | `.claude/skills/` | [adapter](assets/runtime-affordances/per-harness/claude-code.md) |
| **GitHub Copilot CLI** | `.github/agents/*.agent.md` | `.github/skills/` | [adapter](assets/runtime-affordances/per-harness/copilot.md) |
| **Cursor** | `.cursor/rules/*.mdc` | `.cursor/skills/` | [adapter](assets/runtime-affordances/per-harness/cursor.md) |
| **OpenCode** | `.opencode/agent/*.md` | `.opencode/skills/` | [adapter](assets/runtime-affordances/per-harness/opencode.md) |
| **Codex** | `AGENTS.md` files | `~/.codex/skills/` | [adapter](assets/runtime-affordances/per-harness/codex.md) |

The primitives are the same. Only the file names change.

---

**MIT licensed.** If two failure modes above matched something you ship, [open an issue](https://github.com/danielmeppiel/genesis/issues/new) with which one -- that is the data that shapes the next pattern.
