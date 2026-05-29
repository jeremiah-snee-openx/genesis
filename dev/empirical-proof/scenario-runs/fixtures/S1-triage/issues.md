# Issue triage queue (fixture)

Eight inbound GitHub issues for triage. Each gets six lens reads
(severity, scope, owner-team, dup-check, repro-quality, label-set).

---

## Issue #4101 — "CLI hangs forever on `apm install` with offline cache"

Repro: `apm install --offline` after `apm cache prune`. Logs show
"resolving deps..." then nothing. Strace confirms blocked on AF_INET
connect to registry.npmjs.org even with `--offline`. Affects v0.4.0+
on macOS 14, Linux 6.6. Workaround: `--offline --no-resolve` (undoc).

## Issue #4102 — "Typo in --help: 'recieved'"

Output of `apm install --help` shows "Number of packages recieved".
Should be "received". Cosmetic only.

## Issue #4103 — "Memory leak in MCP server when re-loading large skill"

Memory grows ~150MB per skill reload. After 12 reloads OOM-killed.
heapdump shows retained refs in `SkillLoader._cache.weakSet`. Repro
on Node 20.11, MCP server v1.2.3. Filed by enterprise customer with
SLA.

## Issue #4104 — "Add `apm doctor` command"

Feature request: equivalent of `npm doctor` / `brew doctor`. Should
check: node version, registry reachability, cache write perms,
installed skill manifest integrity. ~25 thumbs-up.

## Issue #4105 — "RCE via crafted skill manifest in `apm install`"

Reporter (security researcher, has CVE history): malicious skill
package with shell metacharacters in `postinstall` field executes
arbitrary code as user. PoC attached. CVSS 9.1. Embargo until fix.

## Issue #4106 — "Docs link returns 404"

`https://apm.dev/docs/skills/persona-scoping` returns 404. Should be
`/docs/skills/persona`. Stale link in README of `apm-guide@1.4`.

## Issue #4107 — "Sub-agent dispatch double-charges tokens on retry"

After transient 529 from upstream, sub-agent dispatch retries and
both attempts are billed. Reproducible with `task(agent_type=...)`
followed by `--simulate-529`. Cost impact ~2x on retry-prone runs.

## Issue #4108 — "Windows path with spaces breaks `apm uninstall`"

`apm uninstall "C:\Program Files\My Skill"` errors with
`ENOENT: 'C:\Program'`. Argument quoting lost somewhere in CLI
parser. Affects Windows only; macOS/Linux fine.
