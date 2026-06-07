---
name: system-design
description: "Trigger: diseño de sistema, arquitectura, componentes, trade-offs, ADR. Produce diseños técnicos claros y verificables."
license: Apache-2.0
metadata:
  author: gentleman-programming
  version: "1.0"
  scope: [root]
  auto_invoke:
    - "Diseñar arquitectura o componentes de una propuesta"
    - "Evaluar trade-offs técnicos de una solución"
---

## Activation Contract

Load this skill when designing a system, major feature, migration, ADR, component boundary, interface, data model, or architecture trade-off.

## Hard Rules

- Clarify functional requirements, non-functional requirements, scope boundaries, and existing constraints before designing.
- Make trade-offs explicit; every architectural choice has a cost.
- Prefer simple designs until requirements justify complexity.
- Define failure modes, security boundaries, data consistency, and observability points.
- Do not present target architecture as implemented without verification.

## Decision Gates

| Need | Action |
|---|---|
| Ambiguous requirements | Ask one clarifying question before designing. |
| Multiple viable approaches | Compare at least two options with trade-offs. |
| New persistent data | Define ownership, access path, and consistency model. |
| New boundary/interface | Specify contract, caller, callee, errors, and versioning. |
| Risky decision | Record an ADR-style decision and rollback/mitigation. |

## Execution Steps

1. Capture context, requirements, constraints, and non-goals.
2. Identify components, data stores, interfaces, and external dependencies.
3. Compare alternatives across complexity, scalability, cost, operability, and team fit.
4. Recommend one approach with explicit rationale and risks.
5. Produce a design artifact with open questions and verification hooks.

## Output Contract

Return context, requirements, architecture, key decisions, data/interface notes, risks/mitigations, and open questions.

## References

- `../xai-proposal-orchestrator/SKILL.md` — related orchestration skill for ML/XAI proposals.
