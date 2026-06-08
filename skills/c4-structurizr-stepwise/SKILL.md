---
name: c4-structurizr-stepwise
description: "Trigger: C4, Structurizr DSL, diagramas de arquitectura, C1, C2, C3, C4. Create reviewable C4 diagrams one level at a time."
license: Apache-2.0
metadata:
  author: gentleman-programming
  version: "1.0"
  scope: [root]
  auto_invoke:
    - "Create C4 model or Structurizr DSL architecture diagrams"
    - "Review or improve C1, C2, C3, or C4 diagrams"
---

## Activation Contract

Load this skill when the user asks for C4 diagrams, Structurizr DSL, architecture modeling, or progressive C1/C2/C3/C4 review based on a repository or product context.

## Hard Rules

- Use Engram when available: search prior architecture context before modeling and save approved diagram decisions after each level.
- Base Structurizr syntax on the official Structurizr site/docs; use the local reference notes before generating DSL.
- Before architecture analysis, run the MCP preflight: check Docker, existing MCP config/files, and validator availability; propose setup only with user approval.
- Inspect `AGENTS.md`, README/docs, and relevant source/config files before inferring architecture.
- If the user names a branch, use that branch as the intended source of truth; if unavailable, state that clearly before modeling.
- Work one level at a time: produce C1, pause; then C2, pause; then C3, pause; produce C4 only when explicitly useful.
- Preserve names and relationships across levels unless the user changes them.
- Keep diagrams focused; do not model every file, class, endpoint, helper, or utility.
- Use valid Structurizr DSL; avoid parser-prone multiline element declarations.

## Decision Gates

| Situation | Action |
|---|---|
| Missing system boundary or main actors | Ask one focused question before drafting C1. |
| Enough repo/product context exists | Draft with labeled assumptions. |
| User asks for C3 | Decompose one container only, usually the backend/API. |
| User asks for C4 | Model one component/class cluster only. |
| Engram is available | Read memories first; persist approved C4 state with stable topic keys. |
| Engram is unavailable | Continue from repo evidence and state that memory persistence was skipped. |
| Structurizr MCP/validator is available | Validate or inspect DSL before presenting final code. |
| Structurizr MCP/validator is missing | Propose the local Docker setup from `assets/structurizr-mcp-compose.yaml`; do not install/run without approval. |
| External tech knowledge is needed | Run focused parallel research and summarize only architecture-relevant findings. |

## Execution Steps

1. Search Engram for prior C4, architecture, branch, and project context; read full observations when relevant.
2. Read `references/structurizr-c4-rules.md` for official Structurizr-derived DSL rules.
3. Run the MCP preflight from `references/structurizr-mcp-preflight.md`; if setup is needed, stop for approval before install/run.
4. Read project guidance and map people, software system, external systems, containers, and candidate components.
5. Generate the requested next C4 level with a short explanation, Structurizr DSL, and assumptions.
6. Validate mentally and, when MCP is available, validate/inspect the DSL before presenting final code.
7. Include a compact review checklist; let the person review and request corrections.
8. Apply corrections when needed, then save the accepted level/decisions to Engram.
9. Stop and ask before continuing to the next level.

## Output Contract

Return exactly one C4 level per response unless the user explicitly requests a full draft. Include: brief explanation, Structurizr DSL, assumptions, Engram context used/saved, review checklist, and a pause question.

## References

- `references/structurizr-c4-rules.md` — level boundaries, DSL pitfalls, and the Daily Control Bot example context.
- `references/structurizr-mcp-preflight.md` — Docker/MCP availability checks and safe setup workflow.
- `assets/structurizr-mcp-compose.yaml` — optional local Structurizr MCP Docker Compose template.
