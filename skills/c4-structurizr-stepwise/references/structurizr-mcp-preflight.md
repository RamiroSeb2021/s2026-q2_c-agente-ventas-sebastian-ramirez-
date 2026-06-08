# Structurizr MCP Preflight

Use this before architecture analysis so C4 DSL can be validated when possible.

## Purpose

The Structurizr MCP server can validate, parse, inspect, and export Structurizr DSL. Use it as a guardrail for DSL correctness, not as a substitute for architectural judgment or user review.

## Repository-derived notes

The upstream repo is `https://github.com/structurizr/structurizr` and includes a `structurizr-mcp` module. Relevant verified files:

- `README.md` — Structurizr is the C4 reference implementation and recommends playground or local Docker for quickstart.
- `pom.xml` — multi-module Java/Maven repo using Java 21; modules include `structurizr-dsl`, `structurizr-export`, `structurizr-inspection`, and `structurizr-mcp`.
- `structurizr-mcp/pom.xml` — MCP server is a Spring Boot WAR, version `1.0.0`, using `structurizr-dsl`, `structurizr-export`, `structurizr-inspection`, and Spring AI MCP server WebMVC.
- `structurizr-mcp/src/main/java/com/structurizr/mcp/Server.java` — supported profiles/options are `-dsl`, `-server-create`, `-server-read`, `-server-update`, `-server-delete`, `-plantuml`, and `-mermaid`; if no options are given, it defaults to `-dsl`.
- `structurizr-mcp/src/main/java/com/structurizr/mcp/DslTools.java` — registers MCP tools named `validate`, `parse`, and `inspect`.
- `MermaidTools.java` and `PlantUMLTools.java` — register `export-mermaid`, `export-plantuml`, and `export-c4plantuml`.
- `structurizr-mcp/Dockerfiles/eclipse-temurin-alpine` — expects Java 21, `PORT` env default `8080`, copies built WAR and bundled themes.
- `mcp.sh` — runs `java -jar structurizr-mcp/target/structurizr-mcp-1.0.0.war $@` after building from source.

Implication for this skill: use the prebuilt `structurizr/mcp` image for normal local validation; build from source only when explicitly needed.

## Preflight order

1. Check whether an MCP connector for Structurizr is already available in the active agent/client.
2. Inspect the repo for existing MCP/Docker setup files: MCP config, `compose.yaml`, `docker-compose*.yml`, `Dockerfile`, docs, or scripts mentioning `structurizr/mcp`, `mcp.structurizr.com`, `-dsl`, `-mermaid`, or `-plantuml`.
3. Check Docker availability only with read-only commands when needed, such as `docker --version` and `docker compose version`.
4. If no validator exists, propose a local setup using `../assets/structurizr-mcp-compose.yaml`.
5. Stop for user approval before pulling images, starting containers, editing MCP config, or installing bridge packages such as `mcp-remote`.

## Safe local setup proposal

Prefer local Docker over the public remote MCP when the DSL may reveal private architecture. The public endpoint `https://mcp.structurizr.com/mcp` is convenient, but sends DSL to an external service.

Use the local MCP with DSL/export tools enabled:

```bash
docker compose -f skills/c4-structurizr-stepwise/assets/structurizr-mcp-compose.yaml up -d
```

The compose asset maps host `3000` to container `3000` and sets `PORT=3000`; this intentionally overrides the upstream Dockerfile default of `8080`.

Then configure the active client to connect to:

```text
http://localhost:3000/mcp
```

Some clients that require stdio may need a bridge such as `mcp-remote`; inspect package/install risk before installing it.

## What to do after validation

For every C4 level:

1. Draft the DSL.
2. Validate with MCP tool `validate` if available.
3. Inspect with MCP tool `inspect` when the DSL parses.
4. Optionally parse with MCP tool `parse` when JSON workspace inspection helps.
5. Export with `export-mermaid`, `export-plantuml`, or `export-c4plantuml` only when the user asks for those formats.
6. Fix parser or inspection issues.
7. Present the corrected DSL to the person.
8. Wait for human review.
9. Apply requested corrections.
10. Save the accepted model state to Engram.
11. Continue to the next level only after approval.

## Do not

- Do not run Docker pulls/containers without approval.
- Do not send private DSL to the public Structurizr MCP without approval.
- Do not modify global MCP/client configuration without approval.
- Do not treat MCP validation as proof that the architecture is correct.
