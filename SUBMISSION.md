# Monad Terminal Academy — Submission Blitz MTY 2026

> Copy-paste-ready para el formulario de entrega (17:00 – 17:30 CST).

## Nombre
**Monad Terminal Academy**

## Descripción (1 línea)
Aprende a usar la terminal jugando — gana `$TERM` ERC-20 en Monad testnet por cada comando que dominas.

## Descripción (1 párrafo)
Monad Terminal Academy es un MUD educativo onchain: un mundo de texto modelado como un filesystem real donde las salas son directorios y los items son archivos. Los jugadores aprenden 19 comandos REALES de shell (`ls`, `cd`, `cat`, `grep`, pipes, redirects, `head`, `tail`, incluso un comando `claude` que les enseña a pair-program con IA) y cada comando nuevo que dominan les da `$TERM`, un ERC-20 que reciben directamente en su wallet en **Monad testnet** al hacer `claim`. Construido en un día sobre Evennia + Foundry; contrato deployado y claims funcionando end-to-end en testnet.

## Links

- **Demo live PROD** (Hetzner VPS, Ubuntu 24.04 / cpx11 / ash): **http://178.156.198.144:4101/webclient/**
- **Backup demo** (Cloudflare Quick Tunnel desde local): https://die-hand-alexandria-joan.trycloudflare.com/webclient/
- **Landing**: https://aka-warning-old-geneva.trycloudflare.com/
- **Repo GitHub**: *(pendiente push — subiendo en segundos)*
- **Contrato $TERM (Monad testnet)**: `0x6BCC8bA023faD77Fd9c16735fD0DCb030F1b03d8`
- **Explorer del contrato**: https://testnet.monadexplorer.com/address/0x6BCC8bA023faD77Fd9c16735fD0DCb030F1b03d8
- **Txs ejemplo de claim**:
  - desde local: https://testnet.monadexplorer.com/tx/0x76544f781503b8b9b0205545ef0d3958f196ebf6b62bbd78f9364cfb8089567e
  - **desde PROD (Hetzner)**: https://testnet.monadexplorer.com/tx/0xdcd3c747551ebc8f30e88cf891a791cce3734c11fdff4d26e9c76b08b7b3e55b
- **Pitch text (3 min)**: ver `PITCH.md` en el repo

## Stack

- **Game server**: Evennia 6.0 (Python / Django / Twisted)
- **Smart contract**: Solidity 0.8 · Foundry · ERC-20 custom (sin OpenZeppelin para gas)
- **Onchain bridge**: web3.py (server firma `transfer()` al claim)
- **Webclient**: Evennia + plugin custom (override de `history.js` con `ArrowUp`/`Down` history + TAB autocomplete)
- **Hosting**: Cloudflare Quick Tunnel (demo live) · landing via 3er tunnel
- **Deploy chain**: Monad testnet (chainId 10143)

## Entregables del hackathon (checklist del Notion)

- [x] Demo funcional — URL pública arriba
- [x] Contrato desplegado en Monad testnet — address arriba
- [ ] Repo público en GitHub con README — pendiente en los próximos minutos
- [x] Pitch preparado — 3 min, ver `PITCH.md`

## Equipo
- @meximalist (GitHub: mexiweb3)

## ¿Cómo probarlo en 60 segundos?

1. Abre https://die-hand-alexandria-joan.trycloudflare.com/webclient/
2. Escribe: `create tunombre tupass`
3. Tú aparece en `/home`. Escribe `ls`, `cat README.txt`, `cd ls_dojo`, `cd cd_dojo`, `cat secret.txt`.
4. `link 0x<tu_wallet_EVM>` (MetaMask con Monad testnet agregado).
5. `claim` — ves la tx onchain en el explorer.

## Monad testnet setup (para jueces jugadores)

- RPC: `https://testnet-rpc.monad.xyz`
- Chain ID: `10143`
- Symbol: `MON`
- Explorer: `https://testnet.monadexplorer.com`
- Faucet: `https://faucet.monad.xyz`

## Estructura del pitch (3 min)

1. **Problema** (30 s): millones quieren entrar a tech/web3 pero le tienen miedo a la terminal.
2. **Solución** (45 s): MUD onchain que enseña terminal + recompensa con `$TERM`.
3. **Revenue** (30 s): freemium-to-burn, B2B white-label a bootcamps, NFT de certificación.
4. **Monad** (30 s): ERC-20 deployado · high-TPS para eventos onchain por comando · demo tx en vivo.
5. **Validación** (20 s): construido en 1 día, smoke test end-to-end 0 errores, 19 quests completables.
