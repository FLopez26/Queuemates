import flet as ft
from screens.login_screen import LoginScreen
from screens.home_screen import HomeScreen


def main(page: ft.Page):
    page.title = "QueueMates"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 0
    page.bgcolor = "#121212"

    state = {
        "sp": None,
        "usuario": None,
        "grupo": None,
    }

    def navegar(func):
        """
        Wrapper que ejecuta cualquier cambio de pantalla
        en el hilo principal de Flet de forma segura.
        """
        page.controls.clear()
        func()
        page.update()

    def ir_a_home(sp, usuario):
        state["sp"] = sp
        state["usuario"] = usuario
        def _():
            page.controls.clear()
            page.add(HomeScreen(page, state, ir_a_grupo))
            page.update()
        page.run_thread(_)

    def ir_a_grupo(codigo_grupo):
        from screens.group_screen import GroupScreen
        state["grupo"] = codigo_grupo
        def _():
            page.controls.clear()
            page.add(GroupScreen(page, state, volver_a_home))
            page.update()
        page.run_thread(_)

    def volver_a_home():
        state["grupo"] = None
        def _():
            page.controls.clear()
            page.add(HomeScreen(page, state, ir_a_grupo))
            page.update()
        page.run_thread(_)

    page.add(LoginScreen(page, ir_a_home))


ft.app(main)