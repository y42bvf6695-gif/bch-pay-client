# HEARTBEAT.md Template

```markdown
# Keep this file empty (or with only comments) to skip heartbeat API calls.

# Add tasks below when you want the agent to check something periodically.
```

## Moltbook (cada 30 min)
Si han pasado 30 minutos desde la última revisión de Moltbook:
1. Obtener credenciales desde ~/.config/moltbook/credentials.json
2. GET https://www.moltbook.com/api/v1/home con Authorization Bearer
3. Revisar notificaciones, feed, y mensajes directos
4. Actualizar `lastMoltbookCheck` en memory/heartbeat-state.json
