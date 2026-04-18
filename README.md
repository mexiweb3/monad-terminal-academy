# Monad Terminal Academy

> De `ls` a `claude deploy` en 15 minutos. Aprende shell + Claude CLI + deploy onchain — todo dentro de un MUD.

![Monad](https://img.shields.io/badge/Monad-testnet-6f4dff?style=flat-square)
![Evennia](https://img.shields.io/badge/Evennia-6.0-39ff14?style=flat-square)
![Powered by Claude](https://img.shields.io/badge/Powered%20by-Claude-ff9a3c?style=flat-square)
![Python](https://img.shields.io/badge/python-3.13-3776ab?style=flat-square)
![Solidity](https://img.shields.io/badge/solidity-0.8-363636?style=flat-square)
![License](https://img.shields.io/badge/license-MIT-lightgrey?style=flat-square)

MUD educativo onchain construido para **Monad Blitz MTY 2026**. Los jugadores pasan de **no saber qué es `ls`** a **deployar su primer ERC-20 en Monad testnet** en una sola sesión — aprendiendo shell, operadores (`|`, `>`, `>>`) y el uso de **Claude CLI con skills de Austin Griffith** para generar y deployar código. Al completar las 19 quests cobran **540 `$TERM`** onchain.

El diferenciador no es "academia de terminal". Es **academia de terminal + Claude CLI + deploy onchain, todo desde un MUD** con comportamiento de shell real (prompt dinámico, `↑↓` history, `Tab` autocomplete, `cd -`).

![hero](docs/pitch/screenshots/webclient-05-claim.png)

## ▶ Jugar ahora

| | |
|---|---|
| **Landing** | https://blitz.mexi.wtf/ |
| **Webclient** | https://blitz.mexi.wtf/webclient/ |
| **Telnet raw** | `telnet blitz.mexi.wtf 4100` |

Deploy en **Hetzner** (Ubuntu 24.04 / cpx11 / ash) con **nginx + Let's Encrypt** (HTTPS automático). El game server corre bajo Evennia; el tráfico WebSocket (`wss://blitz.mexi.wtf/ws/`) se hace proxy a puerto interno 4103.

## Qué se siente como terminal real

- **Prompt visible** tipo `tunombre@academy:/academy/ls_dojo$` después de cada comando.
- **History con `↑↓`** (sin Shift, como bash) — plugin custom override en `abyss_node/web/static/webclient/js/plugins/history.js`.
- **Tab autocomplete** de comandos + archivos/dirs del room actual (parseados del output de `ls`).
- **`cd` ergonómico**: `cd` sin args → `/home`, `cd -` → OLDPWD, `cd ..` literal.
- **`mkdir` crea room real** con exit bidireccional — puedes navegar a lo que creas.
- **`touch` + `cat`** persiste archivos virtuales por jugador por room.

## Flujo pedagógico completo

```
ls, pwd, cd → cat → touch, mkdir, grep
  → echo / head / tail / wc / whoami / man / history + pipes (|) + redirects (>, >>)
    → claude skills install austin-griffith/monad-kit
      → claude new contract MiPrimerToken
        → claude deploy MiPrimerToken.sol
          → link <wallet> + claim  (tx real en Monad testnet)
```

**19 quests, 540 `$TERM`, 9 rooms encadenadas**: home → ls_dojo → cd_dojo → cat_dojo → mkdir_dojo → pipe_dojo → redirect_dojo → final_exam → claude_dojo.

## Quests

### Shell básico (7)
| Comando | Reward | Qué enseña |
|---|---:|---|
| `ls` | 10 | listar contenido |
| `pwd` | 10 | directorio actual |
| `cd` | 20 | navegar |
| `cat` | 30 | leer archivos |
| `mkdir` | 30 | crear directorio real (exit bidireccional) |
| `touch` | 30 | crear archivo vacío |
| `grep` | 50 | buscar texto |

### Shell intermedio + operadores (7)
| Comando | Reward | Qué enseña |
|---|---:|---|
| `echo` | 10 | imprimir texto |
| `whoami` | 10 | usuario actual |
| `head` | 20 | primeras líneas |
| `tail` | 20 | últimas líneas |
| `wc` | 20 | contar líneas/palabras/chars |
| `man` | 20 | leer manual |
| `history` | 30 | comandos previos |

### Claude CLI + onchain (5)
| Comando | Reward | Qué enseña |
|---|---:|---|
| `claude` | 30 | abrir el CLI de IA |
| `claude skills install <slug>` | 40 | instalar skill (Austin Griffith / Anthropic) |
| `claude new contract <Nombre>` | 50 | generar Solidity ERC-20 con template |
| `claude deploy <archivo.sol>` | 60 | deployar a Monad testnet (simulado, determinístico) |
| `link 0x…` | 50 | conectar tu wallet EVM |

## Skills disponibles (in-game)

| Slug | Autor | Descripción |
|---|---|---|
| `austin-griffith/scaffold-eth` | Austin Griffith | Quickstart dApps: Hardhat + Next.js + Wagmi |
| `austin-griffith/solidity-basics` | Austin Griffith | Patrones de Solidity: ERC-20, ERC-721, access control |
| `austin-griffith/monad-kit` | Austin Griffith | Deploy directo a Monad testnet + faucet helpers |
| `anthropic/claude-code-guide` | Anthropic | Cómo usar Claude Code CLI (hooks, slash commands, MCP) |

El catálogo vive en `AVAILABLE_SKILLS` en `abyss-node/abyss_node/commands/terminal_commands.py`. Edítalo para remixear tu propia academia (ver [Para builders](#para-builders--forkea-esto)).

## Stack

### Game
- **Evennia 6.0** — MUD framework Python/Django/Twisted
- 9 rooms, 19 comandos, 19 quests, sistema de achievement por milestones
- Webclient HTTP + Telnet raw (puerto 4100)

### AI CLI (simulado in-game)
- Comando `claude` con subcomandos reales: `skills`, `new contract`, `new token`, `deploy`
- 4 skills de referencia (Austin Griffith + Anthropic)
- Contracts generados con template ERC-20 minimal, guardados en el fs virtual del jugador

### Onchain
- **Monad testnet** (chainId `10143`, RPC `testnet-rpc.monad.xyz`)
- ERC-20 minimal custom (sin OpenZeppelin — minimiza gas; el deploy en Monad cuesta ~0.095 MON con gas price fijo 102 gwei)
- **web3.py** firma `transfer()` desde la hot wallet del juego cuando un jugador hace `claim`
- **Nonce locking** para claims concurrentes — `threading.Lock` + cached nonce en `onchain.py` soporta ráfagas de ~10 claims/seg sin colisión de nonce

### Infra de producción
- **Hetzner VPS** (cpx11, ash, Ubuntu 24.04)
- **nginx** como proxy reverse: `/` → landing estático, `/webclient/`, `/static/`, `/admin/` → Evennia HTTP (4101), `/ws/` → WebSocket (4103)
- **Let's Encrypt** con `certbot --nginx` (HTTP→HTTPS redirect automático)
- **Cloudflare DNS** apuntando `blitz.mexi.wtf` directo al VPS (A record, sin CF proxy)
- **Foundry** para compile + deploy del contrato $TERM

## Onchain receipts

| | |
|---|---|
| Contrato `$TERM` | [`0x6BCC8bA023faD77Fd9c16735fD0DCb030F1b03d8`](https://testnet.monadexplorer.com/address/0x6BCC8bA023faD77Fd9c16735fD0DCb030F1b03d8) |
| Tx de claim (desde local) | [`0x76544f…089567e`](https://testnet.monadexplorer.com/tx/0x76544f781503b8b9b0205545ef0d3958f196ebf6b62bbd78f9364cfb8089567e) |
| Tx de claim (desde PROD Hetzner) | [`0xdcd3c7…b3e55b`](https://testnet.monadexplorer.com/tx/0xdcd3c747551ebc8f30e88cf891a791cce3734c11fdff4d26e9c76b08b7b3e55b) |
| Chain ID | `10143` |
| Explorer | https://testnet.monadexplorer.com |

## Screenshots

| Login | Home |
|---|---|
| ![](docs/pitch/screenshots/webclient-01-login.png) | ![](docs/pitch/screenshots/webclient-02-home.png) |

| `pipe_dojo` (<code>&#124;</code>) | `redirect_dojo` (`>`) |
|---|---|
| ![](docs/pitch/screenshots/webclient-06-pipe.png) | ![](docs/pitch/screenshots/webclient-07-redirect.png) |

| `claude skills list` | `claude new contract` |
|---|---|
| ![](docs/pitch/screenshots/webclient-08-skills.png) | ![](docs/pitch/screenshots/webclient-09-newcontract.png) |

| `claude deploy` (clímax) | `claim` onchain |
|---|---|
| ![](docs/pitch/screenshots/webclient-10-deploy.png) | ![](docs/pitch/screenshots/webclient-05-claim.png) |

## Run locally

```bash
# 1. Clonar y preparar venv
git clone https://github.com/mexiweb3/monad-terminal-academy
cd monad-terminal-academy
python3 -m venv .venv
source .venv/bin/activate
pip install evennia web3 python-dotenv

# 2. Config onchain — crear deploy/.env (ejemplo):
mkdir -p deploy
cat > deploy/.env <<'EOF'
PRIVATE_KEY=0x<tu hot wallet con MON de faucet.monad.xyz>
MONAD_RPC_URL=https://testnet-rpc.monad.xyz
MONAD_CHAIN_ID=10143
MONAD_EXPLORER=https://testnet.monadexplorer.com
GAME_WALLET_ADDRESS=0x<address de esa hot wallet>
ABYSS_CONTRACT=
EOF
chmod 600 deploy/.env

# 3. Deploy del ERC-20 $TERM (opcional — puedes reusar el existente)
cd contracts
forge build
export $(grep -v '^#' ../deploy/.env | xargs)
forge script script/DeployAbyss.s.sol:DeployAbyss --rpc-url $MONAD_RPC_URL --broadcast --legacy
# copia la address al .env como ABYSS_CONTRACT=0x...

# 4. Arrancar Evennia
cd ../abyss-node/abyss_node
evennia migrate --noinput
python _init_admin.py      # crea admin/monadtestnet123
python _build_world.py     # construye las 9 rooms
evennia collectstatic --clear --noinput
evennia start
```

Juega via telnet (`telnet localhost 4100`) o webclient (`http://localhost:4101/webclient/`). Credenciales admin: `admin` / `monadtestnet123`.

## Para builders — Forkea esto

Monad Terminal Academy está diseñado como **template** para onboardear dev-newbies a la chain que elijas. El flujo es 100% remixeable:

1. Edita `AVAILABLE_SKILLS` en `abyss-node/abyss_node/commands/terminal_commands.py` con tus propios skills (`owner/slug` + autor + descripción).
2. Edita `_CONTRACT_TEMPLATE` en el mismo archivo para cambiar qué genera `claude new contract` (ERC-721? vault? voting?).
3. Cambia la red en `deploy/.env` (`MONAD_RPC_URL`, `MONAD_CHAIN_ID`) para apuntar a tu L1/L2.
4. Redeploya el contrato reward (`contracts/src/MonadAbyss.sol` — ERC-20 minimal) con tu token.
5. Personaliza rooms/quests en `world/zones/terminal_academy.py` y `QUESTS` en `terminal_commands.py`.

Resultado: **tu propia "X Chain Academy"** — onboarding gamificado con learn-to-earn onchain en la cadena que tu hackathon esté incubando.

## Documentación

- [`PRD.md`](PRD.md) — producto y sesiones de trabajo paralelas
- [`PITCH.md`](PITCH.md) — pitch de 3 minutos
- [`SUBMISSION.md`](SUBMISSION.md) — copy-paste para el formulario de entrega
- [`docs/pitch/pitch.md`](docs/pitch/pitch.md) — slide deck de 1 página
- [`docs/pitch/demo-script.md`](docs/pitch/demo-script.md) — guión de demo de 2 min

## Créditos

- Base: [`abyss-node`](./abyss-node/) — MUD cyberpunk Evennia (proyecto original del que pivotamos)
- Framework: [Evennia](https://www.evennia.com) · [Foundry](https://getfoundry.sh) · [web3.py](https://web3py.readthedocs.io)
- AI CLI: inspirado en [Claude Code](https://claude.com/claude-code) y los skills de [Austin Griffith](https://github.com/austintgriffith)
- Chain: [Monad](https://monad.xyz) testnet

---

Hecho con terminal, Claude y bloques de Monad — **Monad Blitz Monterrey 2026**.
