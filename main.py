import flet as ft
import os
import json
import clr
import psutil
import time
import sys
from pypresence import Presence
from threading import Thread
from System.Net import ServicePointManager, SecurityProtocolType

ServicePointManager.SecurityProtocol = SecurityProtocolType.Tls12 | SecurityProtocolType.Tls13

class DiscordRPC:
    def __init__(self):
        self.rpc = None
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
                elif self.current_tab == "Scripts":
                    details = "Browsing scripts..."
                elif self.current_tab == "Options":
                    details = "Adjusting settings..."

                self.rpc.update(
                    state=f"v{ver} | Seliware v{seliver}",
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
saved_tabs_dir = os.path.join(base_dir, "saved_tabs")
tabs_file = os.path.join(base_dir, "open_tabs.json")

clr.AddReference(dll_path)
from SeliwareAPI import Seliware

Seliware.Initialize()

def getSeliVer():
    ver = Seliware.GetVersion()
    if "-" in ver:
        seliver = ver.split("-", 1)[-1]
    else:
        seliver = ver
    return seliver 

ver = "0.5b"
seliver = getSeliVer()

rbx_pids = []

os.makedirs(saved_tabs_dir, exist_ok=True)
os.makedirs(scripts_dir, exist_ok=True)


def attach_process():
    global rbx_pids
    found = [proc.pid for proc in psutil.process_iter(['name']) if proc.info['name'] == "RobloxPlayerBeta.exe"]
    for pidor in found:
        if pidor not in rbx_pids:
            rbx_pids.append(pidor)
            Seliware.Inject(pidor)
    rbx_pids = [pid for pid in rbx_pids if psutil.pid_exists(pid)]

class PyRO:
    def __init__(self, page: ft.Page):
        self.page = page
        self.setup_window()
        self.rpc = DiscordRPC()
        
        self.tabs = {}
        self.current_tab_index = 0
        self.current_main_tab = "Main"
        self.selected_script = None
        
        self.setup_ui()
        self.file_picker = ft.FilePicker(on_result=self.on_file_selected)
        self.save_picker = ft.FilePicker(on_result=self.on_save_selected)
        self.page.overlay.extend([self.file_picker, self.save_picker])
        self.load_tabs()
        
        if not self.tabs:
            self.add_tab()
        
        self.page.on_window_event = self.on_window_event
        self.rpc.start()
    
    def setup_window(self):
        self.page.title = f"PyRO v{ver}"
        self.page.window_width = 1000
        self.page.window_height = 700
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.window_prevent_close = True
    
    def setup_ui(self):
        self.setup_navigation()
        self.setup_main_tab()
        self.setup_scripts_tab()
        
        self.content_area = ft.Column(expand=True)
        self.page.add(self.content_area)
        self.show_tab_content("Main")
    
    def setup_navigation(self):
        self.nav_drawer = ft.NavigationDrawer(
            controls=[
                ft.NavigationDrawerDestination(label="Main", icon=ft.Icons.CODE),
                ft.NavigationDrawerDestination(label="Scripts", icon=ft.Icons.LIST),
                ft.NavigationDrawerDestination(label="Options", icon=ft.Icons.SETTINGS),
            ],
            on_change=self.on_nav_change
        )
        self.page.drawer = self.nav_drawer
        
        self.app_bar = ft.AppBar(
            title=ft.Text(f"PyRO v{ver} for Seliware v{seliver}"),
            leading=ft.IconButton(
                icon=ft.Icons.MENU,
                on_click=lambda e: self.toggle_nav_drawer()
            ),
        )
        self.page.appbar = self.app_bar
    
    def setup_main_tab(self):
        self.tab_headers = ft.Row(scroll=True, expand=True, height=40)
        self.tab_contents = ft.Column(expand=True)

        self.main_tab_content = ft.Column(
            controls=[
                ft.Row([
                    self.tab_headers,
                    ft.IconButton(ft.Icons.ADD, on_click=lambda _: self.add_tab())
                ]),
                ft.Divider(),

                self.tab_contents,

                ft.Row(
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
                                        bgcolor=ft.Colors.BLUE_800,
                                        padding=ft.padding.symmetric(horizontal=15, vertical=15),
                                        shape=ft.RoundedRectangleBorder(radius=5)
                                    )
                                ),
                                
                                ft.OutlinedButton(
                                    content=ft.Row([
                                        ft.Icon(ft.Icons.CLEAR, color=ft.Colors.BLUE_300, size=20),
                                        ft.Text("Clear", color=ft.Colors.BLUE_300)
                                    ]),
                                    on_click=self.clear_script,
                                    style=ft.ButtonStyle(
                                        side=ft.BorderSide(1, ft.Colors.BLUE_800),
                                        padding=ft.padding.symmetric(horizontal=15, vertical=15),
                                        shape=ft.RoundedRectangleBorder(radius=5)
                                    )
                                ),
                                
                                ft.OutlinedButton(
                                    content=ft.Row([
                                        ft.Icon(ft.Icons.FILE_OPEN, color=ft.Colors.BLUE_300, size=20),
                                        ft.Text("Open File", color=ft.Colors.BLUE_300)
                                    ]),
                                    on_click=self.open_file_dialog,
                                    style=ft.ButtonStyle(
                                        side=ft.BorderSide(1, ft.Colors.BLUE_800),
                                        padding=ft.padding.symmetric(horizontal=15, vertical=15),
                                        shape=ft.RoundedRectangleBorder(radius=5)
                                    )
                                ),
                                
                                ft.OutlinedButton(
                                    content=ft.Row([
                                        ft.Icon(ft.Icons.SAVE, color=ft.Colors.BLUE_300, size=20),
                                        ft.Text("Save File", color=ft.Colors.BLUE_300)
                                    ]),
                                    on_click=self.save_current_file,
                                    style=ft.ButtonStyle(
                                        side=ft.BorderSide(1, ft.Colors.BLUE_800),
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
                            on_click=lambda _: attach_process(),
                            style=ft.ButtonStyle(
                                bgcolor=ft.Colors.BLUE_800,
                                padding=ft.padding.symmetric(horizontal=15, vertical=15),
                                shape=ft.RoundedRectangleBorder(radius=5)
                            )
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    spacing=20,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                )
            ],
            expand=True,
            spacing=10
        )
    
    def setup_scripts_tab(self):
        self.script_list = ft.ListView(expand=True)
        self.scripts_tab_content = ft.Column(
            controls=[
                self.script_list,
                ft.ElevatedButton("Refresh", on_click=self.update_scripts)
            ],
            expand=True
        )
        self.update_scripts()
    
    def add_tab(self, name=None, content="", path=None):
        if name is None:
            tab_num = len(self.tabs) + 1
            name = f"Tab {tab_num}"
            while name in self.tabs:
                tab_num += 1
                name = f"Tab {tab_num}"

        text_field = ft.TextField(
            value=content,
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
            on_click=self.close_tab_click
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
        self.tab_headers.controls = [tab["header"] for tab in self.tabs.values()]
        self.tab_contents.controls = [tab["content"] for tab in self.tabs.values()]
        
        for i, tab in enumerate(self.tabs.values()):
            tab["content"].visible = (i == self.current_tab_index)
            tab["header"].bgcolor = (
                ft.Colors.BLUE_800 if i == self.current_tab_index
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
            except Exception as ex:
                self.show_message(f"Open error: {ex}")

    def toggle_rename(self, text_field, text_display):
        text_field.visible = True
        text_display.visible = False
        self.page.update()

    def rename_tab(self, old_name, new_name):
        if not new_name or new_name in self.tabs:
            return
        tab = self.tabs.pop(old_name)
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
                Seliware.Execute(script)
            except Exception as e:
                self.show_message(f"Execution error: {str(e)}")
    
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
                        leading=ft.PopupMenuButton(
                            icon=ft.Icons.MORE_VERT,
                            items=[
                                ft.PopupMenuItem(text="Execute", on_click=lambda e, fn=f: self.exec_selected(fn)),
                                ft.PopupMenuItem(text="Open", on_click=lambda e, fn=f: self.open_in_editor(fn)),
                                ft.PopupMenuItem(text="Delete", on_click=lambda e, fn=f: self.remove_script(fn)),
                            ],
                        ),
                        title=ft.Text(f),
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
                self.show_message("File saved successfully.")
            except Exception as e:
                self.show_message(f"Save error: {e}")
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
                self.show_message("File saved successfully.")
            except Exception as ex:
                self.show_message(f"Save error: {ex}")


    def exec_selected(self, script_name):
        try:
            with open(os.path.join(scripts_dir, script_name), "r", encoding="utf-8") as f:
                Seliware.Execute(f.read())
        except Exception as e:
            self.show_message(f"Error: {str(e)}")
    
    def open_in_editor(self, script_name):
        path = os.path.join(scripts_dir, script_name)
        
        for tab_name, tab in self.tabs.items():
            if tab["path"] == path:
                self.switch_to_tab(tab_name)
                return
        try:
            with open(path, "r", encoding="utf-8") as f:
                self.add_tab(f"Script: {script_name}", f.read(), path)
        except Exception as e:
            self.show_message(f"Error opening: {str(e)}")
    
    def remove_script(self, script_name):
        try:
            os.remove(os.path.join(scripts_dir, script_name))
            self.update_scripts()
            self.show_message("Script deleted")
        except Exception as e:
            self.show_message(f"Error deleting: {str(e)}")
    
    def apply_editor_settings(self, e):
        try:
            self.font_var = self.font_entry.value
            self.font_size_var = int(self.font_size_entry.value)
            self.top_most_var = self.top_most_switch.value
            
            self.page.window_always_on_top = self.top_most_var
            self.show_message("Settings applied")
        except ValueError:
            self.show_message("Invalid font size")
    
    def save_editor_settings(self, e):
        self.apply_editor_settings(e)
        self.settings.current_settings.update({
            "font": self.font_var,
            "font_size": self.font_size_var,
            "top_most": self.top_most_var,
        })
        self.settings.save_settings()
        self.show_message("Settings saved")
    
    def save_tabs(self):
        tabs_data = []
        for name, tab in self.tabs.items():
            tabs_data.append({
                "name": name,
                "content": tab["text_field"].value,
                "path": tab["path"],
                "saved": tab["saved"]
            })

        try:
            with open(tabs_file, "w", encoding="utf-8") as f:
                json.dump(tabs_data, f, indent=2)
        except Exception as e:
            print(f"Error saving tabs: {e}")
        finally:
            self.page.update()

    
    def load_tabs(self):
        if not os.path.exists(tabs_file):
            return
        
        try:
            with open(tabs_file, "r", encoding="utf-8") as f:
                tabs_data = json.load(f)
                for tab in tabs_data:
                    self.add_tab(tab["name"], tab["content"], tab["path"])
        except Exception as e:
            print(f"Error loading tabs: {e}")
    
    def show_message(self, message):
        self.page.snack_bar = ft.SnackBar(ft.Text(message))
        self.page.snack_bar.open = True
        self.page.update()
    
    def toggle_nav_drawer(self):
        if self.page.drawer:
            self.page.drawer.open = not self.page.drawer.open
            self.page.drawer.update()
    
    def on_nav_change(self, e):
        tab_name = ["Main", "Scripts", "Options"][e.control.selected_index]
        self.show_tab_content(tab_name)
    
    def on_window_event(self, e):
        if e.data == "close":
            self.rpc.close()
            self.save_tabs()
            self.page.window_destroy()

def main(page: ft.Page):
    app = PyRO(page)

ft.app(target=main)
