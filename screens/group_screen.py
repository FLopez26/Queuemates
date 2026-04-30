import flet as ft
from firebase.db import escuchar_votaciones, votar, obtener_grupo


class GroupScreen(ft.Column):
    def __init__(self, page: ft.Page, state: dict, on_volver):
        super().__init__()

        self._page = page
        self.state = state
        self.on_volver = on_volver
        self.watcher = None

        self.expand = True
        self.alignment = ft.MainAxisAlignment.START
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.spacing = 0

        codigo = state["grupo"]
        grupo = obtener_grupo(codigo)

        self.lista_votaciones = ft.Column(
            spacing=12,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )

        self.controls = [
            ft.Container(
                content=ft.Row(
                    controls=[
                        ft.IconButton(
                            icon=ft.icons.ARROW_BACK,
                            icon_color="#FFFFFF",
                            on_click=lambda e: self.salir(),
                        ),
                        ft.Column(
                            controls=[
                                ft.Text(
                                    grupo.get("nombre", codigo),
                                    size=18,
                                    weight=ft.FontWeight.BOLD,
                                    color="#FFFFFF",
                                ),
                                ft.Text(
                                    f"Código: {codigo}  ·  "
                                    f"{len(grupo.get('miembros', []))} miembros",
                                    size=12,
                                    color="#b3b3b3",
                                ),
                            ],
                            spacing=2,
                            expand=True,
                        ),
                        ft.ElevatedButton(
                            text="+ Canción",
                            bgcolor="#1DB954",
                            color="#FFFFFF",
                            height=36,
                            on_click=self.abrir_busqueda,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.START,
                ),
                padding=ft.padding.symmetric(horizontal=16, vertical=12),
                bgcolor="#1a1a1a",
                width=self._page.width,
            ),

            ft.Container(height=12),

            ft.Container(
                content=self.lista_votaciones,
                expand=True,
                padding=ft.padding.symmetric(horizontal=16),
            ),
        ]

        self.watcher = escuchar_votaciones(codigo, self.on_votaciones_actualizadas)

    def on_votaciones_actualizadas(self, docs, changes, read_time):
        self.lista_votaciones.controls.clear()

        if not docs:
            self.lista_votaciones.controls.append(
                ft.Container(
                    content=ft.Text(
                        "Nadie ha propuesto canciones todavía.\n"
                        "¡Pulsa + Canción para ser el primero!",
                        color="#b3b3b3",
                        text_align=ft.TextAlign.CENTER,
                        size=14,
                    ),
                    alignment=ft.alignment.center,
                    padding=ft.padding.all(40),
                )
            )
        else:
            for doc in docs:
                datos = doc.to_dict()
                datos["id"] = doc.id
                self.lista_votaciones.controls.append(
                    self.construir_tarjeta(datos)
                )

        self._page.update()

    def construir_tarjeta(self, datos: dict) -> ft.Container:
        user_id = self.state["usuario"]["id"]
        estado = datos.get("estado", "pendiente")
        votos_si = datos.get("votos_si", [])
        votos_no = datos.get("votos_no", [])
        ya_vote = user_id in votos_si or user_id in votos_no
        votacion_id = datos["id"]

        colores_estado = {
            "pendiente": "#535353",
            "aprobada": "#1DB954",
            "rechazada": "#ff4444",
        }
        color_borde = colores_estado.get(estado, "#535353")

        badges = {
            "pendiente": ("Votando", "#535353", "#FFFFFF"),
            "aprobada":  ("✓ Aprobada", "#1DB954", "#FFFFFF"),
            "rechazada": ("✗ Rechazada", "#ff4444", "#FFFFFF"),
        }
        badge_texto, badge_bg, badge_color = badges.get(
            estado, ("Votando", "#535353", "#FFFFFF")
        )

        if estado == "pendiente" and not ya_vote:
            botones = [
                ft.ElevatedButton(
                    text=f"👍 Sí ({len(votos_si)})",
                    bgcolor="#1DB954",
                    color="#FFFFFF",
                    height=36,
                    on_click=lambda e, vid=votacion_id: self.votar(vid, True),
                ),
                ft.ElevatedButton(
                    text=f"👎 No ({len(votos_no)})",
                    bgcolor="#282828",
                    color="#FFFFFF",
                    height=36,
                    on_click=lambda e, vid=votacion_id: self.votar(vid, False),
                ),
            ]
        else:
            botones = [
                ft.Text(
                    f"👍 {len(votos_si)}   👎 {len(votos_no)}",
                    color="#b3b3b3",
                    size=13,
                ),
            ]

        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Column(
                                controls=[
                                    ft.Text(
                                        datos.get("nombre", ""),
                                        size=15,
                                        weight=ft.FontWeight.BOLD,
                                        color="#FFFFFF",
                                    ),
                                    ft.Text(
                                        datos.get("artista", ""),
                                        size=13,
                                        color="#b3b3b3",
                                    ),
                                    ft.Text(
                                        f"Propuesta por {datos.get('propuesto_por', '')}",
                                        size=11,
                                        color="#535353",
                                    ),
                                ],
                                spacing=3,
                                expand=True,
                            ),
                            ft.Container(
                                content=ft.Text(
                                    badge_texto,
                                    size=11,
                                    color=badge_color,
                                    weight=ft.FontWeight.BOLD,
                                ),
                                bgcolor=badge_bg,
                                padding=ft.padding.symmetric(
                                    horizontal=8, vertical=4
                                ),
                                border_radius=12,
                            ),
                        ],
                    ),
                    ft.Row(controls=botones, spacing=8),
                ],
                spacing=10,
            ),
            padding=ft.padding.all(16),
            bgcolor="#282828",
            border_radius=12,
            border=ft.border.all(1, color_borde),
        )

    def votar(self, votacion_id: str, voto: bool):
        try:
            codigo = self.state["grupo"]
            user_id = self.state["usuario"]["id"]

            from firebase.db import votar as _votar, obtener_playlist_id
            from auth.spotify_auth import anadir_a_playlist

            # Obtén el estado resultante del voto
            estado = _votar(codigo, votacion_id, user_id, voto)

            if estado == "aprobada":
                # Busca el URI de la canción en Firestore
                from firebase.db import db
                doc = db.collection("grupos").document(codigo)\
                        .collection("votaciones").document(votacion_id)\
                        .get().to_dict()

                playlist_id = obtener_playlist_id(codigo)
                track_uri = doc.get("uri", "")

                if playlist_id and track_uri:
                    sp = self.state["sp"]
                    anadir_a_playlist(sp, playlist_id, track_uri)

        except Exception as ex:
            print(f"Error al votar: {ex}")

    def abrir_busqueda(self, e):
        from screens.search_screen import SearchScreen
        self.salir_watcher()
        self._page.controls.clear()
        self._page.add(SearchScreen(self._page, self.state, self.volver_desde_busqueda))
        self._page.update()

    def volver_desde_busqueda(self):
        self._page.controls.clear()
        self._page.add(GroupScreen(self._page, self.state, self.on_volver))
        self._page.update()

    def salir(self):
        self.salir_watcher()
        self.on_volver()

    def salir_watcher(self):
        if self.watcher:
            self.watcher.unsubscribe()
            self.watcher = None