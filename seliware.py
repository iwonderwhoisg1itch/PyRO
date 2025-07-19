import ctypes
import os
import shutil
import winreg
import subprocess
import psutil
import httpx
import json
from websocket_stuff import WebSocketStuff

user32 = ctypes.windll.user32

class SeliwareError(Exception):
    pass

def enum_thread_windows(thread_id):
    handles = []

    @ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)
    def callback(hWnd, lParam):
        handles.append(hWnd)
        return True

    user32.EnumThreadWindows(thread_id, callback, 0)
    return handles

def get_window_text(hWnd):
    length = user32.GetWindowTextLengthW(hWnd)
    if length == 0:
        return ""
    buffer = ctypes.create_unicode_buffer(length + 1)
    user32.GetWindowTextW(hWnd, buffer, length + 1)
    return buffer.value

def enumerate_process_window_handles(pid):
    process = psutil.Process(pid)
    handles = []
    for thread in process.threads():
        handles.extend(enum_thread_windows(thread.id))
    return handles

def has_roblox_window(process):
    for hWnd in enumerate_process_window_handles(process.pid):
        text = get_window_text(hWnd)
        if "Roblox" in text:
            return True
    return False

class Seliware:
    initialized = False
    version = "Unknown, not initialized"
    seliware_path = os.path.join(os.getenv("APPDATA"), "Seliware")
    injector_path = os.path.join(seliware_path, "injector.exe")
    dll_path = os.path.join(seliware_path, "test.dll")
    dll_sys32_path = os.path.join(os.environ["SystemRoot"], "SysWOW64", "test.dll")
    injected_event = []

    @staticmethod
    def initialize():
        if Seliware.initialized:
            return False

        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Seliware", 0, winreg.KEY_READ)
        except FileNotFoundError:
            raise SeliwareError("Seliware registry key not found, run seliware loader again")

        session = "test"
        try:
            session, _ = winreg.QueryValueEx(key, "Session")
        except FileNotFoundError:
            pass

        try:
            version, _ = winreg.QueryValueEx(key, "Version")
            Seliware.version = version
        except FileNotFoundError:
            pass

        headers = {"Content-Type": "text/plain"}
        data = {
            "method": "validatesession",
            "session": session
        }

        try:
            with httpx.Client(http2=True, verify=True, timeout=30.0) as client:
                auth_response = client.post(
                    "https://seliware.com/authenticate",
                    headers=headers,
                    content=json.dumps(data)
                )
                if auth_response.status_code != 200 or auth_response.text.strip() != "valid":
                    raise SeliwareError("Authentication failed. Subscription ended?")

                version_response = client.get("https://seliware.com/version.txt")
                if version_response.status_code != 200:
                    raise SeliwareError("Failed to fetch version.")

                server_version = version_response.text.strip()
                if server_version != Seliware.version:
                    raise SeliwareError("Your Seliware is outdated. Please update it using the loader.")
        except Exception as e:
            raise SeliwareError(f"{e}")

        if not os.path.exists(Seliware.injector_path) or not os.path.exists(Seliware.dll_path):
            raise SeliwareError("Missing injector or DLL. Reinstall Seliware and disable antivirus.")

        shutil.copyfile(Seliware.dll_path, Seliware.dll_sys32_path)

        try:
            WebSocketStuff.initialize_socket()
        except Exception as e:
            raise SeliwareError(f"Websocket server initialization failed. {e}")

        Seliware.initialized = True
        return True


    @staticmethod
    def inject(pid: int):
        try:
            proc = psutil.Process(pid)
            if proc.name() not in ["RobloxPlayerBeta.exe", "RobloxPlayerBeta"]:
                return "Invalid process"

            if not has_roblox_window(proc):
                return "Roblox is not loaded"

            subprocess.Popen([Seliware.injector_path, str(pid)], cwd=Seliware.seliware_path, creationflags=subprocess.CREATE_NEW_CONSOLE)
        except Exception as e:
            return str(e)
        return "Success"

    @staticmethod
    def inject_auto():
        found = False
        for proc in psutil.process_iter(['name', 'pid']):
            if proc.info['name'] == "RobloxPlayerBeta.exe":
                if has_roblox_window(proc):
                    Seliware.inject(proc.info['pid'])
                    found = True
        return "Success" if found else "No Roblox found"

    @staticmethod
    def get_clients_count():
        return len(WebSocketStuff.clients)

    @staticmethod
    def is_injected():
        return Seliware.get_clients_count() > 0

    @staticmethod
    def execute(script: str):
        if not Seliware.is_injected():
            return False
        for key, behavior in WebSocketStuff.clients.items():
            behavior.send_message({
                "command": "execute",
                "value": script
            })
        return True

    @staticmethod
    def on_injected():
        for callback in Seliware.injected_event:
            callback()
