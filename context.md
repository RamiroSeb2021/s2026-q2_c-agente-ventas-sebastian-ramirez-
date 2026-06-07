# Reference Context: `eci_genai` patterns for `streamlit-sales-query-agent`

## Scope and evidence base

Inspected reference project `/home/sebastian-ramirez/trabajo/eci_genai` and current project SDD artifacts. This is read-only research except for this requested handoff file.

Primary evidence:
- `/home/sebastian-ramirez/trabajo/eci_genai/README.md`
- `/home/sebastian-ramirez/trabajo/eci_genai/pyproject.toml`
- `/home/sebastian-ramirez/trabajo/eci_genai/compose.yml`
- `/home/sebastian-ramirez/trabajo/eci_genai/Makefile`
- `/home/sebastian-ramirez/trabajo/eci_genai/.devenv/Dockerfile`
- `/home/sebastian-ramirez/trabajo/eci_genai/6_langchain.ipynb`
- `/home/sebastian-ramirez/trabajo/eci_genai/7_langgraph.ipynb`
- `/home/sebastian-ramirez/trabajo/eci_genai/proyecto.ipynb`
- `AGENTS.md`
- `openspec/config.yaml`
- `openspec/changes/streamlit-sales-query-agent/proposal.md`

Memory note: no callable Engram/memory tool is available in this subagent toolset, so no memory save was performed.

---

## 1. Transferable patterns worth adopting now

### A. Use a minimal `uv` Python project, but adapt dependencies to the app

Evidence:
- Reference `pyproject.toml` uses standard PEP 621 metadata and `requires-python = ">=3.13"` at `/home/sebastian-ramirez/trabajo/eci_genai/pyproject.toml:1-10`.
- It separates dev tooling in `[dependency-groups] dev`, including `ipython`, `mypy`, `ruff`, and `ty` at `/home/sebastian-ramirez/trabajo/eci_genai/pyproject.toml:13-20`.
- Current SDD config already targets `uv` and Docker installs from `pyproject.toml`/`uv.lock` at `openspec/config.yaml:28-47` and requires `uv` in design rules at `openspec/config.yaml:88-92`.
- Current proposal requires initializing `pyproject.toml` and `uv.lock` at `openspec/changes/streamlit-sales-query-agent/proposal.md:17`.

Adopt:
- Create a project-local `pyproject.toml` with PEP 621 metadata, `requires-python`, runtime deps, and a `dev` dependency group.
- Include quality tools early (`ruff`, optionally `mypy` or `ty`) because the reference already models that separation.
- For this project, runtime dependencies should be app-specific, not copied from the course project: likely `streamlit`, `pandas`, `boto3`/Bedrock integration, LangChain/LangGraph package(s), SQL parsing/validation, MCP client/server integration, Excel export dependency such as `openpyxl`, and visualization dependency later.

Design implication:
- The spec/design should require reproducible local setup through `uv sync` only after `pyproject.toml` exists, consistent with `AGENTS.md:217-229`.

### B. Prefer LangGraph for the first agent architecture if tool routing matters

Evidence:
- Reference `7_langgraph.ipynb` installs `langchain`, `langchain-openai`, and `langgraph` using `uv pip install` at `/home/sebastian-ramirez/trabajo/eci_genai/7_langgraph.ipynb:43-44`.
- It imports `StateGraph`, `START`, `END`, `MessagesState`, `MemorySaver`, `ToolNode`, and `tools_condition` at `/home/sebastian-ramirez/trabajo/eci_genai/7_langgraph.ipynb:77-79`.
- It demonstrates graph construction with `StateGraph(...)` at `/home/sebastian-ramirez/trabajo/eci_genai/7_langgraph.ipynb:262`, graph compilation with `MemorySaver` at lines `701-702`, and tool routing with `ToolNode(tools)` plus `tools_condition` at lines `1380-1386`.
- It renders graph structure with Mermaid PNG at `/home/sebastian-ramirez/trabajo/eci_genai/7_langgraph.ipynb:370-371`, `977-978`, and `1410-1411`.
- Current project allows LangGraph, Strands, or LangChain with Bedrock at `openspec/config.yaml:16` and `openspec/config.yaml:32-36`.

Adopt:
- Use LangGraph for a transparent, educational flow: `question -> semantic SQL generation -> SQL validation -> MCP SQL execution -> response formatting`.
- Keep nodes small and named by responsibility; this matches the current modularity requirement in `AGENTS.md:125` and `openspec/config.yaml:88-92`.
- Use graph visualization as documentation/debug aid if lightweight; it is useful for the assignment video/demo and architecture docs.

Design implication:
- Design should define a typed agent state carrying `question`, `generated_sql`, `validation_result`, `query_rows`, `output_intent`, `error`, and possibly `chart_spec`/`export_bytes` in later slices.
- Tool execution should be modeled as an explicit tool boundary, but SQL safety validation must happen before the MCP tool call.

### C. Reuse the tool-calling concept, not the unsafe implementation mechanics

Evidence:
- Reference `6_langchain.ipynb` demonstrates `.bind_tools(tools)` at `/home/sebastian-ramirez/trabajo/eci_genai/6_langchain.ipynb:1626-1627` and passing observations back with `ToolMessage` at lines `1781-1782` and `1913-1915`.
- Reference `7_langgraph.ipynb` demonstrates `model = ChatOpenAI(...).bind_tools(tools)` at `/home/sebastian-ramirez/trabajo/eci_genai/7_langgraph.ipynb:1331-1332` and LangGraph `ToolNode(tools)` at `1380-1386`.
- Current proposal requires MCP SQL execution instead of direct SQLite from Streamlit at `openspec/changes/streamlit-sales-query-agent/proposal.md:20`, `68-74`.

Adopt:
- Treat MCP SQL execution as a tool called by the agent/graph after validation.
- Tool schemas/docstrings should be explicit about input shape and read-only SQL constraints.

Design implication:
- The MCP client wrapper should expose one narrow tool/function such as `execute_readonly_sales_query(sql: str) -> QueryResult`, not a generic shell/database capability.

### D. Use course educational structure for documentation and demo narrative

Evidence:
- Reference README is course-oriented and includes curated learning links: Hugging Face LLM, MCP, Agents courses, and LangGraph Academy at `/home/sebastian-ramirez/trabajo/eci_genai/README.md:17-20`.
- `proyecto.ipynb` requires a clear problem, GenAI relevance, runnable code, source code, and a 5-10 minute demo video at `/home/sebastian-ramirez/trabajo/eci_genai/proyecto.ipynb:28-29`, `55-67`, `75-77`.
- It proposes final-project sections: `Problematica`, `Trabajos Relacionados`, `Metodologia`, `Resultados y Discusion`, `Conclusion` at `/home/sebastian-ramirez/trabajo/eci_genai/proyecto.ipynb:105-141`.
- Current `AGENTS.md` says to explain concepts before code and prefer small teachable steps at `AGENTS.md:119-141` and learning mode at `AGENTS.md:153-161`.

Adopt:
- SDD design/docs should include a short educational architecture explanation: why Streamlit, why LangGraph/LangChain, why MCP boundary, why SQL validation.
- README/design should map to the project rubric: problem, GenAI application, methodology, results/demo, known limitations.
- Include transparent generated SQL in the UI because proposal already mandates it at `proposal.md:24` and the educational value is high.

### E. Keep a lightweight Makefile/help pattern for developer commands

Evidence:
- Reference Makefile provides a self-documenting `help` target at `/home/sebastian-ramirez/trabajo/eci_genai/Makefile:4-6`.
- It groups commands under `##@ Development Environment` and provides `build-devenv`/`connect-devenv` targets at `/home/sebastian-ramirez/trabajo/eci_genai/Makefile:8-14`.

Adopt:
- Add a simple Makefile later, after commands are real, with targets like `help`, `sync`, `run`, `test`, `lint`, `docker-build`, `docker-up`.
- Do not invent targets before files exist; current repo explicitly says no app/uv/Docker/test command is verified yet at `AGENTS.md:217-229`.

### F. Use Compose as a reproducible local-development wrapper, but redesign services for this app

Evidence:
- Reference Compose defines a single dev-environment service with container name, build context, `stdin_open`, and `tty` at `/home/sebastian-ramirez/trabajo/eci_genai/compose.yml:1-8`.
- It requests an NVIDIA GPU device at `/home/sebastian-ramirez/trabajo/eci_genai/compose.yml:12-15`.
- Current proposal says Docker/Compose should plan a Streamlit app container, SQLite MCP server, shared data volume, `.env`, and AWS credentials mounted safely at `openspec/changes/streamlit-sales-query-agent/proposal.md:52-60`.

Adopt:
- Use Compose to express local multi-service topology: Streamlit app plus SQLite MCP server if feasible.
- Keep `stdin_open`/`tty` only for interactive dev containers, not necessarily production-like app service.
- Provide a `.env.example` for non-secret config and rely on AWS credential chain/mounts, consistent with proposal risk controls at `proposal.md:89-90`.

---

## 2. Patterns to avoid or defer

### A. Do not copy notebook-time dependency installation into the app

Evidence:
- `6_langchain.ipynb` uses `!pip install langchain langchain-openai` at `/home/sebastian-ramirez/trabajo/eci_genai/6_langchain.ipynb:92`.
- `7_langgraph.ipynb` uses `!pip install uv` and `!uv pip install ...` inside the notebook at `/home/sebastian-ramirez/trabajo/eci_genai/7_langgraph.ipynb:43-44`.

Avoid:
- No runtime `pip install` in Streamlit, notebooks, or app startup.
- Dependencies must live in `pyproject.toml`/`uv.lock` for reproducibility.

### B. Do not copy unsafe dynamic tool dispatch or shell tools

Evidence:
- `6_langchain.ipynb` dispatches tool calls with `eval(tool_call["name"])(**tool_call["args"])` at `/home/sebastian-ramirez/trabajo/eci_genai/6_langchain.ipynb:1718-1719` and `1871-1872`.
- It defines a generic `shell_command` tool that runs `subprocess.run(command, ...)` at `/home/sebastian-ramirez/trabajo/eci_genai/6_langchain.ipynb:1833-1842`, then binds it as a model tool at `1853-1854`.
- Current proposal explicitly warns prompt instructions are not enough and requires rejecting unsafe SQL operations at `openspec/changes/streamlit-sales-query-agent/proposal.md:86-88`.

Avoid:
- No `eval`-based tool resolution.
- No generic shell command tool in the sales app.
- No generic SQL execution path exposed to the LLM without deterministic validation.

### C. Do not inherit OpenAI-specific classes as the production provider

Evidence:
- Reference notebooks use `ChatOpenAI`, `OpenAI`, and `OpenAIEmbeddings` at `/home/sebastian-ramirez/trabajo/eci_genai/6_langchain.ipynb:121-123` and `ChatOpenAI` in LangGraph at `/home/sebastian-ramirez/trabajo/eci_genai/7_langgraph.ipynb:76`.
- Current project target is Amazon Bedrock at `AGENTS.md:16`, `openspec/config.yaml:36`, and proposal lines `5`, `11`, `21`.

Avoid/defer:
- Treat OpenAI notebook examples as API-shape references only.
- Use Bedrock-compatible LangChain/LangGraph integration or boto3/AWS SDK behind an adapter.

### D. Do not adopt GPU/PyTorch dev container for this app unless later justified

Evidence:
- Reference `.devenv/Dockerfile` is `FROM pytorch/pytorch:2.8.0-cuda12.9-cudnn9-runtime` at `/home/sebastian-ramirez/trabajo/eci_genai/.devenv/Dockerfile:1`.
- Reference Compose reserves an NVIDIA GPU at `/home/sebastian-ramirez/trabajo/eci_genai/compose.yml:12-15`.
- Current sales app uses Bedrock as managed LLM and local SQLite; no local model/GPU need is indicated in `openspec/config.yaml:28-47`.

Avoid/defer:
- Do not use a CUDA/PyTorch base image for the initial app container.
- Prefer a slim Python/uv image unless local ML inference is explicitly added later.

### E. Defer RAG/vector-store patterns

Evidence:
- `6_langchain.ipynb` includes RAG with BeautifulSoup and `InMemoryVectorStore` at `/home/sebastian-ramirez/trabajo/eci_genai/6_langchain.ipynb:1053-1175`.
- Current first slice is SQL over `ventas`, not unstructured document retrieval; proposal non-goals exclude advanced routing and focus on SQL table output at `proposal.md:28-34`.

Avoid/defer:
- No RAG/vector DB in first slice unless the assignment scope changes.
- The relevant schema context is small enough to pass directly to the LLM/agent.

---

## 3. Implications for SDD spec/design

### Framework decision

Recommended design choice: **LangGraph over plain LangChain for first slice**, because the reference already demonstrates state graphs, tool nodes, conditional tool routing, memory/checkpoint hooks, and graph visualization (`7_langgraph.ipynb:77-79`, `936-955`, `1380-1399`, `1410-1411`). This maps cleanly to a multi-step SQL safety flow and makes the architecture teachable.

Spec/design should state:
- The LLM provider is Bedrock, not OpenAI.
- LangGraph is the orchestration layer, with provider-specific LLM hidden behind an adapter.
- If the implementation later chooses plain LangChain or Strands, it must explain why that is simpler while preserving MCP and SQL validation boundaries.

### Module boundaries

Current project rules require separation of Streamlit UI, agent orchestration, SQL/MCP access, visualization, export, config, and sample data at `AGENTS.md:125` and `openspec/config.yaml:88-92`. Design should define modules roughly as:
- `src/config.py`: environment/config validation; no secrets in source.
- `src/data_seed.py`: load `data/ventas.csv` into generated SQLite DB.
- `src/llm.py`: Bedrock chat/model adapter.
- `src/agent/graph.py`: LangGraph state and nodes.
- `src/sql_validation.py`: deterministic SQL validator; no network/LLM.
- `src/mcp_client.py` or `src/sql_tool.py`: narrow MCP query tool.
- `src/ui/streamlit_app.py` or `app.py`: UI only.
- Later: `src/visualization.py`, `src/exports.py`.

### SQL/MCP requirement must remain explicit

Evidence:
- Assignment requires MCP-compatible connectors where possible (`AGENTS.md:13`, `AGENTS.md:138`, `AGENTS.md:244`).
- Proposal makes MCP execution part of the first slice and says direct SQLite from Streamlit is not the target (`proposal.md:7`, `20`, `68-74`).
- Open question remains selecting the specific SQLite MCP connector and service/subprocess model at `proposal.md:95-96`.

Spec/design should include acceptance criteria for:
- A selected preexisting SQLite MCP server/connector, or a documented and justified deferral.
- MCP boundary is swappable and not hardwired into UI.
- Validation rejects non-`SELECT`, multiple statements, unknown tables/columns, and unsafe SQLite commands before MCP execution.

### Docker/Compose design

Reference Compose is useful only as a pattern for dev ergonomics (`compose.yml:1-8`, Makefile `build-devenv`/`connect-devenv` at `Makefile:9-14`), not as app topology. Design should specify:
- App container built with `uv` from `pyproject.toml`/`uv.lock`.
- SQLite MCP server as separate service if feasible; otherwise a managed subprocess with explicit rationale.
- Shared volume/bind mount for generated DB.
- `.env.example` with non-secret config; no real `.env` or AWS credentials committed.
- Local AWS credentials via host credential chain or read-only mount, consistent with proposal `proposal.md:56-60`, `89-90`.

### Educational/rubric alignment

Design/spec should include user-visible transparency and demo readiness:
- UI shows generated SQL before result (`proposal.md:24`, `73`).
- README/design should explain problem, methodology, results/limitations, matching `proyecto.ipynb:105-141`.
- The app must run and demonstrate GenAI API usage, matching rubric evidence at `proyecto.ipynb:55-67`.

---

## 4. Compact meta-prompt for next SDD design/spec agent

**Goal**: Produce/update SDD spec and design artifacts for `openspec/changes/streamlit-sales-query-agent` using `eci_genai` as reference context, selecting a concrete first-slice architecture for a Streamlit sales query agent over `ventas` with Bedrock, LangGraph/LangChain-compatible orchestration, SQL validation, and MCP SQL access.

**Context/evidence**:
- Current repo has no runnable app or verified `pyproject.toml`, `uv.lock`, Streamlit app, Dockerfile, compose file, or tests (`AGENTS.md:26-27`, `AGENTS.md:217-229`).
- Target constraints: Streamlit UI, Docker packaging, `uv`, Bedrock, semantic LLM intent detection, modular architecture, MCP-compatible SQL connector preference (`AGENTS.md:13-19`, `AGENTS.md:124-141`; `openspec/config.yaml:13-17`, `28-47`, `88-92`).
- Proposal first slice requires seed CSV, generated SQLite DB, SQLite MCP access, Bedrock SQL generation, single-statement read-only SQL validation, generated SQL transparency, and table output (`proposal.md:17-26`, `65-75`, `86-96`).
- Reference `eci_genai` has transferable `uv`/dependency group pattern (`pyproject.toml:1-20`), self-documenting Makefile (`Makefile:4-14`), Compose dev service pattern (`compose.yml:1-8`), and LangGraph tool-routing/state examples (`7_langgraph.ipynb:77-79`, `936-955`, `1380-1399`).
- Avoid copying notebook-time `pip install`, OpenAI provider classes, `eval` tool dispatch, generic shell tools, GPU/PyTorch image, and RAG/vector-store scope (`6_langchain.ipynb:92`, `121-123`, `1718-1719`, `1833-1854`; `.devenv/Dockerfile:1`; `compose.yml:12-15`).

**Success criteria**:
- Spec uses RFC 2119 requirements and covers NL question -> Bedrock semantic SQL generation -> SQL validation -> MCP execution -> Streamlit table output.
- Design selects or narrows a concrete agent framework choice; recommended default is LangGraph because the reference demonstrates state, conditional edges, ToolNode, MemorySaver, and graph visualization.
- Design defines clear module boundaries for UI, config, Bedrock adapter, graph/orchestration, SQL validation, MCP client/tool, data seeding, and future visualization/export.
- Design explicitly resolves or flags the SQLite MCP connector/service choice; if unresolved, it must be an explicit design risk/open question, not hidden.
- Docker/Compose plan avoids GPU/PyTorch unless justified and keeps credentials/secrets out of source/images.

**Hard constraints**:
- Do not implement app code in the design/spec phase.
- Do not claim commands are verified until files exist and commands have been run.
- Do not replace MCP with direct SQLite access without explicit justification and a swappable boundary.
- Do not route output intent with brittle fixed keyword checks; semantic LLM inference is required.
- Do not expose shell tools or unrestricted SQL tools to the LLM.

**Suggested approach**:
1. Use LangGraph as the recommended orchestration unless choosing LangChain/Strands is explicitly justified.
2. Define a typed state and nodes: generate SQL, validate SQL, execute via MCP, format result.
3. Specify a deterministic SQL validator independent of the LLM.
4. Specify `pyproject.toml` dependency categories and Docker/Compose topology conceptually, but avoid exact unverified commands unless planned as future commands.
5. Include educational/demo considerations from `proyecto.ipynb`: problem, methodology, runnable demo, visible GenAI/API use, results/limitations.

**Validation for design/spec agent**:
- Check artifact consistency with `openspec/config.yaml` and proposal.
- Ensure spec scenarios cover happy path, invalid SQL rejection, Bedrock config failure, MCP connector failure, empty result, and unsupported output requests in first slice.
- Ensure design includes future extension points for charts, CSV, and Excel without implementing them in first slice.

**Stop/escalation rules**:
- Ask the supervisor/user before finalizing if the design must choose a specific SQLite MCP connector but local evidence is insufficient.
- Stop if requirements drift into implementing charts/exports/Docker fully in the first slice; those are non-goals/deferred by proposal unless explicitly approved.
- Enough evidence is available to recommend LangGraph and `uv`/Compose patterns; no need to rediscover notebooks unless checking exact snippets.

**Resolved assumptions**:
- `eci_genai` is a reference/teaching project, not an implementation to copy.
- Bedrock is the target LLM provider for this assignment even though reference notebooks use OpenAI.
- GPU/CUDA dependencies are not needed for the initial sales agent.
