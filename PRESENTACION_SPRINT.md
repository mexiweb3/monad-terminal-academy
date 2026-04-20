# Sprint de Presentación — Club Industrial 2pm

> El user llega ~1:45 pm al Club Industrial (Monterrey). Dividimos el trabajo en 4 tracks paralelos.

## Estado a este momento (healthcheck OK)

- `https://blitz.mexi.wtf/` → 200 OK (nginx)
- `https://blitz.mexi.wtf/webclient/` → 200 OK
- Wallet hot `0xAA61…7207`: **6.707 MON** (≈67 claims)
- Evennia: 2 procesos (portal + server) vivos
- Repo en `main` commit `7b89bed` (con TODO_STABILITY)

---

## Track 1 (yo, sesión main) — Demo-pack + Cheat Sheet

Lo hago mientras tú te preparas. Entregables:
- Cheat sheet 1-página imprimible con URLs, commands demo, tx ejemplo
- Verificar que el flujo demo corre sin errores
- Backup URL accesible si alguien la quiere jugar en vivo

## Track 2 — Deck visual (Sesión externa A)

**Pega este prompt en una sesión Claude abierta en `/home/mexi/Documents/_active/monadmty/`**:

```
Crea un slide deck HTML con reveal.js (CDN, un solo archivo, sin build)
basado en PITCH.md + SUBMISSION.md + README.md del proyecto Terminal
Academy.

Guárdalo en docs/pitch/deck.html.

Estructura (10-12 slides):
1. Hero: "Terminal Academy" + subtítulo + URL blitz.mexi.wtf
2. Problema: miedo a la terminal, bootcamps costosos, retención baja
3. Solución: MUD onchain, aprendes comandos reales, ganas $TERM
4. Demo screenshot: webclient con prompt visible
5. 3 actos: Despertar · Entrenamiento · Ascensión
6. 23 quests, 700 $TERM, 10 rooms
7. Claude CLI + OpenClaw + Hermes install_dojo (Windows/Mac/Linux)
8. Onchain: contrato 0x6BCC...03d8 en Monad testnet + tx ejemplo
9. Revenue: freemium-to-burn, B2B white-label, NFT certificación
10. Tracción: construido en 1 día, deployado en prod con TLS
11. Roadmap: NFT graduation, leaderboard onchain, skills dinámicos
12. Gracias + QR code al URL

Estilo: fondo oscuro (#05110b), acentos verde matrix (#39ff14) + amber
(#ffd166), tipografía monospace (JetBrains Mono CDN). Transiciones slide
simples.

Incluye scripts para:
- s -> siguiente slide
- p -> presentation mode
- Ctrl+Shift+F -> fullscreen
- e -> export to PDF con `?print-pdf` param

Haz syntax check con curl a tool validator si quieres pero priorizas
velocidad. NO hagas commits. Yo integro al final.
```

## Track 3 — Video demo de backup (Sesión externa B)

**Pega este prompt**:

```
Graba un video-demo de 90 segundos del flujo completo de Terminal Academy
en https://blitz.mexi.wtf/webclient/ como backup por si el WiFi del
evento falla.

Opción 1 (playwright):
- pip install playwright && playwright install chromium
- Script en docs/pitch/record_demo.py que:
  1. Abre el webclient en headless=False (para grabar pantalla)
  2. Espera el prompt de login
  3. Envía "create demovisitor demopass1234" + "y" para confirmar
  4. Espera el prólogo Acto I (scroll para verlo)
  5. Ejecuta: ls, pwd, cat README.txt, cd ls_dojo, cd cd_dojo, cd cat_dojo,
     cat secret.txt, cd mkdir_dojo, touch nota.txt, mkdir miproy,
     grep ABYSS README.txt, cd pipe_dojo, echo hola, cd redirect_dojo,
     cd final_exam, cd install_dojo, node --version,
     npm install -g @anthropic-ai/claude-code,
     cd claude_dojo, claude skills install portdeveloper/monad-development,
     claude new contract MiToken, claude deploy MiToken.sol,
     link vitalik.eth, claim
  6. Entre comandos pausa 1-2 s para que la narrativa se lea
- Usa ffmpeg para grabar la ventana: screencast con OBS o:
  pip install pyvirtualdisplay + record con Xvfb

Opción 2 (manual más rápido): dile al user que grabe con OBS mientras
juega manualmente 2 min — pero recomiendo opción 1 para no quitarle tiempo.

Salida: docs/pitch/demo.mp4 (o .webm) de 60-120 seg.

Si playwright está instalado, úsalo. Si no, instala primero. Reporta
duración, tamaño, path del archivo al terminar.
```

## Track 4 — Q&A prep + talking points (Sesión externa C)

**Pega este prompt**:

```
Lee README.md, PITCH.md, SUBMISSION.md del proyecto Terminal Academy.

Produce dos archivos en docs/pitch/:

1. docs/pitch/qa_anticipado.md — 12 preguntas probables del público del
   Club Industrial (audiencia mezcla: emprendedores, inversores locales,
   tech de Monterrey) con respuesta de 30 segundos cada una. Temas
   probables: modelo de negocio, competencia (Codecademy, Replit,
   boot.dev), cómo se diferencia, por qué Monad específicamente,
   fraude/abuse (someone farm tokens), tracción actual, escalabilidad
   técnica, costos operacionales, plan legal en México (regulación
   cripto), por qué español y no inglés, go-to-market, qué pasa si
   Monad cambia de chainId.

2. docs/pitch/cheat_sheet.md — UNA PÁGINA imprimible con:
   - URLs críticos (demo, repo, contrato, tx ejemplo)
   - Credenciales del admin (si los jueces quieren jugar en vivo)
   - 5 one-liners memorables del pitch ("aprender terminal no debería
     doler", "cada comando que domines vale $TERM", etc)
   - 3 números clave (23 quests, 700 $TERM, 0.4s para 3 claims
     concurrentes)
   - Transiciones entre slides ("ahora pasemos a demo...")
   - Plan B si cae el internet: "abramos localhost:4100 con telnet"
     o mostrar video-demo

No hagas commits. Genera los archivos listos para que yo los integre.
```

---

## Cheat Sheet rápido (te lo doy aquí mismo)

### URLs para memorizar
- Demo: **`blitz.mexi.wtf`**
- Repo: **`github.com/mexiweb3/monad-terminal-academy`**
- Contrato: `0x6BCC...03d8` (Monad testnet)

### Login durante demo
- `connect admin monadtestnet123` (tu cuenta personal preferida)
- O demostración con cuenta nueva: `create <nombre> <pass>`

### Secuencia de demo (90 seg ideal)
```
ls                    → muestra el filesystem, quest +10
cd ls_dojo            → narrativa "Dojo del ver"
pwd                   → muestra path
cat README.txt        → lee archivo, destaca quest +30
cd cat_dojo
cat secret.txt        → fragmento de memoria aparece ★
cd mkdir_dojo
grep ABYSS README.txt → pattern match, +50
cd install_dojo
node --version        → simula check
npm install -g @anthropic-ai/claude-code  → install simulado
cd claude_dojo
claude skills install portdeveloper/monad-development  → skill oficial Monad
claude new contract MiToken  → genera Solidity
claude deploy MiToken.sol    → deploy simulado
link vitalik.eth      → ENS resolver funciona!
claim                 → TX REAL EN MONAD TESTNET
```

### One-liners memorables
- "Aprender terminal no debería doler."
- "Cada comando dominado vale $TERM."
- "De `ls` a deployar un ERC-20 en 15 minutos."
- "La narrativa enseña más que el tutorial."
- "Windows, Mac, Linux — empieza aquí, termina en tu máquina."

### Plan B si cae el internet
1. Abrir `docs/pitch/demo.mp4` localmente (cuando Sesión B lo grabe)
2. Leer screenshots en `docs/pitch/screenshots/`
3. Mostrar código en pantalla: abre `terminal_commands.py` y pasa por `QUESTS`, `AVAILABLE_SKILLS`

### Números clave
- **23 quests** organizadas en 3 actos (Despertar / Entrenamiento / Ascensión)
- **700 $TERM** total por completar todo
- **6.7 MON** en hot wallet hoy (~67 claims disponibles)
- **0.4 s** para 3 claims onchain concurrentes (nonce lock validado)
- **10 fragmentos de memoria** recolectables automáticamente
- **5 helpers narrativos** (narrate/dialogue/scene/achievement/error_sys)
- **1 día** para construir el MVP del hackathon

---

## Orden de ejecución

1. **Tú**: báñate + vístete (mientras todo corre en paralelo)
2. **Tú → ahora mismo**: pasa los 3 prompts a las 3 sesiones externas
3. **Yo (esta sesión)**: cuando me confirmes los 3 cambios de pitch que quieres, los aplico y te genero el deck/cheat sheet final
4. **Integración en 1 hr**: me mandas los 3 outputs de las sesiones, hago merge, verifico, te lo entrego como PDF + link

Arranca ya.
