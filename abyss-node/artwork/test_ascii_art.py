#!/usr/bin/env python3
"""
Test if Nano Banana can generate ASCII art for MUD rooms
"""

import google.generativeai as genai

API_KEY = "AIzaSyB71bAxGF7x9ciQS4Fk6UEICCtoffjRJkA"
genai.configure(api_key=API_KEY)

model = genai.GenerativeModel("nano-banana-pro-preview")

# Test with one room - Entrance to the Abyss
prompt = """Create ASCII art for a text-based MUD game room. The room is:

"Entrance to the Abyss" - A hole in the pavement decorated with a broken neon sign
that says "WELCO E" (the M was stolen years ago). A rusty metal staircase descends
into darkness. Graffiti promises: "Here nobody judges you (because nobody cares)".

Requirements:
- Pure ASCII characters only (no unicode)
- Width: 60-70 characters max
- Height: 15-20 lines
- Cyberpunk/underground aesthetic
- Include the broken neon sign
- Show the descending staircase

Output ONLY the ASCII art, no explanations."""

print("Testing Nano Banana ASCII art generation...")
print("=" * 60)

try:
    response = model.generate_content(prompt)

    # Get the text response
    if response.text:
        print("\nGenerated ASCII art:\n")
        print(response.text)
    else:
        print("No text response received")

except Exception as e:
    print(f"ERROR: {e}")

print("\n" + "=" * 60)
