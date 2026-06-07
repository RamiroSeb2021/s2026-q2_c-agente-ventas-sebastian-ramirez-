---
name: roadmap-propose
description: "Trigger: roadmap, próximos pasos, fases, propuesta ejecutable. Convierte ideas planificadas en secuencia de trabajo."
license: Apache-2.0
metadata:
  author: gentleman-programming
  version: "1.0"
  scope: [root]
  auto_invoke:
    - "Estructurar roadmap o próximos pasos"
    - "Convertir una idea en propuesta ejecutable"
---

## Activation Contract

Load this skill when turning ideas, planned changes, milestones, or vague next steps into an executable roadmap or proposal.

## Hard Rules

- Produce planning artifacts only; do not implement product code.
- Sequence work by dependency, validation value, and risk.
- Do not invent testing commands or implementation mappings when repository evidence is unclear.
- Keep tasks independently completable and reviewable.
- Surface open questions before execution handoff.

## Decision Gates

| Situation | Action |
|---|---|
| Idea is vague | Clarify outcome, user, scope, and constraints. |
| Work is already planned | Promote it into proposal/tasks. |
| Dependencies unclear | Identify prerequisite phases first. |
| Validation missing | Add research/test/pilot step before build-out. |
| Commands unknown | Add open question instead of guessing. |

## Execution Steps

1. Identify target change, goal, constraints, and current planning context.
2. Break scope into phases with dependencies and success criteria.
3. Define implementation, testing/validation, verification, and open questions.
4. Keep roadmap items small enough to execute and review independently.
5. Offer the next execution handoff only after planning is coherent.

## Output Contract

Return roadmap phases, task breakdown, validation plan, risks, open questions, and recommended next handoff.

## References

- `../xai-proposal-orchestrator/SKILL.md` — related ML/XAI proposal orchestration.
