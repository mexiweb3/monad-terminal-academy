"""
Items for The Abyss
Weapons, consumables, implants, quest items, and loot
"""

from evennia import create_object, search_object

# Item Categories
WEAPONS = {
    "rusty_pipe": {
        "key": "Rusty Pipe",
        "desc": "A length of corroded metal pipe. Not elegant, but effective for cracking skulls. Tetanus included at no extra charge.",
        "type": "weapon",
        "subtype": "melee",
        "damage": 5,
        "durability": 20,
        "value": 5,
        "location": "Rat Alley",
    },
    "shock_knuckles": {
        "key": "Shock Knuckles",
        "desc": "Brass knuckles with a built-in taser. The battery is old but still packs enough punch to make someone reconsider their life choices.",
        "type": "weapon",
        "subtype": "melee",
        "damage": 8,
        "durability": 30,
        "effect": {"type": "stun", "chance": 15},
        "value": 25,
        "location": "Chrome Lair",
    },
    "makeshift_shiv": {
        "key": "Makeshift Shiv",
        "desc": "A sharpened piece of scrap metal wrapped in electrical tape. The Abyss special - free with every mugging.",
        "type": "weapon",
        "subtype": "melee",
        "damage": 6,
        "durability": 15,
        "effect": {"type": "bleed", "chance": 20},
        "value": 3,
        "location": "Forgotten Tunnel",
    },
    "junker_pistol": {
        "key": "Junker Pistol",
        "desc": "A frankenstein firearm assembled from three different guns. Fires .38 caliber prayers. 50% chance it jams, 100% chance it's loud.",
        "type": "weapon",
        "subtype": "ranged",
        "damage": 15,
        "ammo_type": "38_caliber",
        "magazine": 6,
        "jam_chance": 50,
        "value": 50,
        "location": "Black Market Plaza",
    },
    "neural_disruptor": {
        "key": "Neural Disruptor",
        "desc": "A chrome wand that fries neural implants. Illegal in 47 districts. Perfect for dealing with Chromes who forgot their manners.",
        "type": "weapon",
        "subtype": "tech",
        "damage": 12,
        "effect": {"type": "disable_cyber", "duration": 10},
        "charges": 5,
        "value": 150,
        "location": "Dead Server Room",
    },
}

CONSUMABLES = {
    # Taqueria food
    "taco_pastor": {
        "key": "Taco Al Pastor 2.0",
        "desc": "Synthetic pork marinated in code-optimized spices. Dona Kernel's secret recipe. Tastes like nostalgia for a past that never existed.",
        "type": "consumable",
        "subtype": "food",
        "effect": {"heal": 15, "buff": {"type": "str", "value": 1, "duration": 300}},
        "value": 8,
        "location": "Taqueria The Last Byte",
    },
    "taco_carnitas": {
        "key": "Taco Carnitas Legacy",
        "desc": "Slow-cooked protein chunks using grandmother's algorithm. Warning: May contain deprecated ingredients.",
        "type": "consumable",
        "subtype": "food",
        "effect": {"heal": 20},
        "value": 10,
        "location": "Taqueria The Last Byte",
    },
    "taco_suadero": {
        "key": "Taco Suadero Bug-Free",
        "desc": "Guaranteed no bugs in this batch. The meat, not the code. We make no promises about the code.",
        "type": "consumable",
        "subtype": "food",
        "effect": {"heal": 12, "buff": {"type": "dex", "value": 1, "duration": 300}},
        "value": 7,
        "location": "Taqueria The Last Byte",
    },
    "salsa_muerte": {
        "key": "Salsa La Muerte",
        "desc": "Dona Kernel's legendary hot sauce. Scoville rating: classified. Side effects include temporary blindness and existential clarity.",
        "type": "consumable",
        "subtype": "food",
        "effect": {"buff": {"type": "damage", "value": 3, "duration": 600}},
        "value": 15,
        "location": "Taqueria The Last Byte",
    },

    # Bar drinks
    "shot_overflow": {
        "key": "Overflow Shot",
        "desc": "Named after the exploit that funded this bar. Strong enough to overflow your buffer and your liver.",
        "type": "consumable",
        "subtype": "drink",
        "effect": {"buff": {"type": "crit", "value": 10, "duration": 300}, "debuff": {"type": "accuracy", "value": -5, "duration": 300}},
        "value": 5,
        "location": "Bar Overflow",
    },
    "bitter_byte": {
        "key": "Bitter Byte",
        "desc": "Eight shots of synthetic whiskey compressed into one. Tastes like regret and smells like progress.",
        "type": "consumable",
        "subtype": "drink",
        "effect": {"heal": 10, "buff": {"type": "con", "value": 2, "duration": 600}},
        "value": 10,
        "location": "Bar Overflow",
    },
    "memory_leak": {
        "key": "Memory Leak",
        "desc": "House special. You won't remember drinking it, which is probably for the best. Side effects may include temporary amnesia and poetry.",
        "type": "consumable",
        "subtype": "drink",
        "effect": {"heal": 25, "debuff": {"type": "int", "value": -2, "duration": 600}},
        "value": 15,
        "location": "Bar Overflow",
    },

    # Medical
    "medkit_expired": {
        "key": "Expired Medkit",
        "desc": "Best before 2089. Contains bandages, antiseptic, and prayers. 20% chance of infection, 80% chance of survival.",
        "type": "consumable",
        "subtype": "medical",
        "effect": {"heal": 30, "infection_chance": 20},
        "value": 20,
        "location": "Underground Clinic",
    },
    "stim_pack": {
        "key": "Stim Pack",
        "desc": "Military-grade adrenaline cocktail. Makes you feel invincible for 60 seconds. The crash afterwards is your problem.",
        "type": "consumable",
        "subtype": "medical",
        "effect": {"buff": {"type": "all_stats", "value": 3, "duration": 60}},
        "value": 35,
        "location": "Underground Clinic",
    },
    "synth_blood": {
        "key": "Synth-Blood Pack",
        "desc": "Universal synthetic blood. Type O-Negative-Whatever. Dr. Splice's special blend - don't ask what's in it.",
        "type": "consumable",
        "subtype": "medical",
        "effect": {"heal": 50},
        "value": 45,
        "location": "Underground Clinic",
    },
}

IMPLANTS = {
    "optical_enhancer": {
        "key": "Optical Enhancer v1.2",
        "desc": "Budget cybereye upgrade. Adds night vision and a HUD. Minor side effects include seeing dead pixels and the occasional BSOD.",
        "type": "implant",
        "slot": "eyes",
        "bonus": {"perception": 2, "accuracy": 5},
        "cyber_cost": 5,
        "value": 100,
        "location": "Underground Clinic",
    },
    "reflex_booster": {
        "key": "Reflex Booster",
        "desc": "Spinal implant that shortcuts your nervous system. React faster than you can think. Thinking is overrated anyway.",
        "type": "implant",
        "slot": "spine",
        "bonus": {"dex": 3, "initiative": 10},
        "cyber_cost": 10,
        "value": 200,
        "location": "Underground Clinic",
    },
    "dermal_armor": {
        "key": "Dermal Armor Plating",
        "desc": "Subdermal steel mesh. Makes you harder to kill but impossible to hug. Social life not included.",
        "type": "implant",
        "slot": "skin",
        "bonus": {"armor": 5, "charisma": -1},
        "cyber_cost": 8,
        "value": 150,
        "location": "Underground Clinic",
    },
    "neural_link": {
        "key": "Basic Neural Link",
        "desc": "Direct brain-computer interface. Required for hacking. Warning: Do not use near strong magnets or angry AIs.",
        "type": "implant",
        "slot": "head",
        "bonus": {"hacking": 10, "int": 1},
        "cyber_cost": 12,
        "value": 250,
        "location": "Dead Server Room",
    },
    "chrome_arm": {
        "key": "Chrome Arm (Left)",
        "desc": "Full cybernetic arm replacement. Grip strength: yes. Fingerprints: no. Warranty: void.",
        "type": "implant",
        "slot": "left_arm",
        "bonus": {"str": 4, "melee_damage": 3},
        "cyber_cost": 15,
        "value": 300,
        "location": "Chrome Lair",
    },
}

QUEST_ITEMS = {
    "corrupted_chip": {
        "key": "Corrupted Data Chip",
        "desc": "A data chip salvaged from the Dead Server Room. The data is scrambled but someone might pay to unscramble it. Or kill for it.",
        "type": "quest",
        "quest": "dr_splice_quest",
        "value": 0,
        "location": "Dead Server Room",
    },
    "chrome_badge": {
        "key": "Chrome Gang Badge",
        "desc": "A metallic badge marking you as Chrome territory-approved. Or a really good fake. The Chromes don't appreciate fakes.",
        "type": "quest",
        "quest": "chrome_initiation",
        "value": 0,
        "location": None,  # Dropped by Chrome NPCs
    },
    "ghost_token": {
        "key": "Ghost Token",
        "desc": "A blank crypto token used by the Ghosts for anonymous transactions. Untraceable. Invaluable. Definitely stolen.",
        "type": "quest",
        "quest": "ghost_network",
        "value": 0,
        "location": "Forgotten Tunnel",
    },
    "temple_offering": {
        "key": "Vintage Hardware Wallet",
        "desc": "An ancient Ledger Nano from the 2020s. The seed phrase is long lost, but the temples consider it a holy relic.",
        "type": "quest",
        "quest": "temple_blessing",
        "value": 50,
        "location": "Abandoned Terminal",
    },
}

LOOT = {
    # Mob drops
    "copper_wire": {
        "key": "Copper Wire Bundle",
        "desc": "A tangle of copper wires salvaged from ancient infrastructure. The rats use these as currency. So do the desperate.",
        "type": "loot",
        "value": 2,
        "drop_from": ["Mech Rat"],
    },
    "spent_battery": {
        "key": "Spent Battery",
        "desc": "A depleted power cell from a surveillance drone. Still has 3% charge. Enough to power a small lamp or a big regret.",
        "type": "loot",
        "value": 3,
        "drop_from": ["Broken Drone"],
    },
    "scrap_metal": {
        "key": "Scrap Metal",
        "desc": "Assorted metal scraps. One person's trash is another person's weapon/armor/dinner plate.",
        "type": "loot",
        "value": 1,
        "drop_from": ["Mech Rat", "Broken Drone"],
    },
    "circuit_board": {
        "key": "Fried Circuit Board",
        "desc": "A circuit board with visible burn marks. Might be salvageable. Might also explode. Only one way to find out.",
        "type": "loot",
        "value": 5,
        "drop_from": ["Broken Drone"],
    },
    "rat_tail": {
        "key": "Mech Rat Tail",
        "desc": "A cybernetic rat tail, still twitching. Some believe it brings luck. Others use it as a whip. Both are valid.",
        "type": "loot",
        "value": 4,
        "drop_from": ["Mech Rat"],
    },
}

CURRENCY = {
    "abyss_coin": {
        "key": "$ABYSS",
        "desc": "The unofficial currency of the underground. Worth exactly what someone is willing to pay. Currently: not much.",
        "type": "currency",
        "stackable": True,
    },
}

MISC = {
    "cigarettes": {
        "key": "Pack of Synth Cigarettes",
        "desc": "Artificial tobacco that's somehow worse for you than the real thing. Popular barter item. Comes in flavors: Despair and Mint Despair.",
        "type": "misc",
        "value": 5,
        "location": "Bar Overflow",
    },
    "holo_dice": {
        "key": "Holographic Dice",
        "desc": "Dice that project random numbers. Definitely not weighted. The Arena uses these for 'fair' gambling.",
        "type": "misc",
        "value": 10,
        "location": "The Arena",
    },
    "fake_id": {
        "key": "Fake ID Chip",
        "desc": "An identity chip with someone else's credentials. Quality: questionable. Usefulness: depends on how desperate you are.",
        "type": "misc",
        "value": 30,
        "location": "Black Market Plaza",
    },
    "old_photo": {
        "key": "Faded Photograph",
        "desc": "A photo of people who probably don't exist anymore. Someone's memory. Someone's loss. Worth nothing. Priceless.",
        "type": "misc",
        "value": 0,
        "location": "Water Tank",
    },
}

# Combine all items
ALL_ITEMS = {
    **WEAPONS,
    **CONSUMABLES,
    **IMPLANTS,
    **QUEST_ITEMS,
    **LOOT,
    **MISC,
}


def create_items(caller):
    """Create starter items in The Abyss."""
    caller.msg("Creating items for The Abyss...")
    created = 0

    for item_key, item_data in ALL_ITEMS.items():
        location_name = item_data.get("location")
        if not location_name:
            continue

        location = search_object(location_name)
        if not location:
            caller.msg(f"  ERROR: Room not found for {item_data['key']} -> {location_name}")
            continue
        location = location[0]

        # Check if item already exists in location
        existing = [obj for obj in location.contents if obj.key == item_data["key"]]
        if existing:
            caller.msg(f"  {item_data['key']} already exists, skipping...")
            continue

        # Create item
        item = create_object(
            "typeclasses.objects.Object",
            key=item_data["key"],
            location=location
        )
        item.db.desc = item_data["desc"]
        item.db.item_type = item_data.get("type", "misc")
        item.db.value = item_data.get("value", 0)

        # Set type-specific attributes
        if item_data.get("subtype"):
            item.db.subtype = item_data["subtype"]
        if item_data.get("damage"):
            item.db.damage = item_data["damage"]
        if item_data.get("effect"):
            item.db.effect = item_data["effect"]
        if item_data.get("durability"):
            item.db.durability = item_data["durability"]
            item.db.max_durability = item_data["durability"]
        if item_data.get("bonus"):
            item.db.bonus = item_data["bonus"]
        if item_data.get("cyber_cost"):
            item.db.cyber_cost = item_data["cyber_cost"]
        if item_data.get("slot"):
            item.db.slot = item_data["slot"]

        caller.msg(f"  Created: {item_data['key']} in {location_name}")
        created += 1

    caller.msg(f"\nTotal items created: {created}")
    return created


def remove_items(caller):
    """Remove all Abyss items."""
    caller.msg("Removing items...")
    removed = 0
    for item_key, item_data in ALL_ITEMS.items():
        existing = search_object(item_data["key"])
        for item in existing:
            if hasattr(item, 'db') and getattr(item.db, 'item_type', None):
                item.delete()
                caller.msg(f"  Removed: {item_data['key']}")
                removed += 1
    caller.msg(f"Total removed: {removed}")


def list_items():
    """Print all items by category."""
    categories = [
        ("WEAPONS", WEAPONS),
        ("CONSUMABLES", CONSUMABLES),
        ("IMPLANTS", IMPLANTS),
        ("QUEST ITEMS", QUEST_ITEMS),
        ("LOOT", LOOT),
        ("MISC", MISC),
    ]

    for cat_name, cat_items in categories:
        print(f"\n=== {cat_name} ===")
        for key, data in cat_items.items():
            value = data.get('value', 0)
            print(f"  {data['key']} - ${value} ABYSS")
