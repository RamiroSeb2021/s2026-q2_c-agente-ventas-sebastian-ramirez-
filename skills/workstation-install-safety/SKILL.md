---
name: workstation-install-safety
description: "Trigger: install, clone, run repo, dependencies, caches, Docker, Neovim, dotfiles. Decide safe workstation placement first."
license: Apache-2.0
metadata:
  author: gentleman-programming
  version: "1.0"
  scope: [root]
  auto_invoke:
    - "Start Juanchito work after switching machines"
    - "Install local workstation tools"
    - "Install, clone, or run a repo"
    - "Move caches, Docker data, models, datasets, or dotfiles"
allowed-tools: Read, Bash, Glob, Grep
---

## Activation Contract

Load this skill before installing software, cloning/running repos, setting up local tools, moving caches, configuring Docker storage, or deciding where workstation data should live.

## Hard Rules

- Do not run install, clone, move, format, mount, `sudo`, `curl | sh`, or destructive cleanup until preflight is complete.
- Verify real system state before changing paths, caches, Docker data, mounts, dependencies, or active repos.
- Prefer project-local installs and copy/sync plus verification before replacing paths.
- Never delete backups under `/storage/backups` unless the user explicitly approves after verification.
- Stop if `/mnt/nvme-dev` approaches 40 GB free.
- If package install or supply-chain risk appears, load `dependency-supply-chain-security` before install.

## Decision Gates

| Item | Destination / action |
|---|---|
| Active repos | `/mnt/nvme-dev/projects`, optionally symlinked from `~/trabajo`. |
| High-churn caches | `/mnt/nvme-dev/cache` only when useful. |
| Heavy virtual envs | `/mnt/nvme-dev/venvs` for selected envs. |
| Docker data | `/mnt/nvme-dev/docker` only after migration plan. |
| Small active ML assets | `/mnt/nvme-dev/models-active` or `datasets-active`. |
| Cold backups/large assets | `/storage`. |
| Lightweight user config | `$HOME`. |

## Execution Steps

1. Identify the install/move category and choose the destination with rollback.
2. Run read-only checks first: `df -h`, `findmnt /mnt/nvme-dev`, `lsblk -o NAME,SIZE,FSTYPE,LABEL,MOUNTPOINTS,MODEL`, relevant `du -sh`, destination existence checks, and repo status.
3. For dependencies, detect lockfiles and prefer reproducible commands.
4. For scripts or repos from links, read instructions/scripts before execution and identify write paths.
5. Execute only the smallest safe step, then verify result and space.

## Output Contract

Return chosen destination, verification performed, command run/proposed, rollback, remaining risk, and required user confirmation.

## References

- `../../AGENTS.md` — Juanchito workstation, Engram sync, and supply-chain rules.
- `../dependency-supply-chain-security/SKILL.md` — dependency install hardening.
