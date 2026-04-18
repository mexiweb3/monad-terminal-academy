# Monad Terminal Academy — PRD

> Hackathon Monad. MUD educativo que enseña terminal a principiantes y paga `$TERM` ERC-20 en Monad testnet al completar quests. Base: `abyss-node` (Evennia).

## 1. Estado actual (2026-04-18)

Cerrado end-to-end ✅:

- **Servidor Evennia** corriendo local (puertos 4100/4101/4103).
- **Contrato `$TERM`** deployado: `0x6BCC8bA023faD77Fd9c16735fD0DCb030F1b03d8` (Monad testnet, chainId 10143).
- **Público** vía Cloudflare Quick Tunnel: `https://die-hand-alexandria-joan.trycloudflare.com/webclient/`
- **19 comandos**:
  - shell básico: `ls`, `pwd`, `cd`, `cat`, `touch`, `mkdir`, `grep`
  - shell intermedio (Sesión A): `echo` (con `|`, `>`, `>>`), `head`, `tail`, `wc`, `whoami`, `man`, `clear`, `history`
  - IA (Sesión A): `claude` + subcomandos `skills list|install|installed`, `new contract|token`, `deploy`
  - onchain: `link`, `quests`, `claim`
- **9 rooms** encadenadas: home → ls_dojo → cd_dojo → cat_dojo → mkdir_dojo → pipe_dojo → redirect_dojo → final_exam → claude_dojo.
- **19 quests** (540 `$TERM` total por completar todas).
- **Claim onchain probado** (txs `0x76544f...089567e`, `0x753b572d...`).

Contexto completo: memoria en `~/.claude/projects/-home-mexi-Documents--active-monadmty/memory/` (project, runbook, reference). Léelas antes de arrancar.

## 2. Quickstart común a cualquier sesión

```bash
cd /home/mexi/Documents/_active/monadmty/abyss-node/abyss_node
source /home/mexi/Documents/_active/monadmty/.venv/bin/activate
# Verificar server vivo:
ps aux | grep -E "twistd|cloudflared" | grep -v grep
# Si no hay twistd: evennia start
# Aplicar cambios Python: evennia reload
```

Admin: `admin` / `monadtestnet123`. Probar con `python _smoke.py` (o ver runbook).

## 3. Reglas de no-colisión entre sesiones paralelas

- **NO tocar sin coordinar**: `deploy/.env`, `contracts/`, `server/conf/settings.py`, archivos de memoria, `PRD.md` (este archivo).
- Cada sesión se queda en **sus archivos owned** (ver abajo). Puede LEER cualquier cosa.
- Cambios que requieren `evennia reload`: coordinar para no pisar. Mejor que cada sesión haga reload al terminar su chunk.
- Al acabar cada tarea: smoke test end-to-end que el claim sigue funcionando (`quests → link → claim` debe emitir tx hash real).

---

## Sesión A — Expandir gameplay: shell intermedio + Claude CLI ✅ CERRADA

**Valor**: contenido educativo ampliado: además de shell real, la Academia ahora enseña a usar **Claude CLI** para instalar skills (ej. los de Austin Griffith / Scaffold-ETH) y generar/deployar contratos en Monad. Pitch: "no solo aprendes la terminal — aprendes a usar IA en la terminal para crear tus propios tokens".

**Archivos owned (editados):**
- `abyss-node/abyss_node/commands/terminal_commands.py` (nuevas clases `CmdX`)
- `abyss-node/abyss_node/commands/default_cmdsets.py` (registro)
- `abyss-node/abyss_node/world/zones/terminal_academy.py` (nuevas rooms / archivos virtuales)
- `abyss-node/abyss_node/_smoke_session_a.py` (smoke test vía API interno de Evennia)

**Archivos solo lectura:** resto del repo.

**Tareas (hechas):**

- [x] Comandos shell intermedios: `echo <texto>` (con `|`, `>`, `>>`), `head [-n N] <file>`, `tail [-n N] <file>`, `wc [-l|-w|-c] <file>`, `whoami`, `man <cmd>`, `clear`, `history [N]`. Comportamiento fiel al shell real, sin inventar syntax.
- [x] Pipes y redirects dentro de `CmdEcho` — simulados, soporta `echo TXT | wc|grep|head|tail` y `echo TXT > file`, `echo TXT >> file`.
- [x] Comando `claude` (meta-tool de IA) con subcomandos: `skills list|installed|install <owner/slug>`, `new contract <Nombre>`, `new token <SYMBOL>`, `deploy <file.sol>`. Catálogo de skills incluye 3 de Austin Griffith (scaffold-eth, solidity-basics, monad-kit) y el de Anthropic (claude-code-guide). `deploy` requiere tener `monad-kit` instalado y genera address/tx pseudo-determinísticos (simulado — no onchain).
- [x] Quests en `QUESTS`: 14 nuevas además de las 8 previas → **19 totales** (total 540 `$TERM`). Shell 10–30 c/u, Claude 30–60 c/u, link 50.
- [x] 4 rooms nuevas encadenadas después de `mkdir_dojo`: `pipe_dojo` (pipes), `redirect_dojo` (>, >>), `final_exam` (combina 3+ comandos), `claude_dojo` (graduación: flujo IA).
- [x] Registrado todo en `default_cmdsets.py` sin pisar el `CmdHelpCustom` de Sesión B.
- [x] `python _build_world.py` + `evennia reload` aplicados.
- [x] Smoke test end-to-end vía API interno (`_smoke_session_a.py`) — crea account+char, corre los 40+ comandos secuenciales, verifica `19/19 quests` y `claim` onchain con tx real.

**Criterios de aceptación (pasados):**
- ✅ Jugador nuevo completa las 19 quests (8 originales + 7 shell intermedio + 4 Claude CLI) de home → claude_dojo.
- ✅ Cada comando nuevo completa su quest en el primer uso con args correctos.
- ✅ `claim` envía tx real en Monad testnet sin regresiones (última tx probada: `0x753b572d4cc3265d082d5da4793bb6d8f29bcfeb355d8b49adc463dabddb827b`).

**Flujo pedagógico final (lo que aprende el jugador):**
```
ls, pwd, cd → cat → touch, mkdir, grep
  → echo/head/tail/wc/whoami/man/history + pipes (|) + redirects (>, >>)
    → claude skills install austin-griffith/monad-kit
      → claude new contract MiPrimerToken
        → claude deploy MiPrimerToken.sol
          → link <wallet> + claim (tx real en Monad testnet)
```

**Fuera de scope:** tocar contrato, UX/visual, NPCs, landing (siguen siendo de Sesión B y C).

---

## Sesión B — Onboarding y UX

**Valor**: diferenciador en el pitch — "onboarding tan bueno que un no-técnico de 60 años puede completar el tutorial". NPCs le dan vida al mundo.

**Archivos owned (editables):**
- `abyss-node/abyss_node/typeclasses/characters.py` (hooks `at_post_login` / `at_first_login`)
- `abyss-node/abyss_node/world/npcs/academy_npcs.py` (crear — NPC instructor)
- `abyss-node/abyss_node/commands/help_command.py` (crear — `help` custom con colores)
- `abyss-node/abyss_node/commands/default_cmdsets.py` (solo para registrar `CmdHelpCustom`; coordinar brevemente con Sesión A si edita el mismo archivo — ambas solo añaden `self.add(...)`)

**Archivos solo lectura:** resto del repo.

**Tareas:**

- [ ] Hook `at_post_login` del Character: al primer login, mostrar banner ASCII art de "MONAD TERMINAL ACADEMY" + tutorial message guiando a `ls`. Idempotente (no repetir en re-logins).
- [ ] Crear NPC "Prof. Shell" en `/home`. Typeclass en `academy_npcs.py`. Reacciona a `say hola prof` con un diálogo scripted que sugiere el próximo paso según el progreso de quests del player (`caller.db.quest_done`).
- [ ] Crear `CmdHelpCustom` que reemplaza el help default con: lista de comandos terminal (categoría "Terminal"), comandos Monad (categoría "Monad"), y un "¿Cuál intento?" recomendando la próxima quest pendiente.
- [ ] Mensajes de achievement al cruzar hitos: 3 quests completadas ("Te estás volviendo shell-ninja"), 5 ("Ya puedes presumir en Discord"), todas ("Linkea wallet y `claim`"). Guardar en `caller.db.achievements_shown`.
- [ ] Script `_spawn_npcs.py` que spawnea/reusa el NPC en /home (idempotente).

**Criterios de aceptación:**
- Usuario nuevo registrándose desde webclient ve banner + mensaje orientador automáticamente.
- `help` en cualquier momento da una recomendación contextual de próxima quest.
- Prof. Shell responde al menos a 3 interacciones distintas.

**Fuera de scope:** nuevos comandos terminal, nuevas rooms, contrato, landing page.

---

## Sesión C — Landing page + README + pitch assets

**Valor**: primera impresión para jueces. Página con CTA "Jugar ahora" que abra el webclient; README github-ready; video/gif del flujo completo.

**Archivos owned (editables):**
- `/home/mexi/Documents/_active/monadmty/landing/` (nuevo — HTML/CSS/JS estático)
- `/home/mexi/Documents/_active/monadmty/README.md` (nuevo — top-level)
- `/home/mexi/Documents/_active/monadmty/docs/pitch/` (nuevo — screenshots, gif, pitch-deck.md)

**Archivos solo lectura:** resto del repo (pero sí puede leer código para documentar).

**Tareas:**

- [ ] `landing/index.html`: single-page estática con dark mode tipo terminal. Secciones: hero (título + CTA "jugar"), "¿Cómo funciona?" (3 pasos: conectar → aprender → claim), "Quests" (lista visual), "Tech stack" (Evennia + Monad + ERC-20), footer con tx del deploy + link al explorer. Sin framework — HTML/CSS vanilla para no añadir build step.
- [ ] Publicar landing via Cloudflare Quick Tunnel TERCERO apuntando a un `python -m http.server 8080` servido desde `landing/`. Capturar URL y documentar en README.
- [ ] `README.md` top-level: badges (Monad, Evennia, License), descripción de 1 párrafo, imagen hero, "Play now" CTA, sección "How it works", sección "Stack técnico", sección "Run locally" (5 comandos del quickstart), link al PRD y memoria, créditos.
- [ ] `docs/pitch/screenshots/`: capturas del webclient en diferentes puntos (home, post-ls, post-claim con tx hash). Usar herramientas headless si hace falta — Playwright con el venv (`pip install playwright && playwright install chromium`).
- [ ] `docs/pitch/pitch.md`: 1-slide deck en markdown (problema → solución → demo → stack → visión — 5 bullets por sección máximo).
- [ ] `docs/pitch/demo-script.md`: guión de 2 min para grabar el demo live (acciones exactas, timestamps).

**Criterios de aceptación:**
- Landing URL público accesible desde cualquier dispositivo, mobile-responsive.
- README legible en GitHub sin errores (preview local con `grip` o similar).
- Screenshots muestran el flujo completo sin placeholders.

**Fuera de scope:** código de juego, contrato, onchain.

---

## Entregable final (coordinador)

Cuando las 3 sesiones terminen, main session:
1. Pull-in de cambios de cada sesión, reload Evennia, smoke test.
2. Verifica que contratos/URLs/memoria siguen vivas.
3. Actualiza memoria (`project_hackathon_monad.md`) con los nuevos comandos/rooms/URLs.
4. Prepara el submission del hackathon: URL pública + tx onchain + link al landing + README.
