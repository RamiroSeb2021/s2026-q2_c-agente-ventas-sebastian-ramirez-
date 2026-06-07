# Commit message template

```text
<type>(<scope>): <short title>

Changes:
- <what changed, grouped by file/topic, based only on the diff>

Rationale:
- <why the change was needed and what risk, user need, or workflow gap it addresses>

Related docs:
- <docs, skills, ADRs, README sections, or "None">

Safety/Scope:
- <important boundaries, exclusions, or non-goals>

Verification:
- <commands, manual diff review, tests, or not run with reason>
```

## Notes

- `type` recomendado: `docs`, `feat`, `fix`, `chore`, `refactor`, `test`
- título: Conventional Commit en inglés, máximo 72 caracteres
- líneas del cuerpo: máximo 100 caracteres por línea
- mensaje completo: máximo 1200 caracteres
- si el mensaje supera 1200 caracteres o mezcla temas, dividir en commits por tema
- temas típicos: `docs`, `skills`, `tests`, `code`, `config`, `data/context`
- cuerpo: qué se hizo, dónde cambió, por qué se hizo, docs relacionados y verificación
