# Session checklist — Engram entre computadoras

## Antes de empezar

1. `git pull`
2. `engram sync --import`
3. `engram sync --status`
4. Confirmar que no hay dudas de continuidad

## Durante la sesión

1. Una sola máquina escritora por bloque de trabajo
2. No reutilizar mismo `topic_key` si hubo trabajo paralelo no fusionado
3. Si hay conflicto, usar `merge-pendiente`

## Al cerrar

1. `engram sync`
2. `git add .engram/`
3. commit/push
