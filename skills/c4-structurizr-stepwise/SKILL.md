---
name: c4-structurizr-stepwise
description: "Trigger: C4, Structurizr DSL, diagramas de arquitectura, C1, C2, C3, C4. Create reviewable C4 diagrams one level at a time."
license: Apache-2.0
metadata:
  author: gentleman-programming
  version: "1.1"
  scope: [root]
  auto_invoke:
    - "Create C4 model or Structurizr DSL architecture diagrams"
    - "Review or improve C1, C2, C3, or C4 diagrams"
---

## Activation Contract

Load this skill when the user asks for C4 diagrams, Structurizr DSL, architecture modeling, or progressive C1/C2/C3/C4 review based on a repository or product context.

## Hard Rules

- Use C4 for communicating static structure through hierarchical zoom, not for inventorying everything or designing by diagramming.
- Inspect `AGENTS.md`, README/docs, source/config, and Engram memories before inferring architecture.
- If the user names a branch, use that branch as the intended source of truth; if unavailable, state that clearly before modeling.
- Work one level at a time: C1, review; C2, review; C3, review; C4 only when explicitly useful.
- Ask the minimum needed questions; if evidence is enough, draft with visible assumptions instead of interrogating the user.
- Preserve accepted names and relationships across levels unless review changes them.
- Draw only architecturally meaningful elements. Omit folder maps, endpoint lists, class dumps, helpers, utilities, and cross-cutting clutter.
- Every relationship needs a purpose; add mechanism/style only when it clarifies communication.
- Valid Structurizr syntax is not proof of architectural quality; validate DSL and review semantic fit separately.
- Do not install, pull, run Docker/MCP, or send private DSL to public services without user approval.

## Decision Gates

| Case | Action |
|---|---|
| Missing target system, boundary, or primary actors | Ask one focused question before C1. |
| C1 requested | Show target system, people, external systems, and purpose relationships only. |
| C2 requested | Open one software system into major runnable units/data stores; keep useful C1 actors/systems. |
| C3 requested | Decompose one container into coarse components that map to real/intended code. |
| C4 requested | Proceed only for one complex component/pattern where class/code detail adds value. |
| Diagram fails review checklist | Fix current level before continuing. |
| Validator/MCP exists | Validate/inspect DSL before final output. |
| Validator/MCP missing | Offer approved setup path; otherwise do mental syntax review. |

## Execution Steps

1. Read `references/c4-modeling-judgment.md`, `references/c4-review-checklists.md`, and `references/structurizr-c4-rules.md` before drafting.
2. Search Engram for prior C4/architecture context; read full observations when relevant.
3. Run the MCP preflight from `references/structurizr-mcp-preflight.md`; stop for approval before any setup.
4. Inspect repo/product evidence and identify the next valid C4 level.
5. Draft one level with concise explanation, Structurizr DSL, assumptions/questions, and level-specific review checklist.
6. Validate syntax when possible, then review semantic quality against the checklist.
7. Apply corrections, save accepted C4 decisions to Engram, and stop before the next level.

## Output Contract

Return exactly one C4 level unless the user explicitly requests a full draft. Include: level and purpose, Structurizr DSL, assumptions/open questions, validation result, review checklist, Engram context used/saved, and one pause question.

## References

- `references/c4-modeling-judgment.md` — C4 boundaries, audience guidance, omissions, and anti-patterns.
- `references/c4-review-checklists.md` — definition of done by C4 level.
- `references/structurizr-maintainability.md` — workspace conventions and syntax-vs-quality guidance.
- `references/structurizr-c4-rules.md` — Structurizr DSL rules, MCP notes, and repository inspection guidance.
- `references/structurizr-mcp-preflight.md` — Docker/MCP availability checks and safe setup workflow.
- `assets/structurizr-mcp-compose.yaml` — optional local Structurizr MCP Docker Compose template.
