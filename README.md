# QueueMates 🎵

Aplicación móvil colaborativa para votar canciones en grupo. Crea un grupo con tus amigos, proponed canciones y decidid por votación qué suena a continuación. Las canciones aprobadas se añaden automáticamente a una playlist compartida de Spotify.

## ¿Cómo funciona?

1. Inicia sesión con tu cuenta de Spotify
2. Crea un grupo o únete a uno con su código de 4 letras
3. Propón canciones buscando directamente en Spotify
4. El grupo vota — si la mayoría aprueba, la canción se añade a la playlist del grupo
5. La playlist aparece automáticamente en tu biblioteca de Spotify

## Tecnologías

- **Flet** — framework Python para apps móviles y de escritorio
- **Spotify Web API** — búsqueda de canciones y gestión de playlists
- **Firebase Firestore** — base de datos en tiempo real para grupos y votaciones
- **Spotipy** — cliente Python para la API de Spotify

## Requisitos

- Python 3.11 o superior
- Cuenta de Spotify
- Proyecto en Firebase con Firestore activado
- App registrada en Spotify Developer Dashboard

## Instalación

### 1. Clona el repositorio

```bash
git clone https://github.com/TU_USUARIO/queuemates.git
cd queuemates
```

### 2. Crea el entorno virtual e instala dependencias

```bash
python -m venv venv
source venv/Scripts/activate  # Windows (Git Bash)
source venv/bin/activate       # Mac / Linux

pip install -r requirements.txt
```

### 3. Configura las credenciales

Crea un archivo `.env` en la raíz del proyecto:

```env
SPOTIFY_CLIENT_ID=tu_client_id
SPOTIFY_CLIENT_SECRET=tu_client_secret
SPOTIFY_REDIRECT_URI=http://127.0.0.1:8888/callback
FIREBASE_CREDENTIALS=nombre-de-tu-serviceAccountKey.json
```

**Spotify:** Registra una app en [developer.spotify.com/dashboard](https://developer.spotify.com/dashboard) y copia el Client ID y Client Secret. Añade `http://127.0.0.1:8888/callback` como Redirect URI en la configuración de la app.

**Firebase:** Crea un proyecto en [console.firebase.google.com](https://console.firebase.google.com), activa Firestore Database en modo prueba, y descarga la clave de cuenta de servicio desde *Configuración del proyecto → Cuentas de servicio → Generar nueva clave privada*. Coloca el archivo JSON en la raíz del proyecto.

### 4. Ejecuta la app

```bash
python main.py
```

Se abrirá una ventana de escritorio y el navegador para hacer login con Spotify.

## Estructura del proyecto

```
queuemates/
├── main.py                  # Entrada de la app y navegación
├── auth/
│   └── spotify_auth.py      # Login y operaciones con Spotify API
├── firebase/
│   └── db.py                # Operaciones con Firestore
├── models/
│   └── group.py             # Modelos de datos
├── screens/
│   ├── login_screen.py      # Pantalla de login
│   ├── home_screen.py       # Lista de grupos del usuario
│   ├── group_screen.py      # Votaciones en tiempo real
│   └── search_screen.py     # Búsqueda de canciones
└── requirements.txt
```

## Flujo de datos

```
[App móvil]
    ↕ escritura / lectura en tiempo real
[Firebase Firestore]
    → notifica cambios a todos los miembros del grupo al instante
[App móvil]
    ↕ cuando una votación se aprueba
[Spotify Web API]
    → añade la canción a la playlist del grupo
```

## Variables de entorno necesarias

| Variable | Descripción |
|---|---|
| `SPOTIFY_CLIENT_ID` | Client ID de tu app en Spotify Developer |
| `SPOTIFY_CLIENT_SECRET` | Client Secret de tu app en Spotify Developer |
| `SPOTIFY_REDIRECT_URI` | URI de redirección tras el login |
| `FIREBASE_CREDENTIALS` | Nombre del archivo JSON de Firebase |

## Notas

- El archivo `.env` y el `serviceAccountKey.json` **nunca deben subirse a GitHub**. Están incluidos en `.gitignore`.
- La app está en modo desarrollo de Spotify, por lo que solo los usuarios añadidos manualmente en el Spotify Developer Dashboard pueden usarla. Para uso público habría que solicitar acceso extendido.
- Las votaciones se actualizan en tiempo real gracias a los listeners de Firestore — no hace falta recargar la app.

## Próximos pasos

- Empaquetado como APK para Android
- Notificaciones push al móvil con Firebase Cloud Messaging
- Soporte para playlists de YouTube
