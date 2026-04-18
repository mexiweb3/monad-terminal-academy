# Abyss Node - Game Guide

Welcome to **The Abyss**, the undercity of Neo-Withmore. Year 2111. Megacorps rule above, the forgotten survive below.

## Quick Start

1. Connect via web (`http://localhost:4001`) or telnet (`localhost:4000`)
2. Create account and character
3. You spawn in the **Underground Clinic** - Dr. Splice just saved your life
4. Explore, fight, loot, survive

---

## The Abyss - Zone Map

```
                    [TEMPLE SATOSHI]---[DEAD SERVER]---[TEMPLE VITALIK]
                           |                |                |
                           +-------[TEMPLE TOLY]-------------+
                                        |
                                        |
    [FORGOTTEN TUNNEL]---[BLACK MARKET PLAZA]---[UNDERGROUND CLINIC] << SPAWN
                                   |
    [CHROME LAIR]----------[CENTRAL CROSSING]-------[ABANDONED TERMINAL]
          |                        |                        |
    [THE ARENA]            [TAQUERIA]                [BAR OVERFLOW]
                                   |
         [RAT ALLEY]----[RUSTED PASSAGE]----[WATER TANK]
                               |
                    [ENTRANCE TO ABYSS]
                               |
                    [STAIRS TO CRIMSON] >> LOCKED (100 $ABYSS)
```

### Room Connections

| Room | Exits |
|------|-------|
| Entrance | north → Passage, south → Stairs |
| Rusted Passage | north → Crossing, south → Entrance, east → Tank, west → Alley |
| Rat Alley | east → Passage |
| Water Tank | west → Passage |
| Central Crossing | north → Plaza, south → Passage, east → Terminal, west → Lair, down → Taqueria |
| Black Market Plaza | north → Temple Toly, south → Crossing, east → Clinic, west → Tunnel |
| Underground Clinic | west → Plaza |
| Abandoned Terminal | west → Crossing, down → Bar |
| Bar Overflow | up → Terminal |
| Taqueria | up → Crossing |
| Chrome Lair | east → Crossing, south → Arena |
| The Arena | north → Lair |
| Forgotten Tunnel | east → Plaza |
| Temple Toly | north → Server, south → Plaza |
| Dead Server | south → Toly, west → Satoshi, east → Vitalik |
| Temple Satoshi | east → Server |
| Temple Vitalik | west → Server |
| Stairs to Crimson | north → Entrance |

---

## NPCs

### Friendly NPCs

| NPC | Location | Services |
|-----|----------|----------|
| **Dr. Splice** | Underground Clinic | Implant installation, healing, medical supplies |
| **Doña Kernel** | Taqueria | Food (heals + buffs), gossip |
| **Arm Bartender** | Bar Overflow | Drinks (buffs), information, rumors |
| **Chrome Guard** | Stairs to Crimson | Passage to upper city (100 $ABYSS fee) |

### Hostile Mobs

| Mob | Location | Level | Drops |
|-----|----------|-------|-------|
| **Mech Rat** | Rat Alley | 1 | 5-15 $ABYSS, Copper Wire |
| **Broken Drone** | Abandoned Terminal | 2 | 10-25 $ABYSS, Scrap Metal, Data Chip |

---

## Combat Guide

### Starting Combat
```
attack <target>
attack rat
attack drone
```

### Combat Flow
1. You attack the target
2. Target counter-attacks
3. Both auto-attack every 3 seconds
4. Combat ends when someone dies or flees

### Death & Loot
- Mobs drop a **corpse** when killed
- Use `loot` or `loot corpse` to grab everything
- Or `get <item> from corpse` for specific items
- Corpses decay in 60 seconds!

### Tips
- Check your HP: `score` or `stats`
- Heal with consumables: `use medkit`
- Run away: `flee` (moves to random exit)
- Equip weapons for more damage: `equip pipe`

---

## Items & Equipment

### Equipment Slots
```
weapon   - Your primary weapon
armor    - Body protection
head     - Helmet or headgear
implant  - Cybernetic enhancement
```

### Item Commands
```
inventory          - See what you're carrying
get <item>         - Pick up item from ground
drop <item>        - Drop item
equip <item>       - Wear/wield item
unequip <slot>     - Remove equipped item
use <item>         - Use consumable item
loot               - Loot nearest corpse
```

### Starter Gear Locations

| Item | Where to Find |
|------|---------------|
| Metal Pipe | Rat Alley, Rusted Passage |
| Rusty Knife | Chrome Lair |
| Leather Jacket | Abandoned Terminal |
| Medkit | Underground Clinic |
| Synth Taco | Taqueria |

---

## Temple Blessings

Visit the three crypto temples in the server room area for temporary buffs:

| Temple | Blessing | Effect | Duration |
|--------|----------|--------|----------|
| **Satoshi** | Luck of the Whitepaper | +10% loot drops | 1 hour |
| **Vitalik** | Smart Contract Mind | +2 INT | 1 hour |
| **Toly** | Speed of TPS | +15% action speed | 30 min* |

*Toly's blessing is "unreliable" - may randomly fail (just like mainnet)

---

## Economy

### Currency: $ABYSS
- Loot from mobs
- Find in containers
- Trade with other players
- Spend at shops

### Prices (approximate)
| Item | Cost |
|------|------|
| Medkit | 25 $ABYSS |
| Synth Taco | 10 $ABYSS |
| Leather Jacket | 50 $ABYSS |
| Shock Baton | 100 $ABYSS |
| Crimson Access | 100 $ABYSS |

---

## Survival Tips

### For New Players

1. **Don't rush into combat** - Check your stats first with `score`
2. **Loot fast** - Corpses decay in 60 seconds
3. **Stock up on healing** - Get tacos from Doña Kernel, medkits from Dr. Splice
4. **Explore carefully** - Read room descriptions, they contain hints
5. **Save $ABYSS** - You'll need 100 to access Crimson District

### Combat Tips

1. **Equip a weapon** - Bare fists do minimal damage
2. **Check mob HP** - Mobs show health percentage when you look at room
3. **Know when to flee** - Better to run than die
4. **Heal between fights** - Don't chain-pull mobs

### Exploration Tips

1. **Map it out** - The Abyss has 18 rooms in a maze
2. **Visit temples** - Free buffs help a lot
3. **Talk to NPCs** - They have quests and info
4. **Check containers** - Loot spawns in various locations

---

## Commands Reference

### Movement
```
north/n, south/s, east/e, west/w
up/u, down/d
look/l              - Look at current room
look <thing>        - Examine something
```

### Combat
```
attack <target>     - Start combat
flee                - Escape combat
score/stats         - View your stats
```

### Items
```
inventory/inv/i     - View inventory
get <item>          - Pick up
drop <item>         - Drop
use <item>          - Use consumable
equip <item>        - Equip
unequip <slot>      - Unequip
loot                - Loot corpse
```

### Social
```
say <message>       - Talk in room
whisper <player>=<msg> - Private message
who                 - See online players
```

### Info
```
help                - Help system
help <topic>        - Specific help
look                - Look around
examine <thing>     - Detailed look
```

---

## Lore

### The Year is 2111

The megacorps won. They own the sky, the data, the light. Everyone with credits lives above in the chrome towers and neon gardens of Neo-Withmore.

But you? You're below. In **The Abyss**.

Down here, the forgotten scrape by on synthetic protein and stolen bandwidth. The rats are smarter than most people. The water tastes like regret. And everyone's running from something.

You woke up on Dr. Splice's table with a new scar and no memory of how you got here. He says you owe him $50 ABYSS. He also says you should probably get a weapon before leaving the clinic.

Welcome to the bottom. The only way is up. Or deeper down.

### Factions

- **Corpies** - Corporate drones with premium implants. Rarely venture below.
- **Runners** - Freelance hackers. Information is currency.
- **Chromes** - More machine than human. They have their own lair.
- **Ghosts** - No on-chain identity. They don't exist, officially.
- **Synths** - AI robots with emerging consciousness. Legal status: complicated.

### The Three Prophets

The undercity worships three figures from the old crypto wars:

- **Satoshi** - The anonymous creator. No one knows who they were.
- **Vitalik** - The eternal youth who promised the world computer.
- **Toly** - The speed merchant. His temple crashes sometimes.

---

*"In the Abyss, nobody judges you. Because nobody cares."*
