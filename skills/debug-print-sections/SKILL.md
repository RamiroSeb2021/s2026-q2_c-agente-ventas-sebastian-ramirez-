---
name: debug-print-sections
description: "Trigger: mejorar prints, debug output, logs temporales. Formatea salidas CLI por secciones legibles sin cambiar lógica."
license: Apache-2.0
metadata:
  author: gentleman-programming
  version: "1.0"
  scope: [root]
  auto_invoke:
    - "Mejorar prints o salidas de debug en scripts"
    - "Separar salida CLI por secciones legibles"
---

# Skill: debug-print-sections

## Activation Contract

Use this skill when improving temporary script output, exploratory prints, smoke-test output, or CLI debugging traces. Apply it especially to Python scripts that inspect APIs, datasets, emails, payloads, or intermediate rows.

## Hard Rules

- Preserve business logic unless the user explicitly asks for behavior changes.
- Do not hide exceptions; make failures easier to see.
- Group output by sections with stable titles.
- Prefer small helper functions over repeated `print("\n...")` blocks.
- Use `pprint(..., sort_dicts=False)` for nested dicts/lists that humans inspect.
- Keep labels in the user's language when the surrounding script already uses that language.

## Decision Gates

| Situation | Action |
|---|---|
| One value | Use `print_kv(label, value)` |
| Object metadata | Use a section title, then type/ids/important fields |
| Nested dict/list | Use `print_data(label, value)` with `pprint` |
| Optional content | Print a clear empty-state line, e.g. `Sin adjuntos` |
| Long API exploration | Separate setup, sample, attributes, attachments, row, API response |

## Execution Steps

1. Add compact helpers near the top of the script: `print_section`, `print_kv`, and optionally `print_data`.
2. Replace ad-hoc prints with titled sections.
3. Keep the original inspected values unless they are invalid or broken.
4. For dataset rows, print the row under a single section and preserve key order.
5. Validate with a syntax check or the lightest safe command available.

## Output Contract

Return:
- Which script output sections were added.
- Whether logic changed or only presentation changed.
- Any validation performed.

## References

- `scripts/gmail_lab/dataSetCreator.py` — current Gmail lab exploratory script.
