---
name: descriptive-commits
description: 'Trigger: commit message, mensaje de commit, mejorar mensaje. Draft commit messages only; never stage or commit.'
license: Apache-2.0
metadata:
  author: gentleman-programming
  version: 1.0
  scope: [root]
  auto_invoke:
    - "When user asks for a commit message"
    - "When user asks to rewrite or improve a commit message"
---

## Activation Contract

Load this skill only when the user asks to draft, rewrite, improve, or explain a commit message without executing Git changes.

## Hard Rules

- Never stage files, create commits, amend commits, or mutate Git state.
- If the user asks to execute a commit, hand off to `guardiania-smart-commit`.
- Always inspect real `git status`, staged diff, unstaged diff, and recent commit style before drafting.
- Use a conventional commit title plus a descriptive body.
- The body MUST explain what was created, modified, removed, or fixed; what changed; and the purpose behind the change.
- Never include AI attribution, `Co-Authored-By`, or tool-generated signatures.

## Decision Gates

| Situation | Action |
|---|---|
| User asks for a message only | Return title and body; do not stage or commit. |
| User asks to commit/stage/amend | Stop and invoke `guardiania-smart-commit`. |
| Multiple work units exist | Propose separate commit messages by topic. |
| Unrelated/sensitive files exist | Warn that they should not be included. |

## Execution Steps

1. Run Git state checks: status, staged/unstaged diff, and recent log.
2. Identify the coherent work unit and excluded files.
3. Draft the title using Conventional Commits.
4. Draft the body using `assets/commit-body-template.md`.
5. Return the message only; do not stage or commit.

## Output Contract

Return the proposed commit title/body, suggested topic split when useful, and files that should be included/excluded.

## References

- `assets/commit-body-template.md` — required descriptive body structure.
