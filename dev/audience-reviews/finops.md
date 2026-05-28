# FinOps Review: Genesis Cost-Economics Layer

## VERDICT: DEFENSIBLE bordering on RIGOROUS for design-time; DIRECTIONAL once you cross into runtime/operate.

## STRONG

- Vocabulary (cacheable prefix, variable suffix, cache invalidator, output tax, TTL tradeoff) is at the upper end of FinOps playbooks I see.
- Role-class abstraction over SKU is correct architecture (survives Sonnet 4.6→4.7→Opus churn).
- Boolean-not-gradient framing on cache discipline is exactly right and I quote it in client decks.
- Anthropic pricing in `claude-code.md` §9 checks out (input/output/cache-write/cache-read on Sonnet/Opus/Haiku all verified against my notes).
- Cap-gate mechanism. CFOs love a hard ceiling.

## NAMED CLIENT FAILURE MODES THIS WOULD CATCH

- ✅ Class-uniform graph (12-lens panel all on Opus, $47K→$9K after gradient)
- ✅ Timestamp in system prompt killing cache (Series C devtools, $22K/mo invisible regression)
- ✅ Router-as-planner anti-pattern (example 06 flags it)
- ✅ MCP tool-catalogue churn mid-session

## NAMED FAILURE MODES NOT CAUGHT

- ❌ Tenant-prefix fragmentation in multi-tenant SaaS
- ❌ Tail-spend P99 blowups (no distribution vocabulary; low/high hides it)
- ❌ Monthly drift after deploy (no Operate-phase loop)
- ❌ Stale pricing assumptions auto-aging projections out of truth
- ❌ Arithmetic errors in the worked example itself

## BLOCKERS (CFO-defensibility holes)

1. **Worked example numbers don't add up.** `06-cost-aware-panel.md` line 144: "6 × planner ... 30K input × ~6K output ... ~$0.54." Against Opus L145 ($15 input / $75 output): 30K × $15/M = $0.45, 6K × $75/M = $0.45 = **$0.90, not $0.54**. CFO who spot-checks rejects entire projection on arithmetic grounds. **Most fixable defensibility hole.**
2. **"Range" with no confidence interval.** CFO will ask P50 or worst case. Should require P50 + P95, not low/high.
3. **No monthly cadence multiplier.** $0.18/run × ?? = ?? . Framework stops one math step short of what CFO buys.
4. **Output tax band understates multi-provider variance.** On OpenAI o-series, output:input is 8x. The 3-5x is Anthropic-centric.
5. **No staleness alarm.** 90-day re-verify is SHOULD, not gate.

## SCOPE GAPS

- No tail-spend anomaly detection vocabulary (runtime, not design-time, but should be named).
- No attribution model (which module / tenant / feature flag is costing money).
- No cache-sharing-across-tenants concept (5-10x lever).
- No batch API as a pattern (50% off on Anthropic & OpenAI batch APIs is a design choice).
- No cost regression testing in step 8.

## WHAT WOULD HARDEN IT

- Fix arithmetic in example 06.
- Require P50/P95 instead of low/high.
- Add monthly-cadence multiplier in projection template.
- Require cap-widen events to be logged with rationale.
- Add "cost regression vs prior projection" diff in step 8.

**Net:** Strong Inform-phase tool. Solid Optimize-phase tool. Missing Operate phase entirely. Fix the arithmetic, add P50/P95 + monthly rollup, then it's RIGOROUS.
