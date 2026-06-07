---
name: humanize-writing
description: "Trigger: humanizar texto, bajar tono robótico, pulir borrador IA. Mejora naturalidad sin perder precisión ni intención."
license: Apache-2.0
metadata:
  author: gentleman-programming
  version: "1.0"
  scope: [root]
  auto_invoke:
    - "Humanizar o pulir un borrador escrito por IA"
    - "Bajar tono robótico o rígido sin perder precisión"
---

## Activation Contract

Load this skill when text is correct but sounds rigid, generic, over-polished, repetitive, or obviously AI-shaped.

## Hard Rules

- Preserve meaning, precision, claims, limits, and nuance.
- Do not invent personal experience, emotions, anecdotes, citations, or evidence.
- Do not make serious text artificially casual.
- Improve editorial quality; do not frame the work as detector evasion.
- If the original is vague or unsupported, ask/flag before polishing.

## Decision Gates

| Problem | Action |
|---|---|
| Minor stiffness | Light edit: remove filler and smooth rhythm. |
| Repetitive structure | Moderate edit: vary cadence and transitions. |
| Weak paragraph logic | Strong edit: rebuild paragraphs while preserving intent. |
| Missing evidence or unclear claim | Flag content issue before humanizing. |

## Execution Steps

1. Identify text type, audience, register, and intervention level.
2. Separate content problems from prose problems.
3. Remove filler, generic corporate phrasing, false transitions, and mechanical symmetry.
4. Vary rhythm while keeping logical control.
5. Audit that facts, promises, scope, and limits did not change.

## Output Contract

Return `Diagnóstico`, `Versión revisada`, and `Cambios clave` with what was removed, varied, clarified, and preserved.

## References

- `assets/editorial-checklist.md` — detailed editorial checklist.
