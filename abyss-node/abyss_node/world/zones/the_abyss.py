"""
The Abyss - First zone of Abyss Node
Cyberpunk undercity with dark humor

Run with: @py from world.zones.the_abyss import build_the_abyss; build_the_abyss(self)
"""

import json
import os
from evennia import create_object, search_object

# Load ASCII art for rooms
ASCII_ART_PATH = os.path.join(
    os.path.dirname(__file__),
    "..", "..", "..", "artwork", "ascii_art", "all_rooms.json"
)

def load_ascii_art():
    """Load ASCII art from JSON file."""
    try:
        with open(ASCII_ART_PATH, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

ROOMS = {
    "entrance": {
        "key": "Entrance to the Abyss",
        "desc": """A hole in the fractured pavement decorated with a broken neon sign
that reads "WELC ME". The 'O' was stolen years ago. A metal staircase
descends into darkness, each step more rusted than the last. Graffiti
on the wall promises: "No one judges you here (because no one cares)." """,
        "zone": "the_abyss"
    },
    "passage": {
        "key": "Rusted Passage",
        "desc": """A narrow corridor that some architect designed for "efficiency" and
ended up being a tetanus trap. Pipes drip something green that no one
wants to analyze. A broken screen repeats "SYSTEM OFFLINE" since 2089.
Technically it's contemporary art now.""",
        "zone": "the_abyss"
    },
    "alley": {
        "key": "Rat Alley",
        "desc": """A dead-end alley that genetically modified rats have claimed as an
independent republic. They have their own economy based on copper wires.
Graffiti says: "The Ghosts never forget" and someone added below:
"But they do forgive for $ABYSS." """,
        "zone": "the_abyss"
    },
    "tank": {
        "key": "Water Tank",
        "desc": """An industrial tank that promised "clean water for everyone" in 2045.
Now it's an Airbnb for refugees with one-star reviews. Hammocks hang
like metallic spider webs. A family watches you with the hospitality
of those who have already sold everything they could sell.""",
        "zone": "the_abyss"
    },
    "crossing": {
        "key": "Central Crossing",
        "desc": """The heart of the Abyss, where four tunnels converge under a cracked
dome that once held a holographic clock. Now only light fragments
project the wrong time: 99:99. Beggars and dealers exchange glances.
The murmur of illegal transactions fills the air.""",
        "zone": "the_abyss"
    },
    "plaza": {
        "key": "Black Market Plaza",
        "desc": """Capitalism in its purest form: no regulations, no taxes, no warranties.
Stalls sell "slightly used" organs next to tacos of questionable origin.
A corrupted hologram announces deals that expired decades ago. The smell
is indescribable, and that's a compliment.""",
        "zone": "the_abyss"
    },
    "clinic": {
        "key": "Underground Clinic",
        "desc": """You wake up on an operating table that has seen better days (and worse
patients). Dr. Splice looks at you with a mix of professional pride and
personal disappointment. "You survived. I owe you $50 ABYSS, I bet against
you." A sign reads: "Installations and Extractions - Results not guaranteed
but definitely memorable." """,
        "zone": "the_abyss",
        "is_spawn": True
    },
    "terminal": {
        "key": "Abandoned Terminal",
        "desc": """A subway station where the last train passed in 2078. The rusted
wagons now serve as luxury condos (by Abyss standards). A vending
machine keeps trying to sell you a Coca-Cola for $0.99 - inflation
never reached here. The sealed tunnel has radiation warnings that
are probably exaggerated. Probably.""",
        "zone": "the_abyss"
    },
    "lair": {
        "key": "Chrome Lair",
        "desc": """Chrome territory. Here the debate "how much metal makes you stop being
human?" is resolved with violence. Cyborgs plugged into charging towers
scan you with LED eyes. A synthetic voice asks: "Do you come in peace
or in pieces?" It's not a rhetorical question.""",
        "zone": "the_abyss"
    },
    "tunnel": {
        "key": "Forgotten Tunnel",
        "desc": """A maintenance tunnel the system forgot to update, hack, or demolish.
Ghosts use this passage to move without leaving an on-chain trace.
Ancient graffiti shows escape routes that no longer exist and political
promises that were never kept. The smell of dampness is free, like
everything good here.""",
        "zone": "the_abyss"
    },
    "server": {
        "key": "Dead Server Room",
        "desc": """A data graveyard where dead servers blink with residual life. Hackers
come here looking for lost information like digital archaeologists.
The cold is brutal - the cooling systems keep running because no one
remembers how to turn them off. They say the first Bitcoin block was
stored here. It's a lie, but it sells.""",
        "zone": "the_abyss"
    },
    "bar": {
        "key": "Bar Overflow",
        "desc": """A bar named after the bug that founded it (someone hacked an ATM).
The bartender is a robotic arm that mixes drinks with millimetric
precision and zero personality. The clientele includes hackers,
assassins, and accountants - all three equally dangerous. Happy hour
is when there's no shootout.""",
        "zone": "the_abyss"
    },
    "taqueria": {
        "key": "Taqueria The Last Byte",
        "desc": """The best taqueria in the Abyss (and the only one). Dona Kernel serves
synthetic protein tacos that taste suspiciously good. No one asks what
they're made of. The menu has options like "Al Pastor 2.0", "Carnitas
Legacy" and "Bug-Free Suadero". Accepts $ABYSS and barter. Hours are
"whenever Dona Kernel feels like it." """,
        "zone": "the_abyss"
    },
    "arena": {
        "key": "The Arena",
        "desc": """A combat pit where Chromes settle disputes, gamblers lose fortunes,
and gladiators lose limbs. The rules are simple: enter alive, leave
however you can. A sign reads "We are not responsible for damage,
death, or loss of on-chain identity". Entry costs, exit costs more.""",
        "zone": "the_abyss"
    },
    "temple_satoshi": {
        "key": "Temple of Satoshi",
        "desc": """A sanctuary dedicated to the anonymous prophet who created Bitcoin
and vanished. Electric candles flicker in front of a monitor displaying
the whitepaper on loop. The faithful meditate on decentralization while
a monk recites the genesis block. A plaque reads: "In Code We Trust".
Donations in BTC only (obviously).""",
        "zone": "the_abyss",
        "buff": {"type": "luck", "value": 10, "duration": 3600}
    },
    "temple_vitalik": {
        "key": "Temple of Vitalik",
        "desc": """A minimalist space dedicated to the eternal youth who promised the
world computer. Holograms show ETH DevCon conferences on infinite loop.
Devotees debate gas fees and layer 2s as if they were sacred texts.
A poster says "Merge Complete" next to a candle that never goes out.
NFTs here are relics.""",
        "zone": "the_abyss",
        "buff": {"type": "int", "value": 2, "duration": 3600}
    },
    "temple_toly": {
        "key": "Temple of Toly",
        "desc": """The newest of the temples, dedicated to the architect of Solana.
Everything here is FAST. The monks speak in TPS. A clock shows latency
in milliseconds. "Move Fast Break Things" posters adorn the walls next
to monkey memes. The temple crashed three times during construction
but "it's stable now" (they say).""",
        "zone": "the_abyss",
        "buff": {"type": "dex", "value": 15, "duration": 1800, "unreliable": True}
    },
    "stairs": {
        "key": "Stairs to Crimson District",
        "desc": """An emergency staircase leading to the Crimson District, where life
is expensive but at least there's natural (artificial) light. A Chrome
guard blocks the way. "Got 100 $ABYSS? No. Then come back when you have
something to offer besides hope." Music and laughter from people who
can afford them filter down from above.""",
        "zone": "the_abyss",
        "locked": True,
        "unlock_cost": 100
    }
}

EXITS = [
    ("entrance", "north", "passage"),
    ("entrance", "south", "stairs"),
    ("passage", "south", "entrance"),
    ("passage", "north", "crossing"),
    ("passage", "east", "tank"),
    ("passage", "west", "alley"),
    ("alley", "east", "passage"),
    ("tank", "west", "passage"),
    ("crossing", "south", "passage"),
    ("crossing", "north", "plaza"),
    ("crossing", "east", "terminal"),
    ("crossing", "west", "lair"),
    ("crossing", "down", "taqueria"),
    ("plaza", "south", "crossing"),
    ("plaza", "east", "clinic"),
    ("plaza", "west", "tunnel"),
    ("plaza", "north", "temple_toly"),
    ("clinic", "west", "plaza"),
    ("terminal", "west", "crossing"),
    ("terminal", "down", "bar"),
    ("bar", "up", "terminal"),
    ("taqueria", "up", "crossing"),
    ("lair", "east", "crossing"),
    ("lair", "south", "arena"),
    ("arena", "north", "lair"),
    ("tunnel", "east", "plaza"),
    ("temple_toly", "south", "plaza"),
    ("temple_toly", "north", "server"),
    ("server", "south", "temple_toly"),
    ("server", "west", "temple_satoshi"),
    ("server", "east", "temple_vitalik"),
    ("temple_satoshi", "east", "server"),
    ("temple_vitalik", "west", "server"),
    ("stairs", "north", "entrance"),
]


def build_the_abyss(caller):
    """Build The Abyss zone."""
    caller.msg("Building The Abyss...")

    # Load ASCII art
    ascii_art_data = load_ascii_art()
    if ascii_art_data:
        caller.msg(f"  Loaded ASCII art for {len(ascii_art_data)} rooms")
    else:
        caller.msg("  WARNING: No ASCII art found")

    created_rooms = {}
    for room_key, room_data in ROOMS.items():
        existing = search_object(room_data["key"], typeclass="typeclasses.rooms.Room")
        if existing:
            caller.msg(f"  Room '{room_data['key']}' exists, updating ASCII art...")
            room = existing[0]
            # Update ASCII art for existing rooms
            if room_key in ascii_art_data:
                room.db.ascii_art = ascii_art_data[room_key].get("ascii", "")
            created_rooms[room_key] = room
            continue

        room = create_object("typeclasses.rooms.Room", key=room_data["key"])
        room.db.desc = room_data["desc"]
        room.db.zone = room_data.get("zone", "the_abyss")

        # Add ASCII art
        if room_key in ascii_art_data:
            room.db.ascii_art = ascii_art_data[room_key].get("ascii", "")

        if room_data.get("is_spawn"):
            room.db.is_spawn = True
        if room_data.get("buff"):
            room.db.buff = room_data["buff"]
        if room_data.get("locked"):
            room.db.locked = True
            room.db.unlock_cost = room_data.get("unlock_cost", 100)

        created_rooms[room_key] = room
        caller.msg(f"  Created: {room_data['key']}")

    for from_room, direction, to_room in EXITS:
        if from_room not in created_rooms or to_room not in created_rooms:
            continue

        from_room_obj = created_rooms[from_room]
        existing_exit = [ex for ex in from_room_obj.exits if ex.key == direction]
        if existing_exit:
            continue

        create_object(
            "typeclasses.exits.Exit",
            key=direction,
            location=created_rooms[from_room],
            destination=created_rooms[to_room]
        )
        caller.msg(f"  Exit: {from_room} --{direction}--> {to_room}")

    caller.msg(f"\nThe Abyss built! Rooms: {len(created_rooms)}")
    return created_rooms


def destroy_the_abyss(caller):
    """Remove all Abyss rooms."""
    caller.msg("Destroying The Abyss...")
    for room_key, room_data in ROOMS.items():
        existing = search_object(room_data["key"], typeclass="typeclasses.rooms.Room")
        for room in existing:
            for exit_obj in room.exits:
                exit_obj.delete()
            room.delete()
            caller.msg(f"  Deleted: {room_data['key']}")
    caller.msg("The Abyss destroyed.")


def update_ascii_art(caller):
    """Update ASCII art for all existing Abyss rooms."""
    caller.msg("Updating ASCII art for The Abyss...")

    ascii_art_data = load_ascii_art()
    if not ascii_art_data:
        caller.msg("ERROR: Could not load ASCII art")
        return

    updated = 0
    for room_key, room_data in ROOMS.items():
        existing = search_object(room_data["key"], typeclass="typeclasses.rooms.Room")
        for room in existing:
            if room_key in ascii_art_data:
                room.db.ascii_art = ascii_art_data[room_key].get("ascii", "")
                caller.msg(f"  Updated: {room_data['key']}")
                updated += 1

    caller.msg(f"ASCII art updated for {updated} rooms.")
