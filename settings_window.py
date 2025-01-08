import csv
from tkinter import Toplevel, StringVar, messagebox, ttk
from utils import prevent_focus

class SettingsWindow:
    """A class to encapsulate the settings window logic."""

    def __init__(self, root, file_display_file):
        self.root = root
        self.file_display_file = file_display_file
        self.file_display_var = StringVar()
        self.file_display_options = []
        self.create_window()

    def create_window(self):
        """Creates the settings window."""
        self.settings_window = Toplevel(self.root)
        self.settings_window.title("Settings")
        self.settings_window.geometry("400x300")
        self.settings_window.resizable(False, False)

        # Dropdown menu to select the file display option
        ttk.Label(self.settings_window, text="File Display:").pack(pady=10)
        self.file_display_dropdown = ttk.Combobox(
            self.settings_window,
            textvariable=self.file_display_var,
            state="readonly",
        )
        self.file_display_dropdown.pack(pady=10)
        self.file_display_dropdown.bind("<FocusIn>", prevent_focus)

        # Initialize the dropdown menu
        self.load_file_display_dropdown()

        # Save button
        ttk.Button(
            self.settings_window, text="Save", command=self.save_settings
        ).pack(pady=20, side="bottom")

        self.settings_window.transient(self.root)
        self.settings_window.grab_set()
        self.settings_window.protocol("WM_DELETE_WINDOW", self._on_close)
    
    def _on_close(self):
        """Release grab and close the edit chain window."""
        self.settings_window.grab_release()
        self.settings_window.destroy()

    def load_file_display_dropdown(self):
        """Load file display options into the dropdown menu."""
        try:
            with open(self.file_display_file, "r") as f:
                reader = csv.reader(f)
                for row in reader:
                    if row:
                        self.file_display_options.append(row[0])

            # Set the dropdown values and the default value
            self.file_display_dropdown["values"] = self.file_display_options[3:]
            if self.file_display_options:  # Ensure there are options to set as the default
                self.file_display_var.set(self.file_display_options[1])  # Default value
        except Exception as e:
            messagebox.showerror(
                "Error", f"Failed to load file display options: {e}"
            )

    def save_settings(self):
        """Save the selected file display option."""
        file_display_selection = self.file_display_var.get()
        try:
            with open(self.file_display_file, "r") as file_display_file:
                lines = file_display_file.readlines()

            # Replace or add the second line
            if len(lines) >= 2:
                lines[1] = file_display_selection + "\n"
            else:
                while len(lines) < 1:
                    lines.append("\n")
                lines.append(file_display_selection + "\n")

            with open(self.file_display_file, "w") as file_display_file:
                file_display_file.writelines(lines)

            messagebox.showinfo("Success", "Settings saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {e}")
