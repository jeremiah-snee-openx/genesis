# PR #1424 — feat(lsp): add first-class LSP server support to install pipeline

**Mode:** advisory multi-lens review (correctness, security, performance, style, test-coverage)
**Synthesis:** DISSENT-WEIGHTED arbiter
**Scope:** +2363 / -114 across 24 files
**Posting:** NONE — output captured to disk only (token-measurement run)

> **Line-number note.** Reviewer lenses were grounded on the unified diff (`pr.diff`) as a single corpus per the panel design (C6 EXTERNAL CORPUS GROUNDING, no repo clone). Cited line numbers are offsets into that diff, not new-file line numbers. A real GitHub post-stage would map these via `git diff --unified=0 --line-numbers` before calling `add-pr-review-comment`. The file paths and the cited code regions are accurate.

---

## Summary

This PR mirrors the existing MCP integration pattern cleanly: extraction of shared collect/dedupe/stale-cleanup helpers into `integration/_shared.py` is the right shape, and the test surface (≈1,080 new test lines across 4 files) covers the unit boundaries of `LSPDependency`, plugin parsing, and `LSPIntegrator` static methods well.

Three cross-lens signals stand out and the panel converges on them:

1. **Falsy-value handling in `LSPDependency.from_dict`** — both **correctness** and **style** flagged the `d.get('camelCase') or d.get('snake_case')` pattern. With numeric and structured fields (timeouts, `max_restarts`, `initializationOptions`), `0` and `{}` are valid but get bypassed. The fix is the explicit-membership check the model already uses for booleans a few lines down; the inconsistency itself is the smell.
2. **Untrusted-input validation gap at the `.lsp.json` / `plugin.json` boundary** — **security** flagged missing type checks on `args`, `env`, `extensionToLanguage` and a TOCTOU window on `.lsp.json` writes; **test-coverage** independently flagged that the "skip invalid server" warning path is asserted only as "returns empty list" without `caplog` verification. Together these point at one underspecified contract: what does the LSP model promise about strings-vs-anything from a plugin file.
3. **Redundant I/O in the install path** — **performance** flagged three places where parsed state is re-read or re-written without a change check (lockfile re-parse in `_shared.resolve_locked_apm_yml_paths`, full JSON dump on every `install` call, parse-modify-write per stale entry). None of these are hot in single-package installs, but in CI-style mass installs the constant factor compounds.

**Dissent / minority signal preserved:**
- **Correctness HIGH** on `_substitute_plugin_root` (plugin_parser.py near diff line 666) — function is called but no definition appears in the diff. May exist pre-existing in the file; worth a one-line confirmation in the PR description either way.
- **Test-coverage HIGH** that `run_lsp_integration` orchestration uses a mocked `LSPIntegrator` rather than an end-to-end wiring test from `apm.yml` through to file writes. Only one lens raised this; it is preserved in the inline list rather than dropped.

**Style nits rolled up** (per soft-cap rule): generic `-> list:` annotations, missing `logger: CommandLogger` type hint, occasional `builtins.set()`/`builtins.dict()` usage where bare constructors suffice. These do not warrant individual inline comments.

**No verdict, no merge signal.** All comments below are observations.

---

## Inline comments

### Correctness × Style (consensus — falsy-value handling)

- **`src/apm_cli/models/dependency/lsp.py`** (diff lines ~1598–1610) — **medium**
  The `d.get('camelCase') or d.get('snake_case')` pattern is used for `extensionToLanguage`, `initializationOptions`, `timeout`, `shutdown_timeout`, and `max_restarts`. For these fields `0` and `{}` are valid values but get treated as absent and silently overridden by the snake_case fallback. The same `from_dict` already uses `... if 'restartOnCrash' in d else d.get('restart_on_crash')` for booleans a few lines down — applying that pattern uniformly removes the inconsistency. Flagged independently by both the correctness and style lenses.

### Correctness (unique)

- **`src/apm_cli/deps/plugin_parser.py`** (diff line ~666) — **high (verify)**
  `_substitute_plugin_root` is referenced in the new code but no definition appears in this diff. If it exists upstream of the diff window this is fine; if not, the LSP-extraction path NameErrors at runtime. A quick `grep -n _substitute_plugin_root src/apm_cli/deps/plugin_parser.py` in the PR description would close this out.

- **`src/apm_cli/install/lsp/integration.py`** (diff line ~878) — **low**
  `verbose_detail(...)` for the transitive-LSP count only fires when `transitive_lsp` is non-empty. The "0 transitive LSP deps" case stays silent, which is asymmetric with how the MCP path reports. Minor observability gap.

### Security

- **`src/apm_cli/models/dependency/lsp.py`** (diff line ~1563, `args`) — **medium**
  `args: list[str] | None` is type-declared but not value-validated on `from_dict`. A plugin manifest can put non-strings in there; if the field later feeds a subprocess `argv`, `str()`-coercion will produce surprising launches (e.g. `"{'cmd': 'rm'}"`). Validate element types at parse time.

- **`src/apm_cli/models/dependency/lsp.py`** (diff line ~1566, `env`) — **medium**
  Same shape for `env: dict[str, str] | None` — declared, not validated. Untrusted plugin input can put numerics or nested objects in env values; subprocess `env=` requires str→str.

- **`src/apm_cli/models/dependency/lsp.py`** (diff line ~1730, `extensionToLanguage`) — **medium**
  Validated as a dict but the value type is not enforced. Non-string language identifiers will flow through to Claude Code's LSP routing.

- **`src/apm_cli/integration/lsp_integrator.py`** (diff line ~1364, `.lsp.json` write) — **medium**
  Read-modify-write of `.lsp.json` is non-atomic. A symlink swap or concurrent installer would race; using `os.replace` on a same-directory temp file gives an atomic-rename guarantee on POSIX/NTFS without needing a lockfile.

- **`src/apm_cli/deps/plugin_parser.py`** (diff line ~660, symlink check) — **low**
  `candidate.is_symlink()` is performed during auto-discovery; the `_read_lsp_file` path also uses `relative_to()` for containment. Both look correct; flagging only so the ordering invariant ("symlink check precedes any read") is preserved in future refactors.

- **`src/apm_cli/models/dependency/lsp.py`** (diff line ~1575, `workspace_folder`) — **low**
  Plain string, no `path_security` pass. If consumers ever treat it as a filesystem path under the project root, `../` traversal becomes reachable. Cheap to add a normalization helper now.

### Performance

- **`src/apm_cli/integration/_shared.py`** (diff line ~1015) — **medium-high**
  `resolve_locked_apm_yml_paths` calls `LockFile.read(lock_path)` unconditionally. `run_lsp_integration` (and the MCP twin) already parsed the lockfile once; threading the parsed `existing_lock` through avoids a second YAML deserialize on every install.

- **`src/apm_cli/integration/lsp_integrator.py`** (diff line ~1189, `remove_stale`) — **medium-high**
  Stale cleanup reads, parses, mutates, dumps, and writes `.lsp.json` per entry; the inner re-iteration over the removed set just to log is O(n) extra work. Batch the deletions and do one write at the end.

- **`src/apm_cli/integration/lsp_integrator.py`** (diff line ~1364, `install`) — **medium**
  `install` always writes the full JSON back, even when the on-disk config already matches. A shallow equality check before write is one comparison and removes a filesystem write per no-op install — meaningful in test loops and CI.

- **`src/apm_cli/integration/lsp_integrator.py`** (diff line ~1099, `collect_transitive`) — **medium**
  `APMPackage.from_apm_yml(...)` is called per transitive `apm.yml` with no caching. For repos with shared transitive packages the same YAML is parsed multiple times.

- **`src/apm_cli/integration/lsp_integrator.py`** (diff lines ~1135 / ~1146) — **low**
  `get_server_names` and `get_server_configs` make two passes; the caller in `run_lsp_integration` (~diff 892–893) consumes both, so a single pass returning a tuple is a cheap consolidation.

### Style (only the items not rolled into the summary)

- **`src/apm_cli/deps/plugin_parser.py`** (diff line ~756) — **low-medium**
  Bare `except Exception` around `LSPDependency.from_dict(...)`. Narrowing to `ValueError` (or whatever `from_dict` actually raises after the validation work above) keeps unrelated bugs from being silently swallowed and keeps the warning-log signal honest.

### Test coverage

- **`tests/unit/install/test_lsp_integration.py`** (diff line ~2266) — **high**
  `run_lsp_integration` is exercised only through a mocked `LSPIntegrator`. There is no end-to-end test that starts from an `apm.yml`, runs `APMPackage.get_lsp_dependencies()`, and asserts the resulting `.lsp.json` + lockfile state. This is the gap most likely to let an install-pipeline regression slip through.

- **`tests/unit/deps/test_lsp_dependency.py`** (diff line ~1733) — **medium**
  Serialization round-trip is covered on the dataclass; the YAML round-trip through `LockFile.save()` / `LockFile.read()` for `lsp_servers` and `lsp_configs` is not. Closes the loop on the new lockfile fields added in `deps/lockfile.py`.

- **`tests/unit/deps/test_plugin_parser_lsp.py`** (diff line ~2053) — **medium**
  Missing edge-case rows: `lspServers: null`, `lspServers: []`, and `.lsp.json` being a directory rather than a file. The `if lsp_value is not None` branch and the `is_file()` guard deserve direct tests.

- **`tests/unit/integration/test_lsp_integrator.py`** (diff line ~2671, `remove_stale`) — **medium**
  Happy paths covered; the corrupted-`.lsp.json` (invalid JSON or non-dict root) branch is silent in the source and untested. A test that confirms the graceful-skip behavior pins the contract.

- **`tests/unit/deps/test_plugin_parser_lsp.py`** (diff line ~2140) — **low**
  `_lsp_servers_to_apm_deps` test asserts the empty-list return for invalid input but does not assert the warning is logged per skipped server. A `caplog` assertion would protect the observability contract that operators rely on when a plugin ships a bad entry.

- **`tests/unit/integration/test_lsp_integrator.py`** (diff line ~2482, dedupe) — **low**
  First-occurrence-wins is tested on hand-built `LSPDependency` objects; an end-to-end variant where dedupe is reached via `collect_transitive` (with two mock packages declaring the same server name with different configs) exercises the integration path the unit test currently abstracts away.

---

_End of advisory review. No verdict, label, approval state, or merge signal emitted._
