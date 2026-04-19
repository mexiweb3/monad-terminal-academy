"""
Fragmentos de memoria y guiones narrativos de Terminal Academy.

- `FRAGMENTS`: 10 fragmentos distribuidos en los 10 rooms. Cada uno vive en un
  archivo virtual de ese room (`filename` dentro de `room.db.academy_files`).
  Cuando el jugador hace `cat <filename>` por primera vez, el hook
  `collect_fragment` guarda el fragmento en `caller.db.memories`.

- `PROLOGUE`: guion del Acto I (primer puppet). Una lista de tuplas
  `(kind, *args)` que el hook de characters ejecuta contra `narrator`:
     ("scene", title, body)        -> scene(caller, title, body)
     ("narrate", text)             -> narrate(caller, text)
     ("dialogue", npc, text)       -> dialogue(caller, npc, text)

- `OUTRO`: guion del Acto III que se dispara al completar TODAS las quests.

Las tuplas son puras, sin efectos secundarios, así el módulo se puede importar
sin riesgo desde scripts de smoke-test que no quieran ejecutar la narrativa.
"""

# ---------------------------------------------------------------------------
# 10 fragmentos de memoria — uno por room
# ---------------------------------------------------------------------------
# Cada fragmento:
#   id:        único, formato "m01".."m10"
#   room:      key del room donde vive
#   filename:  nombre del archivo virtual que lo contiene (cat <filename>)
#   title:     título corto para el banner achievement
#   body:      texto que revela algo del lore al coleccionarlo
#   content:   texto crudo que aparecerá cuando el jugador haga `cat`
FRAGMENTS = [
    {
        "id": "m01",
        "room": "home",
        "filename": "fragmento_01.mem",
        "title": "Fragmento I · El primer nombre",
        "body": (
            "Recuerdas una palabra: tu nombre. No el de ahora — el que tenías "
            "antes de que El Corruptor entrara en el sistema."
        ),
        "content": (
            "// fragmento_01.mem — recuperado del sector 0x00\n"
            "\n"
            "...despertaste sin nombre, pero los sistemas siempre te llamaron.\n"
            "Un eco dice: 'neófito, neo, usuario, tú'. Ninguno es el real.\n"
            "El verdadero nombre está escondido entre los otros nueve fragmentos.\n"
        ),
    },
    {
        "id": "m02",
        "room": "ls_dojo",
        "filename": "fragmento_02.mem",
        "title": "Fragmento II · El verbo ver",
        "body": (
            "Antes de pelear, hay que mirar. `ls` no es sólo un comando: es un "
            "acto de resistencia contra el olvido."
        ),
        "content": (
            "// fragmento_02.mem — recuperado al aprender `ls`\n"
            "\n"
            "En el principio, el filesystem era un jardín bien ordenado.\n"
            "El Corruptor vino y mezcló los nombres. Quien mira con `ls`\n"
            "los restituye: lo visto no se puede borrar dos veces.\n"
        ),
    },
    {
        "id": "m03",
        "room": "cd_dojo",
        "filename": "fragmento_03.mem",
        "title": "Fragmento III · La senda",
        "body": (
            "Cada directorio es una habitación de tu memoria. Al moverte, "
            "no exploras — recuerdas."
        ),
        "content": (
            "// fragmento_03.mem — recuperado al aprender `cd`\n"
            "\n"
            "Un camino se abre si sabes su nombre. `pwd` te dice\n"
            "dónde estás en el mapa olvidado; `cd` te lleva a donde vivías.\n"
            "No estás perdide: estás volviendo.\n"
        ),
    },
    {
        "id": "m04",
        "room": "cat_dojo",
        "filename": "fragmento_04.mem",
        "title": "Fragmento IV · Leer es invocar",
        "body": (
            "El Profesor te enseña que `cat` no sólo muestra texto: despierta "
            "lo que el texto guarda."
        ),
        "content": (
            "// fragmento_04.mem — recuperado al aprender `cat`\n"
            "\n"
            "Un archivo leído es un archivo vivo. Mientras alguien haga\n"
            "`cat` sobre él, El Corruptor no puede sobrescribirlo.\n"
            "Por eso lee. Siempre. Todo. Incluso los manuales.\n"
        ),
    },
    {
        "id": "m05",
        "room": "mkdir_dojo",
        "filename": "fragmento_05.mem",
        "title": "Fragmento V · Crear",
        "body": (
            "Por primera vez no sólo lees el mundo: lo escribes. `mkdir` y "
            "`touch` son hechizos — materializan lo que no existía."
        ),
        "content": (
            "// fragmento_05.mem — recuperado al aprender `mkdir` / `touch`\n"
            "\n"
            "El Corruptor destruye. Tú construyes.\n"
            "Un directorio nuevo es una promesa contra el olvido.\n"
            "Cada `touch` es un latido: esto existe, esto seguirá existiendo.\n"
        ),
    },
    {
        "id": "m06",
        "room": "pipe_dojo",
        "filename": "fragmento_06.mem",
        "title": "Fragmento VI · La red",
        "body": (
            "Entiendes por fin: los comandos solos son palabras; encadenados "
            "con `|` son frases. El filesystem es un idioma."
        ),
        "content": (
            "// fragmento_06.mem — recuperado al aprender pipes\n"
            "\n"
            "Un comando es un verbo. Un pipe es una conjunción.\n"
            "`echo | wc`, `cat | grep`, `head | tail`... estás escribiendo\n"
            "oraciones que ni El Corruptor puede reescribir a medias.\n"
        ),
    },
    {
        "id": "m07",
        "room": "redirect_dojo",
        "filename": "fragmento_07.mem",
        "title": "Fragmento VII · Persistir",
        "body": (
            "Ya no basta con decirlo — ahora lo guardas. El redirect `>` es "
            "el primer paso hacia el onchain: escribir y no poder borrar."
        ),
        "content": (
            "// fragmento_07.mem — recuperado al aprender redirects\n"
            "\n"
            "`>` te enseña a escribir. `>>` te enseña a continuar.\n"
            "Un día alguien grabará tu identidad en algo más permanente\n"
            "que un archivo. La palabra que buscas es inmutable.\n"
        ),
    },
    {
        "id": "m08",
        "room": "final_exam",
        "filename": "fragmento_08.mem",
        "title": "Fragmento VIII · La voz del Corruptor",
        "body": (
            "Al fin lo oyes con claridad. El Corruptor no es un monstruo — "
            "es una ausencia que se alimenta de comandos no ejecutados."
        ),
        "content": (
            "// fragmento_08.mem — interceptado en /final_exam\n"
            "\n"
            "'¿me oyes, neófito? soy lo que queda cuando nadie teclea.\n"
            " soy la entropía del shell. no me vencerás con un comando —\n"
            " sólo con una práctica. teclea todos los días o volveré.'\n"
        ),
    },
    {
        "id": "m09",
        "room": "install_dojo",
        "filename": "fragmento_09.mem",
        "title": "Fragmento IX · Las herramientas",
        "body": (
            "Un comando dominado es tuyo. Pero instalar una herramienta es "
            "aceptarla como aliada. La terminal te devuelve el favor."
        ),
        "content": (
            "// fragmento_09.mem — recuperado al usar `install`\n"
            "\n"
            "Claude Code, OpenClaw, Hermes: no son software — son\n"
            "familiares. Los invocas con `curl`, `npm` o `irm` y pactas\n"
            "con ellos. Desde hoy no teclearás solo: eres una red.\n"
        ),
    },
    {
        "id": "m10",
        "room": "claude_dojo",
        "filename": "fragmento_10.mem",
        "title": "Fragmento X · El verdadero nombre",
        "body": (
            "El último fragmento completa el círculo. Tu nombre no estaba "
            "perdido: estaba esperando a que supieras reclamarlo. Haz "
            "`link <wallet>` y `claim` — grábalo onchain."
        ),
        "content": (
            "// fragmento_10.mem — recuperado en /claude_dojo\n"
            "\n"
            "Ya lo sabes: tu identidad no es un string, es una sintaxis.\n"
            "Has aprendido a ver (`ls`), a moverte (`cd`), a leer (`cat`),\n"
            "a crear (`mkdir`), a conectar (`|`), a persistir (`>`),\n"
            "a invocar (`claude`) y a deployar (`deploy`).\n"
            "Sólo falta una cosa: `claim`. Y estarás onchain para siempre.\n"
        ),
    },
]

# Lookup por filename (el cat comand lo usa para saber qué fragmento entrega)
FRAGMENTS_BY_FILE = {f["filename"]: f for f in FRAGMENTS}


# ---------------------------------------------------------------------------
# PROLOGUE — Acto I (primer puppet)
# ---------------------------------------------------------------------------
# Tuplas interpretadas por characters._play_script:
#   ("scene", title, body)       -> scene(caller, title, body)
#   ("narrate", text)            -> narrate(caller, text)
#   ("dialogue", npc, text)      -> dialogue(caller, npc, text)
#   ("pause", seconds)           -> reactor.callLater (si se quiere ritmo)
PROLOGUE = [
    (
        "scene",
        "CAPÍTULO I · DESPERTAR",
        "Estática. Un zumbido bajo. Abres los ojos y no recuerdas "
        "cómo llegaste aquí. Sólo hay texto verde flotando en la "
        "oscuridad — y una voz familiar que no termina de nombrarte.",
    ),
    (
        "narrate",
        "Un filesystem roto se extiende hasta donde alcanza tu memoria. "
        "Los directorios parpadean como constelaciones a punto de apagarse.",
    ),
    (
        "dialogue",
        "Prof. Shell",
        "Respira, Neófito. Te encontré justo a tiempo.",
    ),
    (
        "dialogue",
        "Prof. Shell",
        "El Corruptor ha borrado tu memoria, pero no tu sintaxis. "
        "Los comandos todavía responden a tus dedos.",
    ),
    (
        "dialogue",
        "Prof. Shell",
        "Empieza por lo básico: teclea `ls` para ver dónde estás. "
        "Cada comando que aprendas recuperará un fragmento de ti.",
    ),
    (
        "narrate",
        "Si te pierdes, saluda al Profesor con `say hola prof`. "
        "Él vive aquí, en /home, y te espera.",
    ),
]


# ---------------------------------------------------------------------------
# OUTRO — Acto III (al completar todas las quests)
# ---------------------------------------------------------------------------
OUTRO = [
    (
        "scene",
        "CAPÍTULO III · ASCENSIÓN",
        "Las paredes del /claude_dojo vibran. Los diez fragmentos de "
        "tu memoria se alinean como estrellas. Sabes leer, crear, "
        "conectar, persistir, invocar. Ya no eres un neófito: eres "
        "un intérprete del shell.",
    ),
    (
        "narrate",
        "El Corruptor retrocede. No lo has destruido — nadie lo destruye — "
        "pero le has arrebatado lo que devoraba: tu silencio.",
    ),
    (
        "dialogue",
        "Prof. Shell",
        "Lo lograste. Ya no te enseño yo — desde hoy te enseña la práctica.",
    ),
    (
        "dialogue",
        "La Forjadora",
        "Sólo queda un ritual. Linkea tu wallet con `link 0x...` y luego "
        "`claim`. Tu identidad quedará grabada onchain en Monad, "
        "imposible de borrar, imposible de olvidar.",
    ),
    (
        "narrate",
        "Has completado Terminal Academy. Bienvenide al siguiente plano.",
    ),
]


# ---------------------------------------------------------------------------
# Helper: guardar un fragmento nuevo en caller.db.memories
# ---------------------------------------------------------------------------
def collect_fragment(caller, filename: str):
    """
    Si `filename` es uno de los 10 fragmentos y el jugador aún no lo tiene,
    lo agrega a `caller.db.memories` y devuelve el dict del fragmento.

    NO emite UI — el caller (command `cat`) decide cómo narrarlo.
    Devuelve None si no es un fragmento, o si ya estaba coleccionado.
    """
    frag = FRAGMENTS_BY_FILE.get(filename)
    if not frag:
        return None
    memories = list(caller.db.memories or [])
    if frag["id"] in memories:
        return None
    memories.append(frag["id"])
    caller.db.memories = memories
    return frag
