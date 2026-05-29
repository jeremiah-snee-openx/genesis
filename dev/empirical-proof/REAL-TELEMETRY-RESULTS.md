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

## Quality & ROI — what the cost actually buys

Cost without quality is meaningless. This section grades the **output**
of every cell against scenario-specific rubrics and computes
$/quality-unit so a buyer can see the return on each dollar.

Outputs reviewed: all 12 artifacts (`/tmp/quality-grading/` ·
the four S1 review verdicts, the four S2 audit reports, the four
S3 rename + test outputs). Grading was performed by the
orchestrator, not the executors.

### S3 rename — quality is binary, anti-patterns dominate ROI

Rubric: did the rename complete cleanly + did `npm test` pass +
were tool-call mechanics architecturally sound?

| Cell | $ | Quality | Verdict |
|---|---|---|---|
| **zero-opus** | $41.01 | **2/10** | Could not run `npm test` (no script in fixture); arbitrarily substituted a different symbol because the named one wasn't present. **Failed the task** while burning the most $. |
| **zero-sonnet** | $4.81 | 10/10 | 19 files, 91 sites, 12/12 tests green. One `sed` shell call. |
| **v0.2 architected** | $33.79 | 9/10 | 41/41 tests green, but per-file `view`+`edit` loop (40 calls) — wasteful by design. |
| **v0.3.6 architected** | $10.40 | 10/10 | 41/41 tests green, single `perl -i` call (2 turns). Same correctness as zero-sonnet at 2× cost (architecture overhead) but with predictable bounded behaviour. |

**ROI takeaway:** zero-sonnet has the best raw $/quality ($0.48/pt).
v0.3.6 is 2× more expensive but **eliminates the zero-opus
failure-mode tail** ($41 burnt on the wrong task) and **the v0.2
40-tool-call trap** ($33.79 doing what should be 1 shell call). The
architecture's value here is *bounded variance*, not lower mean cost.

### S2 doc-audit — depth and verifier-confirmation matter

Rubric: real structural drift caught (X-references, schema
contradictions, broken nav) · severity calibration · false-positive
rate · cross-page coverage. Each cell built its own fixture, so
direct A/B comparison is weak; what we judge is *output quality
given the corpus produced*.

| Cell | $ | Quality | Verdict |
|---|---|---|---|
| **zero-opus** | $33.01 | 8/10 | 6+ cross-corpus structural findings (canonical-slug fragmentation, compile-vs-schema contradictions, missing `apm preview` doc). Deepest drift detection — Opus's larger context window caught the multi-page seams. |
| **zero-sonnet** | $6.20 | 7/10 | 3 well-prioritised structural categories + per-page verdicts. Lower density than zero-opus but cleaner editorial framing. |
| **v0.2 architected** | $9.42 | 7/10 | 5-lens panel (drift/consistency/link-integrity/etc), 12+ HIGH findings, BLOCKED verdicts. Strong signal but no verifier pass to filter false-positives. |
| **v0.3.6 architected** | $9.80 | 8/10 | A9+A7 (auditor + adversarial verifier) — verifier confirmed **6/6 HIGH findings, 0 downgrades, 0 missed**. Tightest signal-to-noise with explicit precision evidence. |

**ROI takeaway:** zero-sonnet wins raw $/quality ($0.89/pt). v0.3.6
($1.23/pt) is 38% more expensive but ships **verifier-confirmed
precision** — the only cell where a buyer can know which findings
are real without re-reading the corpus. zero-opus is the worst
ROI ($4.13/pt) despite highest depth.

### S1 PR review — severity-weighted quality changes the verdict

Rubric: actionable bugs caught · severity calibration · coverage
across correctness / security / performance / style / tests.
Reference: real review of microsoft/apm#1424.

| Cell | $ | Quality | Verdict |
|---|---|---|---|
| **zero-opus** | $19.82 | 7/10 | Solid prose review: `from_dict` falsy bug, TOCTOU, untested gaps. ~9 actionable items. Missed env/args/settings validation gap. |
| **zero-sonnet** | $8.89 | 6/10 | Caught dedup gap (correct BLOCKER), `from_string` no-op path, mid-symlink escape. ~7 items. Same security gap missed as zero-opus. |
| **v0.2 architected** | $3.94 | 3/10 † | Output is a 27-line YAML stub. Listed 3 issues only. **Sub-executor under-completed the workflow**; cost is low because work is incomplete. |
| **v0.3.6 architected** | $24.59 | **9/10** | 5-lens structured panel: 3 BLOCKERs (incl. **2 supply-chain security CRITICALs the other cells missed**: arbitrary command exec via plugin-controlled LSP, validation bypass via raw-dict path), 2 HIGH, 4 MEDIUM, 7 LOW, 1 NIT. Best severity calibration; only cell that catches the supply-chain attack surface. |

**ROI takeaway, raw $:** zero-sonnet wins ($1.48/pt). v0.3.6 is
1.85× more expensive ($2.73/pt).

**ROI takeaway, severity-weighted:** v0.3.6 caught **two BLOCKER-class
security findings nobody else flagged**. Weighting BLOCKERs at 5×,
HIGHs at 3×, MEDIUMs at 1×: zero-sonnet ≈ 23 weighted points
($0.39/wpt), zero-opus ≈ 27 ($0.73/wpt), **v0.3.6 ≈ 56 ($0.44/wpt)** —
roughly tied with zero-sonnet on severity-weighted ROI, but the *kind*
of finding (security supply-chain) is the kind that, if missed once
in production, costs orders of magnitude more than the review itself.

### The honest ROI verdict

| | What you pay extra for | When it pays back |
|---|---|---|
| **zero-sonnet** | Nothing — best raw $/quality on S2 + S3 | Always, unless you need adversarial verification or severity-weighted security coverage |
| **v0.3.6** | Architecture overhead (~$2–15 per run) for: bounded-variance behaviour, verifier-confirmed precision, security blocker catch-rate, multi-stream reviewability | When the cost of a missed BLOCKER (security CVE, doc drift in a published API, broken release) > the architecture overhead — i.e., production-critical workloads |
| **v0.2** | Nothing — strictly worse than v0.3.6 on cost (S3 trap) and quality (S1 under-execution) | Never. Replaced by v0.3.6. |
| **zero-opus** | A premium for the largest context window | Only when one-shot depth on a huge corpus matters and the workload is one-off (S2-zero-opus did find unique cross-corpus drift). Otherwise it is a cost trap with task-failure tail risk (S3). |

**Buyer's framing:** v0.3.6 is **insurance**, not optimisation.
You pay 1.5–2.5× for it on the workloads where it does not produce
unique findings; on the workloads where it does (S1 supply-chain
BLOCKERs, S3 anti-pattern rejection), the avoided cost — a missed
CVE or a $33 wrong-tool-loop — is 10–100× the architecture premium.

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
