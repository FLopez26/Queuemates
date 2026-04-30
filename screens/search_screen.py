import flet as ft
from auth.spotify_auth import buscar_canciones
from firebase.db import proponer_cancion


class SearchScreen(ft.Column):
    def __init__(self, page: ft.Page, state: dict, on_volver):
        super().__init__()

        self._page = page
        self.state = state
        self.on_volver = on_volver

        self.expand = True
        self.alignment = ft.MainAxisAlignment.START
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.spacing = 0

        self.resultados = ft.Column(
            spacing=8,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )

        self.status = ft.Text("", color="#b3b3b3", size=13)

        self.input_busqueda = ft.TextField(
            label="Buscar canción o artista",
            width=320,
            bgcolor="#282828",
            border_color="#535353",
            focused_border_color="#1DB954",
            color="#FFFFFF",
            label_style=ft.TextStyle(color="#b3b3b3"),
            on_submit=self.buscar,
            suffix=ft.IconButton(
                icon=ft.icons.SEARCH,
                icon_color="#1DB954",
                on_click=self.buscar,
            ),
        )

        self.controls = [
            ft.Container(
                content=ft.Row(
                    controls=[
                        ft.IconButton(
                            icon=ft.icons.ARROW_BACK,
                            icon_color="#FFFFFF",
                            on_click=lambda e: self.on_volver(),
                        ),
                        ft.Text(
                            "Proponer canción",
                            size=18,
                            weight=ft.FontWeight.BOLD,
                            color="#FFFFFF",
                        ),
                    ],
                ),
                padding=ft.padding.symmetric(horizontal=16, vertical=12),
                bgcolor="#1a1a1a",
                width=self._page.width,
            ),

            ft.Container(height=20),
            self.input_busqueda,
            ft.Container(height=8),
            self.status,
            ft.Container(height=8),

            ft.Container(
                content=self.resultados,
                expand=True,
                padding=ft.padding.symmetric(horizontal=16),
            ),
        ]

    def buscar(self, e):
        query = self.input_busqueda.value.strip()
        if not query:
            return

        self.status.value = "Buscando..."
        self.resultados.controls.clear()
        self._page.update()

        try:
            sp = self.state["sp"]
            canciones = buscar_canciones(sp, query)

            if not canciones:
                self.status.value = "No se encontraron resultados"
                self._page.update()
                return

            self.status.value = f"{len(canciones)} resultados"

            for cancion in canciones:
                self.resultados.controls.append(
                    self.construir_resultado(cancion)
                )

            self._page.update()

        except Exception as ex:
            self.status.value = f"Error al buscar: {ex}"
            self._page.update()

    def construir_resultado(self, cancion: dict) -> ft.Container:
        def proponer(e, c=cancion):
            self.proponer_cancion(c)

        duracion_seg = cancion["duracion_ms"] // 1000
        minutos = duracion_seg // 60
        segundos = duracion_seg % 60
        duracion_str = f"{minutos}:{segundos:02d}"

        imagen = ft.Container(
            width=48,
            height=48,
            bgcolor="#535353",
            border_radius=6,
            content=ft.Icon(ft.icons.MUSIC_NOTE, color="#b3b3b3", size=24),
        )

        if cancion.get("imagen"):
            imagen = ft.Image(
                src=cancion["imagen"],
                width=48,
                height=48,
                fit=ft.ImageFit.COVER,
                border_radius=ft.BorderRadius(6, 6, 6, 6),
            )

        return ft.Container(
            content=ft.Row(
                controls=[
                    imagen,
                    ft.Column(
                        controls=[
                            ft.Text(
                                cancion["nombre"],
                                size=14,
                                weight=ft.FontWeight.BOLD,
                                color="#FFFFFF",
                                max_lines=1,
                                overflow=ft.TextOverflow.ELLIPSIS,
                            ),
                            ft.Text(
                                f"{cancion['artista']} · {cancion['album']}",
                                size=12,
                                color="#b3b3b3",
                                max_lines=1,
                                overflow=ft.TextOverflow.ELLIPSIS,
                            ),
                            ft.Text(
                                duracion_str,
                                size=11,
                                color="#535353",
                            ),
                        ],
                        spacing=2,
                        expand=True,
                    ),
                    ft.ElevatedButton(
                        text="Proponer",
                        bgcolor="#1DB954",
                        color="#FFFFFF",
                        height=34,
                        on_click=proponer,
                    ),
                ],
                spacing=12,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.padding.all(12),
            bgcolor="#282828",
            border_radius=10,
            border=ft.border.all(1, "#333333"),
        )

    def proponer_cancion(self, cancion: dict):
        try:
            codigo = self.state["grupo"]
            user_id = self.state["usuario"]["id"]

            propuesta = {
                "nombre": cancion["nombre"],
                "artista": cancion["artista"],
                "album": cancion["album"],
                "uri": cancion["uri"],
                "imagen": cancion.get("imagen", ""),
                "propuesto_por": user_id,
            }

            proponer_cancion(codigo, propuesta)

            self.status.value = f"✓ '{cancion['nombre']}' enviada a votación"
            self.resultados.controls.clear()
            self._page.update()

            import time
            time.sleep(1.5)
            self.on_volver()

        except Exception as ex:
            self.status.value = f"Error al proponer: {ex}"
            self._page.update()