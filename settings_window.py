import tkinter as tk
from tkinter import Toplevel, StringVar, messagebox, ttk
from utils import prevent_focus, load_dropdown

class SettingsWindow:
    """A class to encapsulate the settings window logic."""

    def __init__(self, root, file_display_file, exit_after_execution_file):
        self.root = root
        self.file_display_file = file_display_file
        self.file_display_var = StringVar()
        self.file_display_options = []
        self.exit_after_execution_file = exit_after_execution_file
        self.exit_after_execution_var = StringVar()
        self.exit_after_execution_options = []
        self.focus_dropdown_var = StringVar()
        self.create_window()
        self.create_widgets()

    def create_window(self):
        """Creates the settings window."""
        self.settings_window = Toplevel(self.root)
        self.settings_window.title("Settings")
        self.settings_window.geometry("400x200")
        self.settings_window.resizable(False, False)
        self.settings_window.transient(self.root)
        self.settings_window.grab_set()
        self.settings_window.protocol("WM_DELETE_WINDOW", self._on_close)

    def create_widgets(self):
        """Creates widgets for the settings window."""
        # Constants
        dropdown_width = 35

        # Label frame
        label_frame = tk.Frame(self.settings_window)
        label_frame.grid(row=0, column=0, sticky="nw", padx=5, pady=5)
        ttk.Label(label_frame, text="File Display:", width=15).grid(row=0, column=0, padx=5, pady=20, sticky="w")
        ttk.Label(label_frame, text="Exit After Execution:", width=18).grid(row=1, column=0, padx=5, pady=20, sticky="w")

        # Dropdown frame
        dropdown_frame = tk.Frame(self.settings_window)
        dropdown_frame.grid(row=0, column=1, sticky="ne", padx=5, pady=5)
        self.file_display_dropdown = ttk.Combobox(
            dropdown_frame,
            textvariable=self.file_display_var,
            state="readonly",
            width=dropdown_width
        )
        self.file_display_dropdown.grid(row=0, column=0, padx=5, pady=20)
        self.file_display_dropdown.bind("<FocusIn>", prevent_focus)

        self.exit_after_execution_dropdown = ttk.Combobox(
            dropdown_frame,
            textvariable=self.exit_after_execution_var,
            state="readonly",
            width=dropdown_width
        )
        self.exit_after_execution_dropdown.grid(row=1, column=0, padx=5, pady=20)
        self.exit_after_execution_dropdown.bind("<FocusIn>", prevent_focus)

        # Save button frame
        button_frame = tk.Frame(self.settings_window)
        button_frame.grid(row=1, column=0, columnspan=2, sticky="s", pady=20)
        ttk.Button(button_frame, text="Save", command=self.save_settings).grid(row=0, column=0)

        # Initialize the dropdown menu
        load_dropdown(self.file_display_dropdown, self.file_display_file, self.file_display_var, self.file_display_options)
        load_dropdown(self.exit_after_execution_dropdown, self.exit_after_execution_file, self.exit_after_execution_var, self.exit_after_execution_options)

    def _on_close(self):
        """Release grab and close the edit chain window."""
        self.settings_window.grab_release()
        self.settings_window.destroy()

    def update_setting(self, value, settings_file):
        """Save a setting selection to its file"""
        try:
            with open(settings_file, "r") as file:
                lines = file.readlines()

            # Replace or add the second line
            if len(lines) >= 2:
                lines[1] = value + "\n"
            else:
                while len(lines) < 1:
                    lines.append("\n")
                lines.append(value + "\n")

            with open(settings_file, "w") as file:
                file.writelines(lines)

            return True
        except Exception as e:
            return False
        
    def save_settings(self):
        """Save the selected settings options."""
        file_display_save_result = self.update_setting(self.file_display_var.get(), self.file_display_file)
        if not file_display_save_result: raise Exception("Error: could not save file display setting.")
        exit_after_execution_save_result = self.update_setting(self.exit_after_execution_var.get(), self.exit_after_execution_file)
        if not exit_after_execution_save_result: raise Exception("Error could not save exit after execution setting.")
        messagebox.showinfo("Success", "Settings saved successfully!")
        self.settings_window.destroy()
