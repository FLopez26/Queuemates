import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
import os

load_dotenv()

SCOPES = "user-read-private playlist-modify-public playlist-modify-private"
SCOPES = "user-read-private playlist-modify-public playlist-modify-private user-follow-modify"


def get_spotify_client() -> spotipy.Spotify:
    """
    Devuelve un cliente autenticado con Spotify.
    La primera vez abre el navegador para hacer login.
    El token se guarda en caché para no pedir login cada vez.
    """
    auth = SpotifyOAuth(
        client_id=os.getenv("SPOTIFY_CLIENT_ID"),
        client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
        redirect_uri=os.getenv("SPOTIFY_REDIRECT_URI"),
        scope=SCOPES,
        cache_path=".spotify_token_cache",
        open_browser=True,
    )
    return spotipy.Spotify(auth_manager=auth)


def obtener_perfil(sp: spotipy.Spotify) -> dict:
    """
    Devuelve los datos básicos del usuario logueado:
    id, nombre y foto de perfil.
    """
    perfil = sp.current_user()
    return {
        "id": perfil["id"],
        "nombre": perfil["display_name"],
        "foto": perfil["images"][0]["url"] if perfil.get("images") else None,
    }


def buscar_canciones(sp: spotipy.Spotify, query: str) -> list[dict]:
    """
    Busca canciones en Spotify y devuelve una lista limpia.
    """
    resultados = sp.search(q=query, type="track", limit=8)
    canciones = []

    for track in resultados["tracks"]["items"]:
        canciones.append({
            "nombre": track["name"],
            "artista": track["artists"][0]["name"],
            "album": track["album"]["name"],
            "uri": track["uri"],
            "imagen": track["album"]["images"][0]["url"] if track["album"]["images"] else None,
            "duracion_ms": track["duration_ms"],
        })

    return canciones


def anadir_a_playlist(sp: spotipy.Spotify, playlist_id: str, track_uri: str):
    """
    Añade una canción aprobada a la playlist del grupo en Spotify.
    """
    sp.playlist_add_items(playlist_id, [track_uri])

def crear_playlist_grupo(sp: spotipy.Spotify, nombre_grupo: str) -> str:
    """
    Crea una playlist en Spotify con el nombre del grupo.
    Usa el endpoint me/playlists para evitar restricciones de la API.
    """
    playlist = sp._post("me/playlists", payload={
        "name": f"QueueMates · {nombre_grupo}",
        "public": True,
        "description": "Playlist colaborativa creada con QueueMates",
    })
    return playlist["id"]
