# Predictability probe: `task(agent_type='explore')` on Copilot CLI

**Date:** 2026-05-29. **Harness:** Copilot CLI v1.0.55-7. **Goal:** verify that `task(agent_type='explore')` reliably fires claude-haiku-4.5 across varying task complexity, validating Cell G's `OMIT model:` choice as a *short-term* tactic (and motivating the v0.3.3 reframe toward explicit binding for portability).

## Method

Three explore dispatches with varying complexity, all submitted via the `task` tool from a Copilot CLI Opus 4.7 session. Model fired by each subagent is captured via per-model token attribution in the session's process log.

| Probe | Prompt complexity | Goal |
|---|---|---|
| 1 | Trivial: list files in a directory | Cold-start, minimal context, single tool call |
| 2 | Medium: grep + count matches across N files | Multi-tool, structured output |
| 3 | Complex: read a markdown file and produce a multi-paragraph prose analysis | Long context, generation-heavy |

## Result

| Probe | Duration | Subagent turns | Cost (Haiku) | Model fired |
|---|---:|---:|---:|---|
| 1 | 3s | 2 | <$0.01 | claude-haiku-4.5 |
| 2 | 30s | 5 | $0.05 | claude-haiku-4.5 |
| 3 | 89s | 7 | $0.14 | claude-haiku-4.5 |
| **Total** | — | **14** | **$0.19** | — |

All three probes fired claude-haiku-4.5. No promotion to Sonnet or Opus observed even on the long-context prose-generation probe (#3).

## Conclusions

1. **Harness default IS stable for complexity TODAY.** Copilot CLI does not silently promote `task(agent_type='explore')` to a higher class based on prompt complexity. The TRIVIAL-class binding holds across the tested span.
2. **OMITting `model:` on `task(agent_type='explore')` is a working tactic on Copilot CLI today.** Cell G's $2.85 executor cost is reproducible.
3. **BUT cross-version durability is not tested.** A future Copilot CLI release may change the default. No release-note guarantee exists.
4. **AND cross-harness portability is not tested.** Claude Code, OpenCode, Codex, Cursor defaults are not measured. Some harnesses have no equivalent of `task(agent_type='explore')` at all and would bind everything at session level.

**Implication for v0.3.3 corpus:** explicit binding (`model: claude-haiku-4.5` on each lens) is the durable discipline. Same cost shape on Copilot CLI today; portable to other harnesses; predictable across harness versions. The probe validates the OMIT tactic as *not currently broken* on Copilot CLI, NOT as the recommended pattern.
