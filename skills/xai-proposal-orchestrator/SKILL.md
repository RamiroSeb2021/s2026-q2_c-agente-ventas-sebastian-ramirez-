---
name: xai-proposal-orchestrator
description: "Trigger: propuesta ML/XAI, próximos pasos XAI, arquitectura futura, validación de usuarios. Orquesta propuesta técnica-académica."
license: Apache-2.0
metadata:
  author: gentleman-programming
  version: "1.0"
  scope: [root]
  auto_invoke:
    - "Estructurar próximos pasos de una propuesta de ML/XAI"
    - "Orquestar redacción académica + system design + roadmap + antropología"
---

## Activation Contract

Load this skill when structuring a machine learning/XAI proposal that needs academic framing, future architecture, roadmap, user validation, and operational behavior.

## Hard Rules

- Orchestrate base skills; do not replace them: `academic-writing`, `system-design`, `roadmap-propose`, `grad-ethnography`, `humanize-writing`.
- Start from the human problem, not the tooling.
- Describe ML/XAI behavior as data → prediction/recommendation → explanation → action → feedback → risk.
- Do not present infrastructure (Paperclip, OpenClaw, frameworks) as the core innovation.
- Be honest about what is proposed, validated, speculative, or pending.

## Decision Gates

| Main gap | Dominant lens |
|---|---|
| Weak academic argument | `academic-writing`. |
| Unclear architecture | `system-design`. |
| Vague next steps | `roadmap-propose`. |
| Missing user reality | `grad-ethnography`. |
| Robotic final prose | `humanize-writing`. |
| Mixed proposal problem | Use this orchestration skill. |

## Execution Steps

1. Frame problem, objective, contribution, and limits academically.
2. Map real user practices, language, and contextual validation needs.
3. Define expected ML/XAI behavior and failure risk.
4. Sketch the minimum architecture and key trade-offs.
5. Sequence next steps: data, validation, prototype, integration, evaluation.
6. Polish final prose only after argument and structure are coherent.

## Output Contract

Return academic justification, user/context lens, ML/XAI behavior table, minimal architecture, roadmap, risks, and claims that must not be made yet.

## References

- `../academic-writing/SKILL.md` — academic rigor.
- `../system-design/SKILL.md` — architecture and trade-offs.
- `../roadmap-propose/SKILL.md` — next-step sequencing.
- `../grad-ethnography/SKILL.md` — contextual validation.
- `../humanize-writing/SKILL.md` — final prose polish.
