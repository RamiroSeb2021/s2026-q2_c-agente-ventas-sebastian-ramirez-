# Repository Guidelines

## What this project is

- State the project in one sentence.
- Name the current domain, users, and non-goals if known.
- Distinguish product/system names from agent names when they overlap.

## Repo Reality

- Describe what exists in the tree today.
- Describe what is documentation, scaffold, configuration, or runnable implementation.
- Use: **Documented ≠ implemented** when docs are ahead of code.

## How to interpret this repo

Use this taxonomy before making claims:

- **Verified current state**: present in the tree and inspected.
- **Target design**: documented architecture or intended behavior, not necessarily implemented.
- **Planned / future**: roadmap or proposal work that depends on later implementation.

## Documentation entrypoints

| Topic | Source of truth |
|------|-----------------|
| Overview | `README.md` |
| Architecture | `docs/...` |
| Operations | `docs/...` |
| Decisions | `docs/...` |

## Repository map

```text
src/        Application code, if present
scripts/    Operational or local scripts, if present
docs/       Project documentation
AGENTS.md   Agent-facing repository instructions
README.md   Human-facing project introduction
```

## Rules for assistants

- Verify tree state before claiming a file, script, endpoint, table, or feature exists.
- Ask whether the user wants docs, scaffold, or real implementation when ambiguous.
- Surface contradictions with file evidence instead of silently choosing one source.
- Preserve user constraints and project safety rules.
- Avoid destructive git, filesystem, database, email, cloud, or publishing operations without explicit approval.

## Branching and review policy

- State branch dependency rules if the repo has stacked work.
- State when to split changes or ask before large diffs.
- Never commit unless explicitly asked.

## Learning or collaboration mode

- Capture project-specific teaching style, review style, language preference, or design mode.
- Explain concepts before large code blocks when the user is learning.

## Skills Reference

Use local skills when applicable:

| Skill | When to use it | Path |
|-------|----------------|------|
| `skill-name` | Trigger condition | `skills/skill-name/SKILL.md` |

## Auto-invoke Skills

When performing these actions, invoke the corresponding skill first:

| Action | Skill |
|--------|-------|
| Create or rewrite AGENTS.md | `create-agents-md` |

## Tooling / Sync

- List safe discovery commands first.
- Separate commands that mutate files or external state.
- Include setup/sync commands only after verifying they exist.

## Verified Commands

### Safe / lightweight

```bash
git status --short
git ls-files
```

### Mutating or situational

```bash
# Add only commands that were verified and clearly labeled.
```

## Security / hard blocks

- List absolute prohibitions and sensitive systems.
- Include allowed non-destructive alternatives.

## Gotchas

- Capture non-obvious repo facts that prevent future agent mistakes.
- Mention generated files, derived instructions, or docs that are often mistaken for implementation.
