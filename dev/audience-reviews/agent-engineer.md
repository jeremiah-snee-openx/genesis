# Senior Agent Engineer Review — `genesis` cost-economics addition

## LIKED

- **Role-class taxonomy** (`assets/runtime-affordances/model-catalog.md` L22–32, L36–136) is the right level of abstraction. "Models age out, role classes don't" is exactly how I want my designs written. `planner / implementer / reviewer / trivial / long-context-retriever` is the smallest workable set.
- **Cache invalidator enumeration** in `assets/token-economics.md` L91–101 and `assets/design-patterns.md` B13 L875–895 names real production gotchas I've personally been bitten by: timestamped persona, mid-session MCP tool-catalog churn, mid-session effort toggle. The framing "cache discipline is a boolean per turn, not a gradient" (`token-economics.md` L105) is a sharp mental model I will quote in design reviews.
- **R5 COST PRUNE step 1** (`refactor-patterns.md` L246–249) — "Observe (do not guess)" with a baseline trace requirement before pattern application. This is the single most adult line in the whole addition.
- **The cost-shape matrix** (`pattern-tradeoffs.md` L285–295) with the "first match wins, don't stack" selection rule (L297–308) prevents the obvious failure mode of architects bolting on B12+B13+B14+B15 reflexively.
- **Worked example 06** structure: starting design → bands table → re-architecture diagram → "what stays the same" → "when this is the wrong call" (L193–203). That last section ("low cadence, high disagreement rate, quality stance, N<4") is what separates a real engineer's playbook from a sales deck.
- `claude-code.md` §9 (L119–169) actually closes the loop: role class → SKU → $/Mtok → cache-aware breakpoint binding → stance binding. Operationally usable.

## FRICTION

- **Substrate sprawl on the cost check.** Five files for one step. At 11pm shipping a hotfix design, I will skip three of them.
- **Two sources of truth for step 3.2.** `SKILL.md` L190–204 and `references/cost-economics-process.md` L112–196 both describe the same procedure with different shapes.
- **Band vocabulary collides with itself.** "S" in prefix and "S" in output mean different absolute numbers.
- **Four stances is one too many.** `quality` and `unbounded` differ only in whether the projection is recorded.

## VALUE

Concrete: would refactor release-notes-from-merged-PRs workflow this week. Applying A12 with reviewer-class workers cuts that workflow's spend by ~75%. B13's invalidator audit would catch a timestamped `## Current date:` header that has been silently killing cache for months.

## BLOCKERS

1. **The step-8 "cost contract gate" is not a gate.** No script, no lint. Either ship `scripts/cost-lint.sh` or rename to "checklist."
2. **Example 06 numbers do not reconcile against the adapter's own price table.** $0.54 should be $0.90 against Opus L145 rates. Fix or remove the dollar column.
3. **Cache-hit-ratio in the projection contract.** Runtime telemetry number, unobservable at design time. Drop from contract, keep as runtime observation feeding R5.
4. **Pricing footnote rot.** 90-day re-verify is unenforced.

## VERDICT

**SHIP WITH FIXES.** Three things must land: (1) reconcile or remove the dollar figures in example 06, (2) demote "cost contract gate" to "cost checklist" or ship the lint, (3) remove cache-hit-ratio from the step-6 contract.
