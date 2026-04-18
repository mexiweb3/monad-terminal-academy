"""
Item Commands for The Abyss

Commands: use, equip, unequip, inventory
"""

from evennia import Command, CmdSet


class CmdUse(Command):
    """
    Use a consumable item.

    Usage:
      use <item>

    Consumes food, drinks, or medical items for their effects.
    """

    key = "use"
    aliases = ["consume", "eat", "drink"]
    locks = "cmd:all()"
    help_category = "Items"

    def func(self):
        caller = self.caller

        if not self.args:
            caller.msg("Use what?")
            return

        # Find item in inventory
        item = caller.search(self.args.strip(), location=caller)
        if not item:
            return

        # Check if it's consumable
        item_type = item.db.item_type
        if item_type != "consumable":
            caller.msg(f"You can't consume {item.key}.")
            return

        # Apply effects
        effect = item.db.effect or {}
        messages = []

        # Healing
        if "heal" in effect:
            heal_amount = effect["heal"]
            old_hp = caller.db.hp
            caller.db.hp = min(caller.db.hp + heal_amount, caller.db.max_hp)
            actual_heal = caller.db.hp - old_hp
            if actual_heal > 0:
                messages.append(f"|g+{actual_heal} HP|n")

        # Buffs
        if "buff" in effect:
            buff = effect["buff"]
            buff_type = buff.get("type", "")
            buff_value = buff.get("value", 0)
            duration = buff.get("duration", 300)

            # Store active buffs
            if not caller.db.active_buffs:
                caller.db.active_buffs = {}

            caller.db.active_buffs[buff_type] = {
                "value": buff_value,
                "duration": duration,
                "remaining": duration
            }
            messages.append(f"|c+{buff_value} {buff_type.upper()}|n for {duration}s")

        # Debuffs (negative effects)
        if "debuff" in effect:
            debuff = effect["debuff"]
            debuff_type = debuff.get("type", "")
            debuff_value = debuff.get("value", 0)
            duration = debuff.get("duration", 300)

            if not caller.db.active_buffs:
                caller.db.active_buffs = {}

            caller.db.active_buffs[debuff_type] = {
                "value": debuff_value,
                "duration": duration,
                "remaining": duration
            }
            messages.append(f"|r{debuff_value} {debuff_type.upper()}|n for {duration}s")

        # Infection chance (for expired medkits)
        if "infection_chance" in effect:
            import random
            if random.randint(1, 100) <= effect["infection_chance"]:
                damage = 5
                caller.db.hp -= damage
                messages.append(f"|R-{damage} HP (infection!)|n")

        # Consume the item
        subtype = item.db.subtype or "item"
        caller.msg(f"You consume {item.key}.")

        if messages:
            caller.msg(" ".join(messages))

        # Announce to room
        if caller.location:
            if subtype == "food":
                caller.location.msg_contents(
                    f"{caller.key} eats something.",
                    exclude=[caller]
                )
            elif subtype == "drink":
                caller.location.msg_contents(
                    f"{caller.key} takes a drink.",
                    exclude=[caller]
                )
            elif subtype == "medical":
                caller.location.msg_contents(
                    f"{caller.key} uses medical supplies.",
                    exclude=[caller]
                )

        # Delete the consumed item
        item.delete()


class CmdEquip(Command):
    """
    Equip a weapon or implant.

    Usage:
      equip <item>
      wield <item>

    Equips weapons to increase damage or implants to gain bonuses.
    """

    key = "equip"
    aliases = ["wield", "wear"]
    locks = "cmd:all()"
    help_category = "Items"

    def func(self):
        caller = self.caller

        if not self.args:
            caller.msg("Equip what?")
            return

        # Find item in inventory
        item = caller.search(self.args.strip(), location=caller)
        if not item:
            return

        item_type = item.db.item_type

        # Initialize equipment slots if needed
        if not caller.db.equipped:
            caller.db.equipped = {
                "weapon": None,
                "head": None,
                "eyes": None,
                "spine": None,
                "skin": None,
                "left_arm": None,
                "right_arm": None,
            }

        if item_type == "weapon":
            # Unequip current weapon first
            current = caller.db.equipped.get("weapon")
            if current:
                caller.msg(f"You put away {current.key}.")
                # Return stats to base
                if current.db.damage:
                    caller.db.damage -= current.db.damage

            # Equip new weapon
            caller.db.equipped["weapon"] = item
            if item.db.damage:
                caller.db.damage += item.db.damage

            caller.msg(f"|gYou equip {item.key}.|n")
            caller.msg(f"Damage: {caller.db.damage}")

            if caller.location:
                caller.location.msg_contents(
                    f"{caller.key} equips {item.key}.",
                    exclude=[caller]
                )

        elif item_type == "implant":
            slot = item.db.slot
            if not slot:
                caller.msg(f"{item.key} can't be installed.")
                return

            # Check cyber cost
            cyber_cost = item.db.cyber_cost or 0
            current_cyber = caller.db.stats.get("cyber", 0) if caller.db.stats else 0
            max_cyber = 50  # Maximum cybernetic capacity

            # Calculate total cyber in use
            total_cyber = 0
            for eq_slot, eq_item in caller.db.equipped.items():
                if eq_item and eq_item.db.cyber_cost:
                    total_cyber += eq_item.db.cyber_cost

            if total_cyber + cyber_cost > max_cyber:
                caller.msg(f"|rNot enough cyber capacity! ({total_cyber + cyber_cost}/{max_cyber})|n")
                return

            # Unequip current implant in slot
            current = caller.db.equipped.get(slot)
            if current:
                caller.msg(f"You remove {current.key}.")
                # Remove bonuses
                if current.db.bonus:
                    for stat, value in current.db.bonus.items():
                        if stat in caller.db.stats:
                            caller.db.stats[stat] -= value
                        elif stat == "armor":
                            caller.db.armor -= value

            # Install new implant
            caller.db.equipped[slot] = item

            # Apply bonuses
            if item.db.bonus:
                for stat, value in item.db.bonus.items():
                    if stat in caller.db.stats:
                        caller.db.stats[stat] += value
                    elif stat == "armor":
                        caller.db.armor += value

            # Update cyber level
            caller.db.stats["cyber"] = total_cyber + cyber_cost

            caller.msg(f"|gYou install {item.key} in your {slot}.|n")
            if item.db.bonus:
                bonus_str = ", ".join([f"+{v} {k.upper()}" for k, v in item.db.bonus.items()])
                caller.msg(f"Bonuses: {bonus_str}")

            if caller.location:
                caller.location.msg_contents(
                    f"{caller.key} installs a cybernetic implant.",
                    exclude=[caller]
                )

        else:
            caller.msg(f"You can't equip {item.key}.")


class CmdUnequip(Command):
    """
    Unequip a weapon or implant.

    Usage:
      unequip <item>
      remove <item>

    Removes equipped items. Implants can be painful to remove.
    """

    key = "unequip"
    aliases = ["remove", "unwield"]
    locks = "cmd:all()"
    help_category = "Items"

    def func(self):
        caller = self.caller

        if not self.args:
            caller.msg("Unequip what?")
            return

        if not caller.db.equipped:
            caller.msg("You don't have anything equipped.")
            return

        search_term = self.args.strip().lower()

        # Find equipped item
        found_slot = None
        found_item = None
        for slot, item in caller.db.equipped.items():
            if item and search_term in item.key.lower():
                found_slot = slot
                found_item = item
                break

        if not found_item:
            caller.msg(f"You don't have '{self.args.strip()}' equipped.")
            return

        # Unequip
        if found_item.db.item_type == "weapon":
            if found_item.db.damage:
                caller.db.damage -= found_item.db.damage
            caller.db.equipped["weapon"] = None
            caller.msg(f"You put away {found_item.key}.")
            caller.msg(f"Damage: {caller.db.damage}")

        elif found_item.db.item_type == "implant":
            # Remove bonuses
            if found_item.db.bonus:
                for stat, value in found_item.db.bonus.items():
                    if stat in caller.db.stats:
                        caller.db.stats[stat] -= value
                    elif stat == "armor":
                        caller.db.armor -= value

            # Update cyber level
            if found_item.db.cyber_cost:
                caller.db.stats["cyber"] -= found_item.db.cyber_cost

            caller.db.equipped[found_slot] = None

            # Removing implants hurts!
            import random
            damage = random.randint(5, 15)
            caller.db.hp -= damage
            caller.msg(f"|rYou painfully remove {found_item.key}. (-{damage} HP)|n")

            if caller.location:
                caller.location.msg_contents(
                    f"{caller.key} grimaces while removing a cybernetic implant.",
                    exclude=[caller]
                )
        else:
            caller.db.equipped[found_slot] = None
            caller.msg(f"You unequip {found_item.key}.")


class CmdInventory(Command):
    """
    View your inventory.

    Usage:
      inventory
      inv
      i

    Shows all items you're carrying and what's equipped.
    """

    key = "inventory"
    aliases = ["inv", "i"]
    locks = "cmd:all()"
    help_category = "Items"

    def func(self):
        caller = self.caller
        items = caller.contents

        msg = []
        msg.append("|c╔══════════════════════════════════╗|n")
        msg.append(f"|c║|n  |wINVENTORY - {caller.key}|n")
        msg.append("|c╠══════════════════════════════════╣|n")

        # Show equipped items
        msg.append("|c║|n  |yEQUIPPED:|n")
        if caller.db.equipped:
            weapon = caller.db.equipped.get("weapon")
            if weapon:
                dmg = weapon.db.damage or 0
                msg.append(f"|c║|n    Weapon: |w{weapon.key}|n (+{dmg} dmg)")
            else:
                msg.append("|c║|n    Weapon: |xNone|n")

            # Show implants
            implant_slots = ["head", "eyes", "spine", "skin", "left_arm", "right_arm"]
            for slot in implant_slots:
                implant = caller.db.equipped.get(slot)
                if implant:
                    msg.append(f"|c║|n    {slot.replace('_', ' ').title()}: |m{implant.key}|n")
        else:
            msg.append("|c║|n    |xNothing equipped|n")

        msg.append("|c╠══════════════════════════════════╣|n")

        # Show carried items
        msg.append("|c║|n  |yITEMS:|n")
        if items:
            for item in items:
                item_type = item.db.item_type or "misc"
                value = item.db.value or 0

                # Color by type
                if item_type == "weapon":
                    color = "|r"
                elif item_type == "consumable":
                    color = "|g"
                elif item_type == "implant":
                    color = "|m"
                elif item_type == "quest":
                    color = "|y"
                elif item_type == "loot":
                    color = "|x"
                else:
                    color = "|w"

                # Check if equipped
                equipped_marker = ""
                if caller.db.equipped:
                    for slot, eq_item in caller.db.equipped.items():
                        if eq_item == item:
                            equipped_marker = " |g[E]|n"
                            break

                msg.append(f"|c║|n    {color}{item.key}|n{equipped_marker} - ${value}")
        else:
            msg.append("|c║|n    |xEmpty|n")

        msg.append("|c╠══════════════════════════════════╣|n")

        # Show currency
        coins = caller.db.abyss_coins or 0
        msg.append(f"|c║|n  |Y$ABYSS: {coins}|n")

        msg.append("|c╚══════════════════════════════════╝|n")

        caller.msg("\n".join(msg))


class CmdGet(Command):
    """
    Pick up an item.

    Usage:
      get <item>
      take <item>
      pick up <item>

    Picks up an item from your current location.
    """

    key = "get"
    aliases = ["take", "pick up", "grab"]
    locks = "cmd:all()"
    help_category = "Items"

    def func(self):
        caller = self.caller

        if not self.args:
            caller.msg("Get what?")
            return

        # Find item in room
        item = caller.search(self.args.strip(), location=caller.location)
        if not item:
            return

        # Can't pick up characters, exits, or rooms
        if hasattr(item, 'is_exit') or hasattr(item.db, 'npc_type') or item == caller.location:
            caller.msg(f"You can't pick up {item.key}.")
            return

        # Check if item is gettable
        if item.db.no_get:
            caller.msg(f"You can't pick up {item.key}.")
            return

        # Move item to inventory
        item.move_to(caller, quiet=True)
        caller.msg(f"You pick up {item.key}.")

        if caller.location:
            caller.location.msg_contents(
                f"{caller.key} picks up {item.key}.",
                exclude=[caller]
            )


class CmdDrop(Command):
    """
    Drop an item.

    Usage:
      drop <item>

    Drops an item from your inventory to the ground.
    """

    key = "drop"
    aliases = ["put down"]
    locks = "cmd:all()"
    help_category = "Items"

    def func(self):
        caller = self.caller

        if not self.args:
            caller.msg("Drop what?")
            return

        # Find item in inventory
        item = caller.search(self.args.strip(), location=caller)
        if not item:
            return

        # Check if equipped
        if caller.db.equipped:
            for slot, eq_item in caller.db.equipped.items():
                if eq_item == item:
                    caller.msg(f"You need to unequip {item.key} first.")
                    return

        # Drop item
        item.move_to(caller.location, quiet=True)
        caller.msg(f"You drop {item.key}.")

        if caller.location:
            caller.location.msg_contents(
                f"{caller.key} drops {item.key}.",
                exclude=[caller]
            )


class CmdGive(Command):
    """
    Give an item to someone.

    Usage:
      give <item> to <target>

    Gives an item from your inventory to another character.
    """

    key = "give"
    locks = "cmd:all()"
    help_category = "Items"

    def func(self):
        caller = self.caller

        if not self.args or " to " not in self.args:
            caller.msg("Usage: give <item> to <target>")
            return

        parts = self.args.split(" to ", 1)
        item_name = parts[0].strip()
        target_name = parts[1].strip()

        # Find item
        item = caller.search(item_name, location=caller)
        if not item:
            return

        # Find target
        target = caller.search(target_name, location=caller.location)
        if not target:
            return

        if target == caller:
            caller.msg("You can't give something to yourself.")
            return

        # Check if equipped
        if caller.db.equipped:
            for slot, eq_item in caller.db.equipped.items():
                if eq_item == item:
                    caller.msg(f"You need to unequip {item.key} first.")
                    return

        # Give item
        item.move_to(target, quiet=True)
        caller.msg(f"You give {item.key} to {target.key}.")
        target.msg(f"{caller.key} gives you {item.key}.")

        if caller.location:
            caller.location.msg_contents(
                f"{caller.key} gives something to {target.key}.",
                exclude=[caller, target]
            )


class CmdLoot(Command):
    """
    Loot a corpse.

    Usage:
      loot <corpse>
      loot all from <corpse>

    Takes all items and coins from a corpse.
    """

    key = "loot"
    aliases = ["search corpse", "search body"]
    locks = "cmd:all()"
    help_category = "Items"

    def func(self):
        caller = self.caller

        if not self.args:
            # Try to find any corpse in the room
            corpses = [obj for obj in caller.location.contents
                       if obj.is_typeclass("typeclasses.corpse.Corpse")]
            if not corpses:
                caller.msg("There's nothing to loot here.")
                return
            corpse = corpses[0]
        else:
            corpse = caller.search(self.args.strip(), location=caller.location)
            if not corpse:
                return

        # Check if it's a corpse
        if not corpse.is_typeclass("typeclasses.corpse.Corpse"):
            caller.msg(f"You can't loot {corpse.key}.")
            return

        looted = []

        # Take all items from corpse
        for item in list(corpse.contents):
            item.move_to(caller, quiet=True)
            looted.append(item.key)

        # Take coins
        coins = corpse.db.coins or 0
        if coins > 0:
            caller.db.abyss_coins = (caller.db.abyss_coins or 0) + coins
            looted.append(f"{coins} $ABYSS")
            corpse.db.coins = 0

        if looted:
            caller.msg(f"|gYou loot: {', '.join(looted)}|n")
            if caller.location:
                caller.location.msg_contents(
                    f"{caller.key} loots the corpse.",
                    exclude=[caller]
                )
        else:
            caller.msg("The corpse has already been looted.")


class ItemCmdSet(CmdSet):
    """Item commands."""

    key = "ItemCmdSet"
    priority = 1

    def at_cmdset_creation(self):
        self.add(CmdUse())
        self.add(CmdEquip())
        self.add(CmdUnequip())
        self.add(CmdInventory())
        self.add(CmdGet())
        self.add(CmdDrop())
        self.add(CmdGive())
        self.add(CmdLoot())
