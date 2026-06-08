# Structurizr C4 Stepwise Rules

## Official Structurizr source notes

These rules were derived from:

- `https://structurizr.com/`
- `https://docs.structurizr.com/dsl`
- `https://docs.structurizr.com/dsl/basics`
- `https://docs.structurizr.com/dsl/tutorial`
- `https://docs.structurizr.com/dsl/includes`
- `https://docs.structurizr.com/dsl/docs`
- `https://docs.structurizr.com/dsl/language`
- `https://docs.structurizr.com/dsl/identifiers`
- `https://docs.structurizr.com/ai`
- `https://docs.structurizr.com/ai/dsl-generation`
- `https://docs.structurizr.com/ai/mcp`
- `https://docs.structurizr.com/server/documentation`

Structurizr is a models-as-code tool for the C4 model. Prefer one consistent `workspace` that contains one `model` and several `views`, so C1/C2/C3 diagrams reuse the same elements and relationships instead of drifting across separate diagrams.

The official AI guidance reinforces why this matters: Structurizr is text-based, version-controllable, diff-friendly, model-based, and C4-aware. Unlike generic diagrams-as-code tools, it enforces hierarchy rules such as containers inside software systems and components inside containers. Treat AI-generated DSL as a draft that usually needs cleanup, validation, inspection, and human architectural review.

## Core DSL structure

Use this minimum shape:

```dsl
workspace "Name" "Description" {
    !identifiers hierarchical

    model {
        user = person "User"
        system = softwareSystem "Software System" {
            web = container "Web Application" "Allows users to interact with the system." "Technology"
            db = container "Database" "Stores application data." "Database" {
                tags "Database"
            }
        }

        user -> system.web "Uses"
        system.web -> system.db "Reads from and writes to"
    }

    views {
        systemContext system "C1-SystemContext" {
            include *
            autoLayout lr
        }

        container system "C2-Containers" {
            include *
            autoLayout lr
        }
    }
}
```

Key points from the official docs:

- `workspace` wraps the model and views.
- `model` defines elements and relationships; it is non-visual.
- `views` defines what diagrams render from that model.
- Assign identifiers only to elements/relationships that must be referenced.
- Use `!identifiers hierarchical` when nested containers/components may reuse local names; then reference them as `system.container`.
- Relationships use `source -> destination "Description" ["Technology"]`.
- `include *` has level-specific behavior; use explicit includes when actors or external systems must remain visible.
- Define stable view keys (`C1-SystemContext`, `C2-Containers`, etc.) because generated keys are not stable and can lose manual layout information.
- Use `autoLayout [tb|bt|lr|rl]` when you want automatic layout.

## DSL correctness rules

Apply these before returning DSL:

- Lines are processed in order; do not forward-reference identifiers before they are defined.
- Opening `{` must be on the same line as the statement; closing `}` must be on its own line.
- Line breaks matter; split long lines only with `\` as the last character when needed.
- Use `""` as a placeholder when skipping an earlier optional property.
- Software system and person names must be unique.
- Container names must be unique within a software system.
- Component names must be unique within a container.
- Relationship descriptions from the same source to same destination must be unique.
- Use `!include <file|directory|url>` only for intentional modularization; included content is inlined in discovery order.

## Supplementary documentation

When the user wants architecture docs in addition to diagrams, Structurizr can publish lightweight supplementary technical documentation with the workspace:

- Server documentation renders Markdown or AsciiDoc files in the browser together with the workspace model, making it easy to embed diagrams from the same workspace.
- DSL supports `!docs <path> [fully qualified class name]` on a workspace, software system, or container.
- The docs path must be relative to the DSL parent file and located in the same directory or a subdirectory.
- By default, Markdown/AsciiDoc files are imported alphabetically by filename, and images in that directory/subdirectories are imported too.
- Structurizr rendering may differ from dedicated documentation tools; if exact docs rendering/control is required, prefer external docs tooling with iframe/image embeds.

Use this only when the request includes a documentation deliverable; do not bloat a C1/C2/C3 diagram response with full guidebook content.

## Useful Structurizr MCP behavior

If a Structurizr MCP server or equivalent validator is available, use it before returning final DSL:

- Validate Structurizr DSL: returns `OK` or parser errors.
- Parse Structurizr DSL: returns JSON workspace or parser errors.
- Inspect Structurizr DSL: returns inspection violations.
- Export a view to Mermaid/PlantUML/C4-PlantUML when the user asks for another format.

Do not start local Docker/MCP tooling without user approval; validation is opportunistic when already available.

## Level boundaries

- **C1 System Context**: people, target software system, external systems, and high-level relationships only. Do not include containers, databases, APIs, components, classes, endpoints, or functions.
- **C2 Containers**: preserve C1 people/external systems and add containers inside the system, such as UI apps, APIs, databases, schedulers, queues, or workers. Do not add internal components.
- **C3 Components**: decompose one container at a time. Prefer meaningful architectural components: controllers, services, repositories, adapters/clients, validators, schedulers, and domain services. Do not model the full system at once.
- **C4 Code/Class**: optional and narrow. Use only for one specific component when class-level detail helps explain a design decision.

## Stepwise interaction pattern

1. Generate C1 and ask for corrections.
2. Wait for user feedback.
3. Generate C2 and ask for corrections.
4. Wait for user feedback.
5. Generate C3 for one container and ask for corrections.
6. Generate C4 only if the user needs class-level detail.

Never generate C1 through C4 in one response unless the user explicitly requests a complete first draft.

## Repository inspection checklist

Inspect, when present:

- `AGENTS.md` or `agents.md`
- `README.md`
- `docs/`, `architecture/`, or ADR files
- `src/`, `app/`, service modules, tests, and config files
- Infrastructure/deployment files such as Docker, compose, Terraform, or package/dependency files

If the user specifies a branch, verify whether it exists locally or remotely. Do not switch branches when the worktree is dirty unless the user approves.

## Engram usage

Use Engram as continuity storage for the model, not as a replacement for repository evidence.

Before drafting each level:

1. Call recent context/memory search for the project.
2. Search for terms such as `C4`, `Structurizr`, the system name, branch name, `architecture`, and prior diagram level names.
3. Read full observations that contain accepted actors, containers, components, corrections, or naming decisions.

After the user approves or corrects a level, save a concise memory with:

- **What**: accepted C4 level and key diagram decisions;
- **Why**: user review/approval or correction;
- **Where**: diagram file/path if one exists, or `conversation / Structurizr DSL draft`;
- **Learned**: naming corrections, actor/container/component constraints, DSL pitfalls.

Use stable topic keys when possible:

- `architecture/c4/{system-name}/c1`
- `architecture/c4/{system-name}/c2`
- `architecture/c4/{system-name}/c3/{container-name}`
- `architecture/c4/{system-name}/c4/{component-name}`

If Engram is unavailable, continue from inspected files and explicitly say memory persistence was skipped.

## Parallel search guidance

Parallel research can be useful, but keep it focused:

- one search for repository structure and architecture evidence;
- one search for domain requirements or prior conversation notes;
- one search for external technology references such as Structurizr DSL syntax or framework docs.

Compress findings into the diagram assumptions; do not dump research notes.

## Structurizr DSL rules

Prefer one-line element declarations when possible:

```dsl
backendApi = container "Backend API" "Processes reports and applies business rules." "Node.js / Express"
```

Avoid parser-prone multiline declarations like:

```dsl
backendApi = container "Backend API"
    "Processes reports and applies business rules."
    "Node.js / Express"
```

Use explicit `include` statements in views when people or external systems disappear accidentally.

## Daily Control Bot example context

Prior conversation context may include a system named **Daily Control Bot** for Acme Corp.

The system:

- sends scheduled notifications to Scrum team members;
- receives daily reports using predefined fields;
- validates missing reports;
- detects repeated topics three times consecutively;
- alerts possible blockers or stagnation;
- publishes reports in a Microsoft Teams channel visible to the group.

C1 actors/systems used before:

- Integrante Scrum
- Scrum Master
- Equipo Scrum
- Daily Control Bot
- Microsoft Teams
- Microsoft Entra ID
- Microsoft Graph API

C2 containers used before:

- Teams App / Bot
- Backend API
- Scheduler
- Daily Reports Database

Important correction: C2 must preserve the consumption users from C1. Do not remove `Integrante Scrum`, `Scrum Master`, or `Equipo Scrum` unless the user asks.

C3 decomposition used before for `Backend API`:

- Report Controller
- Configuration Controller
- Report Service
- Daily Validation Service
- Blockage Detection Service
- Notification Service
- Teams Graph Client
- Report Repository

## Quality checklist

Before returning DSL, verify:

- requested level matches the content;
- C1 has no containers;
- C2 has containers but no internal components;
- C3 decomposes one container;
- C1 users remain visible in C2/C3 when useful;
- names are consistent across levels;
- DSL syntax is likely valid;
- response pauses for user review.
