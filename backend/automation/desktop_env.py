import os
import subprocess
import webbrowser
import pyautogui
import time

def open_application(app_name):
    """Attempt to open a common application by name."""
    app_name = app_name.lower()
    
    if 'chrome' in app_name:
        print("Opening Chrome...")
        # Cross-platform way: start empty browser
        webbrowser.open('http://google.com')
        return "Opened Google Chrome"
        
    elif 'notepad' in app_name:
        print("Opening Notepad...")
        if os.name == 'nt':
            subprocess.Popen('notepad.exe')
        return "Opened Notepad"
        
    elif 'calculator' in app_name or 'calc' in app_name:
        print("Opening Calculator...")
        if os.name == 'nt':
            subprocess.Popen('calc.exe')
        return "Opened Calculator"
        
    else:
        # Fallback: Just open the start menu and type it (Windows specific fallback)
        if os.name == 'nt':
            pyautogui.press('win')
            time.sleep(0.5)
            pyautogui.write(app_name)
            time.sleep(0.5)
            pyautogui.press('enter')
            return f"Attempted to open {app_name} via Windows search"
        return f"Cannot open {app_name} on this OS yet"

def search_youtube(query):
    """Search YouTube for the given query."""
    print(f"Searching YouTube for: {query}")
    url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
    webbrowser.open(url)
    return f"Searching YouTube for {query}"

def play_music():
    """Simulate media play/pause key."""
    print("Toggling Media Play/Pause...")
    pyautogui.press('playpause')
    return "Toggled media playback"

def set_volume(level="up"):
    """Increase or decrease volume."""
    if level == "up":
        pyautogui.press('volumeup', presses=5)
        return "Increased volume"
    elif level == "down":
        pyautogui.press('volumedown', presses=5)
        return "Decreased volume"
    elif level == "mute":
        pyautogui.press('volumemute')
        return "Muted volume"

def shutdown_system(confirm=False):
    """Shutdown the system (only if confirmed)."""
    if confirm:
        print("Shutting down system...")
        if os.name == 'nt':
            os.system('shutdown /s /t 10') # 10 second warning
            return "System will shut down in 10 seconds."
        else:
            return "Shutdown command not implemented for this OS."
    else:
        return "Shutdown requires confirmation."
