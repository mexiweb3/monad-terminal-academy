"""
NPCs educativos de Monad Terminal Academy.

- `ProfShell` vive en `/home`. Reacciona a `say` con saludos, tips, ayuda
  con claim, y a partir de iter-2 también con 3+ triggers sobre Claude:
  qué es claude, qué es un skill, cómo deploy, y shout-out a Austin.
- `ClaudeAvatar` vive en `/claude_dojo`. Reacciona a `say hola` con un
  banner de graduación contextual según `installed_skills` / `deployed_contracts`.

Uso:
  python _spawn_npcs.py       # spawnea/reutiliza ambos NPCs idempotentemente
"""

import re

from evennia import create_object
from evennia.utils import delay
from evennia.utils.search import search_object

from typeclasses.characters import Character


PROF_SHELL_DESC = (
    "|cProf. Shell|n — instructora virtual de Monad Terminal Academy.\n"
    "Su hoodie dice |w'> sudo teach_me'|n y carga una laptop con mil stickers.\n"
    "Salúdala con |wsay hola prof|n. También sabe de Claude: prueba "
    "|wsay qué es claude|n, |wsay qué es un skill|n o |wsay cómo deploy|n."
)

CLAUDE_AVATAR_DESC = (
    "|mClaude Avatar|n — proyección holográfica del CLI de IA. Vibra suavemente\n"
    "sobre el piso del |cclaude_dojo|n, leyendo un papelito invisible donde\n"
    "aparece tu progreso. Salúdale con |wsay hola|n y te guía a graduarte."
)


def _get_quests():
    """Import perezoso para no crear ciclo con terminal_commands."""
    try:
        from commands.terminal_commands import QUESTS
    except Exception:
        QUESTS = []
    return QUESTS


def _get_skills_catalog():
    """Lee el catálogo de skills publicado por terminal_commands (Sesión A)."""
    try:
        from commands.terminal_commands import AVAILABLE_SKILLS
        return AVAILABLE_SKILLS
    except Exception:
        return {}


def _get_deploy_enabling_skills():
    """Set de slugs que habilitan `claude deploy`. Fallback al skill original."""
    try:
        from commands.terminal_commands import DEPLOY_ENABLING_SKILLS
        return set(DEPLOY_ENABLING_SKILLS)
    except Exception:
        return {"austin-griffith/monad-kit"}


# ---------------------------------------------------------------------------
# Base
# ---------------------------------------------------------------------------
class AcademyNPC(Character):
    """
    Base para NPCs de la academia. No combaten, solo hablan.

    Subclases definen `react_to_say(player, content_lower)` para responder.
    """

    # Nombre visible con el que el NPC "habla" (color incluido)
    speaker_label = "NPC"

    def at_object_creation(self):
        super().at_object_creation()
        self.db.npc_type = "instructor"
        self.db.faction = "academy"
        self.db.aggro_range = 0
        self.db.hp = 999
        self.db.max_hp = 999
        self.locks.add("attack:false()")

    def at_msg_receive(self, text=None, from_obj=None, **kwargs):
        """
        Detecta cuando un player hace `say` algo en la room. El formato
        default de Evennia es: `Player says, "..."`.
        """
        if not from_obj or from_obj == self:
            return True
        if not getattr(from_obj, "has_account", False):
            return True
        raw = text
        if isinstance(text, (tuple, list)):
            raw = text[0] if text else ""
        if not isinstance(raw, str):
            return True
        lower = raw.lower()
        if " says," not in lower and " dice," not in lower and " dijo," not in lower:
            return True
        m = re.search(r'["\u201c]([^"\u201d]*)["\u201d]', raw)
        if not m:
            return True
        content = m.group(1).lower().strip()
        if not content:
            return True
        delay(0.8, self.react_to_say, from_obj, content)
        return True

    def react_to_say(self, player, content):
        """Override en subclases."""
        return

    def _say(self, text):
        """NPC habla a la room con su speaker_label."""
        if self.location:
            self.location.msg_contents(
                f'{self.speaker_label} dice, "{text}"', from_obj=self
            )


# ---------------------------------------------------------------------------
# Prof. Shell (home)
# ---------------------------------------------------------------------------
class ProfShell(AcademyNPC):
    """
    Instructora virtual en `/home`. Reacciona a:
      - hola prof / hello prof         → saludo + recomendación de próxima quest
      - ayuda / help                   → tips generales
      - claim / reclam                 → flujo onchain
      - qué es claude / que es claude  → explica el CLI de IA (iter-2)
      - qué es un skill / skills       → lista catálogo de skills (iter-2)
      - cómo deploy / como deploy      → pasos para deployar (iter-2)
      - austin                         → shout-out a Austin Griffith (iter-2)
      - adios / bye / chau             → despedida
    """

    speaker_label = "|cProf. Shell|n"

    def at_object_creation(self):
        super().at_object_creation()
        self.db.desc = PROF_SHELL_DESC
        self.db.npc_type = "instructor"

    # --- Routing ------------------------------------------------------
    def react_to_say(self, player, content):
        if not self.location or player.location != self.location:
            return
        # Ordenado por especificidad (matches más específicos primero)
        if "hola prof" in content or "hello prof" in content or "hi prof" in content:
            return self._greet(player)
        if "que es claude" in content or "qué es claude" in content or "what is claude" in content:
            return self._explain_claude(player)
        if "que es un skill" in content or "qué es un skill" in content or "skills?" in content or "que son los skills" in content or "qué son los skills" in content:
            return self._explain_skills(player)
        if "como deploy" in content or "cómo deploy" in content or "how deploy" in content:
            return self._explain_deploy(player)
        if "austin" in content or "scaffold" in content:
            return self._austin_shoutout(player)
        if "claim" in content or "reclam" in content:
            return self._explain_claim(player)
        if "ayuda" in content or "help" in content or "tip" in content:
            return self._tips(player)
        if any(w in content for w in ("adios", "adiós", "bye", "chau", "nos vemos")):
            return self._farewell(player)
        # cualquier otra cosa: ignorar silenciosamente

    # --- Responses ----------------------------------------------------
    def _next_quest_for(self, player):
        """Devuelve el dict de la próxima quest pendiente (orden q01→q19)."""
        done = set(player.db.quest_done or [])
        for q in _get_quests():
            if q["id"] not in done:
                return q
        return None

    def _progress_line(self, player):
        """Texto 'llevas X/Y' + hint de próximo paso contextual."""
        done = set(player.db.quest_done or [])
        total = len(_get_quests()) or 1
        nxt = self._next_quest_for(player)
        if nxt is None:
            wallet = player.db.wallet or ""
            pending = int(player.db.abyss_pending or 0)
            if wallet and pending > 0:
                return (
                    f"Llevas {total}/{total} comandos. "
                    f"Escribe `claim` y recibes {pending} $TERM onchain."
                )
            if not wallet:
                return (
                    f"Llevas {total}/{total} comandos. "
                    f"Linkea tu wallet con `link 0x...` y después `claim`."
                )
            return f"Llevas {total}/{total} comandos. ¡Ya reclamaste todo, graduade!"
        cmd = nxt["cmd"]
        if cmd.startswith("claude:"):
            pretty = {
                "skill":  "claude skills install austin-griffith/monad-kit",
                "new":    "claude new contract MiToken",
                "deploy": "claude deploy MiToken.sol",
            }.get(cmd.split(":", 1)[1], cmd)
            return (
                f"Llevas {len(done)}/{total} comandos. "
                f"Te falta `{pretty}` (+{nxt['reward']} $TERM)"
            )
        return (
            f"Llevas {len(done)}/{total} comandos. "
            f"Te falta `{cmd}` — {nxt['desc']} (+{nxt['reward']} $TERM)"
        )

    def _greet(self, player):
        self._say(f"¡Hola {player.key}! {self._progress_line(player)}")

    def _explain_claim(self, player):
        wallet = player.db.wallet or ""
        pending = int(player.db.abyss_pending or 0)
        if not wallet:
            self._say(
                "El `claim` manda $TERM onchain en Monad testnet. "
                "Primero: `link 0xTuWallet` para asociar una address. "
                "Después: `claim` y recibes un tx hash real en el explorer."
            )
        elif pending == 0:
            self._say(
                f"Tu wallet {wallet[:6]}... ya está linkeada, pero no tienes $TERM pendientes. "
                f"Completa más quests y vuelve."
            )
        else:
            self._say(
                f"Estás ready: {pending} $TERM reservados para {wallet[:6]}...{wallet[-4:]}. "
                f"Escribe `claim` y recibes el tx hash en segundos."
            )

    def _tips(self, player):
        self._say(
            "Tips: `ls` lista, `pwd` te dice dónde estás, `cd <dir>` cambia de directorio. "
            "Escribe `help` para ver todos los comandos y tu próxima quest. "
            "Y `quests` para ver tu progreso + $TERM pendientes."
        )

    def _farewell(self, player):
        self._say(
            f"Nos vemos, {player.key}. Recuerda: quien aprende terminal nunca está perdide."
        )

    # --- iter-2: triggers sobre Claude CLI --------------------------------
    def _explain_claude(self, player):
        self._say(
            "`claude` es un CLI de IA (modelo claude-opus-4-7 de Anthropic). "
            "En la vida real le pides código en lenguaje natural y lo genera. "
            "Aquí lo simulamos con subcomandos explícitos: "
            "`claude skills install ...`, `claude new contract ...`, `claude deploy ...`. "
            "Escribe solo `claude` para ver el menú."
        )

    def _explain_skills(self, player):
        catalog = _get_skills_catalog()
        if not catalog:
            self._say(
                "Los `skills` son paquetes de conocimiento que Claude aprende a usar. "
                "Hay 4 disponibles en esta academia. Escribe `claude skills list` para verlos."
            )
            return
        # Línea por skill: slug — name (author)
        lines = []
        for slug, meta in catalog.items():
            name = meta.get("name", slug)
            author = meta.get("author", "?")
            lines.append(f"{slug} — {name} ({author})")
        self._say(
            "Un `skill` es un paquete de conocimiento que Claude carga para una tarea. "
            "Disponibles: " + " · ".join(lines) +
            ". Instala con `claude skills install <slug>`."
        )

    def _explain_deploy(self, player):
        installed = set(player.db.installed_skills or [])
        deployed = list(player.db.deployed_contracts or [])
        deploy_skills = _get_deploy_enabling_skills()
        has_deploy_skill = bool(installed & deploy_skills)

        # Paso a paso personalizado
        if deployed:
            last = deployed[-1]
            addr = last.get("address", "?") if isinstance(last, dict) else "?"
            self._say(
                f"Ya deployaste {len(deployed)} contrato(s). El último en {addr[:12]}... "
                f"Puedes generar más con `claude new contract Otro`."
            )
            return
        if not has_deploy_skill:
            self._say(
                "Flujo de deploy: 1) instala un skill con soporte de deploy — "
                "`claude skills install portdeveloper/monad-development` (oficial, "
                "auto-verify) o `austin-griffith/monad-kit`. 2) `claude new contract "
                "MiToken` (genera .sol). 3) `claude deploy MiToken.sol`."
            )
            return
        self._say(
            "Ya tienes skill de deploy. Ahora: 1) `claude new contract MiToken` para "
            "generar el .sol, 2) `cat MiToken.sol` para revisar, "
            "3) `claude deploy MiToken.sol`."
        )

    def _austin_shoutout(self, player):
        self._say(
            "Austin Griffith es el creador de Scaffold-ETH — el toolkit open source más "
            "usado para arrancar dApps. Sus skills (`scaffold-eth`, `solidity-basics`, "
            "`monad-kit`) son los que usa Claude aquí. Gracias Austin, legend."
        )


# ---------------------------------------------------------------------------
# Claude Avatar (claude_dojo)
# ---------------------------------------------------------------------------
class ClaudeAvatar(AcademyNPC):
    """
    NPC de `/claude_dojo`. Reacciona a:
      - hola / hello           → banner de graduación + estado del flujo
      - skill / install        → recuerda instalar monad-kit si no está
      - deploy                 → explica el deploy o felicita si ya hay
      - austin                 → shout-out a Austin Griffith
    """

    speaker_label = "|mClaude Avatar|n"

    def at_object_creation(self):
        super().at_object_creation()
        self.db.desc = CLAUDE_AVATAR_DESC
        self.db.npc_type = "instructor"

    # --- Routing ------------------------------------------------------
    def react_to_say(self, player, content):
        if not self.location or player.location != self.location:
            return
        if "hola" in content or "hello" in content or "hi " in content or content.strip() in ("hi", "hey"):
            return self._graduation_prompt(player)
        if "skill" in content or "install" in content:
            return self._prompt_skill(player)
        if "deploy" in content or "ship" in content:
            return self._prompt_deploy(player)
        if "austin" in content or "scaffold" in content:
            return self._austin(player)
        if "que eres" in content or "qué eres" in content or "what are you" in content:
            return self._identity(player)
        # ignorar otros saludos

    # --- Responses ----------------------------------------------------
    def _graduation_prompt(self, player):
        installed = set(player.db.installed_skills or [])
        deployed = list(player.db.deployed_contracts or [])
        deploy_skills = _get_deploy_enabling_skills()
        has_deploy_skill = bool(installed & deploy_skills)

        head = (
            f"Bienvenide a claude_dojo, {player.key}. "
            "Aquí te gradúas usando IA para generar y deployar código."
        )
        if deployed:
            last = deployed[-1] if isinstance(deployed[-1], dict) else {}
            addr = last.get("address", "?")
            self._say(
                f"{head} Ya deployaste {len(deployed)} contrato(s) — último en "
                f"{addr[:12]}... ¡Oficialmente graduade! Linkea wallet y `claim`."
            )
            return
        if not installed:
            self._say(
                f"{head} Paso 1: instala un skill. Sugerido: "
                f"`claude skills install portdeveloper/monad-development` (oficial) "
                f"o `austin-griffith/monad-kit`."
            )
            return
        # Instalado pero sin skill de deploy
        if not has_deploy_skill:
            self._say(
                f"{head} Tienes {len(installed)} skill(s) pero ninguno habilita deploy. "
                f"Instala `portdeveloper/monad-development` o `austin-griffith/monad-kit`."
            )
            return
        self._say(
            f"{head} Tienes skill de deploy ready. Ahora: "
            f"`claude new contract MiToken` y luego `claude deploy MiToken.sol`."
        )

    def _prompt_skill(self, player):
        installed = set(player.db.installed_skills or [])
        deploy_skills = _get_deploy_enabling_skills()
        has_deploy_skill = bool(installed & deploy_skills)
        if not installed:
            self._say(
                "Instala tu primer skill — sugerido `portdeveloper/monad-development` "
                "(oficial con auto-verify) o `austin-griffith/monad-kit`. "
                "Ver todos con `claude skills list`."
            )
        elif not has_deploy_skill:
            self._say(
                f"Ya tienes {len(installed)} skill(s), pero para deployar necesitas uno "
                f"de estos: {', '.join(sorted(deploy_skills))}."
            )
        else:
            self._say(
                f"Ya tienes {len(installed)} skill(s), incluido uno con deploy. "
                f"Sigue con `claude new contract MiToken`."
            )

    def _prompt_deploy(self, player):
        installed = set(player.db.installed_skills or [])
        deployed = list(player.db.deployed_contracts or [])
        deploy_skills = _get_deploy_enabling_skills()
        if deployed:
            last = deployed[-1] if isinstance(deployed[-1], dict) else {}
            addr = last.get("address", "?")
            tx = last.get("tx", "?")
            self._say(
                f"¡Ya deployaste! Último contrato en {addr[:12]}... (tx {tx[:10]}...). "
                f"Puedes generar otro con `claude new contract Otro`."
            )
            return
        if not (installed & deploy_skills):
            self._say(
                f"Para `claude deploy` necesitas un skill de deploy. Sugerido: "
                f"`portdeveloper/monad-development` (oficial) o `austin-griffith/monad-kit`."
            )
            return
        # tiene kit, no ha deployado
        loc = self.location
        room_files = (player.db.fs_files or {}).get(loc.dbref, {}) if loc else {}
        sol = next((f for f in room_files if f.endswith(".sol")), None)
        if sol:
            self._say(
                f"Tienes `{sol}` generado. Lánzalo: `claude deploy {sol}`."
            )
        else:
            self._say(
                "Tienes monad-kit pero aún no generaste .sol. "
                "Corre `claude new contract MiToken` y luego `claude deploy MiToken.sol`."
            )

    def _austin(self, player):
        self._say(
            "Austin Griffith es un OG de DevRel en Ethereum. Publica los skills "
            "`scaffold-eth`, `solidity-basics` y `monad-kit` que Claude usa aquí."
        )

    def _identity(self, player):
        self._say(
            "Soy la proyección del CLI `claude`. En esta academia represento al modelo "
            "claude-opus-4-7 de Anthropic — aquí simulado, pero afuera es real."
        )


# ---------------------------------------------------------------------------
# Spawner helper (idempotente)
# ---------------------------------------------------------------------------
def _spawn_or_reuse(typeclass_path, key, room_key, desc, verbose=True):
    """Crea o reutiliza un NPC `key` en room `room_key`. Idempotente."""
    from typeclasses.rooms import Room

    rooms = search_object(room_key, typeclass=Room)
    if not rooms:
        if verbose:
            print(f"ERROR: room '{room_key}' no existe. Corre _build_world.py primero.")
        return None
    room = rooms[0]

    for obj in room.contents:
        if obj.key == key:
            if verbose:
                print(f"{key} ya vive en /{room_key} ({obj.dbref}). Idempotente.")
            if obj.typeclass_path != typeclass_path:
                obj.swap_typeclass(typeclass_path, clean_attributes=False, run_start_hooks="all")
                if verbose:
                    print(f"  → swap_typeclass a {typeclass_path}")
            obj.db.desc = desc
            return obj

    npc = create_object(typeclass_path, key=key, location=room)
    npc.db.desc = desc
    if verbose:
        print(f"{key} creada en /{room_key} ({npc.dbref}).")
    return npc


def spawn_prof_shell(verbose=True):
    return _spawn_or_reuse(
        "world.npcs.academy_npcs.ProfShell",
        "Prof. Shell",
        "home",
        PROF_SHELL_DESC,
        verbose=verbose,
    )


def spawn_claude_avatar(verbose=True):
    return _spawn_or_reuse(
        "world.npcs.academy_npcs.ClaudeAvatar",
        "Claude Avatar",
        "claude_dojo",
        CLAUDE_AVATAR_DESC,
        verbose=verbose,
    )


def spawn_all_academy_npcs(verbose=True):
    """Spawnea/reusa todos los NPCs de la academia. Idempotente."""
    return {
        "prof_shell": spawn_prof_shell(verbose=verbose),
        "claude_avatar": spawn_claude_avatar(verbose=verbose),
    }
