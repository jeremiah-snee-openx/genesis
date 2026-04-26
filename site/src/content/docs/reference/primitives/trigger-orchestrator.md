---
title: 5. Trigger Orchestrator
description: A declarative pipeline that spawns sessions in response to events.
sidebar:
  order: 6
  label: Trigger Orchestrator
---

A declarative pipeline that spawns sessions in response to events (schedule, push, comment, label, manual). Lives ABOVE the thread, deciding when work begins and what initial context it carries.

**INDUSTRY TERMS:** "workflow", "hook", "automation", "trigger".

**WHEN TO USE:** cross-session work where a stimulus (PR opened, file changed, time elapsed) needs to start an agent run with predefined inputs and an upstream-side filter.

**KEY PROPERTY:** it is the only primitive whose execution surface is fully declarative. It does not carry a context window itself; it dispatches others that do.

## See also

- [Module Entrypoint](/genesis/reference/primitives/module-entrypoint/) -- substrate-invoked binding mode is what triggers dispatch.
- [Child-Thread Spawn](/genesis/reference/primitives/child-thread-spawn/) -- triggers spawn child threads, never carry their own.
- A trigger surface example (gh-aw / GitHub Agentic Workflows) and its substrate fields (SANDBOXING / CAPABILITY_GATING / AUDIT_SURFACE) will be cross-linked from the Reference catalogue once published.
