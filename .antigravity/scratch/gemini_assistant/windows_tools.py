import os
import subprocess
import pyautogui
import datetime
import logging

def open_application(app_name: str):
    """Opens a Windows application."""
    logging.info(f"Opening application: {app_name}")
    try:
        # Simple approach: try to run the command directly
        # This works for things like 'notepad', 'calc', 'mspaint', 'explorer'
        subprocess.Popen(app_name, shell=True)
        return f"Opened {app_name}"
    except Exception as e:
        return f"Failed to open {app_name}: {e}"

def minimize_windows():
    """Minimizes all windows to show the desktop."""
    logging.info("Minimizing windows")
    pyautogui.hotkey('win', 'd')
    return "Minimized all windows"

def type_text(text: str):
    """Types the given text at the current cursor position."""
    logging.info(f"Typing text: {text}")
    pyautogui.write(text, interval=0.01)
    return "Typed text"

def press_hotkey(keys: list):
    """Presses a combination of keys (e.g., ['ctrl', 'c'])."""
    logging.info(f"Pressing hotkey: {keys}")
    try:
        pyautogui.hotkey(*keys)
        return f"Pressed {keys}"
    except Exception as e:
        return f"Failed to press keys: {e}"

def get_system_time():
    """Returns the current system time."""
    now = datetime.datetime.now().strftime("%H:%M")
    return f"The current time is {now}"

# Dictionary mapping function names to the actual functions
# This will be used by the Gemini Agent to execute tools
TOOLS_MAP = {
    "open_application": open_application,
    "minimize_windows": minimize_windows,
    "type_text": type_text,
    "press_hotkey": press_hotkey,
    "get_system_time": get_system_time
}
