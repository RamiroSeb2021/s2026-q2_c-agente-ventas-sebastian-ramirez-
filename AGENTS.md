# Repository Guidelines

## What this project is

This repository is for a practical assignment: build an Agentic AI sales analysis agent that answers natural-language questions over a SQL `ventas` table and can return tables, charts, and exported files.

Target assignment requirements:

- Accept sales questions in natural language.
- Translate user intent into SQL queries over a sample sales database.
- Return results as text, table, chart, CSV, or Excel depending on the user's intent.
- Use an agent framework such as LangGraph, Strands, or LangChain.
- Prefer preexisting connectors that implement MCP for SQL/database access.
- Keep SQL/query logic, agent flow, visualization, persistence, and documentation modular.
- Do not depend on fixed prompt keywords for intent routing; use a language model to infer intent.
- Amazon Bedrock is available and may be used as the LLM provider.
- Build the user interface as a Streamlit app.
- Package the app with Docker for reproducible local execution.
- Use `uv` for Python dependency and environment management.

## Repo Reality

Current verified state:

- This repo contains a working Streamlit sales analysis app slice for the assignment.
- `scripts/seed_database.py` creates a deterministic local SQLite database with the required `ventas` table.
- `tests/test_seed_database.py` verifies database creation, schema, row count, and required values.
- `app.py` implements a Spanish Streamlit chat UI that asks sales questions, shows generated SQL when present, renders tables/charts, and exposes CSV/Excel downloads.
- `src/sales_query_agent/` contains modular app code for configuration, database path handling, Bedrock plan generation, prompt contracts, SQL validation, MCP SQLite execution, output helpers, and a minimal LangGraph boundary.
- The SQLite execution boundary uses `mcp-server-sqlite` through the MCP Python SDK and exposes safe wrappers around read-only query/table diagnostics for the app.
- Amazon Bedrock is integrated as the LLM provider for structured semantic plans (`output_type`, `sql`, and optional `chart_type`).
- `Dockerfile` and `compose.yaml` exist for reproducible local packaging, but container runtime verification is not recorded here yet.
- Tests cover seed database creation plus config, database helpers, Bedrock plan parsing, prompts, SQL guardrails, MCP client behavior, query service flow, LangGraph boundary, and output/chart/export helpers.
- **Documented ≠ implemented**: keep distinguishing current inspected files from target/future capabilities, especially richer multi-node orchestration and unverified Docker runtime behavior.

When adding implementation, update this section only after inspecting the created files.

## How to interpret this repo

Use this taxonomy before making claims:

- **Verified current state**: present in the tree and inspected.
- **Target design**: required or intended behavior from the assignment, not necessarily implemented.
- **Planned / future**: roadmap or teaching steps that depend on later implementation.

If a user asks for a feature and the repo does not yet contain supporting files, say that clearly and propose the next smallest implementation step.

## Documentation entrypoints

| Topic | Source of truth |
| --- | --- |
| Agent-facing repo rules | `AGENTS.md` |
| Main project README | `README.md` when created |
| Skill authoring/reference | `docs/skill-style-guide.md` |
| Local AGENTS.md creation skill | `skills/create-agents-md/SKILL.md` |
| Skill registry | `.atl/skill-registry.md` when regenerated |

## Repository map

Verified current tree:

```text
AGENTS.md                         Agent-facing repository instructions
.gitignore                        Local ignore rules; `.atl/` is ignored
.gga                              Gentleman Guardian Angel pre-commit review config; excludes `uv.lock`
.env.example                      Non-secret environment example for generated database path
.python-version                   Python version pin for uv/local tooling
README.md                         Human-facing current slice summary
Dockerfile                        Container image definition for the Streamlit app
compose.yaml                      Local Streamlit app orchestration
app.py                            Streamlit chat UI entrypoint
pyproject.toml                    Python project metadata and dependencies managed by uv
uv.lock                           Locked dependency graph
scripts/seed_database.py          Deterministic SQLite seed script for `ventas`
src/sales_query_agent/            Modular app code: config, Bedrock, MCP, validation, outputs, graph
tests/                            Pytest coverage for seed DB, app modules, validation, MCP, graph, outputs
openspec/changes/                 Planning/design artifacts for implemented and historical slices
skills/c4-structurizr-stepwise/   Local C4/Structurizr skill guidance
```

Expected future or generated tree for the assignment:

```text
data/             Generated local SQLite database or sample data, when created
docs/             Additional architecture, usage notes, examples, and design decisions
outputs/          Generated charts or CSV/Excel files; usually gitignored unless examples are intentional
```

Do not claim expected future paths exist until they are created and inspected.

## Assignment domain model

The sample database must include a `ventas` table with these columns:

| Column | Meaning |
| --- | --- |
| `id` | Sale identifier |
| `vendedor` | Seller name |
| `sede` | City/branch/location |
| `producto` | Product sold |
| `cantidad` | Quantity sold |
| `precio` | Unit price |
| `fecha` | Sale date |

Example target queries:

```sql
SELECT producto, SUM(cantidad) AS total_vendido
FROM ventas
WHERE sede = 'Medellín'
GROUP BY producto
ORDER BY total_vendido DESC
LIMIT 5;
```

```sql
SELECT vendedor, SUM(cantidad * precio) AS total_ventas
FROM ventas
WHERE sede = 'Bogotá'
GROUP BY vendedor
ORDER BY total_ventas DESC
LIMIT 1;
```

## Rules for assistants

- Explain concepts before code because this is a learning assignment.
- Keep user-facing explanations in Spanish when the user writes in Spanish.
- Keep repository-facing artifacts, code, identifiers, comments, and filenames in English unless the user explicitly asks otherwise.
- Verify tree state before claiming a file, script, table, dependency, command, or feature exists.
- Ask whether the user wants documentation, scaffold, or real implementation when the request is ambiguous.
- Prefer small, teachable steps over one large generated solution.
- Preserve the assignment constraint: intent detection must use an LLM, not brittle hardcoded keyword checks.
- Use modular design: separate the Streamlit UI, agent orchestration, SQL/MCP access, chart generation, file exports, configuration, and sample data.
- Surface contradictions with file evidence instead of silently choosing one source.
- Avoid destructive git, filesystem, database, cloud, or publishing operations without explicit approval.

## Selected implementation direction

This is the current inspected implementation direction:

- Language: Python, managed with `uv`.
- UI: Streamlit chat app in `app.py`.
- Agent framework: minimal LangGraph boundary in `src/sales_query_agent/agent_graph.py`.
- LLM provider: Amazon Bedrock through `src/sales_query_agent/bedrock_client.py`.
- Database: local SQLite sample database with the required `ventas` table.
- SQL connector: MCP SQLite via `mcp-server-sqlite`, wrapped in `src/sales_query_agent/mcp_client.py`.
- Output formats: Streamlit table/text output plus Plotly charts and CSV/Excel download helpers.
- Containerization: `Dockerfile` and `compose.yaml` are present; treat Docker runtime status as unverified unless a session explicitly verifies it.

Future work should improve orchestration depth, packaging confidence, and any assignment polish without replacing the safe MCP/LLM/validation boundaries.

Before adding dependencies, explain the stack choice and get confirmation if it affects setup complexity.

## Branching and review policy

- Never commit unless the user explicitly asks.
- Keep changes reviewable and grouped by purpose: docs, uv/Python scaffold, data, Streamlit UI, agent logic, visualization/export, Docker packaging, tests.
- Ask before turning this assignment into a large multi-area implementation.
- If implementation grows beyond a small slice, propose a plan first.

## Learning mode

Act as a teaching coding agent for this repo:

1. Restate the goal in plain language.
2. Explain the concept or design choice.
3. Make the smallest useful file change.
4. Show how to run or verify it when commands exist.
5. Summarize what changed and what the next step teaches.

Avoid dumping unexplained code.

## Skills Reference

Use local skills when applicable:

| Skill | When to use it | Path |
| --- | --- | --- |
| `create-agents-md` | Create, rewrite, or audit this file | `skills/create-agents-md/SKILL.md` |
| `skill-registry` | Regenerate the skill index after skill changes | `/home/sebastian-ramirez/.pi/agent/npm/node_modules/gentle-pi/skills/skill-registry/SKILL.md` |
| `create-readme` | Create or improve the main README | `/home/sebastian-ramirez/trabajo/juanchito/skills/create-readme/SKILL.md` |
| `documentation-writer` | Write deeper technical docs beyond README | `/home/sebastian-ramirez/trabajo/juanchito/skills/documentation-writer/SKILL.md` |
| `system-design` | Produce architecture, components, and trade-off docs | `/home/sebastian-ramirez/trabajo/juanchito/skills/system-design/SKILL.md` |
| `c4-structurizr-stepwise` | Create or review C4/Structurizr diagrams level by level | `skills/c4-structurizr-stepwise/SKILL.md` |

## Auto-invoke Skills

When performing these actions, invoke the corresponding skill first:

| Action | Skill |
| --- | --- |
| Create or rewrite `AGENTS.md` | `create-agents-md` |
| Create or improve `README.md` | `create-readme` |
| Add or modify skills | `skill-registry` |
| Create architecture/design docs | `system-design` |
| Create or review C4/Structurizr diagrams | `c4-structurizr-stepwise` |
| Write technical documentation beyond README | `documentation-writer` |

## Tooling / Sync

Safe discovery commands:

```bash
git status --short
find . -maxdepth 3 -type f -not -path './.git/*' -not -path './.atl/*' | sort
```

JSON validation for project settings:

```bash
python3 -m json.tool .pi/settings.json >/dev/null
```

Application commands defined by current files:

```bash
uv sync
uv run streamlit run app.py
```

Mutating/situational commands:

```bash
# Regenerate the skill registry only after skill changes or when requested.
# The exact command may depend on the active Pi/gentle-pi installation.
```

Do not invent application, uv, or Docker run commands until project files define them.

## Verified Commands

These commands have been verified in this repo:

```bash
git status --short
find . -maxdepth 3 -type f -not -path './.git/*' -not -path './.atl/*' | sort
uv run python scripts/seed_database.py
uv run pytest
```

Streamlit, Bedrock, MCP, and Docker files exist. Do not claim Docker runtime has been verified unless a session runs and records it.

## Security / hard blocks

- Do not commit, push, publish, delete data, or modify external cloud resources without explicit user approval.
- Do not store AWS credentials, Bedrock keys, database passwords, generated secrets, or local `.env` contents in git.
- Do not run `uv sync`, dependency installation, or Docker builds blindly; inspect dependency/container files first and explain the reason.
- Do not execute generated SQL against production or external databases. Use local/sample data unless explicitly approved.
- Prefer read-only SQL first; any write/migration/drop operation requires explicit approval.
- Treat `outputs/`, charts, CSV, Excel exports, and local databases as generated artifacts unless the user asks to version examples.

## Gotchas

- Pi project settings paths in `.pi/settings.json` resolve relative to `.pi`; the root `skills/` directory should be referenced as `../skills`.
- `.atl/skill-registry.md` is an index for delegation, not proof that Pi has loaded a skill into the current session. Restart Pi after changing skill paths if the runtime skill list matters.
- The assignment says to use MCP-compatible connectors where possible. Do not implement a custom connector first without explaining why an existing connector is not being used.
- Intent detection must be semantic. Do not write code that assumes exact Spanish phrases such as `grafico`, `csv`, or `top 5` are always present.
