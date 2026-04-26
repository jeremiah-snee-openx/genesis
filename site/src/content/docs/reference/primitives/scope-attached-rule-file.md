---
title: 3. Scope-Attached Rule File
description: A constraint that auto-applies whenever the agent operates on a matching path or context.
sidebar:
  order: 4
  label: Scope-Attached Rule File
---

A constraint that auto-applies whenever the agent operates on a matching path or context. Cross-cutting rules ride along instead of needing to be re-stated in every persona.

**INDUSTRY TERMS:** "instruction file", "rule", "memory", "always-load".

**WHEN TO USE:** invariants that must hold across many capabilities (encoding rules, secret-handling, project-specific style) -- attach to the path or glob they govern.

**KEY PROPERTY:** the harness controls when these load (path match, file match). The author does not call them; the runtime injects them.

## See also

- [Persona Scoping File](/genesis/reference/primitives/persona-scoping-file/) -- personas declare WHO; rules declare WHAT INVARIANTS hold.
- Per-harness rule file paths and frontmatter dialects: [Harness setup](/genesis/reference/harnesses/).
