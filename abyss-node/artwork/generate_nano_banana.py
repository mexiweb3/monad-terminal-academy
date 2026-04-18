#!/usr/bin/env python3
"""
Generate room images using Nano Banana (Google Gemini)
"""

import google.generativeai as genai
import json
import os
import time

API_KEY = "AIzaSyB71bAxGF7x9ciQS4Fk6UEICCtoffjRJkA"
genai.configure(api_key=API_KEY)

model = genai.GenerativeModel("nano-banana-pro-preview")

# Load prompts
with open("/home/davidiego2/Documents/_active/abyss-node/artwork/room_prompts.json") as f:
    data = json.load(f)

# Create output directory
output_dir = "/home/davidiego2/Documents/_active/abyss-node/artwork/rooms_nano_banana"
os.makedirs(output_dir, exist_ok=True)

rooms = data["rooms"]
total = len(rooms)

print(f"Generating {total} room images with Nano Banana...")
print("=" * 50)

for i, (room_key, room_data) in enumerate(rooms.items(), 1):
    name = room_data["name"]
    prompt = room_data["prompt"]

    output_path = os.path.join(output_dir, f"{room_key}.jpg")

    print(f"\n[{i}/{total}] {name}")

    try:
        response = model.generate_content(f"Generate an image: {prompt}")

        # Extract image
        for candidate in response.candidates:
            for part in candidate.content.parts:
                if hasattr(part, 'inline_data') and part.inline_data:
                    img_data = part.inline_data.data
                    with open(output_path, "wb") as f:
                        f.write(img_data)
                    print(f"    Saved: {output_path}")
                    break

        # Rate limiting - wait between requests
        time.sleep(2)

    except Exception as e:
        print(f"    ERROR: {e}")
        time.sleep(5)  # Wait longer on error

print("\n" + "=" * 50)
print("Done!")
