"""
Room

Rooms are simple containers that has no location of their own.

"""

from evennia.objects.objects import DefaultRoom

from .objects import ObjectParent


class Room(ObjectParent, DefaultRoom):
    """
    Rooms are like any Object, except their location is None
    (which is default). They also use basetype_setup() to
    add locks so they cannot be puppeted or picked up.
    (to change that, use at_object_creation instead)

    See mygame/typeclasses/objects.py for a list of
    properties and methods available on all Objects.
    """

    def return_appearance(self, looker, **kwargs):
        """
        Custom room appearance with ASCII art.
        """
        # Build the appearance string
        text = []

        # Room name (title)
        text.append(f"|c{self.key}|n")
        text.append("")

        # ASCII art (if available)
        if self.db.ascii_art:
            # Clean up any markdown code blocks from the ASCII art
            ascii_art = self.db.ascii_art
            ascii_art = ascii_art.replace("```ascii", "").replace("```text", "").replace("```", "")
            text.append(f"|x{ascii_art.strip()}|n")
            text.append("")

        # Description
        if self.db.desc:
            text.append(self.db.desc)
            text.append("")

        # Exits
        exits = self.exits
        if exits:
            exit_names = [f"|w{ex.key}|n" for ex in exits]
            text.append(f"|yExits:|n {', '.join(exit_names)}")

        # Characters in room (excluding looker)
        characters = [
            obj for obj in self.contents
            if obj.has_account and obj != looker
        ]
        if characters:
            char_names = [f"|c{char.key}|n" for char in characters]
            text.append(f"|yPlayers:|n {', '.join(char_names)}")

        # NPCs/Mobs in room
        npcs = [
            obj for obj in self.contents
            if hasattr(obj, 'db') and obj.db.npc_type and obj != looker
        ]
        if npcs:
            npc_names = []
            for npc in npcs:
                if npc.db.npc_type == "mob":
                    hp_pct = int((npc.db.hp / npc.db.max_hp) * 100) if npc.db.max_hp else 100
                    npc_names.append(f"|r{npc.key}|n |x({hp_pct}% HP)|n")
                else:
                    npc_names.append(f"|g{npc.key}|n")
            text.append(f"|yNPCs:|n {', '.join(npc_names)}")

        # Objects in room (items, corpses, etc)
        objects = [
            obj for obj in self.contents
            if not obj.has_account
            and not (hasattr(obj, 'db') and obj.db.npc_type)
            and obj not in exits
        ]
        if objects:
            obj_names = [f"|w{obj.key}|n" for obj in objects]
            text.append(f"|yItems:|n {', '.join(obj_names)}")

        return "\n".join(text)
