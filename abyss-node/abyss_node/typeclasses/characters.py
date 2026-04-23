"""
Characters - Players and NPCs with combat stats

Combat system for The Abyss MUD
"""

import random
import time
from evennia.objects.objects import DefaultCharacter
from evennia import create_object, search_object
from evennia.utils import delay

from .objects import ObjectParent


# Idle watcher — cada N segundos revisa si el jugador está inactivo y hay quests
# pendientes; si sí, Prof. Shell deja caer una pista sutil.
IDLE_INTERVAL = 45          # cadencia del ticker en segundos
IDLE_THRESHOLD = 45         # silencio mínimo antes de disparar un hint
IDLE_HINT_COOLDOWN = 45     # espaciado mínimo entre hints consecutivos


# Ejemplo de swap a i18n — demuestra el patrón. El resto del banner sigue
# hardcoded en ES hasta que otra sesión complete la migración; esta función
# sólo saca el título de TRANSLATIONS["banner.title"] según caller.
def render_academy_banner(caller=None):
    """Banner de bienvenida de la Academia.

    Si `caller` es None o no se puede resolver idioma, usa DEFAULT_LANG.
    Solo la LÍNEA DEL TÍTULO se traduce por ahora (prueba del plumbing).
    """
    try:
        from utils.i18n import t
        title = t(caller, "banner.title") if caller is not None else "M O N A D   T E R M I N A L   A C A D E M Y"
    except Exception:
        title = "M O N A D   T E R M I N A L   A C A D E M Y"
    return (
        "\n"
        "|g ╔══════════════════════════════════════════════════════════╗|n\n"
        f"|g ║|n    |y{title}|n             |g║|n\n"
        "|g ║|n    aprende la terminal · gana |y$TERM|n onchain en Monad       |g║|n\n"
        "|g ║|n    + |cClaude CLI|n para generar y deployar contratos          |g║|n\n"
        "|g ╚══════════════════════════════════════════════════════════╝|n\n"
    )


# Compat: algunos módulos pueden importar ACADEMY_BANNER como string. Mantener
# el símbolo con el render default (sin caller → ES) para no romper imports.
ACADEMY_BANNER = render_academy_banner()

ACADEMY_TUTORIAL = (
    "|wBienvenide a la Academia.|n Curso interactivo de terminal que paga\n"
    "|y$TERM|n (ERC-20 en Monad testnet) por cada quest completada.\n"
    "Escribe |ghelp|n para ver tu próxima quest o |wsay hola prof|n si te perdés.\n"
)

# (quests_completadas_threshold, key_en_achievements_shown, mensaje)
ACHIEVEMENTS = [
    (
        3,
        "shell_ninja",
        "\n|y★ ACHIEVEMENT DESBLOQUEADO ★|n  "
        "Te estás volviendo |gshell-ninja|n 🥷 (3 comandos dominados).\n"
        "Sigue así — escribe |whelp|n para ver qué sigue.\n",
    ),
    (
        5,
        "discord_flex",
        "\n|y★ ACHIEVEMENT DESBLOQUEADO ★|n  "
        "Ya puedes |gpresumir en Discord|n 🎙 (5 comandos). "
        "Cuéntaselo a los normies.\n",
    ),
    (
        10,
        "shell_plumber",
        "\n|y★ ACHIEVEMENT DESBLOQUEADO ★|n  "
        "|gShell-plomero certificado|n: pipes + redirects domados (10 comandos).\n"
        "Sigue a |cclaude_dojo|n cuando quieras meterte con IA + onchain.\n",
    ),
    (
        15,
        "hacker_in_training",
        "\n|y★ ACHIEVEMENT DESBLOQUEADO ★|n  "
        "|gHacker en formación|n — Claude te está enseñando a generar código (15 comandos).\n",
    ),
    (
        19,
        "academy_graduate",
        "\n|y★★★ GRADUACIÓN ★★★|n  "
        "|gGraduado de la Academia|n. "
        "Linkea wallet con |wlink 0x...|n y usa |wclaim|n para recibir tus $TERM onchain.\n",
    ),
]


class Character(ObjectParent, DefaultCharacter):
    """
    Character with combat stats and abilities.
    Used for both players and NPCs.
    """

    def at_object_creation(self):
        """Called when character is first created."""
        super().at_object_creation()
        # Base stats
        self.db.hp = 100
        self.db.max_hp = 100
        self.db.damage = 5
        self.db.armor = 0
        self.db.level = 1
        self.db.xp = 0
        self.db.xp_to_level = 100

        # Combat state
        self.db.in_combat = False
        self.db.combat_target = None

        # Currency
        self.db.abyss_coins = 10

        # Stats (cyberpunk style)
        self.db.stats = {
            "str": 10,  # Strength - melee damage
            "dex": 10,  # Dexterity - accuracy, dodge
            "con": 10,  # Constitution - HP
            "int": 10,  # Intelligence - hacking, tech
            "wis": 10,  # Wisdom - perception
            "cha": 10,  # Charisma - prices, dialogue
            "cyber": 0, # Cybernetic level
        }

        # Equipment slots
        self.db.equipped = {
            "weapon": None,
            "head": None,
            "eyes": None,
            "spine": None,
            "skin": None,
            "left_arm": None,
            "right_arm": None,
        }

        # Active buffs from consumables
        self.db.active_buffs = {}

    def at_post_puppet(self, **kwargs):
        """
        Se llama cada vez que una Account toma control del personaje.
        La primera vez mostramos el banner + tutorial (idempotente vía
        db.first_login_done) y después el prólogo narrativo del Acto I
        (idempotente vía db.seen_prologue). También celebramos el primer
        deploy onchain si no fue celebrado todavía (idempotente vía
        achievements_shown).
        """
        super().at_post_puppet(**kwargs)
        # NPCs con npc_type ya seteado no deben recibir onboarding.
        if getattr(self.db, "npc_type", None):
            return
        if not self.db.first_login_done:
            self.db.first_login_done = True
            # Usa el renderer con caller para que el título respete el idioma
            # del account (account.db.language). Ejemplo del swap i18n.
            self.msg(render_academy_banner(self))
            self.msg(ACADEMY_TUTORIAL)
        # Prólogo narrativo v2 — Acto I DESPERTAR. Independiente del banner:
        # un player puede tener first_login_done=True por un flujo anterior
        # y aún no haber visto el prólogo narrativo nuevo.
        self._play_prologue_once()
        # Celebrar el primer deploy una sola vez (independiente del banner
        # — un jugador puede deployar en sesión anterior y re-conectar).
        self._celebrate_first_deploy()
        # Onboarding (Sesión C) — iniciar idle-watcher y sembrar timestamp
        # de actividad para que Prof. Shell no hable al instante de loguearse.
        try:
            self.db.last_cmd_time = time.time()
            self._register_idle_watcher()
        except Exception:
            # Nunca romper el login por un bug del watcher.
            pass
        # Tracking de rooms visitadas (para desbloqueo progresivo de quests)
        try:
            self._record_visited_room()
        except Exception:
            pass

    def at_after_move(self, source_location, **kwargs):
        """Hook cuando el character entra a una room. Registra en visited_rooms
        para desbloquear las quests de ese room gradualmente."""
        try:
            super().at_after_move(source_location, **kwargs)
        except TypeError:
            super().at_after_move(source_location)
        if getattr(self.db, "npc_type", None):
            return
        try:
            self._record_visited_room()
        except Exception:
            pass

    def _record_visited_room(self):
        """Añade la room actual a caller.db.visited_rooms (idempotente)."""
        if not self.location:
            return
        key = getattr(self.location, "key", None)
        if not key:
            return
        visited = list(self.db.visited_rooms or [])
        if key not in visited:
            visited.append(key)
            self.db.visited_rooms = visited
            # Aviso narrativo al primer acceso a cada dojo (excepto home)
            if key != "home":
                try:
                    from utils.narrator import narrate
                    narrate(
                        self,
                        f"Has descubierto un lugar nuevo: |c/{key}|n. "
                        f"Las quests de esta sala ya aparecen en |wquests|n."
                    )
                except Exception:
                    pass

    def at_post_unpuppet(self, account=None, session=None, **kwargs):
        """Al desconectarse, apagamos el idle-watcher para liberar recursos."""
        try:
            super().at_post_unpuppet(account=account, session=session, **kwargs)
        except TypeError:
            # Compat con firmas más antiguas de Evennia.
            super().at_post_unpuppet()
        if getattr(self.db, "npc_type", None):
            return
        try:
            self._unregister_idle_watcher()
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Onboarding (Sesión C) — idle-watcher + hints sutiles de Prof. Shell
    # ------------------------------------------------------------------

    def _register_idle_watcher(self):
        """Registra un ticker que cada IDLE_INTERVAL llama a `_idle_hint`."""
        try:
            from evennia.scripts.tickerhandler import TICKER_HANDLER
        except Exception:
            return
        try:
            TICKER_HANDLER.add(
                interval=IDLE_INTERVAL,
                callback=self._idle_hint,
                idstring=f"ta_idle_{self.id}",
                persistent=False,
            )
        except Exception:
            pass

    def _unregister_idle_watcher(self):
        """Remueve el ticker idle del jugador."""
        try:
            from evennia.scripts.tickerhandler import TICKER_HANDLER
        except Exception:
            return
        try:
            TICKER_HANDLER.remove(
                interval=IDLE_INTERVAL,
                callback=self._idle_hint,
                idstring=f"ta_idle_{self.id}",
                persistent=False,
            )
        except Exception:
            pass

    def _idle_hint(self):
        """
        Si el jugador lleva >IDLE_THRESHOLD segundos sin ejecutar comando,
        y hay quests pendientes, Prof. Shell le suelta un hint narrativo.
        Espaciado por IDLE_HINT_COOLDOWN para no ser spam.
        """
        if getattr(self.db, "npc_type", None):
            return
        if not self.has_account:
            return
        loc = self.location
        if not loc:
            return

        now = time.time()
        last_cmd = float(self.db.last_cmd_time or 0.0)
        last_hint = float(self.db.last_idle_hint or 0.0)

        if last_cmd and (now - last_cmd) < IDLE_THRESHOLD:
            return
        if last_hint and (now - last_hint) < IDLE_HINT_COOLDOWN:
            return

        try:
            from commands.terminal_commands import QUESTS
        except Exception:
            QUESTS = []
        done = set(self.db.quest_done or [])
        pending_quests = [q for q in QUESTS if q["id"] not in done]

        try:
            from utils.narrator import dialogue as _dlg
        except Exception:
            def _dlg(caller, npc, text):
                caller.msg(f"» {npc}: {text}")

        if not pending_quests:
            # Endgame hints (linkear wallet / claim).
            wallet = self.db.wallet or ""
            pending = int(self.db.abyss_pending or 0)
            if pending > 0 and not wallet:
                _dlg(
                    self, "Prof. Shell",
                    f"Tienes |y{pending} $TERM|n pendientes. Conecta tu wallet "
                    "con |wlink 0x...|n (o mira |wtutorial wallet|n si dudas).",
                )
                self.db.last_idle_hint = now
            elif pending > 0 and wallet:
                _dlg(
                    self, "Prof. Shell",
                    f"Todo listo: ejecuta |wclaim|n para recibir "
                    f"|y{pending} $TERM|n.",
                )
                self.db.last_idle_hint = now
            return

        nxt = pending_quests[0]
        hint_txt = self._pick_idle_hint(nxt["cmd"], (loc.key or "").lower(), nxt)
        if not hint_txt:
            return
        _dlg(self, "Prof. Shell", hint_txt)
        self.db.last_idle_hint = now

        # Check achievements por si algo cruzó umbral sin notificar.
        try:
            from commands.achievements import check_achievements
            check_achievements(self)
        except Exception:
            pass

    def _pick_idle_hint(self, cmd: str, loc_key: str, quest: dict) -> str:
        """Devuelve el texto del hint según el próximo comando objetivo."""
        by_cmd = {
            "ls": "Si no sabes por dónde empezar, escribe |gls|n. Es el primer respiro.",
            "pwd": "Prueba |wpwd|n — te dice exactamente dónde estás.",
            "cd": "Mira las salidas con |wls|n y luego |wcd <nombre>|n para moverte.",
            "cat": "Hay archivos aquí esperando lectura. Prueba |wcat <archivo>|n.",
            "mkdir": "Crea un subdirectorio con |wmkdir experimentos|n para practicar.",
            "touch": "Un archivo vacío es potencial. |wtouch notas.txt|n y luego llénalo.",
            "grep": "Busca un patrón en el archivo del room: |wgrep TOKEN <archivo>|n.",
            "echo": "|wecho hola mundo|n imprime texto. Con |w> archivo|n lo escribe.",
            "whoami": "|wwhoami|n — cuando dudes de tu identidad, el sistema responde.",
            "head": "Lee el principio de un archivo con |whead -n 5 <archivo>|n.",
            "tail": "Lee el final con |wtail -n 5 <archivo>|n.",
            "wc": "|wwc <archivo>|n te da líneas, palabras y bytes.",
            "man": "Consulta el manual: |wman ls|n, |wman grep|n.",
            "history": "|whistory|n te muestra todo lo que has tecleado.",
            "claude": "En |cclaude_dojo|n escribe |wclaude|n para abrir el CLI de IA.",
            "claude:skill": "Instala el kit oficial: |wclaude skills install portdeveloper/monad-development|n.",
            "claude:new": "Genera un contrato: |wclaude new contract MiToken|n.",
            "claude:deploy": "Deploya a Monad: |wclaude deploy MiToken.sol|n.",
            "verify:claude": "Deployá con Claude REAL y vuelve: |wverify claude <tx-hash>|n.",
            "link": "Si ya tienes wallet, |wlink 0x...|n la conecta. Si no, |wtutorial wallet|n.",
            "node": "Verifica Node con |wnode --version|n.",
            "install:claude": "Instala Claude Code: |wcurl -fsSL https://claude.ai/install.sh | bash|n.",
            "install:openclaw": "Instala OpenClaw: |wcurl -fsSL https://openclaw.ai/install.sh | bash|n.",
            "install:hermes": "Instala Hermes: |wcurl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash|n.",
        }
        txt = by_cmd.get(cmd)
        if txt:
            return txt
        return f"Tu próximo reto: {quest.get('desc', '')}"

    def execute_cmd(self, raw_string, session=None, **kwargs):
        """
        Hook corrido en CADA comando tecleado por el jugador. Lo usamos para
        refrescar `last_cmd_time` — base del idle-watcher.
        """
        if not getattr(self.db, "npc_type", None):
            try:
                self.db.last_cmd_time = time.time()
            except Exception:
                pass
        return super().execute_cmd(raw_string, session=session, **kwargs)

    def _play_prologue_once(self):
        """Acto I DESPERTAR, idempotente vía db.seen_prologue."""
        if self.db.seen_prologue:
            return
        try:
            from world.lore.fragments import PROLOGUE
            self._play_script(PROLOGUE)
        except Exception:
            # Nunca romper el login por un bug narrativo.
            return
        self.db.seen_prologue = True
        try:
            self.save()
        except Exception:
            pass

    def _play_outro_once(self):
        """Acto III ASCENSIÓN, idempotente vía db.seen_outro.

        Se dispara cuando `quest_done` contiene las N ids de `QUESTS`.
        Llamar desde `_check_achievements` tras completar una quest.
        """
        if self.db.seen_outro:
            return
        try:
            from commands.terminal_commands import QUESTS
        except Exception:
            return
        done = set(self.db.quest_done or [])
        if len(done) < len(QUESTS):
            return
        try:
            from world.lore.fragments import OUTRO
            self._play_script(OUTRO)
        except Exception:
            return
        self.db.seen_outro = True
        try:
            self.save()
        except Exception:
            pass

    def _play_script(self, script):
        """Interpreta tuplas (kind, *args) contra utils.narrator helpers.

        Kinds soportados:
          ("scene", title, body)
          ("narrate", text)
          ("dialogue", npc_name, text)
        Cualquier otro kind (o excepción en un helper) se ignora sin romper
        la secuencia.
        """
        try:
            from utils.narrator import narrate, dialogue, scene
        except Exception:
            return
        for entry in script or []:
            if not entry:
                continue
            kind = entry[0]
            args = entry[1:]
            try:
                if kind == "scene" and args:
                    title = args[0]
                    body = args[1] if len(args) > 1 else ""
                    scene(self, title, body)
                elif kind == "narrate" and args:
                    narrate(self, args[0])
                elif kind == "dialogue" and len(args) >= 2:
                    dialogue(self, args[0], args[1])
            except Exception:
                continue

    def _celebrate_first_deploy(self):
        """Idempotente: muestra felicitación por el primer deploy simulado."""
        deployed = self.db.deployed_contracts or []
        if not deployed:
            return
        shown = list(self.db.achievements_shown or [])
        if "first_deploy" in shown:
            return
        last = deployed[-1] if isinstance(deployed[-1], dict) else {}
        addr = last.get("address", "?")
        tx = last.get("tx", "?")
        fname = last.get("file", "?")
        shown.append("first_deploy")
        self.db.achievements_shown = shown
        self.msg(
            "\n|g╭─ PRIMER DEPLOY ──────────────────────────────────╮|n\n"
            f"|g│|n  ¡Deployaste tu primer contrato: |w{fname}|n!\n"
            f"|g│|n  address: |y{addr}|n\n"
            f"|g│|n  tx:      |w{tx}|n\n"
            f"|g│|n  |x(simulado en esta demo — flujo real vía Foundry)|n\n"
            "|g╰──────────────────────────────────────────────────╯|n"
        )

    def msg(self, text=None, *args, **kwargs):
        """
        Override del msg default para engancharle el check de achievements
        y la |mdetección de fragmentos de memoria|n leídos. Solo aplica a
        players (NPCs no acumulan quests).
        """
        super().msg(text, *args, **kwargs)
        # Evitamos recursión cuando el propio achievement emite msg.
        if getattr(self, "_in_ach_check", False):
            return
        self._in_ach_check = True
        try:
            # Detectar fragmentos de memoria (cat de fragmento_XX.mem)
            self._detect_memory_fragment(text)
            self._check_achievements()
        except Exception:
            # Jamás romper el flujo de mensajes por un bug de achievements.
            pass
        finally:
            self._in_ach_check = False

    def _detect_memory_fragment(self, text):
        """
        Si el texto mostrado al player corresponde al output de
        `cat fragmento_XX.mem`, guarda el fragmento en `db.memories`
        y emite un `achievement()` narrativo. Idempotente: sólo la primera
        vez que se lee cada fragmento.

        El header de cat (ver commands/terminal_commands.py:291) es
        `|x────── {filename} ──────|n`. El regex exige los dashes Unicode
        alrededor para evitar falsos positivos cuando otro texto menciona
        el archivo (README, hints, descripciones de room).
        """
        if not text or not isinstance(text, str):
            return
        if "fragmento_" not in text or "──" not in text:
            return
        try:
            from world.lore.fragments import FRAGMENTS_BY_FILE, collect_fragment
            from utils.narrator import achievement
        except Exception:
            return
        import re
        # Header real de cat: "|x────── fragmento_XX.mem ──────|n"
        candidates = re.findall(r"──────\s+(fragmento_\d{2}\.mem)\s+──────", text)
        for fname in candidates:
            if fname not in FRAGMENTS_BY_FILE:
                continue
            frag = collect_fragment(self, fname)
            if not frag:
                continue
            # Emite achievement una sola vez (collect_fragment devuelve None
            # si ya estaba coleccionado).
            try:
                total = len(FRAGMENTS_BY_FILE)
                got = len(self.db.memories or [])
                body = (
                    f"{frag['body']}\n"
                    f"Memoria {got}/{total} recuperada."
                )
                achievement(self, frag["title"], body, reward=0)
            except Exception:
                pass
            break  # sólo un fragmento por mensaje

    def _check_achievements(self):
        """Muestra mensajes de achievement al cruzar hitos de quests.

        Además dispara el outro (Acto III ASCENSIÓN) al completar TODAS
        las quests, UNA sola vez, con guard `db.seen_outro`.
        """
        quest_done = self.db.quest_done
        if not quest_done:
            return
        # Outro Acto III — sólo dispara si acabamos de completar TODAS las
        # quests y aún no se mostró. Lo llamamos primero para que el player
        # vea la escena antes del resto de achievements ya mostrados.
        try:
            self._play_outro_once()
        except Exception:
            pass
        # Sesión C — achievements narrativos (Primer respiro, Memoria
        # despertando, Hacker novato, Maestro del shell, Neo del shell).
        # Son idempotentes por su propio guard interno.
        try:
            from commands.achievements import check_achievements as _narr_ach
            _narr_ach(self)
        except Exception:
            pass
        shown = list(self.db.achievements_shown or [])
        count = len(quest_done)
        new_shown = False
        for threshold, key, message in ACHIEVEMENTS:
            if count >= threshold and key not in shown:
                shown.append(key)
                new_shown = True
                # super().msg para evitar re-entrar en el check.
                super().msg(message)
        if new_shown:
            self.db.achievements_shown = shown
        # F4 · mint prompt — al completar TODAS las quests, invitar una sola
        # vez a mintear el NFT-certificado. Guard `db.mint_prompt_shown`.
        try:
            from commands.terminal_commands import QUESTS as _QUESTS
            if (
                len(set(quest_done)) >= len(_QUESTS)
                and not self.db.mint_prompt_shown
            ):
                self.db.mint_prompt_shown = True
                super().msg(
                    "\n|y★ Ya eres intérprete del shell.|n "
                    "Teclea |wmint|n para grabar tu certificado onchain.\n"
                )
        except Exception:
            pass

    def get_display_name(self, looker, **kwargs):
        """Show HP in name for combat."""
        name = super().get_display_name(looker, **kwargs)
        if self.db.npc_type == "mob" and looker != self:
            hp_pct = int((self.db.hp / self.db.max_hp) * 100) if self.db.max_hp else 0
            if hp_pct >= 75:
                status = "|g[Healthy]|n"
            elif hp_pct >= 50:
                status = "|y[Wounded]|n"
            elif hp_pct >= 25:
                status = "|r[Badly Wounded]|n"
            else:
                status = "|R[Near Death]|n"
            return f"{name} {status}"
        return name

    def at_damage(self, damage, attacker=None):
        """
        Called when taking damage.
        Returns True if character died.
        """
        # Apply armor reduction
        actual_damage = max(1, damage - self.db.armor)
        self.db.hp -= actual_damage

        if attacker:
            self.msg(f"|r{attacker.key} hits you for {actual_damage} damage!|n")
            attacker.msg(f"|gYou hit {self.key} for {actual_damage} damage!|n")

        # Check for death
        if self.db.hp <= 0:
            self.db.hp = 0
            self.at_death(attacker)
            return True
        return False

    def at_death(self, killer=None):
        """Called when HP reaches 0."""
        self.db.in_combat = False
        self.db.combat_target = None

        # Announce death
        self.location.msg_contents(
            f"|R{self.key} has been defeated!|n",
            exclude=[self]
        )

        if self.db.npc_type == "mob":
            # NPC death - create corpse with loot and give XP
            self.create_corpse()
            if killer and hasattr(killer.db, 'xp'):
                xp_gained = self.db.stats.get("xp", 10) if self.db.stats else 10
                killer.gain_xp(xp_gained)

            # Schedule respawn
            respawn_time = 60  # 60 seconds
            delay(respawn_time, self.respawn)
        else:
            # Player death - respawn at clinic
            self.msg("|RYou have been defeated!|n")
            self.msg("|yYou wake up at the Underground Clinic...|n")
            delay(3, self.player_respawn)

    def player_respawn(self):
        """Respawn player at clinic."""
        clinic = search_object("Underground Clinic")
        if clinic:
            self.move_to(clinic[0], quiet=True)
            self.db.hp = self.db.max_hp // 2  # Respawn at half HP
            self.msg("|gYou regain consciousness on an operating table.|n")
            self.location.msg_contents(
                f"{self.key} wakes up on the operating table.",
                exclude=[self]
            )

    def respawn(self):
        """Respawn mob at original location."""
        self.db.hp = self.db.max_hp
        self.db.in_combat = False
        self.db.combat_target = None
        if self.location:
            self.location.msg_contents(
                f"|y{self.key} has respawned!|n"
            )

    def create_corpse(self):
        """Create a corpse with loot when mob dies."""
        from typeclasses.corpse import create_corpse as make_corpse

        # Create the corpse
        corpse = make_corpse(self, self.location)

        # Add loot to corpse
        loot_table = self.db.stats.get("loot", []) if self.db.stats else []
        loot_dropped = []

        for item_name in loot_table:
            if random.random() < 0.5:  # 50% drop chance
                item = create_object(
                    "typeclasses.objects.Object",
                    key=item_name,
                    location=corpse  # Loot goes IN the corpse
                )
                item.db.desc = f"Loot from {self.key}."
                item.db.item_type = "loot"
                item.db.value = random.randint(1, 5)
                loot_dropped.append(item_name)

        # Add coins to corpse
        coins = random.randint(1, 10)
        corpse.db.coins = coins

        # Announce
        self.location.msg_contents(
            f"|x{self.key} falls, leaving behind a corpse.|n"
        )
        if loot_dropped:
            self.location.msg_contents(
                f"|yThe corpse contains: {', '.join(loot_dropped)} and {coins} $ABYSS|n"
            )

    def gain_xp(self, amount):
        """Gain experience points."""
        self.db.xp += amount
        self.msg(f"|c+{amount} XP|n")

        # Check for level up
        while self.db.xp >= self.db.xp_to_level:
            self.level_up()

    def level_up(self):
        """Level up the character."""
        self.db.xp -= self.db.xp_to_level
        self.db.level += 1
        self.db.xp_to_level = int(self.db.xp_to_level * 1.5)

        # Increase stats
        self.db.max_hp += 10
        self.db.hp = self.db.max_hp
        self.db.damage += 2

        self.msg(f"|G*** LEVEL UP! You are now level {self.db.level}! ***|n")
        self.msg(f"|g+10 Max HP, +2 Damage|n")
        if self.location:
            self.location.msg_contents(
                f"|G{self.key} has reached level {self.db.level}!|n",
                exclude=[self]
            )

    def attack(self, target):
        """
        Attack a target.
        Returns damage dealt.
        """
        # Calculate damage
        base_damage = self.db.damage

        # Add weapon damage if equipped
        # TODO: Check equipped weapon

        # Add stat bonus
        str_bonus = (self.db.stats.get("str", 10) - 10) // 2 if self.db.stats else 0

        # Random variance
        damage = base_damage + str_bonus + random.randint(-2, 2)
        damage = max(1, damage)

        # Check for critical hit
        crit_chance = 5 + (self.db.stats.get("dex", 10) - 10) if self.db.stats else 5
        if random.randint(1, 100) <= crit_chance:
            damage *= 2
            self.msg("|Y*** CRITICAL HIT! ***|n")
            target.msg("|R*** CRITICAL HIT! ***|n")

        return damage

    def start_combat(self, target):
        """Start combat with a target."""
        self.db.in_combat = True
        self.db.combat_target = target
        # Start auto-attack loop for players
        if not self.db.npc_type:
            delay(3, self.auto_attack)

    def end_combat(self):
        """End combat."""
        self.db.in_combat = False
        self.db.combat_target = None

    def auto_attack(self):
        """Auto-attack loop for players in combat."""
        if not self.db.in_combat or not self.db.combat_target:
            return

        target = self.db.combat_target

        # Check if target is still valid
        if not target or target.location != self.location:
            self.msg("|yYour target is gone. Combat ended.|n")
            self.end_combat()
            return

        if target.db.hp <= 0:
            self.msg(f"|g{target.key} is defeated!|n")
            self.end_combat()
            return

        # Check if player is still alive
        if self.db.hp <= 0:
            return

        # Attack!
        damage = self.attack(target)
        died = target.at_damage(damage, self)

        if died:
            self.end_combat()
        else:
            # Continue combat every 3 seconds
            delay(3, self.auto_attack)


class NPC(Character):
    """
    NPC character with AI behavior.
    Can be merchants, guards, or hostile mobs.
    """

    def at_object_creation(self):
        """Set up NPC."""
        super().at_object_creation()
        self.db.npc_type = "generic"
        self.db.faction = "neutral"
        self.db.dialogue = {}
        self.db.aggro_range = 0  # 0 = not aggressive

    def at_damage(self, damage, attacker=None):
        """NPC response to being attacked."""
        died = super().at_damage(damage, attacker)

        if not died and attacker and self.db.npc_type == "mob":
            # Fight back!
            if not self.db.in_combat:
                self.start_combat(attacker)
                self.location.msg_contents(
                    f"|r{self.key} attacks {attacker.key}!|n"
                )
            # Counter-attack
            delay(2, self.mob_attack)

        return died

    def mob_attack(self):
        """Mob attacks its target."""
        if not self.db.in_combat or not self.db.combat_target:
            return

        target = self.db.combat_target

        # Check if target is still here and alive
        if not target or target.location != self.location:
            self.end_combat()
            return

        if target.db.hp <= 0:
            self.end_combat()
            return

        # Attack!
        damage = self.attack(target)
        died = target.at_damage(damage, self)

        if died:
            self.end_combat()
        else:
            # Continue combat
            delay(3, self.mob_attack)
