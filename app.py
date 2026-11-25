"""Bucle principal del juego: cámara, MediaPipe, estados y pantalla.

La lógica de los ejercicios vive en movimientos.py.
"""
import sys
import time

import cv2
import mediapipe as mp
import numpy as np

from config import config  # se usa solo config.model_path
from movimientos import siguiente_movimiento

# ---------------------------------------------------------------------------
# Configuración de MediaPipe
# ---------------------------------------------------------------------------
BaseOptions = mp.tasks.BaseOptions
PoseLandmarker = mp.tasks.vision.PoseLandmarker
PoseLandmarkerOptions = mp.tasks.vision.PoseLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode
POSE_CONNECTIONS = mp.tasks.vision.PoseLandmarksConnections.POSE_LANDMARKS

options = PoseLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=config.model_path),
    running_mode=VisionRunningMode.VIDEO,
    num_poses=1,
)

DURACION_JUEGO = 30   # segundos
CUENTA_ATRAS = 3      # segundos de cuenta atrás antes de empezar


# ---------------------------------------------------------------------------
# Dibujo
# ---------------------------------------------------------------------------
def dibujar_esqueleto(frame, landmarks):
    h, w, _ = frame.shape
    for conexion in POSE_CONNECTIONS:
        a, b = landmarks[conexion.start], landmarks[conexion.end]
        cv2.line(frame, (int(a.x * w), int(a.y * h)), (int(b.x * w), int(b.y * h)),
                 (255, 0, 0), 2)
    for p in landmarks:
        cv2.circle(frame, (int(p.x * w), int(p.y * h)), 3, (0, 255, 0), -1)


def texto_centrado(frame, texto, y, escala=1.0, color=(0, 255, 0), grosor=2):
    h, w, _ = frame.shape
    (tw, _), _ = cv2.getTextSize(texto, cv2.FONT_HERSHEY_SIMPLEX, escala, grosor)
    cv2.putText(frame, texto, ((w - tw) // 2, y), cv2.FONT_HERSHEY_SIMPLEX,
                escala, color, grosor)


def texto_centro_pantalla(frame, texto, escala=1.0, color=(0, 255, 0), grosor=2):
    """Dibuja el texto centrado tanto en horizontal como en vertical."""
    h, w, _ = frame.shape
    (tw, th), _ = cv2.getTextSize(texto, cv2.FONT_HERSHEY_SIMPLEX, escala, grosor)
    cv2.putText(frame, texto, ((w - tw) // 2, (h + th) // 2),
                cv2.FONT_HERSHEY_SIMPLEX, escala, color, grosor)


# ---------------------------------------------------------------------------
# Bucle principal
# ---------------------------------------------------------------------------
def main():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("No se pudo abrir la cámara")
        sys.exit(1)

    # espera -> cuenta_atras -> jugando -> fin -> (Enter) cuenta_atras ...
    estado = "espera"
    puntos = 0
    t_inicio_juego = 0.0
    t_inicio_cuenta = 0.0
    movimiento = None

    t_programa = time.time()
    ultimo_ts = -1

    with PoseLandmarker.create_from_options(options) as landmarker:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            frame = cv2.flip(frame, 1)  # efecto espejo
            h, w, _ = frame.shape

            # --- Detección (MediaPipe espera RGB; OpenCV da BGR) ---
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
            ts = int((time.time() - t_programa) * 1000)
            ts = max(ts, ultimo_ts + 1)  # el timestamp debe ser creciente
            ultimo_ts = ts
            result = landmarker.detect_for_video(mp_image, ts)
            lm = result.pose_landmarks[0] if result.pose_landmarks else None

            if lm:
                dibujar_esqueleto(frame, lm)

            key = cv2.waitKey(1) & 0xFF
            if key == 27:  # ESC
                break

            # ------------------------- ESTADOS -------------------------
            if estado == "espera":
                texto_centrado(frame, "Colocate de cuerpo entero", h // 2 - 30)
                texto_centrado(frame, "Pulsa ENTER para empezar", h // 2 + 20)
                if key == 13:
                    t_inicio_cuenta = time.time()
                    estado = "cuenta_atras"

            elif estado == "cuenta_atras":
                transcurrido = time.time() - t_inicio_cuenta
                restante_cuenta = CUENTA_ATRAS - transcurrido

                if restante_cuenta <= 0:
                    # Termina la cuenta atrás: empieza el juego
                    puntos = 0
                    t_inicio_juego = time.time()
                    movimiento = siguiente_movimiento()
                    estado = "jugando"
                else:
                    numero = int(restante_cuenta) + 1  # 3, 2, 1
                    texto_centrado(frame, "Preparate...", h // 2 - 120, 1.0, (0, 255, 255))
                    texto_centro_pantalla(frame, str(numero), 8.0, (0, 255, 255), 12)

            elif estado == "jugando":
                restante = DURACION_JUEGO - (time.time() - t_inicio_juego)

                if restante <= 0:
                    estado = "fin"
                else:
                    if lm:
                        if movimiento.verificar(lm):
                            puntos += 1
                            movimiento = siguiente_movimiento(movimiento)
                    else:
                        texto_centrado(frame, "No te veo: colocate de cuerpo entero",
                                       h - 30, 0.8, (0, 0, 255))

                    texto_centrado(frame, movimiento.nombre, 50, 1.4, (0, 255, 255), 3)
                    cv2.putText(frame, f"Puntos: {puntos}", (10, h - 20),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    cv2.putText(frame, f"Tiempo: {restante:4.1f}", (w - 220, h - 20),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            if estado == "fin":
                frame = np.zeros_like(frame)  # pantalla en negro
                texto_centrado(frame, f"Puntos: {puntos}", h // 2 - 20, 1.6, (0, 255, 0), 3)
                texto_centrado(frame, "ENTER: jugar de nuevo", h // 2 + 50, 0.9)
                texto_centrado(frame, "ESC: salir", h // 2 + 90, 0.9, (255, 128, 0))
                if key == 13:
                    t_inicio_cuenta = time.time()
                    estado = "cuenta_atras"

            cv2.imshow("Juego de ejercicios", frame)

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()