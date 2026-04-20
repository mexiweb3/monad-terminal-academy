# Terminal Academy — TODO de estabilidad

> Lo que queda pendiente para convertir el demo de hackathon en un sistema **production-grade**. Ordenado por impacto y categorizado.

Estado actual (2026-04-20): prod en `https://blitz.mexi.wtf/` sobre Hetzner cpx11, sin systemd, sin monitoreo, SQLite sin backup, hot wallet con PK en `.env`.

---

## 🔴 Crítico — puede romper el servicio

### 1. systemd unit para Evennia
**Síntoma**: si el VPS reinicia, el juego queda caído hasta que alguien haga SSH y arranque manual.
**Fix**: `/etc/systemd/system/evennia.service` con `ExecStart=... evennia start --log` + `Restart=always`. También `evennia.timer` opcional para auto-reload diario.
**Effort**: 30 min.

### 2. Nonce-cache drift en crash
**Síntoma**: nonce está en memoria (`_nonce_cache`). Si el server muere durante una tx pending en mempool, al reinicio refetchea `get_transaction_count(pending)` — pero si la red ya aceptó la pending pero el RPC aún no la refleja, hay colisión.
**Fix**: persistir `_nonce_cache["next"]` en un JSON file + reconciliar con `pending` al arranque (tomar max entre lo persistido y el RPC).
**Effort**: 1 h.

### 3. Wallet balance monitoring + alertas
**Síntoma**: si la hot wallet baja de X MON, los claims fallan con "insufficient balance" sin avisar al admin.
**Fix**: un ticker cada hora que lee `cast balance` y si está <0.5 MON, envía alerta (Telegram bot / email / webhook Slack).
**Effort**: 2 h.

### 4. SQLite backup + restore
**Síntoma**: `abyss_node/server/evennia.db3` tiene todas las accounts, wallets linkeadas, quest progress, fragmentos recolectados. Si se corrompe o el disco muere, perdemos TODO.
**Fix**: cronjob diario `sqlite3 evennia.db3 ".backup /backup/$(date +%F).db3"` + rotación 7 días + sync a S3 / Backblaze B2.
**Effort**: 2 h.

### 5. Private key rotation plan
**Síntoma**: PK de la hot wallet está en `deploy/.env`. Si se filtra (accidental commit, VPS comprometido, etc.) → alguien drena fondos + toma ownership del contrato.
**Fix documentado**:
- Generar nueva wallet con `cast wallet new`
- Deployar contrato nuevo (el actual no es upgradeable) o transferir ownership si implemento `transferOwnership` (el contrato actual sí lo tiene)
- Actualizar `deploy/.env` con nueva PK + address
- Rotar `ABYSS_CONTRACT` si redeploy
- Revocar allowances si hubo approvals
**Effort**: 30 min si tienes runbook listo; 2h si hay pánico.

### 6. Let's Encrypt auto-renew verificación
**Síntoma**: cert expira en 90 días. Certbot tiene timer systemd por default. Verificar que `systemctl status certbot.timer` esté activo.
**Fix**: comando único `systemctl enable --now certbot.timer` + `certbot renew --dry-run` para validar.
**Effort**: 10 min.

---

## 🟡 Importante — degrada UX

### 7. Logs centralizados + error tracking
**Síntoma**: logs en `server/logs/server.log` + `portal.log` + `lockwarnings.log`. Nadie los ve hasta que hay incidente. Python tracebacks invisibles al admin.
**Fix**: Sentry SDK para errors (`sentry-sdk[django]`) con DSN en `.env`. Logrotate para files locales. Opcional: journald + loki/grafana.
**Effort**: 1 h (Sentry solo); 4 h (stack completo).

### 8. Rate limiting de claims
**Síntoma**: un usuario puede spammear `claim` si acumula pending. Sin rate limit, se vacía la wallet.
**Fix**: (a) server-side: max 1 claim / wallet / 6 h en `onchain.py`. (b) onchain: si redeploy, añadir `mapping(address => uint256 lastClaim)` en el contrato con require 6h.
**Effort**: 1 h server-side; 2 h onchain (redeploy).

### 9. Anti-abuse de accounts
**Síntoma**: `create user1 pass`, `create user2 pass`, etc — fácil spam. Cada uno gana 700 $TERM. Rate limit actual de Evennia (que vimos en smoke test: "creating too many accounts") es por IP, pero bots rotan IP.
**Fix**: requerir email verificado, o captcha en webclient, o gate con Sign-In-With-Ethereum (SIWE).
**Effort**: 3 h (captcha); 6 h (SIWE completo).

### 10. Leaderboard onchain real
**Síntoma**: `CmdLeaderboard` lee `caller.db.run_duration` de DB local. Si alguien juega local, no entra al leaderboard global.
**Fix**: leer eventos `Transfer` del contrato desde deploy block + agrupar por `to` + cruzar con wallets linkeadas en DB.
**Effort**: 3 h.

### 11. Deploy automation con GitHub Actions
**Síntoma**: cada deploy es `tar | scp | ssh "tar xzf + evennia reload"` manual. Fácil olvidar un paso.
**Fix**: GH Action que al push a `main`:
  - rsync al VPS con ssh key
  - `evennia collectstatic --clear --noinput`
  - `evennia reload`
  - smoke test HTTP check
  - rollback si falla
**Effort**: 3 h.

### 12. Rollback strategy
**Síntoma**: si un push rompe prod, no hay "undo" rápido. El fix actual es git revert + redeploy manual.
**Fix**: mantener último tag `production-stable` + script `./rollback.sh` que hace `git checkout <tag> && rsync + reload`.
**Effort**: 1 h (combinado con CI/CD).

### 13. Tests automatizados en CI
**Síntoma**: no hay test suite. Todo se valida con smoke tests ad-hoc que escribo por mano.
**Fix**:
  - `pytest` + `pytest-django` para unit tests de Command classes + narrator helpers
  - Test integration que monta Evennia embebido y corre comandos via socket
  - CI GitHub Actions que ejecuta antes de merge
**Effort**: 6 h para suite básica.

### 14. Schema migrations de `caller.db`
**Síntoma**: si cambio el formato de `caller.db.quest_done` (ej. de list a set), players viejos se rompen.
**Fix**: función `migrate_player_state(caller)` que corre en `at_post_puppet` y normaliza campos antiguos al nuevo schema. Marcado con `caller.db.schema_version`.
**Effort**: 2 h.

---

## 🟢 Nice-to-have — hardening / escala

### 15. Move a PostgreSQL
**Por qué**: SQLite sirve para <100 users concurrentes. Si el juego crece, postgres es estándar + mejor concurrencia + replica + backups.
**Fix**: Evennia lo soporta nativo. Cambiar `DATABASES` en settings + `evennia migrate`. Requiere backup del SQLite primero.
**Effort**: 2 h + operaciones.

### 16. Load balancer + 2 instancias
**Por qué**: cpx11 es single-point-of-failure. Si el VPS cae, prod cae.
**Fix**: 2 cpx11 con load balancer Hetzner (€5/mes LB) + sticky sessions para Evennia (el state de player está en DB shared).
**Effort**: 4 h.

### 17. CDN para assets estáticos
**Por qué**: JS/CSS/imágenes del webclient se sirven desde el VPS. Un CDN los pone más cerca de usuarios globales.
**Fix**: Cloudflare R2 + proxy Cloudflare OR bunny.net. `evennia collectstatic` a S3/R2 con `django-storages`.
**Effort**: 3 h.

### 18. Analytics de gameplay
**Por qué**: no sé cuántos jugadores completan el tutorial, dónde se atoran, cuánto tiempo toma.
**Fix**: events en DB propia + dashboard metabase/grafana. Privacidad: anonimizar username si son públicos.
**Effort**: 6 h.

### 19. I18n (inglés)
**Por qué**: actualmente solo español. Audiencia global limitada.
**Fix**: usar `gettext` de Django + `django.utils.translation.gettext_lazy as _` en los strings. Traducciones en `locale/en/LC_MESSAGES/`.
**Effort**: 8 h para traducir todo + infra.

### 20. Skills dinámicos (real GitHub pull)
**Por qué**: catálogo de `AVAILABLE_SKILLS` está hardcoded. Si quiero añadir un skill, toca deploy.
**Fix**: leer `skills_catalog.yaml` desde GitHub raw (repo propio o de portdeveloper). Cache 1h. Fallback al hardcoded si falla el fetch.
**Effort**: 3 h.

### 21. NFT de certificación "Graduated Terminal Academy"
**Por qué**: mencionado en pitch como roadmap. No implementado.
**Fix**: deploy ERC-721 minimal en Monad testnet. Al `reconstruct memory` + 10/10 fragmentos + tx hash en explorer, mint NFT al player.
**Effort**: 6 h (contrato + integración).

### 22. Contrato upgradeable o Safe multisig
**Por qué**: actual no puede fixear bugs onchain; hot wallet única es riesgo.
**Fix**: redeploy con UUPS proxy pattern (OpenZeppelin) + ownership en Safe multisig. Si hubiera exploit, pausar + upgrade.
**Effort**: 4 h.

---

## 🧪 QA / Testing

### 23. Suite de smoke tests en el repo
**Síntoma**: scripts de smoke test viven en `/tmp/smoke_*.py` en mi máquina. Nadie más los puede correr.
**Fix**: mover a `tests/smoke/full_flow.py` + doc "how to run". Ejecutar en CI después del deploy.
**Effort**: 2 h.

### 24. Load testing
**Síntoma**: nunca probé con >3 sesiones concurrentes. No sé en qué punto se cae.
**Fix**: script con `asyncio` que abre 100 sockets al 4100, cada uno juega 5 min, medir latency p95.
**Effort**: 3 h.

### 25. Cross-browser testing
**Síntoma**: webclient validado solo en Firefox Linux. Safari / Chrome / mobile desconocido.
**Fix**: BrowserStack o similar. Minimum Chrome/Firefox/Safari desktop + Chrome/Safari mobile.
**Effort**: 2 h setup + tiempo de review manual.

---

## 📊 Observabilidad

### 26. Uptime monitor externo
**Fix**: UptimeRobot / Better Stack pingeando `https://blitz.mexi.wtf/webclient/` cada minuto. Alerta si down >2min.
**Effort**: 15 min.

### 27. Error aggregation (Sentry)
Ya cubierto en #7.

### 28. Metrics dashboard
**Fix**: Grafana + Prometheus. Métricas clave: connected players, claims/hr, wallet balance, tx success rate, p95 claim latency.
**Effort**: 4-6 h.

---

## 💰 Onchain risk

### 29. Multi-sig ownership
**Por qué**: si PK se filtra, adiós. Safe multisig con 2-de-3 firmantes protege.
**Fix**: deploy Safe en Monad testnet + transfer ownership del contrato $TERM al Safe.
**Effort**: 2 h.

### 30. Rate limit onchain en el contrato
**Por qué**: defensa en profundidad. Aunque el server tenga rate limit, el contrato también debería.
**Fix**: mapping `lastClaim[address]` + require `block.timestamp - lastClaim[to] > 6 hours`. Requiere redeploy.
**Effort**: 1 h código; 1 h redeploy + migración.

### 31. Pausable contract
**Por qué**: si detecto exploit, pausar transfers gana tiempo.
**Fix**: OpenZeppelin `Pausable` pattern. Admin puede `pause()` / `unpause()`. Requiere redeploy.
**Effort**: 1 h.

---

## Priorización sugerida (orden de ataque)

Si retomo con 1 día de trabajo:
1. systemd unit (#1) — 30 min
2. SQLite backup (#4) — 2 h
3. Sentry para error tracking (#7) — 1 h
4. Uptime monitor externo (#26) — 15 min
5. Let's Encrypt verificación (#6) — 10 min
6. Runbook de PK rotation (#5) — 30 min
7. Wallet balance alertas (#3) — 2 h
Total: ~7 h — cubre los bloques críticos.

Si retomo con 1 semana:
- Agregar #2 (nonce cache persistente), #8 (rate limit claims), #11 (CI/CD), #15 (postgres).

Si paso a "production" real (>100 users/día):
- #16 (LB + 2 instancias), #22 (multi-sig + upgradeable), #29 (Safe ownership).

---

## Cómo priorizar cuando regrese

Pregunta principal: **¿el proyecto va a seguir siendo un demo post-hackathon, o escala a producción real?**

- Si **demo**: critical items #1, #4, #5, #6, #26 son suficientes (~5 h).
- Si **producción**: todo el 🔴 + 🟡 (~40 h de work).
