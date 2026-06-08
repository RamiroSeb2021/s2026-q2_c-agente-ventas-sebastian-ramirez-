# Sales Query Agent Specification

## Purpose

Define the sales analysis agent behavior across the current Streamlit/Bedrock/LangGraph/MCP/SQLite slice. Current implementation uses deterministic local data generation, Amazon Bedrock for semantic intent and SQL generation, a minimal LangGraph agent boundary, deterministic SQL validation, `mcp-server-sqlite` for MCP-mediated SQLite execution, and a chat-style Streamlit table interface.

### Requirement: Minimal Agent Framework Boundary

The system MUST route Streamlit questions through an agent framework boundary instead of wiring the UI directly to Bedrock and SQL execution.

#### Scenario: Streamlit delegates to LangGraph boundary

- GIVEN the user submits a supported sales question in the Streamlit chat UI
- WHEN the app processes the request
- THEN the app MUST call the LangGraph sales agent boundary
- AND the LangGraph boundary MUST return the generated SQL and table result without the UI calling Bedrock or SQLite directly

## Requirements

### Requirement: Deterministic Sales Data Seeding

The system MUST provide a deterministic Python seed process that generates simulated sales data for the `ventas` domain model using a fixed random seed.

#### Scenario: Deterministic seed reproducibility

- GIVEN the seed process is run twice with the same configured fixed random seed
- WHEN it generates the sales dataset artifacts
- THEN the resulting `ventas` records MUST be equivalent across runs
- AND the resulting dataset MUST include the columns `id`, `vendedor`, `sede`, `producto`, `cantidad`, `precio`, and `fecha`

### Requirement: Generated Data Artifact Policy

The system MUST treat generated sales datasets and generated SQLite database files as reproducible artifacts rather than committed source of truth.
The project MUST keep generated database artifacts out of required committed first-slice source inputs.

#### Scenario: Generated artifacts are not treated as source

- GIVEN the project contains a deterministic seed process for sales data
- WHEN generated database artifacts such as `data/sales.db` are created
- THEN the seed process and fixed seed configuration MUST remain the source of truth for regenerating them
- AND generated artifacts MUST be safe to delete and recreate from the seed process
- AND generated artifacts MUST NOT be required as committed source inputs for first-slice behavior

### Requirement: Seed Initialization Before Query Service Use

The local setup MUST run the seed or initialization process before the application database dependency relies on the SQLite database. Current Compose packaging includes a one-shot `seed` service that runs before the app service.

#### Scenario: Seed/init runs before app or MCP depends on DB

- GIVEN the generated SQLite database is required for query execution
- WHEN the local environment or Docker Compose starts the system for the first slice
- THEN the seed or initialization process MUST run before the app or future MCP dependency attempts to query the database
- AND the app MUST NOT assume a precommitted database artifact exists in the repository

### Requirement: Bedrock for Semantic SQL Generation Only

The system MUST use Amazon Bedrock for semantic intent interpretation and SQL generation only.

#### Scenario: Bedrock generates SQL for a sales question

- GIVEN a natural-language sales question and the known `ventas` schema
- WHEN the agent asks Bedrock to help fulfill the request
- THEN Bedrock MUST be used to infer intent and generate a candidate SQL query
- AND Bedrock MUST NOT be used as the source of dataset creation or mutation

#### Scenario: Bedrock configuration or model access fails

- GIVEN the application cannot access the configured Bedrock region, credentials, or model
- WHEN a user submits a sales question
- THEN the system MUST stop before attempting SQL execution
- AND the UI MUST show a clear user-facing error that the Bedrock request could not be completed
- AND the error shown to the user MUST NOT require exposing raw secrets or stack traces

### Requirement: Streamlit Chat Natural-Language Query Interface

The system MUST provide a chat-style Streamlit user interface that accepts natural-language sales questions for the first slice.

#### Scenario: User enters a natural-language question

- GIVEN the Streamlit app is available to the user
- WHEN the user asks a sales question in natural language
- THEN the system MUST accept the question through a chat input without requiring brittle fixed prompt keywords
- AND the user's question MUST appear as a user chat message
- AND the question MUST be routed to the semantic intent and SQL generation flow

#### Scenario: Prior chat messages remain visible

- GIVEN the user has already asked one or more questions in the current Streamlit session
- WHEN the app rerenders
- THEN prior user and assistant messages MUST remain visible from `st.session_state.messages`

### Requirement: Read-Only SQL Validation

The system MUST validate generated SQL before MCP execution and permit only a single read-only `SELECT` statement.
The system MUST require a numeric `LIMIT` clause for generated sales queries to avoid unbounded full-table dumps.
For this slice, validation is intentionally conservative token/regex validation rather than full SQL parsing.

#### Scenario: Unsafe SQL is rejected before MCP

- GIVEN Bedrock returns SQL that is not a single read-only `SELECT` statement
- WHEN the system validates the SQL before MCP execution
- THEN the system MUST reject the SQL before any MCP database call is made
- AND the system MUST present a clear user-facing validation failure

#### Scenario: Unknown table or column is rejected

- GIVEN Bedrock returns SQL that references a table other than `ventas` or references columns outside `id`, `vendedor`, `sede`, `producto`, `cantidad`, `precio`, and `fecha`
- WHEN the system validates the SQL
- THEN the system MUST reject the SQL before MCP execution
- AND the system MUST identify the query as outside the allowed schema boundary

#### Scenario: Query without LIMIT is rejected

- GIVEN Bedrock returns a valid read-only `SELECT` query against `ventas` without a numeric `LIMIT` clause
- WHEN the system validates the SQL
- THEN the system MUST reject the SQL before query execution
- AND the system MUST tell the user that a `LIMIT` clause is required

#### Scenario: Common SQLite read-only operators are accepted

- GIVEN Bedrock returns a valid read-only `SELECT` query against `ventas` using common SQLite syntax such as `DISTINCT`, `IN`, `LIKE`, `IS NOT NULL`, `CASE`, `HAVING`, or `OFFSET`
- WHEN the system validates the SQL
- THEN the validator MUST treat those SQL syntax tokens as language constructs rather than unknown column names
- AND the query MUST still satisfy the single-statement, read-only, allowed-schema, and numeric `LIMIT` guardrails

#### Scenario: Validator remains intentionally narrow

- GIVEN Bedrock returns a SQL construct outside the first-slice validator subset
- WHEN the system validates the SQL before MCP execution
- THEN the system MAY reject the query even if SQLite could execute it
- AND the accepted subset MUST remain guarded by single-statement `SELECT`, schema allowlist, blocked keyword rejection, comment rejection, numeric `LIMIT`, and MCP `read_query` execution only

#### Scenario: Full-table request is safely limited

- GIVEN the user asks to show all sales rows or explicitly asks for no limit
- WHEN Bedrock generates SQL for the request
- THEN the generated SQL MUST still include a safe numeric `LIMIT` clause
- AND the system MUST NOT execute an unbounded full-table query

### Requirement: MCP-Mediated SQLite Query Execution

The system MUST execute validated queries through a preexisting SQLite MCP server or connector rather than direct in-process application querying.
The current implementation uses `mcp-server-sqlite` and its `read_query` tool.
The MCP connection MUST be fixed/configured through environment or deployment configuration, not dynamically registered as an arbitrary user-provided MCP server from the Streamlit UI.

#### Scenario: MCP connector unavailable

- GIVEN the SQL query has passed validation
- WHEN the configured SQLite MCP server or connector is unavailable or returns an execution failure
- THEN the system MUST report that query execution could not be completed through the MCP dependency
- AND the UI MUST show a clear failure state instead of a misleading successful result

#### Scenario: User checks configured MCP status

- GIVEN the Streamlit app has a configured SQLite MCP connection
- WHEN the user views the app settings or clicks a connection test control
- THEN the UI MUST show the configured MCP status as connected or disconnected
- AND the UI MUST NOT require the user to manually register arbitrary MCP commands, transports, or credentials from the browser

### Requirement: SQL Transparency in the UI

The system MUST always display the generated SQL to the user before or alongside the result for the first slice.

#### Scenario: SQL is visible for a successful query

- GIVEN a user asks a supported sales question
- WHEN the system generates a valid SQL query
- THEN the assistant chat message MUST display the generated SQL to the user
- AND the SQL display MUST occur for the first-slice supported flow regardless of whether the result is empty or non-empty

### Requirement: Table Result Output

The system MUST render supported first-slice query results as a table in the Streamlit UI.

#### Scenario: Happy path top products query

- GIVEN the seeded `ventas` data includes sales in Medellín
- WHEN the user asks for the top products sold in Medellín
- THEN the system MUST generate a SQL query for that request
- AND the system MUST display the generated SQL in the assistant chat message
- AND the system MUST show the returned records as a table in the assistant chat message

#### Scenario: Empty query result

- GIVEN a validated SQL query executes successfully through the MCP dependency
- WHEN the query returns no rows
- THEN the system MUST keep the generated SQL visible
- AND the assistant chat message MUST show a clear empty-result state instead of treating the query as an execution failure

### Requirement: Out-of-Scope Chat Refusal

The system MUST politely refuse questions outside the sales-analysis scope in an assistant chat message.

#### Scenario: Out-of-scope question is refused without SQL or table

- GIVEN the user asks a question that is not about the `ventas` sales data
- WHEN Bedrock classifies the request as outside the supported scope
- THEN the assistant chat message MUST show a polite refusal
- AND the assistant message MUST NOT show generated SQL
- AND the assistant message MUST NOT show a dataframe or result table

### Requirement: First-Slice Unsupported Output Handling

The system SHOULD clearly defer unsupported chart or export requests in the first slice. This behavior is planned but not yet fully implemented in the current chat UI; chart and CSV/Excel support remain future Slice 4 work.

#### Scenario: Unsupported chart or export request

- GIVEN the user asks for a chart, CSV, or Excel output during the first slice
- WHEN the request reaches the first-slice system behavior
- THEN the system MUST communicate that chart or export output is not yet supported in this slice
- AND the system MAY still continue with a supported table-oriented response only if doing so does not misrepresent the unsupported request as fully completed

### Requirement: Python Dependency Reproducibility

The system MUST use `uv` to manage Python dependencies and lockfile state for the project.

#### Scenario: Dependency definition is reproducible

- GIVEN the first slice defines Python dependencies for the app and supporting components
- WHEN the dependency configuration is prepared for local or containerized setup
- THEN the project MUST use `pyproject.toml` as the dependency source and `uv.lock` as the reproducible lock artifact
- AND downstream packaging assumptions for the app MUST align with `uv`-managed dependency resolution

### Requirement: Docker and Compose as Target Architecture

The system MUST treat Docker and Compose as the target runtime architecture for packaging this project, even if full Docker implementation is deferred to a later task.

#### Scenario: Packaging architecture is defined before full implementation

- GIVEN the first slice may defer complete Docker implementation work
- WHEN the system documents the first-slice behavior and architecture
- THEN the architecture MUST define Docker and Compose as the intended packaging path for the Streamlit app, seed/init process, and SQLite MCP dependency
- AND the deferred implementation MUST NOT change the first-slice requirements for deterministic seeding, MCP execution, SQL validation, or table output behavior
