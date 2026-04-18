# Monad Terminal Academy — Pitch de 3 minutos

> Estructura del pitch oficial (Notion Blitz MTY): **Problema · Solución · Revenue · Monad · Validación**. ≤ 3 min, ≤ 1 idea por bullet.

---

## 🎭 Abre con el hook (15 s)

> "¿Cuántos de ustedes le han tenido miedo a una terminal? Yo también.
> La primera vez que abrí bash, cerré la laptop. Hoy construimos una solución onchain para que ningún principiante vuelva a sentir eso.
> Los invito a **Monad Terminal Academy**."

*(mientras hablas, abres https://die-hand-alexandria-joan.trycloudflare.com/webclient/ en pantalla completa)*

---

## 1️⃣ Problema (30 s)

- **Miles de personas quieren entrar a tech / web3 / cripto pero no saben usar una terminal.**
- Los tutoriales de hoy son PDFs aburridos o cursos de 40 hrs — **la retención es brutalmente baja**.
- En web3 esto es peor: no puedes deployar un contrato, correr un nodo, ni hacer un `forge script` si no te sientes cómodo con `cd`, `ls`, `cat`, `grep`.
- **Los bootcamps pagan hasta $2,000 USD por alumno. La mayoría desertan en la primera semana por friction técnica.**

## 2️⃣ Solución (45 s)

**Monad Terminal Academy** es un **MUD onchain** (mundo de texto) modelado como un filesystem real:

- Las **salas = directorios** (9 rooms encadenadas: `/home` → `ls_dojo` → `cd_dojo` → `cat_dojo` → `mkdir_dojo` → `pipe_dojo` → `redirect_dojo` → `final_exam` → **`claude_dojo`**).
- Los **items = archivos** (`README.txt`, `log.txt`, `secret.txt`, cheatsheets).
- **19 comandos REALES** de terminal: desde `ls` / `cd` / `cat` hasta `grep` / `echo` con pipes `|`, redirects `>` `>>`, `head` / `tail` / `wc` / `man` / `history` — y un comando **`claude`** que enseña a usar IA desde la terminal (skills, scaffold de contratos, deploy).
- El webclient soporta **↑↓ para history y TAB para autocomplete**, igual que bash de verdad.
- Cada comando aprendido completa una **quest** → acumula `$TERM`. 19 quests, **540 `$TERM`** al completar todo.
- Cuando el jugador linkea su wallet con `link 0x...` y corre `claim`, recibe sus `$TERM` **onchain en Monad testnet**.

*(demo live — 45 s: create account → ls → cat README → cd → grep → link → claim → mostrar tx en explorer)*

## 3️⃣ ¿Cómo hace dinero? (30 s)

Tres capas:

1. **Freemium-to-burn**: jugador gratis aprende básico. Para desbloquear módulos avanzados (git, ssh, docker, solidity, foundry) **quema `$TERM`**.
2. **B2B academies white-label**: bootcamps y empresas pagan **en USD** por deploys propios de la Academia con su branding y su currículum. Cada empresa tiene su propio ERC-20.
3. **Certificaciones NFT**: jugador que termine el programa recibe un **NFT onchain "Graduated"** — verifiable, portable entre empleadores. **Cobramos fee de mint.**

Ticket promedio: $5 USD/alumno/mes en B2C, $20k USD/deploy en B2B.

## 4️⃣ ¿Cómo usa Monad? (30 s)

- `$TERM` es **ERC-20 en Monad testnet** (contrato `0x6BCC8bA023faD77Fd9c16735fD0DCb030F1b03d8`).
- Cada `claim` es una **transferencia onchain** firmada por la hot wallet del juego — ya hicimos [demo live tx hoy](https://testnet.monadexplorer.com/tx/0x76544f781503b8b9b0205545ef0d3958f196ebf6b62bbd78f9364cfb8089567e).
- **¿Por qué Monad y no Base/Arbitrum?** El high-TPS es clave cuando escale a miles de estudiantes completando quests en paralelo. Cada comando ejecutado puede ser un evento onchain sin blowup de gas — **eso solo lo hace posible Monad**.
- Roadmap: burns de $TERM para desbloquear contenido, mint de NFT de certificación (ERC-721), eventualmente leaderboard global onchain.

## 5️⃣ Validación / aprendizaje (20 s)

- **Construido en 1 día** por este equipo — stack nuevo (Evennia + Foundry + Monad testnet) integrado end-to-end.
- **Smoke test completo**: jugador nuevo `create demostudent ...` completa 19 quests con 0 errores → `claim` onchain con tx real en el explorer en la primera corrida.
- **Aprendizaje clave**: principiantes responden al gameplay ANTES que al código. El token onchain es el gancho, el aprendizaje es el producto. Añadir el comando `claude` abrió una capa no planeada — **enseñamos terminal Y enseñamos a pair-program con IA**, que es el stack real del dev 2026.
- **Riesgo principal**: UX del webclient todavía asusta a no-técnicos → siguiente iteración: modo "novato absoluto" con NPC instructor guiado (Prof. Shell, ya en la base).

## 🎤 Cierre (10 s)

> "Si creen que web3 necesita onboarding mejor, esta es nuestra apuesta.
> **Monad Terminal Academy. Aprendes terminal, te llevas tokens reales.**
> Play ahora: `die-hand-alexandria-joan.trycloudflare.com/webclient/` · Repo: [próximamente] · Gracias."

---

## Assets a tener listos en pantalla

1. Webclient abierto en `/home` con el banner ANSI visible
2. Tab del navegador con `testnet.monadexplorer.com/tx/0x76544f...089567e`
3. Tab con este PITCH.md por si pierdes el hilo
4. Tab con el landing `aka-warning-old-geneva.trycloudflare.com`

## Plan B si la demo falla

- Screenshots pre-capturados en `docs/pitch/screenshots/`
- Mencionar: "el demo corre en local via Cloudflare Quick Tunnel — URL pública efímera pero reproducible con un solo comando". Muestras el código en 5 s.

## Notas

- **Duración real**: 2:40 aprox. 20 s de buffer para aplausos/transiciones.
- **Tono**: energía alta, directo, español coloquial. Evita tecnicismos innecesarios (no todos los jueces son devs).
- **El número mágico**: `$10,000 MXN` = primer premio. Cada segundo cuenta.
