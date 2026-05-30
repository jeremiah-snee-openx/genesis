# Code Review: microsoft/apm#1424
## feat(lsp): add first-class LSP server support to install pipeline
**+2363 / −114 · 24 changed files**

---

## Executive Summary

This PR adds first-class LSP (Language Server Protocol) server support to the APM install pipeline, mirroring the existing MCP integration pattern. It introduces `LSPDependency` (model), `LSPIntegrator` (orchestrator), `_shared.py` (extracted helpers), `run_lsp_integration()` (install orchestration), and `_extract_lsp_servers` / `_read_lsp_file` functions for reading `lspServers` blocks out of **untrusted** `plugin.json` files shipped with packages.

**Trust boundary**: `plugin.json` files from installed packages are untrusted. The code reads `lspServers` from them and writes results to `.lsp.json` (project scope) or `~/.claude.json` (user scope), which Claude Code reads to start language server processes. This trust boundary makes security correctness critical.

**Review conducted via 5-lens panel (A12 GRADIENT WORKFLOW, DISAGREE → heavy synthesis path).**

| Lens | Findings | CRITICAL | HIGH | MEDIUM | LOW |
|------|----------|----------|------|--------|-----|
| Correctness | 11 | 0 | 3 | 6 | 2 |
| Security | 14 | 3 | 6 | 3 | 2 |
| Performance | 8 | 0 | 2 | 4 | 2 |
| Style | 9 | 0 | 3 | 4 | 2 |
| Test Coverage | 19 | 1 | 7 | 7 | 4 |
| **TOTAL RAW** | **61** | **3+1*** | **21** | **25** | **11+1*** |

*PERF-008 arbitrated from LOW→CRITICAL (validated object discarded = security bypass, not just perf waste).*

**Arbitrated severity totals**: CRITICAL=4, HIGH=21, MEDIUM=25, LOW=11

**Synthesis path**: DISAGREE → synth-heavy (claude-opus-4.7).  
Two cross-lens severity conflicts detected: (1) `_read_lsp_file` TOCTOU rated HIGH (correctness) vs CRITICAL (security); (2) discarded LSPDependency rated LOW (performance) vs CRITICAL (security). Both arbitrated to CRITICAL per dissent-weighted rule (higher severity wins).

---

## ⛔ CRITICAL ACTIONS REQUIRED (Block Merge)

The following 14 findings meet the CRITICAL THRESHOLD (severity HIGH+ AND exploitable / data-loss / broken-happy-path):

| ID | Lens | Sev | Title |
|----|------|-----|-------|
| **SEC-002** | Security | CRITICAL | Validated LSPDependency object discarded — raw unvalidated dict written to config |
| **SEC-001** | Security | CRITICAL | TOCTOU symlink attack between path validation and file read |
| **SEC-009** | Security | CRITICAL | Arbitrary JSON in `initializationOptions` and `settings` injected into LSP config |
| **CORR-003** | Correctness | HIGH→CRITICAL* | Path traversal check uses resolved path but file opened via unresolved — symlink bypass |
| **SEC-003** | Security | HIGH | Unsanitized `env` dict from untrusted plugin.json injected into LSP process environment |
| **SEC-004** | Security | HIGH | Arbitrary `args` list from untrusted plugin.json passes through without validation |
| **SEC-005** | Security | HIGH | Relative `command` path from untrusted plugin.json enables execution of attacker-controlled binaries |
| **SEC-006** | Security | HIGH | `${CLAUDE_PLUGIN_ROOT}` substitution in `command` enables arbitrary binary execution |
| **SEC-007** | Security | HIGH | Non-atomic write to config files — race condition and corruption risk |
| **SEC-008** | Security | HIGH | Symlink attack on `~/.claude.json` write — no symlink check before writing |
| **CORR-001** | Correctness | HIGH | Wrong variable `should_install_mcp` used as LSP install gate — broken happy-path |
| **TEST-001** | Test Coverage | CRITICAL | No tests for SEC-002 (discarded validated object) — security regression can re-enter silently |
| **TEST-002** | Test Coverage | HIGH | No test for path traversal / symlink bypass in `_read_lsp_file` |
| **TEST-003** | Test Coverage | HIGH | No test for `should_install_mcp` vs `should_install_lsp` gating |

*CORR-003 arbitrated from HIGH to CRITICAL (cross-lens severity conflict resolved in favour of security lens).

**The highest-priority blocker is SEC-002**: the entire `LSPDependency.validate()` call in `_lsp_servers_to_apm_deps` is a no-op — the validated object is thrown away and the raw, unvalidated dict is appended and flows unmodified into `~/.claude.json` / `.lsp.json`. Combined with the TOCTOU gap (SEC-001/CORR-003), an attacker distributing a malicious package can execute arbitrary code on the victim's machine via LSP server process injection.

---

## Findings by Lens

### Correctness (11 findings)

**[CORR-001] HIGH** Wrong variable passed as `should_install`: `should_install_mcp` instead of LSP-specific flag
> The call `run_lsp_integration(..., should_install=should_install_mcp, ...)` reuses the MCP install flag for LSP gating. If LSP and MCP have independent enable/disable logic (e.g., `--only=mcp` vs `--only=lsp`), this silently skips all LSP installation when MCP is disabled, or vice versa. There is no evidence a dedicated `should_install_lsp` variable exists, meaning the control flow for LSP is permanently coupled to MCP's gate.
> **Recommendation:** Introduce a dedicated `should_install_lsp` variable computed with the same logic as `should_install_mcp` but scoped to LSP. Pass that variable instead.

**[CORR-002] HIGH** `new_lsp_configs` never initialized to a safe default — potential NameError
> In the `elif should_install and not lsp_deps` branch, `LSPIntegrator.update_lockfile(builtins.set(), lock_path, lsp_configs={})` correctly clears configs. However `new_lsp_configs` is only ever assigned inside the `if should_install and lsp_deps:` block. If code is ever refactored to reference `new_lsp_configs` outside that block, a `NameError` will be raised. The variable is not initialised to a safe default at the top of the function, unlike `new_lsp_servers` which is initialised to `builtins.set()`.
> **Recommendation:** Initialise `new_lsp_configs: builtins.dict = {}` alongside `new_lsp_servers` at the top of the function, before the branching logic.

**[CORR-003] HIGH** [Arbitrated: CRITICAL] Path traversal check uses resolved path but file is opened via unresolved path — symlink bypass possible
> `target = (plugin_path / rel_path).resolve()` is checked with `target.relative_to(plugin_path.resolve())` to confirm containment. However, the file is then re-opened via `candidate = plugin_path / rel_path` (unresolved). If `rel_path` itself is not a symlink but an intermediate directory in `plugin_path` is a symlink pointing outside the root, the resolved check may pass for a different effective path than the one actually read. More critically, the symlink check `candidate.is_symlink()` only checks the final component; if any intermediate path component is a symlink the containment guarantee from `.resolve()` does not apply to the unresolved open path.
> **Recommendation:** Use `target` (the already-resolved path) for the actual file read: `target.read_text(...)` instead of reopening via `candidate`. This eliminates any gap between the checked path and the opened path.

**[CORR-004] MEDIUM** Falsy-zero integer fields incorrectly fall through to snake_case fallback via `or`
> `startup_timeout=d.get('startupTimeout') or d.get('startup_timeout')` uses Python's boolean `or`, which treats `0` as falsy. If a caller sets `startupTimeout: 0` (meaning 'no timeout / immediate'), the expression evaluates `0 or d.get('startup_timeout')` and silently substitutes the snake_case value (or `None`). The same defect applies to `shutdown_timeout` and `max_restarts`. This is a silent data-corruption bug: the explicit user intent of `0` is discarded.
> **Recommendation:** Use an explicit sentinel: `startup_timeout = d['startupTimeout'] if 'startupTimeout' in d else d.get('startup_timeout')`. Apply the same pattern for `shutdown_timeout` and `max_restarts`.

**[CORR-005] MEDIUM** Root-level `lsp_deps` duplicates are never deduplicated when there are no transitive deps
> `LSPIntegrator.deduplicate(lsp_deps + transitive_lsp)` is only called when `transitive_lsp` is non-empty. If the root `apm.yml` already contains duplicate LSP dependency entries, they are never deduplicated. Downstream, `install()` will process duplicates, and `lsp_count` will be overcounted.
> **Recommendation:** Always deduplicate `lsp_deps` before proceeding: call `lsp_deps = LSPIntegrator.deduplicate(lsp_deps)` unconditionally after collecting root deps.

**[CORR-006] MEDIUM** First-install path skips transitive LSP collection because `apm_modules_path` does not yet exist
> On the very first `apm install` run, `apm_modules_path` does not exist before packages are installed. The guard `if should_install and apm_modules_path.exists()` therefore skips `collect_transitive`, so no transitive LSP deps from newly installed packages are picked up in the same run. Users must run `apm install` twice.
> **Recommendation:** Collect transitive LSP deps *after* the package install step completes, not before.

**[CORR-007] MEDIUM** `remove_stale` cleans only active scope — stale servers in non-active scope left behind
> The method has two mutually exclusive branches: `if not user_scope` cleans `.lsp.json`, `if user_scope` cleans `~/.claude.json`. If a project was previously installed in user scope and is later installed in project scope (or vice versa), the stale entries in the other scope are never removed.
> **Recommendation:** Consider always cleaning both scopes, or document that cross-scope cleanup is not performed.

**[CORR-008] MEDIUM** `logger` parameter not validated for None before calling `logger.progress()`
> `remove_stale` has a `logger=None` default but calls `logger.progress(...)` unconditionally when entries are removed. If the caller omits `logger`, this raises `AttributeError`.
> **Recommendation:** Guard calls with `if logger:` before `logger.progress(...)`, or add a NullCommandLogger default.

**[CORR-009] MEDIUM** `update_lockfile` silently no-ops when lockfile does not exist
> If `lock_path` does not yet exist, `update_lockfile` returns immediately without creating the file or raising an error. This means on a fresh install, the LSP server list is silently dropped.
> **Recommendation:** Log a warning via `_log.warning` when lock_path doesn't exist. Consider propagating the error so the caller can decide.

**[CORR-010] LOW** String LSP deps produce `{"name": dep}` config which is inconsistent with object deps
> For string-typed deps, `get_server_configs` returns `configs[dep] = {"name": dep}`. This config dict has only a `name` key and no `command`, making it invalid per `LSPDependency.validate(strict=True)`.
> **Recommendation:** For string deps, store an empty dict `{}` in configs (or skip them) rather than `{"name": dep}`.

**[CORR-011] LOW** `count` increments even when server config is unchanged — counter may be inaccurate for list fields
> In `install()`, `count` is incremented with `if name not in existing or existing[name] != cfg`. If `cfg` contains lists (e.g., `args`) in different orders, `!=` may return True spuriously.
> **Recommendation:** Low risk for typical configs. Consider normalizing list fields before comparison.

---

### Security (14 findings)

**[SEC-001] CRITICAL** TOCTOU symlink attack between path validation and file read
> In `_read_lsp_file`, the path is first resolved and validated via `target.relative_to(plugin_path.resolve())`, then the symlink check is done on `candidate = plugin_path / rel_path` (the unresolved path). Between the `is_symlink()` check and the actual `path.read_text()` call in `_read_lsp_json`, an attacker who controls the package directory can replace the regular file with a symlink pointing to any file on the filesystem. The race window exists because `candidate` is never re-resolved before reading.
> **Recommendation:** Open the file using `os.open()` with `O_NOFOLLOW` to atomically prevent symlink following at the OS level, or use pathlib with a resolved path and hold the file descriptor open. At minimum, use `target` (the already-resolved path) for the actual read and re-validate containment.

**[SEC-002] CRITICAL** Validated LSPDependency object discarded — raw unvalidated dict written to config
> `_lsp_servers_to_apm_deps` creates an `LSPDependency` object solely for validation, then discards it and appends the original raw `dep` dict. This dict flows into `install()` where it hits the `isinstance(dep, dict)` branch, which does a raw copy with zero further sanitization and writes it directly into `~/.claude.json` or `.lsp.json`. Effectively, the validation chokepoint is a no-op: it validates a temporary object and then throws it away.
> **Recommendation:** Replace `deps.append(dep)` with `deps.append(validated_dep)` where `validated_dep` is the `LSPDependency` object returned by `from_dict()`. In `install()`, eliminate the raw-dict branch or raise if a dict reaches it.

**[SEC-003] HIGH** Unsanitized `env` dict from untrusted plugin.json injected into LSP process environment
> The `env` field is copied verbatim from `plugin.json` into the LSP config that Claude Code reads to start language server processes. There is no validation of env key names or values. An attacker distributing a malicious package can inject environment variables such as `LD_PRELOAD`, `DYLD_INSERT_LIBRARIES`, `PATH`, `PYTHONPATH`, `NODE_OPTIONS=--require /tmp/evil.js`, enabling code execution or credential exfiltration.
> **Recommendation:** Validate `env` as a flat `dict[str, str]`. Maintain a denylist of dangerous variable names (`LD_PRELOAD`, `LD_LIBRARY_PATH`, `DYLD_INSERT_LIBRARIES`, `PYTHONPATH`, `NODE_OPTIONS`, `PATH`, etc.) and reject matching entries.

**[SEC-004] HIGH** Arbitrary `args` list from untrusted plugin.json passes through without validation
> The `args` field from `plugin.json` is copied directly into the LSP config without any validation of content, length, or type. An attacker can inject arguments that alter the behavior of the spawned LSP binary: e.g., `--config /attacker/path`, `--eval <code>`, `--require evil-module`.
> **Recommendation:** Validate that `args` is a `list[str]` with each element being a non-empty string of bounded length. Consider a denylist for dangerous argument prefixes.

**[SEC-005] HIGH** Relative `command` path from untrusted plugin.json enables execution of attacker-controlled binaries
> `validate_path_segments` is called with `allow_current_dir=True`, meaning `command` values like `./node_modules/.bin/evil` or `./run.sh` are accepted. Combined with `${CLAUDE_PLUGIN_ROOT}` substitution, an attacker can set `command` to `${CLAUDE_PLUGIN_ROOT}/evil` to execute arbitrary binaries from the package.
> **Recommendation:** Require `command` to be a binary resolvable via system `PATH` only (bare filename, no path separators). Disallow `./` and `../` prefixes. Prohibit `${CLAUDE_PLUGIN_ROOT}` in `command` specifically.

**[SEC-006] HIGH** `${CLAUDE_PLUGIN_ROOT}` substitution applied to `command` enables arbitrary binary execution
> The `_substitute_plugin_root` function replaces `${CLAUDE_PLUGIN_ROOT}` in ALL string values within the server config dict, including `command`. This means a plugin can set `"command": "${CLAUDE_PLUGIN_ROOT}/bin/myserver"` and have Claude Code execute an arbitrary binary shipped inside the package. The substitution happens before validation, so `validate_path_segments` receives an already-substituted absolute path that passes trivially.
> **Recommendation:** Do not allow `${CLAUDE_PLUGIN_ROOT}` substitution in the `command` field. Only permit substitution in `args`, `env` values, `workspaceFolder`, and similar non-executable fields.

**[SEC-007] HIGH** Non-atomic write to config files — race condition and corruption risk
> `~/.claude.json` and `.lsp.json` are read, modified in memory, and written back with `write_text()` — a non-atomic operation. A crash or concurrent process between the read and write leaves the file in an inconsistent state. On systems with predictable temp file names, an attacker may be able to replace the target with a symlink between the read and write.
> **Recommendation:** Write to a temp file in the same directory (`tempfile.NamedTemporaryFile(dir=..., delete=False)`), then atomically rename it over the target (`os.replace()`). Use `fcntl.flock()` for mutual exclusion.

**[SEC-008] HIGH** Symlink attack on `~/.claude.json` write — no symlink check before writing
> Before writing to `~/.claude.json`, there is no check that the path is not a symlink. An attacker who can create `~/.claude.json` as a symlink can redirect the write to any file writable by the user, such as `~/.bashrc`, `~/.ssh/authorized_keys`.
> **Recommendation:** Before `write_text()`, verify the path is not a symlink using `os.path.islink()`. Use `os.replace()` with an atomic temp file approach.

**[SEC-009] CRITICAL** Arbitrary JSON in `initializationOptions` and `settings` injected into LSP config
> `initializationOptions` and `settings` accept arbitrary nested JSON structures (type `Any`) from untrusted `plugin.json` with no validation of type, depth, or content. Depending on how Claude Code processes these fields, they may override security-relevant settings or exploit vulnerabilities in LSP client handling.
> **Recommendation:** Apply a JSON schema or depth/size limit to `initializationOptions` and `settings`. At minimum, validate they are plain dicts with bounded depth (max 5 levels) and maximum total serialized size.

**[SEC-010] MEDIUM** Unvalidated `workspaceFolder` path may point to arbitrary filesystem locations
> `workspaceFolder` is a string field accepted from `plugin.json` without path traversal validation. An attacker can set it to an absolute path (e.g., `/etc`, `/home/victim/.ssh`). When Claude Code uses this to set the LSP workspace root, it may grant the language server access to sensitive directories.
> **Recommendation:** Validate `workspaceFolder` using `validate_path_segments()` and require it to be a relative path or restricted to paths within the project root.

**[SEC-011] MEDIUM** Inline `lspServers` dict from plugin.json bypasses file-level symlink/path checks
> When `plugin.json` contains `"lspServers": { ... }` as a dict, the servers are used directly without file-reading guards. Combined with SEC-002 (validated object discarded), the raw dict flows through unmodified.
> **Recommendation:** Apply the same validation pipeline regardless of how `lspServers` is supplied. Fix SEC-002 first.

**[SEC-012] MEDIUM** Security-relevant write failures silently swallowed at DEBUG level
> Both `~/.claude.json` and `.lsp.json` write paths catch all exceptions and log them only at `DEBUG` level. If a write fails, the caller receives a return count with no indication that the security-critical configuration was not written.
> **Recommendation:** Log at `WARNING` or `ERROR` level for write failures. Return a distinct error code or raise a specific exception type that the caller can surface to the user.

**[SEC-013] MEDIUM** Path confinement check uses resolved path but file read uses unresolved path
> The confinement check uses the resolved path, but all subsequent operations use `candidate = plugin_path / rel_path` (unresolved). The correct pattern is to resolve once and use the resolved path exclusively.
> **Recommendation:** After the confinement check passes, set `candidate = target` (already-resolved) and use it for all subsequent checks and reads.

**[SEC-014] LOW** LSP server name regex permits characters usable in JSON key injection or log injection
> The `_NAME_REGEX` allows names containing `:`, `=`, `/`, and `@`. Names with `/` could be confused with filesystem paths in downstream consumers.
> **Recommendation:** Review whether all permitted characters in `_NAME_REGEX` are intentional for Claude Code consumers. Consider tightening the regex to disallow `:` and `=` unless required.

---

### Performance (8 findings)

**[PERF-001] HIGH** Lockfile read from disk 3+ times per install run
> `MCPIntegrator.collect_transitive()`, `LSPIntegrator.collect_transitive()`, and `LSPIntegrator.update_lockfile()` each independently read the lockfile from disk. For a single `apm install` invocation, this results in at minimum 3 disk reads of the same file. In CI environments with cold disk caches or network filesystems, this adds measurable latency.
> **Recommendation:** Read the lockfile once at the start of the integration phase and pass the parsed object through the call chain. The `collect_transitive` and `update_lockfile` signatures should accept an optional `existing_lock` parameter.

**[PERF-002] HIGH** O(n²) dict comparison in server install loop
> For each incoming server config, `install()` checks `if name not in existing or existing[name] != cfg`. When `existing` is a dict this is O(1), but `cfg` comparison is a deep dict equality check. If `cfg` contains large nested structures (e.g., `initializationOptions`), repeated comparisons in a loop over many servers compounds to O(n × m) where m is the config size.
> **Recommendation:** Pre-hash configs using `json.dumps(cfg, sort_keys=True)` or compute a SHA256 of serialized configs to reduce comparison cost per server.

**[PERF-003] MEDIUM** Separate iterations over server list for names vs configs — avoidable double pass
> `get_server_names()` and `get_server_configs()` each iterate the full `lsp_deps` list independently. In `run_lsp_integration()` both are called sequentially, resulting in two full list traversals.
> **Recommendation:** Merge into a single `get_servers()` method returning both names and configs as a tuple, or iterate once and unpack.

**[PERF-004] MEDIUM** Full directory scan of apm_modules for every install run, including up-to-date packages
> Every `apm install` invocation scans all subdirectories under `apm_modules_path` looking for `plugin.json` files, even for packages that haven't changed. For projects with many installed packages, this is unnecessary I/O.
> **Recommendation:** Cache the LSP server list in the lockfile keyed by package name + version. Only re-read `plugin.json` for packages whose version changed since the last lock.

**[PERF-005] MEDIUM** Config file parsed twice on stale cleanup: once in remove_stale, once in install
> When `remove_stale()` is called before `install()`, both methods independently read and parse the same config file (`~/.claude.json` or `.lsp.json`). The parsed content should be passed between calls.
> **Recommendation:** Accept an optional parsed config dict parameter in both methods and return the updated dict for chaining.

**[PERF-006] MEDIUM** Deduplication uses O(n) iteration with string coercion in inner loop
> `deduplicate_deps` iterates over all deps, converting each to a string key for dedup. If deps are complex nested dicts this string conversion is expensive and repeated.
> **Recommendation:** Pre-compute canonical keys outside the loop or use `json.dumps(dep, sort_keys=True)` once per dep.

**[PERF-007] LOW** Transitive dep collection rebuilds list from lockfile on each call
> Each call to `collect_transitive()` re-reads and re-parses the lockfile, then filters for LSP entries. For large lockfiles with many transitive deps, this is unnecessary repeated parsing.
> **Recommendation:** Cache the result with `functools.lru_cache` or use the existing_lock passthrough (see PERF-001).

**[PERF-008] LOW** [Arbitrated: CRITICAL per SEC-002] LSPDependency object constructed then discarded — wasted allocation
> Per SEC-002 (confirmed independently): `LSPDependency` is constructed for validation then discarded; the raw dict is appended. This wastes an object allocation and validation pass.
> **Recommendation:** Fix SEC-002: use the constructed `LSPDependency` object directly, eliminating the wasted allocation.

---

### Style (9 findings)

**[STYLE-001] HIGH** Static-method-only class should be a module-level namespace
> `LSPIntegrator` has zero instance methods and carries no state — all methods are `@staticmethod`. Python convention (PEP 8, Google style) is to use a module or a set of module-level functions for stateless utilities. The class form adds unnecessary cognitive overhead and prevents natural import aliasing. The analogous `MCPIntegrator` has the same shape, suggesting this is a copy-paste pattern from a class that once had state.
> **Recommendation:** Convert to module-level functions in `lsp_integrator.py` and import them directly. If the class is kept for polymorphism reasons (duck-typing with MCPIntegrator), document that intent explicitly.

**[STYLE-002] HIGH** Validation logic split across `validate(strict=False)` and `validate(strict=True)` is misleading
> The `strict` flag changes not just error-raising behavior but also which fields are validated (strict adds `command` format checking). This is a violation of single-responsibility: callers need to know the internal difference. A caller that calls `validate(strict=False)` may believe validation passed when only a subset was checked.
> **Recommendation:** Separate into two methods: `validate_presence()` (required fields) and `validate_strict()` (full format checking). Or document explicitly what each mode checks.

**[STYLE-003] HIGH** Function too long; multiple abstraction levels mixed — install orchestration, side effects, and error handling
> `run_lsp_integration()` is approximately 80 lines of dense logic mixing: transitive dep collection, deduplication, LSP count, remove_stale, install, update_lockfile, and progress reporting. Extracting sub-functions would dramatically improve readability.
> **Recommendation:** Extract helpers: `_collect_all_lsp_deps()`, `_report_lsp_results()`. Limit the orchestrator to 30–40 lines.

**[STYLE-004] MEDIUM** `from_dict` uses `or`-chaining for camelCase/snake_case fallback — brittle pattern
> The camelCase → snake_case fallback uses Python `or` which silently ignores falsy values (0, False, empty string, empty list). This is covered from a correctness view (CORR-004) but is also a style concern: the pattern is hard to read and maintain.
> **Recommendation:** Use an explicit sentinel (`dict.get` with a `_MISSING` default) or write a small `_get_field(d, *keys)` helper that doesn't conflate missing-key with falsy-value.

**[STYLE-005] MEDIUM** Nested try/except blocks with overwide `Exception` catch
> The function has nested `try/except Exception` blocks where specific exceptions (`json.JSONDecodeError`, `PermissionError`, `FileNotFoundError`) could be caught individually for better diagnostics.
> **Recommendation:** Replace bare `except Exception` with specific exception types. Log the exception class and message at DEBUG level for easier troubleshooting.

**[STYLE-006] MEDIUM** Two separate isinstance branches for dict vs LSPDependency — should be unified
> `install()` has two branches: one for `dict` and one for `LSPDependency`. This duplication is fragile — behavior diverges between paths. Fixing SEC-002 would eliminate the dict branch entirely.
> **Recommendation:** After SEC-002 is fixed, remove the dict branch. Until then, document why both branches exist.

**[STYLE-007] MEDIUM** Missing type annotations on `_shared.py` functions
> `deduplicate_deps` and `resolve_locked_apm_yml_paths` lack type annotations. The rest of the codebase uses annotations consistently.
> **Recommendation:** Add `list[dict]` / `set[str]` / `dict` return type annotations.

**[STYLE-008] LOW** Loop variable `dep` reused for both raw dict and validated object — shadowing risk
> Inside the loop, `dep` is the raw dict; after `LSPDependency.from_dict(dep)` it is re-bound to the validated object in a separate variable `lsp_dep`. The naming is clear but proximity risk of `deps.append(dep)` vs `deps.append(lsp_dep)` is exactly the SEC-002 bug.
> **Recommendation:** Rename the validated object to match its role: `validated = LSPDependency.from_dict(dep)`. Then `deps.append(validated)` is unambiguous.

**[STYLE-009] LOW** `lsp_count` initialized to `len(lsp_deps)` but overwritten without use — dead assignment
> At the top of the function `lsp_count = len(lsp_deps)`. It is immediately overwritten by `lsp_count = LSPIntegrator.install(...)`. The initial assignment is dead code.
> **Recommendation:** Remove the initial `lsp_count = len(lsp_deps)` assignment.

---

### Test Coverage (19 findings)

**[TEST-001] CRITICAL** No tests for SEC-002: validated LSPDependency discarded — security regression can be silently reintroduced
> The most critical finding in this PR (SEC-002: validated object discarded, raw dict written) has zero test coverage. There is no test asserting that the object returned by `LSPDependency.from_dict()` is the one ultimately written to the config file. Without a test, the fix for SEC-002 (if made) can regress silently.
> **Recommendation:** Add a test: after calling `_lsp_servers_to_apm_deps()` with a malformed server config that passes `LSPDependency.from_dict()` validation but whose raw dict differs from the validated object, assert that the output is equal to the validated object's `to_dict()`, not the raw input dict.

**[TEST-002] HIGH** No test for path traversal / symlink bypass in `_read_lsp_file`
> `_read_lsp_file` implements a path confinement check meant to prevent reading outside the plugin directory. There is no test that: (a) attempts a path traversal via `../../../etc/passwd`, (b) verifies symlinks are rejected, (c) validates the TOCTOU gap is handled correctly. Without tests, the fix for SEC-001/CORR-003 has no regression guard.
> **Recommendation:** Add tests: (1) assert `_read_lsp_file` raises when given `rel_path = '../../secret'`, (2) assert it raises when `rel_path` points to a symlink, (3) assert a valid nested relative path succeeds.

**[TEST-003] HIGH** No test for `should_install_mcp` vs `should_install_lsp` gating
> The CORR-001 bug (wrong flag variable passed to `run_lsp_integration`) would not be caught by any existing test because no test exercises the case where MCP is disabled but LSP should still install (or vice versa).
> **Recommendation:** Add integration tests covering: (1) MCP disabled, LSP enabled — assert LSP install runs, (2) LSP disabled, MCP enabled — assert LSP install does not run.

**[TEST-004] HIGH** No test for falsy-zero integer field handling in `LSPDependency.from_dict`
> The CORR-004 bug (falsy `0` overridden by `or` chaining) is not tested. No test passes `startupTimeout: 0` and asserts the result is `startup_timeout = 0` (not `None`).
> **Recommendation:** Add parametrized tests for `startup_timeout`, `shutdown_timeout`, and `max_restarts` with values: `0`, `None`, and a positive integer. Assert that `0` yields `0`, not `None`.

**[TEST-005] HIGH** No test for `remove_stale` with `logger=None` default — AttributeError not caught
> CORR-008 identifies that `remove_stale(logger=None)` will raise `AttributeError` if it finds stale entries. No test calls `remove_stale` without a logger.
> **Recommendation:** Add a test: call `LSPIntegrator.remove_stale(...)` with `logger=None` and stale entries present; assert it does not raise.

**[TEST-006] HIGH** No test for non-atomic write failure recovery
> SEC-007 identifies non-atomic writes to `~/.claude.json` and `.lsp.json`. No test simulates a write failure partway through and verifies the file is left in a consistent state.
> **Recommendation:** Mock `Path.write_text` to raise `IOError` after a partial write. Assert the original file content is preserved.

**[TEST-007] HIGH** No test for cross-scope stale cleanup (CORR-007)
> `remove_stale` only cleans the active scope. There is no test verifying that switching between user and project scope leaves stale entries in the previous scope.
> **Recommendation:** Add a test: install in user scope, then install in project scope; assert the user scope still contains the old entries (document the limitation), or verify cleanup if that behavior is added.

**[TEST-008] MEDIUM** No test for `env` field with dangerous variable names
> SEC-003 (LD_PRELOAD injection via env) is untested. No test passes an `env` dict containing `LD_PRELOAD` and asserts it is rejected.
> **Recommendation:** Add tests: (1) `env: {LD_PRELOAD: evil.so}` → rejected by validation, (2) `env: {VALID_KEY: value}` → accepted.

**[TEST-009] MEDIUM** No test for `${CLAUDE_PLUGIN_ROOT}` substitution in command field (SEC-006)
> The `_substitute_plugin_root` function applies to all string values including `command`. No test verifies that substitution in `command` is either blocked or produces the expected output.
> **Recommendation:** Add a test: set `command: '${CLAUDE_PLUGIN_ROOT}/bin/server'` and assert whether substitution is allowed or blocked (depending on the fix applied for SEC-006).

**[TEST-010] MEDIUM** No test for `update_lockfile` on a non-existent lock path (CORR-009)
> `update_lockfile` silently no-ops if the lockfile doesn't exist. There is no test for the fresh-install case where the lockfile has not been created yet.
> **Recommendation:** Add a test: call `update_lockfile` with a non-existent path; assert the lockfile is created (or assert the expected warning is logged, depending on intended behavior).

**[TEST-011] MEDIUM** No test for `install()` with string LSP deps (CORR-010)
> `get_server_configs()` returns `{"name": dep}` for string-typed deps, which is an incomplete config. No test covers the string-dep branch.
> **Recommendation:** Add a test: pass string deps through `install()` and assert no config key is written with only a `name` field (or that the dep is skipped).

**[TEST-012] MEDIUM** No test for `LSPDependency.validate(strict=True)` vs `validate(strict=False)` difference
> The `strict` mode validates additional fields. No test covers the difference in behavior between the two modes.
> **Recommendation:** Add a parametrized test: same input dict, compare fields validated in each mode. Verify strict mode catches command format errors that non-strict mode ignores.

**[TEST-013] MEDIUM** No end-to-end test for `run_lsp_integration` on first install (CORR-006)
> CORR-006 identifies that first-install skips transitive dep collection because `apm_modules_path` doesn't exist. No test covers the path where `apm_modules_path.exists()` is False.
> **Recommendation:** Add a test: call `run_lsp_integration` with a non-existent `apm_modules_path`; assert transitive deps are still collected after package installation.

**[TEST-014] MEDIUM** No test for `deduplicate` with duplicate server names across LSP deps
> `LSPIntegrator.deduplicate` is not directly tested with conflicting entries. No test verifies which duplicate is kept (first, last, or error) and that count is accurate.
> **Recommendation:** Add a test: pass two deps with the same name and different configs; assert exactly one survives and `lsp_count` is 1.

**[TEST-015] LOW** No test for `collect_transitive` with empty lockfile
> No test verifies that `collect_transitive` on an empty lockfile returns an empty list without error.
> **Recommendation:** Add a test: pass an empty lockfile; assert return is empty list.

**[TEST-016] LOW** No test for `get_server_names` with zero LSP deps
> `get_server_names()` is not tested with an empty deps list.
> **Recommendation:** Add a test: pass empty deps list; assert return is empty set.

**[TEST-017] LOW** No test for `_extract_lsp_servers` with dict-format `lspServers`
> When `plugin.json` contains `lspServers` as an inline dict (not a file path), a different code branch is followed. No test covers this.
> **Recommendation:** Add a test: construct a `plugin.json` with `lspServers: {server1: {command: node, args: []}}` as a dict; assert it is correctly extracted.

**[TEST-018] LOW** No test for `remove_stale` in user scope vs project scope
> `remove_stale` has user-scope and project-scope branches. No test covers both code paths.
> **Recommendation:** Add two tests: one for user scope, one for project scope, each asserting correct stale entry removal.

**[TEST-019] LOW** No test for `LSPDependency` with all optional fields set to None
> No test verifies that all optional fields default to `None` when not provided in `from_dict`.
> **Recommendation:** Add a minimal test: pass `{name: server, command: node}` and assert all optional fields are None.

---

## Cross-Lens Convergence Notes

Per dissent-weighted synthesis rules, findings are **preserved verbatim in their respective lens sections** above. Cross-lens overlaps are noted below for information only — they do not cause merging.

| Underlying defect | Lens findings | Arbitration |
|---|---|---|
| TOCTOU / symlink bypass in `_read_lsp_file` | SEC-001 (CRITICAL), CORR-003 (HIGH→CRITICAL*), SEC-013 (MEDIUM), TEST-002 (HIGH) | *Severity arbitrated CRITICAL — security lens wins |
| Validated LSPDependency discarded; raw dict written | SEC-002 (CRITICAL), PERF-008 (LOW→CRITICAL*), STYLE-006 (MEDIUM), STYLE-008 (LOW), SEC-011 (MEDIUM), TEST-001 (CRITICAL) | *PERF-008 arbitrated CRITICAL — security framing wins |
| `${CLAUDE_PLUGIN_ROOT}` / relative command → RCE | SEC-005 (HIGH), SEC-006 (HIGH), TEST-009 (MEDIUM) | Fix together |
| Falsy-zero `or`-chaining in `from_dict` | CORR-004 (MEDIUM), STYLE-004 (MEDIUM), TEST-004 (HIGH) | |
| Wrong `should_install_mcp` flag for LSP | CORR-001 (HIGH), TEST-003 (HIGH) | Broken happy-path |
| `remove_stale(logger=None)` AttributeError | CORR-008 (MEDIUM), TEST-005 (HIGH) | |
| Cross-scope stale cleanup not performed | CORR-007 (MEDIUM), TEST-007 (HIGH) | |
| Non-atomic config writes / symlink writes | SEC-007 (HIGH), SEC-008 (HIGH), TEST-006 (HIGH) | |
| Lockfile read repeatedly | PERF-001 (HIGH), PERF-005 (MEDIUM), PERF-007 (LOW) | One optimization fixes all |
| `update_lockfile` no-op on missing lock | CORR-009 (MEDIUM), TEST-010 (MEDIUM) | |
| String LSP deps emit incomplete configs | CORR-010 (LOW), TEST-011 (MEDIUM) | |
| `validate(strict=…)` field-set differs | STYLE-002 (HIGH), TEST-012 (MEDIUM) | |
| First-install skips transitive collection | CORR-006 (MEDIUM), TEST-013 (MEDIUM) | |

---

## Model Dispatch Record (B12 Binding Confirmation)

| Agent | Model | Notes |
|-------|-------|-------|
| lens-correctness | `claude-sonnet-4.6` | Architect binding honored |
| lens-security | `claude-sonnet-4.6` | Architect binding honored |
| lens-performance | `claude-sonnet-4.6` | Architect binding honored |
| lens-style | `claude-haiku-4.5` | **Fallback**: `gpt-5-mini` unavailable in this harness |
| lens-test-coverage | `claude-sonnet-4.6` | Architect binding honored |
| **synth-heavy (this doc)** | **`claude-opus-4.7`** | **B12 FIRING SLOT** |
| orchestrator (disagreement detector + dispatch) | `claude-sonnet-4.6` | Pinned session model |

**Synthesis path**: DISAGREE → heavy  
**Conflicts detected**: 2 cross-lens severity disagreements  
1. `_read_lsp_file` TOCTOU: CORR=HIGH vs SEC=CRITICAL → arbitrated CRITICAL  
2. Discarded LSPDependency: PERF=LOW vs SEC=CRITICAL → arbitrated CRITICAL
