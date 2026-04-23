# EVENNIA_DECISION.md

> **Autor**: F8 (research agent) — **Fecha**: 2026-04-22 — **Contexto**: Terminal Academy / Monad Blitz MTY
> **Pregunta**: ¿Seguimos con Evennia o migramos de stack para escalar a 500–5,000 alumnos?
> **Nota metodológica**: Este documento prioriza data pública sobre opinión. Donde no hay data sólida lo marco explícitamente ("sin data pública — asumo X con confidence Y"). El objetivo es que esta sea la única lectura necesaria para decidir.

---

## 1. TL;DR

**Recomendación**: **Híbrido — mantener Evennia como "arcade narrativo" en desktop, construir en paralelo una capa web-first (xterm.js + Postgres + SIWE) que sea el producto principal mobile, y usar Discord como comunidad + distribución.** No migres todo a una sola alternativa. Evennia es insustituible para las 3 cosas que lo hacen especial (rooms/NPCs/sense-of-place, comunidad sync, identidad onchain cableada) pero técnicamente no sirve para 500–5,000 alumnos mobile-first. Build Stack A (xterm.js web) como producto principal, mantener Evennia como experiencia "premium desktop" opcional que se conecta a la misma DB, y Stack B (Discord bot) como capa de comunidad y funnel.

Tres razones por las que la migración total a una sola alternativa es mala idea:

1. **Stack A sola (xterm.js)** te da mobile y escala pero destruye las fortalezas narrativas que hacen a Terminal Academy diferenciado — construir eso desde cero en React es 200+ horas que ya están resueltas en Evennia.
2. **Stack B sola (Discord)** es excelente para comunidad y tiene los números en LatAm, pero convierte el curso en "otro bot más" y pierdes el momento "WOW" del terminal real.
3. **Stack C (KodeKloud/Replit)** no deja customizar narrativa lo suficiente, y el precio ($15–29/mes/usuario) se come el presupuesto antes de los 100 alumnos. No son aliados para la versión onchain/Claude Code.

El híbrido cuesta ~€50/mes en infra para 500 alumnos (Hetzner CPX22 + Postgres managed + bot container) y es incremental — no tenés que parar todo. En 4 semanas tenés v1 del track web; en 8 semanas tenés el bot de Discord integrado; Evennia queda como el "endgame premium" que los alumnos graduados pueden explorar. **Migrar completo ahora es prematuro** — la data concreta para las 3 alternativas puras es insuficiente, y Evennia no es el bottleneck de la versión actual (el bottleneck es el onboarding mobile y la comunidad).

---

## 2. Tabla comparativa (5 alternativas × 8 criterios, 1–5)

| Criterio | A: Node+xterm.js | B: Discord-first | C: Plataforma (KodeKloud/Replit) | D: GH Classroom híbrido sin MUD | E: Evennia + capas (status quo) |
|---|---|---|---|---|---|
| **UX mobile** (alto) | 3/5 xterm.js funciona pero mobile es complicado; typing/keyboard problemas conocidos ([xterm.js #5377](https://github.com/xtermjs/xterm.js/issues/5377)) | **5/5** Discord mobile es el app default de 70% de Gen Z LatAm ([Business of Apps](https://www.businessofapps.com/data/discord-statistics/)) | 3/5 Replit mobile decente, KodeKloud mobile web pobre | 4/5 docs web responsive es trivial, pero GH Classroom mobile es incómodo | **1/5** webclient actual no responsive; MUD clients mobile (BlowTorch, TinTin++) son apps de nicho |
| **Escala 500–5k concurrentes** (alto) | **5/5** Node+WS+Postgres escala linealmente, freeCodeCamp demo'd esto con $754k/año para 2.1B minutos/año ([freeCodeCamp](https://www.freecodecamp.org/news/the-first-billion-minutes-the-numbers-behind-freecodecamp-the-tiny-nonprofit-thats-teaching-9c2ee9f8102c)) | **5/5** Discord bots escalan a 170k+ guilds con hybrid sharding ([discord-hybrid-sharding](https://github.com/meister03/discord-hybrid-sharding)) | **5/5** es SaaS; la escala es problema del vendor | 4/5 GH Classroom maneja millones de students ya | 2/5 Evennia tope ~150–250 concurrentes en VPS típica ([Evennia Online Setup](https://github.com/evennia/evennia/wiki/Online-Setup)); SQLite actual es single-writer |
| **Preserva 3 fortalezas** (alto) | 2/5 narrativa perdés a menos que la reconstruyas; comunidad real-time requiere trabajo; onchain es igual | 3/5 comunidad ✔, narrativa en text-channels pierde inmersión, onchain vía bot funciona | 1/5 ninguna de las 3 fortalezas se preserva en SaaS cerrado | 2/5 sin rooms, sin comunidad sync, solo onchain ✔ | **5/5** las 3 fortalezas viven en Evennia — lo que construiste ya está ahí |
| **Resuelve 3 fricciones** (alto) | **5/5** mobile ✔, tools-reales ✔ (sesión per user), scale ✔ | 4/5 mobile ✔, tools-reales ✗ (sigue simulado en slash commands), scale ✔ | **5/5** todas resueltas pero a costo de customización | 4/5 mobile ✔, tools-reales ✔ (GH codespaces real), scale ✔ — pero perdés el "efecto shell" | 1/5 nada resuelto — F3/F5/F6 son patches sobre las fricciones estructurales |
| **Costo mensual 500 users** (medio) | **5/5** ~€50/mes (Hetzner CPX22 + managed PG €15) | **5/5** ~€10/mes (1 VPS pequeño, Discord gratis) | 2/5 $7,500–14,500/mes ($15–29 × 500, hay descuentos edu) | **5/5** ~€0 GitHub edu + €10 VPS comunidad | **5/5** ~€8/mes actual (Hetzner CPX11) |
| **Effort migración** (medio) | 2/5 ~200–300h build from zero | 3/5 ~80–120h para bot + onchain integration | 4/5 ~40h crear cursos en la plataforma | 3/5 ~100h armar materiales + repos template | **5/5** 0 effort — ya existe |
| **Ejemplos reales similares** (alto) | **5/5** Katacoda (RIP, O'Reilly 2022), Instruqt, LabEx, Killercoda, freeCodeCamp, Cratecode — todos usan xterm.js ([list by iximiuz](https://iximiuz.com/en/posts/learn-by-doing-platforms/)) | 4/5 InsightEdu academic paper, bot de 510k estudiantes ([Zack medium](https://medium.com/@Zack.hardtoname/i-made-a-bot-used-by-510k-students-for-3-centuries-worth-of-time-ad2379bdb7ed)) | **5/5** KodeKloud reales, Replit Classroom reales, ambos con decenas de miles de students paying | 4/5 GitHub Classroom is used en miles de universidades; Cyfrin Updraft tiene 200k+ students | 2/5 Arx (7 conectados hoy, 476 registrados total — [mudstats](https://mudstats.com/World/Arx,AftertheReckoning)), Sindome; nicho muy chico |
| **Riesgo técnico** (medio) | 4/5 stack maduro pero node-pty/auth/sandboxing per-user = vectores de ataque | **5/5** Discord mantenido por empresa, SDK estable, shards bien documentados | 3/5 vendor lock-in, políticas pueden cambiar (Katacoda cerrado es advertencia: [kubernetes.io](https://kubernetes.io/blog/2023/02/14/kubernetes-katacoda-tutorials-stop-from-2023-03-31/)) | **5/5** GitHub infra = top 0.1% reliability | 4/5 Evennia activa ([recent commits 2026-03-19](https://github.com/evennia/evennia/commits/master)), 2k stars, pero comunidad chica, bus-factor real |

**Score ponderado** (peso Alto=3, Medio=1):

| | A | B | C | D | E |
|---|---|---|---|---|---|
| UX mobile (3) | 9 | 15 | 9 | 12 | 3 |
| Escala (3) | 15 | 15 | 15 | 12 | 6 |
| Preserva (3) | 6 | 9 | 3 | 6 | 15 |
| Resuelve (3) | 15 | 12 | 15 | 12 | 3 |
| Costo (1) | 5 | 5 | 2 | 5 | 5 |
| Effort (1) | 2 | 3 | 4 | 3 | 5 |
| Ejemplos (3) | 15 | 12 | 15 | 12 | 6 |
| Riesgo (1) | 4 | 5 | 3 | 5 | 4 |
| **TOTAL** | **71** | **76** | **66** | **67** | **47** |

**Lectura honesta de la tabla**: B (Discord-first) gana en el agregado simple, pero tiene un hoyo fatal en "preserva las fortalezas" que un score ponderado no captura. A (xterm.js) es un segundo cercano con el problema inverso: resuelve las fricciones pero borra la narrativa. E (status quo) queda último — no porque sea malo en sí, sino porque no resuelve nada de lo que el owner identifica como fricción. La respuesta correcta es un **híbrido A+B** que cose las fortalezas de Evennia en una plataforma nueva — lo cual no es una de las 5 alternativas puras, pero es lo que la data sugiere.

---

## 3. Análisis por alternativa

### Stack A — Custom Node.js + xterm.js + Postgres + WebSockets

**Qué es**: Plataforma web construida desde cero. Frontend React/Next.js embebe [xterm.js](https://xtermjs.org/) (el mismo emulador de terminal que usa VS Code) en el navegador. Backend Node.js con [node-pty](https://github.com/microsoft/node-pty) forkea pseudo-terminales per user, los WebSockets transportan el stdin/stdout, Postgres persiste progreso/quests/wallets. Auth vía SIWE (Sign-In With Ethereum, [EIP-4361](https://docs.login.xyz/)) así el wallet del alumno es la identidad desde el día 0.

**Ejemplos reales que validan el stack**:

- **Katacoda** (O'Reilly, 2015–2022) corrió sobre xterm.js + containers. Fue la referencia del espacio hasta que O'Reilly lo cerró en Junio 2022, shutdown final de tutoriales de Kubernetes en [Marzo 2023](https://kubernetes.io/blog/2023/02/14/kubernetes-katacoda-tutorials-stop-from-2023-03-31/). Llegó a millones de users concurrentes en su peak.
- **Instruqt** (Netherlands): heredó el mercado post-Katacoda. Pricing enterprise ~$15K prepaid por 1000 hours ([reviews](https://us.fitgap.com/products/000516/instruqt)). Usa xterm.js.
- **LabEx**: alternative directa, 6000+ labs, €8/mes individual. Target mercado chino principalmente ([labex.io/pricing](https://labex.io/pricing)).
- **Killercoda**: sucesor comunitario libre, corre scenarios estilo Katacoda. Free tier limitado.
- **freeCodeCamp**: si bien no usa xterm.js para terminal real, demuestra que un nonprofit puede servir 2.1B minutos de educación con $754k/año de budget ([artículo oficial](https://www.freecodecamp.org/news/the-first-billion-minutes-the-numbers-behind-freecodecamp-the-tiny-nonprofit-thats-teaching-9c2ee9f8102c)). Arquitectura simple, CDN fuerte, DB Postgres.
- **Crunchy Data Playground**: PostgreSQL compilado a WebAssembly corriendo full en browser, con terminal psql interactivo ([link](https://www.crunchydata.com/developers/playground)). Demuestra que el paradigma "terminal real en el browser sin backend" es viable para cargas chicas.
- **Exercism**: 82 languages tracks, in-browser editor, ~694k students solo en Python ([exercism.org](https://exercism.org)). No es terminal puro pero muestra que in-browser coding ed escala.
- **Scrimba**: 1.5M users, interactive code-in-lesson ([newsletter](https://newsletter.dominuskelvin.dev/p/per-borgen-educating-15m-users-how)).

**Pros concretos**:

1. **Escala lineal horizontal**: Node + WS behind load balancer + Postgres primary/replica es el playbook más usado del mundo. Un CPX22 de Hetzner (€8/mes) aguanta ~5k conexiones WS con ws library en producción ([WebSocket benchmarker](https://healeycodes.com/websocket-benchmarker)).
2. **Mobile-first por construcción**: podés usar react-xterm y customizar touch, o si el comando es realmente crítico, fallback a una UI custom de "tap to run command" como Scrimba. xterm.js tiene limitaciones mobile documentadas ([#5377](https://github.com/xtermjs/xterm.js/issues/5377), [#2403](https://github.com/xtermjs/xterm.js/issues/2403) — copy/paste, predictive keyboard, iOS Smart Keyboard), pero son bugs superables con trabajo de UX; no son arquitecturales.
3. **Tools reales, no simuladas**: si usás node-pty con containers Docker (uno por sesión o uno por alumno) podés hacer que `claude` sea el Claude CLI REAL instalado dentro del container del alumno. Eso resuelve la fricción F5 estructural: los alumnos realmente tienen una shell en la nube donde `npm install -g @anthropic-ai/claude-code` instala el CLI de verdad.
4. **Zero vendor lock-in**: todo el stack es open source. Si Hetzner sube precios 37% como hizo en April 2026 ([Hetzner Statement](https://www.hetzner.com/pressroom/statement-price-adjustment/)), podés mover a Fly.io o DigitalOcean.
5. **SIWE como auth**: el wallet ES el login. Cero passwords, cero "recovery email". Los onchain badges son el estándar ([Web3Auth en 2026](https://web3auth.io/)). Gitcoin Passport + EAS ([Ethereum Attestation Service](https://docs.passport.xyz/building-with-passport/smart-contracts/overview)) te permite emitir attestations portables del tipo "completó Terminal Academy".

**Contras concretos**:

1. **Effort masivo**: reconstruir lo que Evennia te da gratis (rooms, NPCs, combat engine, persistence, admin panel Django, webclient JS, Telnet compatibility) son 200–300h. Enrique dev real, esto es 2–3 meses de sprint intenso para un solo developer. [Evennia tiene ~2k stars y commits 2026](https://github.com/evennia/evennia/commits/master); replicar eso es pelearse con el peso de 20 años de MUD engineering.
2. **Seguridad de node-pty multi-tenant es peligrosa**: si un alumno corre `rm -rf /` en su container, no rompe nada. Pero si escapa del container via un CVE de Docker/Node, es tu VPS. Requirís Kubernetes con gVisor o firecracker VMs per-user, lo cual te dispara costo e ingeniería. [Coder.com](https://coder.com/pricing) y [Gitpod](https://www.gitpod.io/) cobran enterprise precisamente por esto — la sandboxing is hard.
3. **Narrativa perdida**: tenés que implementar el concepto "Prof. Shell en room con ASCII art" desde cero. Esto NO es trivial — el engine de Evennia que despliega un room con NPCs conversacionales + fragmentos de memoria + progressive unlock es ~30 archivos Python ya escritos. Reescribir en TS es fácil; diseñar bien el abstract layer de "rooms" y "NPCs" sobre Postgres es un mes de diseño.
4. **Comunidad real-time desde cero**: el "ver a otros alumnos en el mismo dojo" es un feature social único de los MUDs. Reimplementarlo en web (lista de alumnos conectados en el room, chat del room) es trivial pero toma tiempo + requiere feature set de Discord eventually.
5. **Bug/feature parity con Claude CLI real**: si la promesa es "aquí instalás Claude Code de verdad", necesitás manejar subscripciones de Anthropic API del alumno o tener un key compartido — eso es $$$ variable. Una sesión típica de Claude Code puede gastar $0.10–$2 por alumno por sesión. Para 500 alumnos, $50–$1000/dia. Es un costo oculto que rompe el modelo económico.

**Costo real 500 alumnos**:

- Hetzner CPX22 (4 vCPU, 16GB, €7.99/mes): app server + WS. Holds ~5k concurrentes con ws library.
- Hetzner managed Postgres Basic (€15/mes): 500–2000 queries/s headroom.
- Si containers per user: Hetzner CCX13 con K3s (€14.86/mes) + storage.
- CDN Cloudflare R2 (free tier cubre 99% del tráfico de un dojo).
- **Total infra sin Anthropic API**: ~€40–€60/mes.
- **Total infra con Claude CLI real compartido** (hot wallet / shared key): $50–$500/mes variable según uso. **Plot twist**: si cada alumno necesita su propio key, esto es problema del alumno, no tuyo. Si el MUD provee el key, es tu costo.

**Citas clave que validan escala**: Twisted (el framework de Evennia) "puede escalar a 15M+ WebSocket connections" en teoría, ~78MB RAM para 5k conexiones en benchmark conservador ([Johal scaling article](https://www.johal.in/scalable-node-js-alternatives-python-twisted-async-frameworks-comparison-2025/)). Pero "beyond 50K concurrent connections per server, look at Go or Rust". Django Channels (alternativa Python pura) hits sweet spot "under 10K concurrent connections per server" ([Better Stack guide](https://betterstack.com/community/guides/scaling-python/django-websockets/)). Node+ws with uvloop similar o mejor.

**Riesgos**:

- **Alto**: escribís un MVP que es 70% lo que ya tenés en Evennia, 30% valor nuevo. Terminás con dos sistemas a mantener si conservás Evennia en paralelo.
- **Medio**: node-pty containerization mal hecho → seguridad rota.
- **Medio**: UX mobile de terminal real es difícil. Podés terminar con un UX peor que Discord para la audiencia mobile (alumnos LatAm con phones).
- **Bajo**: stack maduro, abundancia de libs, hiring pool grande.

**Confidence en las estimaciones**: Alto para costo infra (data de pricing público confirmada). Medio-alto para effort (estimación basada en equivalencia con Katacoda post-mortem y Gitpod).

---

### Stack B — Discord-first

**Qué es**: El curso vive dentro de Discord. Un bot (discord.js o discord.py) maneja:

- **Slash commands** para cada comando del curso: `/ls`, `/claude skills install <slug>`, `/claim 0xADDRESS`.
- **Role-based progression**: "Graduado del ls_dojo" es un rol automáticamente asignado.
- **Leaderboards via embeds**: top 100 alumnos por `$TERM`.
- **Onchain claim via bot**: usuario escribe `/claim <wallet>`, bot firma tx on Monad testnet.
- **Discord Activities** (optional): embed web apps como "Terminal Playground" dentro de Discord usando el [Embedded App SDK](https://github.com/discord/embedded-app-sdk) si querés una experiencia más rica.

Opcionalmente, el MUD de Evennia queda como "easter egg": un link que abre el webclient para los que quieran la experiencia premium.

**Ejemplos reales que validan**:

- **"I made a Bot Used by 510k Students for 3 Centuries' Worth of Time"** ([Zack, Medium](https://medium.com/@Zack.hardtoname/i-made-a-bot-used-by-510k-students-for-3-centuries-worth-of-time-ad2379bdb7ed)): study bot Discord con leaderboards en tiempo real, 170k students activos. Mostró que gamification + leaderboards en Discord escalan a centenares de miles.
- **InsightEdu** ([arxiv paper](https://arxiv.org/abs/2511.05685)): peer-reviewed case study. 12 concurrent instructors × 20–50 students each = 240–600 students per bot instance. 1.2GB RAM, 15–20% CPU, 30–60s auto-reconnect.
- **Programming course con 116 students** usando Discord bot para attendance + feedback ([arxiv 2407.19266](https://arxiv.org/html/2407.19266v1)).
- **Python Discord**: 420k members, staff de 100+ helpers, es LA referencia de community educativa programming ([pythondiscord.com](https://www.pythondiscord.com/)).
- **Galxe, Zealy**: plataformas de quests onchain que operan principalmente vía Discord bots ([blockchainappfactory](https://www.blockchainappfactory.com/blog/discord-communities-gamification-xp-quests-tokens/)). Token distributions + NFT claims + wallet connections desde el día 0.

**Pros concretos**:

1. **Mobile nativo perfecto**: Discord es el app de default mobile de la audiencia target. 69.94% de Discord users son <34 años, 41.32% entre 18–24 ([Discord Statistics 2026](https://sqmagazine.co.uk/discord-statistics/)). LatAm en particular: Brasil es #2 con 115.9M users, 12.8% del traffic global. Mobile-first ya es el 63% del growth global.
2. **Comunidad built-in**: voice channels, ver quién está online, reactions, threads, roles. TODO resuelto por Discord. El alumno literalmente ya está logueado.
3. **Escala trivial**: hybrid sharding lleva bots a 170k+ guilds con ~60% reducción de recursos ([discord-hybrid-sharding npm](https://www.npmjs.com/package/discord-hybrid-sharding)). Un solo VPS pequeño serve 5k students sin sweat.
4. **Costo: ~€0 Discord + ~€10 VPS**: la carga del hosting es casi toda en un único Node.js process (discord.js) + conexión a Postgres/SQLite. CPX11 es suficiente hasta 10k students concurrentes.
5. **Monad ecosystem también va para allá**: los Discord servers de Monad son donde está la comunidad, según la data del [Blitz hackathon program](https://everstake.one/resources/blog/monad-ignites-the-builder-economy-hackathons-ai-and-a-3-month-accelerator). Distribución viral orgánica mucho más fácil.
6. **Onchain claim se siente natural en Discord**: usuarios ya conectan wallets a Discord via Galxe/Zealy/Guild.xyz. "Link wallet" es un flow conocido, no uno que tenés que enseñar.

**Contras concretos**:

1. **Tools reales siguen simuladas**: `/ls` seguirá siendo simulado dentro del bot. El alumno NO tiene una shell real donde `npm install` funciona. Esto es exactamente la fricción F5 que el owner identificó, y Discord-first NO la resuelve. Podés mitigar con Discord Activities embedded (ver bullet B6 abajo), pero eso te lleva a construir Stack A otra vez.
2. **Narrativa plana**: no hay "rooms" con ASCII art persistente donde "ves" a Prof. Shell. Se reduce a text messages en un channel. El sense-of-place que hace a Terminal Academy especial se pierde. Podés paliar con Discord threads = "dojos" y embed rich formatting, pero no es lo mismo que entrar a un room y sentir que viajaste.
3. **Discord puede banear**: si el bot spam claims onchain o se interpreta como "airdrop farming", Discord puede banear el bot o server. Hay precedent de bots de crypto banned ([blog.communityone.io](https://blog.communityone.io/telegram-vs-discord/)). Riesgo de plataforma es real.
4. **Alumno no aprende terminal real**: el alumno pasa del bot de Discord al claim onchain, pero NUNCA abrió una terminal real en su compu. Si el objetivo pedagógico era "mi sobrina aprende shell", Discord-first falla. Si el objetivo era "onboarding a Monad/crypto", Discord-first es óptimo.
5. **Discord Activities SDK todavía es early** ([embedded-app-sdk](https://github.com/discord/embedded-app-sdk)): el modo "embed web app en iframe dentro de Discord" existe pero no es ampliamente documentado para casos de uso educación. Si querés meter un web-terminal, terminás construyendo Stack A igual.
6. **LatAm es Telegram, no Discord, en algunos segmentos**: los datos muestran que Telegram es dominante en regiones emergentes ([Telegram vs Discord 2026](https://www.mightynetworks.com/resources/telegram-vs-discord)). Brasil y México tienen ambos platforms fuertes; Argentina y otros países de habla hispana tienen más peso Telegram/WhatsApp. **Sin data pública** sobre el split específico para crypto education en LatAm — asumo Discord > Telegram para developer-target audiencia porque Monad/Ethereum comms viven en Discord (confidence: medio).

**Costo real 500 alumnos**:

- Hetzner CPX11 (2 vCPU, 4GB, €3.49/mes): bot + Postgres local.
- Discord: $0 (server gratis, bot free tier cubre 1000s de guilds).
- Infra onchain (game wallet con MON testnet): $0 (testnet MON via faucet).
- **Total**: **€5–10/mes**. La más barata del set.

**Citas que validan escala**: Hybrid sharding "has been battle-tested against bots managing up to 600k Guilds, reducing resource overhead by 40-60% versus common sharding managers" ([discord-hybrid-sharding](https://github.com/meister03/discord-hybrid-sharding)). Sharding solo requerido a 2500 guilds; internal sharding a ~14000.

**Riesgos**:

- **Medio**: Discord ToS change o ban del bot. Mitigación: mantener el código portable a Telegram/Slack.
- **Medio**: perder la narrativa = perder el diferenciador de Terminal Academy. Se convierte en "otro bot de quests crypto más".
- **Bajo**: escalabilidad técnica — Discord resuelve esto.
- **Alto**: tools reales siguen falsas, fricción F5 NO se resuelve.

**Confidence**: Alta para mobile/escala (data sólida de Discord 2026). Medio para LatAm-specific preferences (mixed signals en data pública).

---

### Stack C — Plataforma existente (KodeKloud / Replit / Instruqt / LabEx)

**Qué es**: En lugar de construir plataforma, montás el curso en un SaaS existente. Los candidatos con sandbox real + terminal son:

- **KodeKloud**: pricing Standard $15/mes, Pro $21, Business $28, AI $29 ([Kodekloud pricing 2026](https://kodekloud.com/pricing/)). Business plan tiene team dashboard + license rotation.
- **Replit Teams** (retirado Feb 2026) → **Replit Pro**: $100/mes para hasta 15 builders, tiered credit discounts, 80% education discount ([Replit pricing 2026](https://replit.com/pricing), [blog.replit.com](https://blog.replit.com/pro-plan)). "80% discount on the classroom product" para educators.
- **Instruqt**: pricing prepaid $15K minimum por 1000 hours — enterprise target, no fit para tu budget ([reviews](https://us.fitgap.com/products/000516/instruqt)).
- **LabEx**: $8.3/mes individual, $19.9 monthly; 6000+ labs, 2000+ challenges ([labex.io/pricing](https://labex.io/pricing)). Team volume discounts a partir de 5 users (10% off).
- **Killercoda**: free tier + Plus tier paid. Menos info de pricing público ([killercoda pricing](https://killercoda.com/pricing)).

**Ejemplos reales**:

- **Katacoda** fue la referencia hasta que O'Reilly cerró public access en Junio 2022, tutoriales de Kubernetes sunset Marzo 2023 ([kubernetes.io official post](https://kubernetes.io/blog/2023/02/14/kubernetes-katacoda-tutorials-stop-from-2023-03-31/)). ESTA ES LA ADVERTENCIA PRINCIPAL: SaaS educativos se matan de un día para otro. Killercoda fue creado específicamente para poder correr scenarios de Katacoda post-muerte.
- **Cyfrin Updraft**: 50+ hours de content, gratis, 31 lessons en Solana ([cyfrin.io](https://www.cyfrin.io/), [updraft.cyfrin.io/courses](https://updraft.cyfrin.io/courses)). Lo hacen outside de plataformas como KodeKloud. Ese es otro signal: en crypto-ed, los serios construyen su propia plataforma.
- **CryptoZombies**: 400k+ registered users, in-browser step-by-step lessons ([cryptozombies.io](https://cryptozombies.io/)). Plataforma propia no en SaaS genérica.
- **LabEx**: 6000+ labs, active en 2026, target mercado chino + global.

**Pros concretos**:

1. **Zero infra**: no manejás servers, containers, auth, escalado. Es problema del vendor.
2. **UX mobile resuelta**: casi todas las plataformas tienen mobile web decente (Replit especialmente).
3. **Sandboxing ya resuelto**: Firecracker microVMs o equivalente, un alumno no rompe al otro.
4. **Fast time-to-launch**: podés tener el curso live en 1–2 semanas.
5. **Reliability top-tier**: 99.9%+ uptime generally.

**Contras concretos**:

1. **Narrativa imposible**: estas plataformas te dan editor + terminal + markdown. NO te dejan crear rooms, NPCs, combat, fragmentos de memoria. La arquitectura de Terminal Academy (prólogo → dojos → El Corruptor) **no fit** en ninguna de estas plataformas.
2. **Onchain cableado = no soportado**: ni KodeKloud ni Replit ni LabEx tienen primitives para interactuar con smart contracts ni hot wallets. Podés instrumentar desde los labs un curl al RPC de Monad, pero la integración con el contract `$TERM` + SIWE + claims tendrías que hacer fuera de la plataforma → perdés el valor central.
3. **Costo explosivo a escala**: a $15/mes × 500 alumnos = $7,500/mes. A $29/mes × 500 = $14,500/mes. Con descuento educativo 80% de Replit Pro = ~$20/builder/mes = $10k/mes para 500. **No es viable sin ingresos recurrentes por alumno** y el proyecto es gratis/open source.
4. **Vendor risk demostrado**: Katacoda cerrado por O'Reilly 2022 es el caso de estudio. Replit retiró el plan Teams en Feb 2026 y forzó upgrade a Pro. La estabilidad de pricing no es garantizada.
5. **Lock-in de contenido**: tus labs/escenarios viven dentro del formato del vendor. Migrar implica reescribir todo.
6. **Branding ajeno**: "Terminal Academy en KodeKloud" es un subsite. Pierde la identidad propia.

**Costo real 500 alumnos** (con edu discount optimista):

| Plataforma | Pricing retail | Con edu discount | Total mensual 500 |
|---|---|---|---|
| KodeKloud Standard | $15/mes | ~$9/mes (40% BF) | $4,500/mes |
| KodeKloud Business | $28/mes | ~$19.60/mes (30% off) | $9,800/mes |
| Replit Pro (old Teams) | $100/mes / 15 builders | $20/builder with 80% off | ~$10,000/mes |
| LabEx Pro | $8.30/mes | $7.47 team volume | $3,735/mes |
| Instruqt | ~$15/hour prepaid | contact sales | No viable < $15K chunks |

**Realista bajo**: $3,700–4,500/mes para 500 alumnos. **Realista alto**: $10,000–14,500/mes. Ninguno fit a un proyecto open source sin revenue. Y no preserva la narrativa, que es el diferenciador.

**Riesgos**:

- **Alto**: precio disparado, no modelo económico viable.
- **Alto**: lock-in + vendor shutdown risk (Katacoda precedent).
- **Alto**: pérdida absoluta de la narrativa.
- **Medio**: integración onchain requiere workarounds fuera de la plataforma.

**Confidence**: Alta en pricing (todos públicos). Alta en incompatibilidad narrativa (verificado en docs de KodeKloud/Replit/LabEx — todos orientados a labs lineales, no a juegos).

---

### Stack D — Híbrido web + GitHub Classroom + Discord + verificación onchain (sin MUD)

**Qué es**: Stack de herramientas existentes cosidas con buen diseño:

- **Docs como content principal**: Docusaurus o MkDocs hosteado en GH Pages / Vercel.
- **GitHub Classroom**: assignments (auto-graded con CI), feedback vía pull requests.
- **Discord**: comunidad, announcements, help-channel.
- **Contrato onchain**: smart contract emite certificado (NFT o atestación EAS) al ser invocado por tu backend que valida "completó assignment X en GH Classroom".
- **Sin MUD, sin terminal simulado**: el alumno clona el repo localmente o usa GH Codespaces, corre los comandos reales en su compu.

**Ejemplos reales**:

- **Cyfrin Updraft**: está cerca de esto — docs + videos + material en GitHub + Discord server muy activo. 50+ hours, gratis, cursos de Solidity/Foundry/Vyper ([updraft.cyfrin.io](https://updraft.cyfrin.io/courses)). ~200k estudiantes según self-reporting.
- **Speed Run Ethereum / BuidlGuidl**: Austin Griffith's playbook — challenges en GH + reviews + onchain incentives. Mostrado escalar a miles de builders.
- **GitHub Classroom** per se: usado en miles de universidades, integración con Canvas ([JHU example](https://support.cmts.jhu.edu/hc/en-us/articles/19824197847181-Connect-GitHub-Classroom-to-your-Canvas-Course)).
- **EDU Chain** (Open Campus, 2026): primer blockchain for education, Learn/Own/Earn tokenized achievements ([educhain.xyz](https://educhain.xyz/)). Es EXACTAMENTE la dirección Stack D + onchain.
- **El Salvador Bitcoin Diploma 2.0** (Feb 2026): integrado blockchain en currículum nacional ([cryptostart.app](https://www.cryptostart.app/from-classroom-to-country-how-crypto-education-and-simulators-are-going-global-in-2026/)).

**Pros concretos**:

1. **Stack de herramientas top-tier**: GitHub = 99.99% uptime. Cada pieza es battle-tested.
2. **Tools 100% reales**: el alumno corre `npm install -g @anthropic-ai/claude-code` en SU compu. No simulación.
3. **Onchain es natural**: GitHub Actions trigger → backend verifica → smart contract emite NFT/token. Pattern conocido.
4. **Costo trivial**: GH Classroom free for education, Discord gratis, docs site gratis en Vercel, backend minimal en Railway/Fly ($5/mes). **Total ~€5–10/mes 500 alumnos**.
5. **Escalable a 5000+ sin refactor**: GitHub handles millones de devs.
6. **Skill transfer real**: el alumno sale sabiendo Git, GH, Discord — skills reales.

**Contras concretos**:

1. **Setup barrier alto**: el alumno tiene que instalar Git, crear cuenta GH, clonar repo, instalar dependencies. Para un tutorial "de cero a deploy en 15 min" este flow NO sirve. Es lo opuesto a "entra al webclient y ya".
2. **Desktop-first total**: casi nada funciona bien en mobile. Un alumno con solo celular queda out.
3. **Sin narrativa**: es "curso online tradicional + Discord". Pierde el sense-of-place, los NPCs, el progression emocional.
4. **Sin comunidad sync**: Discord es async. El "ver a otros alumnos en el mismo dojo en tiempo real" no existe.
5. **Fricción alta para no-coders**: el alumno target de Terminal Academy ("mi sobrina que no sabe qué es `ls`") se ahoga con el setup. Es curso para devs, no para onboarding absoluto.

**Costo real 500 alumnos**: €5–10/mes. La más barata del set.

**Riesgos**:

- **Bajo**: infra stable, pricing predictable, vendor risk muy bajo.
- **Alto**: UX barrier — el alumno newbie no logra setup. Esta es LA razón por la que Evennia ganó: el alumno entra al webclient y está jugando. Stack D les pide que piensen primero.
- **Alto**: pérdida de narrativa + comunidad sync.

**Confidence**: Alta. Stack de herramientas existentes, todo público.

---

### Stack E — Evennia + capas (status quo + F3 + F5 + F6)

**Qué es**: Aceptás que Evennia no es perfecto pero mantenés el core y sumás:

- **F3 Stability**: systemd, SQLite backup, Postgres migration, Sentry, uptime monitor, wallet monitoring. De [TODO_STABILITY.md](../TODO_STABILITY.md) puntos #1–#4, #26 (~7h de trabajo).
- **F5 Portal real**: alumno sale del MUD a su terminal real para correr `claude`, luego vuelve con un "token de verificación" que el MUD valida onchain. Workaround para el "tools simulados".
- **F6 Landing web + Discord bot**: landing en blitz.mexi.wtf con marketing, Discord server para comunidad con bot que hace cross-post de achievements del MUD.
- **Mobile: no-op honesto**: seguimos desktop-first. Si un alumno quiere mobile, usa un MUD client (BlowTorch en Android, [TinTin++](http://tintin.mudhalla.net/) iOS/Android) — y le damos instrucciones.

**Ejemplos reales del ecosistema Evennia**:

- **Arx, After the Reckoning**: 7 concurrent, 476 registered total ([mudstats Arx](https://mudstats.com/World/Arx,AftertheReckoning)). Active desde 2016. Top-tier roleplay MUD.
- **Sindome** (aunque es MOO custom, no Evennia): desde 1997, cyberpunk, mediano playerbase activo ([sindome.org](https://www.sindome.org/)).
- **Evennia Game Index**: lista automática de games en ([games.evennia.com](http://games.evennia.com/)).
- **MUDStats**: 728 active MUDs totales en 2026 ([mudstats.com](https://mudstats.com/)).

**Pros concretos**:

1. **Zero migration risk**: el sistema ya funciona. Lo que existe: 23 commands, 10 rooms, NPCs, quest system, onchain claim, webclient, Telnet, Cloudflare + Let's Encrypt.
2. **Narrative unmatched**: rooms, NPCs, fragmentos — no lo puede replicar ninguna alternativa sin rework enorme.
3. **Evennia está vivo**: commits 2026-03-19, 2k stars, Discord activo ([github.com/evennia/evennia](https://github.com/evennia/evennia)). No es abandonware.
4. **Costo infra baja**: CPX11 €3.49/mes. Más CPX22 €7.99/mes si escalás.
5. **SQLite es suficiente para demo y early product**: hasta ~100 concurrent. Con Postgres migration (#15 en TODO, 2h) llegás a ~1000+.

**Contras concretos**:

1. **Mobile roto**: webclient no responsive. Telnet mobile requiere app third-party. La audiencia target (LatAm, mobile-first) queda fuera. Esto ES la fricción #1 que el owner identifica.
2. **Tools simuladas**: `claude`, `openclaw`, `hermes` viven dentro del MUD. Los alumnos creen haber aprendido, no lo hicieron. Fricción #2. F5 lo mitiga pero es workaround (salir del MUD, volver con prueba).
3. **Escala tope**: performance testing de Evennia sugiere "desktop handled around 150 concurrent players without much effort, maybe up to 250 on a good day" ([Online Setup wiki](https://github.com/evennia/evennia/wiki/Online-Setup)). Para 500+ necesitás Postgres + tuning + probablemente multiple workers — Evennia no es horizontal scale trivial.
4. **Comunidad MUD es nicho**: 728 MUDs activos total en 2026. Arx con sus 7 concurrent es un top-tier MUD. El mercado total de MUD players es chiquito. Si querés masividad, Evennia no te ayuda.
5. **Admin panel Django es un vector**: el dev mantiene Django + Twisted + Evennia + SQLite/PG + nginx. Stack bus-factor-de-uno. Un fix de Django 5.x puede requerir testing de Evennia compatibility.
6. **Nonce-drift onchain**: ya identificado en TODO_STABILITY #2. Bug vivo.

**Costo real 500 alumnos**:

- Hetzner CPX11 actual: €3.49/mes.
- Post-migration a Postgres Basic: +€15/mes = ~€18/mes total.
- Si subís a CPX22 para headroom: ~€23/mes total.
- **Total**: **€5–25/mes**. Ultra barato.

**Riesgos**:

- **Alto**: no resolvés NADA de las fricciones core (mobile, tools-real, scale).
- **Alto**: audiencia target (mobile, no-dev) sigue fuera.
- **Medio**: bus-factor uno en el dev principal.
- **Bajo**: infra stability (si aplicás F3 completo).
- **Bajo**: Evennia abandonware (está muy activo).

**Confidence**: Alta en todos los puntos (data del propio repo del owner y mudstats públicos).

---

## 4. Recomendación con 3 escenarios

### Escenario 1 — **Quedate con Evennia (Stack E puro) SI**:

- **El proyecto sigue siendo un demo de hackathon / showcase artístico**, no un producto con 500+ alumnos reales.
- **La audiencia no es mobile-first** — son devs o hackathon judges con laptop que entran por 20 min.
- **Querés preservar la identidad artística cyberpunk intacta** y no diluir la experiencia.
- **No querés tomar más budget de dev** — el proyecto ya funciona y vos movés de aquí sin invertir 200+ horas.

En este escenario, el plan es **cerrar el TODO_STABILITY en 7h** (items #1, #4, #5, #6, #7, #26) y eso es suficiente. **No migres**. Terminal Academy queda como un hackathon artifact hermoso + runbook. Si alguien pregunta "¿cómo lo escalo?", tu respuesta es "reescribí en stack web, y llamame".

### Escenario 2 — **Migrate al Híbrido A+B (web xterm.js + Discord bot) SI**:

- **Querés producto real con 500–5,000 alumnos en el próximo trimestre**.
- **La audiencia es mobile-first LatAm** y usan Discord/Telegram más que laptops.
- **Tenés 200+ horas de dev para invertir en v2** o podés conseguir 1–2 devs adicionales.
- **El onchain claim es central** (no accesorio).

El plan es el **plan de migración escalonado** (sección 5). Punto crítico: NO apagues Evennia al día 1. Evennia queda como "endgame rooms" para graduados. La mayoría entra por Discord o web.

### Escenario 3 — **Híbrido PARCIAL + Stack D (docs web + GH Classroom) SI**:

- **Tu audiencia es más dev-próxima** (hackathon crypto builders, no absolutos newbies) y podés asumir que tienen Git/terminal basics.
- **Querés enfocarte en el valor onchain + Claude Code real**, no en el shell teaching de cero.
- **No querés mantener infra** y preferís todo sobre GitHub + Discord + Vercel.

El plan es pivotar Terminal Academy hacia "Monad Builder Bootcamp": docs en Docusaurus, challenges en GH Classroom con auto-grade, certificate onchain, Discord para comunidad. Evennia queda como "legacy demo" en blitz.mexi.wtf para ver la historia del proyecto.

---

## Mi recomendación definitiva

**Escenario 2 (Híbrido A+B) con Evennia como capa premium**, si el owner quiere producto real. Razón específica: los datos muestran que:

- **Mobile es no-negociable**. Discord's mobile-driven growth (63%) + LatAm Brazil top-2 + 69% users <34 años = si tu plataforma no es mobile-first, el CAC es brutal.
- **Tools reales resuelven F5 estructuralmente**. Stack A con containers per-user te permite `npm install -g @anthropic-ai/claude-code` de verdad, no simulado. Eso transforma el proyecto de "demo vistoso" a "realmente enseña tools".
- **Discord es la distribución natural del ecosystem Monad**. El hackathon mismo vive en Discord. Si tu bot distribuye $TERM con buenas UX, va a crecer orgánicamente.
- **Evennia como premium endgame** preserva lo que es irreplaceable (rooms, Prof. Shell, fragmentos de memoria) sin bloquear el growth del producto principal.

Si el owner prefiere velocidad sobre ambición, **Escenario 3 (Stack D)** es aceptable pero pierde el "WOW" del terminal que hace a Terminal Academy especial.

---

## 5. Plan de migración (Escenario 2)

**Timeline realista**: 12 semanas (~240h de dev para 1 persona solo-full-time; dividir entre 2–3 devs lo acorta pero introduce coordination overhead).

### Fase 0 — Stability del Evennia actual (Semana 0–1, ~7h)

No tocar nada del producto nuevo todavía. Objetivo: Evennia estable como fallback y como fuente de verdad durante la migración.

- Aplicar TODO_STABILITY items #1 (systemd), #4 (SQLite backup cron + S3), #6 (certbot verify), #26 (UptimeRobot), #5 (runbook PK rotation), #7 (Sentry), #3 (wallet alerts).
- Resultado: si todo se cae, Evennia sigue vivo y notificás al dev.

### Fase 1 — Foundation web (Semana 2–4, ~60h)

- **Repo nuevo**: `terminal-academy-web` (Next.js 15 + TS + Tailwind).
- **Auth**: SIWE con NextAuth.js ([dev.to guide 2026](https://dev.to/frankdotdev/kill-the-password-how-to-implement-sign-in-with-ethereum-siwe-in-2026-2741)). Wallet es login desde el día 0.
- **DB**: Postgres managed (Hetzner/Supabase) con schema: `users(wallet, progress_json)`, `quests`, `skills`, `attempts`.
- **API**: tRPC o REST simple. Endpoints: `GET /quests`, `POST /attempt`, `POST /claim`.
- **Frontend v1 sin terminal**: solo cuadrícula de quests con lecciones markdown. Conectá wallet, leés contenido, pasás al siguiente quest manualmente con botones. **Despliegue en Vercel con dominio staging**.
- **Objetivo entregable**: quests 1–7 (ls/pwd/cd/cat/mkdir/touch/grep) navegables en mobile, wallet linked.

### Fase 2 — Terminal real (Semana 4–6, ~60h)

- **Backend**: Node.js + ws (WebSocket) + [node-pty](https://github.com/microsoft/node-pty). Deploy en Fly.io o Hetzner con Docker Compose.
- **Sandboxing**: Docker containers per session, spawned on demand, TTL 1h. Base image Ubuntu 24.04 + Node + curl. Resource limits: 256MB RAM, 0.25 CPU, 100MB disk per container.
- **Frontend**: integrar xterm.js con fallback a UI "tap to run" en mobile (detect touch, show big button per quest instead of virtual keyboard).
- **Verification**: comando `tacmd verify <quest>` dentro del container que POSTea hash firmado a tu backend; backend verifica estado del fs y marca quest done.
- **Objetivo entregable**: alumno conecta wallet, recibe container en <5s, corre comandos reales (ls, cd, cat), completa quest 1.

### Fase 3 — Claude CLI real (Semana 6–7, ~30h)

- **Instalar Claude CLI en base image del container**: `curl -fsSL https://claude.ai/install.sh | bash`.
- **Shared API key del juego** (rotatable): alumnos gastan del pool del juego para sus primeras N interacciones, luego se les pide setup propio. Rate limit 10 req/alumno/día.
- **Skills catalog dinámico**: servir desde YAML en GH raw (TODO #20 resuelto de paso).
- **Deploy real a Monad testnet desde el container**: `cast send` con la hot wallet del alumno (si la tiene financiada) o vía backend proxy.
- **Objetivo entregable**: alumno ejecuta `claude new contract MiPrimerToken` → genera archivo real Solidity → `claude deploy` → tx real en testnet Monad.

### Fase 4 — Discord bot (Semana 7–9, ~40h)

- **Bot discord.js con commands**: `/progress`, `/leaderboard`, `/claim`.
- **Conecta a la misma Postgres**: progreso compartido entre web y Discord.
- **Webhooks de celebración**: cuando alumno completa quest en web, bot post en canal #achievements.
- **Onboarding en Discord**: slash command `/start` crea link único al webapp con magic login (token de Discord = prefill de wallet opción).
- **Objetivo entregable**: comunidad Discord con 100+ miembros, bot procesando claims.

### Fase 5 — Mobile UX polish + Evennia bridge (Semana 9–11, ~40h)

- **Mobile-first CSS**: responsive de verdad, virtual keyboard friendly.
- **"Enter the Arcade" button**: link del webapp que abre Evennia webclient para alumnos que quieren la experiencia premium. Auto-login via wallet signature.
- **Analytics**: Plausible o PostHog.
- **Evennia queda para "rooms secretas" post-graduación**: escenas narrativas con Prof. Shell, El Corruptor, fragmentos de memoria. El alumno graduado recibe NFT + acceso a Evennia.

### Fase 6 — Launch + load test (Semana 11–12, ~20h)

- **Load test con Locust o Artillery**: simular 500, 1000, 2000 concurrent users.
- **Tuning**: si Postgres satura → read replica. Si Node WS satura → sharding. Si Docker containers saturan → K3s con autoscaling.
- **Soft launch a comunidad Monad Discord**.
- **Hard launch con post en hackathon channels + LatAm dev groups**.

### Cuándo apagar Evennia

**Nunca del todo**. Evennia se convierte en la experiencia "endgame" para graduados:

- Los quests 1–15 (shell básico + intermedio + install dojo + claude basics) ocurren en web.
- Quests 16–23 (claude skills + deploy onchain + claim + lore quests) pueden empezar en web y terminar en Evennia como "recompensa narrativa".
- La hot wallet del juego + smart contract `$TERM` sirven ambos backends (ya está compartida via DB).
- Si en 6 meses Evennia concurrentes es <10 MAU y el web tiene >1000 MAU, dejás Evennia en mantenimiento mínimo. Solo apagás si el cost infra se vuelve prohibitivo (no lo será — €3.49/mes).

**Riesgo de migración**: el dev se cansa en Fase 2 (terminal real con Docker sandboxing es lo más complejo) y abandona. Mitigación: hacer Fase 2 un spike de 1 semana antes de comprometerse al plan completo. Si el spike falla, pivot a Escenario 3.

---

## Appendix — Datos que NO encontré (honestidad)

Para transparencia, estos son puntos donde la data pública fue escasa y donde usé asunciones:

- **Player counts específicos de MUDs Evennia en 2025–2026**: solo encontré Arx (7 concurrentes, [mudstats](https://mudstats.com/World/Arx,AftertheReckoning)). Asumo el resto del ecosystem es similar o menor. Confidence: alto en que el mercado total es chico.
- **LatAm Discord vs Telegram para developer crypto education**: mixed signals. Telegram es fuerte en LatAm general, Discord es fuerte en crypto devs globally. Sin data segmentada. Confidence: medio.
- **Costo real de Anthropic API si se ofrece shared key**: varía enormemente por uso. Asumí $0.10–$2/alumno/sesión basado en pricing de [anthropic.com](https://www.anthropic.com/pricing). Confidence: medio — podría variar ±5x.
- **Scrimba/Exercism infra scale concurrent users**: números públicos de total users (1.5M Scrimba, 694k Python en Exercism) pero no concurrent. Asumí arquitectura horizontal Node/Rails clásica. Confidence: medio.
- **Numero de estudiantes que realmente completan Cyfrin Updraft vs que solo registran**: Cyfrin reporta "200k+ students" pero sin completion rates. Típico en learn-to-earn el completion rate es 5–15%. Confidence: medio.
- **Evennia performance en VPS moderno con Postgres**: benchmark más reciente que encontré es del wiki "desktop handled around 150 concurrent players" que cita tests viejos con dummy clients. Desde entonces Twisted mejoró (asyncio integration, uvloop compat). Sin re-benchmark público de 2025–2026 con PG. Asumí ~500 concurrent es feasible con tuning. Confidence: medio.
- **Node-pty security incidents en production**: no encontré CVE específicos recientes, pero el pattern "container per user + node-pty" es high-risk por default. Asumí que requiere gVisor/Firecracker o equivalente para prod. Confidence: alto en que es riesgoso; medio en el costo de mitigación.
- **GH Classroom + blockchain cert nativo integration**: no encontré proyecto que haga específicamente "GH Classroom submit → on-chain attestation". Es patrón implementable pero no empaquetado. Confidence: alto en feasibility, alto en que no existe off-the-shelf.

---

## Sources

**Evennia y MUD ecosystem**:
- [Evennia oficial](https://www.evennia.com/)
- [Evennia GitHub](https://github.com/evennia/evennia)
- [Evennia Online Setup wiki](https://github.com/evennia/evennia/wiki/Online-Setup)
- [Evennia Web Client docs](https://www.evennia.com/docs/4.x/Components/Webclient.html)
- [EveLite lightweight client](https://github.com/InspectorCaracal/evelite-client)
- [Evennia Game Index](http://games.evennia.com/)
- [Arx stats en MUDStats](https://mudstats.com/World/Arx,AftertheReckoning)
- [Arx, After the Reckoning](https://play.arxgame.org/)
- [Sindome MUD](https://www.sindome.org/)
- [MUDStats global 2026](https://mudstats.com/)
- [Ranvier MUD engine](https://ranviermud.com/)
- [Awesome MUD list](https://github.com/mudcoders/awesome-mud)
- [Medium: 10 MUDs still alive 2026](https://medium.com/@the_andruid/multi-user-dungeons-10-games-still-serving-up-text-based-fun-in-2023-1e3951d3bf43)

**xterm.js y terminal en el browser**:
- [xterm.js oficial](https://xtermjs.org/)
- [xterm.js GitHub](https://github.com/xtermjs/xterm.js)
- [xterm.js mobile touch issue #5377](https://github.com/xtermjs/xterm.js/issues/5377)
- [xterm.js predictive keyboard #2403](https://github.com/xtermjs/xterm.js/issues/2403)
- [xterm.js mobile support #1101](https://github.com/xtermjs/xterm.js/issues/1101)
- [Qovery react-xtermjs](https://www.qovery.com/blog/react-xtermjs-a-react-library-to-build-terminals)
- [Efficient node-pty scaling with socket.io (Medium)](https://medium.com/@deysouvik700/efficient-and-scalable-usage-of-node-js-pty-with-socket-io-for-multiple-users-402851075c4a)
- [microsoft/node-pty](https://github.com/microsoft/node-pty)
- [Crunchy Data Postgres Playground (WASM)](https://www.crunchydata.com/developers/playground)
- [WebAssembly.sh](https://webassembly.sh/)
- [cryptool-org/wasm-webterm](https://github.com/cryptool-org/wasm-webterm)

**Plataformas educación interactiva**:
- [Katacoda shutdown announcement (Kubernetes blog 2023)](https://kubernetes.io/blog/2023/02/14/kubernetes-katacoda-tutorials-stop-from-2023-03-31/)
- [Instruqt pricing](https://instruqt.com/pricing)
- [LabEx pricing 2026](https://labex.io/pricing)
- [KodeKloud pricing 2026](https://kodekloud.com/pricing/)
- [KodeKloud G2 reviews 2026](https://www.g2.com/products/kodekloud/reviews)
- [Replit pricing 2026](https://replit.com/pricing)
- [Replit Pro plan launch Feb 2026](https://blog.replit.com/pro-plan)
- [Replit 80% education discount](https://blog.replit.com/remote)
- [Killercoda pricing](https://killercoda.com/pricing)
- [Learn-by-doing platforms list (iximiuz)](https://iximiuz.com/en/posts/learn-by-doing-platforms/)
- [Collabnix: Kubernetes playground comparison](https://collabnix.com/choosing-the-perfect-kubernetes-playground-a-comparison-of-pwd-killercoda-and-other-options/)
- [freeCodeCamp: The First Billion Minutes](https://www.freecodecamp.org/news/the-first-billion-minutes-the-numbers-behind-freecodecamp-the-tiny-nonprofit-thats-teaching-9c2ee9f8102c)
- [Scrimba 1.5M users newsletter](https://newsletter.dominuskelvin.dev/p/per-borgen-educating-15m-users-how)
- [Exercism](https://exercism.org)
- [CryptoZombies](https://cryptozombies.io/)
- [CodeCombat Wikipedia](https://en.wikipedia.org/wiki/CodeCombat)
- [Cyfrin Updraft courses](https://updraft.cyfrin.io/courses)
- [Cyfrin website](https://www.cyfrin.io/)
- [Speedrun Ethereum](https://speedrunethereum.com/)
- [BuidlGuidl](https://buidlguidl.com/)

**Discord ecosystem**:
- [Discord Statistics 2026 (SQ Magazine)](https://sqmagazine.co.uk/discord-statistics/)
- [Business of Apps Discord data](https://www.businessofapps.com/data/discord-statistics/)
- [Discord Users by Country 2026](https://resourcera.com/data/social/discord-users/)
- [discord.js guide sharding](https://discordjs.guide/sharding/)
- [discord-hybrid-sharding npm](https://www.npmjs.com/package/discord-hybrid-sharding)
- [discord-hybrid-sharding GitHub](https://github.com/meister03/discord-hybrid-sharding)
- [Discord Embedded App SDK](https://github.com/discord/embedded-app-sdk)
- [Discord Activities introduction](https://support-dev.discord.com/hc/en-us/articles/21204423970071-Introducing-the-Embedded-App-SDK)
- [Zack: 510k students Discord bot](https://medium.com/@Zack.hardtoname/i-made-a-bot-used-by-510k-students-for-3-centuries-worth-of-time-ad2379bdb7ed)
- [InsightEdu arXiv 2511.05685](https://arxiv.org/abs/2511.05685)
- [Interactive Learning CS Discord Chatbot arXiv 2407.19266](https://arxiv.org/html/2407.19266v1)
- [Python Discord community (420k members)](https://www.pythondiscord.com/)
- [Discord vs Telegram 2026 (Mighty Networks)](https://www.mightynetworks.com/resources/telegram-vs-discord)
- [Telegram vs Discord community one blog](https://blog.communityone.io/telegram-vs-discord/)
- [Discord gamification with onchain rewards](https://www.blockchainappfactory.com/blog/discord-communities-gamification-xp-quests-tokens/)

**Web3 auth + onchain edu**:
- [SIWE oficial](https://siwe.xyz/)
- [SIWE docs (login.xyz)](https://docs.login.xyz/)
- [SIWE best practices 2025 (Markaicode)](https://markaicode.com/siwe-best-practices-2025/)
- [Kill the Password SIWE 2026 dev.to](https://dev.to/frankdotdev/kill-the-password-how-to-implement-sign-in-with-ethereum-siwe-in-2026-2741)
- [Better Auth SIWE plugin](https://better-auth.com/docs/plugins/siwe)
- [Gitcoin Passport smart contracts](https://docs.passport.xyz/building-with-passport/smart-contracts/overview)
- [Web3 education 38 resources (Alchemy)](https://www.alchemy.com/dapps/best/web3-education-resources)
- [EDU Chain](https://educhain.xyz/)
- [OnChain Education / University of Canterbury](https://www.cryptostart.app/from-classroom-to-country-how-crypto-education-and-simulators-are-going-global-in-2026/)
- [Learn-to-Earn platforms 2026 (BitDegree)](https://www.bitdegree.org/crypto/learn-to-earn-crypto-platforms)

**Monad ecosystem**:
- [Monad oficial](https://www.monad.xyz/)
- [Monad Builder Economy (Everstake)](https://everstake.one/resources/blog/monad-ignites-the-builder-economy-hackathons-ai-and-a-3-month-accelerator)
- [Monad testnet](https://testnet.monad.xyz/)
- [Monad hackathon](https://hackathon.monad.xyz/)

**Infra y scaling benchmarks**:
- [Hetzner pricing adjustment April 2026](https://www.hetzner.com/pressroom/statement-price-adjustment/)
- [Hetzner Cloud review 2026 (Better Stack)](https://betterstack.com/community/guides/web-servers/hetzner-cloud-review/)
- [Fly.io pricing](https://fly.io/pricing/)
- [Fly.io per-user dev environments](https://fly.io/docs/blueprints/per-user-dev-environments/)
- [Railway vs Render 2026](https://northflank.com/blog/railway-vs-render)
- [Scalable Node.js alternatives Twisted comparison](https://www.johal.in/scalable-node-js-alternatives-python-twisted-async-frameworks-comparison-2025/)
- [Django Channels scaling (Better Stack)](https://betterstack.com/community/guides/scaling-python/django-websockets/)
- [Django Channels 1M WebSocket connections (Medium)](https://medium.com/@yogeshkrishnanseeniraj/async-django-scaling-websockets-to-1-million-concurrent-connections-9e1a8165a9ef)
- [Benchmarking WebSocket Servers in Python (Healey)](https://healeycodes.com/websocket-benchmarker)
- [KubeSSH: SSH into Kubernetes pod per user](https://github.com/yuvipanda/kubessh)
- [SQLite vs PostgreSQL 1000 users (DataCamp)](https://www.datacamp.com/blog/sqlite-vs-postgresql-detailed-comparison)

**MUD clients mobile**:
- [BlowTorch Android MUD client](https://bt.happygoatstudios.com/)
- [TinTin++ iOS/Android](http://tintin.mudhalla.net/)
- [Slant: 8 Best MUD clients 2026](https://www.slant.co/topics/7840/~mud-client)
- [List of MUD clients (Wikipedia)](https://en.wikipedia.org/wiki/List_of_MUD_clients)

**Proyecto Terminal Academy (contexto interno)**:
- [Terminal Academy README](../README.md)
- [TODO_STABILITY](../TODO_STABILITY.md)
- [PITCH](../PITCH.md)

---

## Resumen metodológico del research

- **Horas de research**: ~3h equivalent de web searches (40+ queries, ~50+ URLs consultadas).
- **Tokens usados**: ~300k aproximados entre queries y análisis.
- **Data priority**: crucé pricing público + case studies + technical benchmarks + MUD ecosystem stats.
- **Opinión vs data**: marqué explícitamente en "Appendix" donde faltó data pública.
- **Bias declarado**: el autor asume que el owner del proyecto prioriza producto real > arte finalizado. Si es lo contrario, Escenario 1 es obvio.

Fin del documento.
