---
name: create-agents-md
description: "Trigger: AGENTS.md, agent guidelines, repository instructions. Create or rewrite AGENTS.md from repo evidence and examples."
license: Apache-2.0
metadata:
  author: gentleman-programming
  version: "1.0"
  scope: [root]
  auto_invoke: "Create or rewrite repository AGENTS.md"
---

## Activation Contract

Load this skill when creating, rewriting, or auditing a repository-level `AGENTS.md` for coding agents.

## Hard Rules

- Treat `AGENTS.md` as runtime guidance for agents, not a project README.
- Base every project-specific claim on inspected files; mark future plans as planned, target design, or unknown.
- Preserve hard safety rules, destructive-operation bans, verified commands, and source-of-truth docs.
- Keep the final file scannable with short sections, tables, and command blocks.
- Do not copy another repo's domain facts; copy only structure, tone, and reusable patterns.

## Decision Gates

| Situation | Action |
|---|---|
| Repo has no clear implementation | State repo reality and avoid runnable claims. |
| Docs describe more than files show | Separate documented design from verified current state. |
| Existing `AGENTS.md` exists | Preserve valid local rules before rewriting structure. |
| No verified commands found | Add only safe discovery commands and label others unknown. |

## Execution Steps

1. Read root files, docs entrypoints, config, scripts, and any existing `AGENTS.md`.
2. Build a repo map: purpose, current reality, source-of-truth docs, assistant rules, safety constraints, commands, and gotchas.
3. Draft using `assets/AGENTS-TEMPLATE.md`; adapt headings to the repo and remove irrelevant sections.
4. Validate each factual claim against the tree; downgrade uncertain claims to planned/unknown.
5. If changing docs navigation, update README first unless the user explicitly asks only for `AGENTS.md`.

## Output Contract

Return changed files, evidence inspected, assumptions kept, commands verified or not verified, and any sections intentionally omitted.

## References

- `assets/AGENTS-TEMPLATE.md` — starter structure modeled after a strong repository `AGENTS.md`.
- `references/agents-md-checklist.md` — evidence and quality checklist before final handoff.
