import flet as ft
from firebase.db import crear_grupo, unirse_grupo, db


class HomeScreen(ft.Column):
    def __init__(self, page: ft.Page, state: dict, on_entrar_grupo):
        super().__init__()

        self._page = page
        self.state = state
        self.on_entrar_grupo = on_entrar_grupo

        self.expand = True
        self.alignment = ft.MainAxisAlignment.START
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.spacing = 0

        usuario = state["usuario"]

        self.lista_grupos = ft.Column(
            spacing=8,
            scroll=ft.ScrollMode.AUTO,
        )

        self.mensaje = ft.Text("", color="#ff4444", size=13)

        # Panel de crear/unirse, oculto por defecto
        self.input_nombre_grupo = ft.TextField(
            label="Nombre del grupo",
            width=300,
            bgcolor="#282828",
            border_color="#535353",
            focused_border_color="#1DB954",
            color="#FFFFFF",
            label_style=ft.TextStyle(color="#b3b3b3"),
        )

        self.input_codigo = ft.TextField(
            label="Código del grupo (ej: XKQT)",
            width=300,
            bgcolor="#282828",
            border_color="#535353",
            focused_border_color="#1DB954",
            color="#FFFFFF",
            label_style=ft.TextStyle(color="#b3b3b3"),
        )

        self.panel_nuevo = ft.Container(
            visible=False,
            content=ft.Column(
                controls=[
                    ft.Container(height=24),
                    ft.Text("Crear un grupo nuevo",
                            size=16,
                            weight=ft.FontWeight.BOLD,
                            color="#FFFFFF"),
                    ft.Container(height=8),
                    self.input_nombre_grupo,
                    ft.Container(height=8),
                    ft.ElevatedButton(
                        text="Crear grupo",
                        bgcolor="#1DB954",
                        color="#FFFFFF",
                        width=300,
                        height=44,
                        on_click=self.crear_grupo,
                    ),
                    ft.Container(height=24),
                    ft.Divider(color="#282828"),
                    ft.Container(height=24),
                    ft.Text("Unirse a un grupo existente",
                            size=16,
                            weight=ft.FontWeight.BOLD,
                            color="#FFFFFF"),
                    ft.Container(height=8),
                    self.input_codigo,
                    ft.Container(height=8),
                    ft.ElevatedButton(
                        text="Unirse",
                        bgcolor="#282828",
                        color="#FFFFFF",
                        width=300,
                        height=44,
                        on_click=self.unirse_grupo,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        )

        self.controls = [
            # Cabecera
            ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Icon(ft.icons.ACCOUNT_CIRCLE,
                                size=40, color="#1DB954"),
                        ft.Column(
                            controls=[
                                ft.Text(
                                    f"Hola, {usuario['nombre']}",
                                    size=18,
                                    weight=ft.FontWeight.BOLD,
                                    color="#FFFFFF",
                                ),
                                ft.Text(
                                    usuario["id"],
                                    size=12,
                                    color="#b3b3b3",
                                ),
                            ],
                            spacing=2,
                            expand=True,
                        ),
                        ft.IconButton(
                            icon=ft.icons.ADD_CIRCLE_OUTLINE,
                            icon_color="#1DB954",
                            tooltip="Crear o unirse a un grupo",
                            on_click=self.toggle_panel,
                        ),
                    ],
                    spacing=12,
                ),
                padding=ft.padding.all(24),
                width=self._page.width,
                bgcolor="#1a1a1a",
            ),

            ft.Container(height=16),

            # Mis grupos
            ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Text(
                            "Mis grupos",
                            size=16,
                            weight=ft.FontWeight.BOLD,
                            color="#FFFFFF",
                        ),
                        ft.Container(height=8),
                        self.lista_grupos,
                    ],
                ),
                padding=ft.padding.symmetric(horizontal=24),
                width=self._page.width,
            ),

            self.panel_nuevo,
            ft.Container(height=8),
            self.mensaje,
        ]

    def did_mount(self):
        self.cargar_grupos()

    def cargar_grupos(self):
        """
        Busca en Firestore todos los grupos donde
        el usuario actual es miembro.
        """
        user_id = self.state["usuario"]["id"]
        self.lista_grupos.controls.clear()

        try:
            grupos = db.collection("grupos")\
                       .where("miembros", "array_contains", user_id)\
                       .stream()

            encontrados = False
            for grupo in grupos:
                encontrados = True
                datos = grupo.to_dict()
                codigo = grupo.id
                self.lista_grupos.controls.append(
                    self.construir_tarjeta_grupo(codigo, datos)
                )

            if not encontrados:
                self.lista_grupos.controls.append(
                    ft.Text(
                        "Todavía no perteneces a ningún grupo.\n"
                        "Pulsa + para crear o unirte a uno.",
                        color="#b3b3b3",
                        size=14,
                        text_align=ft.TextAlign.CENTER,
                    )
                )

        except Exception as ex:
            self.lista_grupos.controls.append(
                ft.Text(f"Error al cargar grupos: {ex}",
                        color="#ff4444", size=13)
            )

        self._page.update()

    def construir_tarjeta_grupo(self, codigo: str, datos: dict) -> ft.Container:
        num_miembros = len(datos.get("miembros", []))
        nombre = datos.get("nombre", codigo)

        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Icon(ft.icons.QUEUE_MUSIC,
                            color="#1DB954", size=32),
                    ft.Column(
                        controls=[
                            ft.Text(
                                nombre,
                                size=15,
                                weight=ft.FontWeight.BOLD,
                                color="#FFFFFF",
                            ),
                            ft.Text(
                                f"Código: {codigo}  ·  {num_miembros} miembro{'s' if num_miembros != 1 else ''}",
                                size=12,
                                color="#b3b3b3",
                            ),
                        ],
                        spacing=3,
                        expand=True,
                    ),
                    ft.IconButton(
                        icon=ft.icons.ARROW_FORWARD_IOS,
                        icon_color="#b3b3b3",
                        on_click=lambda e, c=codigo: self.on_entrar_grupo(c),
                    ),
                ],
                spacing=12,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.padding.all(16),
            bgcolor="#282828",
            border_radius=12,
            border=ft.border.all(1, "#333333"),
            on_click=lambda e, c=codigo: self.on_entrar_grupo(c),
        )

    def toggle_panel(self, e):
        """Muestra u oculta el panel de crear/unirse."""
        self.panel_nuevo.visible = not self.panel_nuevo.visible
        self._page.update()

    def crear_grupo(self, e):
        nombre = self.input_nombre_grupo.value.strip()

        if not nombre:
            self.mensaje.value = "Escribe un nombre para el grupo"
            self._page.update()
            return

        try:
            sp = self.state["sp"]
            user_id = self.state["usuario"]["id"]

            from auth.spotify_auth import crear_playlist_grupo
            playlist_id = crear_playlist_grupo(sp, nombre)

            from firebase.db import crear_grupo as _crear_grupo
            codigo = _crear_grupo(nombre, user_id, playlist_id)

            self.on_entrar_grupo(codigo)

        except Exception as ex:
            self.mensaje.value = f"Error al crear el grupo: {ex}"
            self._page.update()

    def unirse_grupo(self, e):
        codigo = self.input_codigo.value.strip().upper()

        if len(codigo) != 4:
            self.mensaje.value = "El código debe tener 4 letras"
            self._page.update()
            return

        try:
            user_id = self.state["usuario"]["id"]

            from firebase.db import unirse_grupo as _unirse_grupo
            exito = _unirse_grupo(codigo, user_id)

            if not exito:
                self.mensaje.value = "Código incorrecto, no existe ese grupo"
                self._page.update()
                return

            self.on_entrar_grupo(codigo)

        except Exception as ex:
            self.mensaje.value = f"Error al unirse: {ex}"
            self._page.update()