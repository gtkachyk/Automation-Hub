from tkinter import messagebox
import tkinter as tk
import os
import subprocess

# Constants
SETTINGS_DIR = "Settings"
FILE_DISPLAY_FILE = SETTINGS_DIR + "/file_display.csv"
SHELLS_FILE = "Shells/shells.csv"
DETECTED_IDENTITIES_FILE = "Shells/detected_identities.csv"
CHAINS_DIR = "Chains"
LISTBOX_ITEM_HEIGHT = 16

def get_detected_identity(shell):
    shell = shell + "\n"
    shell_line = 0
    shell_found = False
    with open(SHELLS_FILE) as shell_file:
        for line in shell_file:
            if line == shell:
                shell_found = True
                break
            else:
                shell_line += 1
    if not shell_found: return "Unknown"

    detected_identities_line = 0
    detected_identity = None
    with open(DETECTED_IDENTITIES_FILE) as detected_identities_file:
        for line in detected_identities_file:
            if shell_line == detected_identities_line:
                detected_identity = line
                break
            else:
                detected_identities_line += 1
    if detected_identity == None: return "Unknown"
    return detected_identity[:-1]

def detect_shell(executable_path: str) -> str:
    shell = identify_shell_by_path(executable_path)
    if shell == "Unknown Shell":
        version_info = get_shell_version(executable_path)
        return f"Detected shell by output: {version_info}"
    return shell

def get_shell_version(executable_path: str) -> str:
    try:
        result = subprocess.run(
            [executable_path, "--version"], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            text=True
        )
        return result.stdout.splitlines()[0]
    except Exception as e:
        return f"Error identifying shell: {e}"

def identify_shell(executable_path: str) -> str:
    executable_name = os.path.basename(executable_path).lower()
    parent_dir = os.path.dirname(executable_path).lower()

    # Mapping of shell executables to their names
    shell_mapping = {
        "cmd.exe": "Command Prompt",
        "powershell.exe": "Windows PowerShell",
        "pwsh": "PowerShell Core",
        "bash": "Bash",
        "zsh": "Z Shell",
        "fish": "Fish Shell",
        "tcsh": "Tcsh",
        "dash": "Dash",
        "busybox": "BusyBox Shell",
        "sh": "Bourne Shell",
        "ksh": "Korn Shell",
        "git-bash.exe": "Git Bash",
        "mingw32.exe": "MinGW32 Shell",
        "msys2.exe": "MSYS2 Shell",
        "cygwin": "Cygwin Bash",
        "alacritty": "Alacritty Terminal",
        "hyper": "Hyper Terminal",
        "iterm2": "iTerm2 (macOS Terminal)",
        "terminal.app": "macOS Terminal",
        "wsl.exe": "Windows Subsystem for Linux (WSL)",
        "nu": "NuShell",
        "xonsh": "Xonsh",
        "elvish": "Elvish Shell",
        "eshell": "Emacs Shell (EShell)",
        "clink": "Clink",
    }

    # Check by executable name
    if executable_name in shell_mapping:
        return shell_mapping[executable_name]

    # Check specific hints from parent directory for more context
    if "cygwin" in parent_dir:
        return "Cygwin Bash"
    if "git" in parent_dir and executable_name == "bash":
        return "Git Bash"
    if "msys" in parent_dir:
        return "MSYS2 Shell"
    if "mingw" in parent_dir:
        return "MinGW Shell"
    if "wsl" in parent_dir or executable_name == "wsl.exe":
        return "Windows Subsystem for Linux (WSL)"
    if "hyper" in parent_dir:
        return "Hyper Terminal"
    if "alacritty" in parent_dir:
        return "Alacritty Terminal"

    return "Unknown Shell"


def identify_shell_by_path(executable_path: str) -> str:
    executable_name = os.path.basename(executable_path).lower()
    parent_dir = os.path.dirname(executable_path).lower()

    if "cygwin" in parent_dir:
        return "Cygwin Bash"
    if "git" in parent_dir and executable_name == "bash":
        return "Git Bash"

    return identify_shell(executable_path)

def normalize_path(input_path: str) -> str:
    return os.path.normpath(input_path)

def prevent_focus(event):
    """Redirect focus to the parent widget or another widget."""
    event.widget.tk_focusNext().focus()

def get_setting(filename):
    """Return the second line in the file 'filename'."""
    try:
        with open(filename, "r") as file:
            lines = file.readlines()
            if len(lines) >= 2:
                return lines[1].strip()  # Strip any leading/trailing whitespace or newline
            else:
                return None  # Return None if the file has fewer than 2 lines
    except FileNotFoundError:
        return None  # Return None if the file doesn't exist
    except Exception as e:
        messagebox.showerror("Error", f"Failed to read setting from {filename}: {e}")
        return None

def listbox_clicked_dead_space(event):
    widget = event.widget
    if isinstance(widget, tk.Listbox):
        clicked_index = widget.nearest(event.y)
        bbox = widget.bbox(clicked_index)
        if bbox == None:
            return True
        if event.y > bbox[1] + LISTBOX_ITEM_HEIGHT:
            return True
    return False
