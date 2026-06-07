---
name: dependency-supply-chain-security
description: "Trigger: npm, pnpm, pip, dependency install, package audit, repo link, postinstall, supply chain. Review install risk first."
license: Apache-2.0
metadata:
  author: gentleman-programming
  version: "1.0"
  scope: [root]
  auto_invoke:
    - "Install dependencies"
    - "Install npm or pnpm packages"
    - "Install Python packages"
    - "Audit package or supply chain risk"
    - "Run dependency install with lifecycle scripts"
allowed-tools: Read, Bash, Glob, Grep
---

## Activation Contract

Load this skill before installing dependencies, cloning/running unfamiliar repos, executing package-manager commands, or publishing packages.

## Hard Rules

- Do not run install commands until package manager, lockfile, scripts, and trust boundary are inspected.
- Treat lifecycle scripts (`preinstall`, `install`, `postinstall`, `prepare`) as code execution.
- Prefer exact versions, frozen lockfiles, disabled scripts, and cooldown over `latest`.
- Do not switch package managers or delete old lockfiles without reviewing the diff.
- Never print secrets; assume install scripts can read env vars, SSH keys, npm tokens, and config files.
- Follow Juanchito hardening: no unpinned `npx`/`npm exec`, no `latest` for critical CLIs, and no third-party install scripts by default.

## Decision Gates

| Condition | Action |
|---|---|
| npm project | Require safe `.npmrc` where appropriate and prefer `npm ci --ignore-scripts`. |
| pnpm project | Prefer frozen lockfile, cooldown/minimum release age, and explicit build allowlist. |
| package has lifecycle scripts | Stop; explain risk and request explicit approval or use `--ignore-scripts`. |
| install uses `latest` | Replace with exact version or ask for approval. |
| lockfile has external URLs | Validate HTTPS and allowed registry hosts. |
| publishing npm package | Require OIDC/trusted publishing, provenance, 2FA, least permissions, and `files` allowlist. |

## Execution Steps

1. Inspect manifests and lockfiles: `package.json`, `.npmrc`, `pnpm-workspace.yaml`, lockfiles, Dockerfiles, and install docs.
2. Check scripts and dependency changes before installing.
3. Prefer safe commands: `npm ci --ignore-scripts`, `pnpm install --frozen-lockfile --ignore-scripts`, `uv sync --frozen`, or documented equivalents.
4. For new packages, check age/reputation where possible before install.
5. For pnpm, verify config support before adding security keys.
6. If scripts/builds are genuinely required, allow only specific packages and explain why.

## Output Contract

Return package manager, lockfile status, script risk, version/cooldown decision, command to run, blocked risks, and required user approval.

## References

- `../../AGENTS.md` — Juanchito supply-chain hardening rules.
- `../workstation-install-safety/SKILL.md` — workstation placement and install preflight.
