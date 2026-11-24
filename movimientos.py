"""Movimientos del juego.
 
Cada movimiento hereda de `Movimiento` y define:
  - nombre: texto que se muestra en pantalla
  - verificar(lm): se llama en cada frame; devuelve True cuando se completa
  - reset(): reinicia su estado (se llama al proponerlo)
 
Para añadir un movimiento nuevo: crear la clase y añadirla a MOVIMIENTOS.
 
en MediaPipe la y crece hacia abajo (0 = arriba de la imagen).

"""
import math
import random
 

 
 
class Movimiento:
    nombre = "Base"
 
    def __init__(self):
        self.fase = "inicio"
 
    def reset(self):
        self.fase = "inicio"
 
    def visibles(self, lm, indices, minimo=0.2):
        """True si todos los landmarks indicados se ven con suficiente confianza."""
        for i in indices:
            v = lm[i].visibility
            if v is not None and v < minimo:
                return False
        return True
 
    def verificar(self, lm) -> bool:
        raise NotImplementedError




class LevantarMano(Movimiento):
    nombre = "Levanta la Mano"

    def verificar(self, lm):
        visibles = self.visibles(lm, [0, 15, 16])
           
        arriba = visibles and (lm[15].y < lm[0].y or lm[16].y < lm[0].y)
        if self.fase == "inicio" and not arriba:
            self.fase = "listo"
        elif self.fase == "listo" and arriba:
            return True
        return False

 

# Registro de movimientos disponibles en el juego
MOVIMIENTOS = [LevantarMano()]
 
 
def siguiente_movimiento(actual=None):
    nuevo = random.choice(MOVIMIENTOS)
    nuevo.reset()
    return nuevo
 