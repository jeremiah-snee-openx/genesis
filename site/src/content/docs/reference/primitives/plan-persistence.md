---
title: 6. Plan Persistence
description: A stable artifact holding the active plan, todos, and checkpoints across turns and across spawns.
sidebar:
  order: 7
  label: Plan Persistence
---

A stable artifact (file or structured store) holding the active plan, todos, and checkpoints across turns and across spawns. The cure for attention decay over long sessions.

**INDUSTRY TERMS:** "plan.md", "TODO state", "checkpoints", "session store".

**WHEN TO USE:** any work that is multi-step, multi-file, or spawn-bound. Without a persisted plan, long sessions silently drop earlier decisions and constraints; with one, every re-grounding event (start of a step, return from a spawn, after a tool failure) is a chance to recover.

**KEY PROPERTY:** the plan must be RELOADED at re-grounding boundaries. A written-once-never-read plan is dead weight. The discipline is **write-then-reload, not write-then-trust-recall**.

## See also

- [Child-Thread Spawn](/genesis/reference/primitives/child-thread-spawn/) -- spawns are the canonical re-grounding boundary; reload the plan on entry and on return.
- The B4 Plan Memento and B8 Attention Anchor design patterns will be cross-linked from the Reference catalogue once published.
