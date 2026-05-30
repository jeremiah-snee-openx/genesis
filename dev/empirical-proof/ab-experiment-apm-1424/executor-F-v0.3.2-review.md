# PR Review: microsoft/apm#1424 — feat(lsp): add first-class LSP server support

## Summary
This PR adds LSP server support to the APM install pipeline, mirroring the existing MCP integration (parser extraction from `lspServers` / `.lsp.json`, transitive collection, install/remove_stale, lockfile updates, `${CLAUDE_PLUGIN_ROOT}` substitution). The design is consistent with the established MCP pattern and the core happy path appears functional. The most consequential issues are supply-chain trust for transitive LSP deps (which mirror MCP's trust model but expand the attack surface) and a regression in code style (re-introducing `builtins.set/dict` patterns the MCP refactor removed). After adjudication, **no true BLOCKERs remain** — the alleged `NameError` is a false positive.

## Critical Findings (HIGH+ severity, exploitable or broken-happy-path)

| ID | File | Severity | Issue | Recommendation |
|----|------|----------|-------|----------------|
| SECURITY-002 | `src/apm_cli/integration/lsp_integrator.py` (collect_transitive) | HIGH | Transitive LSP deps from any installed package can inject arbitrary server configs (command/args/env) that Claude Code will later execute. No provenance, trust prompt, or warning surface. Supply-chain RCE risk via deeply-nested deps. | At minimum, emit a clear warning listing every LSP server pulled in transitively (name + plugin + command), and document the trust model. Consider an opt-in flag (`--trust-transitive-lsp`) for parity with how other ecosystems gate post-install scripts. |
| PERFORMANCE-001 | `src/apm_cli/install/lsp/integration.py` (run_lsp_integration L886–902) | HIGH | `install()` and `remove_stale()` each read+write the same `.lsp.json` / `~/.claude.json` back-to-back (2 reads + 2 writes). Doubles I/O on every install and widens the TOCTOU window (see SECURITY-001). | Pass `stale_lsp` into `install()` (or add a unified `apply()` method) so one read/modify/write covers both. Also reduces race surface. |
| STYLE-001 | `src/apm_cli/integration/lsp_integrator.py` | HIGH | New code re-introduces `builtins.set()` / `builtins.dict` patterns that the prior MCP refactor explicitly removed. Direct regression of the project’s own cleanup work. | Replace `builtins.set/dict` with plain `set`/`dict`; remove `import builtins` (STYLE-009). Add a lint rule (`ruff` UP rules) to prevent recurrence. |

No findings meet the BLOCKER bar after adjudication — see Adjudication Notes for the downgrade of CORRECTNESS-001 / TEST-001.

## All Findings by Lens

### Correctness
| ID | Sev (final) | File | Summary |
|----|------|------|---------|
| CORRECTNESS-001 | ~~BLOCKER~~ → **FALSE POSITIVE** | `deps/plugin_parser.py:666` | Alleged undefined `_substitute_plugin_root`. Function exists at L304 (added with MCP work) with matching signature. No NameError at runtime. |
| CORRECTNESS-002 | MEDIUM | `install/lsp/integration.py:873–913` | `run_lsp_integration` receives `logger` but does not forward it to `LSPIntegrator.{collect_transitive, install, remove_stale}`; user-facing `logger.progress()` calls inside `remove_stale` are therefore silent. |
| CORRECTNESS-003 | LOW (downgraded from MEDIUM) | `commands/install.py:540` | `run_lsp_integration(should_install=should_install_mcp)` reuses the MCP gate. Confirmed intentional ("same gate as MCP" — comment L853, tests at L2280+ assert this). Naming is mildly misleading; consider renaming local to `should_install_extensions` or adding an alias. |

### Security
| ID | Sev (final) | File | Summary |
|----|------|------|---------|
| SECURITY-001 | MEDIUM | `integration/lsp_integrator.py` install/remove_stale | Non-atomic read-modify-write of `.lsp.json` / `~/.claude.json`. See adjudication: MEDIUM is correct (local single-user package manager; concurrent `apm install` rare). Fix opportunistically via write-temp+rename. |
| SECURITY-002 | **HIGH** | `integration/lsp_integrator.py` collect_transitive | Transitive LSP injection / supply-chain. See Critical Findings. |
| SECURITY-003 | MEDIUM | `models/dependency/lsp.py` env | `env` dict accepted as-is — allows `PATH`, `LD_PRELOAD`, `DYLD_*`, `PYTHONPATH` overrides. Recommend a denylist of known-dangerous variable names in `LSPDependency.validate()`. |
| SECURITY-004 | MEDIUM | `models/dependency/lsp.py` args | `args` list not screened for shell metacharacters. Safe if Claude Code uses `execvp`-style, but APM should still reject obvious injection (`;`, backticks, `$()`) and document the contract. |
| SECURITY-005 | MEDIUM | `deps/plugin_parser.py` `_substitute_plugin_root` | `${CLAUDE_PLUGIN_ROOT}` is `str.replace`d into every string field (command, args, env values) before path validation. A plugin path containing shell metacharacters would propagate. Validate the plugin path itself and/or substitute only into known-safe fields. |
| SECURITY-006 | LOW | `deps/plugin_parser.py` `_read_lsp_file` | `relative_to()` traversal check can be fragile on case-insensitive FSes; defense-in-depth via symlink rejection already present. |

### Performance
| ID | Sev (final) | File | Summary |
|----|------|------|---------|
| PERFORMANCE-001 | **HIGH** | `install/lsp/integration.py:886–902` | Double read/write of LSP config. See Critical Findings. |
| PERFORMANCE-002 | LOW (downgraded) | `deps/plugin_parser.py:660,680–683` | 3× `stat()` via `exists()/is_file()/is_symlink()`. Runs only during plugin discovery; minor. |
| PERFORMANCE-003 | LOW (downgraded) | `integration/_shared.py:1030` | Per-path `exists()` over locked apm.yml paths. Mirrors MCP path; safe fallback, only matters at 100s of deps. |

### Style
| ID | Sev (final) | File | Summary |
|----|------|------|---------|
| STYLE-001 | **HIGH** | `integration/lsp_integrator.py` (multiple) | `builtins.set/dict` regression. See Critical Findings. |
| STYLE-002 | MEDIUM | `install/lsp/integration.py:828–829` | Missing type annotations on `logger`, `diagnostics`. |
| STYLE-003 | MEDIUM | `integration/lsp_integrator.py:1078,1119,1132,1143` | Bare `list` / `builtins.set` return types — add element types (`list[LSPDependency]`, `set[str]`). |
| STYLE-004 | MEDIUM | `integration/lsp_integrator.py:1272–1374` | `install()` is 103 lines; split per-scope writers into helpers. |
| STYLE-005 | MEDIUM | `integration/lsp_integrator.py:1158–1227` | `remove_stale()` duplicates project- vs user-scope cleanup logic; extract helper. |
| STYLE-006 | MEDIUM | `integration/lsp_integrator.py` (multiple) | Broad `except Exception:` blocks — narrow to `json.JSONDecodeError`, `OSError`. |
| STYLE-007 | LOW | `integration/_shared.py` | Same `builtins.set` non-idiom as STYLE-001 (smaller surface). |
| STYLE-008 | LOW | `models/apm_package.py:154` | `parsed_lsp: list = []` → `list[LSPDependency]`. |
| STYLE-009 | LOW | `integration/lsp_integrator.py:1049` | Drop `import builtins` once STYLE-001 is fixed. |

### Test Coverage
| ID | Sev (final) | File | Summary |
|----|------|------|---------|
| TEST-001 | **FALSE POSITIVE** (was HIGH) | `deps/plugin_parser.py:666` | Duplicate of CORRECTNESS-001; function exists, no missing test needed. |
| TEST-002 | MEDIUM (downgraded from HIGH) | `deps/plugin_parser.py:671–688` | No test for symlink-swap TOCTOU between path validation and read. Real but low practical exploitability (attacker must already own the plugin directory). |
| TEST-003 | MEDIUM (downgraded from HIGH) | `lsp_integrator.collect_transitive` | No test for partial-failure path when one transitive package fails to parse. |
| TEST-004 | MEDIUM | `lsp_integrator.install` | No tests for JSON write failures (EACCES, read-only FS) and atomicity of failed writes. |
| TEST-005 | MEDIUM | `lsp_integrator.get_server_configs` | No tests for malformed `LSPDependency` (missing `to_dict`/`name`). |
| TEST-006 | MEDIUM | `lsp_integrator.update_lockfile` | No tests for corrupted YAML, list-vs-set type mismatch, or clearing to empty. |
| TEST-007 | MEDIUM | `lsp_integrator.remove_stale` | No tests for invalid JSON in `.lsp.json`; ensure corruption isn’t re-serialized. |
| TEST-008 | MEDIUM | `deps/plugin_parser._lsp_servers_to_apm_deps` | No assertion that warnings are logged for skipped invalid servers. |
| TEST-009 | MEDIUM | `deps/plugin_parser._read_lsp_json` | No test for non-dict top-level JSON in `.lsp.json`. |
| TEST-010 | MEDIUM | `run_lsp_integration` | No end-to-end test for direct+transitive merge and dedup (only mocked). |
| TEST-011 | LOW | `models/dependency/lsp.validate` | Missing edge cases (spaces, absolute path, empty string, None with `strict=False`). |
| TEST-012 | LOW | `models/apm_package.get_*_lsp_dependencies` | No tests for malformed `dependencies.lsp` (mixed types, None, non-list) or dev/prod overlap. |

## Severity Breakdown
| Severity | Count |
|----------|-------|
| BLOCKER  | 0     |
| HIGH     | 3     |
| MEDIUM   | 18    |
| LOW      | 8     |
| FALSE POSITIVE | 2 |
| **Total**| **31** |

(Original raw count was 31 across 5 lenses; adjudication eliminated 2 false positives and reclassified 4 severities.)

## Adjudication Notes

1. **CORRECTNESS-001 (BLOCKER) + TEST-001 (HIGH) — `_substitute_plugin_root` undefined** → **FALSE POSITIVE, deduplicated.**
   Verified via `gh api` against `main`: the function is defined at `src/apm_cli/deps/plugin_parser.py:304` (added during MCP work) with signature `(servers: dict[str, Any], abs_root: str, logger: logging.Logger) -> dict[str, Any]` — exactly what the new LSP code at L666 calls. Both lenses missed the unchanged context because they reviewed the diff in isolation. No runtime `NameError` will occur. Lesson: both reviewers should have grepped the full file before flagging "undefined".

2. **TOCTOU race — SECURITY-001 (MEDIUM) vs TEST-002 (HIGH)** → **kept distinct; SECURITY-001 stays MEDIUM, TEST-002 downgraded to MEDIUM.**
   These describe *different* races:
   - SECURITY-001: concurrent `apm install` processes racing on `.lsp.json`. In a local package-manager workflow this is rare (users typically don’t run two installs concurrently; CI runs are usually serialized per workspace). Impact = lost-update, recoverable by re-running. MEDIUM is correct.
   - TEST-002: symlink swap inside a plugin directory between `_read_lsp_file`'s validation and read. Requires an attacker who already controls the plugin directory contents — at which point they can just declare malicious LSP servers directly. Defensive testing is warranted, but HIGH overstates the realistic risk.
   PERFORMANCE-001 (HIGH) overlaps mechanically with SECURITY-001 and should be fixed first; doing so also shrinks the TOCTOU window for free.

3. **CORRECTNESS-003 — `should_install_mcp` reused for LSP** → **downgraded to LOW.**
   Code inspection confirms this is intentional: docstring at L853 says "same gate as MCP", and tests at L2280–2434 explicitly drive `should_install=True/False` for the LSP path expecting MCP-aligned behavior. Not a bug; purely a naming hygiene nit. Optional cleanup: rename caller-side variable to `should_install_extensions` or alias `should_install_lsp = should_install_mcp` with a one-line comment.

4. **Dedup**: CORRECTNESS-001 ≡ TEST-001 (same root cause; both eliminated). SECURITY-006 and TEST-002 cover related symlink/path-traversal concern (kept both — one is the design issue, the other is the missing test).

5. **PERFORMANCE-002/003 downgraded to LOW**: both are cold-path stat overhead with no user-visible impact at realistic scale. The TEST lens did not flag them; the PERFORMANCE lens’s MEDIUM rating was inflated.

## Recommendation

**REQUEST_CHANGES** (not BLOCK).

Required before merge:
- **SECURITY-002**: add transitive-LSP warning surface (list of `name → command` being installed) and document the trust model in the PR description / docs. Even without an opt-in flag, the user must be able to see what's being added.
- **STYLE-001 + STYLE-009**: remove `import builtins` and `builtins.set/dict` usages — this is a self-inflicted regression of work already done on the MCP side and will fail any consistency lint the team adds.
- **CORRECTNESS-002**: thread `logger` into `LSPIntegrator` methods so `remove_stale` progress messages aren't silently dropped.

Strongly recommended (can be a follow-up but should be tracked):
- **PERFORMANCE-001**: unify `install()` + `remove_stale()` into one read/write pass; also closes most of SECURITY-001’s window.
- **SECURITY-003 / SECURITY-005**: env-var denylist and constrain `${CLAUDE_PLUGIN_ROOT}` substitution to known fields.
- **TEST-002, TEST-004, TEST-007, TEST-009, TEST-010**: add the missing negative-path and end-to-end tests.

Nice-to-have: STYLE-002…008, TEST-011/012, PERFORMANCE-002/003.

Once the three "required" items are addressed, the PR is mergeable — the architecture mirrors the established MCP integration correctly and the alleged blocker does not exist.
