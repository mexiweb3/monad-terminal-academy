"""
NPCs for The Abyss
"""

from evennia import create_object, search_object

NPCS = {
    "dr_splice": {
        "key": "Dr. Splice",
        "desc": "A middle-aged man with more implants than a doctor should have. His cybernetic eyes scan you while he smiles with steel teeth.",
        "location": "Underground Clinic",
        "npc_type": "merchant",
        "faction": "neutral",
        "dialogue": {
            "greet": "Ah, another client. Here to upgrade or to fix what they broke?",
            "shop": "I have second-hand implants, but they work. Mostly.",
            "quest": "I need a Data Chip from the Dead Server Room. I pay well.",
            "bye": "Don't die before you pay me."
        }
    },
    "dona_kernel": {
        "key": "Dona Kernel",
        "desc": "A robust woman with mechanical arms that let her cook on four pans at once. Her apron says 'Kiss me I'm root'.",
        "location": "Taqueria The Last Byte",
        "npc_type": "merchant",
        "faction": "neutral",
        "dialogue": {
            "greet": "Mijo! Here to eat or just to look at me? Sit down, you look skinny.",
            "shop": "I got Al Pastor 2.0, Carnitas Legacy, and Bug-Free Suadero.",
            "gossip": "They say the Chromes are getting restless...",
            "bye": "Come back soon! And don't get killed, you owe me three tacos."
        }
    },
    "arm_bartender": {
        "key": "Arm Bartender",
        "desc": "Literally just a robotic arm mounted on the bar. No body, no head, no detectable personality.",
        "location": "Bar Overflow",
        "npc_type": "merchant",
        "faction": "neutral",
        "dialogue": {
            "greet": "*The arm makes a gesture that could be a greeting*",
            "shop": "*Points at a chalkboard: Overflow Shot $5, Bitter Byte $10, Memory Leak $15*",
            "gossip": "*The arm writes on the bar: THE CHROMES ARE LOOKING FOR SOMETHING*",
            "bye": "*The arm gives a thumbs up*"
        }
    },
    "chrome_guard": {
        "key": "Chrome Guard",
        "desc": "More machine than man. His body is 80 percent chromed metal. A red eye scans you while the other looks at you with boredom.",
        "location": "Stairs to Crimson District",
        "npc_type": "guard",
        "faction": "chrome",
        "dialogue": {
            "greet": "*BZZT* You got the 100 $ABYSS? *BZZT*",
            "no_money": "No credits, no access. *BZZT*",
            "bribe": "For 150 I could not see you pass. *BZZT*",
            "bye": "*BZZT* Scram. *BZZT*"
        },
        "unlock_cost": 100
    },
    "mech_rat": {
        "key": "Mech Rat",
        "desc": "A cat-sized rat with rusted implants. Its eyes glow with red LEDs. It looks at you calculating if you are food.",
        "location": "Rat Alley",
        "npc_type": "mob",
        "faction": "hostile",
        "stats": {"hp": 15, "damage": 3, "xp": 10, "loot": ["Copper Wire"]}
    },
    "broken_drone": {
        "key": "Broken Drone",
        "desc": "A surveillance drone that has clearly seen better decades. It floats erratically, crashing into walls.",
        "location": "Abandoned Terminal",
        "npc_type": "mob",
        "faction": "hostile",
        "stats": {"hp": 20, "damage": 5, "xp": 15, "loot": ["Spent Battery"]}
    }
}


def create_npcs(caller):
    """Create all NPCs for The Abyss."""
    caller.msg("Creating NPCs for The Abyss...")
    created = 0

    for npc_key, npc_data in NPCS.items():
        location = search_object(npc_data["location"])
        if not location:
            caller.msg(f"  ERROR: Room not found for {npc_data['key']}")
            continue
        location = location[0]

        existing = [obj for obj in location.contents if obj.key == npc_data["key"]]
        if existing:
            caller.msg(f"  {npc_data['key']} already exists, skipping...")
            continue

        # Use NPC typeclass for mobs, Character for others
        typeclass = "typeclasses.characters.NPC" if npc_data.get("npc_type") == "mob" else "typeclasses.characters.Character"
        npc = create_object(
            typeclass,
            key=npc_data["key"],
            location=location
        )
        npc.db.desc = npc_data["desc"]
        npc.db.npc_type = npc_data.get("npc_type", "generic")
        npc.db.faction = npc_data.get("faction", "neutral")
        npc.db.dialogue = npc_data.get("dialogue", {})

        if npc_data.get("stats"):
            stats = npc_data["stats"]
            npc.db.stats = stats
            npc.db.hp = stats.get("hp", 100)
            npc.db.max_hp = stats.get("hp", 100)
            npc.db.damage = stats.get("damage", 5)
            npc.db.armor = stats.get("armor", 0)

        if npc_data.get("unlock_cost"):
            npc.db.unlock_cost = npc_data["unlock_cost"]

        caller.msg(f"  Created: {npc_data['key']} in {npc_data['location']}")
        created += 1

    caller.msg(f"\nTotal NPCs created: {created}")
    return created


def remove_npcs(caller):
    """Remove all Abyss NPCs."""
    caller.msg("Removing NPCs...")
    removed = 0
    for npc_key, npc_data in NPCS.items():
        existing = search_object(npc_data["key"])
        for npc in existing:
            if hasattr(npc, 'db') and getattr(npc.db, 'npc_type', None):
                npc.delete()
                caller.msg(f"  Removed: {npc_data['key']}")
                removed += 1
    caller.msg(f"Total removed: {removed}")
