#!/usr/bin/env python3
"""
Generate NPC portraits using Nano Banana (Google Gemini)
"""

import google.generativeai as genai
import os
import time

API_KEY = "AIzaSyB71bAxGF7x9ciQS4Fk6UEICCtoffjRJkA"
genai.configure(api_key=API_KEY)

model = genai.GenerativeModel("nano-banana-pro-preview")

# NPC portrait prompts - cyberpunk style matching the game aesthetic
npcs = {
    "dr_splice": {
        "name": "Dr. Splice",
        "prompt": "Cyberpunk portrait of a back-alley surgeon, middle-aged man with cybernetic eye implant and neural interface cables, wearing dirty surgical scrubs, cynical expression, neon-lit underground lab background, dark moody lighting with cyan and magenta accents, detailed portrait style"
    },
    "dona_kernel": {
        "name": "Doña Kernel",
        "prompt": "Cyberpunk portrait of an elderly Mexican woman street food vendor, warm maternal face with subtle tech implants, LED-lit food cart in background, wearing apron with holographic menu, steam rising from synthetic protein tacos, neon signs, underground market setting"
    },
    "arm_bartender": {
        "name": "Arm Bartender",
        "prompt": "Cyberpunk portrait of a robotic bartender arm, chrome mechanical limb with multiple joints and tools, mixing drinks with precision, glowing blue LED indicators, abandoned subway bar background, bottles and neon signs, industrial aesthetic"
    },
    "chrome_guard": {
        "name": "Chrome Guard",
        "prompt": "Cyberpunk portrait of a heavily augmented cyborg guard, more machine than human, chrome plating covering most of face, glowing red scanner eyes, intimidating stance, industrial corridor background, steam and neon lighting"
    },
    "mech_rat": {
        "name": "Mech Rat",
        "prompt": "Cyberpunk creature portrait of a genetically modified rat with mechanical enhancements, copper wire fur, LED eyes, metal teeth, scavenged tech parts integrated into body, dark alley setting, gritty and menacing"
    },
    "broken_drone": {
        "name": "Broken Drone",
        "prompt": "Cyberpunk portrait of a damaged security drone, cracked chassis with exposed wiring, one flickering red eye, sparking components, glitchy holographic display, abandoned metro station setting, dust and debris"
    }
}

# Create output directory
output_dir = "/home/davidiego2/Documents/_active/abyss-node/artwork/npcs_nano_banana"
os.makedirs(output_dir, exist_ok=True)

total = len(npcs)

print(f"Generating {total} NPC portraits with Nano Banana...")
print("=" * 50)

for i, (npc_key, npc_data) in enumerate(npcs.items(), 1):
    name = npc_data["name"]
    prompt = npc_data["prompt"]

    output_path = os.path.join(output_dir, f"{npc_key}.png")

    print(f"\n[{i}/{total}] {name}")

    try:
        response = model.generate_content(f"Generate an image: {prompt}")

        # Extract image
        image_saved = False
        for candidate in response.candidates:
            for part in candidate.content.parts:
                if hasattr(part, 'inline_data') and part.inline_data:
                    img_data = part.inline_data.data
                    with open(output_path, "wb") as f:
                        f.write(img_data)
                    print(f"    Saved: {output_path}")
                    image_saved = True
                    break
            if image_saved:
                break

        if not image_saved:
            print(f"    WARNING: No image data in response")

        # Rate limiting - wait between requests
        time.sleep(2)

    except Exception as e:
        print(f"    ERROR: {e}")
        time.sleep(5)  # Wait longer on error

print("\n" + "=" * 50)
print("Done!")
