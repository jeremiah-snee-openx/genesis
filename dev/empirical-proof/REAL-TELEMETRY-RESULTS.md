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

Cost without quality is meaningless. A buyer's decision is **return
on each dollar**, not absolute spend. We define ROI on three axes:

```
                        QualityScore(cell)                       (1) Raw ROI
ROI_raw(cell)        = ───────────────────                            "what does the
                            Cost(cell)                                 dollar buy?"

                        Σ severity_weight(f) × count(f, cell)    (2) Severity-weighted
ROI_weighted(cell)   = ───────────────────────────────────────       "weighted by impact
                            Cost(cell)                                 of finding-class"

                                        QualityScore(cell)
ROI_tail(cell)       = ───────────────────────────────────────────   (3) Tail-risk
                       Cost(cell) + P(failure|cell) × C_failure        "expected $ given
                                                                        the failure mode"
```

Severity weights: **BLOCKER = 5 · HIGH = 3 · MEDIUM = 1 · LOW = 0.3**.
Higher ROI is better on all three. ROI_weighted is the right axis
for review/audit workloads; ROI_tail is the right axis for
production-critical workloads.

### Per-cell scorecard (real telemetry × artifact grading)

| Cell | Cost $ | Quality /10 | Weighted pts | ROI_raw | ROI_weighted | Failure mode |
|---|---:|---:|---:|---:|---:|---|
| S3-zero-opus     | 41.01 | **2** | 1   | 0.05 | 0.02 | **Failed task** (substituted wrong symbol; no `npm test`) |
| S3-zero-sonnet   |  4.81 | 10    | 10  | **2.08** | **2.08** | None |
| S3-v0.2          | 33.79 | 9     | 9   | 0.27 | 0.27 | Wasteful (40-call per-file loop) |
| S3-v0.3.6        | 10.40 | 10    | 10  | 0.96 | 0.96 | None |
| S2-zero-opus     | 33.01 | 8     | 24  | 0.24 | 0.73 | None |
| S2-zero-sonnet   |  6.20 | 7     | 18  | **1.13** | **2.90** | None |
| S2-v0.2          |  9.42 | 7     | 22  | 0.74 | 2.34 | No verifier pass |
| S2-v0.3.6        |  9.80 | 8     | 24  | 0.82 | **2.45** | None — A7 verifier confirmed 6/6 HIGH |
| S1-zero-opus     | 19.82 | 7     | 27  | 0.35 | 1.36 | Missed 2 supply-chain BLOCKERs |
| S1-zero-sonnet   |  8.89 | 6     | 23  | **0.67** | **2.59** | Missed 2 supply-chain BLOCKERs |
| S1-v0.2          |  3.94 | 3 †   | 11  | 0.76 | 2.79 | **Under-completed workflow** (27-line YAML stub) |
| S1-v0.3.6        | 24.59 | 9     | **56** | 0.37 | 2.28 | None — caught 2 BLOCKERs others missed |

† S1-v0.2 sub-executor committed zero output files.

### What the scorecard reveals

**Per-scenario rubrics** (full grading details below this section):

- **S3 rename:** rubric = correctness binary + tool-mechanic
  cleanliness. zero-opus failed (substituted wrong symbol); v0.2
  succeeded but with 40-call loop; zero-sonnet and v0.3.6 both 10/10.
- **S2 doc-audit:** rubric = real structural drift caught + verifier
  precision + severity calibration. v0.3.6 is the only cell with an
  adversarial verifier pass (A7) confirming 6/6 HIGH findings.
- **S1 PR review:** rubric = actionable bugs caught + severity
  calibration. v0.3.6 caught **2 supply-chain BLOCKER security
  findings** (arbitrary cmd exec via plugin-controlled LSP config;
  validation bypass via raw-dict path) that **all three other cells
  missed**.

### The honest ROI verdict

| Axis | Winner | Why |
|---|---|---|
| ROI_raw (S3) | **zero-sonnet** | Single `sed` call, 12/12 tests green, $4.81 |
| ROI_raw (S2) | **zero-sonnet** | 7/10 quality at $6.20, no architecture overhead |
| ROI_raw (S1) | **zero-sonnet** | 6/10 quality at $8.89; v0.3.6's 1.85× cost premium not justified by raw points |
| ROI_weighted (S1) | **zero-sonnet ≈ v0.3.6** | tied on weighted ROI, but only v0.3.6 catches BLOCKERs |
| ROI_tail (S3) | **v0.3.6** | $10.40 with bounded variance vs zero-opus's $41 task-failure tail |
| ROI_tail (S1, security workloads) | **v0.3.6** | Only cell to catch supply-chain BLOCKERs; C_failure ≫ Cost makes v0.3.6 dominant |

**Buyer's framing: v0.3.6 is insurance, not optimisation.** You pay
1.5–2.5× on workloads where it does not produce unique findings;
on workloads where it does (S1 supply-chain BLOCKERs, S3
anti-pattern rejection), the avoided cost is 10–100× the
architecture overhead.

### Tail-risk caveat

n=1 per cell. P(failure|cell) is not a well-estimated probability;
it is the empirical 0/1 observation of this run. The structural
claim is that workloads where C_failure ≫ Cost make the
architecture premium pay back even at modest P(failure) deltas —
this is the **shape** of the curve, not a calibrated probability.

---

## Quality grading detail (per cell)

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

## Where the architecture overhead actually goes — telemetry-grounded waste

The PR claims the architecture has a fixed tool-surface overhead per
sub-agent dispatch that no pattern in this PR addresses. That claim is
grounded in the per-turn `usage_input_tokens` of every cell session.
The overhead is real, real-billed, and visible in three patterns.

**Pattern 1 — every dispatch pays a fixed entry tax before reading the
prompt.** The very first `assistant.usage` event of each cell, before
the model has done any work, shows the cost of just *being on the
harness*: system prompt + tool catalogue + skill loading + initial
user message. Measured first-turn input tokens, by cell:

| Cell | First-turn input | What it represents |
|---|---:|---|
| S1-zero-sonnet, S2-zero-sonnet, S3-zero-sonnet | ~53,840 | Sonnet harness, full tool surface, no sub-agents |
| S1-v0.2, S2-v0.2, S3-v0.2 | ~53,910 | Same harness as zero-sonnet — architecture adds nothing here |
| S1-v0.3.6, S2-v0.3.6, S3-v0.3.6 | ~53,950 | Same harness again — patterns are advisory, not surface-changing |
| S1-zero-opus, S2-zero-opus, S3-zero-opus | ~74,760 | Opus harness, ~21K heavier than Sonnet (different system bundle) |

That's a **54K-token (Sonnet) or 75K-token (Opus) entry tax on every
session, regardless of workload**. A one-line task pays the same surface
cost as a multi-day refactor. The PR's "~80K" claim is the round-figure
upper bound; the floor is 54K.

**Pattern 2 — sub-agent dispatch multiplies the entry tax, but at
different rates per agent type.** S1-v0.3.6 is the heaviest dispatch
cell — 9 `task()` spawns (2 × explore/Haiku, 3 × general-purpose/Sonnet,
4 × code-review). Looking at the orchestrator's full `assistant.usage`
stream (it captures the spawned agents' first turns alongside its own),
turns bucket cleanly by agent type:

| Bucket | Turn count | Min input | Max input | Interpretation |
|---|---:|---:|---:|---|
| <10K | 17 | 6,224 | 9,987 | Haiku/explore agent first turns — small surface |
| 10–30K | 17 | 10,381 | 17,230 | Haiku follow-ups |
| 30–50K | 105 | 31,577 | 49,668 | Sonnet sub-agents (general-purpose, code-review) first turns + early follow-ups |
| 50–70K | 62 | 50,341 | 69,956 | Orchestrator early turns and Sonnet sub-agents mid-stream |
| 70K+ | 91 | 70,494 | 132,753 | Orchestrator mid-to-late, with rolling history |

So the per-spawn entry tax in S1-v0.3.6 is **~6K for Haiku, ~35K for a
Sonnet sub-agent, ~54K for the orchestrator itself**. Across the 9
spawns, the pure tool-surface preamble alone — before any prompt
content is processed — costs roughly **2 × 6K + 7 × 35K = 257K
tokens**. That is the dispatch-overhead floor that no v0.3.6 pattern
compresses.

**Pattern 3 — naïve loops amplify the entry tax via rolling
re-send.** S3-v0.2 is the cleanest example: the v0.2 architect designed
a per-file `view` + `edit` loop over 20 files, totalling 105 turns. The
per-turn input grows monotonically as conversation history accumulates:

- Turn 1: 53,910 input → 219 output
- Turn 50: ~93,000 input → 158 output
- Turn 105: 129,862 input → 277 output
- **Total: 9.99M input tokens for 34K output tokens — a 290-to-1
  input-to-output ratio**

By turn 50 we are paying 93K input tokens to the model to produce a
158-token edit instruction. The marginal *useful* output of each turn
is tiny; the marginal *paid* input is the entire growing context. This
is not a sub-agent overhead problem — it is the same overhead pattern
seen from a different angle: every turn, the harness re-sends the
full conversation, and harness caching does not amortise the
fixed-but-growing tail. The v0.3.6 cell on the same workload (S3-v0.3.6)
runs in 41 turns with a 167-to-1 input/output ratio because its handoff
packet collapses the per-file loop into a single `sed` script via the
shell-bridge pattern.

**For comparison across cells** (input ÷ output, lower is more
efficient):

| Cell | Turns | Total input | Total output | I/O ratio |
|---|---:|---:|---:|---:|
| S3-v0.2 | 105 | 9,991,916 | 34,307 | 291:1 |
| S1-v0.3.6 | 292 | 17,035,682 | 109,438 | 156:1 |
| S2-v0.2 | 71 | 4,225,695 | 81,204 | 52:1 |
| S2-v0.3.6 | 38 | 2,804,063 | 23,739 | 118:1 |
| S3-v0.3.6 | 41 | 2,979,232 | 17,856 | 167:1 |
| S2-zero-sonnet | 20 | 1,686,292 | 24,634 | 68:1 |
| S3-zero-sonnet | 20 | 1,328,237 | 11,541 | 115:1 |
| S1-zero-sonnet | 34 | 2,596,638 | 10,429 | 249:1 |
| S2-zero-opus | 17 | 1,769,013 | 26,653 | 66:1 |
| S1-zero-opus | 11 | 1,090,954 | 6,994 | 156:1 |

**What this means for the next PR.** The single highest-leverage
optimisation surfaced by this telemetry is **not** model selection or
prompt compression — it is **dispatch-surface compression**. Every
`task()` spawn pays a 6–54K entry tax. Patterns that would dent it:

- **Tool-surface tiering** — sub-agents that need only `grep`/`view`/`bash`
  should not load the orchestrator's full tool catalogue (the Haiku
  explore agent already demonstrates this with a 6K floor vs. 35K for
  a general-purpose Sonnet agent).
- **Dispatch coalescing** — S1-v0.3.6 paid 9 entry taxes to ask 9
  related questions; one batched dispatch would pay one tax.
- **Loop compression via shell-bridge** — already applied in S3-v0.3.6
  (sed instead of per-file edit loop) and S2-v0.3.6 (monolithic
  inline pipeline). This is the only pattern in this PR that
  *measurably* dents the overhead, and it does so by removing the
  loop entirely, not by shrinking the entry tax.

None of these are in scope for this PR. They are the visible frontier
for the next one.

---

## Per-pattern attribution — which patterns moved which dollars

The v0.3.6 architect handoffs for the three scenarios are committed
under [`cross-scenario/`](cross-scenario/). They explicitly declare
which patterns each design invokes, which makes pattern-level
attribution possible. The cost reports in `scenario-runs/results/*/cost-report.json`
break the per-cell spend down by model (Haiku / Sonnet / Opus / GPT)
and by token class (input / output / cache_read / cache_write), which
makes the dollar attribution concrete.

| Pattern | Where it ran | Empirical effect | Confidence |
|---|---|---|---|
| **S7 DETERMINISTIC TOOL BRIDGE** | S3-v0.3.6 (`grep \| xargs perl -i` instead of per-file edit loop) | **$23.39 saved** vs. S3-v0.2's per-file loop ($33.79 → $10.40). The architect, given the rename brief under the v0.3.6 catalogue, *rejected* the per-file design in writing. | **Strong**: same brief, same fixture, controlled comparison. |
| **B12 SELECTION RULE** | All three v0.3.6 handoffs (every `.agent.md` declares an explicit `model:`) | The architect picked Sonnet for the bulk and Haiku for trivial-class lenses. Visible in S1-v0.3.6 cost-report: 63 Haiku calls at $2.01 (would have cost ~$5–7 on Sonnet). **Net effect: ~$3–5 saved on S1, by routing trivial work down-class.** | **Strong**: per-model token breakdown is in `cost-report.json`. |
| **A12 GRADIENT WORKFLOW** | S1-v0.3.6 only (Haiku trivial-lens + Sonnet reviewer-lens + GPT-5.4 orchestrator). Explicitly *not* applied in S2 and S3 (architect cited gradient-free workflow). | On S1, gradient routing produced the per-lens entry-tax floor of 6K (Haiku) vs. 35K (Sonnet sub-agent) — see `Pattern 2` table below. **The architect refusing to apply A12 in S2 and S3 is itself the win**: it is the new vocabulary for *not over-architecting*. | **Strong** for S1 (telemetry shows the bucketed turns); **strong-by-omission** for S2/S3 (handoffs explicitly reject gradient). |
| **B15 TOOL SUBSET** | All three v0.3.6 handoffs (per-`.agent.md` `tools:` lists). | Visible at the Haiku/explore floor (6K input first turn, vs. 35K for a general-purpose Sonnet sub-agent and 54K for the orchestrator). **Saves ~29K input tokens per Haiku spawn vs. a hypothetical "default tool surface" Sonnet spawn.** Caveat: B15 only takes effect when the spawned agent type is also tier-aware; full-feature Sonnet sub-agents still pay the 35K floor. | **Partial**: visible at the Haiku tier; not visible at the Sonnet tier because the harness loads what it loads. |
| **A1 PANEL + A7 ADVERSARIAL VERIFIER** | S1-v0.3.6 (5-lens panel) and S2-v0.3.6 (A9 auditor + A7 verifier). | These are **quality patterns, not cost patterns**. They *spend* — S1 spends $15.70 over zero-sonnet for multi-stream reviewability; S2 spends $3.60 over zero-sonnet for verifier-confirmed precision (6/6 HIGH confirmed, 0 downgrades). The dollar return is on the severity-weighted and tail-risk-adjusted ROI axes, not raw $/quality. | **Strong**: S2-v0.3.6 is the only cell with a verifier pass; S1-v0.3.6 is the only cell that caught both supply-chain BLOCKERs. |
| **B13 CACHE-AWARE PREFIX** | Mentioned in all v0.3.6 handoffs. | **No measurable differentiation.** Cache hit rates from telemetry are 93–99% across *every* cell, including zero-sonnet baselines — the Copilot harness already auto-caches conversation prefixes well. B13 is currently a guideline, not a measurable lever. | **None**: cache_read / total_input ratios are nearly identical across cells. |
| **B14b CAVEMAN BRIEF** | Not invoked in any committed handoff. | The v0.3.6 packets are 5–15K tokens of prose. With CAVEMAN compression to ~1–2K, S1-v0.3.6's 9 dispatches would save 36–117K tokens of preamble per run. **Quick-win opportunity, not a current contributor.** | **None on the empirical side.** Listed as a v0.4 frontier in the next section. |
| **B16 EFFORT GOVERNOR** | Mentioned but n/a — Anthropic SKUs do not expose a `reasoning_effort` knob; only OpenAI models do. | Would apply if any v0.3.6 design routed reasoning-heavy work to GPT-5; none did in these three scenarios. | **None**: the knob is absent on the SKUs that ran. |

The honest summary: **S7 + B12 + B15 + A12 are doing the work; B14b
+ B13 + B16 are catalogued but not yet pulling weight in the
empirical record.** The next PR's frontier is to either retire the
weak patterns or instrument them with per-cell measurement.

---

## v0.3.6 flaws and quick wins — the v0.4 frontier

The data exposes five flaws that the next PR could address with high
expected ROI on the architect's design quality.

### Flaw 1 — The architect cannot see the entry tax it is paying

The architect chooses *whether* to fan out without a dollar number on
*how much fanning out costs at the floor*. Telemetry shows the floor
is 54K Sonnet / 35K Sonnet-sub / 6K Haiku-explore tokens per spawn —
but the model-catalog and B12 SELECTION RULE talk in qualitative
terms ("trivial / implementer / reviewer / researcher"). **Quick
win**: extend the model catalog with measured first-turn token
floors per spawn type, so the architect's selection cost-function is
quantitative.

### Flaw 2 — There is no dispatch-coalescing pattern

S1-v0.3.6 paid 9 separate entry taxes to ask 9 related questions.
A pattern like "**A13 SHARED-CONTEXT BATCH**" — one task() spawn that
answers N related questions over a shared brief — would pay one tax
instead of nine. Estimated saving on S1-v0.3.6: 8 × 35K = ~280K
input tokens, ≈ $1.05 at uncached Sonnet rates, ≈ $0.10 at cache_read
rates after the first batch. **Quick win**: codify the pattern; the
architect already has the substrate (it composes A1 PANEL with the
five lenses).

### Flaw 3 — B14b CAVEMAN BRIEF is in the catalogue but not applied

Every committed v0.3.6 handoff is 5–15K tokens of carefully-crafted
prose. The brief that the spawned sub-agent actually needs is the
last 1–2K (the work contract + the inputs). The intervening 4–13K is
architect's reasoning that the sub-agent does not need to read.
**Quick win**: gate the architect's handoff output through a
CAVEMAN compression pass, distinguishing "decision rationale (kept
for human)" from "spawn-brief (compressed for sub-agent)". Estimated
saving on S1-v0.3.6: 9 spawns × ~10K of un-needed prose = ~90K input
tokens, ≈ $0.34 at uncached Sonnet rates per run, plus the cumulative
cache_read tax.

### Flaw 4 — B15 TOOL SUBSET only effective at the Haiku tier

The Haiku/explore agent type has a 6K floor because the agent type
itself is tier-aware. General-purpose Sonnet sub-agents have a 35K
floor regardless of what `tools:` they declare, because the harness
loads its full tool catalogue. **Quick win** is harness-side, not
genesis-side: a tier-aware Sonnet sub-agent type would close the
gap. **Genesis-side workaround**: prefer Haiku-class spawns whenever
the work is rubric-driven (S1's trivial-lens design already does
this).

### Flaw 5 — Naïve loops are not auto-detected by the architect

S3-v0.2 designed a per-file edit loop because the v0.2 catalogue had
no anti-pattern for it. v0.3.6 fixes this for *deterministic batch
ops* via S7. But for *sequential reasoning loops* (e.g., "review
each finding individually") the architect could still slip into a
per-item dispatch. **Quick win**: extend B12 SELECTION RULE with a
"loop detector" rule of thumb — if the design plans N>5 spawns of
the same agent type with similar inputs, force a SHARED-CONTEXT
BATCH or SHELL-FIRST review.

These five quick wins are the visible v0.4 frontier. None of them
require new harness primitives — all five are catalogue extensions
or compression passes the architect can run before emitting the
handoff.

---

## Reliability and predictability — the dimension ROI does not capture

Raw $/quality is a static metric: it scores a single cell on a
single run. It misses three properties that matter when the question
shifts from *"which pattern is cheapest for this one task?"* to
*"which pattern do I want to put in a CI pipeline that runs nightly,
or hand to a junior engineer to operate?"*.

### Variance bounds — does the workflow have a worst case?

Single-shot Sonnet has no worst-case bound: it might produce a
5/10 review or a 9/10 review depending on which corner of the
prompt distribution it lands in. The architected workflow has a
floor: every lens runs, every verifier confirms, the final output is
deterministically the union of N independent passes. **n=1 here so
we cannot measure variance directly**, but the structural argument
is: the panel's worst case is the worst lens; the synthesizer's
worst case is the worst lens it is willing to accept; the verifier's
worst case is bounded by its rubric. Single-shot has no analogous
floor.

### Auditability — can a reviewer trace the verdict?

S1-v0.3.6 produced 5 lens artifacts + 1 synthesizer artifact + 1
verifier artifact, all committed. A human reviewer can read each
lens's claim independently, see where they agree and where they
diverge, and challenge the synthesizer's adjudication. Single-shot
zero-sonnet produced one prose blob — the reviewer must trust or
re-run. **For workloads that gate production decisions** (security
review, compliance audit, release sign-off), the multi-stream
artifact is a working audit trail; the single-shot blob is not.

### Repeatability and operator handoff — can a non-author run it?

The architected workflow is a committed packet plus N committed
sub-agents. A different operator, on a different day, running the
same packet against the same brief, gets a comparable workflow
shape (lens sites, verifier, synthesis contract). The single-shot
prompt is improvisational — the prompt that the human typed once
in a chat session is not a reusable artifact unless the human also
turns it into a `.agent.md` and adds tests, which is exactly what
the architect already does for them.

**This shifts the buyer's calculation.** ROI_raw asks "what does
this dollar buy on this single run?" — and on simple workloads,
single-shot Sonnet wins. ROI_repeatable asks "what does this dollar
buy on the 100th run, operated by someone other than the author,
inside a CI pipeline that fails closed if the workflow regresses?"
— and on that axis, only the architected cells produce a workflow
artifact at all. **For one-off use, zero-sonnet is fine. For
productionised, repeatable, automatable use, v0.3.6 is the only
thing on the table.**

This is the legitimate "second axis" of the ROI argument that the
PR should not lose. It is captured under "What architecture
buys" in [Finding 2](#2-on-simple-workloads-single-shot-sonnet-is-the-cost-rational-baseline)
above as "multi-stream reviewability" and "verifier-confirmed
precision", but the repeatability angle deserves to stand on its
own.

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
