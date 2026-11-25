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





class TocarPies(Movimiento):
    nombre = "Tocate los pies"

    def verificar(self,lm):
        visibles = self.visibles(lm, [27,28,15,16,25,26])
        
        de_pie = visibles and (lm[15].y < lm[25].y or lm[16].y < lm[16].y)
        

        if self.fase == "inicio" and de_pie:
            self.fase = "listo"

        elif self.fase == "listo":
            margen = 0.1
            derecha = lm[16].y >= lm[28].y - margen*lm[28].y
            izquierda = lm[15].y >= lm[27].y - margen*lm[27].y

            if derecha and izquierda:
                return True
        
        return False

class Saltar(Movimiento):
    nombre = "Salta"
    
    def __init__(self):
        self.inicio_d_pie,self.inicio_d_rod = None,None
        self.inicio_i_pie,self.inicio_i_rod = None,None
        self.margen = 1#controla la altura a la que se debe saltar.
                # A mayor margen, más hay que saltar
   
    def verificar(self, lm):
        visibles = self.visibles(lm, [28,27,26,25])

        if visibles and self.fase == "inicio":
            self.inicio_d_pie, self.inicio_d_rod = lm[28].y,lm[26].y
            self.inicio_i_pie, self.inicio_i_rod = lm[27].y, lm[25].y
            self.fase = "listo"

        if self.fase == "listo":
            salto_d = lm[28].y <= ((self.inicio_d_pie+self.inicio_d_rod)/(2*self.margen))
            salto_i = lm[27].y <= ((self.inicio_i_pie+self.inicio_i_rod)/(2*self.margen))
            if salto_d and salto_i:
                return True
        return False
            
class Sentadilla(Movimiento):
    nombre = "Haz una sentadilla"

    def __init__(self):
        super().__init__()
        self.margen_arriba = 0.8
        self.margen_abajo = 0.3

    def verificar(self, lm):
        visibles = self.visibles(lm, [23,24,25,26,27,28])

        cadera = (lm[23].y + lm[24].y) / 2
        rodilla = (lm[25].y + lm[26].y) / 2
        tobillo = (lm[27].y + lm[28].y) / 2
        espinilla = tobillo - rodilla

        if not visibles:
            return False
        de_pie = cadera < rodilla - self.margen_arriba*espinilla
        abajo = cadera >= rodilla - self.margen_abajo*espinilla

        if self.fase == "inicio" and de_pie:
            self.fase = "listo"
        elif self.fase == "listo" and abajo:
            return True
        return False


# Registro de movimientos disponibles en el juego
MOVIMIENTOS = [Saltar(), TocarPies(), Sentadilla()]
 
 
def siguiente_movimiento(actual=None):
    elegir = [mov for mov in MOVIMIENTOS if mov != actual]
    nuevo = random.choice(elegir)
    nuevo.reset()
    return nuevo
 