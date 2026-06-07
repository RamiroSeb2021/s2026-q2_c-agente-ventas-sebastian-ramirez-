# Design — `find-skills-copy-local`

## Problem

Juanchito ya usa skills locales en `skills/`, pero faltaba un workflow explícito para:

1. descubrir skills públicas del ecosistema abierto,
2. evaluarlas con criterio,
3. traerlas al repo local de forma reproducible.

El problema NO es solo descubrir skills. También hay que resolver la integración local para OpenCode/Codex/Claude sin depender de memoria tribal.

## Goals

- Reusar la idea de `find-skills` de Vercel para discovery.
- Adaptarla al layout real de Juanchito (`skills/`, `.claude/skills`, `.codex/skills`).
- Dejar un workflow claro para copiar/vendorizar skills externas dentro del repo.
- Evitar instalaciones globales cuando el objetivo es mantener la skill como parte del proyecto.

## Non-Goals

- No automatizar descarga masiva de skills.
- No reemplazar `skill-creator` para skills 100% locales.
- No ocultar riesgos de licencia, autoría o mantenimiento upstream.

## Key Decisions

### 1. Skill de workflow, no script ejecutable

Se implementa como skill documental-operativa (`SKILL.md`) porque el valor principal es guiar la decisión correcta del agente y del humano.

### 2. Project-local first

Se privilegia instalación en scope de proyecto porque este repo ya usa symlinks (`.claude/skills -> skills/`, `.codex/skills -> skills/`) y eso reduce drift entre asistentes.

### 3. Copy > symlink para vendoring

Cuando una skill externa pasa a formar parte del repo, se prefiere copia local/versionable sobre dependencia implícita a un path externo.

### 4. Validación explícita posterior

El workflow obliga a chequear `npx skills list --json`, porque instalar no garantiza que el runtime actual del asistente ya la vea.

## Expected Outcome

Cuando alguien pida “buscá una skill y traela local”, el asistente debería:

1. descubrir candidatas públicas,
2. filtrar calidad,
3. instalar/copiar al proyecto,
4. registrar y propagar la skill localmente,
5. reiniciar el runtime si hace falta.
