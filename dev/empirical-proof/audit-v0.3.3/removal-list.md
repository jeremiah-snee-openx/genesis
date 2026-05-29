# Genesis Corpus Audit -- Surgical Removal List

Audit run: 2026-05-29. Auditor: genesis-audits-genesis (claude-opus-4.7,
single pass). Scope: cost-aware additions in PR #12 (v0.1 -> v0.3.3),
applied to the full 8836-line corpus (re-counted: 8881 lines).

Audit discipline applied per the genesis skill itself:

- `SKILL.md` step 5 (PROSE: Progressive Disclosure, Reduced Scope) +
  step 8 (size budget, coherent unit).
- `genesis-architect.agent.md` "classic principles" -- SoC, single
  source of truth, DRY-by-link-not-by-copy.
- `assets/design-patterns.md` B14 PROMPT THRIFT (compression that
  preserves semantic payload), R1 SPLIT trigger BODY OVER BUDGET,
  the THRIFT-IN-PLACE-OF-DESIGN anti-pattern (some recommendations
  below are SPLIT/MOVE, not thrift -- noted per item).
- `assets/refactor-patterns.md` R3 EXTRACT (canonical-home rule for
  duplicated guidance) + R4 INLINE (thin-proxy collapse).

---

## Section 1 -- HEADLINE

- **Baseline corpus:** 8881 lines across 35 files.
- **Proposed removals (NET):** **-720 to -930 lines** (~8-10% of corpus).
- **Files affected:** 7 (no new files; no deletions of whole files;
  one example reduced to a thin pointer is RECOMMENDED but flagged
  HIGH-risk and listed separately).
- **No file moves to references/.** Every removal preserves the
  remaining canonical home for the deleted guidance.

Breakdown by file:

| File                                                            | Current | Proposed cuts | After  |
|------------------------------------------------------------------|---------|---------------|--------|
| `assets/design-patterns.md` (§B12)                               | 1199    | ~70           | ~1130  |
| `assets/architectural-patterns.md` (§A12)                        | 1103    | ~25           | ~1078  |
| `assets/token-economics.md`                                      | 188     | ~25           | ~163   |
| `assets/runtime-affordances/model-catalog.md`                    | 202     | ~30           | ~172   |
| `assets/runtime-affordances/per-harness/copilot.md` (cost block) | 312     | ~95           | ~217   |
| `references/cost-economics-process.md`                           | 305     | ~150          | ~155   |
| `examples/06-cost-aware-panel.md`                                | 247     | ~55 (or ~210 if collapsed to pointer) | ~190 / ~37 |
| **TOTAL**                                                        | 8881    | **~720-930**  | ~8160-7950 |

---

## Section 2 -- TOP 10 REMOVALS (by line count)

### 1. `references/cost-economics-process.md` lines 112-196 -- "Step 3.2 -- cost check in full" sub-sections (~85 lines)

**Removal:** entire "Role class / Prefix shape / Output volume / Tool surface / Workflow shape / Apply stance / Tradeoffs / Output of step 3.2" sub-block.

**Rationale:** This block is a near-verbatim re-statement of
`SKILL.md` step 3.2 (lines 190-203) interleaved with cross-references
to `token-economics.md` and `model-catalog.md`. Each sub-section
names a concept already canonically defined in those files
(invalidator audit -> `token-economics.md` §5; role-class picking ->
`model-catalog.md` §5 role classes; output bands -> `token-economics.md`
"Cost-shape vocabulary"; tool surface -> `design-patterns.md` §B15).
Replace the entire block with the table template at lines 192-196
(one table; preserved). 85 lines collapse to ~12.

**Genesis citation:** SKILL.md step 5 PROSE "Reduced Scope" + R3
EXTRACT canonical-home rule (each concept lives in ONE place; others
link).

**Risk:** **MEDIUM.** All signal preserved in the linked canonical
files; readers who land on this section follow the existing links.

---

### 2. `assets/runtime-affordances/per-harness/copilot.md` lines 234-307 -- "Cost-pattern bindings" sub-section (~74 lines)

**Removal:** The B12/B13/B15/B16 prose blocks. Reduce to a single
**binding-site table** + 3-line note:

```
| Pattern | Copilot binding site                       |
|---------|---------------------------------------------|
| B12     | .agent.md frontmatter `model:` (not SKILL) |
| B13     | opaque to operator; avoid mid-session edits|
| B15     | .agent.md frontmatter `tools:` (not SKILL) |
| B16     | encoded via SKU choice on `model:`         |
```

**Rationale:** Lines 246-279 re-state the SELECTION RULE already in
`design-patterns.md` §B12 (lines 840-909). Lines 281-307 re-state
B13/B15/B16 anti-patterns already in `design-patterns.md`. The
*Copilot-specific* signal is: which frontmatter field carries the
binding. That fits a 6-row table. Everything else is duplication.
SKILL-LEVEL ROUTING ATTEMPT anti-pattern (lines 274-279) is the
one harness-specific anti-pattern -- keep it as a 2-line footnote
under the table.

**Genesis citation:** R3 EXTRACT (B12 SELECTION RULE belongs in
ONE canonical home, `design-patterns.md`; per-harness adapters
provide SITE, not RULE). `composition-substrate.md` separation of
substrate vocabulary from per-harness adapter.

**Risk:** **MEDIUM.** SELECTION RULE intact upstream; binding site
preserved as table; failure mode (SKILL-LEVEL ROUTING ATTEMPT) kept.

---

### 3. `examples/06-cost-aware-panel.md` lines 136-189 -- "Cost projection" + "PROVENANCE WARNING" + arithmetic (~54 lines)

**Removal:** The dollar-figure table (lines 142-146), the arithmetic
paragraph (166-170), the blended-cost paragraph (172-176), and the
range-vs-contract paragraph (183-188).

**Rationale:** The PROVENANCE WARNING itself (lines 148-164) is an
admission that the worked numbers are derived from a *different
harness* (direct Anthropic billing) than the one the empirical
measurement in PR #12 used (Copilot CLI). That contradiction means
the dollar figures actively mis-teach when read on the canonical
harness for this corpus. Keep the qualitative claim ("reviewer
class on bulk lenses, planner only on disagreement") and the
A12/B12/B13/S4 pattern citations (lines 117-135); drop the dollar
math. Cost projection mechanics belong in `references/cost-economics-process.md`
§"Step 6 -- cost projection in full", not duplicated inline in
each example.

**Genesis citation:** `genesis-architect.agent.md` "facts that must
be true" -- cost numbers that contradict the canonical-harness
measurement are facts-that-are-NOT-true; the existing PROVENANCE
WARNING is a smell that the content should not be in the example
at all.

**Risk:** **LOW.** The pedagogical shape (gradient + router +
disagreement detector) is intact; only the misleading arithmetic
is removed.

---

### 4. `references/cost-economics-process.md` lines 14-82 -- per-stance prose expansions (~50 lines net)

**Removal:** Compress each of the four stances (`frugal`,
`balanced`, `quality`, `unbounded`) from its current 8-15-line
prose block to a 3-4 line bullet list:

```
### frugal
Posture: minimize spend; accept ~15-20% quality risk on
non-blast-radius decisions.
Pattern mandates: B12, B15, B16, A12 when applicable; cheapest
role class meeting capability; forbid mid-session model switch.
```

**Rationale:** Each stance block currently restates the same
pattern names with minor variation in posture wording. The
pattern names ARE the contract; the posture sentence is the
operator-readable knob. Two sentences each is sufficient.

**Genesis citation:** B14 PROMPT THRIFT (compress prose
enumerations to tables / rule lists where structure permits).
`design-patterns.md` selection heuristic style (lines 1148-1183)
is the model.

**Risk:** **LOW.** Pattern mandates preserved verbatim.

---

### 5. `assets/runtime-affordances/per-harness/copilot.md` lines 189-232 -- "Default role class per primitive type" prose surrounding the table (~32 lines of prose around a kept ~12-line table)

**Removal:** Trim the "CRITICAL CONSEQUENCE for fan-out designs"
prose (lines 213-232, ~20 lines) to ONE three-line note: "A 5-lens
panel implemented as `task(agent_type='explore')` runs at TRIVIAL
class by default; the same panel as `.agent.md` runs at session
default. The B12 decision on Copilot CLI is primitive-type choice
AND `model:` binding." Trim the introduction (lines 189-201) to
"The default role class an element runs at depends on the
PRIMITIVE TYPE carrying the work, not on the session model.
Architect MUST consult this table at B12 selection."

**Rationale:** The narrative re-explains B12 SELECTION RULE in
Copilot terms; the SELECTION RULE already covers "harness default
is not always the session model" (design-patterns.md line 847-851).
The TABLE is the load-bearing artifact; prose around it is
explanation already given upstream.

**Genesis citation:** SKILL.md step 5 PROSE "Reduced Scope";
B14 PROMPT THRIFT "replace prose enumerations with tables where
structure permits" (the table IS the kept signal).

**Risk:** **MEDIUM.** Some readers benefit from the worked
explanation; collapsing to a table-plus-pointer trusts the
upstream SELECTION RULE to carry the reasoning.

---

### 6. `assets/design-patterns.md` lines 896-909 -- B12 "CONSEQUENCE" block (~14 lines)

**Removal:** Entire CONSEQUENCE paragraph ("in a well-designed B12
application, MOST agentic elements carry an explicit `model:`...
Healthy shape: most elements bound DOWN from session default...").

**Rationale:** This paragraph is editorial commentary on the
SELECTION RULE it follows. The rule already names BIND DOWN
(line 882-886) and the "DEFAULT == REQUIRED" case (line 864-881)
with the same rationale. The CONSEQUENCE block restates the rule
in different prose without adding a new decision dimension. The
pathological shapes (a) and (b) it names ARE the BIND-UP-WITHOUT-
JUSTIFICATION and ZERO-EXPLICIT anti-patterns already enumerated
below (lines 911-968). Replace with single sentence: "See
anti-patterns below for shape-detection."

**Genesis citation:** R4 INLINE (thin-proxy collapse: this block
proxies content present in the rule + anti-patterns). B14 PROMPT
THRIFT "cut polite scaffolding with no semantic content."

**Risk:** **LOW.** Pure restatement; no information loss.

---

### 7. `assets/design-patterns.md` lines 957-968 -- CEREMONIAL BINDING anti-pattern (~12 lines)

**Removal:** Consolidate CEREMONIAL BINDING (narrower) into
BIND-UP-WITHOUT-JUSTIFICATION as a one-paragraph "variant" note
rather than a separate anti-pattern. Cut from ~12 lines to ~4.

**Rationale:** CEREMONIAL BINDING is explicitly defined as
"DOCUMENTS intent THOUGH it matches the harness default IS NOT
this anti-pattern; that is PREDICTABILITY DISCIPLINE." Then it
defines the anti-pattern as "copy-pasting a model binding across
many primitives." That second definition is the BULK-IDENTICAL-
BINDING smell, which is one bullet under BIND-UP-WITHOUT-
JUSTIFICATION, not a separate pattern. Splitting it as a
top-level anti-pattern with most of the prose explaining what
it ISN'T inflates corpus volume relative to its discriminatory
value.

**Genesis citation:** PROSE "Explicit Hierarchy" -- two anti-
patterns with the same cure (cite the role-class) should be one
anti-pattern with two example shapes.

**Risk:** **LOW.** The bulk-identical-binding smell is preserved
as a variant; the disambiguation from PREDICTABILITY DISCIPLINE
remains in the SELECTION RULE itself.

---

### 8. `assets/runtime-affordances/model-catalog.md` lines 137-176 -- "Routing axes" prose + over-detailed BINDING SITE warning (~40 lines, trim to ~15)

**Removal:** The "Routing axes" section (137-156) re-states what
B12 SELECTION RULE already covers (quality ceiling / output volume
/ repeat count = the same axes). The BINDING SITE warning (168-176)
restates the WRONG-PRIMITIVE BINDING anti-pattern from
`design-patterns.md`. Trim Routing axes to a 3-line bullet
("Architect picks role class per quality ceiling, output volume,
repeat count; cheapest class meeting capability profile, promoted
only on STAKES; see B12 SELECTION RULE"); trim BINDING SITE to
"Adapters MUST name the per-element binding site; absence breaks
B12 -- see `design-patterns.md` WRONG-PRIMITIVE BINDING."

**Rationale:** Two upstream sources of truth (SELECTION RULE +
anti-pattern); this file's job is to define role classes, not to
re-derive routing rules. The "What this file does NOT do" block
(159-168) is itself a smell of scope overrun -- if the file is
correctly scoped, the negation list is unnecessary.

**Genesis citation:** Composition substrate "vocabulary, not
how-to" register (the file's own framing); B14 PROMPT THRIFT
"cut polite scaffolding."

**Risk:** **LOW.** Role-class definitions (the file's
load-bearing content) untouched.

---

### 9. `assets/token-economics.md` lines 178-189 -- "What this file does NOT do" (~12 lines)

**Removal:** Entire negation block.

**Rationale:** The file's own framing (lines 1-7) declares the
register correctly ("substrate vocabulary, not how-to"). The
negation block is defensive scaffolding that does not add
positive guidance. Same recommendation applies to
`model-catalog.md` lines 159-168 (overlapping with #8 above) and
`cost-economics-process.md` "When this file is NOT loaded" lines
297-305 (independent removal).

**Genesis citation:** B14 PROMPT THRIFT "cut polite scaffolding";
PROSE "Reduced Scope" honored by file scope, not by
self-disclaimer.

**Risk:** **LOW.** Pure scaffolding removal.

---

### 10. `assets/architectural-patterns.md` lines 947-954 -- A12 HEAVY ADJUDICATOR PR #12 Cell F war-story (~8 lines)

**Removal:** The "Measured cost-without-benefit: PR #12 Cell F
(v0.3.2) ran a 15-turn Opus synth-heavy ($3.95) to adjudicate one
TOCTOU severity disagreement and downgrade three findings..."
paragraph.

**Rationale:** The HEAVY ADJUDICATOR anti-pattern's cure paragraph
(lines 951-954) already names the rule: "leave the synthesizer at
reviewer class; promote to planner only when the S4 gate detects
a HIGH-stakes pattern." The PR #12 citation is a war-story that
duplicates the citation pattern over-used across §B12
(`design-patterns.md` cites PR #12 four times: lines 930, 943,
948, 949). The corpus cites the same empirical episode in five
places; one canonical citation in the SELECTION RULE
WRONG-PRIMITIVE BINDING anti-pattern is sufficient. Drop the four
secondary citations.

**Genesis citation:** R3 EXTRACT canonical-home rule; the
empirical episode has ONE canonical home; subsequent references
should LINK rather than restate.

**Risk:** **MEDIUM.** Some readers benefit from concrete dollar
figures; removing the citation leaves the abstract rule. Mitigated
because example 06 retains the empirical context for readers who
want the war story.

---

## Section 3 -- CONSOLIDATION CANDIDATES

### Triple: B12 SELECTION RULE (CANONICAL HOME: `assets/design-patterns.md` §B12 lines 840-895)

- `assets/design-patterns.md` §B12 SELECTION RULE -- **KEEP as canonical.**
- `assets/runtime-affordances/per-harness/copilot.md` lines 246-269 -- **CUT to BINDING SITE table only** (removal #2).
- `references/cost-economics-process.md` "Role class" sub-section lines 118-128 -- **CUT** (removal #1); replace with link.

Total triple savings: ~50-70 lines.

### Pair: Cost stance mechanics (CANONICAL HOME: `references/cost-economics-process.md` lines 14-108)

- `references/cost-economics-process.md` -- **KEEP as canonical** (cap mechanics, stance declaration mechanics, projection template are the file's load-bearing content).
- `SKILL.md` lines 122-127 -- **KEEP one-paragraph summary** that names stance values + cap + the reference file. Already correctly shaped.
- `token-economics.md` lines 8-14 (load-when triggers naming stance) -- **KEEP**; correct progressive disclosure.

No removal in the pair; flag is that the canonical file itself bloats
(see removals #1, #4, #9 against it).

### Pair: Per-primitive-type default role class (CANONICAL HOME: `assets/runtime-affordances/per-harness/copilot.md` lines 202-211, the table only)

- `copilot.md` table -- **KEEP.**
- `design-patterns.md` §B12 SELECTION RULE rule 1 -- **KEEP** (names the abstract requirement to look up the table).
- `model-catalog.md` lines 168-176 (BINDING SITE warning) -- **CUT** (removal #8); the pointer to the adapter table is enough.

### Pair: Examples 04 and 06 (NO REMOVAL recommended; flagged for monitoring)

Examples 04 (advisory PR review panel) and 06 (cost-aware
re-architecture of example 02's panel) have distinct teaching
goals: 04 demonstrates A1 + A6 + DISSENT-WEIGHTED arbiter; 06
demonstrates A12 GRADIENT OVERLAY on a panel. They share the
"panel" shape but teach orthogonal lessons. **Do NOT consolidate.**
However, example 06's value collapses if its dollar figures are
retained (see removal #3); the recommended trim makes 06 a clean
A12-overlay reference rather than a contradiction.

---

## Section 4 -- KEEP-AS-IS (load-bearing despite bulk)

The following look bulky but are doing real work. Do NOT touch.

1. **`SKILL.md` step process diagram (lines 53-92)** -- 40 lines of
   ASCII flow. Bulky but irreplaceable: every reader of the skill
   uses this as the map. The lines 60-69 cost-check additions are
   minimal (~5 lines for steps 3.2 + 6 + 8 cost callouts).

2. **`design-patterns.md` §B12 SELECTION RULE bullet enumeration
   (lines 840-895)** -- the canonical rule. Bulky because it
   enumerates four (DEFAULT vs REQUIRED) cases AND the operator
   bias axis. Each case is load-bearing for a different design
   decision. Removal #6 (CONSEQUENCE block, 14 lines below the
   rule) is the only safe cut within §B12.

3. **`token-economics.md` "The seven concepts" (lines 44-135)** --
   the substrate vocabulary that every cost-aware section refers
   to. Reads compact (definition + 1-3 sentences per concept).
   Concept #4 CACHE BREAKPOINT and #5 CACHE INVALIDATOR are
   referenced by B13, B14, B15, B16 anti-patterns; removing any
   of them breaks downstream links.

4. **`architectural-patterns.md` §A12 canonical shape + mermaid
   diagram (lines 862-895)** -- the pattern's load-bearing
   visual. ~35 lines including the SVG. The DISCRIMINATOR vs A2
   (lines 897-902) is also load-bearing because A2 STAFFED PLAN
   and A12 GRADIENT WORKFLOW are easily confused.

5. **`model-catalog.md` "The five role classes" (lines 35-135)** --
   the entire role-class taxonomy. Each role class entry is the
   canonical home for capability profile + cost profile + typical
   context size. Routing axes (lines 137-156) are NOT this; they
   are the removable layer.

6. **`copilot.md` "Default role class per primitive type" table
   (lines 202-211)** -- the only place that records the
   primitive-type-default mapping for Copilot CLI. Without this
   table, B12 SELECTION RULE rule 1 cannot execute on Copilot.

7. **`cost-economics-process.md` "Step 6 -- cost projection in
   full" (lines 200-262)** -- the projection template that the
   handoff packet must follow. The six numbered parts are the
   contract that step 8 validates against. Concrete dollar-range
   guidance lives nowhere else.

---

## Section 5 -- DO-NOT-REMOVE (deliberate redundancy for safety)

These look like duplication but exist on purpose. Off-limits.

1. **`design-patterns.md` §B12 WRONG-PRIMITIVE BINDING anti-pattern
   citing PR #12 Executor B (lines 926-938)** -- this is the
   canonical war story that motivates the entire SELECTION RULE
   rule 1. Removing it makes the rule abstract; the operator
   needs the concrete "this is what failure looks like" to
   recognize the trap.

2. **`example 06` patterns-applied citation block (lines 117-135)
   citing A12 + B12 + B13 + S4 with cost-shape matrix rows** --
   looks like duplication of design-patterns.md, but is the
   worked-example's load-bearing teaching: "this is how cost
   patterns compose on a real shape." Required by SKILL.md
   step 6 cost-projection contract (each pattern cited against a
   matrix row).

3. **`copilot.md` SKILL-LEVEL ROUTING ATTEMPT anti-pattern
   (lines 274-279)** -- duplicates `design-patterns.md` §B12
   WRONG-PRIMITIVE BINDING in shape, but the harness-specific
   form (silently ignored vs other harnesses where it errors)
   is the actionable knowledge. Keep even after removal #2
   trims the surrounding block.

4. **`model-catalog.md` "Examples (durability disclaimer: refresh
   from per-harness adapter)" lines (e.g. line 56, 74, 94, 112,
   134)** -- each role class names example model SKUs WITH a
   "refresh from adapter" disclaimer. Looks redundant with the
   per-harness adapters; is deliberate so the role-class file is
   self-contained for cold-load reading even without the adapter.

5. **`SKILL.md` step 3.2 cost-check 8-line summary (lines 190-203)
   AND the `cost-economics-process.md` reference link** -- the
   summary IS the body-budget-respecting summary; the reference
   file is the load-on-demand detail. Progressive disclosure is
   working as designed. Do not collapse.

6. **`token-economics.md` "How this vocabulary interlocks with
   existing substrate" (lines 158-174)** -- explicit cross-links
   to THREADING, PERSISTENCE, ATTENTION concepts. Looks like
   prose padding; is the load-bearing argument that cost is a
   SEVENTH AXIS of the existing substrate, not a graft. Removing
   it weakens the framing that justifies the cost-aware tier
   existing at all.

---

## Appendix: ranking of removals not in TOP 10

11. `cost-economics-process.md` lines 297-305 "When this file is NOT
    loaded" (~9 lines) -- same scaffolding-removal logic as #9.
12. `copilot.md` SELECTION RULE rule 3 restatement (lines 259-269)
    (~10 lines) -- covered indirectly by removal #2.
13. `architectural-patterns.md` §A12 INVERTED GRADIENT + FLAT
    WORKFLOW + BUDGET-DRIVEN PROMOTION anti-patterns -- KEEP all
    three (each names a distinct failure mode); minor wording trim
    only (~5 lines saved).

---

## Cited section anchors (genesis discipline applied)

- SKILL.md step 5 PROSE "Reduced Scope" -> removals #1, #2, #4, #8, #9.
- SKILL.md step 8 size budget -> headline framing.
- R3 EXTRACT canonical-home rule -> removals #1, #2, #10.
- R4 INLINE thin-proxy collapse -> removal #6.
- B14 PROMPT THRIFT "compression preserving semantic payload" ->
  removals #4, #5, #8, #9.
- B14 THRIFT-IN-PLACE-OF-DESIGN anti-pattern -> the audit
  consciously did NOT recommend R1 SPLIT on any file (no new files);
  removal #2 is consolidation, not split.
- `composition-substrate.md` "vocabulary not how-to" register ->
  removal #8 framing (model-catalog stays vocabulary).
- `genesis-architect.agent.md` "facts that must be true" ->
  removal #3 (contradictory dollar figures are not facts that hold).

## End of recommendations.
