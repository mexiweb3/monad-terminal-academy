#!/bin/bash
# ============================================================================
# Terminal Academy — SQLite daily backup
# ============================================================================
#
# Qué hace:
#   Toma snapshot consistente de evennia.db3 usando `sqlite3 .backup`
#   (NO `cp` — cp puede copiar un DB a medio commit si Evennia está escribiendo
#   en ese microsegundo; `.backup` usa la API online de SQLite y garantiza
#   un estado consistente incluso con el server corriendo).
#
#   Rota archivos > 14 días. Loguea cada run a backups/backup.log.
#
# Uso manual (prueba antes de poner en cron):
#   ./backup_db.sh
#
# Uso automatizado (cron diario 3am):
#   ver deploy/scripts/crontab.txt
#
# Exit codes:
#   0  - backup OK
#   1  - DB source no existe
#   2  - sqlite3 no instalado
#   3  - fallo durante .backup
#   4  - fallo al rotar (no fatal pero loguea)
#
# ============================================================================

set -euo pipefail

# --- Config ---
DB_SOURCE="/root/monadmty/abyss-node/abyss_node/server/evennia.db3"
BACKUP_DIR="/root/monadmty/backups"
LOG_FILE="${BACKUP_DIR}/backup.log"
RETENTION_DAYS=14

# --- Helpers ---
log() {
    local msg="$1"
    local ts
    ts="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    echo "[${ts}] ${msg}" | tee -a "${LOG_FILE}" >&2
}

# --- Preflight ---
mkdir -p "${BACKUP_DIR}"

if [[ ! -f "${DB_SOURCE}" ]]; then
    log "FATAL: DB source not found at ${DB_SOURCE}"
    exit 1
fi

if ! command -v sqlite3 >/dev/null 2>&1; then
    log "FATAL: sqlite3 not installed (apt-get install -y sqlite3)"
    exit 2
fi

# --- Backup ---
TIMESTAMP="$(date -u +%Y%m%d_%H%M%S)"
DEST="${BACKUP_DIR}/evennia.db3.${TIMESTAMP}"

log "START backup -> ${DEST}"

# `.backup` command: atomic, online-safe (copy-on-write interno de SQLite)
if ! sqlite3 "${DB_SOURCE}" ".backup '${DEST}'"; then
    log "FATAL: sqlite3 .backup failed"
    # Si quedó un archivo parcial, borrarlo
    [[ -f "${DEST}" ]] && rm -f "${DEST}"
    exit 3
fi

# Verificar que el backup es un DB SQLite válido
if ! sqlite3 "${DEST}" "PRAGMA integrity_check;" | grep -q "^ok$"; then
    log "FATAL: backup integrity check failed for ${DEST}"
    rm -f "${DEST}"
    exit 3
fi

SIZE_BYTES="$(stat -c%s "${DEST}")"
log "OK   backup written (${SIZE_BYTES} bytes)"

# --- Rotación ---
# Borra backups con mtime > RETENTION_DAYS días. `|| true` para que un fallo
# de rotación no tumbe el exit code del script (el backup ya se hizo).
DELETED_COUNT="$(find "${BACKUP_DIR}" -maxdepth 1 -type f -name 'evennia.db3.*' \
    -mtime "+${RETENTION_DAYS}" -print -delete 2>/dev/null | wc -l || true)"

if [[ "${DELETED_COUNT}" -gt 0 ]]; then
    log "ROT  pruned ${DELETED_COUNT} old backup(s) (>${RETENTION_DAYS}d)"
fi

log "DONE"
exit 0
