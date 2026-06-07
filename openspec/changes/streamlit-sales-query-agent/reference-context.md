# Reference Context: Patterns to Reuse

This change uses two local projects as references. They are evidence for structure and ergonomics, not source code to copy blindly.

## References inspected

- `/home/sebastian-ramirez/trabajo/s2026-q2_c-llmbedrock-sebastian-ramirez`
  - Useful for Streamlit + Amazon Bedrock modular app structure, Docker, Compose, `.env.example`, and AWS credential handling.
- `/home/sebastian-ramirez/trabajo/eci_genai`
  - Useful for `uv` project structure, developer ergonomics, LangChain/LangGraph learning patterns, and educational documentation flow.

## Patterns to adopt

### Modular Bedrock + Streamlit structure

Adopt the previous Bedrock app's modular shape, adapted to SQL/MCP:

```text
app.py                  Streamlit entrypoint
src/config.py           environment/config validation
src/bedrock_client.py   Bedrock adapter or LLM adapter
src/prompts.py          schema-aware prompts and instructions
Dockerfile              app image
compose.yaml            app + SQLite MCP topology
.env.example            non-secret configuration example
```

Do not copy the previous chat behavior directly. This project requires a sales SQL workflow and MCP database boundary.

### uv dependency management

Adopt a minimal `uv` project:

- `pyproject.toml` as source of Python metadata/dependencies;
- `uv.lock` for reproducible installs;
- optional dev dependency group for lint/test tools;
- no runtime `pip install` or notebook-style dependency installation.

### LangGraph as preferred orchestration candidate

`eci_genai` shows useful LangGraph patterns: state graph, explicit nodes, tool routing, memory/checkpointing, and graph visualization. For this project, LangGraph is a strong default because the flow is naturally staged:

```text
question -> generate SQL -> validate SQL -> execute via MCP -> format table result
```

The design phase should either choose LangGraph or explicitly justify LangChain/Strands instead.

### Narrow tool/MCP boundary

Adopt the tool-calling concept from the learning notebooks, but not unsafe mechanics. The app should expose a narrow MCP-backed tool such as:

```text
execute_readonly_sales_query(sql) -> QueryResult
```

Avoid:

- generic shell tools;
- `eval`-based tool dispatch;
- unrestricted SQL execution exposed to the LLM.

### Educational documentation style

Adopt the course-style explanation pattern from `eci_genai`:

- problem;
- why GenAI/agentic AI is useful;
- methodology;
- implementation flow;
- results/demo;
- limitations.

The UI should keep generated SQL visible because it supports learning and evaluation.

### Docker and Compose ergonomics

Adopt Compose as the reproducible local-development wrapper, but redesign topology for this app:

```text
streamlit-app service
sqlite-mcp service
shared data volume/bind mount
.env for non-secret config
~/.aws mounted read-only for local Bedrock credentials, if needed
```

Do not adopt GPU/CUDA/PyTorch containers from `eci_genai`; this project uses managed Bedrock and SQLite.

## Patterns to avoid or defer

- Notebook-time `pip install` / `uv pip install` commands inside runtime code.
- OpenAI-specific production classes from notebooks; use Bedrock-compatible adapters.
- Generic shell-command tools.
- `eval` tool dispatch.
- GPU/CUDA development images.
- RAG/vector-store patterns for the first slice.
- Charts and CSV/Excel exports in the first slice; they remain future extensions.

## Implications for spec/design

The next SDD phases should require:

- Deterministic Python seed script -> generated CSV/SQLite DB -> MCP-exposed SQLite database.
- NL question -> Bedrock semantic SQL generation -> deterministic SQL validation -> MCP execution -> Streamlit table output.
- A selected or explicitly deferred SQLite MCP connector decision.
- A SQL validator that allows only a single read-only `SELECT` over `ventas(id, vendedor, sede, producto, cantidad, precio, fecha)`.
- Generated CSV/DB files ignored by git; the fixed-seed Python generator is source of truth.
- Docker/Compose plan with secrets kept out of images and source files.
- Module boundaries for config, Bedrock adapter, prompts, LangGraph/agent flow, SQL validation, MCP client/tool, deterministic data seeding, and Streamlit UI.
- Docker Compose seed/init command that runs the generator before the app/MCP server depends on the generated database.
