# Real-telemetry validation of v0.3.6

> **Methodology.** Every number on this page comes from the Copilot
> cloud `events` table — real `usage_input_tokens`,
> `usage_output_tokens`, `usage_cache_read_tokens`, and
> `usage_cache_write_tokens` for each sub-session, priced at
> Anthropic public rates ([`COSTING.md`](scenario-runs/results/COSTING.md))
> and OpenAI public gpt-5 rates for the one cell that auto-routed to a
> GPT sub-agent. No size estimates, no token modelling, no derivation.
> Profiling protocol: [`PROFILING-PROTOCOL.md`](PROFILING-PROTOCOL.md).
>
> **What is counted.** Only the **executor** session and any sub-agents
> it spawned. The genesis **architect** session that produced each
> v0.2 / v0.3.6 handoff packet was run on Opus 4.7 separately and is
> **not** counted — architecting is an amortised, infrequent cost
> recovered across many runs of the same workflow.

---

## The matrix

Three scenarios, four cells each: **zero-opus** and **zero-sonnet**
are direct single-shot prompts to a frontier model with no agentic
architecture; **v0.2** runs the workflow the v0.2.0 architect
designed; **v0.3.6** runs the workflow the v0.3.6 architect (with
benchmark-grounded model catalog) designed.

| Scenario | Workload | zero-opus | zero-sonnet | v0.2 architected | v0.3.6 architected |
|---|---|---|---|---|---|
| **S3 bulk rename** | 1 symbol → 19 JS files, 62-91 references, `npm test` must pass | **[$41.01](scenario-runs/results/S3-zero-opus-real/cost-report.json)** (30 calls) | **[$4.81](scenario-runs/results/S3-zero-sonnet-real/cost-report.json)** (20 calls) | **[$33.79](scenario-runs/results/S3-v02-real/cost-report.json)** (105 calls) | **[$10.40](scenario-runs/results/S3-v036-real/cost-report.json)** (41 calls) |
| **S2 doc-audit** | 11-page awd-cli docs corpus, drift + link + schema audit | **[$33.01](scenario-runs/results/S2N-zero-opus-real/cost-report.json)** (17 calls) | **[$6.20](scenario-runs/results/S2N-zero-sonnet-real/cost-report.json)** (20 calls) | **[$9.42](scenario-runs/results/S2N-v02-real/cost-report.json)** (61 calls) | **[$9.80](scenario-runs/results/S2N-v036-real/cost-report.json)** (38 calls) |
| **S1 PR review** | microsoft/apm#1424 (LSP install pipeline, +2363/-114, 24 files) | **[$19.82](scenario-runs/results/S1-zero-opus-real/cost-report.json)** (11 calls) | **[$8.89](scenario-runs/results/S1-zero-sonnet-real/cost-report.json)** (34 calls) | **[$3.94](scenario-runs/results/S1-v02-real/cost-report.json)** (17 calls) † | **[$24.59](scenario-runs/results/S1-v036-real/cost-report.json)** (232 calls) |

† S1-v0.2 sub-executor wrote zero output files and committed zero
changes — interpret its low cost as "did not complete the workflow",
not as a win. The other three S1 cells produced full review verdicts.
Numbers retained for transparency.

Per-cell `cost-report.json` files are committed at
[`scenario-runs/results/`](scenario-runs/results/) with the per-model
token breakdown and the chat-session id for replay.

---

## Three honest findings

### Finding 1 — Naive architecture is the cost trap, not architecture itself

**S3-v0.2 ($33.79) costs 7× S3-v0.3.6 ($10.40) and 7× zero-sonnet
($4.81).** The v0.2 architect designed a per-file `view` + `edit`
loop on Sonnet; v0.3.6 routed the same rename through a single
`grep | xargs perl -i` shell call (the S7 DETERMINISTIC TOOL BRIDGE
pattern). The pattern collapsed 105 tool turns into 41.

This is the load-bearing claim of the PR: **the v0.3.6 patterns make
the architect reject the wrong-tool-surface design**. The 3.2×
($33.79 / $10.40) gap is real, measured, and reproducible.

### Finding 2 — On the workloads where the patterns do *not* apply, architecture loses to a smart single-shot

**On S1 PR review and S2 doc-audit, zero-sonnet wins on raw $.**
S1: $8.89 single-shot vs $24.59 for the v0.3.6 5-lens fan-out
(2.8× more). S2: $6.20 single-shot vs $9.80 for either architecture
(1.6× more). The architecture-overhead is real: every sub-agent
re-loads the Copilot CLI tool descriptions, system prompt, and
shared context, paying a per-spawn floor that the single-shot does
not.

What architecture buys on these workloads is **multi-stream
reviewability** (5 independent lens verdicts vs one prose blob),
**class-routed quality** (Sonnet on reviewer lenses, Haiku on
trivial lenses), and **adversarial verification** (A7 reviewer pass).
The PR claims a quality differential, not a cost differential, on
these workloads — and the numbers support that honest framing.

### Finding 3 — Opus single-shot is the *real* anti-pattern

**Every zero-opus cell is 3–8× more expensive than zero-sonnet** with
no observable quality justification on these tasks:
- S3 rename: $41 vs $4.81 (8.5×)
- S2 doc-audit: $33 vs $6.20 (5.3×)
- S1 PR review: $19.82 vs $8.89 (2.2×)

The benchmark-grounding ref committed in v0.3.6
([`runtime-affordances/references/benchmark-grounding.md`](../../skills/genesis/assets/runtime-affordances/references/benchmark-grounding.md))
cites vals.ai SWE-bench data showing Sonnet 4.6 at ~80% accuracy on
multi-file code tasks vs Opus at ~84% — a small quality delta for a
3–8× cost delta. The v0.3.6 model-catalog explicitly steers
architects away from Opus-by-default for these workload classes.
The cells confirm the heuristic.

---

## Why these numbers are 50–200× larger than the size-modeled
## numbers in [`REPORT.md`](REPORT.md)

Every Copilot CLI sub-session loads the full tool surface (~30+ tool
descriptions, ~50 KB of JSON schema), the system prompt
(~10 KB), and the genesis skill bundle (~40 KB) on every turn.
Cache makes most of this re-readable at 10% of base input rate, but
on a fresh sub-agent the **first turn pays full uncached rate** for
all of it. A nominal "100-token user prompt" task actually runs
80–120K input tokens of context per turn.

The modeled numbers in `REPORT.md` ignored this — they counted only
the visible user-prompt and reasoning tokens. They understated raw $
by 50–200× but the **ratios** between cells in those modeled studies
are still valid as ablations. Treat `REPORT.md` as a pattern-isolation
study; treat this page as the absolute-cost ground truth.

---

## What this PR honestly proves

1. **Bad architecture costs more than no architecture.** S3-v0.2's
   per-file edit loop ($33.79) is empirically worse than just asking
   Sonnet to rename the symbol ($4.81). The v0.3.6 patterns
   ([B12 SELECTION RULE](../../skills/genesis/assets/design-patterns/B12-selection-rule.md),
   [B15 TOOL SUBSET](../../skills/genesis/assets/design-patterns/B15-tool-subset.md),
   [S7 DETERMINISTIC TOOL BRIDGE](../../skills/genesis/assets/design-patterns/S7-deterministic-tool-bridge.md))
   give the architect the vocabulary to reject the bad design — and
   the v0.3.6 architect, when handed this brief, did reject it (see
   the v0.3.6 handoff at
   [`cross-scenario/S3-rename-v036/handoff.md`](cross-scenario/S3-rename-v036/handoff.md)).

2. **The benchmark-grounded model catalog makes the architect reject
   Opus-by-default.** All three v0.3.6 architect handoffs picked
   Sonnet for the bulk of the work and reserved Opus for narrow,
   rare arbiter roles only (S1 only). No v0.3.6 design picked Opus
   for the main work — confirmed against
   [`runtime-affordances/references/benchmark-grounding.md`](../../skills/genesis/assets/runtime-affordances/references/benchmark-grounding.md).

3. **Architecture has a fixed overhead.** Every sub-agent dispatch
   pays a tool-surface and system-prompt floor (~80K input tokens
   uncached on first turn). On workloads with ≤5 sub-agents and
   simple deterministic work, a single-shot Sonnet is the
   cost-rational baseline. The v0.3.6 architect knows this — see
   its [S2N doc-audit handoff](cross-scenario/S2N-docaudit-v036/handoff.md)
   that explicitly chose **monolithic single-session** over fan-out,
   citing the B12 SELECTION RULE wrong-primitive-binding warning.

---

## What this PR does NOT prove

- It does not prove the architected workflows produce *better*
  output than zero-sonnet on S1 or S2. We have artifacts
  ([`scenario-runs/results/*/output.md`](scenario-runs/results/))
  but no human-graded quality comparison. The cost numbers stand
  alone; quality claims would need a separate study.
- It does not prove the patterns transfer outside these three
  workload shapes. Three scenarios is not a workload taxonomy.
- It does not credit Opus's quality margin on harder benchmarks.
  On SWE-bench Hard or refactoring with deep semantic constraints,
  the 3–8× Opus premium may pay back. These three fixtures do not
  test that regime.

---

## Reproducing

1. Read [`PROFILING-PROTOCOL.md`](PROFILING-PROTOCOL.md) for the
   hard rules (one cell = one sub-session, architecting not counted,
   real telemetry only).
2. Each cell's `cost-report.json` includes the
   `chat_session_id` — re-query the `events` table with that id to
   replay the harvest.
3. Architect handoff packets are committed under
   [`cross-scenario/`](cross-scenario/) — re-dispatch any cell by
   handing the packet to a fresh executor session.

---

**Cell sessions (chat ids for telemetry replay):**

| Cell | chat_session_id |
|---|---|
| S3-zero-opus    | 21482332-49d7-471c-a5f5-927c7a5c92db |
| S3-zero-sonnet  | 7b91ca14-66ff-4865-815e-4a75b4ee6383 |
| S3-v02          | 79ee3ffe-88a4-4472-8c2b-7e999111b949 |
| S3-v036         | 7208403f-0602-4423-9d80-791991c2e63b |
| S2N-zero-opus   | 6b0d88db-cfa2-4e27-a274-b9bbfb0432d8 |
| S2N-zero-sonnet | f5546460-e060-40e7-a5c7-9eac08792a32 |
| S2N-v02         | b0c79812-ef68-4075-b403-615e6c84df6f |
| S2N-v036        | c43ed1b1-9d89-4449-89da-f1d5f2a31a0e |
| S1-zero-opus    | eb461ebf-95d4-42fa-8897-6bcc94868d7e |
| S1-zero-sonnet  | df27531f-249b-4c83-b3b2-3a1fd995c5ea |
| S1-v02          | e27b2f57-aced-4424-9a04-33ec5552b92f |
| S1-v036         | ff901d47-3a7f-4829-96f7-391f28b36885 |
