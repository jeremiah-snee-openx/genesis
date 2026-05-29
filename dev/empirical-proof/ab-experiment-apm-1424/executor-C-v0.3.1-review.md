# Advisory PR Review — microsoft/apm#1424

## Headline
- CRITICAL: 1
- HIGH: 1
- MEDIUM: 9
- LOW: 9
- Total post-clustering: 20 (raw across all lenses: 21)

## Summary
The PR adds substantive new functionality (LSP servers as first-class install-pipeline citizens) with broad surface area across parsing, validation, integration, and lockfile handling. The dominant risk class is **security**: untrusted plugin manifests flow into spawn-time configuration with weak validation, most notably an unfiltered `env` dict that enables `LD_PRELOAD`-style arbitrary code execution. Correctness/perf issues are real but contained (Pythonic `or` foot-guns, redundant lockfile reads, non-atomic JSON writes). Test coverage for two new public APMPackage methods and the new shared helpers is light. Recommend blocking on the env-validation issue; the rest can land as follow-ups.

## Top Findings (inline-comment candidates, ranked)

### #1 [CRITICAL] Unvalidated env dict in LSP manifest enables LD_PRELOAD / DYLD_INSERT_LIBRARIES RCE
- File: `src/apm_cli/models/dependency/lsp.py:144`
- Lens(es): security
- Dissent weight: SOLE-IN-DOMAIN (security lens owns code-execution risks; not down-weighted). Promoted to CRITICAL under threshold rule 5(b) — exploitable RCE path.
- Detail: `validate()` covers `name`, `command`, and `transport` but applies no filtering to the `env` dict. A malicious or compromised plugin can declare `env: { LD_PRELOAD: "/tmp/evil.so" }` (or `DYLD_INSERT_LIBRARIES` on macOS, or a hijacked `PATH`). The keys/values are serialized verbatim into `.lsp.json` and `~/.claude.json`, and Claude Code honours them when spawning the server — yielding arbitrary code execution in the user's session.
- Suggested action: Add an env-key denylist (`LD_PRELOAD`, `LD_LIBRARY_PATH`, `LD_AUDIT`, `DYLD_*`, `PATH`, `PYTHONPATH`, `NODE_OPTIONS`, …) or, preferably, an allowlist regex applied in `validate()`. Reject the dependency on violation with a clear error citing the offending key.

### #2 [HIGH] `initialization_options` accepts unvalidated arbitrary nested objects AND the parser drops explicit `{}`
- File: `src/apm_cli/models/dependency/lsp.py:1601` (also referenced at line 33)
- Lens(es): correctness + security
- Dissent weight: CROSS-LENS-REINFORCED → PROMOTED (MEDIUM → HIGH). Same field/region flagged independently by two lenses with different framings.
- Detail: (a) Correctness: `initialization_options = d.get('initializationOptions') or d.get('initialization_options')` treats an explicit empty dict `{}` as falsy, silently falling through to the snake_case key (typically absent). A plugin author resetting server options via `initializationOptions: {}` has the setting dropped. (b) Security: the same field accepts arbitrary nested JSON with no schema or size bound, then is written straight to spawn config. The two flaws compound: silent drops mask malformed payloads.
- Suggested action: Replace `or` with explicit `'initializationOptions' in d` membership tests (also for `settings`). Add a schema validator constraining values to JSON primitives, with a size cap (e.g., 64 KB serialized).

### #3 [MEDIUM] `workspaceFolder` not validated for path traversal
- File: `src/apm_cli/models/dependency/lsp.py:144`
- Lens(es): security
- Dissent weight: SOLE-IN-DOMAIN
- Detail: `command` is checked via `validate_path_segments()`, but `workspace_folder` has no equivalent guard. A plugin can declare `workspaceFolder: "../../../../etc"`, written verbatim to config. LSP servers that honour `workspaceFolder` will operate on directories outside the project root, exposing sensitive files for indexing/completion.
- Suggested action: Apply the same `validate_path_segments()` (or stricter: must be relative, must resolve within project root) to `workspace_folder`.

### #4 [MEDIUM] `command` permits arbitrary absolute paths — only `..` traversal blocked
- File: `src/apm_cli/models/dependency/lsp.py:164`
- Lens(es): security
- Dissent weight: SOLE-IN-DOMAIN
- Detail: `validate_path_segments()` blocks `../` but permits any absolute path (`/bin/bash`, `/usr/bin/curl`, `/tmp/payload`). A malicious plugin can coerce Claude Code into launching arbitrary system binaries as an "LSP server". This is adjacent to the env-injection issue but distinct — fixing #1 does not fix this.
- Suggested action: Reject absolute paths in `command` by default. If absolute commands are required for some servers, require an opt-in flag and a per-binary allowlist.

### #5 [MEDIUM] TOCTOU between traversal guard and file read in plugin parser
- File: `src/apm_cli/deps/plugin_parser.py:467`
- Lens(es): security
- Dissent weight: SOLE-IN-DOMAIN
- Detail: Traversal check uses `(plugin_path / rel_path).resolve()` for safety validation, but the subsequent read opens the unresolved candidate path. An attacker with write access to the plugin directory can swap a symlink between the two operations, bypassing the guard.
- Suggested action: Open and read the **resolved** path (or `open()` the file handle once and reuse it). Alternatively, use `os.open` with `O_NOFOLLOW` on the final segment.

### #6 [MEDIUM] Integer fields use `or` — silently drops the value `0`
- File: `src/apm_cli/models/dependency/lsp.py:1605`
- Lens(es): correctness
- Dissent weight: SOLE-IN-DOMAIN
- Detail: `startup_timeout`, `shutdown_timeout`, and `max_restarts` are parsed with `d.get('startupTimeout') or d.get('startup_timeout')`. A user explicitly setting `maxRestarts: 0` (meaning "never restart") short-circuits through `or` and falls back to the snake_case key (usually `None`), silently discarding the intent. `restart_on_crash` already uses the correct `is not None` idiom — apply the same pattern to these three fields.
- Suggested action: Replace with `d['startupTimeout'] if 'startupTimeout' in d else d.get('startup_timeout')` (and equivalents).

### #7 [MEDIUM] LSP integration gated on `should_install_mcp` couples two independent features
- File: `src/apm_cli/commands/install.py:539`
- Lens(es): correctness
- Dissent weight: SOLE-IN-DOMAIN
- Detail: `run_lsp_integration(..., should_install=should_install_mcp)` ties LSP execution to the MCP gate. Today this happens to work, but it (a) prevents a future `--only=lsp` / `--only=mcp` from cleanly separating the two and (b) means any future reason to disable MCP also silently disables LSP. LSP and MCP are documented as separate dependency kinds; their gates should be independent.
- Suggested action: Introduce `should_install_lsp` derived from the same `--only`/`--skip` logic as MCP, and pass it through.

### #8 [MEDIUM] Redundant lockfile disk-read on every install (LSP + MCP each re-parse)
- File: `src/apm_cli/integration/_shared.py:36` (and `src/apm_cli/integration/lsp_integrator.py:216`)
- Lens(es): performance
- Dissent weight: SOLE-IN-DOMAIN (clustered with the analogous `update_lockfile` re-read at lsp_integrator.py:216 — both are the "lockfile re-parsed when already in memory" pattern)
- Detail: `resolve_locked_apm_yml_paths` calls `LockFile.read(lock_path)` unconditionally, even though `run_lsp_integration` already holds the parsed lockfile as `existing_lock`. `LSPIntegrator.update_lockfile` repeats the same pattern (up to twice per install). Each call is a redundant file-read + YAML-parse (+ write for the latter).
- Suggested action: Thread the already-parsed `LockFile` through `resolve_locked_apm_yml_paths` and `update_lockfile` as an optional argument; fall back to disk read only when absent.

## Methodology note
Clusters were formed on (file, code region) tuples — same file plus either same line or same field/symbol (e.g., `initialization_options` at lines 33 and 1601 collapsed into one region). Within a cluster, severity is the MAX across lenses; cross-lens reinforcement (≥2 lenses, even with different framings) promotes the cluster one level — applied once, to the `initialization_options` cluster (MEDIUM→HIGH). Dissent weighting kept all sole-lens security findings at face value because RCE/path-traversal/TOCTOU are squarely in the security lens's domain; no out-of-domain discounts were applied (the lone style finding stayed LOW on its own merits). The CRITICAL threshold required HIGH-or-above post-promotion **plus** an exploitable RCE / data-loss / happy-path-broken qualifier; only the unvalidated `env` dict cleared the bar (LD_PRELOAD → arbitrary code execution at LSP-spawn time). The promoted `initialization_options` cluster is HIGH but capped there since the exploit path requires additional server-side cooperation. The top-8 inline list is ranked by (severity_rank, dissent_weight, specificity); MEDIUM ties were broken in favour of higher-blast-radius security/correctness issues over test-coverage gaps.
