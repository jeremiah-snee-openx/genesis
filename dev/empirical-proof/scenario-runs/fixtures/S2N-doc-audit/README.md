# S2N — doc-audit + reground (realistic agentic workload)

## Workload

A 11-file docs corpus (~3000 lines, ~30K tokens) for a CLI tool
(`awd`). The operator wants to:

1. **Audit** each page for drift against the current CLI command set
   (e.g. references to removed flags, renamed commands, stale
   examples)
2. **Cross-page consistency check** — same concept named differently
   across pages (e.g. "package" vs "bundle"), conflicting installation
   instructions
3. **Reground proposal** — propose edits per page with a brief
   rationale; editorial panel reviews before applying

This is the doc-sync / doc-audit class of workload — the realistic
agentic counterpart to "rename a symbol" (which is just sed).

## Why this is genuinely agentic

- Requires REVIEWER judgement (is this drift real? does the example
  still work?) — not a classification task
- Requires cross-document reasoning (consistency across pages)
- Each page warrants its own pass but they share corpus-wide context
  (the CLI command set, the terminology)
- Editorial panel review is itself a multi-lens fan-out

## Fixture contents

| Path | Lines | Concept under audit |
|------|-------|---------------------|
| `docs/quickstart.mdx` | 186 | Top-of-funnel install + first run |
| `docs/getting-started/installation.md` | ~50 | CLI install variations |
| `docs/getting-started/authentication.md` | ~80 | Token resolution flow |
| `docs/consumer/install-packages.md` | ~120 | `apm install` command surface |
| `docs/consumer/run-scripts.md` | ~100 | `apm run` command surface |
| `docs/consumer/authentication.md` | ~80 | Consumer-side auth |
| `docs/producer/compile.md` | 180 | `apm compile` command surface |
| `docs/producer/preview-and-validate.md` | 137 | `apm preview` + `apm validate` |
| `docs/reference/manifest-schema.md` | ~200 | apm.yml schema |
| `docs/reference/policy-schema.md` | 298 | Policy file schema |
| `docs/reference/baseline-checks.md` | ~100 | Baseline check definitions |

Total: ~3000 lines, estimated ~30K tokens.

## Three cost-points under test

| Cell | Architecture | Model(s) |
|------|--------------|----------|
| **S2N-zero-opus** | Zero-workflow: single prompt with all docs + CLI command list | Opus 4.7 (single call) |
| **S2N-zero-sonnet** | Zero-workflow: same prompt | Sonnet 4.6 (single call) |
| **S2N-v02** | v0.2 generic editorial panel: 1 lens × 11 pages, all-sonnet, no cost vocabulary | Sonnet 4.6 throughout |
| **S2N-v035** | v0.3.5 class-routed panel: 3 lenses × 11 pages with TRIVIAL/REVIEWER split, B12 + B13 + B14b + B16 applied | Haiku 4.5 + Sonnet 4.6 |
