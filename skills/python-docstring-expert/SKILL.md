---
name: python-docstring-expert
description: "Trigger: Python docstrings, documentar código Python, revisar docstrings. Crea docstrings útiles sin sobredocumentar."
license: Apache-2.0
metadata:
  author: zenless-lab; adapted-for-juanchito-by-gentleman-programming
  version: "1.0"
  scope: [root]
  auto_invoke:
    - "Document Python code"
    - "Add or update Python docstrings"
    - "Review Python documentation quality"
---

## Activation Contract

Load this skill when creating, updating, or reviewing Python docstrings for modules, classes, public functions, methods, or changed code whose documentation may be stale.

## Hard Rules

- Document to add value, not noise; docstrings that repeat names are debt.
- Public APIs and complex logic need docstrings; simple private helpers usually do not.
- If code changes signature, return, exceptions, or responsibility, update the docstring in the same change.
- Prefer PEP 257: concise summary, blank line for details, imperative voice, final punctuation.
- Put constructor parameters in the class docstring unless the project has a different convention.

## Decision Gates

| Situation | Decision |
|---|---|
| Public API | Add or update docstring. |
| Class used by other modules | Add class docstring. |
| Simple private function | Omit docstring or use a focused comment. |
| Recursive/nested/non-obvious logic | Add docstring. |
| Docstring contradicts code | Fix or remove it. |
| Example would clarify non-obvious usage | Add minimal example/doctest. |

## Execution Steps

1. Inspect code responsibility and public/private exposure.
2. Decide whether a docstring is warranted before writing.
3. Update stale docstrings whenever code behavior changed.
4. Use templates only when they clarify arguments, returns, exceptions, or examples.
5. Keep examples minimal; tests still belong in tests.

## Output Contract

Return docstrings added/updated/removed, rationale for omissions, and any code-doc mismatches fixed.

## References

- `references/evaluation.md` — when to write docstrings.
- `references/components.md` — module/class/function rules.
- `references/formatting_and_tone.md` — formatting and voice.
- `assets/module_templates.py` — module examples.
- `assets/class_templates.py` — class examples.
- `assets/function_templates.py` — function examples.
