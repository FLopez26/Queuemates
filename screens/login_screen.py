import flet as ft
import threading
from auth.spotify_auth import get_spotify_client, obtener_perfil


class LoginScreen(ft.Column):
    def __init__(self, page: ft.Page, on_login_success):
        super().__init__()

        self._page = page
        self.on_login_success = on_login_success

        self.expand = True
        self.alignment = ft.MainAxisAlignment.CENTER
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.spacing = 24

        self.status = ft.Text(
            "",
            color="#b3b3b3",
            size=14,
        )

        self.boton_login = ft.ElevatedButton(
            text="Entrar con Spotify",
            bgcolor="#1DB954",
            color="#FFFFFF",
            width=220,
            height=48,
            on_click=self.hacer_login,
        )

        self.controls = [
            ft.Icon(ft.icons.QUEUE_MUSIC, size=80, color="#1DB954"),
            ft.Text(
                "QueueMates",
                size=32,
                weight=ft.FontWeight.BOLD,
                color="#FFFFFF",
            ),
            ft.Text(
                "Votad juntos qué suena a continuación",
                size=16,
                color="#b3b3b3",
            ),
            self.boton_login,
            self.status,
        ]

    def did_mount(self):
        """
        Flet llama a este método cuando el control ya está
        montado en la página. Es el momento seguro para
        arrancar tareas en segundo plano.
        """
        threading.Thread(target=self._login_automatico, daemon=True).start()

    def _login_automatico(self):
        try:
            sp = get_spotify_client()
            usuario = obtener_perfil(sp)
            self.on_login_success(sp, usuario)
        except Exception:
            pass

    def hacer_login(self, e):
        self.boton_login.disabled = True
        self.status.value = "Abriendo Spotify..."
        self._page.update()

        threading.Thread(target=self._hacer_login_thread, daemon=True).start()

    def _hacer_login_thread(self):
        try:
            sp = get_spotify_client()
            usuario = obtener_perfil(sp)
            self.on_login_success(sp, usuario)
        except Exception as ex:
            self.boton_login.disabled = False
            self.status.value = f"Error al conectar: {ex}"
            self._page.update()