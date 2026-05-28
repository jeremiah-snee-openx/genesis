# CTO Evaluation: genesis Cost-Economics Addition

## STRATEGIC FIT

Yes, and bluntly: this targets the exact failure mode driving my $45K → projected $58K next month. Our spend isn't growing because we're shipping more agents; it's growing because nobody is asking "does this lens *need* planner-class?" before shipping a panel. Example 06 dramatizes precisely that — a 6×planner review panel cut to ~$0.12-0.18/run from ~$0.54 by role-class shifting and a disagreement gate (`examples/06-cost-aware-panel.md`, lines 142-150). A 3-4× per-workflow reduction on review-shaped workloads, which are most of my agent fleet, would meaningfully bend the 30%/month curve.

More important strategically: the addition treats cost as a **design dimension, not a post-hoc optimization**. Step 3.2 is mandatory and mirrors the tradeoff check (`SKILL.md` line 190, line 67 process diagram). That's the right altitude. Today my team optimizes cost reactively after I forward a billing screenshot. This pushes it upstream into the architecture review I already pay for.

## GOVERNANCE & VISIBILITY

Strong, with one caveat.

What I can put in a board deck:
- **Per-workflow cost projection with S/M/L scenarios** and a low-high range (`cost-economics-process.md`, "Step 6", parts 2-3). Range, not point — boards understand worst-case anchors.
- **Declared stance recorded verbatim** per design (part 5). That's a governance artifact: I can say "78% of new agent designs this quarter shipped under `balanced` or `frugal` stance" — that's an OKR.
- **Cap-as-gate** (lines 85-108): the only place the skill refuses to ship. This is the lever I actually want — a hard, auditable "designs over $X/run require CTO sign-off."

Engineering OKRs this enables:
- "100% of new agent designs ship with a cost projection in the handoff packet."
- "Median projected $/run for new workflows ≤ $0.20 (frugal-stance class)."
- "Step 8 cost-contract-gate violations (`SKILL.md` lines 473-478) < 5% of merged designs."

Caveat: the dollar figure is a **prediction**, sourced from a per-harness pricing footnote with a verification date stamp (`cost-economics-process.md`, part 2). It's not actual billed spend. For board-grade ROI claims I need to reconcile projections against actual invoices monthly, which the skill does not do. That's *my* job to wire up — but the projection is the missing input that today doesn't exist.

## ADOPTION FRICTION

Real and non-trivial. Costs:

- **Vocabulary load.** Engineers must internalize five role classes, four stances, ~7 cost patterns (B12-B16, A12, R5), the cost-shape matrix, and the step 3.2 table format. That's a ~1-2 week ramp for the 8-person team before designs flow naturally. I'd budget one sprint of velocity tax.
- **Step 3.2 is mandatory by default** (`SKILL.md` line 202: skip only when stance is `unbounded` AND opt-out). Every non-trivial design now produces a per-module table and a 6-part projection. For a small refactor that's overkill — the doc acknowledges this ("When this file is NOT loaded", lines 287-295), but the escape hatch requires judgment my juniors don't yet have. They will over-apply it.
- **Cap-gate halts designs** (lines 96-108). First time a senior engineer's design gets blocked at the cap mid-Friday-afternoon, I will hear about it.

What slips: roughly 1 sprint of feature velocity during ramp, then ~10-15% design overhead steady-state on new agent work (not on app code — this is scoped to agentic primitives, which is maybe 20% of my engineering surface). Net velocity over a quarter: probably flat-to-positive once the rework loop ("we shipped it, it cost too much, redesign") shrinks.

## RISK

Four new failure modes worth naming:

1. **Stance-knob gaming.** `unbounded` skips the gate entirely (line 203, lines 62-70 of the process doc). An engineer under deadline pressure declares `unbounded`, ships, and the projection becomes a rubber stamp. Mitigation: require CTO/staff approval to declare `unbounded`; treat `unbounded` declarations as an OKR-tracked metric.
2. **Cap-gate as design blocker.** A tight cap + an honestly-projected L scenario over it = halt. The three offered escapes (widen cap / change stance / coarser pattern, lines 99-104) are reasonable, but in practice the path of least resistance is "widen the cap." Caps drift up. Mitigation: cap changes require the same approval as the original cap.
3. **Friction → ad-hoc design.** If step 3.2 feels like tax, engineers route around the skill entirely ("I'll just write the prompt, it's small"). The skill only helps designs that go through it. Mitigation: require the handoff packet (which includes the projection) as a PR artifact for any new agentic primitive.
4. **Projection theater.** A 6-part projection with dollar ranges *looks* rigorous but is bounded by the accuracy of the per-harness pricing footnote and the engineer's qualitative band estimates (S/M/L on `cost-economics-process.md` lines 206-214). Garbage qualitative bands → confident-looking but wrong dollar figures I might quote to a board. Mitigation: the step 8 cost contract gate (`SKILL.md` 473-478) validates emitted code against the projection; I need to add post-hoc reconciliation against real invoices to close the loop. **This is the gap.**

## ROI VERDICT

**Yes, mandate it for new agent workflows, with three conditions.**

The math: if even half my agent surface adopts this and gets the 3× reduction example 06 demonstrates, I knock $8-12K/month off the trajectory by next quarter. The skill costs me roughly one sprint of ramp + ~10-15% design overhead on a 20% slice of engineering. That's a clearly positive trade at our spend curve. More importantly, I get a governance artifact (the cost projection + stance + cap) that I currently fabricate by hand for every board review.

Conditions on the mandate:
1. **Mandatory for new agentic primitives only.** Not retrofitted to every existing prompt. Pick the next quarter's net-new agent work as the wedge.
2. **`unbounded` stance requires staff+ approval**, tracked as a metric. Otherwise the gate is theater.
3. **I personally own the reconciliation loop** the skill does *not* provide: monthly, compare projected $/run against actual billed spend per workflow. Without this, the projections are uncalibrated and my board-deck claims are vibes.

What would change my mind:
- Evidence the qualitative bands (S/M/L) systematically under-predict by >2× on real traces. The projection becomes worse than no projection if it's confidently wrong.
- Two sprints in, if my best engineers tell me step 3.2 is producing make-work tables nobody references downstream at step 8. The cost-contract gate (line 473) is the load-bearing part; if it's skipped in practice, the upstream projection is wasted work.
- A cheaper alternative emerging — e.g., a runtime cost-observer that catches the same regressions post-hoc without the design-time tax. Today none exists at this fidelity, so genesis wins on default.

Mandate it. Revisit at the end of next quarter against actual billed spend, not projected.
