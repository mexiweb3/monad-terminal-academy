"""
Room Image Prompts for The Abyss
Cyberpunk MUD - Visual Assets

Style: Dark cyberpunk, neon accents, dystopian atmosphere
Palette: Deep blacks, electric blues, hot pinks, toxic greens, chrome silvers

Run: python room_prompts.py (requires GEMINI_API_KEY environment variable)
"""

import os
import json

# Consistent style suffix for all prompts
STYLE = """
Digital art, cyberpunk aesthetic, dark atmospheric lighting,
neon glow effects, dystopian future, highly detailed,
cinematic composition, 16:9 aspect ratio, concept art style,
Blade Runner meets Akira visual influence
"""

# Color palettes for different room types
PALETTES = {
    "spawn": "warm orange and clinical white with blood red accents",
    "market": "chaotic mix of neon signs - pink, blue, green, yellow",
    "bar": "deep blue and purple with amber drink glow",
    "temple": "ethereal cyan and gold with digital artifacts",
    "industrial": "rust orange, toxic green, warning yellow",
    "residential": "dim warm lights against cold steel blue",
    "combat": "aggressive red and chrome silver",
    "underground": "bioluminescent green and damp grey",
}

ROOM_PROMPTS = {
    "entrance": {
        "name": "Entrance to the Abyss",
        "prompt": f"""
A broken hole in cracked concrete pavement leading down into darkness.
A damaged neon sign reads "WELC ME" with the O missing, flickering pink and blue.
Rusty metal staircase descending into shadow. Graffiti on walls.
Urban decay meets cyberpunk underground entrance.
Colors: {PALETTES['industrial']}
{STYLE}
""",
        "colors": ["#FF6B35", "#1A1A2E", "#16213E", "#E94560"]
    },

    "passage": {
        "name": "Rusted Passage",
        "prompt": f"""
Narrow industrial corridor with exposed pipes dripping green liquid.
Tetanus-inducing rusty metal walls. Broken screen displaying "SYSTEM OFFLINE".
Steam vents and flickering fluorescent lights. Claustrophobic atmosphere.
Colors: {PALETTES['industrial']}
{STYLE}
""",
        "colors": ["#2D3436", "#00B894", "#FDCB6E", "#E17055"]
    },

    "alley": {
        "name": "Rat Alley",
        "prompt": f"""
Dead-end alley filled with electronic waste and copper wires.
Giant cybernetic rats with glowing red LED eyes lurking in shadows.
Graffiti reads "The Ghosts never forget". Bioluminescent fungi on walls.
Garbage and cables everywhere. Dark and menacing atmosphere.
Colors: {PALETTES['underground']}
{STYLE}
""",
        "colors": ["#0F0F0F", "#00FF41", "#FF0040", "#4A4A4A"]
    },

    "tank": {
        "name": "Water Tank",
        "prompt": f"""
Massive industrial water tank converted into makeshift housing.
Hammocks and sleeping pods hanging like spider webs inside metal cylinder.
Faded "CLEAN WATER FOR ALL 2045" propaganda poster. Refugees' belongings.
Warm dim lights against cold industrial metal. Desperate but human.
Colors: {PALETTES['residential']}
{STYLE}
""",
        "colors": ["#2C3E50", "#E67E22", "#95A5A6", "#3498DB"]
    },

    "crossing": {
        "name": "Central Crossing",
        "prompt": f"""
Underground intersection where four tunnels meet under a cracked dome.
Broken holographic clock projecting "99:99" in glitchy cyan light.
Dealers and beggars in shadows. Multiple neon signs pointing different directions.
Heart of the underground. Busy, dangerous, alive with activity.
Colors: {PALETTES['market']}
{STYLE}
""",
        "colors": ["#9B59B6", "#3498DB", "#E74C3C", "#2ECC71"]
    },

    "plaza": {
        "name": "Black Market Plaza",
        "prompt": f"""
Chaotic underground marketplace with illegal goods on display.
Organ jars next to food stalls. Corrupted hologram advertisements.
Neon signs in multiple languages. Dense crowd of shady characters.
Cyberpunk bazaar atmosphere. Capitalism without rules.
Colors: {PALETTES['market']}
{STYLE}
""",
        "colors": ["#FF1493", "#00FFFF", "#FFD700", "#32CD32"]
    },

    "clinic": {
        "name": "Underground Clinic",
        "prompt": f"""
Illegal cybernetic surgery clinic. Operating table with blood stains.
Medical equipment mixed with hacking tools. Jars with implants.
Dr. Splice's workspace - professional chaos. Sign reads "Results not guaranteed".
Clinical white mixed with warning red and chrome medical equipment.
Colors: {PALETTES['spawn']}
{STYLE}
""",
        "colors": ["#FFFFFF", "#FF0000", "#C0C0C0", "#FF6600"]
    },

    "terminal": {
        "name": "Abandoned Terminal",
        "prompt": f"""
Derelict subway station frozen in time since 2078. Rusted train cars.
Vending machine still glowing, offering Coca-Cola for $0.99.
Radiation warning signs near sealed tunnel. Dust and decay everywhere.
Retrofuturism meets post-apocalypse. Nostalgic yet dangerous.
Colors: {PALETTES['industrial']}
{STYLE}
""",
        "colors": ["#8B4513", "#FFD700", "#FF4500", "#808080"]
    },

    "lair": {
        "name": "Chrome Lair",
        "prompt": f"""
Cyborg gang headquarters. Charging towers with humanoids plugged in.
Chrome and steel everywhere. Red LED eyes scanning. Industrial aesthetics.
"ARE YOU HUMAN?" graffiti. Aggressive, territorial, mechanical.
Heavy metal meets flesh. Dehumanization visualized.
Colors: {PALETTES['combat']}
{STYLE}
""",
        "colors": ["#C0C0C0", "#FF0000", "#1C1C1C", "#4169E1"]
    },

    "tunnel": {
        "name": "Forgotten Tunnel",
        "prompt": f"""
Abandoned maintenance tunnel. Damp, dark, forgotten by the system.
Old political graffiti and escape route maps. Dripping water.
Perfect for ghosts who want to stay invisible. Off-grid passage.
Organic decay in mechanical space. Nature reclaiming technology.
Colors: {PALETTES['underground']}
{STYLE}
""",
        "colors": ["#2F4F4F", "#00CED1", "#556B2F", "#708090"]
    },

    "server": {
        "name": "Dead Server Room",
        "prompt": f"""
Massive data center graveyard. Dead servers with blinking residual lights.
Intense cold - frost on surfaces. Blue LED glow from dying machines.
Digital archaeologists' heaven. Ghost data and lost secrets.
Cathedral of dead technology. Reverent silence.
Colors: {PALETTES['temple']}
{STYLE}
""",
        "colors": ["#0000CD", "#00BFFF", "#F0F8FF", "#483D8B"]
    },

    "bar": {
        "name": "Bar Overflow",
        "prompt": f"""
Underground hacker bar. Single robotic arm as bartender behind counter.
Drink menu in code. Clientele of hackers, assassins, accountants.
Dark wood and chrome. Amber liquid glow. No questions asked.
Digital noir atmosphere. Dangerous but welcoming.
Colors: {PALETTES['bar']}
{STYLE}
""",
        "colors": ["#4B0082", "#FF8C00", "#191970", "#DAA520"]
    },

    "taqueria": {
        "name": "Taqueria The Last Byte",
        "prompt": f"""
Cozy underground taqueria. Warm orange lights. Mechanical arms cooking.
Menu board with items like "Al Pastor 2.0" and "Carnitas Legacy".
Dona Kernel's domain - maternal but dangerous. Smells delicious.
Home in the underground. Comfort food meets cyberpunk.
Colors: {PALETTES['residential']}
{STYLE}
""",
        "colors": ["#FF6347", "#FFD700", "#8B4513", "#FFA500"]
    },

    "arena": {
        "name": "The Arena",
        "prompt": f"""
Underground gladiatorial combat pit. Blood-stained fighting ring.
Spectator seats around circular arena. Betting boards with odds.
Chrome fighters and organic ones. Victory or death atmosphere.
Roman colosseum meets robot wars. Brutal entertainment.
Colors: {PALETTES['combat']}
{STYLE}
""",
        "colors": ["#8B0000", "#C0C0C0", "#000000", "#FFD700"]
    },

    "temple_satoshi": {
        "name": "Temple of Satoshi",
        "prompt": f"""
Sacred shrine to Bitcoin's anonymous creator. Electric candles flickering.
Monitor displaying the whitepaper on eternal loop. Gold and cyan glow.
Monks in hooded robes meditating on decentralization. Genesis block carved in stone.
"IN CODE WE TRUST" plaque. Religious reverence for cryptocurrency.
Colors: {PALETTES['temple']}
{STYLE}
""",
        "colors": ["#FFD700", "#00CED1", "#1C1C1C", "#F0E68C"]
    },

    "temple_vitalik": {
        "name": "Temple of Vitalik",
        "prompt": f"""
Minimalist shrine to Ethereum's creator. Holographic DevCon presentations.
Purple and silver aesthetic. NFT relics on pedestals. Gas fee debate murals.
"MERGE COMPLETE" poster with eternal flame. Smart contract scripture.
Modern tech temple. Intellectual worship of the world computer.
Colors: {PALETTES['temple']}
{STYLE}
""",
        "colors": ["#627EEA", "#C0C0C0", "#9B59B6", "#2ECC71"]
    },

    "temple_toly": {
        "name": "Temple of Toly",
        "prompt": f"""
Newest crypto temple, dedicated to Solana's architect. Everything is FAST.
TPS counters and latency clocks. Monkey meme art on walls.
"MOVE FAST BREAK THINGS" banners. Temple crashed during construction (joke).
Speed worship. Chaotic energy. Young and brash aesthetic.
Colors: {PALETTES['temple']}
{STYLE}
""",
        "colors": ["#14F195", "#9945FF", "#000000", "#FFFFFF"]
    },

    "stairs": {
        "name": "Stairs to Crimson District",
        "prompt": f"""
Emergency staircase leading up to light. Chrome guard blocking the way.
"100 $ABYSS" price tag glowing. Music and laughter filtering from above.
Transition from dark underground to bright upper world. Class barrier visualized.
Hope and despair at the threshold. So close yet so far.
Colors: {PALETTES['market']}
{STYLE}
""",
        "colors": ["#DC143C", "#FFD700", "#1C1C1C", "#FFFAF0"]
    }
}


def generate_images():
    """Generate images using Google Gemini API."""
    try:
        import google.generativeai as genai
    except ImportError:
        print("Install google-generativeai: pip install google-generativeai")
        return

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Set GEMINI_API_KEY environment variable")
        return

    genai.configure(api_key=api_key)

    # Use Imagen 3 for image generation
    model = genai.ImageGenerationModel("imagen-3.0-generate-002")

    output_dir = os.path.dirname(os.path.abspath(__file__)) + "/rooms"
    os.makedirs(output_dir, exist_ok=True)

    for room_key, room_data in ROOM_PROMPTS.items():
        print(f"Generating: {room_data['name']}...")
        try:
            result = model.generate_images(
                prompt=room_data["prompt"],
                number_of_images=1,
                aspect_ratio="16:9",
                safety_filter_level="block_only_high",
            )

            for i, image in enumerate(result.images):
                filename = f"{output_dir}/{room_key}.png"
                image._pil_image.save(filename)
                print(f"  Saved: {filename}")

        except Exception as e:
            print(f"  Error: {e}")

    print("\nDone! Images saved to artwork/rooms/")


def export_prompts_json():
    """Export prompts to JSON for external use."""
    output = {
        "style_guide": STYLE,
        "palettes": PALETTES,
        "rooms": ROOM_PROMPTS
    }

    output_path = os.path.dirname(os.path.abspath(__file__)) + "/room_prompts.json"
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)
    print(f"Exported to: {output_path}")


def print_prompts():
    """Print all prompts for manual use."""
    print("=" * 60)
    print("ROOM IMAGE PROMPTS - THE ABYSS")
    print("=" * 60)

    for room_key, room_data in ROOM_PROMPTS.items():
        print(f"\n### {room_data['name'].upper()} ###")
        print(f"Colors: {', '.join(room_data['colors'])}")
        print("-" * 40)
        print(room_data['prompt'].strip())
        print()


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        if sys.argv[1] == "generate":
            generate_images()
        elif sys.argv[1] == "json":
            export_prompts_json()
        elif sys.argv[1] == "print":
            print_prompts()
        else:
            print("Usage: python room_prompts.py [generate|json|print]")
    else:
        print("Room prompts for The Abyss")
        print(f"Total rooms: {len(ROOM_PROMPTS)}")
        print("\nCommands:")
        print("  python room_prompts.py generate  - Generate images (needs GEMINI_API_KEY)")
        print("  python room_prompts.py json      - Export prompts to JSON")
        print("  python room_prompts.py print     - Print all prompts")
