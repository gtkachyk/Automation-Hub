import tkinter as tk
from tkinter import Toplevel, messagebox, filedialog, ttk, StringVar
import os
import csv
from utils import listbox_clicked_dead_space, get_setting, prevent_focus

class EditChainWindow:
    def __init__(self, root, chain_listbox, load_chains, chains_dir, shells_file, file_display_file, chain_name=None):
        self.root = root
        self.chain_listbox = chain_listbox
        self.load_chains = load_chains
        self.chains_dir = chains_dir
        self.shells_file = shells_file
        self.file_display_file = file_display_file
        self.chain_name = chain_name
        self.file_display_setting = get_setting(self.file_display_file)

        self.shells = [] # A list of all the user's shells, loaded in when the window opens.
        self.displayed_shells = []
        self.chain_links = []

        self.selected_script = StringVar() # The stored value of the selected script
        self.selected_shell_alias = StringVar() # The display value of the selected shell. The stored value is accessed by index in the shells list
        self.selected_script_alias = StringVar() # The display value of the selected script

        self._create_window()

    def _create_window(self):
        self.edit_chain_window = Toplevel(self.root)
        self.edit_chain_window.title("Edit Execution Chain")
        self.edit_chain_window.geometry("500x500")
        self.edit_chain_window.resizable(False, False)
        self.edit_chain_window.bind("<Button-1>", self._handle_outside_click)
        self.edit_chain_window.transient(self.root)
        self.edit_chain_window.grab_set()
        self.edit_chain_window.protocol("WM_DELETE_WINDOW", self._on_close)

        self._create_widgets()
        self._initialize_data()

    def _on_close(self):
        """Release grab and close the edit chain window."""
        self.edit_chain_window.grab_release()
        self.edit_chain_window.destroy()

    def _create_widgets(self):
        field_width = 50
        button_width = 8

        # Chain name
        chain_name_frame = tk.Frame(self.edit_chain_window)
        chain_name_frame.pack(pady=5, fill=tk.X)
        ttk.Label(chain_name_frame, text="Chain Name:", width=15).pack(side=tk.LEFT, padx=5)
        self.chain_name_entry = tk.Entry(chain_name_frame, width=field_width)
        self.chain_name_entry.pack(side=tk.LEFT, padx=5)
        if self.chain_name:
            self.chain_name_entry.insert(0, self.chain_name)

        # Shell dropdown
        shell_frame = tk.Frame(self.edit_chain_window)
        shell_frame.pack(pady=5, fill=tk.X)
        ttk.Label(shell_frame, text="Select Shell:", width=15).pack(side=tk.LEFT, padx=5)
        self.shell_dropdown = ttk.Combobox(
            shell_frame,
            textvariable=self.selected_shell_alias,
            state="readonly",
            width=field_width - 3
        )
        self.shell_dropdown.pack(side=tk.LEFT, padx=5)
        self.shell_dropdown.bind("<FocusIn>", prevent_focus)

        # Select script
        script_frame = tk.Frame(self.edit_chain_window)
        script_frame.pack(pady=5, fill=tk.X)
        ttk.Label(script_frame, text="Selected Script:", width=15).pack(side=tk.LEFT, padx=5)
        self.selected_script_display = tk.Entry(
            script_frame,
            textvariable=self.selected_script_alias,
            state="readonly",
            width=field_width
        )
        self.selected_script_display.pack(side=tk.LEFT, padx=5)
        self.select_script_button = tk.Button(script_frame, width=button_width, text="Browse", command=self._select_script)
        self.select_script_button.pack(side=tk.LEFT, padx=5)

        # Link buttons
        link_button_frame = tk.Frame(self.edit_chain_window)
        link_button_frame.pack(pady=10)
        self.add_link_button = tk.Button(link_button_frame, width=button_width, text="Add Link", command=self._add_chain_link)
        self.add_link_button.pack(side=tk.LEFT, padx=5)
        self.add_link_button.config(state="disabled")
        self.delete_link_button = tk.Button(link_button_frame, width=button_width, text="Delete Link", command=self._delete_chain_link, state="disabled")
        self.delete_link_button.pack(side=tk.LEFT, padx=5)
        self.overwrite_selected_link_button = tk.Button(link_button_frame, width=button_width + 3, text="Overwrite Link", command=self._overwrite_selected_chain_link, state="disabled")
        self.overwrite_selected_link_button.pack(side=tk.LEFT, padx=5)

        # Chain links listbox
        self.link_listbox = tk.Listbox(self.edit_chain_window, height=20, activestyle=tk.NONE, exportselection=False)
        self.link_listbox.pack(padx=20, fill=tk.BOTH)

        # Save button
        save_button = tk.Button(self.edit_chain_window, width=button_width, text="Save Chain", command=self._save_chain)
        save_button.pack(pady=5)

    def _initialize_data(self):
        self._load_shells_into_dropdown()
        self._load_chain_links()

    def _load_shells_into_dropdown(self):
        """Load shells into the dropdown menu."""
        try:
            with open(self.shells_file, "r") as f:
                reader = csv.reader(f)
                self.shells.clear()
                for row in reader:
                    if row:
                        self.shells.append(row[0])
                self.displayed_shells = self.get_display_strings(self.shells)
                self.shell_dropdown['values'] = self.displayed_shells
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load shells: {e}")

    def _load_chain_links(self):
        """Load chain links for editing."""
        self.link_listbox.delete(0, tk.END)
        if self.chain_name:
            chain_file = os.path.join(self.chains_dir, f"{self.chain_name}.csv")
            try:
                with open(chain_file, "r") as f:
                    reader = csv.reader(f)
                    for i, row in enumerate(reader):
                        if len(row) == 2:
                            self.link_listbox.insert(tk.END, f"Link-{i}")
                            self.chain_links.append(row)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load chain: {e}")

    def _select_script(self):
        """Open a file dialog to select a script and update the display."""
        filepath = filedialog.askopenfilename(title="Select Shell Script")
        if filepath:
            self.selected_script.set(filepath)
            self.selected_script_alias.set(self.get_display_string(filepath))

            # Enable the add link button if a shell is also selected
            if self.selected_shell_alias.get(): self.add_link_button.config(state="normal")

    def _add_chain_link(self):
        """Add a new chain link."""
        shell = self.shells[self.shell_dropdown.current()]
        script = self.selected_script.get()
        if not shell or not script:
            messagebox.showwarning("Warning", "Please select a shell and script.")
            return
        self.chain_links.append([shell, script])
        self.link_listbox.insert(tk.END, f"Link-{len(self.chain_links) - 1}")
    
    def _delete_chain_link(self):
        """Delete the selected chain link."""
        selected_index = self.link_listbox.curselection()
        if not selected_index:
            messagebox.showwarning("Warning", "Please select a link to delete.")
            return

        index = selected_index[0]
        del self.chain_links[index]
        self.link_listbox.delete(index)

        # Update listbox display
        self.link_listbox.delete(0, tk.END)
        for i, _ in enumerate(self.chain_links):
            self.link_listbox.insert(tk.END, f"Link-{i}")
        messagebox.showinfo("Success", "Selected link deleted.")
    
    def _overwrite_selected_chain_link(self):
        """Overwrite the selected chain link."""
        selected_index = self.link_listbox.curselection()
        if not selected_index:
            messagebox.showwarning("Warning", "Please select a link to overwrite.")
            return

        index = selected_index[0]
        shell = self.shells[self.shell_dropdown.current()]
        script = self.selected_script.get()

        if not shell or not script:
            messagebox.showwarning("Warning", "Please select both a shell and a script.")
            return

        self.chain_links[index] = [shell, script]
        messagebox.showinfo("Success", "Selected link updated.")
    
    def _save_chain(self):
        """Save the chain to a CSV file."""
        chain_name = self.chain_name_entry.get().strip()
        if not chain_name:
            messagebox.showwarning("Warning", "Please enter a chain name.")
            return

        chain_file = os.path.join(self.chains_dir, f"{chain_name}.csv")
        try:
            with open(chain_file, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerows(self.chain_links)
            messagebox.showinfo("Success", f"Chain '{chain_name}' saved successfully.")
            self.load_chains()
            self.edit_chain_window.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save chain: {e}")

    def _on_link_selection(self, event):
        """Populate shell and script fields when a link is selected."""
        try:
            selected_index = self.link_listbox.curselection()[0]
            selected_link = self.chain_links[selected_index]
            self.selected_script.set(selected_link[1])
            self.selected_shell_alias.set(self.get_display_string(selected_link[0]))
            self.selected_script_alias.set(self.get_display_string(selected_link[1]))

            # Enable the delete and overwrite button if a selection is made
            self.add_link_button.config(state="normal")
            self.delete_link_button.config(state="normal")
            self.overwrite_selected_link_button.config(state="normal")
        except IndexError:
            pass

    def _on_deselect_link(self):
        """Deselect the currently selected link."""
        self.link_listbox.selection_clear(0, tk.END)
        self.delete_link_button.config(state="disabled")
        self.overwrite_selected_link_button.config(state="disabled")
    
    def _handle_outside_click(self, event):
        """Handle clicks outside of specific widgets to deselect the link."""
        widget = event.widget
        if isinstance(widget, tk.Listbox):
            if listbox_clicked_dead_space(event):
                self._on_deselect_link()
            else:
                self._on_link_selection(event)
        if widget != self.link_listbox and widget != self.chain_name_entry and widget != self.shell_dropdown and widget != self.select_script_button and widget != self.add_link_button and widget != self.delete_link_button and widget != self.overwrite_selected_link_button:
            self._on_deselect_link()
    
    def get_display_string(self, path):
        if self.file_display_setting == "Full path":
            return path
        elif self.file_display_setting == "File name only":
            return os.path.basename(path)
    
    def get_display_strings(self, paths):
        
        if self.file_display_setting == "Full path":
            output = paths
            return output
        elif self.file_display_setting == "File name only":
            output = []
            for i in range(0, len(paths)):
                output.append(os.path.basename(paths[i]))
            return output
