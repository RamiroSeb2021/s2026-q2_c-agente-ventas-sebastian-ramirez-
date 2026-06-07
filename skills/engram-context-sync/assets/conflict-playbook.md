# Conflict playbook — `topic_key` repetido

## Problema

Dos máquinas escribieron el mismo `topic_key` sin importar antes el estado más reciente.

## Estrategia segura

1. No sobrescribir de inmediato el `topic_key` canónico.
2. Guardar una de las versiones con clave temporal:
   - `contexto/<tema>/merge-pendiente/<maquina-o-fecha>`
3. Leer ambas versiones.
4. Fusionar manualmente contenido correcto.
5. Actualizar el `topic_key` canónico una sola vez.
6. `engram sync` y commit de `.engram/`.

## Regla operativa

Si no hay certeza sobre cuál versión es la más reciente, parar y revisar antes de seguir trabajando con memoria evolutiva.
