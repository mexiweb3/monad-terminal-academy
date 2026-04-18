# Monad Terminal Academy — Pitch

> De `ls` a `claude deploy` en 15 minutos. MUD educativo onchain con Claude CLI integrado.

---

## Problema

- Onboarding onchain para principiantes sigue siendo un precipicio: terminal + Solidity + deploy son 3 curvas a la vez.
- Los cursos de CLI son aburridos y los bootcamps de Solidity asumen que ya sabés `grep`.
- Los juniors no aprenden a delegar código a IA — o usan chatbots a ciegas sin entender el flujo de skills/CLI.
- Los hackathons piden demos con tx reales, no mockups — pero los nuevos devs no llegan ahí en un fin de semana.
- Falta un "Duolingo de ser builder onchain" que cubra **shell + IA + deploy** en un solo flujo con stake real.

## Solución

- MUD educativo donde **el mundo es un filesystem**: rooms = directorios, items = archivos, exits = subdirectorios.
- **19 quests en 3 tiers**: shell básico (7) → shell intermedio + operadores (7) → **Claude CLI + onchain (5)**.
- **Claude CLI simulado in-game**: `claude skills install austin-griffith/monad-kit` → `claude new contract MiToken` → `claude deploy MiToken.sol`. El jugador aprende a pedirle código a una IA sin salir de la Academia.
- Al completar las 19 quests: `link <wallet>` + `claim` → tx real en Monad testnet, 540 `$TERM` al bolsillo del jugador.
- Accesible en navegador, sin instalación, sin wallet plugin.

## Demo (2 min)

- **0:00–0:20** — login, `ls`, `cat README.txt`, `cd ls_dojo`.
- **0:20–0:50** — shell intermedio: `echo hola | wc`, `echo foo > bar.txt`.
- **0:50–1:20** — `claude skills install austin-griffith/monad-kit`, `claude new contract MiToken`, `cat MiToken.sol`.
- **1:20–1:40** — **`claude deploy MiToken.sol`** → clímax: address + tx onchain simulada.
- **1:40–2:00** — `link <wallet>` + `claim` → **tx real** [`0x753b572d…827b`](https://testnet.monadexplorer.com/tx/0x753b572d4cc3265d082d5da4793bb6d8f29bcfeb355d8b49adc463dabddb827b) en Monad explorer.

## Stack

- **Evennia 6.0** — MUD framework maduro Python/Django (puertos 4100/4101/4103).
- **Claude-style CLI in-game** — `claude`, `claude skills list/install`, `claude new contract/token`, `claude deploy`. 4 skills de referencia (Austin Griffith + Anthropic) listados en `AVAILABLE_SKILLS`.
- **ERC-20 minimal custom** en Solidity — sin OpenZeppelin; `contracts/src/MonadAbyss.sol`, deployado en [`0x6BCC…03d8`](https://testnet.monadexplorer.com/address/0x6BCC8bA023faD77Fd9c16735fD0DCb030F1b03d8).
- **web3.py** — el servidor firma `transfer()` desde la hot wallet cada vez que un player hace `claim`.
- **Cloudflare Quick Tunnels + Foundry** — infra sin API keys ni cuentas; reproducible en 5 minutos.

## Visión

- **Template forkeable**: editás `AVAILABLE_SKILLS` + `_CONTRACT_TEMPLATE` → tu propia "X Chain Academy" para cualquier L1/L2.
- **Credencial onchain**: al graduarse, el jugador recibe un SBT "I passed the terminal + Claude + deploy". Útil como proof-of-onboarding para otros dApps.
- **Zonas 2+**: `git_dojo` (commits reales), `tests_dojo` (foundry test), `frontend_dojo` (scaffold-eth real).
- **DAO de curriculum**: autores proponen nuevas quests/skills, votadas con `$TERM`, pagadas por uso.
- **Monad Academy oficial** post-mainnet: onboardear la siguiente ola de devs con un flujo que ya probó funcionar en testnet.
