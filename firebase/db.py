import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv
import os
import random
import string
from datetime import datetime

load_dotenv()

cred = credentials.Certificate(os.getenv("FIREBASE_CREDENTIALS"))
firebase_admin.initialize_app(cred)

db = firestore.client()


def crear_grupo(nombre_grupo: str, spotify_user_id: str, playlist_id: str) -> str:
    """
    Ahora recibe también el playlist_id que se crea en Spotify.
    """
    while True:
        codigo = ''.join(random.choices(string.ascii_uppercase, k=4))
        ref = db.collection("grupos").document(codigo)
        if not ref.get().exists:
            break

    ref.set({
        "nombre": nombre_grupo,
        "creador": spotify_user_id,
        "miembros": [spotify_user_id],
        "playlist_id": playlist_id,   # ← nuevo
        "creado_en": datetime.utcnow(),
    })
    return codigo


def obtener_playlist_id(codigo_grupo: str) -> str:
    """Devuelve el ID de la playlist de Spotify del grupo."""
    grupo = obtener_grupo(codigo_grupo)
    return grupo.get("playlist_id", "")


def unirse_grupo(codigo: str, spotify_user_id: str) -> bool:
    """
    Une al usuario a un grupo existente.
    Devuelve False si el código no existe.
    """
    ref = db.collection("grupos").document(codigo)
    if not ref.get().exists:
        return False

    ref.update({
        "miembros": firestore.ArrayUnion([spotify_user_id])
    })
    return True


def obtener_grupo(codigo: str) -> dict:
    """Devuelve los datos del grupo o {} si no existe."""
    doc = db.collection("grupos").document(codigo).get()
    return doc.to_dict() if doc.exists else {}


def proponer_cancion(codigo_grupo: str, propuesta: dict) -> str:
    """
    Añade una canción a votación en el grupo.
    Devuelve el ID del documento creado en Firestore.
    """
    propuesta["timestamp"] = datetime.utcnow()
    propuesta["estado"] = "pendiente"
    propuesta["votos_si"] = []
    propuesta["votos_no"] = []

    _, ref = db.collection("grupos").document(codigo_grupo) \
               .collection("votaciones").add(propuesta)
    return ref.id


def votar(codigo_grupo: str, votacion_id: str,
          user_id: str, voto: bool) -> str:

    ref = db.collection("grupos").document(codigo_grupo) \
            .collection("votaciones").document(votacion_id)

    campo = "votos_si" if voto else "votos_no"
    ref.update({campo: firestore.ArrayUnion([user_id])})

    doc = ref.get().to_dict()
    grupo = obtener_grupo(codigo_grupo)
    total_miembros = len(grupo.get("miembros", [1]))
    votos_si = len(doc.get("votos_si", []))
    votos_no = len(doc.get("votos_no", []))
    mayoria = total_miembros // 2 + 1

    if votos_si >= mayoria:
        ref.update({"estado": "aprobada"})
        return "aprobada"

    # Si con los votos negativos ya es imposible alcanzar la mayoría
    if votos_no > total_miembros - mayoria:
        ref.update({"estado": "rechazada"})
        return "rechazada"

    return "pendiente"


def escuchar_votaciones(codigo_grupo: str, callback):
    """
    Listener en tiempo real. Cada vez que alguien propone
    una canción o vota, Firestore llama a callback automáticamente.
    Devuelve el objeto watcher para poder cancelarlo luego.
    """
    return db.collection("grupos") \
             .document(codigo_grupo) \
             .collection("votaciones") \
             .order_by("timestamp", direction=firestore.Query.DESCENDING) \
             .on_snapshot(callback)