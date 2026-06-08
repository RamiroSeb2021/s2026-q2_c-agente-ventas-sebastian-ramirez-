## Exploration: Streamlit Chat UI

> Historical note: this exploration predates the implemented MCP runtime and semantic chart/export outputs. It is kept as a planning artifact only; the current source of truth is `openspec/changes/streamlit-sales-query-agent/` plus the inspected application files.

### Current State
The current app is a form-style Streamlit entrypoint: `st.text_area` plus an `Ask` button. On submit, it loads config, creates a Bedrock runtime client, calls `answer_sales_question`, then renders generated SQL and table results as standalone sections. Out-of-scope questions are already represented by `OutOfScopeQuestionError` and shown as `st.info`, but not inside an assistant chat bubble.

The supporting flow already separates UI from `sales_query_agent.query_service`, `bedrock_client`, `database`, and `sql_validation`. Runtime SQL execution is currently a temporary direct SQLite boundary in `database.py`, with comments noting MCP remains the target. OpenSpec already has a related change, `streamlit-sales-query-agent`, whose Slice 4 covers Streamlit UI work; it should be updated rather than creating a competing full change.

The reference Bedrock repo uses the desired chat pattern in `app.py`: initialize `st.session_state.messages`, render history with `st.chat_message`, accept input with `st.chat_input`, append a user message immediately, then append/render the assistant response.

### Affected Areas
- `app.py` — primary refactor target from form-style UI to chat-style message history while preserving generated SQL/table transparency.
- `src/sales_query_agent/query_service.py` — likely stays stable; may need a richer UI-friendly result model only if assistant messages need structured content beyond SQL/rows.
- `src/sales_query_agent/bedrock_client.py` — out-of-scope sentinel already maps to `OutOfScopeQuestionError`; no UI refactor should bypass this semantic boundary.
- `src/sales_query_agent/database.py` — current direct SQLite boundary remains a known temporary implementation detail; future MCP replacement should preserve returned columns/rows for chat rendering.
- `tests/test_query_service.py` and `tests/test_bedrock_client.py` — current behavior tests already cover generated SQL, rows, unsafe SQL, and out-of-scope handling; add a focused UI smoke/helper test only if UI logic is extracted from `app.py`.
- `openspec/changes/streamlit-sales-query-agent/*` — existing related proposal/design/spec/tasks should be amended to mention chat-style UI in Slice 4.

### Approaches
1. **Refactor `app.py` directly to Streamlit chat** — Keep business flow unchanged, but replace `st.text_area`/button rendering with `st.session_state.messages`, `st.chat_message`, and `st.chat_input`.
   - Pros: Smallest diff; follows reference pattern closely; low risk to tested query/Bedrock/SQL modules.
   - Cons: Harder to unit-test Streamlit rendering if all formatting stays inline.
   - Effort: Low

2. **Extract chat message formatting helpers** — Add a small UI helper/model layer that converts query results, empty results, errors, and refusals into renderable assistant message entries.
   - Pros: More testable; better foundation for future charts/CSV/Excel attachments in chat messages.
   - Cons: More files and changed lines; may exceed the small refactor budget if over-designed.
   - Effort: Medium

### Recommendation
Update the existing `streamlit-sales-query-agent` OpenSpec change instead of creating a separate implementation change. Treat `streamlit-chat-ui` as an exploration artifact/change only, because the behavior is a refinement of Slice 4 rather than a new capability boundary.

Implement the direct `app.py` refactor first, borrowing the reference repo's chat primitives but not its AWS-topic prompt behavior. Store structured entries in session state, for example user messages as text and assistant messages as `{content, generated_sql, rows}` so the assistant bubble can render refusal text, SQL code, and `st.dataframe` together. Keep `answer_sales_question` as the app-facing service call.

### Risks
- Streamlit session-state entries must store only serializable/simple structures; dataclass instances may work in-session but plain dicts are safer.
- Rendering `st.dataframe(result.rows)` works today, but preserving column order may require using `result.columns` or a dataframe later.
- Out-of-scope handling must remain model/semantic-driven via `OutOfScopeQuestionError`, not hardcoded UI keyword checks.
- The existing OpenSpec config is stale in places: it says no runnable Streamlit/Bedrock implementation exists, while current files prove `app.py`, Bedrock adapter, validation, and tests now exist.
- Earlier exploration treated MCP as deferred; current implementation uses `mcp-server-sqlite` through the MCP Python SDK, so do not use this historical note as current-state evidence.

### Ready for Proposal
Yes — tell the user to update the existing `streamlit-sales-query-agent` change with a chat-style UI amendment, then implement a small Slice 4 refactor in `app.py`: initialize chat history, use `st.chat_input`, append the user's question, render assistant responses containing generated SQL plus table/empty state, and render polite refusals inside assistant messages.
