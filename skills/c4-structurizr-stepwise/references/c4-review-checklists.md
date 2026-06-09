# C4 Review Checklists

Use these checklists as the definition of done before moving to the next level.

## Universal Definition Of Done

- The view has a meaningful title and stable view key.
- The diagram communicates one level of abstraction.
- Every element has a clear responsibility and belongs at that level.
- Every relationship is labeled with purpose; mechanism/style is included when helpful.
- Assumptions, unresolved questions, and invented notation are visible in notes or legend.
- Names are consistent with previously accepted levels.
- The view matches repo/product evidence or is clearly labeled as proposed.
- Structurizr DSL validates when a validator is available.
- Semantic review passes; syntax validity alone is not enough.

## C1 System Context

Definition of done:

- Target software system boundary is clear.
- Primary people/roles are shown.
- External software systems are shown only when the target system interacts with them.
- Relationships describe business/user purpose at a high level.
- Technical internals are absent.

Review questions:

- Would a non-technical stakeholder understand scope from this view?
- Is anything inside the target system accidentally shown as external?
- Are any actors or external systems missing for the main use cases?
- Are there unlabeled or vague relationships?

## C2 Container

Definition of done:

- The C1 target system is opened into major runnable units/data stores.
- Each container has a responsibility and key technology when known.
- Important people and external systems from C1 remain visible when they clarify usage/integration.
- Communication between containers is shown with purpose and mechanism/style when useful.
- No internal components/classes/endpoints are shown.

Review questions:

- Could developers and operations discuss deployment/runtime responsibilities from this view?
- Is every container independently meaningful as a runnable unit or data store?
- Are data ownership and integration boundaries understandable?
- Did the view accidentally become a component diagram?

## C3 Component

Definition of done:

- Exactly one container is decomposed.
- Components are coarse-grained and have distinct responsibilities.
- Components map to real or intended code/module boundaries.
- External containers/systems are included only when they explain component collaboration.
- Cross-cutting/framework clutter is omitted unless architecturally central.

Review questions:

- Would maintainers recognize these components in the code or planned code?
- Does each component own a clear responsibility?
- Are relationships domain/architecture meaningful rather than generic call chains?
- Is C3 adding value, or would C2 plus text be clearer?

## C4 Code

Definition of done:

- One component/class cluster is in scope.
- The view explains a specific design decision, algorithm, or implementation pattern.
- Only classes/interfaces/functions needed for that story are shown.
- Generated boilerplate, DTO catalogs, and full class dumps are omitted.

Review questions:

- Is code-level detail necessary for the decision being communicated?
- Would the same story be clearer as C3, sequence, or prose?
- Are the shown classes stable enough to document?
- Is this view maintainable, or will it rot immediately?
