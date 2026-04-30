from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Cancion:
    nombre: str
    artista: str
    album: str
    uri: str              # identificador único de Spotify
    imagen_url: str = ""
    duracion_ms: int = 0


@dataclass
class Votacion:
    id: str
    cancion: Cancion
    propuesto_por: str
    estado: str = "pendiente"   # pendiente | aprobada | rechazada
    votos_si: list = field(default_factory=list)
    votos_no: list = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Grupo:
    codigo: str
    nombre: str
    creador: str
    miembros: list = field(default_factory=list)