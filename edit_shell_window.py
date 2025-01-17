import tkinter as tk
from tkinter import Toplevel, messagebox, ttk
from utils import detect_shell, normalize_path, get_shell_options, IDENTITIES_FILE, SHELL_OPTIONS_FILE

class EditShellWindow:
    """A class to encapsulate the edit shell window logic."""

    def __init__(self, root, selected_shell, selected_shell_identity, shell_index):
        self.root = root
        self.selected_shell = selected_shell
        self.selected_shell_identity = selected_shell_identity
        self.shell_index = shell_index
        self.shell_options = get_shell_options(self.selected_shell)
        self.create_window()
        self.create_widgets()

    def create_window(self):
        """Creates the settings window."""
        self.edit_shell_window = Toplevel(self.root)
        self.edit_shell_window.title("Shell Options")
        self.edit_shell_window.geometry("615x175")
        self.edit_shell_window.resizable(False, False)
        self.edit_shell_window.transient(self.root)
        self.edit_shell_window.grab_set()
        self.edit_shell_window.protocol("WM_DELETE_WINDOW", self._on_close)

    def create_widgets(self):
        """Creates widgets for the edit shell window."""
        # Constants
        label_width = 8
        pady = 15

        # Shell identity
        shell_identity_frame = tk.Frame(self.edit_shell_window)
        shell_identity_frame.grid(row=0, column=0, sticky="nw", padx=5, pady=5)
        ttk.Label(shell_identity_frame, text="Identity:", width=label_width).grid(row=0, column=0, padx=5, pady=pady, sticky="w")
        self.shell_identity_entry = tk.Entry(shell_identity_frame)
        self.shell_identity_entry.grid(row=0, column=1, sticky="w", padx=5, pady=5)
        self.shell_identity_entry.insert(0, self.selected_shell_identity)
        ttk.Button(shell_identity_frame, text="Auto Detect", command=self.run_auto_detect).grid(row=0, column=2)

        # Command
        command_frame = tk.Frame(self.edit_shell_window)
        command_frame.grid(row=1, column=0, sticky="nw", padx=5, pady=5)
        ttk.Label(command_frame, text="Options:", width=label_width).grid(row=1, column=0, padx=5, pady=pady, sticky="w")
        self.shell_command_entry = tk.Entry(command_frame)
        self.shell_command_entry.grid(row=1, column=1, sticky="w", padx=5, pady=5)
        self.shell_command_entry.insert(0, self.shell_options[0])
        self.shell_command_entry.config(state="disabled")

        self.pre_script_command_entry = tk.Entry(command_frame)
        self.pre_script_command_entry.grid(row=1, column=2, sticky="w", padx=5, pady=5)
        self.pre_script_command_entry.insert(0, self.shell_options[1])

        self.script_command_entry = tk.Entry(command_frame)
        self.script_command_entry.grid(row=1, column=3, sticky="w", padx=5, pady=5)
        self.script_command_entry.insert(0, self.shell_options[2])
        self.script_command_entry.config(state="disabled")

        self.post_script_command_entry = tk.Entry(command_frame)
        self.post_script_command_entry.grid(row=1, column=4, sticky="w", padx=5, pady=5)
        self.post_script_command_entry.insert(0, self.shell_options[3].rstrip())

        # Save button
        button_frame = tk.Frame(self.edit_shell_window)
        button_frame.grid(row=2, column=0, columnspan=2, sticky="s", pady=pady)
        ttk.Button(button_frame, text="Save", command=self.save_shell_options).grid(row=0, column=0)

    def _on_close(self):
        """Release grab and close the edit shell window."""
        self.edit_shell_window.grab_release()
        self.edit_shell_window.destroy()

    def save_shell_options(self):
        # Save identity
        with open(IDENTITIES_FILE, "r") as f:
            lines = f.readlines()

        lines[self.shell_index] = self.selected_shell + "," + self.shell_identity_entry.get() + "\n"

        with open(IDENTITIES_FILE, "w") as f:
            f.writelines(lines)

        # Save command
        with open(SHELL_OPTIONS_FILE, "r") as f:
            lines = f.readlines()

        for i in range(0, len(lines)):
            options = lines[i].split(",")
            if options[0] == self.selected_shell:
                lines[i] = self.shell_command_entry.get() + "," + self.pre_script_command_entry.get() + "," + self.script_command_entry.get() + "," + self.post_script_command_entry.get().rstrip() + "\n"
                break

        with open(SHELL_OPTIONS_FILE, "w") as f:
            f.writelines(lines)
        
        messagebox.showinfo("Success", "Shell options saved successfully!")
        self.edit_shell_window.destroy()

    def run_auto_detect(self):
        self.shell_identity_entry.delete(0, tk.END)
        self.shell_identity_entry.insert(0, detect_shell(normalize_path(self.selected_shell)))
