# CLAUDE.md - Abyss Node

Cyberpunk MUD built with Evennia. Set in 2111 Neo-Withmore: megacorps, hackers, robots, and $ABYSS crypto economy.

## Quick Start

```bash
cd abyss_node
source ../.venv/bin/activate
evennia start      # Start server
evennia stop       # Stop server
evennia reload     # Reload after code changes
```

**Ports:**
- Telnet: `localhost:4000`
- Web: `http://localhost:4001`

## Project Structure

```
abyss-node/
├── .venv/                    # Python virtual environment
├── artwork/                  # Generated artwork
│   ├── ascii_art/           # ASCII art for rooms (18 files + JSON)
│   ├── rooms/               # DALL-E room images
│   ├── rooms_nano_banana/   # Nano Banana room images
│   ├── npcs/                # DALL-E NPC portraits
│   └── npcs_nano_banana/    # Nano Banana NPC portraits
├── abyss_node/              # Evennia game directory
│   ├── commands/            # Custom commands
│   │   ├── default_cmdsets.py
│   │   └── item_commands.py # get, drop, use, equip, loot
│   ├── server/conf/         # Settings
│   ├── typeclasses/         # Game objects
│   │   ├── characters.py    # Character + NPC with combat
│   │   ├── corpse.py        # Lootable corpses
│   │   ├── objects.py       # Items, weapons, consumables
│   │   └── rooms.py         # Rooms with ASCII art
│   ├── web/                 # Web client
│   └── world/               # World content
│       ├── zones/
│       │   └── the_abyss.py # First zone (18 rooms)
│       ├── npcs/
│       │   └── abyss_npcs.py # NPCs and mobs
│       └── items/
│           └── abyss_items.py # Zone items
└── docs/                    # Documentation
```

## Key Files

| File | Purpose |
|------|---------|
| `typeclasses/characters.py` | Character + NPC classes with combat system |
| `typeclasses/corpse.py` | Corpse typeclass (lootable, decays in 60s) |
| `typeclasses/rooms.py` | Room with ASCII art display |
| `typeclasses/objects.py` | Items, weapons, armor, consumables |
| `commands/item_commands.py` | get, drop, use, equip, unequip, loot, give |
| `world/zones/the_abyss.py` | The Abyss zone (18 rooms) |
| `world/npcs/abyss_npcs.py` | NPCs: Dr. Splice, Doña Kernel, mobs |
| `world/items/abyss_items.py` | 27 items (weapons, armor, consumables) |

## Combat System

**Auto-attack:** Both players and mobs auto-attack every 3 seconds while in combat.

```python
# Start combat
attack <target>

# Combat ends when:
# - Target dies (creates corpse with loot)
# - Player flees
# - Target leaves room
```

**Stats:**
| Stat | Effect |
|------|--------|
| STR | Melee damage, carry weight |
| DEX | Accuracy, dodge chance |
| CON | Max HP, resistance |
| INT | Hacking, tech skills |
| WIS | Perception, willpower |
| CHA | Negotiation, prices |
| CYBER | Implant capacity |

## Item Commands

```
inventory / inv / i     - View inventory
get <item>              - Pick up item
get <item> from <container> - Get from container/corpse
drop <item>             - Drop item
give <item> to <player> - Give item
use <item>              - Use consumable
equip <item>            - Equip weapon/armor
unequip <slot>          - Unequip from slot
loot / loot <corpse>    - Loot all from corpse
```

## Equipment Slots

```python
slots = {
    "weapon": None,      # Melee/ranged weapon
    "armor": None,       # Body armor
    "head": None,        # Helmet/headgear
    "implant": None,     # Cybernetic implant
}
```

## The Abyss Zone (18 Rooms)

**Spawn:** Underground Clinic (clinic)

**Build/Rebuild Zone:**
```
@py from world.zones.the_abyss import build_the_abyss; build_the_abyss(self)
```

**Update ASCII Art:**
```
@py from world.zones.the_abyss import update_ascii_art; update_ascii_art(self)
```

**Spawn NPCs:**
```
@py from world.npcs.abyss_npcs import spawn_abyss_npcs; spawn_abyss_npcs(self)
```

**Spawn Items:**
```
@py from world.items.abyss_items import spawn_abyss_items; spawn_abyss_items(self)
```

## NPCs

| NPC | Location | Type | Function |
|-----|----------|------|----------|
| Dr. Splice | Clinic | shopkeeper | Implants, healing |
| Doña Kernel | Taqueria | shopkeeper | Food buffs, healing |
| Arm Bartender | Bar Overflow | shopkeeper | Drinks, info |
| Chrome Guard | Stairs | guard | Blocks access (100 $ABYSS) |
| Mech Rat | Rat Alley | mob (lvl 1) | Combat |
| Broken Drone | Terminal | mob (lvl 2) | Combat |

## Items (27 Total)

**Weapons:** Metal Pipe, Rusty Knife, Shock Baton, Laser Pistol, Mono Katana, Neural Disruptor
**Armor:** Leather Jacket, Kevlar Vest, Chrome Plating, Neural Dampener
**Consumables:** Medkit, Stim Pack, Synth Taco, Overflow Shot, Energy Drink
**Implants:** Reflex Booster, Dermal Armor, Optical Enhancer
**Quest Items:** Corrupted Data Chip, Access Card, Mysterious Key

## Temple Buffs

| Temple | Buff | Duration | Cost |
|--------|------|----------|------|
| Satoshi | +10% drop rate | 1 hour | 5 $ABYSS |
| Vitalik | +2 INT | 1 hour | Burn NFT item |
| Toly | +15% speed | 30 min | Free (unreliable) |

## Corpse System

When mobs die:
1. Corpse created with mob's loot
2. Players can `loot corpse` or `get <item> from corpse`
3. Corpse decays after 60 seconds
4. Remaining items drop to ground on decay

## Development

```bash
# Reload after code changes
evennia reload

# Check logs
tail -f abyss_node/server/logs/server.log

# Django shell
evennia shell

# Run tests
evennia test
```

## Economy

- **$ABYSS** - In-game currency
- Characters spawn with 100 $ABYSS
- Loot coins from mobs
- Buy/sell with shopkeeper NPCs
- Future: ERC-20 token on Base L2

## Artwork

Generated with Nano Banana (Google Gemini):
- `artwork/rooms_nano_banana/` - 18 room images (JPG)
- `artwork/npcs_nano_banana/` - 6 NPC portraits (PNG)
- `artwork/ascii_art/` - 18 ASCII art files + all_rooms.json

### Nano Banana Setup

1. **Get API Key** from [Google AI Studio](https://aistudio.google.com/)
   - Create project or use existing
   - Generate API key
   - Save to `~/.config/mexi-credentials/.env` as `GEMINI_API_KEY=...`

2. **Install library:**
   ```bash
   source .venv/bin/activate
   pip install google-generativeai
   ```

3. **Usage in Python:**
   ```python
   import google.generativeai as genai

   API_KEY = "your-api-key"
   genai.configure(api_key=API_KEY)

   model = genai.GenerativeModel("gemini-2.0-flash-exp")

   # Generate image
   response = model.generate_content("Generate an image: cyberpunk alley with neon lights")

   # Extract image data
   for candidate in response.candidates:
       for part in candidate.content.parts:
           if hasattr(part, 'inline_data') and part.inline_data:
               img_data = part.inline_data.data
               with open("output.jpg", "wb") as f:
                   f.write(img_data)
   ```

4. **Models that support image generation:**
   - `gemini-2.0-flash-exp` - Fast, good quality
   - `gemini-exp-1206` - Experimental

   Note: Model availability changes. Check Google AI Studio for current models.

### Regenerate Artwork

```bash
source .venv/bin/activate
python artwork/generate_nano_banana.py      # 18 room images
python artwork/generate_npcs_nano_banana.py # 6 NPC portraits
python artwork/generate_ascii_art.py        # 18 ASCII art text files
```

### Prompt Tips for Cyberpunk Art

- Include: "cyberpunk", "neon lights", "dark", "gritty", "underground"
- Avoid: medical/clinical terms (content policy)
- Style: "digital art", "concept art", "atmospheric"
- Resolution: Images generate at ~1024x1024 by default

## References

- [Evennia Docs](https://www.evennia.com/docs/latest/)
- [Evennia GitHub](https://github.com/evennia/evennia)
- [Sindome](https://www.sindome.org/) - Cyberpunk MUD reference
