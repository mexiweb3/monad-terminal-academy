# Terminal Academy — Submission Blitz MTY 2026

> Copy-paste-ready para el formulario de entrega (17:00 – 17:30 CST).

## Project Title
**Terminal Academy**

## Description (1 línea)
Aprende a usar la terminal jugando — gana `$TERM` ERC-20 en Monad testnet por cada comando que dominas.

## Description (1 párrafo)
Terminal Academy es un MUD educativo onchain: un mundo de texto modelado como un filesystem real donde las salas son directorios y los items son archivos. Los jugadores aprenden 23 comandos REALES de shell + install de CLI tools (`ls`, `cd`, `cat`, `grep`, pipes `|`, redirects `>` / `>>`, `head`, `tail`) con **comportamiento de terminal real** (prompt dinámico, `↑↓` history, `Tab` autocomplete, `cd -`, `mkdir` que crea directorios navegables) — más un comando `claude` que simula pair-programar con IA para generar y deployar contratos. Al completar quests conectan su wallet con `link 0x...` y corren `claim` para recibir sus `$TERM` onchain. Deployado en producción en Hetzner con HTTPS vía Let's Encrypt.

## Tweet (copia, publica, y pega el URL del tweet)

```
🖥️ Terminal Academy — de `ls` a deployar un ERC-20 en 15 min.

MUD educativo onchain:
• 19 comandos reales de shell (con prompt, ↑↓, Tab)
• Claude CLI simulado in-game
• Claim $TERM en Monad testnet al completar quests

🎮 https://blitz.mexi.wtf
🐙 github.com/mexiweb3/monad-terminal-academy

#MonadBlitz #MTY
```

## Links

| Campo | Valor |
|---|---|
| **Demo URL** | https://blitz.mexi.wtf/ |
| **Webclient directo** | https://blitz.mexi.wtf/webclient/ |
| **Telnet raw** | `telnet blitz.mexi.wtf 4100` |
| **GitHub URL** | https://github.com/mexiweb3/monad-terminal-academy |
| **Contrato $TERM** | `0x6BCC8bA023faD77Fd9c16735fD0DCb030F1b03d8` |
| **Explorer contrato** | https://testnet.monadexplorer.com/address/0x6BCC8bA023faD77Fd9c16735fD0DCb030F1b03d8 |
| **Tx claim desde PROD** | [`0xdcd3c7…b3e55b`](https://testnet.monadexplorer.com/tx/0xdcd3c747551ebc8f30e88cf891a791cce3734c11fdff4d26e9c76b08b7b3e55b) |
| **Tx claim primera corrida (local)** | [`0x76544f…089567e`](https://testnet.monadexplorer.com/tx/0x76544f781503b8b9b0205545ef0d3958f196ebf6b62bbd78f9364cfb8089567e) |

## Category (sugeridas)
**Education · Gaming · Developer Tools** (aplica cualquiera de las tres — prioriza Education o Gaming según las opciones del formulario)

## Stack

- **Game server**: Evennia 6.0 (Python 3.13 / Django / Twisted)
- **Smart contract**: Solidity 0.8 · Foundry · ERC-20 custom (sin OpenZeppelin para minimizar gas)
- **Onchain bridge**: web3.py con nonce locking (soporta ~10 claims/seg concurrentes sin colisión)
- **Webclient**: Evennia + plugin custom (`history.js` override con `↑↓` history sin Shift + Tab autocomplete + room-context parsing)
- **Hosting producción**: Hetzner VPS (cpx11 / ash / Ubuntu 24.04) + nginx proxy reverse + Let's Encrypt TLS
- **DNS**: Cloudflare (A record directo, sin CF proxy)
- **Deploy chain**: Monad testnet (chainId `10143`, RPC `testnet-rpc.monad.xyz`)

## Entregables del hackathon (checklist del Notion)

- [x] Demo funcional — **https://blitz.mexi.wtf/**
- [x] Contrato desplegado en Monad testnet — `0x6BCC8bA023faD77Fd9c16735fD0DCb030F1b03d8`
- [x] Repo público en GitHub con README — https://github.com/mexiweb3/monad-terminal-academy
- [x] Pitch preparado — 3 min, ver [`PITCH.md`](PITCH.md)

## Equipo

- @meximalist (GitHub: [@mexiweb3](https://github.com/mexiweb3))

## ¿Cómo probarlo en 60 segundos?

1. Abre https://blitz.mexi.wtf/webclient/
2. Escribe: `create tunombre tupassword`
3. Apareces en `/home`. Ejecuta: `ls`, `cat README.txt`, `cd ls_dojo`, `cd cd_dojo`, `cat secret.txt`.
4. Prueba `↑` para recuperar comandos anteriores, `Tab` para autocompletar.
5. `link 0x<tu_wallet_EVM>` (MetaMask con Monad testnet configurada — ver abajo).
6. `claim` — ves la tx onchain en el explorer con tu address recibiendo `$TERM`.

## Monad testnet (para jueces que jueguen con wallet propia)

- **RPC**: `https://testnet-rpc.monad.xyz`
- **Chain ID**: `10143`
- **Symbol**: `MON`
- **Explorer**: `https://testnet.monadexplorer.com`
- **Faucet**: `https://faucet.monad.xyz` (da ~0.01 MON por claim)

## Estructura del pitch (3 min — ver `PITCH.md` completo)

1. **Problema** (30 s): millones quieren entrar a tech/web3 pero le tienen miedo a la terminal.
2. **Solución** (45 s): MUD onchain que enseña terminal con comportamiento real + recompensa con `$TERM`.
3. **Revenue** (30 s): freemium-to-burn, B2B white-label a bootcamps, NFT de certificación.
4. **Monad** (30 s): ERC-20 deployado · nonce locking listo para carga · high-TPS habilita eventos onchain por comando.
5. **Validación** (20 s): construido en 1 día, smoke test 0 errores en 19 quests, 3 claims concurrentes en 0.4 s, deploy a producción con TLS.
