# Profiling protocol — measured token cost across scenarios

## Hard rules

1. **Real telemetry only.** No size-based estimates in final reports.
   Every cost is computed from `events.usage_*` rows in cloud
   session_store at published Anthropic rates (see COSTING.md).

2. **Architecting cost is NOT counted.** Genesis-skill design
   sessions run on Opus 4.7 and produce handoff packets. They are
   excluded from cell-cost totals. Only the runtime executor
   session counts.

3. **One cell = one Copilot sub-session.** Each runtime cell runs
   in its own clean sub-session. Per-cell totals come from
   aggregating that single `session_id` in the events table.

4. **Anthropic published rates** (in `COSTING.md`):
   - opus 4.7: $15/M in · $75/M out · cache_read $1.50/M · cache_write $18.75/M
   - sonnet 4.6: $3/M in · $15/M out · cache_read $0.30/M · cache_write $3.75/M
   - haiku 4.5: $1/M in · $5/M out · cache_read $0.10/M · cache_write $1.25/M

## Cell types

### Zero-workflow cells (`*-zero-opus`, `*-zero-sonnet`)

- One Copilot sub-session
- ONE user turn — paste the operator's raw request, attach the
  fixture path inline, let the assistant respond once
- No genesis skill, no sub-agent dispatch
- Forces the cheapest single-model baseline

### Architected cells (`*-v02`, `*-v036`)

- One Copilot sub-session driving the runtime workflow
- Reads its handoff packet at session start
- Dispatches sub-agents per the packet (these spawn children
  whose tokens roll up under the parent session_id in events)
- No re-architecting inside

## Per-cell artifacts (each session writes these)

`dev/empirical-proof/scenario-runs/results/<cell_id>/`:
- `SESSION_ID` — single line, the session's UUID
- `output.md` — verdict / transcript / artifact produced
- `notes.md` — sub-agent dispatch log (which models routed where)

`cost-report.json` is written **after** the session ends, by the
orchestrator querying telemetry. Sub-sessions do NOT compute their
own cost.

## Telemetry harvest query

```sql
SELECT usage_model, SUM(usage_input_tokens) AS inp,
       SUM(usage_output_tokens) AS outp,
       SUM(usage_cache_read_tokens) AS cread,
       SUM(usage_cache_write_tokens) AS cwrite,
       COUNT(*) AS calls
FROM events
WHERE session_id = '<cell_session_id>'
  AND usage_input_tokens IS NOT NULL
GROUP BY usage_model;
```

Cost formula per model row:
```
cost = base_in × (inp + 0.1 × cread + 1.25 × cwrite) / 1e6
     + base_out × outp / 1e6
```
Sum across model rows → cell `total_cost_usd`.
