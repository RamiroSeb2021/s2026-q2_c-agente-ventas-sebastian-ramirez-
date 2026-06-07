---
name: academic-writing
description: "Trigger: redacción académica, propuesta formal, paper, tesis, revisión de literatura. Eleva estructura, tono y rigor académico."
license: Apache-2.0
metadata:
  author: gentleman-programming
  version: "1.0"
  scope: [root]
  auto_invoke:
    - "Redactar documentos académicos o propuestas formales"
    - "Elevar tono y rigor de una entrega universitaria"
---

## Activation Contract

Load this skill when drafting, restructuring, auditing, or polishing academic work: papers, proposals, theses, literature reviews, chapters, methodology, discussion, or conclusions.

## Hard Rules

- Fix argument structure before polishing sentences.
- Never invent citations, authors, journals, metrics, results, or evidence.
- Mark unsupported claims explicitly; downgrade or qualify them.
- Keep tone precise and rigorous, not inflated or grandiose.
- Separate what the work proposes, demonstrates, suggests, and leaves pending.

## Decision Gates

| Need | Action |
|---|---|
| Disordered text | Rebuild document architecture first. |
| Weak introduction | Use context → problem → gap → objective → contribution. |
| Literature list | Reorganize by themes, debates, gaps, and synthesis. |
| Unclear method | Check fit with objectives and replicability. |
| Superficial discussion | Separate findings, interpretation, implications, limits, future work. |
| Poor closing | Restate contribution and limits without overpromising. |

## Execution Steps

1. Identify document type, audience, expected level, and delivery constraints.
2. Verify problem, question, objective, contribution, evidence, and closing.
3. Reorder sections and paragraphs before line editing.
4. Improve precision, argumentative flow, and academic register.
5. Audit citations, claims, limits, and ethical honesty.

## Output Contract

Return the revised text plus concise notes on structure, claims/evidence gaps, tone changes, and any missing references.

## References

- `assets/imrad-outline.md` — IMRaD structure template.
- `assets/masters-writing-checklist.md` — quality checklist.
- `assets/peer-review-response-template.md` — reviewer response template.
- `assets/upstream-notes.md` — origin and adaptation notes.
