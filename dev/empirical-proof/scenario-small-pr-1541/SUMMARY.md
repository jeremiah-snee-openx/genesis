# Scenario: small-PR executor probe — microsoft/apm#1541

Dispatched as part of PR #12 v0.3.4 multi-scenario validation. Executor (Sonnet 4.6) ran the v0.3+ panel against a small CLI fix (+41/-2, 2 files) with explicit haiku-4.5 lens bindings (v0.3.3 reframe applied).

## Headline

| Metric | Value |
|---|---:|
| Executor cost | ~$0.21 |
| Executor turns | 6 |
| Cost / kLoC | $5.12 (vs $1.15 on PR #1424) |
| BLOCKER findings | 0 |
| HIGH+ findings | 5 |
| Total findings | 18 |
| Arbiter fired? | No (trigger not met) |

## Key reflection (PER-LENS DIFFERENTIATION)

The executor reflected on each lens against the v0.3.4 CAPABILITY PROFILE template:

- **correctness, performance, style:** TRIVIAL genuinely correct on this PR.
- **test-coverage:** TRIVIAL mostly correct (had to infer existing fixtures).
- **security:** TRIVIAL INADEQUATE — could not validate a real MEDIUM bypass finding without out-of-diff function body access. REVIEWER-class with bash/grep would have closed it.

Implication: even on PR #1424, the security lens was likely mis-bound to TRIVIAL. The blocker false-positive (`_substitute_plugin_root`) is consistent with TRIVIAL-class inadequacy on cross-file reasoning. v0.3.4 PER-LENS discipline correctly predicts security should bind to REVIEWER.

## Recommendation

- For small PRs (<50 LoC), fixed Sonnet-executor overhead dominates (~93% of total cost). A 2-lens skinny pipeline would suffice for docs-only or test-only PRs.
- Security lens carve-out: TRIVIAL when all referenced functions are in-diff; REVIEWER when out-of-diff internals are required to close findings.

See REPORT §"Multi-scenario probe: small-PR executor" for full integration into the empirical proof.
