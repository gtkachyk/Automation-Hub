import tkinter as tk
from tkinter import Menu, messagebox, ttk
import csv
import os
import subprocess
import threading
from settings_window import SettingsWindow
from shells_window import ShellsWindow
from edit_chain_window import EditChainWindow
from utils import listbox_clicked_dead_space

# Constants
SETTINGS_DIR = "Settings"
FILE_DISPLAY_FILE = SETTINGS_DIR + "/file_display.csv"
SHELLS_FILE = "Shells/shells.csv"
CHAINS_DIR = "Chains"
LISTBOX_ITEM_HEIGHT = 16

# Ensure directories and files exist
os.makedirs("Shells", exist_ok=True)
os.makedirs(CHAINS_DIR, exist_ok=True)
if not os.path.exists(SHELLS_FILE):
    with open(SHELLS_FILE, "w") as f:
        pass

def open_settings_window():
    SettingsWindow(root, FILE_DISPLAY_FILE)

def open_shells_window():
    ShellsWindow(root, SHELLS_FILE, FILE_DISPLAY_FILE, CHAINS_DIR)

def open_edit_chain_window(chain_name=None):
    EditChainWindow(
        root=root,
        chain_listbox=chain_listbox,
        load_chains=load_chains,
        chains_dir=CHAINS_DIR,
        shells_file=SHELLS_FILE,
        file_display_file=FILE_DISPLAY_FILE,
        chain_name=chain_name
    )

def quit_program():
    """Exit the program gracefully."""
    if messagebox.askokcancel("Quit", "Do you really want to quit?"):
        root.destroy()

def load_chains():
    """Load execution chains from the Chains directory."""
    edit_button.config(state="disabled")
    delete_button.config(state="disabled")
    execute_button.config(state="disabled")
    chain_listbox.delete(0, tk.END)
    for filename in os.listdir(CHAINS_DIR):
        if filename.endswith(".csv"):
            chain_listbox.insert(tk.END, os.path.splitext(filename)[0])

def delete_selected_chains():
    """Delete selected execution chains."""
    selected_indices = chain_listbox.curselection()
    if not selected_indices:
        messagebox.showwarning("Warning", "No chains selected to delete.")
        return

    if not messagebox.askyesno("Confirm Delete", "Are you sure you want to delete the selected chains?"):
        return
    main_window_deselect_link()

    for i in selected_indices[::-1]:
        chain_name = chain_listbox.get(i)
        chain_file = os.path.join(CHAINS_DIR, f"{chain_name}.csv")
        try:
            os.remove(chain_file)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete {chain_name}: {e}")
    load_chains()

def execute_chain():
    """Execute the selected execution chain."""
    selected_indices = chain_listbox.curselection()
    if not selected_indices:
        messagebox.showwarning("Warning", "No chain selected to execute.")
        return

    chain_name = chain_listbox.get(selected_indices[0])
    chain_file = os.path.join(CHAINS_DIR, f"{chain_name}.csv")

    try:
        # Load chain links
        with open(chain_file, "r") as f:
            reader = csv.reader(f)
            chain_links = list(reader)

        if not chain_links:
            messagebox.showwarning("Warning", f"Chain '{chain_name}' has no links to execute.")
            return

        # Execute each link
        for shell, script in chain_links:
            if not os.path.exists(script):
                messagebox.showerror("Error", f"Script not found: {script}")
                return

            # Ensure the script runs in its directory
            script_dir = os.path.dirname(script)
            command = [shell, script]

            try:
                # Launch process in a detached mode
                subprocess.Popen(
                    command,
                    cwd=script_dir,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    stdin=subprocess.DEVNULL,
                    start_new_session=True,
                )
            except Exception as e:
                messagebox.showerror("Error", f"Error executing '{script}': {e}")
                return

        messagebox.showinfo("Success", f"Chain '{chain_name}' executed successfully.")

    except Exception as e:
        messagebox.showerror("Error", f"Failed to execute chain '{chain_name}': {e}")

def main_window_on_link_select(event):
    """Handel chain_listbox item selection."""
    # Enable buttons if a selection is made
    edit_button.config(state="normal")
    delete_button.config(state="normal")
    execute_button.config(state="normal")

def main_window_deselect_link():
    """Deselect the currently selected chain."""
    chain_listbox.selection_clear(0, tk.END)
    edit_button.config(state="disabled")
    delete_button.config(state="disabled")
    execute_button.config(state="disabled")

def main_window_handle_outside_click(event):
    """Handle clicks outside of specific widgets to deselect the chain."""
    widget = event.widget
    if isinstance(widget, tk.Listbox):
        if listbox_clicked_dead_space(event):
            main_window_deselect_link()
        else:
            main_window_on_link_select(event)
    if widget != chain_listbox and widget != edit_button and widget != delete_button and widget != execute_button:
        main_window_deselect_link()

# Main application window
root = tk.Tk()
root.iconbitmap(default="Resources/icon_window.ico")
root.title("Automation-Hub")
root.geometry("600x400")
root.resizable(False, False)
root.bind("<Button-1>", main_window_handle_outside_click)

# Create the menu bar
menu_bar = Menu(root)
root.config(menu=menu_bar)

# File menu
file_menu = Menu(menu_bar, tearoff=0)
file_menu.add_command(label="Settings", command=open_settings_window)
file_menu.add_separator()
file_menu.add_command(label="Shells", command=open_shells_window)
file_menu.add_separator()
file_menu.add_command(label="Quit", command=quit_program)
menu_bar.add_cascade(label="File", menu=file_menu)

# Main window components
frame = tk.Frame(root)
frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

# Main listbox label
ttk.Label(frame, text="Execution Chains", width=15).pack(side=tk.TOP)

# Listbox for displaying execution chains
chain_listbox = tk.Listbox(frame, activestyle=tk.NONE, exportselection=False)
chain_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Scrollbar for the listbox
scrollbar = tk.Scrollbar(frame, orient=tk.VERTICAL, command=chain_listbox.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
chain_listbox.config(yscrollcommand=scrollbar.set)

# Button panel
button_frame = tk.Frame(root)
button_frame.pack(pady=10)
add_button = tk.Button(button_frame, text="Add", command=lambda: open_edit_chain_window())
add_button.pack(side=tk.LEFT, padx=5)
edit_button = tk.Button(button_frame, text="Edit", command=lambda: open_edit_chain_window(chain_listbox.get(chain_listbox.curselection()[0])) if chain_listbox.curselection() else None, state=tk.DISABLED)
edit_button.pack(side=tk.LEFT, padx=5)
delete_button = tk.Button(button_frame, text="Delete", command=delete_selected_chains, state=tk.DISABLED)
delete_button.pack(side=tk.LEFT, padx=5)
execute_button = tk.Button(button_frame, text="Execute", command=execute_chain, state=tk.DISABLED)
execute_button.pack(side=tk.LEFT, padx=5)

# Display chains
load_chains()

# Initially disable Edit, Delete, and Execute buttons
edit_button.config(state=tk.DISABLED)
delete_button.config(state=tk.DISABLED)
execute_button.config(state=tk.DISABLED)

# Run the application
root.mainloop()