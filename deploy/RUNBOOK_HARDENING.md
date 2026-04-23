# Runbook: Hardening de prod — Terminal Academy

Este runbook aplica los fixes del sprint F3 (systemd + backups + logging helper + rate-limit helper + healthcheck) sobre el VPS Hetzner `178.156.198.144` / `blitz.mexi.wtf`.

**Todo pensado para copy-paste.** No hay magia. Si algo falla, cada paso tiene su propio rollback.

Prerequisitos:
- SSH working contra `root@178.156.198.144`.
- Worktree local en `/home/mexi/Documents/_active/monadmty/.claude/worktrees/agent-a68195aa/` con los archivos ya creados (listado al final).
- El user revisó el diff.

---

## 0. Pre-flight desde la laptop

```bash
# Desde el worktree
cd /home/mexi/Documents/_active/monadmty/.claude/worktrees/agent-a68195aa/

# Verifica que todo existe
ls deploy/systemd/terminal-academy.service
ls deploy/scripts/backup_db.sh
ls deploy/scripts/crontab.txt
ls abyss-node/abyss_node/utils/logger.py
ls abyss-node/abyss_node/commands/unloggedin/ratelimit.py
ls abyss-node/abyss_node/web/website/views/healthcheck.py
```

---

## 1. systemd unit

### 1.1 Copiar archivo al VPS

```bash
scp deploy/systemd/terminal-academy.service \
    root@178.156.198.144:/etc/systemd/system/terminal-academy.service
```

### 1.2 Parar el proceso manual actual (si lo hay)

```bash
ssh root@178.156.198.144 <<'REMOTE'
set -e
# Si Evennia corre lanzado a mano, pararlo limpio primero (guarda state).
cd /root/monadmty/abyss-node/abyss_node
/root/monadmty/.venv/bin/evennia stop || true
# Esperar a que libere puertos (Evennia es lentito en full stop)
sleep 5
REMOTE
```

### 1.3 Enable + start vía systemd

```bash
ssh root@178.156.198.144 <<'REMOTE'
set -e
systemctl daemon-reload
systemctl enable terminal-academy
systemctl start terminal-academy
# Espera 10s a que Portal + Server arranquen
sleep 10
systemctl status terminal-academy --no-pager
REMOTE
```

Debe mostrar `active (running)`. Si dice `failed`, ver logs:

```bash
ssh root@178.156.198.144 "journalctl -u terminal-academy -n 100 --no-pager"
```

### 1.4 Smoke test

```bash
# Web debe responder desde fuera
curl -sS https://blitz.mexi.wtf/webclient/ | head -c 200
# Telnet debe responder desde el VPS (4100 está bloqueado externamente vía firewall)
ssh root@178.156.198.144 "echo quit | nc -w 2 localhost 4100 | head -c 200"
```

### 1.5 Rollback

Si el systemd unit se porta mal y querés volver al manual:

```bash
ssh root@178.156.198.144 <<'REMOTE'
systemctl stop terminal-academy
systemctl disable terminal-academy
rm /etc/systemd/system/terminal-academy.service
systemctl daemon-reload
# Arranque manual
cd /root/monadmty/abyss-node/abyss_node
/root/monadmty/.venv/bin/evennia start
REMOTE
```

---

## 2. Daily DB backup

### 2.1 Copiar script

```bash
scp deploy/scripts/backup_db.sh \
    root@178.156.198.144:/root/monadmty/deploy/scripts/backup_db.sh
```

(si `/root/monadmty/deploy/scripts/` no existe en prod, crearlo primero:)

```bash
ssh root@178.156.198.144 "mkdir -p /root/monadmty/deploy/scripts && chmod +x /root/monadmty/deploy/scripts/backup_db.sh"
```

### 2.2 Instalar sqlite3 (si no está)

```bash
ssh root@178.156.198.144 "command -v sqlite3 || apt-get update && apt-get install -y sqlite3"
```

### 2.3 PROBAR MANUALMENTE antes de cron

**No poner en cron hasta que un run manual termine OK.**

```bash
ssh root@178.156.198.144 "/root/monadmty/deploy/scripts/backup_db.sh && echo OK"
# Verificar que se creó el archivo
ssh root@178.156.198.144 "ls -lh /root/monadmty/backups/"
# Verificar log
ssh root@178.156.198.144 "tail /root/monadmty/backups/backup.log"
# Integridad del backup
ssh root@178.156.198.144 "sqlite3 /root/monadmty/backups/evennia.db3.* 'PRAGMA integrity_check;' | head"
```

Si todo da OK:

### 2.4 Instalar cron

```bash
# Abre el crontab del root
ssh root@178.156.198.144 "crontab -e"
```

Pegar el contenido de `deploy/scripts/crontab.txt` (la línea que NO empieza con `#`). Guardar + salir.

Verificar:

```bash
ssh root@178.156.198.144 "crontab -l"
```

### 2.5 Rollback

```bash
# Deshacer cron: editar y borrar la línea.
ssh root@178.156.198.144 "crontab -e"
# Borrar script
ssh root@178.156.198.144 "rm /root/monadmty/deploy/scripts/backup_db.sh"
```

Los backups ya hechos quedan en `/root/monadmty/backups/` — NO borrarlos en rollback, son la red de seguridad.

---

## 3. Structured logger helper

`abyss-node/abyss_node/utils/logger.py` — **nuevo archivo**, no pisa nada. No cambia comportamiento hasta que alguien importe `log_event` desde los comandos.

### 3.1 Sync vía deploy normal (rsync/scp) junto con el resto del código

```bash
# Si ya tenés un proceso de deploy, esto se mete en el próximo push.
# Opción ad-hoc:
scp abyss-node/abyss_node/utils/logger.py \
    root@178.156.198.144:/root/monadmty/abyss-node/abyss_node/utils/logger.py
```

### 3.2 Reload del server

```bash
ssh root@178.156.198.144 "systemctl reload terminal-academy"
# o si está manual todavía:
ssh root@178.156.198.144 "cd /root/monadmty/abyss-node/abyss_node && /root/monadmty/.venv/bin/evennia reload"
```

### 3.3 Verificar que se puede importar

```bash
ssh root@178.156.198.144 <<'REMOTE'
cd /root/monadmty/abyss-node/abyss_node
/root/monadmty/.venv/bin/python -c "from utils.logger import log_event; log_event('runbook_verify', ok=True)"
REMOTE
```

Debe imprimir un JSON line.

### 3.4 Rollback

Es un archivo aislado; borralo:

```bash
ssh root@178.156.198.144 "rm /root/monadmty/abyss-node/abyss_node/utils/logger.py && systemctl reload terminal-academy"
```

---

## 4. Rate-limit helper (NO conectado aún)

`abyss-node/abyss_node/commands/unloggedin/ratelimit.py` — **nuevo archivo, no integrado**. F7 lo va a enganchar al `CmdUnconnectedCreate`. Mientras tanto, sólo lo deployamos.

### 4.1 Copiar

```bash
scp -r abyss-node/abyss_node/commands/unloggedin \
    root@178.156.198.144:/root/monadmty/abyss-node/abyss_node/commands/
```

### 4.2 Verificar import

```bash
ssh root@178.156.198.144 <<'REMOTE'
cd /root/monadmty/abyss-node/abyss_node
/root/monadmty/.venv/bin/python -c "from commands.unloggedin.ratelimit import check_rate_limit; print(check_rate_limit('1.2.3.4'))"
REMOTE
```

Debe imprimir `(True, '')`.

### 4.3 Rollback

```bash
ssh root@178.156.198.144 "rm -rf /root/monadmty/abyss-node/abyss_node/commands/unloggedin"
```

---

## 5. Healthcheck `/health`

### 5.1 Copiar archivos

Cambios en 2 archivos:
- `web/website/views/healthcheck.py` (nuevo)
- `web/website/urls.py` (import + 2 paths agregados)

```bash
scp abyss-node/abyss_node/web/website/views/healthcheck.py \
    root@178.156.198.144:/root/monadmty/abyss-node/abyss_node/web/website/views/healthcheck.py

scp abyss-node/abyss_node/web/website/urls.py \
    root@178.156.198.144:/root/monadmty/abyss-node/abyss_node/web/website/urls.py
```

### 5.2 Reload

```bash
ssh root@178.156.198.144 "systemctl reload terminal-academy"
```

### 5.3 Probar

```bash
curl -sS https://blitz.mexi.wtf/health
# Esperado: {"status": "ok", "service": "terminal-academy", "version": "...", "uptime_sec": N, "db": "ok"}

curl -sS -o /dev/null -w "%{http_code}\n" https://blitz.mexi.wtf/health
# Esperado: 200
```

### 5.4 Configurar monitor externo

En UptimeRobot / Better Stack:
- URL: `https://blitz.mexi.wtf/health`
- Método: GET
- Intervalo: 60s
- Alerta si HTTP != 200 por 2 checks consecutivos.

### 5.5 Rollback

```bash
# Reverter urls.py al previo (git) y borrar la view
ssh root@178.156.198.144 <<'REMOTE'
cd /root/monadmty
git checkout HEAD -- abyss-node/abyss_node/web/website/urls.py
rm abyss-node/abyss_node/web/website/views/healthcheck.py
systemctl reload terminal-academy
REMOTE
```

---

## 6. Post-deploy checklist

```bash
# 1. Servicio activo
ssh root@178.156.198.144 "systemctl is-active terminal-academy"
# -> active

# 2. DB responde
curl -sS https://blitz.mexi.wtf/health | python3 -m json.tool

# 3. Web client funciona
curl -sS -I https://blitz.mexi.wtf/webclient/ | head -1
# -> HTTP/2 200

# 4. Backups cron instalado
ssh root@178.156.198.144 "crontab -l | grep backup_db"

# 5. Logs fluyendo a journald
ssh root@178.156.198.144 "journalctl -u terminal-academy -n 20 --no-pager"
```

---

## 7. Comandos útiles después del deploy

```bash
# Ver logs en vivo
ssh root@178.156.198.144 "journalctl -u terminal-academy -f"

# Filtrar solo eventos estructurados (cuando F* migre prints a log_event)
ssh root@178.156.198.144 "journalctl -u terminal-academy -o cat | grep '^{' | jq ."

# Contar backups y tamaño total
ssh root@178.156.198.144 "ls /root/monadmty/backups/ | wc -l && du -sh /root/monadmty/backups/"

# Forzar un backup ad-hoc (ej. antes de migración)
ssh root@178.156.198.144 "/root/monadmty/deploy/scripts/backup_db.sh"

# Restore desde backup (COPY del backup sobre el DB — requiere server STOPPED)
ssh root@178.156.198.144 <<'REMOTE'
systemctl stop terminal-academy
cp /root/monadmty/abyss-node/abyss_node/server/evennia.db3 /root/monadmty/evennia.db3.before-restore
cp /root/monadmty/backups/evennia.db3.20260422_030000 /root/monadmty/abyss-node/abyss_node/server/evennia.db3
systemctl start terminal-academy
REMOTE
```

---

## 8. Lo que este runbook NO cubre (riesgos residuales)

Ver `TODO_STABILITY.md` para la lista completa. Lo más crítico sin resolver:

| # | Item | Por qué importa |
|---|---|---|
| 2 | Nonce cache persistente | Crash mid-tx puede colisionar nonces en la siguiente arranque |
| 3 | Wallet balance alertas | Si la hot wallet se queda sin MON, los claims fallan silenciosamente |
| 5 | PK rotation plan | PK en `.env` — si se filtra, adiós fondos |
| 7 | Sentry error tracking | Tracebacks en prod quedan en logs, no alertan |
| 9 | Anti-abuse con email/captcha | Rate limit local no frena bots con rotación de IP |
| 11 | CI/CD con rollback auto | Cada deploy es manual; fácil romper prod |
| 15 | Migrar a PostgreSQL | SQLite tope ~100 users concurrentes |
| 29 | Multi-sig ownership del contrato | Single point of failure crítico |

El **backup diario + systemd + healthcheck + helpers** de este sprint cubre el *"si reinicia el VPS / si se corrompe el DB / si quiero saber si el site está vivo"*. Los items de arriba son el siguiente nivel.

---

## 9. Archivos tocados por este sprint

Todos listos en el worktree `agent-a68195aa`:

```
deploy/
├── RUNBOOK_HARDENING.md                   # este archivo
├── systemd/
│   └── terminal-academy.service
└── scripts/
    ├── backup_db.sh                       # +x
    └── crontab.txt

abyss-node/abyss_node/
├── utils/
│   └── logger.py                          # NUEVO (helper)
├── commands/unloggedin/
│   ├── __init__.py                        # NUEVO
│   └── ratelimit.py                       # NUEVO (helper; no enchufado)
└── web/website/
    ├── urls.py                            # MODIFICADO (+ 2 paths /health)
    └── views/
        └── healthcheck.py                 # NUEVO
```
