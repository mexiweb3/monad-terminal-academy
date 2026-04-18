# Demo Script — Monad Terminal Academy (2 min)

Guión para grabar el demo en vivo. Target **1:50–2:10**. Graba con OBS a 1280×800, Chrome en kiosk mode o maximizado, zoom 110%.

## Setup previo (no graba)

```bash
# Verificar stack vivo
ps aux | grep -E "twistd|cloudflared" | grep -v grep
grep trycloudflare /tmp/cf-tunnel.log /tmp/cf-ws.log /tmp/cf-landing.log

# Tener tabs listas:
#  - tab 1: landing   (https://aka-warning-old-geneva.trycloudflare.com/)
#  - tab 2: webclient (https://die-hand-alexandria-joan.trycloudflare.com/webclient/)
#  - tab 3: explorer  (https://testnet.monadexplorer.com/ — abrir al final con la tx)
```

Tener a mano una wallet EVM de prueba (ej. `0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045` = vitalik.eth).

---

## Guion

### 0:00–0:10 — Hook (landing)

> "¿Cómo llevás a alguien de cero a deployar un contrato en Monad en 15 minutos? Terminal + Claude CLI + onchain, todo en un MUD jugable desde el navegador. Monad Terminal Academy."

**Acción**: landing abierta — scroll rápido mostrando hero ("De `ls` a `claude deploy`"), bloque Claude CLI con las 4 skills visibles, quests en 3 columnas (19 total). Clic en "▶ Jugar ahora".

### 0:10–0:20 — Shell básico

> "Creo un user nuevo. Me cae en `/home` de la Academia. El mundo es un filesystem."

**Acción**: `create demoU testpass123!` → `Y` → `connect demoU testpass123!` → `ls` → `cat README.txt` → `cd ls_dojo`.

### 0:20–0:50 — Shell intermedio + operadores

> "Paso por pipe_dojo y redirect_dojo. Aprendo composición con pipes y redirección real."

**Acción** (narrando):
- `cd ..` → `cd cd_dojo` → `cd cat_dojo` → `cd mkdir_dojo` → `cd pipe_dojo`
- `echo hola mundo | wc`  → muestra "1 2 10" (líneas/palabras/chars)
- `cd redirect_dojo`
- `echo "primera linea" > mi.log`
- `echo "segunda linea" >> mi.log`
- `cat mi.log` → muestra las 2 líneas

> "Llevo como 310 `$TERM` pendientes. Vamos a la parte buena."

### 0:50–1:20 — Claude CLI in-game

**Acción**: `cd final_exam` → `cd claude_dojo` → `claude` (muestra banner de ayuda + skills disponibles).

> "En claude_dojo tengo el CLI de IA. Instalo un skill de Austin Griffith para Monad."

- `claude skills list` → muestra las 4 skills (scaffold-eth, solidity-basics, monad-kit, claude-code-guide)
- `claude skills install austin-griffith/monad-kit` → "✓ Skill instalado."
- `claude new contract MiPrimerToken` → "✓ Escrito 54 líneas en MiPrimerToken.sol."
- `cat MiPrimerToken.sol` → muestra Solidity real: `contract MiPrimerToken { ... transfer(...) ... }`

### 1:20–1:40 — **CLÍMAX: `claude deploy`**

> "Y ahora el momento del show. Claude me deploya el contrato a Monad testnet."

**Acción**: `claude deploy MiPrimerToken.sol` — pausa dramática 2-3s — muestra el banner con `address: 0x...` + `tx: 0x...`.

> "Address y tx generados. Pero esto es el juego — lo real viene ahora con el claim."

### 1:40–2:00 — Claim onchain real

**Acción**:
- `link 0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045`
- `quests` (muestra las 19 con checks verdes)
- `claim` — pausa 4-5s mientras el server firma y broadcastea

> "Ahí está el tx hash. Vamos al explorer."

**Acción**: copiar el hash, abrir [testnet.monadexplorer.com/tx/…] en la tab 3. Mostrar `Transfer` event del ERC-20, `540 $TERM → 0xd8dA…6045`.

> "Stack: Evennia + Foundry + web3.py + Claude CLI + Monad. Todo open source, template forkeable. Tu propia X Chain Academy está a un fork de distancia."

---

## Fallbacks si algo falla

- **Claim cuelga > 15s**: cortar a `docs/pitch/screenshots/webclient-05-claim.png` (claim previo exitoso de 540 `$TERM`). El tx oficial es [`0x753b572d…827b`](https://testnet.monadexplorer.com/tx/0x753b572d4cc3265d082d5da4793bb6d8f29bcfeb355d8b49adc463dabddb827b).
- **`claude deploy` no renderiza bonito**: cortar a `webclient-10-deploy.png` y narrar.
- **Webclient no conecta WS**: los URLs del tunnel pueden estar muertos; relanzar `cloudflared tunnel --url http://localhost:4103`, copiar URL nueva, `evennia reload`.
- **Server caído**: `cd abyss-node/abyss_node && source ../../.venv/bin/activate && evennia start`. Esperar 4s.

## Cosas que NO decir en el video

- No mencionar "hackathon pivot" ni pedir disculpas por el stack.
- No mostrar el private key (`deploy/.env` chmod 600 ya es narrativa suficiente).
- Si hay tracebacks de Evennia en pantalla, hacer `evennia reload` antes de seguir.
- No prometer que `claude deploy` **deploya de verdad** — es el hook de la demo, pero el deploy real al ERC-20 `$TERM` ya pasó antes (explorer lo prueba) y el claim onchain es la prueba concreta.
