---
name: create-readme
description: "Trigger: README, crear README, mejorar README, onboarding del repo. Crea o reescribe el README principal con claridad."
license: MIT
metadata:
  author: github/awesome-copilot
  version: "1.0"
  scope: [root]
  auto_invoke:
    - "Create or rewrite project README"
    - "Improve repository README"
---

## Activation Contract

Load this skill when the user asks to create, rewrite, improve, or restructure the repository's main `README.md`.

## Hard Rules

- Keep README as onboarding, not the whole documentation system.
- Verify the actual repo tree before claiming setup, runnable product, folders, scripts, or features.
- For Juanchito, distinguish verified current state from target architecture.
- Link to deeper docs instead of duplicating architecture, ADRs, RLS, ML, or operations detail.
- Do not replace useful existing README content blindly; restructure when possible.

## Decision Gates

| Situation | Action |
|---|---|
| Main README requested | Use this skill. |
| Broader docs requested | Use `documentation-writer`. |
| Repo is not fully runnable | State that clearly. |
| Existing README is salvageable | Improve/restructure, do not rewrite from zero. |

## Execution Steps

1. Inspect `README.md`, `AGENTS.md`, and relevant `docs/` entry points.
2. Verify actual directories/scripts before documenting them.
3. Prioritize: what it is, current status, setup/use, repo structure, next docs.
4. Keep prose concise and navigation-focused.
5. Update navigation docs consistently when repo guidance changes.

## Output Contract

Return the README changes, verified repo-reality notes, and any follow-up docs that should be updated.

## References

- `assets/upstream-notes.md` — origin and local adaptation notes.
