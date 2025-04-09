import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import os
import json
import clr
import psutil
from random import randint

script_dir = os.path.dirname(os.path.abspath(__file__))
dll_path = os.path.join(script_dir, "SeliwareAPI.dll")
scripts_dir = os.path.join(script_dir, "scripts")
saved_tabs_dir = os.path.join(script_dir, "saved_tabs")
tabs_file = os.path.join(script_dir, "open_tabs.json")

clr.AddReference(dll_path)
from SeliwareAPI import Seliware

Seliware.Initialize()

rbx_pids = []

os.makedirs(saved_tabs_dir, exist_ok=True)
os.makedirs(scripts_dir, exist_ok=True)

class ExecutorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PyRO ui")
        self.root.geometry("800x600")

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.tabview = ctk.CTkTabview(root)
        self.tabview.pack(pady=10, padx=10, fill="both", expand=True)

        self.tabview.add("Main")
        self.tabview.add("Scripts")
        self.tabview.add("Options")

        self.editor_tabs = {}
        
        self.init_main_tab()
        self.init_scripts_tab()
        self.load_tabs()

    def init_main_tab(self):
        tab = self.tabview.tab("Main")
        self.editor_tabview = ctk.CTkTabview(tab)
        self.editor_tabview.pack(padx=10, pady=10, fill="both", expand=True)
        
        self.setup_menu()

        btn_frame = ctk.CTkFrame(tab)
        btn_frame.pack(pady=5)

        ctk.CTkButton(btn_frame, text="Execute", command=self.run_code, width=100).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Clear", command=self.clear_content, width=100).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Attach", command=self.attach_process, width=100, fg_color="#FF4500", hover_color="#FF6347").pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="New tab", command=self.add_tab, width=100).pack(side="left", padx=5)

    def init_scripts_tab(self):
        tab = self.tabview.tab("Scripts")
        self.script_list = tk.Listbox(tab, bg="#1a1a1a", fg="white", selectbackground="#3a3a3a", height=15)
        self.script_list.pack(padx=10, pady=(10, 5), fill="both", expand=True)
        self.script_list.bind("<Button-3>", self.show_script_menu)

        ctk.CTkButton(tab, text="Refresh", command=self.update_scripts).pack(pady=5)
        self.update_scripts()

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
        
        text_box = ctk.CTkTextbox(new_tab)
        text_box.pack(fill="both", expand=True, padx=5, pady=5)
        text_box.insert("1.0", content)
        text_box.bind("<Button-3>", lambda e: self.popup_menu.tk_popup(e.x_root, e.y_root))
        
        self.editor_tabs[name] = {
            "textbox": text_box,
            "path": path,
            "saved": True if path else False
        }
        
        self.editor_tabview.set(name)
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

    def attach_process(self):
        global rbx_pids
        found = [proc.pid for proc in psutil.process_iter(['name']) if proc.info['name'] == "RobloxPlayerBeta.exe"]
        for pidor in found:
            if pidor not in rbx_pids:
                rbx_pids.append(pidor)
                Seliware.Inject(pidor)
        rbx_pids = [pid for pid in rbx_pids if psutil.pid_exists(pid)]

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
                self.editor_tabs[new_name] = tab_data
                self.editor_tabview.delete(current)
                self.editor_tabview.add(new_name)
                self.editor_tabview.set(new_name)
                self.save_tabs()

    def remove_tab(self):
        current = self.editor_tabview.get()
        if current:
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
                        return
                    elif answer:
                        self.store_tab(name)
            
            self.editor_tabview.delete(name)
            self.editor_tabs.pop(name)
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
    root = ctk.CTk()
    app = ExecutorApp(root)
    root.mainloop()