# Terminal Academy — Pitch de 3 minutos

> Estructura del pitch oficial (Notion Blitz MTY): **Problema · Solución · Revenue · Monad · Validación**. ≤ 3 min, ≤ 1 idea por bullet.

---

## 🎭 Abre con el hook (15 s)

> "¿Cuántos de ustedes le han tenido miedo a una terminal? Yo también.
> La primera vez que abrí bash, cerré la laptop. Hoy construimos una solución onchain para que ningún principiante vuelva a sentir eso.
> Los invito a **Terminal Academy**."

*(mientras hablas, abres [https://blitz.mexi.wtf/webclient/](https://blitz.mexi.wtf/webclient/) en pantalla completa)*

---

## 1️⃣ Problema (30 s)

- **Miles de personas quieren entrar a tech / web3 / cripto pero no saben usar una terminal.**
- Los tutoriales de hoy son PDFs aburridos o cursos de 40 hrs — **la retención es brutalmente baja**.
- En web3 esto es peor: no puedes deployar un contrato, correr un nodo, ni hacer un `forge script` si no te sientes cómodo con `cd`, `ls`, `cat`, `grep`.
- **Los bootcamps pagan hasta $2,000 USD por alumno. La mayoría desertan en la primera semana por friction técnica.**

## 2️⃣ Solución (45 s)

**Terminal Academy** es un **MUD onchain** (mundo de texto) modelado como un filesystem real:

- Las **salas = directorios** (9 rooms encadenadas: `/home` → `ls_dojo` → `cd_dojo` → `cat_dojo` → `mkdir_dojo` → `pipe_dojo` → `redirect_dojo` → `final_exam` → **`claude_dojo`**).
- Los **items = archivos** (`README.txt`, `log.txt`, `secret.txt`, cheatsheets).
- **23 comandos REALES** de terminal con comportamiento de shell real: **prompt dinámico** (`tunombre@academy:/academy/ls_dojo$`), **`↑↓` history**, **`Tab` autocomplete**, `cd -` para OLDPWD, `mkdir` que crea directorios navegables. Y un comando **`claude`** que enseña a pair-programar con IA desde la terminal.
- Cada comando aprendido completa una **quest** → acumula `$TERM`. 23 quests, **700 `$TERM`** al completar todo.
- Cuando el jugador linkea su wallet con `link 0x...` y corre `claim`, recibe sus `$TERM` **onchain en Monad testnet**.

*(demo live — 45 s: create account → ls → cat README → cd → grep → link → claim → mostrar tx en explorer)*

## 3️⃣ ¿Cómo hace dinero? (30 s)

Tres capas:

1. **Freemium-to-burn**: jugador gratis aprende básico. Para desbloquear módulos avanzados (git, ssh, docker, solidity, foundry) **quema `$TERM`**.
2. **B2B academies white-label**: bootcamps y empresas pagan **en USD** por deploys propios de la Academia con su branding y su currículum. Cada empresa tiene su propio ERC-20.
3. **Certificaciones NFT**: jugador que termine el programa recibe un **NFT onchain "Graduated"** — verifiable, portable entre empleadores. **Cobramos fee de mint.**

Ticket promedio: $5 USD/alumno/mes en B2C, $20k USD/deploy en B2B.

## 4️⃣ ¿Cómo usa Monad? (30 s)

- `$TERM` es **ERC-20 en Monad testnet** (contrato [`0x6BCC…03d8`](https://testnet.monadexplorer.com/address/0x6BCC8bA023faD77Fd9c16735fD0DCb030F1b03d8)).
- Cada `claim` es una **transferencia onchain** firmada por la hot wallet del juego — demo en vivo muestra la [tx real](https://testnet.monadexplorer.com/tx/0xdcd3c747551ebc8f30e88cf891a791cce3734c11fdff4d26e9c76b08b7b3e55b).
- **Diseñado para escalar en Monad**: implementamos **nonce locking** en el server — `threading.Lock` con nonce en caché que permite **10 claims/seg** por hot wallet sin colisión. Con el high-TPS de Monad (10k TPS, 1 bloque/seg), cada comando ejecutado puede ser un evento onchain sin blowup de gas.
- Roadmap: burns de $TERM para desbloquear contenido, mint de NFT de certificación (ERC-721), leaderboard global onchain (ya tenemos el código para leer eventos Transfer del contrato).

## 5️⃣ Validación / aprendizaje (20 s)

- **Construido en 1 día** por este equipo — stack nuevo (Evennia + Foundry + Monad testnet) integrado end-to-end, desplegado en producción con TLS.
- **Smoke test completo**: jugador nuevo `create demostudent …` completa 19 quests con 0 errores → `claim` onchain con tx real en el explorer en la primera corrida.
- **Stress test concurrente**: 3 claims simultáneos tardan **0.4 segundos** con 3 tx hashes distintos — nonce locking funciona bajo carga.
- **Aprendizaje clave**: principiantes responden al gameplay ANTES que al código. El token onchain es el gancho, el aprendizaje es el producto. Añadir el comando `claude` abrió una capa no planeada — **enseñamos terminal Y enseñamos a pair-programar con IA**, que es el stack real del dev 2026.

## 🎤 Cierre (10 s)

> "Si creen que web3 necesita onboarding mejor, esta es nuestra apuesta.
> **Terminal Academy. Aprendes terminal, te llevas tokens reales.**
> Play ahora: `blitz.mexi.wtf` · Repo: `github.com/mexiweb3/monad-terminal-academy` · Gracias."

---

## Assets a tener listos en pantalla

1. **Webclient** abierto en `https://blitz.mexi.wtf/webclient/` con el banner ANSI + prompt visible
2. **Landing** `https://blitz.mexi.wtf/` en otra pestaña (muestra ASCII art + quests + stats)
3. **Explorer** `https://testnet.monadexplorer.com/tx/0xdcd3c7…b3e55b` con tx confirmada
4. **GitHub** `https://github.com/mexiweb3/monad-terminal-academy` con README + screenshots

## Plan B si la demo falla

- Screenshots pre-capturados en `docs/pitch/screenshots/` (10 imágenes cubriendo login → claim).
- Si el dominio no resuelve: acceso por IP directa `http://178.156.198.144:4101/webclient/`.
- Si el VPS tiene un hipo: backup en Cloudflare Quick Tunnel desde local (generable en 5 s con un comando).

## Notas

- **Duración real**: ~2:45. 15 s de buffer para aplausos/transiciones.
- **Tono**: energía alta, directo, español neutral. Evita tecnicismos innecesarios (no todos los jueces son devs).
- **El número mágico**: `$10,000 MXN` = primer premio. Cada segundo cuenta.
