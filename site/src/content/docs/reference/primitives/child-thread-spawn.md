---
title: 4. Child-Thread Spawn
description: A runtime affordance that creates a new execution unit with its own fresh context window.
sidebar:
  order: 5
  label: Child-Thread Spawn
---

A runtime affordance that creates a new execution unit with its OWN fresh context window. Returns a value to the parent. Multiple may run in parallel.

**INDUSTRY TERMS:** "subagent thread", "Task tool", "background agent".

**WHEN TO USE:** any work that benefits from CONTEXT ISOLATION -- a fresh window where a specialized lens (its own persona, its own rule set, its own loaded assets) sits at full attention rather than competing with the parent's session for tokens.

**KEY PROPERTY:** stateless across spawns. Anything not loaded as text into the child thread does not exist for that thread. Hand off via explicit artifacts, not assumed memory.

## Compounding gain

A [MODULE ENTRYPOINT](/genesis/reference/primitives/module-entrypoint/) that is dispatched in a fresh child thread converts a Separation-of-Concerns win into a context-isolation win for free. This is the core argument for splitting a god-module into specialized siblings -- each split unlocks an independently spawnable thread.

## See also

- [Module Entrypoint](/genesis/reference/primitives/module-entrypoint/) -- what runs inside the spawned thread.
- [Persona Scoping File](/genesis/reference/primitives/persona-scoping-file/) -- loaded into the spawn at startup.
- [Plan Persistence](/genesis/reference/primitives/plan-persistence/) -- the only safe handoff channel between parent and spawn.
