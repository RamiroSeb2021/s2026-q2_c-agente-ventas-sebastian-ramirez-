---
name: find-skills-copy-local
description: "Trigger: buscar skill pública, instalar skill, npx skills, vendorizar skill. Copia skills externas al repo con trazabilidad."
license: Apache-2.0
metadata:
  author: gentleman-programming
  version: "1.0"
  scope: [root]
  auto_invoke:
    - "Find and install public skills locally"
    - "Copy external skills into repo"
    - "Search skills.sh or npx skills for a skill"
---

## Activation Contract

Load this skill when searching public skills, installing skills with `npx skills`, or copying/vendorizing an external skill into Juanchito's `skills/` tree.

## Hard Rules

- Separate discovery, quality review, installation, and local integration.
- Do not recommend or copy a skill just because search found it.
- Prefer project-local copy when the result must be versioned in this repo.
- Preserve origin, author, and license information; do not silently claim upstream work.
- After local adaptation, run `skill-sync` when metadata affects `AGENTS.md`.

## Decision Gates

| Case | Action |
|---|---|
| User wants exploration only | Run/search with `npx skills find`. |
| Good skill, no repo adaptation | Install global or project-local as appropriate. |
| Skill must be versioned | Install/copy into `skills/{name}/`. |
| Skill needs Juanchito conventions | Adapt frontmatter/body, register, sync. |
| No suitable skill exists | Propose creating a local skill. |

## Execution Steps

1. Clarify the real need before searching.
2. Search public skills and evaluate source, adoption, repo reputation, and fit.
3. Install project-local with copy when versioning is needed.
4. Validate location with `npx skills list --json` or repo inspection.
5. Normalize to Juanchito style and sync metadata if needed.

## Output Contract

Return candidates considered, chosen source, files copied/adapted, provenance notes, and sync/setup commands run or required.

## References

- `assets/design.md` — local integration design notes.
