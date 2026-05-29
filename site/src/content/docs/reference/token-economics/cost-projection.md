---
title: Cost projection artifact
description: The six-part cost projection Genesis emits at step 6. Bands are the contract; dollar ranges are the prediction. What's auditable vs what ages out.
---

The cost projection lives in the handoff packet alongside the
diagrams and module composition table. **Six parts.**

## 1. Per-module qualitative bands (CONTRACT)

The CONTRACT half. These are the cells step 8 validates against the
emitted code.

| Field | Vocabulary |
|---|---|
| Role class | planner / implementer / reviewer / trivial / long-context-retriever |
| Prefix size | S (under 5K) / M (5-20K) / L (20-100K) / XL (over 100K) |
| Output volume | S (under 500) / M (500-3K) / L (over 3K) |
| Turn count | low (1-3) / medium (4-10) / high (10+) |

**Not** in the contract: cache hit ratio. Runtime telemetry, not a
design-time fact. Observed at runtime and feeds R5 COST PRUNE
evidence, never enters the step-6 contract.

## 2. Workflow-level quantitative range (PREDICTION)

For ONE representative run, range estimates sourced from the
per-harness adapter's pricing footnote (date-stamped):

- Expected input tokens (low-high)
- Expected output tokens (low-high)
- Expected total turns (low-high)
- Expected dollar / credit / premium-request range (low-high)

A range, not a point. Operators want the worst case, not the average.

## 3. Workload scenarios

At minimum three anchor scenarios, each projected to its size:

- **S** = trivial / single-file change
- **M** = feature in a known module
- **L** = repo-wide change (refactor across N files; full audit)

The L scenario is the cap-check input.

## 4. Cited cost patterns

The B12/B13/B14/B15/B16/A12/R5 patterns the design applies, each
with the cost-shape matrix row that motivated it. See
[the patterns page](/genesis/reference/token-economics/patterns/).

## 5. Declared stance

The stance read at step 1, recorded verbatim. Governance artifact.

## 6. Cap check

If a cap was declared, verify each scenario fits under it. If the
L scenario exceeds the cap, halt and surface the three options.

## Why bands AND ranges

Bands age slowly; pricing ages fast.

- **Bands** are the CONTRACT. Step 8 validates them. A reviewer
  reading the packet a year from now still gets the answer ("this
  module was supposed to be reviewer-class with M prefix").
- **Ranges** are the PREDICTION. Operators read them. Sourced from
  the per-harness adapter's pricing footnote that re-verifies past
  90 days.

If pricing churns and the dollar range goes wrong by 30%, the bands
still hold. If the bands go wrong, the design is wrong -- but pricing
churn alone never invalidates the design.

## Template

```markdown
## Cost projection

### 1. Per-module bands

| Module | Role class | Prefix | Output | Turns |
|---|---|---|---|---|
| ... | ... | ... | ... | ... |

### 2. Per-run quantitative range

| Metric | Low | High |
|---|---|---|
| Input tokens / run | ... | ... |
| Output tokens / run | ... | ... |
| Turns / run | ... | ... |
| **$ / run** | ... | ... |

### 3. Workload scenarios

| Scenario | Description | $ / run |
|---|---|---|
| S | ... | ... |
| M | ... | ... |
| L | ... | ... |

### 4. Cited cost patterns

| Pattern | Why | Matrix row |
|---|---|---|
| ... | ... | ... |

### 5. Declared stance: `<frugal|balanced|quality|unbounded>`

### 6. Cap check: PASS / HALT (cap = ..., L scenario = ...)
```

## Pitfalls

- **Spurious precision.** A 50%-wide range with two-decimal cents
  is a trust-killer when production runs at 7x. Round dollar figures
  to honest precision and stamp the verification date.
- **Stale pricing.** The adapter's footnote is dated. If the stamp
  is over 90 days old, re-verify before trusting the dollar column.
  Bands survive; numbers don't.
- **Single point estimate.** Always low-high. Forecasting a single
  number invites cap-blowout the first time the L scenario fires.
