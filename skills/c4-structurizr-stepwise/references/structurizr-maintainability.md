# Structurizr Maintainability

Structurizr lets one model drive many views. Use that strength: avoid separate disconnected diagrams that repeat names and drift over time.

## Workspace Conventions

- Prefer one `workspace` with one `model` and multiple `views` for related C1/C2/C3 diagrams.
- Define elements once in `model`; use views to choose what each diagram shows.
- Use `!identifiers hierarchical` when nested names may repeat or when references are clearer as `system.container.component`.
- Keep view keys stable, such as `C1-SystemContext`, `C2-Containers`, `C3-BackendApi`, because generated keys can break saved layout and references.
- Use consistent naming across levels; rename in one place instead of creating near-duplicates.
- Put broad visual styling in `styles`; avoid encoding meaning only through color unless the legend explains it.
- Keep `!include` modularization intentional. It should improve reviewability, not hide model sprawl.

## Naming Guidance

- Element identifiers should be short, stable, ASCII, and meaningful: `backendApi`, `searchIndex`, `mcpServer`.
- Display names should be human-readable and domain-specific: `KnowledgePDF CLI`, `SQLite FTS5 Index`.
- Avoid identifiers coupled to volatile implementation details unless the codebase really uses those names.
- Prefer explicit relationship labels over generic `Uses`.

## Syntax Validation Vs Modeling Quality

Validation checks whether the DSL parses. It does not check whether the model communicates the right architecture.

Errors that can pass syntax validation:

- C1 view includes containers or infrastructure details.
- C2 view omits important C1 actors, making usage unclear.
- C3 decomposes multiple containers at once.
- Component boxes are just folders or classes with no architectural responsibility.
- Relationships are all labeled `uses`, so the diagram conveys no purpose.
- The model describes a desired fantasy rather than current repo reality, without labeling it as proposed.
- View keys are unstable or duplicated semantically, making future diffs/layouts painful.
- The DSL validates but the audience cannot answer the intended architecture question.

## Review Workflow

1. Validate DSL syntax when a validator is available.
2. Inspect generated/parsed output if the syntax result is surprising.
3. Review level boundaries, naming, relationships, and audience fit manually.
4. Fix semantic problems before moving to the next C4 level.
5. Save accepted naming and boundary decisions to Engram when available.
