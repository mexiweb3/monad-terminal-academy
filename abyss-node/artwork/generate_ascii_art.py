#!/usr/bin/env python3
"""
Generate ASCII art for MUD rooms using Nano Banana (Google Gemini)
"""

import google.generativeai as genai
import json
import os
import time

API_KEY = "AIzaSyB71bAxGF7x9ciQS4Fk6UEICCtoffjRJkA"
genai.configure(api_key=API_KEY)

model = genai.GenerativeModel("nano-banana-pro-preview")

# Room descriptions for ASCII art
rooms = {
    "entrance": {
        "name": "Entrance to the Abyss",
        "desc": "A hole in the pavement with a broken neon sign saying 'WELCO E' (M was stolen). Rusty metal staircase descends into darkness. Graffiti: 'Here nobody judges you (because nobody cares)'."
    },
    "passage": {
        "name": "Rusted Passage",
        "desc": "A corridor designed for 'efficiency' that became a tetanus trap. Pipes leak green fluid. A broken screen repeats 'SYSTEM OFFLINE' since 2089."
    },
    "alley": {
        "name": "Rat Alley",
        "desc": "A dead-end alley claimed by genetically modified rats as an independent republic. They have their own copper-wire economy. Graffiti: 'Ghosts don't forget'."
    },
    "tank": {
        "name": "Water Tank",
        "desc": "Industrial tank that promised 'potable water for all' in 2045. Now an Airbnb for refugees. Hammocks hang like metallic spider webs."
    },
    "crossing": {
        "name": "Central Crossing",
        "desc": "Heart of the Abyss where four tunnels converge under a holographic clock stuck at 99:99. Dealers sell dreams on credit. Beggars accept crypto."
    },
    "plaza": {
        "name": "Black Market Plaza",
        "desc": "Pure capitalism: no regulations, no taxes, no guarantees. Stalls sell 'slightly used' organs next to questionable tacos. Corrupted hologram announces expired offers."
    },
    "clinic": {
        "name": "Underground Clinic",
        "desc": "Operating table that has seen better days. Dr. Splice does implants and extractions. Sign: 'Results not guaranteed but memorable'. SPAWN POINT."
    },
    "terminal": {
        "name": "Abandoned Terminal",
        "desc": "Metro station where the last train passed in 2078. Wagons are now luxury condos (by Abyss standards). Vending machine still selling Coke for $0.99."
    },
    "lair": {
        "name": "Chrome Lair",
        "desc": "Chrome territory. Cyborgs plugged into charging towers scan you with LED eyes. A synthetic voice asks: 'Peace or pieces?' Not rhetorical."
    },
    "tunnel": {
        "name": "Forgotten Tunnel",
        "desc": "Maintenance tunnel the system forgot. Ghosts use it to move without leaving on-chain traces. Old graffiti shows escape routes that no longer exist."
    },
    "server": {
        "name": "Dead Server Room",
        "desc": "Data cemetery where dead servers blink with residual life. Hackers come seeking lost information like digital archaeologists. Freezing cold."
    },
    "bar": {
        "name": "Bar Overflow",
        "desc": "Bar named after the bug that founded it (someone hacked an ATM). Bartender is a robotic arm mixing drinks with precision and zero personality."
    },
    "taqueria": {
        "name": "Taqueria El Ultimo Byte",
        "desc": "Best taqueria in the Abyss (and only one). Dona Kernel serves synthetic protein tacos that taste suspiciously good. Menu: 'Pastor 2.0', 'Carnitas Legacy'."
    },
    "arena": {
        "name": "The Arena",
        "desc": "Combat pit where Chromes settle disputes, gamblers lose fortunes, gladiators lose limbs. Rules: enter alive, exit as you can. Entry costs, exit costs more."
    },
    "temple_satoshi": {
        "name": "Temple of Satoshi",
        "desc": "Sanctuary dedicated to the anonymous prophet who created Bitcoin. Electric candles flicker before a monitor showing the whitepaper on loop. 'In Code We Trust'."
    },
    "temple_vitalik": {
        "name": "Temple of Vitalik",
        "desc": "Minimalist space dedicated to the eternal youth who promised the world computer. Holograms show ETH DevCon conferences. Devotees debate gas fees."
    },
    "temple_toly": {
        "name": "Temple of Toly",
        "desc": "Newest temple, dedicated to Solana's architect. Everything is FAST. Monks speak in TPS. Clock shows latency in milliseconds. 'Move Fast Break Things' posters."
    },
    "stairs": {
        "name": "Stairs to Crimson District",
        "desc": "Emergency staircase to Crimson District where life is expensive but has artificial natural light. Chrome guard blocks: 'Got 100 $ABYSS? No? Come back when you have something.'"
    }
}

# Create output directory
output_dir = "/home/davidiego2/Documents/_active/abyss-node/artwork/ascii_art"
os.makedirs(output_dir, exist_ok=True)

total = len(rooms)

print(f"Generating ASCII art for {total} rooms...")
print("=" * 60)

ascii_collection = {}

for i, (room_key, room_data) in enumerate(rooms.items(), 1):
    name = room_data["name"]
    desc = room_data["desc"]

    print(f"\n[{i}/{total}] {name}")

    prompt = f"""Create ASCII art for a text-based MUD game room called "{name}".

Description: {desc}

Requirements:
- Pure ASCII characters only (no unicode, no emojis)
- Width: 60-70 characters max
- Height: 12-18 lines
- Cyberpunk/underground aesthetic
- Include key visual elements from the description
- Make it atmospheric and moody

Output ONLY the ASCII art, nothing else. No explanations, no markdown."""

    try:
        response = model.generate_content(prompt)

        if response.text:
            ascii_art = response.text.strip()
            ascii_collection[room_key] = {
                "name": name,
                "ascii": ascii_art
            }

            # Save individual file
            output_path = os.path.join(output_dir, f"{room_key}.txt")
            with open(output_path, "w") as f:
                f.write(f"# {name}\n\n")
                f.write(ascii_art)

            print(f"    Saved: {output_path}")
            # Show preview (first 5 lines)
            lines = ascii_art.split('\n')[:5]
            for line in lines:
                print(f"    {line[:60]}")
            if len(ascii_art.split('\n')) > 5:
                print("    ...")
        else:
            print(f"    WARNING: No text response")

        # Rate limiting
        time.sleep(2)

    except Exception as e:
        print(f"    ERROR: {e}")
        time.sleep(5)

# Save all ASCII art to a single JSON file
json_path = os.path.join(output_dir, "all_rooms.json")
with open(json_path, "w") as f:
    json.dump(ascii_collection, f, indent=2)

print(f"\n\nAll ASCII art saved to: {json_path}")
print("=" * 60)
print("Done!")
