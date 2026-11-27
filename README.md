# IPM - Práctica 2: juego de ejercicios

## Introducción

Juego para hacer ejercicio delante de la cámara. En pantalla aparece un movimiento y, cuando lo haces, sumas un punto y sale otro distinto. La partida dura 30 segundos y el objetivo es hacer el máximo de movimientos.

Movimientos que hay:
- Salta
- Tócate los pies
- Haz una sentadilla
- Levanta los brazos
- Levanta la rodilla (izquierda o derecha, al azar)

Para detectar la postura se usa MediaPipe:

- *```Pose Landmarker```* (usado en este repositorio), se pueden ver cada landmark a qué parte del cuerpo pertenece [aquí](https://ai.google.dev/edge/mediapipe/solutions/vision/pose_landmarker?hl=es-419).


## Prerequisitos

Tener instalado **Conda**, [instalar aquí](https://www.anaconda.com/docs/getting-started/miniconda/install).

Tener una cámara web conectada.

## Requisitos

Crear un entorno de conda:
```bash
conda create -n IPM python=3.12
conda activate IPM
```

## Instalación

Se clona el repositorio:
```bash
git clone https://github.com/RaulUclesLajara1/juego-ipm.git
cd juego-ipm
```

Se instalan las dependencias necesarias (MediaPipe, Requests, tqdm, cv2, numpy, etc.):
```bash
pip install -r requirements.txt
```

Se descargan los modelos de MediaPipe en la carpeta `models/` (sin ellos el juego no arranca):
```bash
python download_models.py
```


## Ejecución
```bash
python app.py
```

## Cómo jugar

1. El juego se abre a pantalla completa. Colócate a unos metros de la cámara, de forma que se te vea el cuerpo entero.
2. Pulsa ENTER para empezar. Hay una cuenta atrás de 3 segundos.
3. Haz el movimiento que aparece arriba. Abajo se ven los puntos y el tiempo que queda.
4. Al acabar se muestran los puntos. ENTER para jugar otra vez y ESC para salir.
