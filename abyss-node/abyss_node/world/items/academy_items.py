"""
Items especiales de Terminal Academy (Sesión D — gameplay).

Estos son typeclasses ligeras. En la práctica, la mayoría de los "objetos"
de la Academia son archivos virtuales (`room.db.academy_files`), pero aquí
definimos clases para items físicos que puedan aparecer en los rooms
(ej. un trofeo tras vencer al Corruptor).

Para la mayoría de puzzles y fragmentos, SE USA el sistema de archivos
virtuales — NO hace falta materializar objetos. Estos typeclasses existen
por completitud y para permitir spawn manual si alguien lo quiere.
"""

from typeclasses.objects import Object


class PuzzleFile(Object):
    """
    Archivo "físico" que representa un puzzle (solo cosmético — el puzzle real
    vive en `room.db.academy_files`). Sirve para tener algo looteable y raro.
    """

    def at_object_creation(self):
        super().at_object_creation()
        self.db.item_type = "puzzle_file"
        self.db.value = 0


class MemoryFragment(Object):
    """
    Fragmento de memoria materializado (opcional). La Sesión A guarda los
    fragmentos en `caller.db.memories` por ID; esta clase es por si alguien
    quiere spawnear un fragmento físico en un room.
    """

    def at_object_creation(self):
        super().at_object_creation()
        self.db.item_type = "memory_fragment"
        self.db.value = 0


class CorruptorTrophy(Object):
    """
    Trofeo que aparece tras vencer al Eco del Corruptor.
    Puramente narrativo — sin mecánica asociada.
    """

    def at_object_creation(self):
        super().at_object_creation()
        self.db.item_type = "trophy"
        self.db.value = 100
        self.db.desc = (
            "Un cristal negro que pulsa lentamente. Dentro ves tu propia cara "
            "reflejada — desenfocada, pero tuya. Es lo que queda del Eco "
            "cuando lo derrotas: no un cadáver, sino una prueba de que "
            "existías."
        )


def spawn_corruptor_trophy(caller, location):
    """Spawn un trofeo del Corruptor en la location dada."""
    from evennia import create_object
    trophy = create_object(
        CorruptorTrophy,
        key="Cristal del Eco",
        location=location,
    )
    return trophy
