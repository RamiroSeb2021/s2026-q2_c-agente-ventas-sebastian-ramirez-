---
name: guardiania-smart-commit
description: 'Trigger: has el commit, haz el commit, guardar cambios en Git. Crea commits de Juanchito con staging por tema y cuerpo detallado.'
license: Apache-2.0
metadata:
  author: gentleman-programming
  version: 1.0
  scope: [root]
  auto_invoke:
    - "has el commit"
    - "haz el commit"
    - "When user asks to commit or save changes in Git"
    - "When user asks for a commit message with title and detailed description"
---

## Activation Contract

Load this skill when the user says `has el commit`, `haz el commit`, asks to commit/save Git changes, or asks for a detailed commit message for Juanchito. The inherited skill name stays stable until dependent metadata/scripts are migrated.

## Hard Rules

- Never commit without an explicit user request.
- Always inspect `git status`, `git diff`, and staged diff before committing.
- Do not include secrets or unrelated files.
- Use a short English conventional title plus a highly descriptive body explaining what changed, where it changed, and why it changed.
- Base the message on the real diff; do not invent tests, files, or implementation details.
- Keep the title <=72 characters, body lines <=100 characters, and total commit message <=1200 characters.
- If one message would exceed 1200 characters or mix unrelated themes, split by topic and stage/commit each topic separately when safe.
- Do not add AI attribution or `Co-Authored-By` lines.

## Decision Gates

| Case | Action |
|---|---|
| User asks only for message | Propose title/body; do not commit. |
| User says `has el commit` / `haz el commit` | Review diff, stage by topic, commit. |
| Message exceeds 1200 chars | Categorize themes and create separate commit messages. |
| Multiple coherent topics | Stage and commit each topic separately. |
| Topic split is ambiguous | Recommend split and ask before staging. |
| `.engram/` changed | Include only if part of requested work/sync. |
| Unrelated files present | Warn and suggest separate commit. |
| Sensitive-looking files | Stop and ask before staging. |

## Execution Steps

1. Inspect working tree and staged/unstaged diffs.
2. Categorize changed files into coherent topics: docs, skills, tests, code, config, data/context.
3. Estimate whether one detailed message fits the character limits and one theme.
4. If needed, split into topic commits and stage only files/hunks for the current topic.
5. Draft each message with `assets/commit-message-template.md`, covering changes, rationale, related docs, safety/scope, and verification.
6. Commit after staging the relevant topic when the user requested `has el commit`/`haz el commit`.
7. Report commit hash(es), included/excluded files, and remaining status.

## Output Contract

Return the commit title/body or commit hash(es), topic split, included/excluded files, and post-commit status.

## References

- `assets/commit-message-template.md` — commit message template.
