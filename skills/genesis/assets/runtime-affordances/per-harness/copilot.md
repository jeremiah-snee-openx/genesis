# Per-Harness Adapter: GitHub Copilot

Maps the substrate (../common.md) to GitHub Copilot's concrete
affordances. Load this file ONLY when a primitive declares Copilot
as a target.

Official docs cited:
- https://docs.github.com/en/copilot/reference/custom-agents-configuration
  (CANONICAL custom agent frontmatter spec -- `model`, `tools`, `target`,
  `disable-model-invocation`, `user-invocable`, `mcp-servers`)
- https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/create-custom-agents-for-cli
- https://docs.github.com/en/copilot/concepts/agents/coding-agent/about-hooks
- TODO: official docs needed for agent spawning / task tool syntax
- TODO: official docs needed for trigger orchestration / workflows

## 1. PERSONA SCOPING FILE

In Copilot: Custom Agent
- File extension: .agent.md
- Folder: .github/agents/ (project-local) or .copilot/agents/ (CLI user-scope)
- Frontmatter fields (per CANONICAL spec linked above):
  - `name` (string, optional display name)
  - `description` (string, REQUIRED)
  - `model` (string, optional) -- "Model to use when this custom agent
    executes. If unset, inherits the default model." This is the
    PER-AGENT BINDING SITE that B12 MODEL ROUTER reaches for on Copilot.
    Concrete model identifiers come from the live Copilot models &
    pricing page (`docs.github.com/en/copilot/reference/copilot-billing/models-and-pricing`);
    examples: `claude-sonnet-4.6`, `claude-opus-4.7`, `gpt-5-mini`,
    `gpt-4o-mini`. Do NOT hardcode names in the design (B12 anti-pattern);
    bind at codegen time from the role-class table in section 9.
  - `tools` (list of strings or comma string, optional) -- "If unset,
    defaults to all tools." This is the PER-AGENT BINDING SITE that
    B15 TOOL SUBSET reaches for on Copilot. Aliases: `read`, `edit`,
    `search`, `execute`, `agent`, `web`, `todo`. MCP server tools
    namespaced as `<server>/<tool>` or `<server>/*`. Empty list `[]`
    disables all tools.
  - `target` (string, optional) -- `vscode` | `github-copilot`; if
    unset, both. Use to scope agents that only make sense in one host.
  - `disable-model-invocation` (bool, optional) -- when true, agent
    must be manually selected (cloud-agent context). FORCED vs
    DISCOVERY dispatch knob.
  - `user-invocable` (bool, optional) -- when false, agent is
    programmatic-only (cannot be picked by a human).
  - `mcp-servers` (object, optional) -- per-agent MCP server config
    (NOT used in VS Code IDE; used in cloud agent + CLI).
  - `metadata` (object, optional) -- annotation key/value.
- Activation: loaded when user selects agent from UI, or via CLI agent
  invocation, or automatically by cloud agent based on task context
  (unless `disable-model-invocation: true`).
- Notes: agent name for deduplication derived from filename stem (minus
  `.md` or `.agent.md`); lowest-level config wins (repo > org > enterprise).
  Prompt body capped at 30,000 characters.
- Source: https://docs.github.com/en/copilot/reference/custom-agents-configuration

## 2. MODULE ENTRYPOINT (SKILL)

In Copilot: Skill (agentskills.io standard)
- Entrypoint file name: SKILL.md
- Folder: .github/skills/<skill_name>/ (where <skill_name> is hyphen-case,
  max 64 chars per agentskills.io)
- Frontmatter fields: `name`, `description` ONLY (per the canonical
  agentskills.io spec linked from `assets/primitives.md`).
- IMPORTANT -- skill frontmatter does NOT support `model:` or `tools:`.
  Those fields exist ONLY on `.agent.md` custom-agent profiles (section 1).
  Architectural consequence: B12 MODEL ROUTER and B15 TOOL SUBSET CANNOT
  be applied at the SKILL level on Copilot. To bind a model or scope
  tools for a unit of work, you MUST express that unit as a custom agent
  (`.agent.md`), not as a skill. If the design currently has a skill
  that needs per-element model binding, split or relocate it: either
  make the skill body delegate to a sibling `.agent.md`, or restructure
  the unit as a custom agent and have the skill load it.
- Assets folder: assets/ (arbitrary files loaded on demand from SKILL.md steps)
- Activation: description-driven matching by Copilot when user task aligns
  with skill description; also discoverable via skill commands
- Notes: skill name normalized to hyphen-case at deployment; SKILL.md
  deployed as SKILL.md at skill root (not renamed). Aligns with
  agentskills.io registry contract; description is the primary search key.
- Source: https://docs.github.com/en/copilot/customizing-copilot/adding-custom-instructions-for-github-copilot

## 3. SCOPE-ATTACHED RULE FILE

In Copilot: Instruction file
- File extension: .instructions.md
- Folder: .github/instructions/ (project-local) or .copilot/instructions/ (CLI user-scope)
- Scope mechanism: applyTo: frontmatter field (glob pattern over file paths,
  e.g. applyTo: "**/*.py" or applyTo: "src/**")
- Notes: instruction files are automatically loaded into any thread whose
  work path matches the glob. At user scope, instructions are visible to
  all projects. Pattern matching happens per-thread at runtime.
- Source: https://docs.github.com/en/copilot/customizing-copilot/adding-custom-instructions-for-github-copilot

## 4. CHILD-THREAD SPAWN

In Copilot: TODO: official docs needed
- Mechanism: TODO (likely GitHub Copilot agent tool or equivalent;
  exact syntax TBD pending official documentation)
- Parallelism: TODO
- Persona loading: TODO (child agent can reference a .agent.md?)
- Notes: Copilot agent architecture implies agent-to-agent spawning but
  concrete spawn mechanism not yet documented in accessible sources.
- Source: TODO: official docs needed

## 5. TRIGGER ORCHESTRATOR

In Copilot: TODO: official docs needed
- File format: TODO (likely .github/workflows/ YAML or equivalent)
- Trigger declaration: TODO (events, schedule, user action)
- Session bootstrap: TODO (how initial skills/agents are loaded)
- Output channel: TODO (where results are posted)
- Notes: Copilot CLI supports agents but orchestration/scheduling mechanics
  are not fully documented in current accessible GitHub docs.
- Source: TODO: official docs needed

## 6. PLAN PERSISTENCE

In Copilot CLI: built-in per-session state directory.
- PLAN slot: `~/.copilot/session-state/<session_id>/plan.md`
  (plain markdown; created/edited freely; toggled in via plan mode
  with Shift+Tab)
- TODO/STATUS slot: per-session SQLite database with `todos` and
  `todo_deps` tables exposed via the `sql` tool; statuses
  `pending` | `in_progress` | `done` | `blocked`; dependencies
  expressed as edges
- CHECKPOINT slot:
  `~/.copilot/session-state/<session_id>/checkpoints/<NNN>-<title>.md`
  (auto-emitted at meaningful milestones; `index.md` lists them)
- FILES slot: `~/.copilot/session-state/<session_id>/files/`
  for non-committable artifacts that survive checkpoints
- Notes: re-grounding pattern is to read plan.md early in each
  major phase and to query the todos table for ready items;
  `report_intent` surfaces current intent in the UI in parallel
- Source: TODO: official docs page that names the session-state
  layout (the layout is documented in-session via the `<session_context>`
  block injected into the agent prompt)

## Capabilities Copilot lacks (vs substrate)

- Explicit child-thread spawn syntax: agent spawning is not yet publicly
  documented. Workaround: design skills with self-contained steps rather
  than fan-out (see design-patterns.md Behavioral section); consider
  multi-agent composition via skill descriptions matching.
- Cross-session state: CLI sessions are stateless. Workaround: persist
  state to git or external store; load via task description or skill
  asset imports.
- Built-in event scheduler: Copilot CLI has no native cron. Workaround:
  use external cron/Actions to invoke copilot CLI with seeded prompts.

## Capabilities unique to Copilot (beyond substrate)

- MCP server integration: Copilot CLI and GitHub Copilot support Model
  Context Protocol (MCP) servers for tool extension via ~/.copilot/mcp-config.json.
  This is NOT part of the substrate but is a rich extension point for
  primitives that need tool access beyond native Copilot affordances.
- GitHub Actions integration: Copilot agents can be invoked from Actions
  workflows, bridging repo automation and agent reasoning.

## 9. MODEL CATALOG & BILLING (cost-economics)

Maps the abstract role classes in `../model-catalog.md` to concrete
SKUs offered through GitHub Copilot and to Copilot's premium-request
billing surface. The genesis architect designs in role classes; this
adapter binds them at codegen time.

Verified on: 2025-11-14. Always re-verify multipliers against the
live billing page before quoting; they age out.

### Role class -> concrete model (defaults)

| Role class             | Default SKU                       | Alternative                          |
|------------------------|------------------------------------|--------------------------------------|
| planner                | Claude Opus / GPT-5 (premium tier) | Claude Sonnet 4.x for cost balance   |
| implementer            | Claude Sonnet 4.x / GPT-5 standard | (none -- this IS the default tier)   |
| reviewer               | Claude Sonnet 4.x / GPT-5 standard | GPT-5 mini for checklist work        |
| trivial                | GPT-4o mini / GPT-5 mini           | (none)                               |
| long-context-retriever | Gemini Pro (where offered)         | GPT-5 with extended context          |

### Billing surface

Premium request multipliers. One premium request abstracts the
underlying token cost; different models charge different multipliers
per request. Subscription plan determines monthly included quota;
overage bills per request.

Source: https://docs.github.com/en/copilot/reference/copilot-billing/models-and-pricing
(read the live page; per-model multipliers are updated by GitHub
without prior notice).

### Cost-pattern bindings

CRITICAL -- READ FIRST. The PER-AGENT BINDING SITE on Copilot is the
`.agent.md` custom-agent frontmatter (section 1). It is the ONLY
Copilot primitive whose frontmatter accepts `model:` and `tools:`.
SKILL.md does NOT support these fields (see section 2). When a
B12 / B15 / B16 binding is required, the unit of work MUST be
expressed as a custom agent. If a skill currently holds the unit,
either restructure it as a `.agent.md` or have the skill body
delegate to a sibling `.agent.md` whose frontmatter carries the
binding.

- B12 MODEL ROUTER:
  - BINDING SITE: `.agent.md` frontmatter `model:` field, one
    binding per custom agent. Each fan-out lens / arbiter / classifier
    is its OWN `.agent.md` with its OWN `model:` line, picked from
    the role-class table above. Default-binding-by-omission is
    "inherit the session model" -- that is single-model uniform
    binding, which is what fired (or rather, did NOT fire) in PR #12's
    Executor B run. To actually fire B12, populate `model:` per agent.
  - Session-level fallback: configure model preference per CLI
    session or per workflow if NO per-agent override is set. Mid-
    session switch is supported but partitions the Copilot cache
    (B13 anti-pattern -- avoid).
  - ANTI-PATTERN unique to Copilot: SKILL-LEVEL ROUTING ATTEMPT --
    adding `model:` to SKILL.md frontmatter has no effect (silently
    ignored). Symptom: architect believes B12 is firing; profiling
    shows uniform model billing. Fix: move the unit to `.agent.md`.

- B13 CACHE-AWARE PREFIX: caching behavior is opaque to the operator
  (handled by Copilot's backend); cache discipline still pays off
  because the underlying providers cache. Keep persona / skill body
  stable; avoid mid-session edits to `.github/copilot-instructions.md`.
  Mid-session `model:` switch (see B12) also invalidates the cache --
  bind at agent definition time, not at runtime.

- B15 TOOL SUBSET:
  - BINDING SITE: `.agent.md` frontmatter `tools:` field, one
    binding per custom agent. Use either a list of aliases
    (`tools: ["read", "search"]`) or an empty list (`tools: []`) to
    disable all tools. MCP server tools namespaced as
    `<server>/<tool>` or `<server>/*`. Available aliases per the
    custom-agents-configuration spec: `read`, `edit`, `search`,
    `execute`, `agent`, `web`, `todo`.
  - SKILL.md does NOT support `tools:`. Skill-level tool subsetting
    has to be done via the surrounding session config or by routing
    the work to a `.agent.md` with the scoped subset.
  - Session-level fallback: declare per-MCP-server scoping in
    `.copilot/config.yml` to keep the catalogue bounded for the
    whole session.

- B16 EFFORT GOVERNOR: where the model supports it, declare via the
  model selection (a "high effort" SKU IS the effort declaration on
  Copilot's surface). Combine with B12 binding on `.agent.md` to
  pick a high-effort SKU only for the high-stakes agentic element.

### Stance binding

Operator declares stance in the first prompt OR in
`.github/copilot-instructions.md` as `stance: <value>`. The
genesis-architect persona reads it at step 1.
