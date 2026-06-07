---
name: pi-secure-package-install
description: "Trigger: pi install npm, Pi package install, install Pi extensions. Resolve npm versions and install Pi packages pinned."
license: Apache-2.0
metadata:
  author: gentleman-programming
  version: "1.0"
  scope: [root]
  auto_invoke:
    - "Install Pi npm packages"
    - "Install Pi extensions from npm"
    - "Resolve latest Pi package versions safely"
    - "Update Pi package install commands"
allowed-tools: Read, Bash, Edit, Write
---

## Activation Contract

Load this skill when installing, updating, or rewriting `pi install npm:` commands for Pi packages, extensions, skills, themes, prompt templates, or agent tooling.

## Hard Rules

- Do not install npm Pi packages unpinned, even when the user writes `npm:pkg` without a version.
- Resolve the current npm version with `npm view <pkg> version`, then install `npm:<pkg>@<version>`.
- Preserve the user's requested scope: global by default; project-local only when they ask for `-l`, `--local`, or shared project settings.
- Treat Pi packages as executable tooling with full system access; surface deprecation, install, or package-resolution warnings.
- Do not run destructive cleanup, `pi remove`, or `pi update` without explicit user approval.

## Decision Gates

| Situation | Action |
|---|---|
| User provides unpinned `npm:pkg` | Resolve latest version and install pinned `npm:pkg@x.y.z`. |
| Package is already installed unpinned | Install pinned version; report the legacy unpinned entry if `pi list` still shows it. |
| npm cannot resolve a package | Stop and report the unresolved package; do not guess names. |
| User insists on `latest` | Decline unpinned install and offer automatic pin resolution. |

## Execution Steps

1. Extract all `npm:` package specs and detect global vs local scope.
2. Run `npm view <pkg> version` for each unpinned package; keep already pinned specs unchanged.
3. Run `pi install npm:<pkg>@<version>` with `-l` only when requested.
4. Verify with `pi list` and report installed versions plus warnings.

## Output Contract

Return the resolved install commands, verification result, any warnings, and whether repo files changed.

## References

- `../../AGENTS.md` — Juanchito supply-chain hardening rules for npm/Pi tooling.
