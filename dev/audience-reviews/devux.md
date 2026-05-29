# DevUX Expert Review — genesis cost-economics layer

## VERDICT: FRICTIVE

Not hostile — the underlying model is genuinely good. But the surface area an operator must traverse to GET to that expertise is brutal: ~70 terms of bespoke vocabulary, a 4-value enum with two misleading names, a halt mechanism that fires at the worst possible moment, and a projection artifact whose dollar figures present 50%-wide ranges with two-decimal precision. The letter `L` means three different things.

## TOP UX FRICTIONS

1. **Vocabulary mismatch on turn 1.** Operator says "cheap" — the system needs `frugal`. No "I just want it cheaper" path.
2. **Stance enum has two misleading names.** `frugal` (connotation problem), `quality` (implies balanced is NOT quality — defeats the layer), `unbounded` (useless escape hatch).
3. **Cap halts at step 6 — after sunk cost.** Should rough-in at step 1.
4. **No quantified escape from cap halt.** Three escape options, none of which tell you HOW MUCH to widen.
5. **Spurious precision in projections.** `~$0.12-0.18` with 50% spread looks rigorous but is a trust-killer when production is $1.20.
6. **Letter L overloaded 3 ways.** Workload scenarios, prefix size, output volume all use S/M/L.

## P0 FIXES (low effort, high impact)

- Replace 4-value stance with 2 values: `cheap` and `premium`. Default unspoken.
- Pre-design cost rough-in at step 1 against the intent paragraph alone — move halt from step 6 to step 1.

## P1 FIXES

- Soft-cap with wiggle room (110% / 110-150% / >150% tiers) + partial-fit report.
- Rename: `GRADIENT WORKFLOW` → `tiered workflow`; `PROMPT THRIFT` → `prompt trim`; `EFFORT GOVERNOR` → `reasoning cap`; workload S/M/L → `quick/typical/heavy`.

## P2 FIXES

- Round dollars (`~$0.10-0.20`) + stamp staleness.
- Lead every projection artifact with "BANDS are contract / DOLLARS are prediction" preamble.

## P3

- Stance preview diff at step 1 ("with `cheap` you'd save ~60%").

The defining test: tired operator at 11pm types "make it cheap." Today: 300 lines of reference docs, picks `frugal` by accident, gets a router forced into a workflow with no fan-out, hits cost halt with no guidance. Worth fixing before this meets a real operator.
