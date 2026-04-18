"""
Corpse typeclass for The Abyss

When mobs die, they leave behind a corpse that can be looted.
"""

from evennia import DefaultObject, create_object
from evennia.utils import delay


class Corpse(DefaultObject):
    """
    A corpse left behind when a mob dies.
    Contains loot that can be taken.
    Decays after a set time.
    """

    def at_object_creation(self):
        """Set up the corpse."""
        self.db.decay_time = 60  # Seconds until corpse disappears
        self.db.original_mob = None
        self.db.coins = 0
        self.locks.add("get:false()")  # Can't pick up corpses
        # Start decay timer
        self.ndb.decaying = True
        delay(self.db.decay_time, self.decay)

    def at_init(self):
        """Called when corpse is loaded. Start decay timer."""
        # Only start decay if not already decaying and decay_time is set
        if not self.ndb.decaying and self.db.decay_time:
            self.ndb.decaying = True
            delay(self.db.decay_time, self.decay)

    def decay(self):
        """Corpse decays and disappears."""
        if not self.pk:  # Already deleted
            return

        # Drop any remaining items to the ground
        for item in self.contents:
            item.move_to(self.location, quiet=True)
            if self.location:
                self.location.msg_contents(
                    f"|x{item.key} falls from the rotting corpse.|n"
                )

        # Announce decay
        if self.location:
            self.location.msg_contents(
                f"|xThe corpse of {self.db.original_mob or 'something'} decays into nothing.|n"
            )

        self.delete()

    def return_appearance(self, looker, **kwargs):
        """Custom appearance for corpses."""
        mob_name = self.db.original_mob or "unknown creature"

        text = []
        text.append(f"|xThe bloody remains of {mob_name}.|n")
        text.append(f"|xIt will decay soon.|n")

        # Show contents
        if self.contents:
            text.append("")
            text.append("|yYou can loot:|n")
            for item in self.contents:
                value = item.db.value or 0
                text.append(f"  - {item.key} |x(${value})|n")

        # Show coins
        if self.db.coins > 0:
            text.append(f"  - |Y{self.db.coins} $ABYSS|n")

        if not self.contents and self.db.coins <= 0:
            text.append("|xThe corpse has been looted clean.|n")

        text.append("")
        text.append("|wUse: |nloot corpse|w or |nget <item> from corpse")

        return "\n".join(text)


def create_corpse(mob, location):
    """
    Create a corpse for a dead mob.

    Args:
        mob: The mob that died
        location: Where to create the corpse

    Returns:
        The created corpse object
    """
    corpse = create_object(
        Corpse,
        key=f"corpse of {mob.key}",
        location=location,
        aliases=["corpse", "body", "remains"]
    )

    corpse.db.desc = f"The mangled remains of {mob.key}. Still warm."
    corpse.db.original_mob = mob.key

    return corpse
