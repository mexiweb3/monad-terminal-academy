"""
Combat Commands for The Abyss

Commands: attack, kill, flee, status, hp
"""

from evennia import Command, CmdSet
from evennia.utils import delay


class CmdAttack(Command):
    """
    Attack a target.

    Usage:
      attack <target>
      kill <target>
      hit <target>

    Initiates combat with the specified target. Combat continues
    automatically until one combatant is defeated or flees.
    """

    key = "attack"
    aliases = ["kill", "hit", "fight"]
    locks = "cmd:all()"
    help_category = "Combat"

    def func(self):
        caller = self.caller

        if not self.args:
            caller.msg("Attack who?")
            return

        # Find target in room
        target = caller.search(self.args.strip(), location=caller.location)
        if not target:
            return

        # Can't attack yourself
        if target == caller:
            caller.msg("You can't attack yourself. Seek therapy instead.")
            return

        # Check if target is attackable (has HP)
        if not hasattr(target.db, 'hp') or target.db.hp is None:
            caller.msg(f"You can't attack {target.key}.")
            return

        # Check if target is already dead
        if target.db.hp <= 0:
            caller.msg(f"{target.key} is already dead. No honor in that.")
            return

        # Check if already in combat with this target
        if caller.db.in_combat and caller.db.combat_target == target:
            caller.msg("You're already fighting them!")
            return

        # Start combat
        caller.start_combat(target)

        # Announce
        caller.location.msg_contents(
            f"|r{caller.key} attacks {target.key}!|n",
            exclude=[caller, target]
        )
        caller.msg(f"|rYou attack {target.key}!|n")
        target.msg(f"|R{caller.key} attacks you!|n")

        # First attack
        damage = caller.attack(target)
        target.at_damage(damage, caller)


class CmdFlee(Command):
    """
    Attempt to flee from combat.

    Usage:
      flee

    Try to escape from combat. There's a chance of failure,
    and you might take damage while fleeing.
    """

    key = "flee"
    aliases = ["escape", "run"]
    locks = "cmd:all()"
    help_category = "Combat"

    def func(self):
        caller = self.caller

        if not caller.db.in_combat:
            caller.msg("You're not in combat. No need to flee.")
            return

        # Flee chance based on dexterity
        import random
        dex = caller.db.stats.get("dex", 10) if caller.db.stats else 10
        flee_chance = 40 + (dex - 10) * 3  # Base 40%, +3% per DEX point

        if random.randint(1, 100) <= flee_chance:
            # Successful flee
            caller.msg("|gYou manage to escape from combat!|n")
            caller.location.msg_contents(
                f"{caller.key} flees from combat!",
                exclude=[caller]
            )

            # End combat
            if caller.db.combat_target:
                caller.db.combat_target.end_combat()
            caller.end_combat()

            # Move to random exit
            exits = [ex for ex in caller.location.exits]
            if exits:
                random_exit = random.choice(exits)
                caller.msg(f"You run {random_exit.key}!")
                caller.execute_cmd(random_exit.key)
        else:
            # Failed flee - take damage
            caller.msg("|rYou fail to escape!|n")
            if caller.db.combat_target:
                damage = caller.db.combat_target.attack(caller) // 2
                caller.at_damage(damage, caller.db.combat_target)
                caller.msg("|rYou take damage while trying to flee!|n")


class CmdStatus(Command):
    """
    Check your combat status.

    Usage:
      status
      hp
      stats

    Shows your current HP, level, XP, and combat stats.
    """

    key = "status"
    aliases = ["hp", "stats", "score"]
    locks = "cmd:all()"
    help_category = "Combat"

    def func(self):
        caller = self.caller

        # HP bar
        hp = caller.db.hp or 0
        max_hp = caller.db.max_hp or 100
        hp_pct = int((hp / max_hp) * 100) if max_hp else 0

        # Color based on HP
        if hp_pct >= 75:
            hp_color = "|g"
        elif hp_pct >= 50:
            hp_color = "|y"
        elif hp_pct >= 25:
            hp_color = "|r"
        else:
            hp_color = "|R"

        # HP bar visual
        bar_length = 20
        filled = int((hp / max_hp) * bar_length) if max_hp else 0
        bar = "█" * filled + "░" * (bar_length - filled)

        msg = []
        msg.append("|c╔══════════════════════════════════╗|n")
        msg.append(f"|c║|n  |w{caller.key}|n - Level {caller.db.level or 1}")
        msg.append(f"|c║|n  HP: {hp_color}{bar}|n {hp}/{max_hp}")
        msg.append(f"|c║|n  XP: {caller.db.xp or 0}/{caller.db.xp_to_level or 100}")
        msg.append(f"|c║|n  $ABYSS: |Y{caller.db.abyss_coins or 0}|n")
        msg.append("|c╠══════════════════════════════════╣|n")

        # Stats
        stats = caller.db.stats or {}
        msg.append(f"|c║|n  STR: {stats.get('str', 10):2}  DEX: {stats.get('dex', 10):2}  CON: {stats.get('con', 10):2}")
        msg.append(f"|c║|n  INT: {stats.get('int', 10):2}  WIS: {stats.get('wis', 10):2}  CHA: {stats.get('cha', 10):2}")
        msg.append(f"|c║|n  CYBER: {stats.get('cyber', 0)}")
        msg.append("|c╠══════════════════════════════════╣|n")

        # Combat stats
        msg.append(f"|c║|n  Damage: {caller.db.damage or 5}  Armor: {caller.db.armor or 0}")

        # Combat status
        if caller.db.in_combat:
            target = caller.db.combat_target
            target_name = target.key if target else "Unknown"
            msg.append(f"|c║|n  |rIN COMBAT|n with {target_name}")
        else:
            msg.append(f"|c║|n  |gNot in combat|n")

        msg.append("|c╚══════════════════════════════════╝|n")

        caller.msg("\n".join(msg))


class CmdConsider(Command):
    """
    Consider how tough an enemy is.

    Usage:
      consider <target>
      con <target>

    Estimates how difficult a fight would be.
    """

    key = "consider"
    aliases = ["con"]
    locks = "cmd:all()"
    help_category = "Combat"

    def func(self):
        caller = self.caller

        if not self.args:
            caller.msg("Consider who?")
            return

        target = caller.search(self.args.strip(), location=caller.location)
        if not target:
            return

        if not hasattr(target.db, 'hp') or target.db.hp is None:
            caller.msg(f"{target.key} doesn't look like a fighter.")
            return

        # Compare levels/HP
        caller_power = (caller.db.hp or 100) + (caller.db.damage or 5) * 10
        target_power = (target.db.hp or 100) + (target.db.damage or 5) * 10

        ratio = target_power / caller_power if caller_power else 1

        if ratio < 0.5:
            msg = f"|g{target.key} looks like easy prey.|n"
        elif ratio < 0.75:
            msg = f"|g{target.key} should be a fair fight.|n"
        elif ratio < 1.0:
            msg = f"|y{target.key} looks about your level.|n"
        elif ratio < 1.5:
            msg = f"|y{target.key} looks tougher than you.|n"
        elif ratio < 2.0:
            msg = f"|r{target.key} would be a dangerous fight.|n"
        else:
            msg = f"|R{target.key} would destroy you. Run.|n"

        caller.msg(msg)

        # Show mob HP if hostile
        if target.db.npc_type == "mob":
            hp_pct = int((target.db.hp / target.db.max_hp) * 100) if target.db.max_hp else 0
            caller.msg(f"HP: {hp_pct}%")


class CombatCmdSet(CmdSet):
    """Combat commands."""

    key = "CombatCmdSet"
    priority = 1

    def at_cmdset_creation(self):
        self.add(CmdAttack())
        self.add(CmdFlee())
        self.add(CmdStatus())
        self.add(CmdConsider())
