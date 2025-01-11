import os
import csv
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from utils import listbox_clicked_dead_space, get_setting, normalize_path, detect_shell

class ShellsWindow:
    def __init__(self, root, shells_file, detected_identities_file, file_display_file, chains_dir):
        self.root = root
        self.shells_file = shells_file
        self.detected_identities_file = detected_identities_file
        self.file_display_file = file_display_file
        self.chains_dir = chains_dir

        self.shells_window = tk.Toplevel(self.root)
        self.shells_window.title("Shells")
        self.shells_window.geometry("400x300")
        self.shells_window.resizable(False, False)
        self.shells_window.bind("<Button-1>", self.handle_outside_click)
        self.shells_window.transient(self.root)
        self.shells_window.grab_set()
        self.shells_window.protocol("WM_DELETE_WINDOW", self._on_close)

        self._setup_ui()
        self.load_shells()
    
    def _on_close(self):
        """Release grab and close the edit chain window."""
        self.shells_window.grab_release()
        self.shells_window.destroy()

    def _setup_ui(self):
        # Frame for listbox and label
        shells_frame = tk.Frame(self.shells_window)
        shells_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Label for listbox
        ttk.Label(shells_frame, text="Shell Programs", width=15).pack(side=tk.TOP)

        # Listbox to display shells
        self.shell_listbox = tk.Listbox(shells_frame, activestyle=tk.NONE, exportselection=False)
        self.shell_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Frame for buttons
        shell_button_frame = tk.Frame(self.shells_window)
        shell_button_frame.pack(pady=10)

        self.add_shell_button = tk.Button(shell_button_frame, text="Add Shell", command=self.add_shell)
        self.add_shell_button.pack(side=tk.LEFT, padx=5)

        self.remove_shell_button = tk.Button(shell_button_frame, text="Remove Selected", command=self.remove_selected_shell)
        self.remove_shell_button.pack(side=tk.LEFT, padx=5)
        self.remove_shell_button.config(state="disabled")

    def load_shells(self):
        """Load shells from the CSV file."""
        self.shell_listbox.delete(0, tk.END)
        try:
            with open(self.shells_file, "r") as f:
                reader = csv.reader(f)
                for row in reader:
                    if row:
                        file_display_setting = get_setting(self.file_display_file)
                        if file_display_setting == "Full path":
                            self.shell_listbox.insert(tk.END, row[0])
                        elif file_display_setting == "File name only":
                            self.shell_listbox.insert(tk.END, os.path.basename(row[0]))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load shells: {e}")

    def add_shell(self):
        """Add a new shell program."""
        filepath = filedialog.askopenfilename(title="Select Shell Program")
        if filepath:
            try:
                with open(self.shells_file, "a", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerow([normalize_path(filepath)])
                with open(self.detected_identities_file, "a", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerow([detect_shell(normalize_path(filepath))])

                self.load_shells()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add shell: {e}")

    def remove_selected_shell(self):
        """Remove the selected shell from the list."""
        selected_indices = self.shell_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("Warning", "No shell selected to remove.")
            return

        if messagebox.askyesno("Confirm Delete", "WARNING: deleting a shell program will remove all execution chain links that use it. Are you sure you want to delete the selected shell program?"):
            try:
                # Read all shells, filter out selected ones
                with open(self.shells_file, "r") as f:
                    rows = list(csv.reader(f))
                remaining_rows = [row for i, row in enumerate(rows) if i not in selected_indices]

                # Write back the remaining rows
                with open(self.shells_file, "w", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerows(remaining_rows)

                # Remove all links that use the selected shell from all chains
                selected_shells = {rows[i][0] for i in selected_indices}  # Get selected shell names
                for chain_file in os.listdir(self.chains_dir):
                    chain_path = os.path.join(self.chains_dir, chain_file)
                    if os.path.isfile(chain_path) and chain_file.endswith(".csv"):
                        with open(chain_path, "r") as chain_f:
                            chain_links = list(csv.reader(chain_f))
                            filtered_links = [link for link in chain_links if link[0] not in selected_shells]
                        with open(chain_path, "w", newline="") as chain_f:
                            writer = csv.writer(chain_f)
                            writer.writerows(filtered_links)

                # Reload shells and reset the button state
                self.load_shells()
                self.remove_shell_button.config(state="disabled")

            except Exception as e:
                messagebox.showerror("Error", f"Failed to remove shell: {e}")

    def handle_outside_click(self, event):
        """Handle clicks outside of specific widgets to deselect the shell."""
        widget = event.widget
        if isinstance(widget, tk.Listbox):
            if listbox_clicked_dead_space(event):
                self.deselect_shell()
            else:
                self.on_shell_select(event)
        if widget != self.shell_listbox and widget != self.remove_shell_button:
            self.deselect_shell()

    def deselect_shell(self):
        """Deselect the currently selected shell."""
        self.shell_listbox.selection_clear(0, tk.END)
        self.remove_shell_button.config(state="disabled")
    
    def on_shell_select(self, event):
        """Handel shell_listbox item selection."""
        # Enable buttons if a selection is made
        self.remove_shell_button.config(state="normal")
