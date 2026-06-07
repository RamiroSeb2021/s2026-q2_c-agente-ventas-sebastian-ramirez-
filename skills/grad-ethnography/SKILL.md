---
name: grad-ethnography
description: "Trigger: etnografía, netnografía, thick description, validación contextual. Analiza prácticas y cultura situada."
license: Apache-2.0
metadata:
  author: gentleman-programming
  version: "1.0"
  scope: [root]
  auto_invoke:
    - "Analizar comportamiento de usuarios desde antropología o etnografía"
    - "Agregar validación contextual o cultural a una propuesta"
---

## Activation Contract

Load this skill when studying users or communities through ethnography, netnography, participant observation, thick description, emic/etic analysis, or cultural validation.

## Hard Rules

- Do not call short interviews “ethnography”; true ethnographic validity requires prolonged engagement.
- Distinguish observed behavior from interpretation.
- Use emic categories before imposing etic frameworks.
- Include reflexivity: researcher position shapes access and interpretation.
- Treat online communities ethically; public visibility is not automatic consent.

## Decision Gates

| Situation | Action |
|---|---|
| Need cultural meaning/practice | Use ethnographic framing. |
| Need causal measurement | Use another method; ethnography is not causal proof. |
| Only survey/interview data exists | Call it qualitative insight, not full ethnography. |
| Online community | Apply netnography and consent/privacy checks. |

## Execution Steps

1. Define field site, access, role, duration, and ethical constraints.
2. Capture practices, language, norms, tensions, and power relations.
3. Separate descriptive notes, reflective interpretation, and methodological decisions.
4. Produce thick description with behavior plus context plus meaning.
5. State implications, limits, and validation needs.

## Output Contract

Return field context, cultural themes, thick description, power/reflexivity notes, implications, and method limitations.

## References

- `../xai-proposal-orchestrator/SKILL.md` — related orchestration skill for ML/XAI proposals.
