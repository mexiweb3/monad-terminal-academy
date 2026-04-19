# Terminal Academy — Plan narrativo v2

> Objetivo: transformar el tutorial actual en un **cuento jugable** con diferenciación clara entre mundo-de-juego y terminal-real. 4 sesiones paralelas.

## Lore común (leer primero)

**Despertaste sin memoria en un filesystem roto.** Un ente llamado **El Corruptor** está borrando archivos del sistema primordial. Tu mentor, **El Profesor Shell**, te enseña los comandos ancestrales de Unix para reparar la realidad. Cada comando desbloquea un **fragmento de memoria perdida**. Al completar el ritual final (`claim`), tu identidad queda grabada onchain en Monad — prueba inmutable de que existías.

3 actos:
- **Acto I: Despertar** — home → ls_dojo → cd_dojo → cat_dojo (aprendes que el mundo es texto)
- **Acto II: Entrenamiento** — mkdir → pipe → redirect → final_exam (armas para combatir al Corruptor)
- **Acto III: Ascensión** — install_dojo → claude_dojo → link + claim (trasciendes al onchain)

## Diferenciación mundo ↔ terminal (grammar visual)

| Modo | Color | Prefijo | Ejemplo |
|---|---|---|---|
| **Narrador** (lore, escenas) | `|m` magenta + glow | `🎙  ` o bloque `━━` | `🎙  Abres los ojos. El aire sabe a metal.` |
| **NPC dialogue** | `|c` cyan, nombre en bold | `» <Nombre>:` | `» Prof. Shell: Respira. Estás vivo.` |
| **Quest/Achievement** | `|y` amber, box warm | `★` + box drawing | `★ FRAGMENTO RECUPERADO ★` |
| **Terminal raw** (output de `ls`, `cat`, etc) | `|g` verde / blanco / gris | sin decoración | `home/ ls_dojo/ README.txt` |
| **Error del sistema** | `|r` rojo | `⚠ !` | `⚠ cat: tu.txt: No such file` |
| **Prompt** | verde + cyan, pequeño | ninguno | `neo@academy:/home$` |

**Regla mental para el jugador**: si tiene emoji/bordes/color warm → es **el mundo hablándote**. Si es monoespaciado raw → es **el filesystem respondiendo**.

---

## Sesión A — Narrativa + Lore

**Objetivo**: reescribir todas las descripciones, crear NPCs vivos y un prólogo cinemático.

**Archivos owned** (sólo tú editas):
- `abyss-node/abyss_node/world/zones/terminal_academy.py` — descripciones de rooms
- `abyss-node/abyss_node/world/npcs/academy_npcs.py` — NPCs (Prof. Shell, El Corruptor, otros)
- `abyss-node/abyss_node/world/lore/` (nueva carpeta) — fragmentos de memoria, diálogos
- `abyss-node/abyss_node/typeclasses/characters.py` — hook `at_post_login` con prólogo

**Tareas**:
1. **Prólogo cinemático** (30 s en el primer login):
   ```
   🎙  ...estática...
   🎙  Abres los ojos. No recuerdas cómo llegaste aquí.
   🎙  Estás flotando en un mar de texto verde.
   🎙  Una voz familiar te habla...

   » Prof. Shell: Respira, Neófito. Te encontré justo a tiempo.
   » Prof. Shell: El Corruptor ha borrado tu memoria, pero no tu sintaxis.
   » Prof. Shell: Empieza por lo básico. Teclea `ls` para ver dónde estás.
   ```
   Aplica 1 vez (guarda `caller.db.seen_prologue = True`).
2. **Reescribir desc de 10 rooms** con tono narrativo en lugar de tutorial:
   - Antes: "ls_dojo — aquí practicas el comando ls."
   - Después: "El Dojo del `ls` — aquí aprenderás a *ver*. El Corruptor no puede borrar lo que puedes nombrar."
3. **Crear 3 NPCs**:
   - **Prof. Shell** (`/home`) — mentor guía, da hints según `caller.db.quest_done`
   - **El Eco del Corruptor** (`/final_exam`) — voz misteriosa, deja pistas
   - **La Forjadora** (`/claude_dojo`) — spirit-guide de la IA, te enseña a invocar a Claude
4. **Diálogos reactivos**: NPC usa `caller.db.quest_done` para no repetirse. `say hola prof` → respuesta distinta según progreso.
5. **10 fragmentos de memoria** escondidos en archivos (`cat secret.txt` descubre uno). Al juntar los 10, unlock final cinemático.
6. **Outro al completar todas las quests** — cinemática de "recuperaste tu identidad, deployarla onchain".

**Criterios de aceptación**:
- Usuario nuevo ve el prólogo al conectarse primera vez.
- Cada room tiene desc con TONO narrativo (no instructivo).
- Prof. Shell responde a `say hola` con al menos 5 variaciones según progreso.
- Al terminar final_exam se dispara la escena de Acto III.

**Fuera de scope**: código de comandos terminal, UI/colors helpers, puzzles.

---

## Sesión B — Grammar visual: separar mundo de terminal

**Objetivo**: construir los helpers + el CSS que hacen que la diferenciación sea obvia a 1 vistazo.

**Archivos owned**:
- `abyss-node/abyss_node/utils/narrator.py` (NUEVO) — helpers `narrate()`, `dialogue()`, `scene()`, `achievement()`, `error_sys()`, `terminal()`
- `abyss-node/abyss_node/web/static/webclient/css/narrator.css` (NUEVO)
- `abyss-node/abyss_node/web/static/webclient/js/plugins/narrator.js` (NUEVO) — typewriter effect para narrativa
- `abyss-node/abyss_node/web/templates/webclient/base.html` (OVERRIDE si no existe) — cargar los nuevos assets

**Tareas**:
1. **`narrate(caller, text)`** — emite texto con magenta glow + prefix `🎙  ` + width 60 cols.
2. **`dialogue(caller, npc_name, text)`** — emite `» <Nombre>: <text>` con cyan, nombre en bold.
3. **`scene(caller, title, body)`** — bloque cinemático con separadores `━━━ CAPÍTULO X: TITULO ━━━`.
4. **`achievement(caller, title, body, reward)`** — box warm con ★, reward highlight.
5. **`error_sys(caller, msg)`** — estilo shell error en rojo.
6. **Typewriter JS plugin** — para `scene()`, revela el texto letra por letra (40 ms/char, skip con Enter).
7. **CSS dedicado**:
   - `.narrator` — gradient background sutil, border magenta, text-shadow glow
   - `.dialogue` — left border cyan, padding izquierda
   - `.achievement` — gold gradient, border amber
   - `.cmd-echo` (ya existe) — lo dejamos como está
   - Output raw de comandos → `white-space:pre`, no especial
8. **Tag ANSI extendido** — añadir markers custom tipo `|nar|...|nn|` que el cliente renderiza como narrator block. (Optional si sirve.)
9. **Docstring de cada helper** con ejemplo visual de cómo queda.

**Criterios de aceptación**:
- `from utils.narrator import narrate, dialogue, scene, achievement` funciona.
- `narrate(caller, "Abres los ojos...")` se ve visiblemente distinto a `caller.msg("ls output here")`.
- Typewriter funciona en el webclient; desactivable con setting `NARRATIVE_TYPEWRITER = False` en settings.py.
- Tabla comparativa en el docstring del módulo muestra los 5 modos.

**Fuera de scope**: reescribir contenido narrativo (es Sesión A), crear NPCs, puzzles.

---

## Sesión C — Onboarding + tutorial guiado contextual

**Objetivo**: hacer que los primeros 3 minutos sean MÁGICOS para un user que nunca tocó terminal.

**Archivos owned**:
- `abyss-node/abyss_node/commands/onboarding_command.py` (NUEVO) — `tutorial`, `tutorial wallet`, `tutorial monad`
- `abyss-node/abyss_node/commands/help_command.py` — reformular help como "pide ayuda al Prof"
- `abyss-node/abyss_node/typeclasses/characters.py` (coordinar con A) — hook idle watcher
- `abyss-node/abyss_node/commands/default_cmdsets.py` (solo para registrar nuevos)

**Tareas**:
1. **Creación de character con sabor**: durante `create <user> <pass>`, al crear character, preguntar "Antes de empezar, ¿cómo te llaman los sistemas?" (si es diferente a username). Guardar `caller.db.narrative_name`.
2. **Tutorial forzado del primer comando**: si `caller.db.seen_ls is not True`, el Prof. Shell te repite el hint cada 15 s hasta que hagas `ls`.
3. **Idle watcher**: ticker cada 30 s; si el user no ejecuta comando y está en una room-quest pending, el NPC le da pista sutil.
4. **`tutorial wallet`** — comando que abre flujo guiado: "¿Qué es una wallet? → ¿Por qué Monad testnet? → Cómo agregar la red a MetaMask (con copy-paste RPC) → Cómo copiar tu address → Volvemos al juego con `link 0x...`".
5. **`tutorial monad`** — explica en 30 s por qué Monad (high-TPS, EVM-compat), cómo funciona el faucet, cómo verificar una tx.
6. **`help` reformulado** — en vez de lista cruda, actúa como "Prof. Shell responde":
   - Sin args: da la próxima pista contextual según `quest_done`.
   - Con comando: explica ese comando con ejemplo + "¿por qué es útil?".
7. **Achievements con narrativa**:
   - 1 quest: "Primer respiro" — "El filesystem responde a tu llamada."
   - 5 quests: "Memoria despertando" — "Recuerdas fragmentos."
   - 10 quests: "Hacker novato" — "Puedes moverte en cualquier terminal Unix."
   - Todas: "Neo del shell" — "Estás listo para el siguiente plano."
8. **Welcome screen** al hacer login (después del prólogo): status dashboard tipo `motd`:
   ```
   ┌─ Bitácora de <narrative_name> ────────────┐
   │ Acto actual: I — Despertar                │
   │ Quests: 3/23 · $TERM: 40                  │
   │ Próximo reto: ejecuta `cat README.txt`    │
   │ Wallet: (sin linkear) · Monad testnet     │
   └───────────────────────────────────────────┘
   ```

**Criterios de aceptación**:
- Usuario nuevo no queda "atorado" en los primeros 60 s — si no hace nada, recibe un hint.
- `tutorial wallet` lleva a linkear exitosamente.
- `help cat` explica `cat` con ejemplo REAL + guía narrativa.
- Achievements se disparan en los hitos correctos y muestran texto warm.

**Fuera de scope**: narrative copy de rooms (A), CSS/helpers (B), gameplay puzzles (D).

---

## Sesión D — Gameplay: puzzles, combate, collectibles

**Objetivo**: añadir profundidad de juego más allá de "teclea X, recibe $TERM".

**Archivos owned**:
- `abyss-node/abyss_node/commands/game_commands.py` (NUEVO) — `use`, `solve`, `fight`, `scan`, `reconstruct`
- `abyss-node/abyss_node/world/zones/terminal_academy.py` (solo para spawns de items/puzzle files, coordinar con A)
- `abyss-node/abyss_node/world/items/academy_items.py` (NUEVO)
- `abyss-node/abyss_node/world/quests/puzzles.py` (NUEVO) — engine de puzzles

**Tareas**:
1. **Puzzle `grep` (en ls_dojo o nueva room)**: hay un archivo `crypto_log.txt` con 200 líneas de ruido + 1 línea oculta tipo `TOKEN: blah-blah-XYZ`. Usuario debe correr `grep TOKEN crypto_log.txt` para extraerla. Al hacerlo, unlock siguiente room.
2. **Puzzle `pipe`**: archivo `mensaje.enc` con palabras mezcladas. Solución: `cat mensaje.enc | grep clave | wc -l` te da un número que desbloquea una puerta.
3. **Mini-jefe "El Eco del Corruptor"** (`/final_exam`):
   - Inicia: `fight corruptor` abre batalla por turnos.
   - Cada turno el corruptor "corrompe" un archivo random del room; tú tienes que `restore <archivo>` o `reconstruct <archivo>` antes de N turnos.
   - Gana quien agota al otro.
4. **Collectibles**: 10 fragmentos de memoria escondidos en `cat <archivo>` de rooms específicas. `inventory` los muestra. `reconstruct memory` al tener los 10 = cinemática de Acto III.
5. **Speedrun timer**: desde primer `ls` hasta `claim`, trackear tiempo. `leaderboard` muestra top 10 jugadores (con respeto al stats.py).
6. **Dificultad progresiva**: las rooms avanzadas tienen "bugs" que hay que fixear con comandos aprendidos (ej. `mkdir_dojo` tiene un archivo con permisos rotos que hay que "reparar" con `chmod` simulado).
7. **Easter eggs**: `sudo` sin args responde con un chiste; `rm -rf /` dispara achievement "Reflejos" si el user escribe `cancel` en <3 s.

**Criterios de aceptación**:
- Al menos 3 puzzles funcionales con solución verificable.
- `fight corruptor` termina con win/loss determinado por acciones del player.
- `inventory` muestra collectibles con narrative descriptions.
- `leaderboard` muestra top 3 speedruns.

**Fuera de scope**: todo lo que NO sea mecánica de juego (no narrativa, no CSS, no onboarding).

---

## Reglas de no-colisión

- **Zonas compartidas** (coordinar con main/master):
  - `terminal_commands.py` — nadie lo toca sin coordinar (core de quest/reward)
  - `deploy/.env`, `contracts/` — intocable
  - `server/conf/settings.py` — solo B (si añade `NARRATIVE_TYPEWRITER`)
- Al final de cada tarea: smoke test que 23 quests + claim onchain siguen funcionando.
- Cada sesión hace `evennia reload` solo al terminar su batch. NO durante edits de otras.
- Master integra al final — hace 1 commit por sesión con prefix:
  - `narr:` Sesión A
  - `ui:` Sesión B
  - `onboarding:` Sesión C
  - `gameplay:` Sesión D

## Quickstart de cada sesión

```bash
cd /home/mexi/Documents/_active/monadmty
# En cada terminal separada:
claude
```

Pegar el prompt correspondiente:
- **Sesión A**: `Lee PLAN_NARRATIVE.md y memoria del workspace. Ejecuta Sesión A (Narrativa + Lore) completa hasta cumplir los criterios de aceptación. Respeta las reglas de no-colisión.`
- **Sesión B**: `Lee PLAN_NARRATIVE.md y memoria del workspace. Ejecuta Sesión B (Grammar visual) completa. Respeta las reglas de no-colisión.`
- **Sesión C**: `Lee PLAN_NARRATIVE.md y memoria del workspace. Ejecuta Sesión C (Onboarding + tutorial guiado) completa. Respeta las reglas de no-colisión.`
- **Sesión D**: `Lee PLAN_NARRATIVE.md y memoria del workspace. Ejecuta Sesión D (Gameplay puzzles y combate) completa. Respeta las reglas de no-colisión.`

## Orden recomendado si hay dependencia

B produce helpers (`narrate`, `dialogue`, etc) que A y C USAN. Si arrancas las 4 al mismo tiempo:
- A y C pueden empezar con `caller.msg()` directo y migrar a `narrate()` al final.
- O: lanza B primero (30 min), luego A/C/D en paralelo (60-90 min).

## Entregable final (master)

Al cerrar las 4 sesiones:
1. Smoke test full: prólogo → 23 quests → puzzles → boss → claim onchain.
2. Update README con "Narrativa v2" y screenshots nuevos.
3. Memoria actualizada con nuevo tono.
4. Tag release `v2-narrative`.
