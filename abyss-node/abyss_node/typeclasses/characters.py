"""
Characters - Players and NPCs with combat stats

Combat system for The Abyss MUD
"""

import random
from evennia.objects.objects import DefaultCharacter
from evennia import create_object, search_object
from evennia.utils import delay

from .objects import ObjectParent


ACADEMY_BANNER = (
    "\n"
    "|g ╔══════════════════════════════════════════════════════════╗|n\n"
    "|g ║|n    |yM O N A D   T E R M I N A L   A C A D E M Y|n             |g║|n\n"
    "|g ║|n    aprende la terminal · gana |y$TERM|n onchain en Monad       |g║|n\n"
    "|g ║|n    + |cClaude CLI|n para generar y deployar contratos          |g║|n\n"
    "|g ╚══════════════════════════════════════════════════════════╝|n\n"
)

ACADEMY_TUTORIAL = (
    "|wBienvenide a la Academia.|n Este es un curso interactivo de terminal\n"
    "que paga en |y$TERM|n (ERC-20 en Monad testnet) cuando terminas quests.\n"
    "\n"
    "|yPrimer paso:|n escribe |gls|n y presiona Enter para listar este directorio.\n"
    "En cualquier momento escribe |ghelp|n para ver comandos + tu próxima quest.\n"
    "También puedes saludar a |cProf. Shell|n con |wsay hola prof|n si estás perdide.\n"
    "\n"
    "Ahora también aprendes |cClaude CLI|n + a generar contratos en Monad.\n"
    "Escribe |wclaude|n cuando llegues a |cclaude_dojo|n.\n"
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
        db.first_login_done). También celebramos el primer deploy onchain
        si no fue celebrado todavía (idempotente vía achievements_shown).
        """
        super().at_post_puppet(**kwargs)
        # NPCs con npc_type ya seteado no deben recibir onboarding.
        if getattr(self.db, "npc_type", None):
            return
        if not self.db.first_login_done:
            self.db.first_login_done = True
            self.msg(ACADEMY_BANNER)
            self.msg(ACADEMY_TUTORIAL)
        # Celebrar el primer deploy una sola vez (independiente del banner
        # — un jugador puede deployar en sesión anterior y re-conectar).
        self._celebrate_first_deploy()

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
        tras cualquier output. Solo aplica a players (NPCs no acumulan quests).
        """
        super().msg(text, *args, **kwargs)
        # Evitamos recursión cuando el propio achievement emite msg.
        if getattr(self, "_in_ach_check", False):
            return
        self._in_ach_check = True
        try:
            self._check_achievements()
        except Exception:
            # Jamás romper el flujo de mensajes por un bug de achievements.
            pass
        finally:
            self._in_ach_check = False

    def _check_achievements(self):
        """Muestra mensajes de achievement al cruzar hitos de quests."""
        quest_done = self.db.quest_done
        if not quest_done:
            return
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
