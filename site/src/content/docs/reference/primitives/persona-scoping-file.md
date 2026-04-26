---
title: 1. Persona Scoping File
description: A markdown document loaded at session start to scope WHO the agent is.
sidebar:
  order: 2
  label: Persona Scoping File
---

A markdown document loaded at session start to scope WHO the agent is. Sets voice, expertise lens, hard constraints, anti-patterns it flags. It has no execution life of its own -- it is text loaded into a context window.

**INDUSTRY TERMS:** "agent file", "subagent definition", "mode", "AGENTS.md".

**WHEN TO USE:** any time a body of work benefits from a stable lens (a domain expert, a reviewer voice, an arbitrator persona).

**KEY PROPERTY:** orthogonal to threads. A persona is loaded INTO a thread. A thread is not a persona. Conflating the two is the most common error in this domain.

## See also

- [Child-Thread Spawn](/genesis/reference/primitives/child-thread-spawn/) -- the runtime that personas are loaded into.
- [Module Entrypoint](/genesis/reference/primitives/module-entrypoint/) -- the unit of REUSE; can compose with personas.
- Per-harness paths and frontmatter for persona files: [Harness setup](/genesis/reference/harnesses/).
