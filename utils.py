from tkinter import messagebox
import tkinter as tk
import os
import subprocess
import csv

# Constants
## Settings
EXIT_AFTER_EXECUTION_DEFAULT = "Never"
EXIT_AFTER_EXECUTION_OPTIONS = ["Always", "After success only", "After failure only", "Never"]
FILE_DISPLAY_DEFAULT = "File name only"
FILE_DISPLAY_OPTIONS = ["Full path", "File name only"]

## Files
CHAINS_DIR = "Chains"
RESOURCES_DIR = "Resources"
ICON_TASKBAR_FILE = "Resources/icon_taskbar.ico"
ICON_WINDOW_FILE = "Resources/icon_window.ico"
SETTINGS_DIR = "Settings"
FILE_DISPLAY_FILE = "Settings/file_display.csv"
EXIT_AFTER_EXECUTION_FILE = "Settings/exit_after_execution.csv"
SHELLS_DIR = "Shells"
IDENTITIES_FILE = "Shells/identities.csv"
SHELL_OPTIONS_FILE = "Shells/shell_options.csv"
SHELLS_FILE = "Shells/shells.csv"

## Misc
LISTBOX_ITEM_HEIGHT = 16
DELIMITER = ","
SCRIPT_PLACEHOLDER = "<your-script>"

def load_dropdown(dropdown, file, var, options):
    """Load file display options into the dropdown menu."""
    try:
        with open(file, "r") as f:
            reader = csv.reader(f)
            for row in reader:
                if row:
                    options.append(row[0])

        # Set the dropdown values and the default value
        dropdown["values"] = options[3:]
        if options:
            var.set(options[1])
    except Exception as e:
        messagebox.showerror(
            "Error", f"Failed to load dropdown options: {e}"
        )

def setup_application_files():
    confirm_dir_existence(CHAINS_DIR)
    confirm_dir_existence(RESOURCES_DIR)
    confirm_file_existence(ICON_TASKBAR_FILE)
    confirm_file_existence(ICON_WINDOW_FILE)
    confirm_dir_existence(SETTINGS_DIR)
    confirm_file_existence(FILE_DISPLAY_FILE)
    confirm_file_existence(EXIT_AFTER_EXECUTION_FILE)
    confirm_dir_existence(SHELLS_DIR)
    confirm_file_existence(IDENTITIES_FILE)
    confirm_file_existence(SHELL_OPTIONS_FILE)
    confirm_file_existence(SHELLS_FILE)

def confirm_dir_existence(dir):
    os.makedirs(dir, exist_ok=True)

def confirm_file_existence(file):
    if not os.path.exists(file):
        with open(file, "w") as f:
            pass
    
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
    with open(IDENTITIES_FILE) as detected_identities_file:
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
        return f"{version_info}"
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
                return lines[1].strip() # Strip any leading/trailing whitespace or newline
            else:
                return None # Return None if the file has fewer than 2 lines
    except FileNotFoundError:
        return None # Return None if the file doesn't exist
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

def get_shell_by_index(index):
    with open(SHELLS_FILE) as f:
        return f.readlines()[index]

def get_shell_identity_by_index(index):
    with open(IDENTITIES_FILE) as f:
        return f.readlines()[index].split(",")[1].rstrip()

def get_shell_options(shell):
    with open(SHELL_OPTIONS_FILE) as f:
        lines = f.readlines()
        for line in lines:
            options = line.split(",")
            if options[0] == shell:
                return options
    raise Exception("Error: could not find shell options for shell: " + str(shell))

def is_valid_settings_file(file, supported_options):
    try:
        if not os.path.isfile(file):
            raise Exception(f"does not exist.")
        expected_lines = len(supported_options) + 3
        with open(file) as f:
            lines = f.readlines()
            if len(lines) > expected_lines:
                raise Exception(f"invalid number of lines ({len(lines)}).")
            if lines[0].strip() != "# Selected":
                raise Exception(f"first line does not equal '# Selected'.")
            if lines[1].strip() not in supported_options:
                raise Exception(f"selected option ({lines[1].strip()}) is not in list of supported options.")
            if lines[2].strip() != "# Options":
                raise Exception(f"third line does not equal '# Options'.")
            if lines[3:expected_lines] != [opt + "\n" for opt in supported_options]:
                raise Exception(f"list of supported options is invalid.")
    except Exception as e:
        raise Exception(f"settings file '{file}' is invalid ---> {e}.")

def validate_file(file):
    normalized_file = file
    normalized_file = normalize_path(normalized_file)
    try:
        if file != normalized_file:
            raise Exception(f"path is not normalized")
        if not os.path.isfile(file):
            raise Exception(f"does not exist")
        if DELIMITER in file:
            raise Exception(f"path contains forbidden characters")
    except Exception as e:
        raise Exception(f"file '{file}' is invalid ---> {e}.")

def validate_shell(shell):
    try:
        validate_file(shell)
        # Check if shell has exactly one entry in SHELLS_FILE
        with open(SHELLS_FILE) as shells_file:
            shells = shells_file.readlines()
            if shells.count(shell + "\n") != 1:
                raise Exception(f"did not find exactly one corresponding entry in {SHELLS_FILE}")

        # Check if shell has exactly one entry in SHELLS_OPTIONS_FILE
        with open(SHELL_OPTIONS_FILE) as options_file:
            options = [line.split(",")[0] for line in options_file]
            if options.count(shell) != 1:
                raise Exception(f"did not find exactly one corresponding entry in {SHELL_OPTIONS_FILE}")

        # Check if shell has exactly one entry in IDENTITIES_FILE
        with open(IDENTITIES_FILE) as identities_file:
            identities = [line.split(",")[0] for line in identities_file]
            if identities.count(shell) != 1:
                raise Exception(f"did not find exactly one corresponding entry in {IDENTITIES_FILE}")
    except Exception as e:
        raise Exception(f"shell '{shell}' is invalid ---> {e}")

def validate_link(link):
    parts = link.split(DELIMITER)
    try:
        if len(parts) != 2:
            raise Exception(f"improperly formatted.")
        shell, script = parts
        validate_shell(shell)
        validate_file(script)
    except Exception as e:
        raise Exception(f"link '{link}' is invalid ---> {e}.") 

def validate_chains_directory():
    """Validates the Chains directory and its contents."""
    # Check if CHAINS_DIR exists
    if not os.path.isdir(CHAINS_DIR):
        raise Exception(f"chains directory does not exist")

    for chain_file in os.listdir(CHAINS_DIR):
        chain_path = os.path.join(CHAINS_DIR, chain_file)
        if not chain_file.endswith(".csv"):
            continue

        try:
            # Check if each link is valid in each chain file
            with open(chain_path) as f:
                links = f.readlines()
                for link in links:
                    validate_link(link.strip())
        except Exception as e:
            raise Exception(f"chains directory is invalid ---> chain file '{chain_file}' is invalid ---> {e}")

def validate_settings_directory():
    """Validates the Settings directory and its contents."""
    if not os.path.isdir(SETTINGS_DIR):
        raise Exception(f"settings directory does not exist")

    # Validate exit_after_execution.csv
    is_valid_settings_file(EXIT_AFTER_EXECUTION_FILE, EXIT_AFTER_EXECUTION_OPTIONS)

    # Validate file_display.csv
    is_valid_settings_file(FILE_DISPLAY_FILE, FILE_DISPLAY_OPTIONS)

def validate_shells_directory():
    """Validates the Shells directory and its contents."""
    if not os.path.isdir(SHELLS_DIR):
        raise Exception(f"shells directory does not exist")

    try:
        with open(SHELLS_FILE) as shells_file:
            shells = shells_file.readlines()

        with open(IDENTITIES_FILE) as identities_file:
            identities = identities_file.readlines()

        with open(SHELL_OPTIONS_FILE) as options_file:
            options = options_file.readlines()

        if len(shells) != len(identities):
            raise Exception(f"found unequal number of shells ({len(shells)}) and shell identities ({len(identities)}).")
        if len(shells) != len(options):
            raise Exception(f"found unequal number of shells ({len(shells)}) and shell option lists ({len(options)}).")

        for i, shell in enumerate(shells):
            shell = shell.strip()
            validate_file(shell)

            identity_parts = identities[i].strip().split(DELIMITER)
            if len(identity_parts) != 2:
                raise Exception(f"invalid identity entry '{identity_parts}' for shell {shell}.")
            if identity_parts[0] != shell:
                raise Exception(f"invalid identity '{identity_parts[0]}' for shell {shell}.")

            option_parts = options[i].strip().split(DELIMITER)
            if len(option_parts) != 4:
                raise Exception(f"invalid options entry '{option_parts}' for shell {shell}.")
            if option_parts[0] != shell:
                raise Exception(f"invalid first option '{option_parts[0]}' for shell {shell}.")
            if option_parts[2] != SCRIPT_PLACEHOLDER:
                raise Exception(f"invalid third option '{option_parts[2]}' for shell {shell}.")
    except Exception as e:
        raise Exception(f"shells directory is invalid ---> {e}")

def validate_state():
    """Validates the overall state of the application."""
    try:
        validate_chains_directory()
        validate_settings_directory()
        validate_shells_directory()
    except Exception as e:
        raise Exception(e)
