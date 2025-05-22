import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import os
import json
import clr
import psutil
from pypresence import Presence
import time
from threading import Thread
from pygments.lexers.scripting import LuaLexer
from chlorophyll import CodeView



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
                    details = f"Looking into main tab -> {self.current_editor_tab[:15]}..." if self.current_editor_tab else "Editing scripts..."
                elif self.current_tab == "Scripts":
                    details = "Browses through the saved scripts..."
                elif self.current_tab == "Options":
                    details = "Tweaking settings..."

                self.rpc.update(
                    state=f"v{ver} | Selected api: Seliware | ver: {Seliware.GetVersion()}",
                    details=details,
                    large_image="icon",
                    large_text="PyRO",
                    start=self.time,
                    buttons=[{"label": "GitHub", "url": "https://github.com/iwonderwhoisg1itch/PyRO"}, {"label": "Discord", "url": "https://discord.gg/UWtjQayY9q"}]
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

script_dir = os.path.dirname(os.path.abspath(__file__))
dll_path = os.path.join(script_dir, "SeliwareAPI.dll")
scripts_dir = os.path.join(script_dir, "scripts")
saved_tabs_dir = os.path.join(script_dir, "saved_tabs")
tabs_file = os.path.join(script_dir, "open_tabs.json")

clr.AddReference(dll_path)
from SeliwareAPI import Seliware

ver = str("0.4")

Seliware.Initialize()

rbx_pids = []

os.makedirs(saved_tabs_dir, exist_ok=True)
os.makedirs(scripts_dir, exist_ok=True)

class EditorSettings:
    def __init__(self):
        self.settings_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "settings.json")
        self.default_settings = {
            "font": "Fira Code",
            "font_size": 10
        }
        self.current_settings = self.default_settings.copy()
        self.load_settings()

    def load_settings(self):
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                    self.current_settings.update(loaded)
            except Exception as e:
                print(f"Error loading settings: {e}")

    def save_settings(self):
        try:
            with open(self.settings_file, "w", encoding="utf-8") as f:
                json.dump(self.current_settings, f, indent=2)
        except Exception as e:
            print(f"Error saving settings: {e}")

    def apply_settings(self, editor):
        editor.configure(
            font=(self.current_settings["font"], self.current_settings["font_size"])
        )

def attach_process():
    global rbx_pids
    found = [proc.pid for proc in psutil.process_iter(['name']) if proc.info['name'] == "RobloxPlayerBeta.exe"]
    for pidor in found:
        if pidor not in rbx_pids:
            rbx_pids.append(pidor)
            Seliware.Inject(pidor)
    rbx_pids = [pid for pid in rbx_pids if psutil.pid_exists(pid)]


class PyRO:
    def __init__(self):
        self.font_var = None
        self.font_size_var = None
        self.script_list = None
        self.selected_script = None
        self.popup_menu = None
        self.editor_tabview = None
        self.root = ctk.CTk()
        self.root.title(f"PyRO v{ver} | Selected api: Seliware | ver: {Seliware.GetVersion()}")
        self.root.geometry("900x600")

        self.rpc = DiscordRPC()
        self.settings = EditorSettings()
        self.rpc.start()

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.tabview = ctk.CTkTabview(self.root)
        self.tabview.pack(pady=10, padx=10, fill="both", expand=True)

        self.tabview.configure(command=lambda: self.on_tab_change())

        self.tabview.add("Main")
        self.tabview.add("Scripts")
        self.tabview.add("Options")

        self.tabview.configure(command=self.on_tab_change)

        self.top_most_var = tk.BooleanVar(value=False)

        self.editor_tabs = {}

        self.init_main_tab()
        self.init_scripts_tab()
        self.init_settings_tab()
        self.load_tabs()

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.root.mainloop()
        self.root.update_idletasks()

    def on_tab_change(self):
        current_tab = self.tabview.get()
        self.rpc.set_tab(current_tab)

        if current_tab == "Main" and self.editor_tabview:
            current_editor_tab = self.editor_tabview.get()
            self.rpc.set_editor_tab(current_editor_tab if current_editor_tab else "")

    def on_editor_tab_change(self):
        if self.tabview.get() == "Main":
            current_editor_tab = self.editor_tabview.get()
            self.rpc.set_editor_tab(current_editor_tab if current_editor_tab else "")

    def on_close(self):
        self.rpc.close()
        self.root.destroy()

    def init_main_tab(self):
        tab = self.tabview.tab("Main")

        main_container = ctk.CTkFrame(tab)
        main_container.pack(fill="both", expand=True, padx=10, pady=10)

        main_container.grid_rowconfigure(0, weight=1)
        main_container.grid_rowconfigure(1, weight=0)
        main_container.grid_columnconfigure(0, weight=1)

        self.editor_tabview = ctk.CTkTabview(main_container)
        self.editor_tabview.grid(row=0, column=0, sticky="nsew", pady=(0, 5))
        self.editor_tabview.configure(command=lambda: self.on_editor_tab_change())
        self.setup_menu()

        btn_frame = ctk.CTkFrame(main_container, bg_color="#2b2b2b", fg_color="#2b2b2b")
        btn_frame.grid(row=1, column=0, sticky="ew")

        btn_frame = ctk.CTkFrame(btn_frame, fg_color="transparent")
        btn_frame.pack(anchor="center", pady=5)

        ctk.CTkButton(btn_frame, text="Execute", command=self.run_code, width=100).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Clear", command=self.clear_content, width=100).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Attach", command=attach_process, width=100, fg_color="#FF4500",
                      hover_color="#FF6347").pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="New tab", command=self.add_tab, width=100).pack(side="left", padx=5)

    def init_scripts_tab(self):
        tab = self.tabview.tab("Scripts")
        self.script_list = tk.Listbox(tab, bg="#1a1a1a", fg="white", selectbackground="#3a3a3a", height=15)
        self.script_list.pack(padx=10, pady=(10, 5), fill="both", expand=True)
        self.script_list.bind("<Button-3>", self.show_script_menu)

        ctk.CTkButton(tab, text="Refresh", command=self.update_scripts).pack(pady=5)
        self.update_scripts()

    def init_settings_tab(self):
        tab = self.tabview.tab("Options")

        editor_frame = ctk.CTkFrame(tab)
        editor_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(editor_frame, text="Editor Settings", font=("Arial", 14, "bold")).pack(anchor="w", pady=(0, 10))

        font_frame = ctk.CTkFrame(editor_frame)
        font_frame.pack(fill="x", pady=5)

        ctk.CTkLabel(font_frame, text="Font:").pack(side="left", padx=5)
        self.font_var = tk.StringVar(value=self.settings.current_settings["font"])
        font_entry = ctk.CTkEntry(font_frame, textvariable=self.font_var)
        font_entry.pack(side="left", padx=5, fill="x", expand=True)

        ctk.CTkLabel(font_frame, text="Size:").pack(side="left", padx=5)
        self.font_size_var = tk.IntVar(value=self.settings.current_settings["font_size"])
        font_size_spin = ctk.CTkEntry(font_frame, textvariable=self.font_size_var, width=50)
        font_size_spin.pack(side="left", padx=5)

        btn_frame = ctk.CTkFrame(editor_frame)
        btn_frame.pack(fill="x", pady=10)

        ctk.CTkButton(btn_frame, text="Apply", command=self.apply_editor_settings).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Save", command=self.save_editor_settings).pack(side="left", padx=5)

        top_most_frame = ctk.CTkFrame(tab)
        top_most_frame.pack(fill="x", padx=10, pady=10)
        top_most_switch = ctk.CTkSwitch(top_most_frame, text="Top Most Toggle", variable=self.top_most_var,
                                        command=self.toggle_top_most)
        top_most_switch.pack(anchor="w")

    def save_editor_settings(self):
        self.apply_editor_settings()
        self.settings.save_settings()
        messagebox.showinfo("Success", "Settings saved")

    def apply_editor_settings(self):
        self.settings.current_settings.update({
            "font": self.font_var.get(),
            "font_size": self.font_size_var.get()
        })

        for tab_data in self.editor_tabs.values():
            self.settings.apply_settings(tab_data["textbox"])

        messagebox.showinfo("Success", "Font settings applied to current tabs")


    def toggle_top_most(self):
        self.root.attributes('-topmost', self.top_most_var.get())

    def setup_menu(self):
        self.popup_menu = tk.Menu(self.root, tearoff=0)
        self.popup_menu.add_command(label="Copy", command=self.copy_content)
        self.popup_menu.add_command(label="Paste", command=self.paste_content)
        self.popup_menu.add_command(label="Cut", command=self.cut_content)
        self.popup_menu.add_separator()
        self.popup_menu.add_command(label="Select all", command=self.select_all_content)
        self.popup_menu.add_separator()
        self.popup_menu.add_command(label="Rename", command=self.change_tab_name)
        self.popup_menu.add_command(label="Close", command=self.remove_tab)
        self.popup_menu.add_command(label="Save", command=self.store_tab)

    def show_script_menu(self, event):
        sel = self.script_list.curselection()
        if sel:
            self.selected_script = self.script_list.get(sel[0])
            menu = tk.Menu(self.root, tearoff=0)
            menu.add_command(label="Execute", command=self.exec_selected)
            menu.add_command(label="Load in editor", command=self.open_in_editor)
            menu.add_command(label="Delete", command=self.remove_script)
            menu.tk_popup(event.x_root, event.y_root)

    def remove_script(self):
        if hasattr(self, 'selected_script'):
            path = os.path.join(scripts_dir, self.selected_script)
            try:
                os.remove(path)
                self.update_scripts()
                messagebox.showinfo("Done", "Script removed")
            except Exception as e:
                messagebox.showerror("Error", f"Failed: {str(e)}")

    def update_scripts(self):
        self.script_list.delete(0, tk.END)
        for f in os.listdir(scripts_dir):
            if f.endswith((".lua", ".txt")):
                self.script_list.insert(tk.END, f)

    def open_in_editor(self):
        name = self.selected_script
        path = os.path.join(scripts_dir, name)

        for tab_name, tab_data in self.editor_tabs.items():
            if tab_data.get("path") == path:
                self.editor_tabview.set(tab_name)
                return

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = f.read()

            tab_name = f"Script: {name}"
            self.create_tab(tab_name, data, path)
        except Exception as e:
            messagebox.showerror("Error", f"Failed: {str(e)}")

    def create_tab(self, name, content="", path=None):
        new_tab = self.editor_tabview.add(name)

        text_box = CodeView(
            new_tab,
            lexer=LuaLexer,
            font=(self.settings.current_settings["font"], self.settings.current_settings["font_size"]),
            color_scheme="dracula",
            autohide_scrollbar=True
        )
        text_box.pack(fill="both", expand=True, padx=5, pady=5)
        text_box.insert("1.0", content)
        text_box.bind("<Button-3>", lambda e: self.popup_menu.tk_popup(e.x_root, e.y_root))

        self.editor_tabs[name] = {
            "textbox": text_box,
            "path": path,
            "saved": True if path else False
        }

        self.editor_tabview.set(name)
        self.rpc.set_editor_tab(name)
        self.save_tabs()

    def add_tab(self):
        name = f"Tab {len(self.editor_tabs) + 1}"
        self.create_tab(name)

    def exec_selected(self):
        path = os.path.join(scripts_dir, self.selected_script)
        try:
            with open(path, "r", encoding="utf-8") as f:
                Seliware.Execute(f.read())
        except Exception as e:
            messagebox.showerror("Error", f"Failed: {str(e)}")

    def get_current_tab(self):
        current = self.editor_tabview.get()
        return self.editor_tabs.get(current)

    def run_code(self):
        tab = self.get_current_tab()
        if tab:
            Seliware.Execute(tab["textbox"].get("1.0", "end-1c"))

    def clear_content(self):
        tab = self.get_current_tab()
        if tab:
            tab["textbox"].delete("1.0", "end")

    def copy_content(self):
        tab = self.get_current_tab()
        if tab:
            self.root.clipboard_clear()
            try:
                text = tab["textbox"].get("sel.first", "sel.last")
                self.root.clipboard_append(text)
            except tk.TclError:
                pass
        return "break"

    def paste_content(self):
        tab = self.get_current_tab()
        if tab:
            try:
                text = self.root.clipboard_get()
                tab["textbox"].insert("insert", text)
            except tk.TclError:
                pass
        return "break"

    def cut_content(self):
        self.copy_content()
        tab = self.get_current_tab()
        if tab:
            try:
                tab["textbox"].delete("sel.first", "sel.last")
            except tk.TclError:
                pass
        return "break"

    def select_all_content(self):
        tab = self.get_current_tab()
        if tab:
            tab["textbox"].tag_add("sel", "1.0", "end")
        return "break"

    def change_tab_name(self):
        current = self.editor_tabview.get()
        if current:
            new_name = self.get_new_name(current)
            if new_name and new_name != current:
                tab_data = self.editor_tabs.pop(current)
                content = tab_data["textbox"].get("1.0", "end-1c")
                self.editor_tabview.delete(current)
                self.create_tab(new_name, content, tab_data["path"])
                self.editor_tabs[new_name]["saved"] = tab_data["saved"]
                self.rpc.set_editor_tab(new_name)
                self.save_tabs()

    def remove_tab(self):
        current = self.editor_tabview.get()
        if current:
            new_current = self.editor_tabview.get()
            self.rpc.set_editor_tab(new_current if new_current else "")
            self.close_tab(current)

    def close_tab(self, name):
        if name in self.editor_tabs:
            tab = self.editor_tabs[name]
            if not tab["saved"]:
                content = tab["textbox"].get("1.0", "end-1c")
                if content.strip():
                    answer = messagebox.askyesnocancel(
                        "Save?",
                        f"Save changes in '{name}'?"
                    )
                    if answer is None:
                        self.editor_tabview.delete(name)
                        self.editor_tabs.pop(name)
                        return
                    elif answer:
                        self.store_tab()
                        return

            self.editor_tabview.delete(name)
            self.editor_tabs.pop(name)
            new_current = self.editor_tabview.get()
            self.rpc.set_editor_tab(new_current if new_current else "")
            self.save_tabs()

    def store_tab(self):
        current = self.editor_tabview.get()
        if current:
            self.save_tab(current)

    def save_tab(self, name):
        tab = self.editor_tabs.get(name)
        if not tab:
            return

        content = tab["textbox"].get("1.0", "end-1c")
        path = tab.get("path")

        if not path:
            path = filedialog.asksaveasfilename(
                initialdir=scripts_dir,
                defaultextension=".lua",
                filetypes=[("Lua Files", "*.lua"), ("Text Files", "*.txt"), ("All Files", "*.*")]
            )
            if not path:
                return

        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)

            tab["path"] = path
            tab["saved"] = True

            new_name = f"Script: {os.path.basename(path)}"
            if new_name != name:
                self.editor_tabview.delete(name)
                self.editor_tabs.pop(name)
                self.create_tab(new_name, content, path)

            messagebox.showinfo("Success", "Saved")
            self.update_scripts()
            self.save_tabs()
        except Exception as e:
            messagebox.showerror("Error", f"Failed: {str(e)}")

    def get_new_name(self, current):
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Rename")
        dialog.geometry("300x150")
        dialog.transient(self.root)
        dialog.grab_set()

        result = tk.StringVar(value=current)

        ctk.CTkLabel(dialog, text="New name:").pack(pady=5)
        entry = ctk.CTkEntry(dialog, textvariable=result)
        entry.pack(pady=5, padx=10, fill="x")

        def submit():
            dialog.destroy()

        ctk.CTkButton(dialog, text="OK", command=submit).pack(pady=5)

        dialog.wait_window()
        return result.get()

    def save_tabs(self):
        tabs = []
        for name, data in self.editor_tabs.items():
            tabs.append({
                "name": name,
                "path": data["path"],
                "content": data["textbox"].get("1.0", "end-1c"),
                "saved": data["saved"]
            })

        try:
            with open(tabs_file, "w", encoding="utf-8") as f:
                json.dump(tabs, f, indent=2)
        except Exception as e:
            print("Save error:", e)

    def load_tabs(self):
        if os.path.exists(tabs_file):
            try:
                with open(tabs_file, "r", encoding="utf-8") as f:
                    tabs = json.load(f)

                for tab in tabs:
                    content = tab.get("content", "")
                    path = tab.get("path")
                    name = tab.get("name", f"Tab {len(self.editor_tabs) + 1}")

                    self.create_tab(name, content, path)
                    self.editor_tabs[name]["saved"] = tab.get("saved", True)

            except Exception as e:
                print("Load error:", e)


if __name__ == "__main__":
    app = PyRO()
