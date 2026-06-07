---
name: documentation-writer
description: "Trigger: documentación técnica, how-to, reference, explanation, docs más allá del README. Escribe docs con enfoque Diátaxis."
license: MIT
metadata:
  author: github/awesome-copilot
  version: "1.0"
  scope: [root]
  auto_invoke:
    - "Write general project documentation"
    - "Create technical docs beyond README"
---

## Activation Contract

Load this skill when writing project documentation other than the main README: tutorials, how-to guides, technical references, explanations, architecture notes, or conceptual docs.

## Hard Rules

- Use Diátaxis deliberately: tutorial, how-to, reference, or explanation.
- Do not mix documentation modes into one chaotic document.
- Define audience, reader goal, scope included, and scope excluded before writing.
- Follow existing repo tone and vocabulary.
- Do not claim documented target architecture is implemented unless verified in the tree.

## Decision Gates

| Request | Action |
|---|---|
| Main `README.md` | Use `create-readme` instead. |
| Task completion guide | Write a how-to. |
| Exact API/command/schema facts | Write reference. |
| Concepts, trade-offs, rationale | Write explanation. |
| New user learning path | Write tutorial. |
| Ambiguous request | Ask for document type, audience, and goal. |

## Execution Steps

1. Classify the document type using Diátaxis.
2. Inspect relevant existing docs and repo reality before drafting.
3. Propose structure when scope is non-trivial.
4. Write clear Markdown with headings that match the chosen mode.
5. Link to deeper docs instead of duplicating long material.

## Output Contract

Return the document or patch summary, document type, audience, scope decisions, and any repo-reality caveats.

## References

- `assets/upstream-notes.md` — origin and local adaptation notes.
