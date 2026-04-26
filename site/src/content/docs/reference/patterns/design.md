---
title: Design patterns (C1-C6, S1-S7, B1-B10)
description: The 23-pattern Tier-2 catalogue an architect picks from when shaping ONE piece of work. Cut on the same axes as the Gang-of-Four -- Creational, Structural, Behavioral.
---

The catalogue an architect picks from when shaping ONE piece of work. Cut on the same three axes the Gang-of-Four uses for object-oriented design patterns (Creational / Structural / Behavioral), so a classical software architect lands on familiar ground.

Each entry below uses the verbatim Genesis definition: AI-native name, classical analog, when, mechanism, anti-patterns. Tier-3 [architectural patterns](/genesis/reference/patterns/architectural/) COMPOSE these. Tier-1 idioms realize them in a specific harness.

```
                    +---------------------------------+
                    |  TIER 2 design patterns         |
                    +---------------------------------+
                    |                                 |
   CREATIONAL              STRUCTURAL                 BEHAVIORAL
   (how primitives         (how primitives            (how primitives
    come into being)        compose at rest)           interact at run)
   ----------                ----------                ----------
   LAZY ASSET                COMPOSED MODULE           FAN-OUT + SYNTHESIZER
   PERSONA PRELOAD           DEPENDENCY ADAPTER        CONDITIONAL DISPATCH
   (with GROUNDED EXPERT     ORCHESTRATOR FACADE       SUPERVISOR
    BRIEFING sub-rule)       VALIDATION DECORATOR      PLAN MEMENTO
   THREAD SPAWN              LAZY PROXY                ACCEPTANCE OBSERVER
   DESCRIPTION DISPATCH      RULE BRIDGE               PROMPT TEMPLATE
   PERSONA PROTOTYPE         DETERMINISTIC TOOL        TODO COMMAND
   EXTERNAL CORPUS            BRIDGE                   ATTENTION ANCHOR (*)
    GROUNDING                                          GOAL STEWARD
                                                       HUMAN CHECKPOINT
```

(*) ATTENTION ANCHOR has no classical analog. It is the LLM-physics-native cure for goal drift on long sessions and earns first-class status in the catalogue. See its [dedicated page](/genesis/reference/patterns/b8-attention-anchor/).

---

# Creational patterns

How primitives, threads, and personas come into being.

## C1. LAZY ASSET

> CLASSICAL ANALOG: Lazy Initialization.
>
> WHEN: a MODULE ENTRYPOINT bundles knowledge that only some invocations need. Loading it eagerly inflates every session.
>
> MECHANISM: the SKILL.md body names the asset by relative path; the agent loads it only when the process step that needs it executes. The asset stays out of context until then.
>
> ANTI-PATTERN: EAGER BLOAT -- inlining the asset into SKILL.md "for convenience". Every dispatch hit pays the load cost.

---

## C2. PERSONA PRELOAD

> CLASSICAL ANALOG: Constructor / object initialization.
>
> WHEN: a thread needs a stable lens for the duration of its session.
>
> MECHANISM: the harness loads a PERSONA SCOPING FILE at session start, biasing all subsequent inference. The persona is the constructor that "new"s up the thread's identity.
>
> ANTI-PATTERN: MID-SESSION PERSONA SWAP -- swapping persona text mid-session. The earlier persona's tokens still occupy attention; the swap produces a hybrid lens that is neither.

**SUB-RULE -- GROUNDED EXPERT BRIEFING.** A persona declared as "expert in X" without grounding the persona in real X-corpus produces a NAMED-NOT-GROUNDED EXPERT: a confident voice with no factual anchor. Mitigation: the persona scoping file MUST point at the corpus the expert reads from (file paths, doc URLs, or asset references), and the briefing handoff to that thread MUST cite specific source artifacts the persona inspected before responding. A persona is its LENS plus its CITATIONS, not its title alone.

---

## C3. THREAD SPAWN

> CLASSICAL ANALOG: Factory Method (the runtime is the factory; the spawn call returns a fresh execution unit with its own context).
>
> WHEN: a unit of work benefits from a fresh context window -- isolation from siblings, full attention on its own scope.
>
> MECHANISM: parent invokes the harness's spawn affordance with a task description and (optionally) a persona / module to load at startup. Child runs, returns a value, exits.
>
> ANTI-PATTERN: UNBOUNDED SPAWN -- letting any thread spawn any depth of descendants. Couple with SUPERVISOR (B3) to bound the tree.

---

## C4. DESCRIPTION DISPATCH

> CLASSICAL ANALOG: Service Locator (the harness's dispatcher LLM locates the right MODULE ENTRYPOINT by signature match against preloaded descriptions).
>
> WHEN: any DISCOVERY-mode skill. The user does not name the skill; the dispatcher infers it from the user's turn.
>
> MECHANISM: at session start, the harness preloads every installed module's frontmatter description. On each user turn, the dispatcher chooses (probabilistically) which description best matches the request and invokes that module.

KEY PROPERTY: DESCRIPTION = FUNCTION SIGNATURE. The description names trigger nouns and verbs, the boundary, and the intended caller. It is not marketing copy.

> ANTI-PATTERN: DISPATCH COLLISION -- two installed modules with overlapping descriptions. The dispatcher guesses; ~half of misses go silent. HIGH severity finding in any review.

---

## C5. PERSONA PROTOTYPE

> CLASSICAL ANALOG: Prototype.
>
> WHEN: you need several persona variants that differ only in narrow parameters (lens severity, output format, audience). Writing N near-duplicate persona files duplicates the maintenance surface.
>
> MECHANISM: one base PERSONA SCOPING FILE captures the shared lens. Each variant is a thin file that links to the base and overrides only the delta. At spawn time, the parent loads base + delta into the child thread.
>
> ANTI-PATTERN: COPY-PASTE PERSONAS -- five persona files with 80% shared content. The shared text drifts; each lens behaves differently across runs for unrelated reasons.

---

## C6. EXTERNAL CORPUS GROUNDING

> CLASSICAL ANALOG: Dependency Injection from an external service + versioned read-through cache.
>
> WHEN: an agent must reason over facts that the LLM substrate cannot hold reliably -- because pretraining is frozen and cutoff-dated, or because the corpus changes faster than any model release. Examples: a third-party spec, a dependency's current API, a live repo state, the day's CHANGELOG.
>
> MECHANISM: at the step that needs the fact, the agent fetches it from a NAMED, AUTHORITATIVE source (URL, doc page, file path, tool output). The source identifier is captured in the handoff packet alongside the fetched content. Downstream readers can re-verify by re-fetching from the same source. The corpus is loaded LAZY (only at the step that needs it), not eager (at session start).

**BOUNDED SCOPE SUB-RULE.** Every external grounding declaration MUST state explicitly what the corpus is authoritative FOR. A spec is authoritative for its container surface, not for the broader ontology that wraps it. Importing an external corpus's framing into questions it does not own is AUTHORITY OVERREACH and is a HIGH-severity finding in review. Worked example: agentskills.io is authoritative for the SKILL.md container surface (frontmatter, body budget, layout, scripts conventions, evals). It is NOT authoritative for the genesis primitive taxonomy.

ANTI-PATTERNS:
- **STALE-CORPUS RELIANCE** -- citing a fact "as of training" without fetching from the named source.
- **UNVERIFIED CITATION** -- naming a source URL but not fetching from it. The source is decorative; the fact is still hallucinated.
- **AUTHORITY OVERREACH** -- expanding the corpus's authority beyond what it actually owns; importing its framing into ontology questions. The bounded-scope sub-rule exists to prevent this.
- **EAGER EXTERNAL FETCH** -- preloading a live source at session start "in case we need it". Live sources go stale; load lazy.

---

# Structural patterns

How primitives compose at rest. These are SOURCE-TIME relationships, realized through the module graph.

## S1. COMPOSED MODULE

> CLASSICAL ANALOG: Composite.
>
> WHEN: a high-order module's behavior is "load these N existing modules and orchestrate them".
>
> MECHANISM: the orchestrator module declares dependencies on the leaf modules and loads them at the relevant process step. No content is duplicated; each leaf evolves independently.
>
> ANTI-PATTERN: HIDDEN COUPLING -- copying a leaf's content into the orchestrator instead of depending on it. Drift is guaranteed.

---

## S2. DEPENDENCY ADAPTER

> CLASSICAL ANALOG: Adapter.
>
> WHEN: the architect's reasoning depends on an abstract substrate (a module-system-tool, a harness's runtime affordances) but the concrete syntax differs across tools / harnesses.
>
> MECHANISM: the architect persona is deliberately ignorant of the concrete syntax. A separate adapter file (`module-system-adapters/<tool>.md`, `runtime-affordances/per-harness/<harness>.md`) exposes the substrate's contract in the tool's own dialect. The coder thread loads the adapter at codegen time only.
>
> ANTI-PATTERN: LEAKY ABSTRACTION -- the architect persona naming `apm.yml`, `package.json`, `.cursor/rules`, etc. The reasoning becomes non-portable; redesigning for a new harness requires editing the architect.

---

## S3. ORCHESTRATOR FACADE

> CLASSICAL ANALOG: Facade.
>
> WHEN: an internally complex multi-step capability needs to be exposed to the dispatcher as a single callable signature.
>
> MECHANISM: a thin MODULE ENTRYPOINT presents one description to the dispatcher. Its body sequences the underlying primitives (skills, personas, threads, gates). Callers see one trigger; behind it lives a topology.
>
> ANTI-PATTERN: STUB ORCHESTRATION -- the facade only sequences with no interlock, gate, or synthesis decision. It is a wrapper that adds nothing; cut it and let callers invoke the primitives directly.

---

## S4. VALIDATION DECORATOR

> CLASSICAL ANALOG: Decorator.
>
> WHEN: a procedure produces an artifact whose correctness can be checked deterministically before downstream steps consume it.
>
> MECHANISM: wrap the producing step with a deterministic gate (linter, test run, schema validator, checklist invocation). The gate decides pass / revise. The decorated step keeps its single responsibility; the decorator owns the verification concern.
>
> ANTI-PATTERN: WRAPPING WITHOUT BLOCKING -- recording violations to a log without halting. Non-blocking gates degrade to noise.

---

## S5. LAZY PROXY

> CLASSICAL ANALOG: Proxy (specifically: virtual proxy / on-demand materialization).
>
> WHEN: a module references a heavy asset (long worked example, large ruleset, full per-harness adapter) that should not load until a specific step needs it.
>
> MECHANISM: the module body holds a relative-path reference; the agent treats the path as a placeholder and materializes the content only at the step that consumes it. The reference acts as a stand-in proxy that defers the real load.

DIFFERENCE FROM C1 (LAZY ASSET): C1 is the creational decision to package an asset as deferred-load. S5 is the structural shape of the reference itself -- a placeholder proxy that the runtime materializes on demand. Both cooperate: declare with C1, reference with S5.

> ANTI-PATTERN: PROXY SPRAWL -- pointers to pointers to pointers. Materialize in a single hop where possible.

ORTHOGONAL TO DISTRIBUTION BOUNDARY: load-on-demand does NOT cross the distribution boundary. A lazily-loaded asset still ships inside the module's published bundle; deferring its load only changes when the agent reads it, not whether it is packaged.

---

## S6. RULE BRIDGE

> CLASSICAL ANALOG: Bridge (decouple abstraction from implementation so both vary independently).
>
> WHEN: many personas share the same hard rules (encoding, secrets, review etiquette) but each persona has its own voice. Inlining the rules into every persona couples voice to rules; updating one rule requires editing N persona files.
>
> MECHANISM: extract the rules into SCOPE-ATTACHED RULE FILEs. The runtime auto-loads them on path / context match. Personas now vary along the LENS axis; rules vary along the CONSTRAINT axis; neither edits the other.
>
> ANTI-PATTERN: BAKED-IN RULES -- repeating the encoding rule inside every persona. Drift, then contradiction.

---

## S7. DETERMINISTIC TOOL BRIDGE

> CLASSICAL ANALOG: Adapter (GoF) at the language boundary; closer to a Hardware Abstraction Layer or FFI -- the structured seam between a high-level, probabilistic caller (the LLM) and a low-level, deterministic executor (CPU code: CLI, script, MCP server, HTTP API).
>
> WHEN: the design names a CONSEQUENTIAL SIDE EFFECT or a FACT THAT MUST BE TRUE. Examples: "apply database migration", "delete files", "read current branch", "post a comment on issue 42", "compute SHA-256 of artifact". Anything where the answer must be the actual answer (not a plausible answer) and any state change that must actually happen (not be claimed to have happened).

MECHANISM:

1. **NAME THE BOUNDARY.** The design explicitly identifies which steps are LLM-OWNED (selection, parameter binding, interpretation) and which are TOOL-OWNED (execution).
2. **PICK THE SUBSTRATE.** CLI command, script in a known language (python, bash, go, etc.), MCP server, HTTP API. The substrate is whatever the harness can already invoke; this pattern does not introduce a new runtime.
3. **STRUCTURED CONTRACT.** Inputs and outputs flow through a typed interface (function signature, JSON schema, MCP tool spec). The LLM sees the SCHEMA, not the implementation; the implementation stays deterministic.
4. **INTERPRET, DO NOT EXECUTE.** The LLM reads the tool's return value and decides what to do next. It does not re-execute the tool's logic in prose to "double-check" -- that re-introduces the probabilism the bridge removes.
5. **PAIR WITH S4 WHERE WARRANTED.** For irreversible side effects, gate the tool call behind a deterministic precondition check (also a tool call) and a B10 HUMAN CHECKPOINT.

DIFFERENCE FROM S2 (DEPENDENCY ADAPTER): S2 adapts ONE LLM-loaded module to ANOTHER LLM-loaded module's interface (text-to-text). S7 crosses the LLM/CPU boundary itself (text-to-tool-call-to-CPU-to-text). They compose: S2 inside the LLM layer, S7 between layers.

DIFFERENCE FROM S6 (RULE BRIDGE): S6 separates voice from constraint INSIDE the LLM context (both sides are still inferenced text). S7 separates probabilistic reasoning from deterministic execution ACROSS the runtime boundary.

ANTI-PATTERNS:
- **HAND-ROLLED HALLUCINATION.** The design declares a side effect ("update the deployment manifest") and leaves the LLM to emit the edited file as text without invoking the underlying tool (git, yq, kubectl). The "execution" is a high-variance regeneration of the artifact. Bridge it.
- **TOOLLESS ASSERTION.** The design depends on a fact ("current branch is main", "no migrations pending", "lockfile is up to date") and takes the LLM's recall of that fact as authoritative. The fact must come from a tool call, not memory.
- **OPAQUE TOOL.** The bridge exists but the design hides what the tool actually does, so reviewers cannot reason about determinism.
- **TOOL-CALL HALLUCINATION.** The LLM emits a tool invocation against a tool that does not exist or with parameters outside the schema. Mitigation: the harness exposes only declared tools (the schema is loaded into context), and S4 validates the parameter shape before the call.
- **UNGUARDED DESTRUCTIVE TOOL.** A bridge to an irreversible side effect (DROP TABLE, force push, delete bucket) without a precondition tool check AND a B10 HUMAN CHECKPOINT.
- **TERMINAL UNDERUSE.** The skill describes a check or read in prose ("ensure the working tree is clean", "confirm the file exists") when a one-line preloaded shell call (`git status --porcelain`, `test -f path`) would settle it deterministically. The terminal is right there; not using it is the most common form of HAND-ROLLED HALLUCINATION.

SELECTION HEURISTIC: If a design step contains the words "apply", "delete", "post", "deploy", "compute", "verify", or names a system of record (db, repo, queue, cluster, file system), it MUST cross S7. If a design step contains "decide", "compose", "summarize", "propose", "weigh", it stays in the LLM layer.

EXTENSION ROUTES (pick the narrowest that fits):

1. **PRELOADED TERMINAL ROUTE** (default). The skill instructs the LLM to run a specific command via the harness's shell tool. Fast to author, no new infrastructure.
2. **CUSTOM CLI / SCRIPT / API ROUTE.** The operator authors a purpose-built executable (python script, shell wrapper, internal HTTP endpoint, deterministic calculator) and the skill body instructs the LLM to use it with a documented contract.
3. **MCP SERVER ROUTE.** The operation is exposed by a Model Context Protocol server; the harness advertises it to the LLM as a first-class tool with a typed schema.

---

# Behavioral patterns

How primitives interact at run time.

## B1. FAN-OUT + SYNTHESIZER

> CLASSICAL ANALOG: Master-Worker (also: map-reduce; thread-pool with join + reducer).
>
> WHEN: >=3 independent lenses with no shared state, where each lens benefits from a fresh context window.
>
> MECHANISM: parent spawns one CHILD-THREAD per lens (each loading its own PERSONA PRELOAD). Each child returns a finding. Parent runs a synthesis pass (often loading an arbitrator persona) that produces ONE verdict.

```
parent (orchestrator + synthesizer)
   |
   +-- spawn ---> thread A (lens A) --+
   +-- spawn ---> thread B (lens B) --+
   +-- spawn ---> thread C (lens C) --+
                                      v
                                fan-in to parent
                                      |
                                      v
                                 synthesize -> single output
```

> ANTI-PATTERN: FAN-OUT-IN-ONE-CONTEXT -- running all N lenses sequentially inside a single window. Each lens contaminates the next; later lenses inherit attention drift from earlier ones.

B1 is the engine inside [A1 PANEL](/genesis/reference/patterns/a1-panel/).

---

## B2. CONDITIONAL DISPATCH

> CLASSICAL ANALOG: Strategy.
>
> WHEN: a single lens, but which procedure runs depends on input classification.
>
> MECHANISM: parent classifies the input, then loads the matching procedure (a different persona, a different skill, a different rule set). Only the chosen branch's text enters context.
>
> ANTI-PATTERN: ALL-BRANCHES-LOADED -- preloading every procedure's text "in case". Defeats the savings; the unused branches still compete for attention.

---

## B3. SUPERVISOR

> CLASSICAL ANALOG: Mediator (also: actor supervision tree of bounded depth).
>
> WHEN: a long task with checkpointable subtasks where the next spawn depends on prior results (dynamic plan).
>
> MECHANISM: a SUPERVISOR thread is the single planner. Workers cannot spawn peer workers (avoids unbounded fan-out). The supervisor re-plans after each worker returns.
>
> ANTI-PATTERN: WORKER-SPAWNS-WORKER -- decentralizes planning; tree depth becomes uncontrolled; supervisor loses oversight.

---

## B4. PLAN MEMENTO

> CLASSICAL ANALOG: Memento (capture and externalize state so it can be restored later).
>
> WHEN: any non-trivial work. Without externalized state, long sessions silently drop earlier decisions.
>
> MECHANISM: write the plan (goal, decomposition, todos, checkpoints, acceptance criterion) to PLAN PERSISTENCE BEFORE execution begins. Reload it at every re-grounding boundary: start of each step, return from each spawn, after each tool failure.

```
[ planning ]                    [ persistence ]
   decide problem    -->       PLAN ARTIFACT
   decompose         -->       TODO/STATUS
   pick topology     -->       (CHECKPOINT slot)
                                       ^
[ execution ]                          |
   step k starts ---- reload ----------+
      do work
   step k ends ------ update ----------+
      (advance status)
   spawn child? --> child gets POINTER to plan slice
   return from spawn -- reload --------+
```

> ANTI-PATTERN: WRITE-ONCE-NEVER-READ -- producing a plan at the start and never reloading it. The persistence is dead weight without the reload discipline.

B4 is the storage substrate that lets [B8 ATTENTION ANCHOR](/genesis/reference/patterns/b8-attention-anchor/) work.

---

## B5. ACCEPTANCE OBSERVER

> CLASSICAL ANALOG: Observer (the acceptance criterion observes the implementation; mismatch raises a finding).
>
> WHEN: any non-trivial work. The cost is one gate; the catch rate is high (drift accumulates silently throughout execution).
>
> MECHANISM: at the END of the work, RELOAD the acceptance criterion from PLAN PERSISTENCE. Without re-reading the implementation, list what the criterion demands. THEN compare against the implementation. Mismatch = drift. The reverse direction matters: reading the implementation first biases the gate to approve.
>
> ANTI-PATTERN: ACCEPTANCE-DRIFT -- silently editing the criterion mid-work to match the emerging result. The criterion is now a description, not a test. Pin it; only revise via an explicit re-plan event.

---

## B6. PROMPT TEMPLATE

> CLASSICAL ANALOG: Template Method (define the skeleton; subclasses fill in specific steps).
>
> WHEN: many similar capabilities follow the same skeleton (preamble, context loading, body, output schema, sign-off) but differ in narrow slots (the lens, the target artifact, the acceptance criterion).
>
> MECHANISM: extract the skeleton into a shared asset (often a PERSONA SCOPING FILE or a rule file). Each capability supplies only the slot-specific content. The template guarantees structural consistency; the slots carry the specialization.
>
> ANTI-PATTERN: TEMPLATE-DRIFT -- each capability re-invents the skeleton with cosmetic variations. Integrators cannot rely on the output shape.

---

## B7. TODO COMMAND

> CLASSICAL ANALOG: Command (encapsulate intent as an object that can be queued, replayed, undone).
>
> WHEN: a plan decomposes into discrete units of intent that the agent will execute over many turns and possibly across spawns.
>
> MECHANISM: each todo carries: id, title, description, status, optionally a staffed persona / skill, optionally dependencies on other todos. The agent updates status as it works (pending -> in_progress -> done | blocked). The serialized todo IS the command; the executor is its handler.

KEY PROPERTY: a todo is dispatchable. A todo with `staff: persona-X` or `skill: Y` realizes [STAFFED PLAN](/genesis/reference/patterns/architectural/#a4-staffed-plan).

> ANTI-PATTERN: GHOST TODOS -- creating todos and never updating their status. The plan and the executor diverge; recovery requires re-deriving state from artifacts.

---

## B8. ATTENTION ANCHOR

B8 is the highest-leverage behavioral pattern in the catalogue and has its own [dedicated page](/genesis/reference/patterns/b8-attention-anchor/). The short version:

> CLASSICAL ANALOG: NONE. This pattern has no faithful classical counterpart -- it is induced by LLM physics (attention decay over distance / over turns) rather than by software-engineering structure. It is, however, the single most important behavioral pattern for any non-trivial agent task.
>
> WHEN: any session that will exceed roughly a few dozen turns, or any plan whose acceptance criterion / hard constraints were established at turn 0 and must still hold at turn N. Long-running tasks WITHOUT periodic re-injection of the goal and hard constraints DRIFT silently from initial intent.
>
> MECHANISM: the goal, the hard constraints, and the acceptance criterion are RE-INJECTED into context at scheduled boundaries: start of every meaningful step, before any spawn, after any spawn returns, after any tool failure or error recovery, at any natural pause in execution.

ANTI-PATTERNS: ANCHOR DRIFT, OVER-ANCHORING, IMPLICIT-ANCHOR. See the [B8 page](/genesis/reference/patterns/b8-attention-anchor/) for the full definitions.

---

## B9. GOAL STEWARD

> CLASSICAL ANALOG: Mediator + intent-validator (a dedicated role whose sole job is to assert "are we still solving the original problem?").
>
> WHEN: a multi-round or multi-wave plan where the goal is at risk of silent reinterpretation as new findings, persona votes, or sub-results accrete. The PANEL (A1) and ALIGNMENT LOOP (A8) shapes are typical hosts.
>
> MECHANISM: a dedicated thread (a CEO/steward persona) holds the canonical goal statement and the success criteria. At each gate, the steward compares the proposed next step against the goal, names the delta, and either approves, requests refinement, or escalates. The steward IS the alignment authority; specialist lenses do not arbitrate their own contributions.

ANTI-PATTERNS:
- **MOVING-GOALPOST STEWARD** -- the steward edits the goal mid-flow to match emerging findings. The goal is not fixed; nothing is aligned. If the goal genuinely needs to change, escalate to the human (B10 HUMAN CHECKPOINT) and freeze the new goal explicitly.
- **RUBBER-STAMP STEWARD** -- the steward approves every proposal without citing the success criteria. The role is decorative.
- **STEWARD WITHOUT ARTIFACT** -- the goal lives in chat history, not in a persisted artifact (B4 PLAN MEMENTO). Attention drift erases it.

WHY THIS IS FIRST-CLASS. Long-running tasks drift from initial goals without an explicit steward. The steward is the named owner of "alignment to original intent" -- without a named owner, alignment is no one's job. This pattern is the procedural counterpart to the B8 ATTENTION ANCHOR token-budget cure.

---

## B10. HUMAN CHECKPOINT

> CLASSICAL ANALOG: Approval Gate + manual override in a workflow engine.
>
> WHEN: a step is irrecoverable, expensive, or requires authority the agent does not have. Common examples: shipping a release; merging to main; deleting persistent state; making any decision that the agent's self-confidence cannot resolve (drift detection; suspected hallucination; tie between equally-fit patterns).
>
> MECHANISM: the procedure halts at a named checkpoint. The agent emits a structured prompt to the human (current state, options, recommended choice with rationale, escape hatches). Execution does not resume until the human responds. The response IS the gate verdict.

ANTI-PATTERNS:
- **SILENT DRIFT** -- the agent suspects misalignment but powers through rather than checkpointing. The checkpoint is the cure for self-conscious drift; using it is the discipline.
- **CHATTY GATE** -- checkpointing on every minor decision. Floods the human and trains them to rubber-stamp. Reserve for the real irrecoverables.
- **FALSE-CHOICE GATE** -- presenting options that all lead to the same outcome; the human's input does not change behaviour.
- **POST-HOC CHECKPOINT** -- asking the human to approve a step the agent already executed. Not a checkpoint; a notification.

WHY THIS IS FIRST-CLASS. Hallucination is inherent. When the agent itself suspects fabrication or unbounded scope creep, only an external authority can break the loop. The HUMAN CHECKPOINT is the explicit escape hatch named in the architecture, not an ad-hoc rescue.

---

## Selection heuristic

When in doubt, prefer the pattern that minimizes context degradation in any one thread.

```
1 lens, 1 procedure                        -> single sequential
                                              (no Tier-2 pattern needed)

>=3 independent lenses, no shared state    -> B1 FAN-OUT + SYNTHESIZER

procedure depends on input class           -> B2 CONDITIONAL DISPATCH

long task, dynamic plan                    -> B3 SUPERVISOR

verifiable artifact between steps          -> S4 VALIDATION DECORATOR

multi-step / multi-file / spawn-bound      -> B4 PLAN MEMENTO (always)
                                              + B8 ATTENTION ANCHOR (always)

ANY work past trivial scope                -> add B5 ACCEPTANCE OBSERVER
                                              and B8 ATTENTION ANCHOR

multi-round plan with risk of goal drift   -> add B9 GOAL STEWARD

irrecoverable step / suspected drift       -> add B10 HUMAN CHECKPOINT

facts depend on external corpus or live    -> add C6 EXTERNAL CORPUS
state; or pretraining-cutoff sensitive        GROUNDING (lazy, bounded)
```

B4, B5, and B8 are orthogonal to topology choice. B9 layers on top of any multi-thread plan; B10 layers on top of any irrecoverable boundary; C6 layers on top of any work that touches external facts.

When two or more patterns from this catalogue fit the same slot, cite the matrix that cut your choice in the handoff packet.

## Cross-references

- [Architectural patterns](/genesis/reference/patterns/architectural/) -- Tier-3 shapes that compose these design patterns.
- [Refactor patterns](/genesis/reference/patterns/refactor/) -- restructure modules at source-time, orthogonal to the runtime topology these design patterns describe.
- [B8 ATTENTION ANCHOR](/genesis/reference/patterns/b8-attention-anchor/) and [A1 PANEL](/genesis/reference/patterns/a1-panel/) deep dives.
- For the LLM-physics theory that motivates B8 + B4, see Chapter 11 "Context Engineering" in the [Agentic SDLC Handbook](https://danielmeppiel.github.io/agentic-sdlc-handbook/handbook/ch11-context-engineering.html).
- For the failure-mode catalogue, see Chapter 14 "Anti-Patterns and Failure Modes" in the handbook.
