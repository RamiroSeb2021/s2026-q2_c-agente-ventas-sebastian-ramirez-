---
name: engram-context-sync
description: "Trigger: Engram sync, cambiar de computadora, .engram, import/export. Sincroniza contexto sin tocar la DB viva."
license: Apache-2.0
metadata:
  author: gentleman-programming
  version: "1.0"
  scope: [root]
  auto_invoke:
    - "Synchronize Engram context across computers"
    - "Start Juanchito work after switching machines"
    - "Version or troubleshoot .engram project context"
---

## Activation Contract

Load this skill when starting Juanchito work on another computer, syncing `.engram/`, running Engram import/export, or handling `topic_key` conflict risk.

## Hard Rules

- Never sync `~/.engram/engram.db` between computers.
- Treat `repo/.engram/` as the versionable transport layer only.
- Before deep work on a different machine, confirm `git pull` and `engram sync --import`.
- If the user is unsure about import status, stop deep work and ask them to sync first.
- Do not blindly upsert the same `topic_key` after parallel work; merge first.

## Decision Gates

| Scenario | Action |
|---|---|
| New machine, same repo | `git pull` → `engram sync --import` → status check. |
| End of work block | `engram sync` → commit/push `.engram/` if requested. |
| Full backup/migration | Use `engram export` / `engram import`. |
| Parallel edits to same topic | Save temporary topic, compare, merge, then update canonical topic. |
| Continuity uncertain | Ask the sync question before continuing. |

## Execution Steps

1. Check whether `.engram/manifest.json` exists.
2. Confirm import status with the user when continuity matters.
3. Use `.engram/` for repo transport; keep live DB local.
4. For conflicts, preserve both versions before consolidating.
5. Document any final sync/commit instructions clearly.

## Output Contract

Return sync status, commands run or required, conflict risk, and next safe action.

## References

- `assets/conflict-playbook.md` — conflict handling.
- `assets/session-checklist.md` — start/end session checklist.
