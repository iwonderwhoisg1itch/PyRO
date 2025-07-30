import win32gui
import win32process
import os
import ujson as json
import psutil
import time
import sys
import urllib3
import requests
import subprocess
import flet as ft
import threading
import asyncio
import random
from math import floor
from urllib.request import urlopen
from pypresence import Presence
from threading import Thread
from seliware import Seliware

if os.path.exists("upd.bat"):
    try:
        os.remove("udp.bat")
    except:
        pass

class ExecutorAPI:
    def __init__(self, api):
        self.selected_api = api
        self.loaded_api = None
        self.auto_inject_enabled = False
        self.auto_inject_thread = None

    def load_api(self):
        self.loaded_api = Seliware

    def init_api(self):
        if self.selected_api == "Seliware":
            self.loaded_api.initialize()

    def getapiname(self):
        return self.selected_api

    def getrawapiver(self):
        if self.selected_api == "Seliware":
            return self.loaded_api.version

    def getapiver(self):
        if self.selected_api == "Seliware":
            ver = self.loaded_api.version
            return ver.split("-", 1)[-1] if "-" in ver else ver

    def Inject(self):
        global rbx_pids

        found = [proc.pid for proc in psutil.process_iter(['name']) if proc.info['name'] == "RobloxPlayerBeta.exe"]

        rbx_pids = [pid for pid in rbx_pids if psutil.pid_exists(pid)]

        for pid in found:
            if pid not in rbx_pids:
                try:
                    if self.selected_api == "Seliware":
                        self.loaded_api.inject(pid)
                    rbx_pids.append(pid)
                    print(f"Injected into PID {pid}")
                except Exception as e:
                    print(f"Injection failed for PID {pid}: {e}")

    def AutoInject(self, enabled: bool):
        if enabled == self.auto_inject_enabled:
            return

        self.auto_inject_enabled = enabled

        if enabled:
            if not self.auto_inject_thread or not self.auto_inject_thread.is_alive():
                self.auto_inject_thread = Thread(target=self._auto_inject_loop, daemon=True)
                self.auto_inject_thread.start()

    def _auto_inject_loop(self):
        global rbx_pids
        previous_pids = []

        while self.auto_inject_enabled:
            current_pids = [proc.pid for proc in psutil.process_iter(['name']) if proc.info['name'] == "RobloxPlayerBeta.exe"]

            new_pids = [pid for pid in current_pids if pid not in previous_pids]

            for pid in new_pids:
                if pid in rbx_pids:
                    continue
                if self._wait_for_window(pid, timeout=15):
                    try:
                        if self.selected_api == "Seliware":
                            self.loaded_api.inject(pid)
                        rbx_pids.append(pid)
                    except Exception as e:
                        print(f"Injection failed for PID {pid}: {e}")
                else:
                    print(f"No window found for PID {pid}, skipping injection")

            previous_pids = current_pids
            time.sleep(1)

    def _wait_for_window(self, pid, timeout=15):
        def enum_handler(hwnd, result_list):
            try:
                _, found_pid = win32process.GetWindowThreadProcessId(hwnd)
                if found_pid == pid and win32gui.IsWindowVisible(hwnd):
                    result_list.append(hwnd)
            except:
                pass

        for _ in range(timeout * 10):
            hwnds = []
            win32gui.EnumWindows(enum_handler, hwnds)
            if hwnds:
                return True
            time.sleep(0.1)

        return False

    def Execute(self, scr):
        if self.selected_api == "Seliware":
            self.loaded_api.execute(scr)

class DiscordRPC:
    def __init__(self, exec_api):
        self.rpc = None
        self.exec_api = exec_api
        self.client_id = "1364911632773545984"
        self.running = False
        self.current_tab = "Main"
        self.current_editor_tab = ""
        self.time = int(time.time())

    def start(self):
        try:
            self.rpc = Presence(self.client_id)
            self.rpc.connect()
            self.running = True
            Thread(target=self.update_presence, daemon=True).start()
        except Exception as e:
            print(f"Discord RPC error: {e}")

    def update_presence(self):
        while self.running:
            try:
                details = ""
                if self.current_tab == "Main":
                    details = f"Editing: {self.current_editor_tab[:15]}..." if self.current_editor_tab else "Editing scripts..."
                elif self.current_tab == "Options":
                    details = "Adjusting settings..."

                self.rpc.update(
                    state=f"{ver} | Seliware v{self.exec_api.getapiver()}",
                    details=details,
                    large_image="icon",
                    large_text="PyRO",
                    start=self.time,
                    buttons=[
                        {"label": "GitHub", "url": "https://github.com/iwonderwhoisg1itch/PyRO"},
                        {"label": "Discord", "url": "https://discord.gg/UWtjQayY9q"}
                    ]
                )
            except Exception as e:
                print(f"RPC update error: {e}")
            time.sleep(3)

    def set_tab(self, tab_name):
        self.current_tab = tab_name

    def set_editor_tab(self, tab_name):
        self.current_editor_tab = tab_name

    def close(self):
        self.running = False
        if self.rpc:
            self.rpc.close()

def get_base_path():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))

base_dir = get_base_path()
bin_dir = os.path.dirname(os.path.abspath(__file__))
dll_path = os.path.join(bin_dir, "SeliwareAPI.dll")
scripts_dir = os.path.join(base_dir, "scripts")
tabs_dir = os.path.join(base_dir, "tabs")
settings_file = os.path.join(base_dir, "settings.json")

ver = "v0.7.2"

splashs  = ["smart man with glasses download",
            "Умный в гору не пойдет, умный человек скачать обои - Ян Топлесс",
            "Made by G1itch, Powered by Autism :troll:",
            "Free Seliware 💯💯💯💯 REAL!!! 🤑🤑🤑🤑",
            "i love flet <3",
            "Fun fact! This ui is made by Seliware staff member!",
            "Fun fact! This ui runs custom custom ui api!",
            "i farted",
            "getwave.wtf >>>>> seliware.com",
            "Сосал?",
            "What kind of hottie is using this ui?",
            "Also try TRX ui made by my friend!",
            "Also try KRNL old ui made by my friend!",
            "Also try KRNL new ui made by my friend!",
            "Also try SynX custom ui!",
            "We each got… fifteen dollars. Oh, and a quarter. Don’t forget the quarter",
            "ъуъ",
            "Я ВЫЕБАЛ ХЛЕБ!!!!!!!!!!!!",
            "a = '123' print('a')",
            "Скачать армяне",
            "There was an problem while processing your request: Authentication failed. Subscription ended?"]

rbx_pids = []

os.makedirs(scripts_dir, exist_ok=True)
os.makedirs(tabs_dir, exist_ok=True)

class ThemeManager:
    def __init__(self):
        self.themes = {
            "Blue":    {"primary": ft.Colors.BLUE_800,    "secondary": ft.Colors.BLUE_300,    "accent": ft.Colors.BLUE_600},
            "Red":     {"primary": ft.Colors.RED_800,     "secondary": ft.Colors.RED_300,     "accent": ft.Colors.RED_600},
            "Green":   {"primary": ft.Colors.GREEN_800,   "secondary": ft.Colors.GREEN_300,   "accent": ft.Colors.GREEN_600},
            "Purple":  {"primary": ft.Colors.PURPLE_800,  "secondary": ft.Colors.PURPLE_300,  "accent": ft.Colors.PURPLE_600},
            "Orange":  {"primary": ft.Colors.ORANGE_800,  "secondary": ft.Colors.ORANGE_300,  "accent": ft.Colors.ORANGE_600},
            "Amber":   {"primary": ft.Colors.AMBER_800,   "secondary": ft.Colors.AMBER_300,   "accent": ft.Colors.AMBER_600},
            "Cyan":    {"primary": ft.Colors.CYAN_800,    "secondary": ft.Colors.CYAN_300,    "accent": ft.Colors.CYAN_600},
            "Brown":   {"primary": ft.Colors.BROWN_800,   "secondary": ft.Colors.BROWN_300,   "accent": ft.Colors.BROWN_600},
            "Blue Grey": {"primary": ft.Colors.BLUE_GREY_800, "secondary": ft.Colors.BLUE_GREY_300, "accent": ft.Colors.BLUE_GREY_600},
            "Pink":    {"primary": ft.Colors.PINK_800,    "secondary": ft.Colors.PINK_300,    "accent": ft.Colors.PINK_600},
            "Teal":    {"primary": ft.Colors.TEAL_800,    "secondary": ft.Colors.TEAL_300,    "accent": ft.Colors.TEAL_600},
            "Deep Purple": {"primary": ft.Colors.DEEP_PURPLE_800, "secondary": ft.Colors.DEEP_PURPLE_300, "accent": ft.Colors.DEEP_PURPLE_600},
            "Light Green": {"primary": ft.Colors.LIGHT_GREEN_800, "secondary": ft.Colors.LIGHT_GREEN_300, "accent": ft.Colors.LIGHT_GREEN_600},
            "Lime":    {"primary": ft.Colors.LIME_800,    "secondary": ft.Colors.LIME_300,    "accent": ft.Colors.LIME_600},
        }

        self.current_theme = "Blue"
    
    def get_theme_colors(self, theme_name=None):
        theme_name = theme_name or self.current_theme
        return self.themes.get(theme_name, self.themes["Blue"])
    
    def set_theme(self, theme_name):
        if theme_name in self.themes:
            self.current_theme = theme_name
            return True
        return False

class PyRO:
    def __init__(self, page: ft.Page):
        self.page = page
        self.theme_manager = ThemeManager()
        self.setup_window()
        self.ExecutorAPI = ExecutorAPI("Seliware")

        self.toast_overlay = ft.Stack(expand=True)
        self.page.overlay.append(self.toast_overlay)
        
        page.theme = ft.Theme()

        self.tabs = {}
        self.current_tab_index = 0
        self.current_main_tab = "Main"
        
        self.show_toast("Loading", None)
        self.ExecutorAPI.load_api()
        self.ExecutorAPI.init_api()

        self.rpc = DiscordRPC(self.ExecutorAPI)

        self.setup_ui()
        self.file_picker = ft.FilePicker(on_result=self.on_file_selected)
        self.save_picker = ft.FilePicker(on_result=self.on_save_selected)
        self.page.overlay.extend([self.file_picker, self.save_picker])
        self.load_settings()
        
        threading.Thread(target=self.load_tabs_thread, daemon=True).start()
        
        self.page.on_window_event = self.on_window_event
        self.rpc.start()
        self.apply_theme()
        self.show_toast("Loaded!", ft.Icons.CHECK)
        self.ExecutorAPI.loaded_api.injected_event.append(self.injected)

    def load_tabs_thread(self):
        self.page.run_task(self._load_tabs_async)

    async def _load_tabs_async(self):
        if not os.path.exists(tabs_dir):
            self.add_tab()
            self.page.update()
            return

        try:
            tab_files = [f for f in os.listdir(tabs_dir) if f.endswith('.lua')]
            
            if not tab_files:
                self.add_tab()
                self.page.update()
                return

            loaded_tabs = []
            for tab_file in tab_files:
                tab_path = os.path.join(tabs_dir, tab_file)
                try:
                    with open(tab_path, "r", encoding="utf-8") as f:
                        content = f.read()
                    tab_name = os.path.splitext(tab_file)[0]
                    loaded_tabs.append((tab_name, content, tab_path))
                except Exception as e:
                    print(f"Error loading tab {tab_file}: {e}")

            for tab_name, content, tab_path in loaded_tabs:
                self.add_tab(tab_name, content, tab_path)

            if not self.tabs:
                self.add_tab()

        except Exception as e:
            self.show_toast(f"Error loading tabs: {e}", ft.Icons.ERROR)
            self.add_tab()

        self.page.update()

    def injected(self):
        self.show_toast("Injected!", ft.Icons.CHECK)

    def show_toast(self, text: str, icon=None):
        colors = self.theme_manager.get_theme_colors()
        
        toast_container = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Icon(icon, color=ft.Colors.WHITE) if icon else ft.Container(width=0),
                    ft.Text(text, color=ft.Colors.WHITE),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            padding=15,
            border_radius=5,
            width=250,
            opacity=0,
            animate_opacity=300,
            top=20,
            bgcolor=colors["primary"]
        )
        
        self.toast_overlay.controls.append(toast_container)
        
        page_width = self.page.width
        toast_container.left = (page_width - 250) / 2
        
        toast_container.opacity = 1
        self.page.update()
        
        def hide_toast():
            toast_container.opacity = 0
            self.page.update()
            
            def remove_toast():
                if toast_container in self.toast_overlay.controls:
                    self.toast_overlay.controls.remove(toast_container)
                    self.page.update()
            
            threading.Timer(0.3, remove_toast).start()
        
        threading.Timer(1.5, hide_toast).start()

    def setup_window(self):
        self.page.title = f"PyRO {ver} | {random.choice(splashs)}"
        self.page.window_width = 1000
        self.page.window_height = 700
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.window_prevent_close = True
    
    def setup_ui(self):
        Colors = self.theme_manager.get_theme_colors()
        self.setup_main_tab()
        self.setup_options_tab()
        
        self.content_area = ft.Column(expand=True)
        self.page.add(self.content_area)
        for tab in self.tabs.values():
            tab["text_field"].cursor_color = Colors["accent"]
            tab["text_field"].selection_color = Colors["secondary"]
        self.show_tab_content("Main")
    
    def setup_main_tab(self):
        self.script_list = ft.ListView(expand=True)
        self.update_scripts()
        
        script_panel = ft.Container(
            content=ft.Column(
                controls=[
                    self.script_list
                ],
                expand=True
            ),
            width=200,
            padding=10
        )

        self.tab_headers = ft.Row(scroll=True, expand=True, height=40)
        self.tab_contents = ft.Column(expand=True)

        self.add_tab_button = ft.IconButton(
            ft.Icons.ADD,
            icon_color=self.theme_manager.get_theme_colors()["secondary"],
            on_click=lambda _: self.add_tab()
        )

        editor_panel = ft.Column(
            controls=[
                ft.Row([
                    self.tab_headers,
                    self.add_tab_button
                ]),
                ft.Divider(),
                self.tab_contents,
                self.create_button_row()
            ],
            expand=True
        )

        self.main_tab_content = ft.Row(
            controls=[
                editor_panel,
                ft.VerticalDivider(width=1),
                script_panel
            ],
            expand=True
        )
    
    def create_button_row(self):
        Colors = self.theme_manager.get_theme_colors()
        return ft.Row(
            controls=[
                ft.Row(
                    controls=[
                        ft.ElevatedButton(
                            content=ft.Row([
                                ft.Icon(ft.Icons.PLAY_ARROW, color=ft.Colors.WHITE, size=20),
                                ft.Text("Execute", color=ft.Colors.WHITE)
                            ]),
                            on_click=self.execute_script,
                            style=ft.ButtonStyle(
                                bgcolor=Colors["primary"],
                                padding=ft.padding.symmetric(horizontal=15, vertical=15),
                                shape=ft.RoundedRectangleBorder(radius=5)
                            )
                        ),
                        
                        ft.OutlinedButton(
                            content=ft.Row([
                                ft.Icon(ft.Icons.CLEAR, color=Colors["secondary"], size=20),
                                ft.Text("Clear", color=Colors["secondary"])
                            ]),
                            on_click=self.clear_script,
                            style=ft.ButtonStyle(
                                side=ft.BorderSide(1, Colors["primary"]),
                                padding=ft.padding.symmetric(horizontal=15, vertical=15),
                                shape=ft.RoundedRectangleBorder(radius=5)
                            )
                        ),
                        
                        ft.OutlinedButton(
                            content=ft.Row([
                                ft.Icon(ft.Icons.FILE_OPEN, color=Colors["secondary"], size=20),
                                ft.Text("Open File", color=Colors["secondary"])
                            ]),
                            on_click=self.open_file_dialog,
                            style=ft.ButtonStyle(
                                side=ft.BorderSide(1, Colors["primary"]),
                                padding=ft.padding.symmetric(horizontal=15, vertical=15),
                                shape=ft.RoundedRectangleBorder(radius=5)
                            )
                        ),
                        
                        ft.OutlinedButton(
                            content=ft.Row([
                                ft.Icon(ft.Icons.SAVE, color=Colors["secondary"], size=20),
                                ft.Text("Save File", color=Colors["secondary"])
                            ]),
                            on_click=self.save_current_file,
                            style=ft.ButtonStyle(
                                side=ft.BorderSide(1, Colors["primary"]),
                                padding=ft.padding.symmetric(horizontal=15, vertical=15),
                                shape=ft.RoundedRectangleBorder(radius=5)
                            )
                        ),

                        ft.OutlinedButton(
                            content=ft.Row([
                                ft.Icon(ft.Icons.SETTINGS, color=Colors["secondary"], size=20),
                                ft.Text("Settings", color=Colors["secondary"])
                            ]),
                            on_click=lambda _: self.show_tab_content("Options"),
                            style=ft.ButtonStyle(
                                side=ft.BorderSide(1, Colors["primary"]),
                                padding=ft.padding.symmetric(horizontal=15, vertical=15),
                                shape=ft.RoundedRectangleBorder(radius=5)
                            )
                        ),
                    ],
                    spacing=10,
                    expand=True
                ),

                ft.ElevatedButton(
                    content=ft.Row([
                        ft.Icon(ft.Icons.LINK, color=ft.Colors.WHITE, size=20),
                        ft.Text("Attach", color=ft.Colors.WHITE)
                    ]),
                    on_click=lambda _: self.ExecutorAPI.Inject(),
                    style=ft.ButtonStyle(
                        bgcolor=Colors["primary"],
                        padding=ft.padding.symmetric(horizontal=15, vertical=15),
                        shape=ft.RoundedRectangleBorder(radius=5)
                    )
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            spacing=20,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )
    
    def toggle_auto_inject(self, value):
        self.ExecutorAPI.AutoInject(value)
        self.save_settings()

    def setup_options_tab(self):
        self.theme_dropdown = ft.Dropdown(
            options=[ft.dropdown.Option(theme) for theme in self.theme_manager.themes.keys()],
            value=self.theme_manager.current_theme,
            on_change=self.change_theme,
            width=200
        )
        
        self.auto_inject_switch = ft.Switch(
            label="Auto Attach",
            value=False,
            on_change=lambda e: self.toggle_auto_inject(e.control.value) 
        )
        
        self.options_tab_content = ft.Column(
            controls=[
                ft.Row([
                    ft.IconButton(
                        icon=ft.Icons.ARROW_BACK,
                        on_click=lambda _: self.show_tab_content("Main"),
                        tooltip="Back to main"
                    ),
                    ft.Text(
                        "Appearance Settings", 
                        size=24, 
                        weight=ft.FontWeight.BOLD,
                        font_family="Roboto"
                    ),
                ], alignment=ft.MainAxisAlignment.START),
                
                ft.Divider(),
                ft.Row([
                    ft.Text("Theme:", font_family="Roboto"),
                    self.theme_dropdown
                ]),
                ft.ElevatedButton(
                    "Apply Theme",
                    on_click=lambda _: self.apply_theme(),
                    icon=ft.Icons.COLOR_LENS,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=5),
                        padding=ft.padding.symmetric(horizontal=20, vertical=10)
                    )
                ),
                ft.Divider(),
                ft.Row([
                    ft.Text("Injection Settings", 
                           size=24, 
                           weight=ft.FontWeight.BOLD,
                           font_family="Roboto")
                ]),
                ft.Row([
                    self.auto_inject_switch
                ])
            ],
            spacing=20,
            expand=True
        )
    
    def change_theme(self, e):
        self.theme_manager.set_theme(self.theme_dropdown.value)
    
    def apply_theme(self):
        if self.theme_manager.set_theme(self.theme_dropdown.value):
            Colors = self.theme_manager.get_theme_colors()
            seed_color = Colors["primary"]
            
            self.page.theme = ft.Theme(
                color_scheme_seed=seed_color,
                color_scheme=ft.ColorScheme(
                    primary=Colors["primary"],
                    secondary=Colors["secondary"],
                    surface=ft.Colors.BLACK
                )
            )
            
            for tab in self.tabs.values():
                tab["text_field"].cursor_color = Colors["accent"]
                tab["text_field"].selection_color = Colors["secondary"]
            
            self.update_ui_theme()
            self.save_settings()
            self.page.update()
    
    def update_ui_theme(self):
        Colors = self.theme_manager.get_theme_colors()
        
        self.add_tab_button.icon_color = Colors["secondary"]

        for i, (name, tab) in enumerate(self.tabs.items()):
            tab["header"].bgcolor = (
                Colors["primary"] if i == self.current_tab_index 
                else ft.Colors.TRANSPARENT
            )
            close_btn = tab["header"].content.controls[2]
            if isinstance(close_btn, ft.IconButton):
                close_btn.icon_color = Colors["secondary"]
        
        button_row = self.create_button_row()
        if len(self.main_tab_content.controls) > 0 and len(self.main_tab_content.controls[0].controls) > 3:
            self.main_tab_content.controls[0].controls[3] = button_row
        
        self.page.update()
    
    def add_tab(self, name=None, content="", path=None):
        Colors = self.theme_manager.get_theme_colors()

        if name is None:
            tab_num = len(self.tabs) + 1
            name = f"Tab {tab_num}"
            while name in self.tabs:
                tab_num += 1
                name = f"Tab {tab_num}"

        text_field = ft.TextField(
            value=content,
            cursor_color=Colors["accent"],
            selection_color=Colors["secondary"],
            multiline=True,
            hint_text="Script goes here...",
            expand=True,
            border=ft.InputBorder.NONE,
            on_change=lambda e: self.save_tabs()
        )

        tab_text = ft.Text(name)
        tab_name_input = ft.TextField(
            value=name,
            visible=False,
            height=30,
            content_padding=ft.padding.symmetric(horizontal=10, vertical=5),
            on_submit=lambda e, old_name=name: self.rename_tab(old_name, e.control.value)
        )

        tab_click_area = ft.GestureDetector(
            content=ft.Container(content=tab_text),
            on_tap=lambda e, tab_name=name: self.switch_to_tab(tab_name),
            on_double_tap=lambda e, tf=tab_name_input, t=tab_text: self.toggle_rename(tf, t)
        )

        close_btn = ft.IconButton(
            icon=ft.Icons.CLOSE,
            icon_size=14,
            data=name,
            on_click=self.close_tab_click,
            icon_color=Colors["secondary"]
        )

        tab_header = ft.Container(
            content=ft.Row([tab_click_area, tab_name_input, close_btn]),
            padding=ft.padding.symmetric(horizontal=10, vertical=5),
            height=40,
            border_radius=5,
            data=name,
            bgcolor=ft.Colors.TRANSPARENT
        )

        content_container = ft.Container(
            content=text_field,
            expand=True,
            visible=False
        )

        self.tabs[name] = {
            "header": tab_header,
            "content": content_container,
            "text_field": text_field,
            "text": tab_text,
            "input": tab_name_input,
            "path": path,
            "saved": path is not None
        }

        self.update_tabs_ui()
        self.switch_to_tab(name)
        self.rpc.set_editor_tab(name)
        self.save_tabs()
    
    def update_tabs_ui(self):
        Colors = self.theme_manager.get_theme_colors()
        self.tab_headers.controls = [tab["header"] for tab in self.tabs.values()]
        self.tab_contents.controls = [tab["content"] for tab in self.tabs.values()]
        
        for i, tab in enumerate(self.tabs.values()):
            tab["content"].visible = (i == self.current_tab_index)
            tab["header"].bgcolor = (
                Colors["primary"] if i == self.current_tab_index
                else ft.Colors.TRANSPARENT
            )
        
        self.page.update()
    
    def switch_to_tab(self, tab_name):
        for i, name in enumerate(self.tabs.keys()):
            if name == tab_name:
                self.current_tab_index = i
                break
        
        self.update_tabs_ui()
        self.rpc.set_editor_tab(tab_name)
    
    def close_tab_click(self, e):
        self.close_tab(e.control.data)
    
    def close_tab(self, tab_name):
        tab = self.tabs.get(tab_name)
        if not tab:
            return

        if not tab["saved"] and tab["text_field"].value.strip():
            def handle_dialog(result):
                self.page.dialog.open = False
                self.page.update()
                if result:
                    self._remove_tab(tab_name)

            confirm_dialog = ft.AlertDialog(
                modal=True,
                title=ft.Text("Unsaved Changes"),
                content=ft.Text(f"Tab '{tab_name}' has unsaved changes. Close anyway?"),
                actions=[
                    ft.TextButton("Yes", on_click=lambda e: handle_dialog(True)),
                    ft.TextButton("No", on_click=lambda e: handle_dialog(False)),
                ],
                on_dismiss=lambda e: handle_dialog(False)
            )

            self.page.dialog = confirm_dialog
            if confirm_dialog not in self.page.controls:
                self.page.controls.append(confirm_dialog)
            confirm_dialog.open = True
            self.page.update()
        else:
            self._remove_tab(tab_name)

    def open_file_dialog(self, e=None):
        self.file_picker.pick_files(
            allow_multiple=False,
            file_type=ft.FilePickerFileType.CUSTOM,
            allowed_extensions=["lua", "txt"]
        )

    def on_file_selected(self, e: ft.FilePickerResultEvent):
        if e.files:
            file_path = e.files[0].path
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                script_name = os.path.basename(file_path)
                self.add_tab(f"Script: {script_name}", content, file_path)
                self.show_toast(f"Opened: {script_name}", ft.Icons.FILE_OPEN)
            except Exception as ex:
                self.show_toast(f"Open error: {ex}", ft.Icons.ERROR)

    def toggle_rename(self, text_field, text_display):
        text_field.visible = True
        text_display.visible = False
        self.page.update()

    def rename_tab(self, old_name, new_name):
        if not new_name or new_name in self.tabs:
            return
            
        tab = self.tabs.pop(old_name)
        
        if tab["path"] and os.path.exists(tab["path"]):
            try:
                new_path = os.path.join(tabs_dir, f"{new_name}.lua")
                os.rename(tab["path"], new_path)
                tab["path"] = new_path
            except Exception as e:
                self.show_toast(f"Error renaming file: {e}", ft.Icons.ERROR)
        
        tab["text"].value = new_name
        tab["input"].value = new_name
        tab["text"].visible = True
        tab["input"].visible = False
        tab["header"].data = new_name
        tab["header"].content.controls[-1].data = new_name
        self.tabs[new_name] = tab
        
        self.update_tabs_ui()
        self.rpc.set_editor_tab(new_name)
        self.save_tabs()

    def _remove_tab(self, tab_name):
        if tab_name not in self.tabs:
            return
            
        tab = self.tabs[tab_name]
        
        if tab["path"] and os.path.exists(tab["path"]):
            try:
                os.remove(tab["path"])
            except Exception as e:
                self.show_toast(f"Error deleting tab file: {e}", ft.Icons.ERROR)
        
        tab_index = list(self.tabs.keys()).index(tab_name)
        del self.tabs[tab_name]
        
        if self.current_tab_index >= tab_index:
            self.current_tab_index = max(0, self.current_tab_index - 1)
        
        if not self.tabs:
            self.add_tab()
        else:
            self.update_tabs_ui()
        
        self.save_tabs()
    
    def show_tab_content(self, tab_name):
        self.content_area.controls.clear()
        if tab_name == "Main":
            self.content_area.controls.append(self.main_tab_content)
        elif tab_name == "Scripts":
            self.content_area.controls.append(self.scripts_tab_content)
        elif tab_name == "Options":
            self.content_area.controls.append(self.options_tab_content)
        
        self.current_main_tab = tab_name
        self.rpc.set_tab(tab_name)
        self.page.update()
    
    def execute_script(self, e):
        if not self.tabs:
            return
        
        current_tab = list(self.tabs.values())[self.current_tab_index]
        script = current_tab["text_field"].value
        if script.strip():
            try:
                if self.ExecutorAPI.loaded_api.is_injected():
                    self.ExecutorAPI.Execute(script)
                    self.show_toast("Script executed", ft.Icons.PLAY_ARROW)
                else:
                    self.show_toast("Please attach!", ft.Icons.CLEAR)
            except Exception as e:
                self.show_toast(f"Execution error: {str(e)}", ft.Icons.ERROR)
    
    def clear_script(self, e):
        if not self.tabs:
            return
        
        current_tab = list(self.tabs.values())[self.current_tab_index]
        current_tab["text_field"].value = ""
        current_tab["saved"] = False
        self.page.update()
    
    def update_scripts(self, e=None):
        self.script_list.controls.clear()
        for f in os.listdir(scripts_dir):
            if f.endswith((".lua", ".txt")):
                self.script_list.controls.append(
                    ft.ListTile(
                        title=ft.Text(f),
                        trailing=ft.PopupMenuButton(
                            icon=ft.Icons.MORE_VERT,
                            items=[
                                ft.PopupMenuItem(text="Execute", icon=ft.Icons.PLAY_ARROW,
                                                on_click=lambda e, fn=f: self.exec_selected(fn)),
                                ft.PopupMenuItem(text="Open", icon=ft.Icons.OPEN_IN_NEW,
                                                on_click=lambda e, fn=f: self.open_in_editor(fn)),
                                ft.PopupMenuItem(text="Delete", icon=ft.Icons.DELETE,
                                                on_click=lambda e, fn=f: self.remove_script(fn)),
                            ]
                        )
                    )
                )
        self.page.update()

    def save_current_file(self, e=None):
        current_tab = list(self.tabs.values())[self.current_tab_index]
        if current_tab["path"]:
            try:
                with open(current_tab["path"], "w", encoding="utf-8") as f:
                    f.write(current_tab["text_field"].value)
                current_tab["saved"] = True
                self.show_toast("File saved successfully", ft.Icons.CHECK)
            except Exception as e:
                self.show_toast(f"Save error: {e}", ft.Icons.ERROR)
        else:
            self.save_picker.save_file(
                file_name="script.lua",
                file_type=ft.FilePickerFileType.CUSTOM,
                allowed_extensions=["lua", "txt"]
            )

    def on_save_selected(self, e: ft.FilePickerResultEvent):
        if e.path:
            current_tab = list(self.tabs.values())[self.current_tab_index]
            try:
                with open(e.path, "w", encoding="utf-8") as f:
                    f.write(current_tab["text_field"].value)
                current_tab["saved"] = True
                current_tab["path"] = e.path
                self.show_toast("File saved successfully", ft.Icons.CHECK)
            except Exception as ex:
                self.show_toast(f"Save error: {ex}", ft.Icons.ERROR)

    def exec_selected(self, script_name):
        try:
            with open(os.path.join(scripts_dir, script_name), "r", encoding="utf-8") as f:
                self.ExecutorAPI.Execute(f.read())
            self.show_toast(f"Executed: {script_name}", ft.Icons.PLAY_ARROW)
        except Exception as e:
            self.show_toast(f"Error: {str(e)}", ft.Icons.ERROR)
    
    def open_in_editor(self, script_name):
        path = os.path.join(scripts_dir, script_name)
        
        for tab_name, tab in self.tabs.items():
            if tab["path"] == path:
                self.switch_to_tab(tab_name)
                return
        try:
            with open(path, "r", encoding="utf-8") as f:
                self.add_tab(f"Script: {script_name}", f.read(), path)
            self.show_toast(f"Opened: {script_name}", ft.Icons.FILE_OPEN)
        except Exception as e:
            self.show_toast(f"Error opening: {str(e)}", ft.Icons.ERROR)
    
    def remove_script(self, script_name):
        try:
            os.remove(os.path.join(scripts_dir, script_name))
            self.update_scripts()
            self.show_toast(f"Deleted: {script_name}", ft.Icons.DELETE)
        except Exception as e:
            self.show_toast(f"Error deleting: {str(e)}", ft.Icons.ERROR)
    
    def load_settings(self):
        if os.path.exists(settings_file):
            try:
                with open(settings_file, "r", encoding="utf-8") as f:
                    settings = json.load(f)
                    if "theme_name" in settings:
                        self.theme_manager.set_theme(settings["theme_name"])
                        self.theme_dropdown.value = settings["theme_name"]
                    if "auto_inject" in settings:
                        self.auto_inject_switch.value = settings["auto_inject"]
                        self.ExecutorAPI.AutoInject(settings["auto_inject"])
            except Exception as e:
                self.show_toast(f"Error loading settings: {e}", ft.Icons.ERROR)
    
    def save_settings(self):
        settings = {
            "theme_name": self.theme_manager.current_theme,
            "auto_inject": self.auto_inject_switch.value
        }
        try:
            with open(settings_file, "w", encoding="utf-8") as f:
                json.dump(settings, f, indent=2)
        except Exception as e:
            self.show_toast(f"Error saving settings: {e}", ft.Icons.ERROR)
    
    def save_tabs(self):
        current_paths = set()
        
        try:
            for name, tab in self.tabs.items():
                safe_name = "".join(c for c in name if c.isalnum() or c in (' ', '_', '-')).rstrip()
                if not safe_name:
                    safe_name = "untitled"
                    
                tab_path = os.path.join(tabs_dir, f"{safe_name}.lua")
                
                with open(tab_path, "w", encoding="utf-8") as f:
                    f.write(tab["text_field"].value)
                    
                tab["path"] = tab_path
                tab["saved"] = True
                current_paths.add(tab_path)

            for f in os.listdir(tabs_dir):
                if f.endswith('.lua'):
                    file_path = os.path.join(tabs_dir, f)
                    if file_path not in current_paths:
                        try:
                            os.remove(file_path)
                        except Exception as e:
                            print(f"Error removing old tab file {f}: {e}")
        except Exception as e:
            self.show_toast(f"Error saving tabs: {e}", ft.Icons.ERROR)
            
        self.page.update()
    
    def on_nav_change(self, e):
        tab_name = ["Main", "Options"][e.control.selected_index]
        self.show_tab_content(tab_name)
    
    def on_window_event(self, e):
        if e.data == "close":
            self.rpc.close()
            self.save_tabs()
            self.save_settings()
            self.page.window_destroy()

def main(page: ft.Page):
    app = PyRO(page)

update = False

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def updater_screen(page: ft.Page):
    global ver
    page.title = "PyRO Updater"
    page.window_resizable = False
    page.theme_mode = ft.ThemeMode.DARK
    page.horizontal_alignment = "center"
    page.vertical_alignment = "center"

    theme_manager = ThemeManager()
    if os.path.exists(settings_file):
        try:
            with open(settings_file, "r", encoding="utf-8") as f:
                settings = json.load(f)
                if "theme_name" in settings:
                    theme_manager.set_theme(settings["theme_name"])
        except:
            pass

    colors = theme_manager.get_theme_colors()

    page.theme = ft.Theme(
        color_scheme_seed=colors["primary"],
        color_scheme=ft.ColorScheme(
            primary=colors["primary"],
            secondary=colors["secondary"],
            surface=ft.Colors.BLACK
        )
    )

    app_name = ft.Text("PyRO",
                      size=50,
                      weight="bold",
                      color=colors["primary"],
                      font_family="Roboto")

    version_text = ft.Text(f"{ver}",
                         color=ft.Colors.WHITE70,
                         size=22)

    left_content = ft.Column(
        [
            app_name,
            version_text
        ],
        alignment="center",
        horizontal_alignment="center",
        spacing=5
    )

    changelog_title = ft.Text("Changelog:",
                            visible=False,
                            weight="bold",
                            color=ft.Colors.WHITE,
                            size=20)

    changelog_text = ft.Text(
        "",
        visible=False,
        color=ft.Colors.WHITE70,
        size=16,
        max_lines=None,
        no_wrap=False,
        expand=True
    )

    right_content = ft.Column(
        [
            changelog_title,
            changelog_text
        ],
        alignment="center",
        horizontal_alignment="center",
        spacing=10,
        expand=True
    )

    main_layout = ft.Row(
        [
            ft.Container(
                content=left_content,
                expand=True,
                alignment=ft.alignment.center
            ),
            ft.Container(
                content=right_content,
                expand=True,
                alignment=ft.alignment.top_left,
                padding=10
            )
        ],
        vertical_alignment="center",
        expand=True
    )

    progress = ft.ProgressBar(width=400, color=colors["primary"])
    progress_text = ft.Text("Checking for updates...", size=12, color=ft.Colors.WHITE)

    content = ft.Column(
        [
            main_layout,
            progress,
            progress_text
        ],
        alignment="center",
        horizontal_alignment="center",
        spacing=20,
        expand=True
    )

    page.add(content)

    def update_progress(current, total):
        progress.value = current / total
        progress_text.value = f"Downloading update... {floor(current/total*100)}% ({current/1024/1024:.1f}MB/{total/1024/1024:.1f}MB)"
        page.update()

    def download_with_progress(url):
        try:
            with urlopen(url) as response:
                total_size = int(response.headers.get('content-length', 0))
                downloaded = 0
                block_size = 8192

                with open("PyRO.zip", 'wb') as f:
                    while True:
                        buffer = response.read(block_size)
                        if not buffer:
                            break
                        f.write(buffer)
                        downloaded += len(buffer)
                        update_progress(downloaded, total_size)

            return True
        except Exception as e:
            progress_text.value = f"Download error: {str(e)}"
            page.update()
            return False

    def download_update(url):
        try:
            progress_text.value = "Preparing download..."
            progress.value = None
            page.update()

            if download_with_progress(url):
                progress_text.value = "Update downloaded. Installing..."
                page.update()
                create_bat()

                def close_and_run():
                    global update
                    time.sleep(0.5)
                    subprocess.Popen(["start", "upd.bat"], shell=True)
                    page.window.close()
                    update = True

                Thread(target=close_and_run, daemon=True).start()

        except Exception as e:
            progress_text.value = f"Download error: {str(e)}"
            page.update()

    def create_bat():
        bat_code = r'''@echo off
title Updating...

echo waiting 15 seconds because ui takes a long time to close :sob:...
timeout /t 15 >nul

echo Deleting old files...

del /f /q PyRO.exe

rmdir /s /q _internal

echo Extracting new version...
powershell -Command "Expand-Archive -Path 'PyRO.zip' -DestinationPath '.' -Force"

echo Deleting PyRO.zip...

del /f /q PyRO.zip

echo Done.

echo Done.
echo you can close this window and open PyRO if it does not happen automatically
start "" PyRO.exe
pause
exit
'''

        with open("upd.bat", "w", encoding="utf-8") as f:
            f.write(bat_code)

    def animate_progress():
        for i in range(30):
            time.sleep(0.03)
            progress.value = i / 30
            page.update()

    def check_update():
        global ver
        try:
            response = requests.get(
                f"https://api.github.com/repos/iwonderwhoisg1itch/PyRO/releases/latest",
                timeout=10,
                verify=False
            )
            response.raise_for_status()
            release_info = response.json()
            latest_version = release_info['tag_name']
            changelog = release_info['body']
            assets = release_info.get('assets', [])
            download_url = assets[0]['browser_download_url'] if assets else release_info['html_url']

            if latest_version != ver:
                ver = latest_version
                version_text.value = ver
                progress_text.value = f"Update available: {latest_version}"
                changelog_title.visible = True
                changelog_text.visible = True
                changelog_text.value = changelog
                page.update()
                time.sleep(0.5)
                download_update(download_url)
            else:
                progress_text.value = "You have the latest version"
                animate_progress()

        except requests.exceptions.ReadTimeout:
            progress_text.value = "Timeout while checking for updates"
            animate_progress()
        except requests.exceptions.SSLError:
            progress_text.value = "SSL connection error. Check your certificates."
            animate_progress()
        except requests.exceptions.RequestException as e:
            progress_text.value = f"Request error: {str(e)}"
            changelog_text.value = "Unable to retrieve release information."
            changelog_title.visible = True
            changelog_text.visible = True
            animate_progress()

        page.update()
        time.sleep(1)
        page.window.close()

    Thread(target=check_update, daemon=True).start()


ft.app(target=updater_screen)
if not update:
    ft.app(target=main)