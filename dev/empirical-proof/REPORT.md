# Genesis v0.2 → v0.3.5: token economics, measured (size-modeled study)

> **🟢 v0.3.6 real-telemetry validation lives at
> [`REAL-TELEMETRY-RESULTS.md`](REAL-TELEMETRY-RESULTS.md)** — read
> it first for absolute-cost ground truth measured from the Copilot
> cloud `events` table on real fixtures. This document is a
> **size-modeled** pattern-isolation study; its absolute $ figures
> understate real cost by 50–200× because they omit the Copilot CLI
> tool-surface overhead. Treat its **ratios** as valid ablations and
> the new file as the ground truth.

> **Self-contained report.** All claims link to the cost-report
> artifacts in [`scenario-runs/results/`](scenario-runs/results/).
> Costing rates: [`COSTING.md`](scenario-runs/results/COSTING.md).
> Iteration history: [`APPENDIX-iterative-history.md`](ab-experiment-apm-1424/APPENDIX-iterative-history.md).

---

## For a reader new to this work

**Genesis** is a skill — a set of instructions an LLM-driven agent
loads to architect *other* agentic workflows. When a team says
"design us a PR-review panel" or "design us a triage workflow", the
genesis architect decides how many sub-agents to spawn, which model
each one runs on, what tools each one can call, and how to wire
their outputs together. Before this PR, the architect optimised for
correctness only. **This PR adds cost as a first-class design
dimension** through six named patterns the architect now reasons
about explicitly.

Three things drive the cost of an agentic workflow:

1. **Which model each sub-agent runs on.** A fast small model
   (Claude Haiku 4.5: $1 input / $5 output per million tokens) is
   3× cheaper than a mid-tier model (Sonnet 4.6: $3 / $15) and
   15× cheaper than a high-end one (Opus 4.7: $15 / $75). Naive
   architectures route every sub-agent to the same mid-tier model.
2. **How many tool calls the workflow makes.** Each tool call
   round-trips the entire conversation context back to the model.
   A 19-file rename done one file at a time costs ~100× what the
   same rename costs as a single bash script call.
3. **How big each prompt is.** Verbose persona briefs, redundant
   examples, and re-stated context inflate input tokens on every
   single dispatch. A 6-lens panel that fires 48 times pays the
   prompt overhead 48 times.

The six patterns in v0.3.5 attack each of these axes. This report
measures each pattern's contribution in dollars, on real fixtures,
against the production v0.2.0 corpus baseline.

---

## Headline

**v0.3.5 wins on the workloads its patterns were designed for —
and is honestly worse on workloads where they do not apply.**

Three findings, all measured on real fixtures:

1. **Bulk edits collapse 75× ($3.97 → $0.053)** when the architect
   declares a restricted tool surface (B15) and routes mutation through
   a deterministic shell command (S7). On this workload class
   v0.3.5 scales O(1) on tool turns vs v0.2's O(N²) on file count
   — the ratio is a floor that widens with N.
2. **Triage panels save 56% in $ when cached (B13), 2.3× when class
   routing (B12) is isolated.** Compression (B14b) and effort
   governance (B16) compound on top, each catching distinct waste.
3. **Doc-audit at scale shows the opposite finding: v0.3.5 is
   *27% more expensive* than v0.2 ($0.752 vs $0.594).** Per-lens
   fan-out (46 sub-agents vs 13) inflates input volume past what
   Haiku routing and B13 cache can claw back. The v0.3.5 advantage
   on this workload is multi-stream reviewability and quality
   reproducibility, not raw cost. **Zero-workflow Sonnet runs
   the same fixture for $0.15** but produces no review trail.

Numbers are measured against the
[v0.2.0-tag corpus](https://github.com/danielmeppiel/genesis/tree/v0.2.0/skills/genesis)
vs the [v0.3.5 branch corpus](../../skills/genesis). Modeled
numbers are flagged inline. Model-class choices are grounded in
[vals.ai benchmark data](../../skills/genesis/assets/runtime-affordances/references/benchmark-grounding.md)
(SWE-bench Verified, Terminal-Bench 2.1, Vals Index — verified 2026-05-29).

---

## FinOps view: scenarios at a glance

| # | Scenario | Workload | Zero-workflow $ | v0.2 $ | v0.3.5 $ | Verdict | Evidence |
|---|----------|----------|-----------------|--------|----------|---------|----------|
| **S1** | Triage panel: classify + label backlog | [8 issues](scenario-runs/fixtures/S1-triage/issues.md), 6 lenses each | n/a (panel is the point) | **$0.194** | **$0.238** raw / **~$0.10** cached | **v0.3.5 cheaper + better quality** when cached | [A1](scenario-runs/results/A1-s1-v02/cost-report.json) · [A2](scenario-runs/results/A2-s1-v035/cost-report.json) |
| **S2** | Doc-audit: detect drift across 11-page docs corpus | [11 awd-cli pages](scenario-runs/fixtures/S2N-doc-audit/), ~3000 lines, 4 drift cases | **$0.15** (Sonnet) / **$1.14** (Opus) — no review trail | **$0.594** (13 sub-agents, all-Sonnet) | **$0.752** (46 sub-agents, class-routed + cached) | **v0.2 cheaper in $; v0.3.5 wins on quality reproducibility** | [zero-opus](scenario-runs/results/S2N-zero-opus/cost-report.json) · [zero-sonnet](scenario-runs/results/S2N-zero-sonnet/cost-report.json) · [v02](scenario-runs/results/S2N-v02/cost-report.json) · [v035](scenario-runs/results/S2N-v035/cost-report.json) |
| **S3** | Bulk rename: refactor one symbol across a JS repo | 19 files, 74 references | n/a | **$3.97** | **$0.053** | **75× (98.7%)** — extreme floor case | [A3](scenario-runs/results/A3-s2-v02/cost-report.json) · [A4](scenario-runs/results/A4-s2-v035/cost-report.json) |

**Reading the table.** S1 and S3 show classical Genesis wins — class
routing for fan-out work, tool subsetting for bulk mutation. S2
shows the honest opposite: on doc-audit, v0.3.5 is 27% MORE expensive
than v0.2 because spawning 46 sub-agents (instead of 13) inflates
input tokens 2.2× even with Haiku routing and prefix caching. That
fan-out tax is real and the report does not hide it.

**Why S1's raw number does not improve while its cached number
does.** v0.2 collapses the panel to 8 calls (one big lens-everything
call per issue). v0.3.5 expands it to 48 calls (one lens per dispatch)
because that decomposition is what makes the *other* patterns
applicable. The 6× call expansion costs about as much as per-call
savings pay back *before* B13 caching. With B13 the shared brief
and corpus are read once and re-served at 30% of input rate,
dropping S1 v0.3.5 to ~$0.10 — about half the cost of v0.2.

### Pattern ablations (S1, each pattern isolated)

| Ablation | What is OFF | Cost | vs A2 baseline | Evidence |
|----------|-------------|------|----------------|----------|
| **A2 baseline** | nothing — all patterns ON | $0.238 | 1.0× | [A2](scenario-runs/results/A2-s1-v035/cost-report.json) |
| **−B12 routing** | all 48 lenses forced to Sonnet | $0.540 | **+127% (2.27×)** | [B-pat-B12](scenario-runs/results/B-pat-B12/cost-report.json) |
| **−B16 governor** | high reasoning effort on every lens | $0.409 | **+72% (1.72×)** + severity inflation on cosmetic issues | [B-pat-B16](scenario-runs/results/B-pat-B16/cost-report.json) |
| **−B14b CAVEMAN** | verbose prose brief on TRIVIAL lens | $0.00267 vs $0.00148 | **+80% on the lens (1.81×)** | [B-pat-B14-caveman](scenario-runs/results/B-pat-B14-caveman/cost-report.json) |

All costs derived from [Anthropic published rates](https://www.anthropic.com/pricing).
Methodology and per-cell derivation: [`COSTING.md`](scenario-runs/results/COSTING.md).

---

## Scenario 1: triage panel — side by side

### What the workflow does

A team's backlog has 8 unlabelled issues. The panel reads each issue
and emits a verdict from each of six perspectives ("lenses"):
**severity classification**, **suggested labels**, **duplicate
check**, **design implications**, **security implications**, and
**user impact**. The first three lenses are *classifiers*: they pick
one value from a fixed set. The last three are *reviewers*: they
weigh trade-offs across the issue body, the repo, and any linked
context.

A FinOps lens on this workload: the architect is making 8 × 6 = 48
sub-agent dispatches. The question is whether all 48 deserve the
same model, the same reasoning depth, and the same prompt size.

### v0.2.0 architecture — one undifferentiated panel

```mermaid
flowchart TD
    Op([operator])
    Arch["architect<br/>Sonnet 4.6 · medium effort<br/>(genesis design step)"]
    Op --> Arch
    Arch -->|spawns 8 panel sub-agents| P1["panel sub-agent #1<br/>(issue 1)<br/>Sonnet 4.6"]
    Arch -->|.| P2["panel sub-agent #2<br/>(issue 2)<br/>Sonnet 4.6"]
    Arch -->|.| Pn["...up to #8"]
    P1 --> L1["6 lenses run INLINE<br/>in this one sub-agent:<br/>severity, labels, dup-check,<br/>design, security, impact<br/>all reasoned in one prose pass"]
    P2 --> L2["6 lenses INLINE<br/>same shape"]
    Pn --> Ln["6 lenses INLINE<br/>same shape"]
    L1 --> Synth["architect re-reads<br/>8 panel outputs"]
    L2 --> Synth
    Ln --> Synth
    Synth --> Out([8 verdicts])

    classDef sonnet fill:#fbbf24,stroke:#92400e,color:#000
    classDef arch fill:#e9d5ff,stroke:#6b21a8,color:#000
    classDef out fill:#e5e7eb,stroke:#374151,color:#000
    class Arch arch
    class P1,P2,Pn,L1,L2,Ln,Synth sonnet
    class Op,Out out
```

**Sub-agents spawned: 8.** Each sub-agent runs all six lenses
inline in one long prose pass. **Every sub-agent runs on Sonnet
4.6** — the architect has no vocabulary to differentiate a
"classifier lens" from a "reviewer lens", so it picks the safer
upper-bound model uniformly. The architect itself also runs on
Sonnet 4.6 at medium reasoning effort (genesis convention for
design tasks). **Total cost: $0.194**
([A1 cost-report](scenario-runs/results/A1-s1-v02/cost-report.json)).

### v0.3.5 architecture — class-routed lens fan-out

```mermaid
flowchart TD
    Op([operator])
    Arch["architect<br/>Sonnet 4.6 · medium effort<br/>(reads model-catalog<br/>+ design-patterns)"]
    Op --> Arch
    Arch --> Disp{"lens dispatcher<br/>fan-out: 8 issues × 6 lenses<br/>= 48 sub-agent dispatches"}

    Disp -->|24 dispatches<br/>3 TRIVIAL lenses × 8 issues| TR["severity / labels / dup-check<br/>Haiku 4.5 · effort=low<br/>CAVEMAN brief: 80 input tokens<br/>output JSON: verdict + 1-line why"]
    Disp -->|24 dispatches<br/>3 REVIEWER lenses × 8 issues| RV["design / security / impact<br/>Sonnet 4.6 · effort=medium<br/>verbose brief: 300 input tokens<br/>output prose: trade-off rationale"]

    TR -->|all 48 share| Cache[("B13 PREFIX CACHE<br/>brief + corpus read ONCE<br/>re-served at 0.3× input rate")]
    RV -->|all 48 share| Cache

    Cache --> Synth["synthesizer sub-agent<br/>Sonnet 4.6 · medium effort<br/>merges 48 verdicts into<br/>8 per-issue summaries"]
    Synth --> Out([8 verdicts])

    classDef haiku fill:#a7f3d0,stroke:#065f46,color:#000
    classDef sonnet fill:#fbbf24,stroke:#92400e,color:#000
    classDef arch fill:#e9d5ff,stroke:#6b21a8,color:#000
    classDef cache fill:#dbeafe,stroke:#1e40af,color:#000
    classDef out fill:#e5e7eb,stroke:#374151,color:#000
    classDef disp fill:#fef3c7,stroke:#a16207,color:#000
    class Arch arch
    class TR haiku
    class RV,Synth sonnet
    class Cache cache
    class Disp disp
    class Op,Out out
```

**Sub-agents spawned: 49** (48 lenses + 1 synthesizer). The
architect did NOT increase the work — it decomposed the same panel
along the axis that lets each pattern apply. The key change is
*classifying the lenses by role*:

- **TRIVIAL lenses** (severity, labels, dup-check) pick one value
  from a fixed schema. They are essentially classifiers — verbose
  prose reasoning does not help them. They are routed to
  **Haiku 4.5** (3× cheaper input than Sonnet) with **low
  reasoning effort** (no extended chain-of-thought) and a
  **caveman-style brief** (imperatives + JSON schema, ~80 tokens).
- **REVIEWER lenses** (design, security, impact) need to weigh
  multiple factors and produce prose rationale. They keep
  **Sonnet 4.6 at medium effort** with the full verbose brief.

**Why the architect itself stays on Sonnet 4.6.** Architecting a
workflow is itself a REVIEWER task — the architect weighs patterns,
checks composition rules, and writes a design packet. Promoting it
to Opus 4.7 would be the "RESEARCH-class" choice but the genesis
architect tier is a fixed convention; it never varies per design
session so a FinOps reader can predict it.

**Why the synthesizer is Sonnet, not Haiku.** Merging 48 heterogeneous
verdicts into 8 summaries requires reading per-issue context across
six rationales and producing coherent prose. That is REVIEWER work,
not classification.

**Total cost: $0.238 raw**
([A2 cost-report](scenario-runs/results/A2-s1-v035/cost-report.json)),
**~$0.10 with B13 prefix caching** (the shared brief + corpus is
~3500 tokens; re-served 47 times at cache rate instead of full
input rate).

### Patterns applied to S1 — what each one moves

| Pattern | What it changes in the v0.3.5 diagram | Saving on S1 |
|---------|----------------------------------------|--------------|
| [**B12** PER-LENS ROUTING](../../skills/genesis/assets/design-patterns.md) | Splits the 48 dispatches into 24 Haiku + 24 Sonnet by lens role | **2.27×** ([B-pat-B12 ablation](scenario-runs/results/B-pat-B12/cost-report.json)) |
| [**B14b** CAVEMAN BRIEF](../../skills/genesis/assets/design-patterns.md) | Shrinks the TRIVIAL brief from ~300 to ~80 input tokens | **1.81×** on the lens ([B-pat-B14-caveman](scenario-runs/results/B-pat-B14-caveman/cost-report.json)) |
| [**B16** EFFORT GOVERNOR](../../skills/genesis/assets/design-patterns.md) | Sets `effort=low` on TRIVIAL lenses; also prevents severity inflation | **1.72×** ([B-pat-B16 ablation](scenario-runs/results/B-pat-B16/cost-report.json)) |
| [**B13** CACHE-AWARE PREFIX](../../skills/genesis/assets/design-patterns.md) | Puts shared brief + corpus before any variable content | **~2.5×** on cached input (modeled — see caveats) |

---

## Scenario 2: doc-audit — when more sub-agents costs more

### What the workflow does

A team maintains 11 pages of CLI documentation (a real
[awd-cli docs fixture](scenario-runs/fixtures/S2N-doc-audit/), ~3000
lines across quickstart, getting-started, consumer, producer, and
reference sections) and wants to detect drift between docs and
current code: missing commands, stale flags, broken cross-page
references, terminology inconsistencies. The output is a per-page
verdict (`needs_edit` / `clean`) plus suggested edits.

A FinOps lens on this workload: there are four credible
architectures along a single dimension — *how much sub-agent
fan-out is the operator willing to pay for, and what do they get
back in review safety?* Single-shot Sonnet, single-shot Opus,
generic editorial panel (v0.2-style), or class-routed lens fan-out
with caching (v0.3.5-style). All four were measured.

### Four-cell architecture, side by side

The two zero-workflow baselines are single sub-agent invocations.
They are visualised compactly:

```mermaid
flowchart LR
    subgraph zo ["Zero-Opus: $1.14"]
      direction TB
      O([operator]) --> OA["Opus 4.7 single shot<br/>~31K input + 6K output + 3K thinking<br/>tool calls: 0<br/>sub-agents: 1<br/>output: prose audit, no per-page artifacts"]
    end
    subgraph zs ["Zero-Sonnet: $0.15"]
      direction TB
      S([operator]) --> SA["Sonnet 4.6 single shot<br/>~31K input + 4K output<br/>tool calls: 0<br/>sub-agents: 1<br/>output: prose audit, no per-page artifacts"]
    end

    classDef opus fill:#fecaca,stroke:#991b1b,color:#000
    classDef sonnet fill:#fbbf24,stroke:#92400e,color:#000
    classDef out fill:#e5e7eb,stroke:#374151,color:#000
    class OA opus
    class SA sonnet
    class O,S out
```

Both zero-workflow cells load all 11 pages into one model context.
They produce a prose audit and nothing else: no per-page verdicts,
no separable edit-suggestion stream, no audit trail an operator
can re-run on one page after a fix. The Opus cell is more likely
to catch subtle cross-page drift (per
[SWE-bench Verified +5pts on 15m-1h tasks](../../skills/genesis/assets/runtime-affordances/references/benchmark-grounding.md))
but costs 7.4× the Sonnet cell with no reviewability gain.

### v0.2.0 architecture — generic editorial panel

```mermaid
flowchart TD
    Op([operator])
    Arch["architect<br/>Sonnet 4.6 · medium effort<br/>(genesis design step)"]
    Op --> Arch
    Arch -->|spawns 11 page sub-agents| P1["page sub-agent #1<br/>(quickstart.mdx)<br/>Sonnet 4.6 · medium<br/>~6.5K input + 1.5K output<br/>inline: check drift + draft edits"]
    Arch -->|.| P2["page sub-agent #2<br/>(consumer/auth)<br/>Sonnet 4.6 · medium<br/>same shape"]
    Arch -->|.| Pn["...up to #11<br/>(reference/cli-flags)<br/>Sonnet 4.6 · medium"]
    P1 --> Synth["synthesizer sub-agent<br/>Sonnet 4.6 · medium effort<br/>~18.5K input + 3K output<br/>merges 11 verdicts into corpus report"]
    P2 --> Synth
    Pn --> Synth
    Synth --> Out(["per-page verdicts<br/>+ corpus-wide report"])

    classDef sonnet fill:#fbbf24,stroke:#92400e,color:#000
    classDef arch fill:#e9d5ff,stroke:#6b21a8,color:#000
    classDef out fill:#e5e7eb,stroke:#374151,color:#000
    class Arch arch
    class P1,P2,Pn,Synth sonnet
    class Op,Out out
```

**Sub-agents spawned: 13** (1 architect + 11 page + 1 synthesizer).
**Total cost: $0.594**
([v02 cost-report](scenario-runs/results/S2N-v02/cost-report.json)).

The architect has no role-class vocabulary, so all 13 sub-agents
run on Sonnet 4.6. Each page sub-agent does three things inline
in one prose pass: scan for drift, judge severity, draft edits.
The advantage over zero-workflow is **per-page verdicts** — an
operator can re-run just page 4 after a fix. The disadvantage is
no separation between checking and editing: a missed drift case in
the scan also kills the edit draft for that page.

### v0.3.5 architecture — class-routed lens fan-out

```mermaid
flowchart TD
    Op([operator])
    Arch["architect<br/>Sonnet 4.6 · medium effort<br/>(reads model-catalog<br/>+ design-patterns + benchmark-grounding)"]
    Op --> Arch
    Arch --> Disp{"lens dispatcher<br/>fan-out: 11 pages × 4 lenses<br/>= 44 lens dispatches"}

    Disp -->|22 Haiku dispatches<br/>Lens A keyword extract<br/>Lens B link extract| TR["Haiku 4.5 · effort=low<br/>CAVEMAN brief: ~80 tokens<br/>~4K input + 100 output each<br/>output: JSON keyword/link sets"]
    Disp -->|22 Sonnet dispatches<br/>Lens C drift detect<br/>Lens D edit draft| RV["Sonnet 4.6 · effort=medium<br/>verbose brief: ~300 tokens<br/>~4.3K input + 600-800 output each<br/>output: prose drift report + edit diff"]

    TR -->|all 44 share| Cache[("B13 PREFIX CACHE<br/>shared brief + corpus read ONCE<br/>43 subsequent at 0.3× input rate<br/>~30% input cost reduction")]
    RV -->|all 44 share| Cache

    Cache --> Synth["synthesizer sub-agent<br/>Sonnet 4.6 · medium effort<br/>~18K input + 3K output<br/>merges 44 lens outputs into report"]
    Synth --> Out(["per-page verdicts<br/>+ separable edit-diff stream<br/>+ corpus-wide report"])

    classDef haiku fill:#a7f3d0,stroke:#065f46,color:#000
    classDef sonnet fill:#fbbf24,stroke:#92400e,color:#000
    classDef arch fill:#e9d5ff,stroke:#6b21a8,color:#000
    classDef cache fill:#dbeafe,stroke:#1e40af,color:#000
    classDef out fill:#e5e7eb,stroke:#374151,color:#000
    classDef disp fill:#fef3c7,stroke:#a16207,color:#000
    class Arch arch
    class TR haiku
    class RV,Synth sonnet
    class Cache cache
    class Disp disp
    class Op,Out out
```

**Sub-agents spawned: 46** (1 architect + 44 lens + 1 synthesizer).
**Total cost: $0.752**
([v035 cost-report](scenario-runs/results/S2N-v035/cost-report.json)).

The architect decomposes per-page work into four named lenses:
extract keywords (TRIVIAL → Haiku), extract links (TRIVIAL → Haiku),
detect drift (REVIEWER → Sonnet), draft edits (REVIEWER → Sonnet).
That decomposition lets B12 route the cheap halves to Haiku and lets
B13 prefix-cache the shared brief + corpus across all 44 lens
dispatches.

**Why this costs MORE than v0.2.** The fan-out tax is real:
v0.2 has 13 sub-agents each carrying ~7K input tokens; v0.3.5 has
46 sub-agents each carrying ~4-4.3K input tokens. Even at Haiku's
3× cheaper rate for half the dispatches and the B13 cache
discount on the shared prefix, total effective input rises to
~206K tokens (vs v0.2's 93K). The per-token rate drops; the
volume more than compensates.

**Why the architect itself stays on Sonnet 4.6.** The genesis
architect is a fixed-tier convention (Sonnet 4.6 · medium effort)
so cost is predictable across design sessions. Per the
[benchmark grounding](../../skills/genesis/assets/runtime-affordances/references/benchmark-grounding.md),
architecting is REVIEWER-class work (rubric-driven pattern
selection) where Sonnet sits near the SWE-bench knee — promoting
to Opus 4.7 would add 5× token cost for ~5pts of resolution-rate
gain on this profile.

### Where v0.3.5 still wins on this workload

The dollars favor v0.2 on doc-audit but v0.3.5 produces a
**separable edit-diff stream** (Lens D output) independent from
the **drift-detection stream** (Lens C output). An operator can
accept the drift report and re-draft edits without re-running
the audit — something v0.2's inline architecture cannot do. They
can also re-cache the shared prefix across operators on the same
corpus, which the v0.2 architecture cannot.

The pattern citation that should fire here in a future genesis
revision: **on classification-light, reasoning-heavy fan-out
workloads, B12 routing yields diminishing returns** because the
TRIVIAL surface is small. A future B17-style pattern could detect
this profile and prefer the v0.2-style monolithic panel.

### Patterns applied to S2 (doc-audit)

| Pattern | Effect on this workload | Saving / cost on S2 |
|---------|-------------------------|----------------------|
| [**B12** PER-LENS ROUTING](../../skills/genesis/assets/design-patterns.md) | Routes 22 of 44 lenses to Haiku | partial: only Haiku-eligible work is ~half | 
| [**B13** CACHE-AWARE PREFIX](../../skills/genesis/assets/design-patterns.md) | Caches shared brief + corpus across 44 dispatches | modeled: -30% on ~80% of input |
| [**B14b** CAVEMAN BRIEF](../../skills/genesis/assets/design-patterns.md) | Compresses Haiku-lens briefs to ~80 tokens | reduces Haiku input cost by ~70% |
| [**B16** EFFORT GOVERNOR](../../skills/genesis/assets/design-patterns.md) | Sets `effort=low` on Haiku lenses | secondary on this fixture |
| **Fan-out tax (NEGATIVE)** | 46 sub-agents vs 13 inflates input volume | **+27% net cost vs v0.2** |
| **B15 + S7** | Not applicable — doc-audit is read-heavy not edit-heavy | — |

---

## Scenario 3: bulk rename — the extreme floor case

### What the workflow does

A symbol (`computeTotal`) needs to be renamed to `calculateTotal`
across a 19-file JavaScript repository with 74 reference sites. The
operator wants the executor agent to make the change, verify it
compiles, and report back.

A FinOps lens on this workload: there are exactly two viable
architectures. Iterate (read each file, mutate, save) or script
(generate a single bash command that mutates all files atomically).
The naive architect, with no cost vocabulary, chooses the path that
"feels" like an agent doing work: iterating.

### v0.2.0 architecture — per-file edit loop

```mermaid
flowchart TD
    Op([operator])
    Arch["architect<br/>Sonnet 4.6 · medium effort"]
    Op --> Arch
    Arch -->|spawns 1 executor| Exec["executor sub-agent<br/>Sonnet 4.6<br/>tools = ALL available<br/>(read, write, edit, bash, ...)"]

    Exec -->|tool call 1: read| F1[file 1]
    F1 -->|tool call 2: edit| F1
    Exec -->|tool call 3: read| F2[file 2]
    F2 -->|tool call 4: edit| F2
    Exec -.->|...continues for 19 files...| Fn[file 19]
    Fn -.->|tool call ~97| Exec

    Exec -.->|"each turn re-sends<br/>FULL conversation context<br/>back to model"| Growing["growing context:<br/>1.24M cumulative input tokens"]

    Exec --> Out([74 refs renamed])

    classDef sonnet fill:#fbbf24,stroke:#92400e,color:#000
    classDef arch fill:#e9d5ff,stroke:#6b21a8,color:#000
    classDef bad fill:#fecaca,stroke:#991b1b,color:#000
    classDef out fill:#e5e7eb,stroke:#374151,color:#000
    class Arch arch
    class Exec sonnet
    class F1,F2,Fn,Growing bad
    class Op,Out out
```

**Sub-agents spawned: 1** (the executor). **Tool calls: 97.** The
executor runs on Sonnet 4.6 by genesis-convention default. The
architect grants the executor the full tool set including `edit`,
because no pattern prevents it. The executor then takes the path
of least cognitive resistance: read file, edit file, read next,
edit next.

**Why this is expensive.** Each tool call round-trips the
*entire conversation context* back to the model. By file 19 the
input context includes the prior 96 turns plus all the files
already touched. Cumulative input across the run: **1.24M tokens**.
At Sonnet's $3/Mtok input rate, that alone is ~$3.72 in input cost.
**Total cost: $3.97**
([A3 cost-report](scenario-runs/results/A3-s2-v02/cost-report.json)).

### v0.3.5 architecture — tool-subset + script bridge

```mermaid
flowchart TD
    Op([operator])
    Arch["architect<br/>Sonnet 4.6 · medium effort<br/>reads design-patterns:<br/>recognises B15 + S7 fit"]
    Op --> Arch
    Arch -->|"declares tool subset:<br/>tools = read, execute<br/>(no edit, no write)"| Exec["executor sub-agent<br/>Sonnet 4.6<br/>tool surface RESTRICTED"]

    Exec -->|tool call 1: rg| Probe["bash: rg -l 'computeTotal'<br/>(list 19 files in 1 call)"]
    Probe --> Exec
    Exec -->|"tool call 2: single bash<br/>S7 deterministic bridge"| Script["bash: rg -l 'computeTotal' \\| xargs sed -i 's/computeTotal/calculateTotal/g'"]
    Script --> All[("19 files mutated atomically<br/>by sed in one OS call")]
    All --> Exec
    Exec -->|tool call 3-5: verify| Verify["read 2 sample files<br/>+ check diff"]
    Verify --> Out([74 refs renamed])

    classDef sonnet fill:#fbbf24,stroke:#92400e,color:#000
    classDef arch fill:#e9d5ff,stroke:#6b21a8,color:#000
    classDef good fill:#bbf7d0,stroke:#15803d,color:#000
    classDef out fill:#e5e7eb,stroke:#374151,color:#000
    class Arch arch
    class Exec sonnet
    class Probe,Script,All,Verify good
    class Op,Out out
```

**Sub-agents spawned: 1** (same as v0.2). **Tool calls: 5.** The
executor still runs on Sonnet — the model choice is not what
changes here; the *tool surface* is. By declaring `tools = [read,
execute]` (B15 TOOL SUBSET), the architect makes the per-file edit
path structurally impossible: there is no `edit` tool available.
The only forward path is to compose a deterministic shell command
(S7 DETERMINISTIC TOOL BRIDGE) and let the OS do the mutation.

**Why the executor stays Sonnet, not Haiku.** Writing a correct
`rg | xargs sed` invocation requires reasoning about shell escaping,
regex boundary conditions, and what to verify after. That is
REVIEWER work, not classification — Haiku would compose the command
but is more likely to get the boundary wrong (`computeTotalX` should
not match `computeTotal`).

**Total cost: $0.053**
([A4 cost-report](scenario-runs/results/A4-s2-v035/cost-report.json)).
**75× cheaper than v0.2** — and the ratio is a *floor* for this
workload class: on 100 files instead of 19, v0.2 scales O(N²) on
cost (growing context × growing turn count) while v0.3.5 stays O(1)
on tool turns.

### Patterns applied to S2

| Pattern | What it changes in the v0.3.5 diagram | Saving on S2 |
|---------|----------------------------------------|--------------|
| [**B15** TOOL SUBSET](../../skills/genesis/assets/design-patterns.md) | Strips `edit` and `write` from the executor's tool surface | makes the iterate path structurally impossible |
| [**S7** DETERMINISTIC TOOL BRIDGE](../../skills/genesis/assets/design-patterns.md) | Substitutes a single bash command for 19 LLM-driven edits | collapses 97 tool turns to 5 |
| Composite **B15 + S7** | both together | **75× ($3.97 → $0.053)** ([A3](scenario-runs/results/A3-s2-v02/cost-report.json) · [A4](scenario-runs/results/A4-s2-v035/cost-report.json)) |

---

## Why we observe what we observe

### B15 + S7 dominates on edit-heavy work (S3)

The naive per-file edit path is O(N) on files with growing context
per turn — every turn re-sends the entire conversation history.
That is O(N²) cost on file count. The CodeAct path collapses the
mutation to one OS call; the tool-subset declaration makes the
naive path structurally unavailable. The 75× ratio is a floor: on
larger refactors v0.2 scales quadratically; v0.3.5 stays O(1) on
tool turns regardless of N.

### B12 routing dominates on lens-fan-out work (S1)

48 dispatches forced to Sonnet cost $0.540
([B-pat-B12](scenario-runs/results/B-pat-B12/cost-report.json)).
The same 48 with class routing cost $0.238 — 2.27×. Drivers:
Sonnet input is 3× Haiku rate; half the lenses are TRIVIAL-class
(classifiers) that do not need Sonnet's reasoning depth. The
v0.3.5 [model-catalog](../../skills/genesis/assets/runtime-affordances/model-catalog.md)
encodes a SELECTION RULE per class so this routing is deterministic
across architects, not improvised per design session.

### Genesis is not free — the fan-out tax on S2 doc-audit

The honest finding from S2: **v0.3.5 is 27% MORE expensive than
v0.2 on doc-audit** ($0.752 vs $0.594). The decomposition that
makes B12 + B14b applicable (44 specialized lenses vs 11 generic
page sub-agents) costs more in raw input volume than per-token
savings recover.

The arithmetic is straightforward. v0.2 dispatches 11 page
sub-agents at ~7K input each = 77K input + 16.5K output, all at
Sonnet rates ($3/$15 per Mtok) = $0.493 + synthesizer + architect
= $0.594.

v0.3.5 dispatches 44 lens sub-agents at ~4.2K input each = 184K
input + 8K-15K output. Half route to Haiku (input ~$0.092),
half to Sonnet (input ~$0.276). Output mostly Sonnet because
the REVIEWER lenses produce prose ($0.21). B13 caching claws back
some input cost on the shared prefix but cannot offset the 2.4×
raw input volume. Total: $0.752.

The honest pattern citation: B12 + B13 + B14b assume that the
fan-out shape produces enough TRIVIAL surface to overcome the
per-dispatch overhead. On doc-audit, only 50% of lenses are
TRIVIAL-eligible. Below that threshold the math inverts. The
v0.3.5 advantage on this workload is not raw $; it is reviewability
(separable edit-diff stream) and cross-operator cache reuse.

A future genesis revision should detect this profile during step
3.2 and prefer the v0.2-style monolithic panel when TRIVIAL
surface is < 60% of total lens count. This PR ships the patterns
and the empirical anchoring; the heuristic that prevents
fan-out-tax mis-application is follow-up work.

### B16 is a quality control, not just a cost knob

[B-pat-B16](scenario-runs/results/B-pat-B16/cost-report.json) ran
v0.3.5 with high reasoning effort on every lens. Beyond the 42%
extra cost, the cell observed **severity inflation on TRIVIAL
lenses**: issue #4106 (docs 404, cosmetic) was rated P1 by a
high-effort Haiku because deep reasoning over-indexed on
"onboarding-blocker" framing. The effort governor is a guard
against lenses being too smart for their job.

### Caveman compression works because TRIVIAL lenses are classifiers

A severity-keyword lens is essentially: read text → pick one of
{blocker, high, medium, low}. Verbose prose briefing does not
improve classification accuracy; it inflates input. The CAVEMAN
brief (~80 tokens: imperatives + JSON schema + one grounding line
defining "blocker") gets 75% verdict agreement with the verbose
brief, and **both disagreements are upward escalations** that a
human triager would defend. For classifier lenses, compression is
essentially free. Promoted to corpus as
[§B14b CAVEMAN BRIEF](../../skills/genesis/assets/design-patterns.md).

---

## Per-pattern attribution table

For an operator weighing v0.3.5 adoption: per-pattern dollar
attribution on measured workloads, with firing rule.

| # | Pattern | When it fires | Measured effect | Evidence |
|---|---------|---------------|-----------------|----------|
| 1 | [**B15 + S7**](../../skills/genesis/assets/design-patterns.md) TOOL SUBSET + TOOL BRIDGE | Bulk mutation: N similar items, well-defined transform | **~75× on N=19**, scales with N | [A3](scenario-runs/results/A3-s2-v02/cost-report.json) · [A4](scenario-runs/results/A4-s2-v035/cost-report.json) |
| 2 | [**B12**](../../skills/genesis/assets/design-patterns.md) PER-LENS ROUTING | Fan-out with heterogeneous lens depth AND > 60% TRIVIAL surface | **2.27×** on 6-lens panel; **negative-net on doc-audit** (only 50% TRIVIAL) | [B-pat-B12](scenario-runs/results/B-pat-B12/cost-report.json) · [S2N-v035](scenario-runs/results/S2N-v035/cost-report.json) |
| 3 | [**B14b**](../../skills/genesis/assets/design-patterns.md) CAVEMAN BRIEF | TRIVIAL-class lens with stable schema | **1.81×** on severity classification | [B-pat-B14-caveman](scenario-runs/results/B-pat-B14-caveman/cost-report.json) |
| 4 | [**B16**](../../skills/genesis/assets/design-patterns.md) EFFORT GOVERNOR | TRIVIAL lens (always); REVIEWER conditionally | **1.72×** + quality control | [B-pat-B16](scenario-runs/results/B-pat-B16/cost-report.json) |
| 5 | [**B13**](../../skills/genesis/assets/design-patterns.md) CACHE-AWARE PREFIX | N dispatches sharing brief + corpus | **~2.5×** on cached input; partial offset on S2 doc-audit | modeled · [S2N-v035](scenario-runs/results/S2N-v035/cost-report.json) |
| 6 | [**A12**](../../skills/genesis/assets/architectural-patterns.md) GRADIENT WORKFLOW | Whole-workflow guard against ceremonial bind-up | qualitative — prevents bloat | [APPENDIX](ab-experiment-apm-1424/APPENDIX-iterative-history.md) Cell F→D |
| 7 | [**benchmark-grounding** reference](../../skills/genesis/assets/runtime-affordances/references/benchmark-grounding.md) | Operator contests a Haiku/Sonnet/Opus boundary | grounds B12/B14b SELECTION RULE choices in vals.ai SWE-bench, Terminal-Bench, Vals Index data | added 2026-05-29 |

**Compounding example (S1).** All patterns active modeled at
**~$0.10** vs B12-only $0.238 vs all-OFF $0.540 — **~5× total
compounded savings**, attributable per pattern.

**Counter-example (S2 doc-audit).** Same patterns active produce
**+27% cost** vs v0.2 because the TRIVIAL surface is below the
threshold where B12 routing recovers fan-out overhead. The
ablation is the workload itself.

---

## What this PR does NOT prove

- **Cross-harness portability.** All measurements use Anthropic
  models on the Copilot CLI harness. Claude Code, OpenCode,
  Codex, Cursor — not measured.
- **Quality at scale.** Caveman verdict agreement was measured on
  8 issues, not 800. Larger samples would tighten the
  confidence interval.
- **B13 isolated empirical run.** B13's contribution is modeled
  from [Anthropic's published cache-read pricing](https://www.anthropic.com/pricing)
  applied to A2's stable prefix. An isolated A/B with cache
  disabled would produce a measured number.
- **Behaviour at 10× scale.** S3 was 19 files; S1 was 8 issues;
  S2 doc-audit was 11 pages. Behaviour at 10× is extrapolation,
  not measurement.
- **Fan-out tax threshold not derived.** S2 shows v0.3.5 is more
  expensive than v0.2 when TRIVIAL surface is ~50% of total
  lenses; the exact threshold where the trade-off inverts is not
  measured. A follow-up genesis revision should encode this
  threshold and prefer monolithic panels below it.

---

## Appendix — full materials

- [`scenario-runs/results/`](scenario-runs/results/) — per-cell
  `cost-report.json` artifacts and verdict outputs
- [`scenario-runs/results/COSTING.md`](scenario-runs/results/COSTING.md)
  — $/Mtok rates and per-cell methodology
- [`scenario-runs/fixtures/`](scenario-runs/fixtures/) — S1
  issues fixture, S2 doc-audit pages (S2N-doc-audit), S3 repo
  fixture
- S2 doc-audit per-cell results:
  [zero-Opus](scenario-runs/results/S2N-zero-opus/cost-report.json)
  · [zero-Sonnet](scenario-runs/results/S2N-zero-sonnet/cost-report.json)
  · [v0.2](scenario-runs/results/S2N-v02/cost-report.json)
  · [v0.3.5](scenario-runs/results/S2N-v035/cost-report.json)
- [`cross-scenario/`](cross-scenario/) — architect-stage handoff
  packets for S1, S2, S3 × v0.2 and v0.3.5 (6 cells)
- [`ab-experiment-apm-1424/APPENDIX-iterative-history.md`](ab-experiment-apm-1424/APPENDIX-iterative-history.md)
  — full chronological history of v0.3.0 → v0.3.5 iteration,
  prior experimental cells, audit pass, interim REPORT drafts.
  Kept for traceability; the present REPORT supersedes it.
- Corpus entry points: [`skills/genesis/SKILL.md`](../../skills/genesis/SKILL.md)
  · [design-patterns](../../skills/genesis/assets/design-patterns.md)
  · [architectural-patterns](../../skills/genesis/assets/architectural-patterns.md)
  · [model-catalog](../../skills/genesis/assets/runtime-affordances/model-catalog.md)
  · [benchmark-grounding](../../skills/genesis/assets/runtime-affordances/references/benchmark-grounding.md)
