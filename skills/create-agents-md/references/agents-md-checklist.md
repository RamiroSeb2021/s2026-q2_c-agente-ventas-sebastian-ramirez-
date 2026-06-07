# AGENTS.md Checklist

Use this checklist before finalizing an `AGENTS.md`.

## Evidence checklist

- [ ] Root files inspected: `README.md`, existing `AGENTS.md`, config files, scripts, and docs index when present.
- [ ] Repository map matches actual folders in `git ls-files` / `find`.
- [ ] Runnable claims were verified with file evidence or command evidence.
- [ ] Future-looking architecture is labeled as target design or planned work.
- [ ] Source-of-truth docs are listed by topic, not as a generic dump.
- [ ] Safety constraints are explicit and hard to miss.
- [ ] Commands are split into safe/lightweight vs mutating/situational.
- [ ] Local skills and auto-invoke rules point to real paths when available.

## Quality checklist

- [ ] Agent-facing, not human onboarding prose.
- [ ] Short sections, bullets, tables, and command blocks.
- [ ] No copied domain facts from another repository.
- [ ] No hidden destructive permissions or ambiguous cleanup instructions.
- [ ] Clear rule for ambiguous user requests: docs vs scaffold vs implementation.
- [ ] Clear rule for `Documented ≠ implemented` when docs lead code.

## Handoff notes

Report what was inspected, what was intentionally left unknown, and which commands were not run. If `AGENTS.md` was generated from an example repository, name the example only as a structural influence, not as a factual source.
