from tkinter import messagebox
import tkinter as tk

LISTBOX_ITEM_HEIGHT = 16

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
