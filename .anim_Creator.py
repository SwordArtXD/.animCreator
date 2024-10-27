import os, sys
import json  # Now using JSON for settings
import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, Menu
from animExport import export_single_animation, export_all_animations
from FBX_import import load_fbx_animations  # Import the actual FBX handler

# Path for the settings.json file
settings_file = "settings.json"

# Define color themes (including additional ones)
color_themes = {
    "blue": {
        "CTkFrame": {"fg_color": "#333333"},
        "CTkLabel": {"text_color": "#FFFFFF"},
        "CTkButton": {"fg_color": "#007BFF", "text_color": "#FFFFFF"}
    },
    "orange": {
        "CTkFrame": {"fg_color": "#333333", "border_color": "#FFA500"},
        "CTkLabel": {"fg_color": "#000000", "text_color": "#FFA500"},
        "CTkButton": {"fg_color": "#FFA500", "text_color": "#000000"}
    },
    "pink": {
        "CTkFrame": {"fg_color": "#333333"},
        "CTkLabel": {"text_color": "#FF69B4"},
        "CTkButton": {"fg_color": "#FF69B4", "text_color": "#000000"}
    },
    "red": {
        "CTkFrame": {"fg_color": "#333333"},
        "CTkLabel": {"text_color": "#FF6347"},
        "CTkButton": {"fg_color": "#FF0000", "text_color": "#000000"}
    },
    "yellow": {
        "CTkFrame": {"fg_color": "#333333"},
        "CTkLabel": {"text_color": "#FFD700"},
        "CTkButton": {"fg_color": "#FFD700", "text_color": "#000000"}
    },
    "purple": {
        "CTkFrame": {"fg_color": "#333333"},
        "CTkLabel": {"text_color": "#DA70D6"},
        "CTkButton": {"fg_color": "#6F2DA8", "text_color": "#FFFFFF"}
    }
}

class FBXToAnimConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title(".anim Creator")

        # Set the custom icon for the application window
        self.root.iconbitmap("icon.ico")  # Ensure icon.ico is in the same directory as this script

        # Padding values for the main frame
        self.main_frame_padding = {'padx': 20, 'pady': 20}  # Define padding here

        # Set window size and allow maximization
        self.root.geometry("540x630")
        self.root.resizable(True, False)

        # Set the theme for customtkinter
        ctk.set_appearance_mode("dark")  # Dark mode
        
        # Load settings from the JSON file
        self.settings = self.load_settings()

        # Apply the saved window position
        window_position = self.settings.get("window_position", "100x100")
        self.root.geometry(f"540x630+{window_position.split('x')[0]}+{window_position.split('x')[1]}")

        # Initialize theme-related variables before applying any theme
        self.blue_theme_var = tk.IntVar(value=1 if self.settings.get("theme") == "blue" else 0)
        self.orange_theme_var = tk.IntVar(value=1 if self.settings.get("theme") == "orange" else 0)
        self.pink_theme_var = tk.IntVar(value=1 if self.settings.get("theme") == "pink" else 0)
        self.red_theme_var = tk.IntVar(value=1 if self.settings.get("theme") == "red" else 0)
        self.yellow_theme_var = tk.IntVar(value=1 if self.settings.get("theme") == "yellow" else 0)
        self.purple_theme_var = tk.IntVar(value=1 if self.settings.get("theme") == "purple" else 0)

        # Build UI components
        self.build_ui()

        # Apply the saved theme after building the UI
        self.apply_saved_theme()

    def build_ui(self):
        """Build the user interface for the application."""
        # Create main frame
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.pack(fill="both", expand=True, **self.main_frame_padding)

        # Settings button (toggle behavior)
        self.settings_button = self.create_button(
            root=self.main_frame,
            text="Settings",
            command=self.toggle_settings,
            anchor="nw",
            padx=10,
            pady=10
        )

        # Label for showing the FBX file name at the top
        self.fbx_label = ctk.CTkLabel(self.main_frame, text="Select an FBX file to begin", font=("Arial", 14))
        self.fbx_label.pack(pady=10)

        # File selection button
        self.select_fbx_button = ctk.CTkButton(
            self.main_frame,
            text="Select FBX File",
            command=self.select_fbx_file,
            width=25
        )
        self.select_fbx_button.pack(pady=10)

        # Rounded Listbox frame with left padding
        self.listbox_frame = ctk.CTkFrame(self.main_frame, fg_color="#2E2E2E", corner_radius=15)
        self.listbox_frame.pack(pady=10, padx=(5, 5), fill="both", expand=True)  # Increased left padding to 50px for testing


        # Inside the build_ui method

        self.anim_listbox = tk.Listbox(
            self.listbox_frame,
            height=10,
            bg='#2E2E2E',  # Background color of the listbox
            fg='white',  # Text color
            highlightbackground='#2E2E2E',  # Same as background to hide the border
            selectbackground='#4A90E2',  # Color for selected background (blue in this case)
            selectforeground='white',  # Text color for selected items
            highlightthickness=0,  # Removes the border thickness
            relief="flat",  # Removes any 3D effect
            selectmode="single",
            borderwidth=0,  # Removes the border
            font=("Calibri", 14)  # Larger font size
        )

        # Remove any underline (set in the select style)
        self.anim_listbox.configure(activestyle="none")  # This disables the underline effect

        self.anim_listbox.pack(pady=5, padx=(25,5), fill="both", expand=True)
        self.anim_listbox.bind('<Button-3>', self.show_context_menu)

        # Right-click context menu for rename, delete, and export
        self.context_menu = Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Export", command=self.export_single_animation)
        self.context_menu.add_command(label="Rename", command=self.rename_animation)
        self.context_menu.add_command(label="Delete", command=self.delete_animation)

        # Custom Export Directory selection
        self.export_dir_frame = ctk.CTkFrame(self.main_frame)
        self.export_dir_frame.pack(pady=10)

        # Save the browse button as an instance variable
        self.export_dir_entry = ctk.CTkEntry(self.export_dir_frame, width=300)
        self.export_dir_entry.pack(side="left", padx=(0, 5))

        # Store browse button as an instance variable for color updates
        self.browse_button = ctk.CTkButton(self.export_dir_frame, text="Browse", command=self.select_export_directory)
        self.browse_button.pack(side="left", padx=(5, 0))

        # Export all button
        self.export_all_button = ctk.CTkButton(self.main_frame, text="Export All Animations", command=self.export_all_animations_handler, width=25, state="disabled")
        self.export_all_button.pack(pady=10)

        # Status label
        self.status_label = ctk.CTkLabel(self.main_frame, text="", text_color="green", wraplength=500, anchor="center", justify="center")
        self.status_label.pack(pady=10, fill="both")

        # Hidden settings frame
        self.build_settings_frame()

    def build_settings_frame(self):
        """Build the settings frame UI."""
        self.settings_frame = ctk.CTkFrame(self.root)
        self.settings_frame.pack_forget()

        # Back Button
        self.back_button = ctk.CTkButton(self.settings_frame, text="Back", command=self.toggle_settings)
        self.back_button.pack(anchor="nw", padx=10, pady=10)

        # Settings frame content
        ctk.CTkLabel(self.settings_frame, text="Default Export Directory:").pack(pady=10)
        self.settings_export_dir_entry = ctk.CTkEntry(self.settings_frame, width=300)
        self.settings_export_dir_entry.pack(pady=10)
        if self.settings.get("default_export_dir"):
            self.settings_export_dir_entry.insert(0, self.settings["default_export_dir"])

        # Store browse button in settings as instance variable for color updates
        self.browse_button_settings = ctk.CTkButton(self.settings_frame, text="Browse", command=self.select_default_export_directory)
        self.browse_button_settings.pack(pady=10)

        # Color theme options with new themes (Pink, Red, Yellow, Purple)
        ctk.CTkLabel(self.settings_frame, text="Color Themes:").pack(pady=10)
        ctk.CTkCheckBox(self.settings_frame, text="Blue (Default)", variable=self.blue_theme_var, command=self.apply_blue_theme).pack(anchor="w", padx=10)
        ctk.CTkCheckBox(self.settings_frame, text="Orange", variable=self.orange_theme_var, command=self.apply_orange_theme).pack(anchor="w", padx=10)
        ctk.CTkCheckBox(self.settings_frame, text="Pink", variable=self.pink_theme_var, command=self.apply_pink_theme).pack(anchor="w", padx=10)
        ctk.CTkCheckBox(self.settings_frame, text="Red", variable=self.red_theme_var, command=self.apply_red_theme).pack(anchor="w", padx=10)
        ctk.CTkCheckBox(self.settings_frame, text="Yellow", variable=self.yellow_theme_var, command=self.apply_yellow_theme).pack(anchor="w", padx=10)
        ctk.CTkCheckBox(self.settings_frame, text="Purple", variable=self.purple_theme_var, command=self.apply_purple_theme).pack(anchor="w", padx=10)

        # Store Save button as an instance variable for color updates
        self.save_button = ctk.CTkButton(self.settings_frame, text="Save", command=self.save_export_directory)
        self.save_button.pack(pady=20)

    def create_button(self, root, text, command, anchor, padx, pady):
        button = ctk.CTkButton(root, text=text, command=command)
        button.pack(anchor=anchor, padx=padx, pady=pady)
        return button

    def toggle_settings(self):
        """Toggles between the main window and the settings window"""
        if self.main_frame.winfo_ismapped():  # If main frame is visible
            self.main_frame.pack_forget()  # Hide main frame
            self.settings_frame.pack(fill="both", expand=True, padx=20, pady=20)  # Apply padding when showing
        else:
            self.settings_frame.pack_forget()  # Hide settings frame
            self.main_frame.pack(fill="both", expand=True, **self.main_frame_padding)  # Show main frame with padding

    def reset_theme_vars(self, active_var):
        """Reset all theme variables except the active one"""
        self.blue_theme_var.set(0)
        self.orange_theme_var.set(0)
        self.pink_theme_var.set(0)
        self.red_theme_var.set(0)
        self.yellow_theme_var.set(0)
        self.purple_theme_var.set(0)
        active_var.set(1)  # Set the active theme


    def apply_blue_theme(self):
        self.reset_theme_vars(self.blue_theme_var)
        self.update_ui_colors("blue")
        self.settings["theme"] = "blue"
        self.save_settings()

    def apply_orange_theme(self):
        self.reset_theme_vars(self.orange_theme_var)
        self.update_ui_colors("orange")
        self.settings["theme"] = "orange"
        self.save_settings()

    def apply_pink_theme(self):
        self.reset_theme_vars(self.pink_theme_var)
        self.update_ui_colors("pink")
        self.settings["theme"] = "pink"
        self.save_settings()

    def apply_red_theme(self):
        self.reset_theme_vars(self.red_theme_var)
        self.update_ui_colors("red")
        self.settings["theme"] = "red"
        self.save_settings()

    def apply_yellow_theme(self):
        self.reset_theme_vars(self.yellow_theme_var)
        self.update_ui_colors("yellow")
        self.settings["theme"] = "yellow"
        self.save_settings()

    def apply_purple_theme(self):
        self.reset_theme_vars(self.purple_theme_var)
        self.update_ui_colors("purple")
        self.settings["theme"] = "purple"
        self.save_settings()

    def update_ui_colors(self, theme_name):
        """Updates the colors of the UI elements based on the selected theme."""
        theme = color_themes.get(theme_name, color_themes["blue"])  # Default to blue if theme not found

        # Apply the theme colors to all relevant widgets in both frames (main and settings)
        self.main_frame.configure(fg_color=theme["CTkFrame"]["fg_color"])
        self.settings_frame.configure(fg_color=theme["CTkFrame"]["fg_color"])

        # Main frame widgets
        self.fbx_label.configure(text_color=theme["CTkLabel"]["text_color"])
        self.select_fbx_button.configure(fg_color=theme["CTkButton"]["fg_color"], text_color=theme["CTkButton"]["text_color"])
        self.export_all_button.configure(fg_color=theme["CTkButton"]["fg_color"], text_color=theme["CTkButton"]["text_color"])
        self.export_dir_entry.configure(fg_color=theme["CTkFrame"]["fg_color"])
        self.status_label.configure(text_color=theme["CTkLabel"]["text_color"])
        self.settings_button.configure(fg_color=theme["CTkButton"]["fg_color"], text_color=theme["CTkButton"]["text_color"])
        self.browse_button.configure(fg_color=theme["CTkButton"]["fg_color"], text_color=theme["CTkButton"]["text_color"])

        # Settings frame widgets
        self.settings_export_dir_entry.configure(fg_color=theme["CTkFrame"]["fg_color"])
        self.back_button.configure(fg_color=theme["CTkButton"]["fg_color"], text_color=theme["CTkButton"]["text_color"])
        self.browse_button_settings.configure(fg_color=theme["CTkButton"]["fg_color"], text_color=theme["CTkButton"]["text_color"])
        self.save_button.configure(fg_color=theme["CTkButton"]["fg_color"], text_color=theme["CTkButton"]["text_color"])

        # Ensure immediate changes take effect by updating all widgets
        self.root.update()

    def select_fbx_file(self):
        self.fbx_file = filedialog.askopenfilename(title="Select FBX File", filetypes=[("FBX files", "*.fbx")])
        if self.fbx_file:
            self.anim_listbox.delete(0, tk.END)  # Clear the listbox first
            self.animations_with_originals, self.scene = load_fbx_animations(self.fbx_file)
            self.animations = [cleaned_name for _, cleaned_name in self.animations_with_originals]
            
            for anim in self.animations:
                self.anim_listbox.insert(tk.END, anim)
            
            self.fbx_label.configure(text=f"{self.fbx_file.split('/')[-1]}")
            self.export_all_button.configure(state="normal")

    def show_context_menu(self, event):
        try:
            self.selected_animation_index = self.anim_listbox.nearest(event.y)
            self.anim_listbox.selection_clear(0, tk.END)
            self.anim_listbox.selection_set(self.selected_animation_index)
            self.context_menu.post(event.x_root, event.y_root)
        except IndexError:
            pass

    def rename_animation(self):
        index = self.selected_animation_index
        original_name = self.anim_listbox.get(index)

        # Create the rename window
        rename_window = ctk.CTkToplevel(self.root)
        rename_window.title("Rename Animation")
        rename_window.geometry("360x180")

        # Set the icon for the rename window
        rename_window.iconbitmap("icon.ico")  # Set the icon here

        # Center the rename window
        self.root.update_idletasks()  # Update root dimensions
        window_width = 360
        window_height = 180
        screen_width = self.root.winfo_width()
        screen_height = self.root.winfo_height()
        x = self.root.winfo_x() + (screen_width // 2) - (window_width // 2)
        y = self.root.winfo_y() + (screen_height // 2) - (window_height // 2)
        rename_window.geometry(f"{window_width}x{window_height}+{x}+{y}")

        # Make the rename window modal and lock the main window
        rename_window.grab_set()
        rename_window.transient(self.root)  # Set the rename window as a child of the main window

        # Disable the main window from being moved or interacted with
        self.root.attributes("-disabled", True)

        # Handle window close to re-enable the main window
        def on_close():
            self.root.attributes("-disabled", False)
            rename_window.grab_release()
            rename_window.destroy()
            # Unbind the flash event after closing the rename window
            self.root.unbind("<FocusIn>")

        rename_window.protocol("WM_DELETE_WINDOW", on_close)

        entry_box = ctk.CTkEntry(rename_window, width=300)
        entry_box.insert(0, original_name)
        entry_box.pack(pady=20)

        def commit_rename():
            new_name = entry_box.get()
            if new_name:
                self.anim_listbox.delete(index)
                self.anim_listbox.insert(index, new_name)
                self.animations[index] = new_name
                self.animations_with_originals[index] = (self.animations_with_originals[index][0], new_name)
                self.status_label.configure(text=f"Animation renamed to: {new_name}")
                on_close()

        rename_button = ctk.CTkButton(rename_window, text="Rename", command=commit_rename)
        rename_button.pack(pady=10)

        # Flash main window and play sound only when interaction is attempted with the main window while rename window is active
        def flash_main_window(event=None):
            if rename_window.winfo_exists():  # Ensure the rename window is still open
                self.root.bell()  # Play a system warning sound
                self.root.after(100, lambda: self.root.configure(bg="red"))  # Flash red for a brief moment
                self.root.after(300, lambda: self.root.configure(bg=""))  # Reset back to normal

        # Defer binding the focus event until after the rename window is fully opened
        def bind_focus_event():
            self.root.bind("<FocusIn>", flash_main_window)

        # Set a small delay before binding the event to ensure the rename window is fully initialized
        rename_window.after(100, bind_focus_event)

    def delete_animation(self):
        index = self.selected_animation_index
        del self.animations[index]
        del self.animations_with_originals[index]
        self.anim_listbox.delete(index)
        self.status_label.configure(text="Animation deleted.")

    def export_single_animation(self):
        selected_index = self.anim_listbox.curselection()
        if selected_index:
            selected_animation = self.anim_listbox.get(selected_index)
            save_path = filedialog.asksaveasfilename(defaultextension=".anim", filetypes=[("Anim files", "*.anim")], initialfile=f"{selected_animation}.anim")
            if save_path:
                export_single_animation(selected_animation, save_path, self.scene)
                self.status_label.configure(text=f"Exported {selected_animation} to {save_path}", text_color="green")
            else:
                self.status_label.configure(text="Export canceled.", text_color="red")
        else:
            self.status_label.configure(text="No animation selected.", text_color="red")

    def export_all_animations_handler(self):
        if not self.fbx_file:
            self.status_label.configure(text="Error: No FBX file loaded!", text_color="red")
            return
        export_dir = self.export_dir or self.settings.get("default_export_dir")
        if not export_dir:
            self.status_label.configure(text="Error: Please select an export directory!", text_color="red")
            return
        export_all_animations([anim_cleaned for _, anim_cleaned in self.animations_with_originals], export_dir, self.scene)
        self.status_label.configure(text="All animations exported successfully!", text_color="green")

    def select_export_directory(self):
        self.export_dir = filedialog.askdirectory(title="Select Custom Export Directory")
        if self.export_dir:
            self.export_dir_entry.delete(0, tk.END)
            self.export_dir_entry.insert(0, self.export_dir)
            self.status_label.configure(text=f"Custom export directory set to: {self.export_dir}")

    def select_default_export_directory(self):
        self.settings["default_export_dir"] = filedialog.askdirectory(title="Select Default Export Directory")
        if self.settings["default_export_dir"]:
            self.settings_export_dir_entry.delete(0, tk.END)
            self.settings_export_dir_entry.insert(0, self.settings["default_export_dir"])
            self.status_label.configure(text=f"Default export directory set to: {self.settings['default_export_dir']}")

    def save_export_directory(self):
        self.settings["default_export_dir"] = self.settings_export_dir_entry.get()
        self.status_label.configure(text=f"Default export folder saved: {self.settings['default_export_dir']}")
        self.save_settings()

    def load_settings(self):
        if os.path.exists(settings_file):
            with open(settings_file, 'r') as f:
                settings = json.load(f)
                # Set default values for missing fields
                settings.setdefault("window_position", "100x100")  # Default window position if not saved
                return settings
        else:
            # Default settings
            return {
                "default_export_dir": "",
                "theme": "blue",
                "window_position": "100x100"
            }

    def save_settings(self):
        self.settings["window_position"] = f"{self.root.winfo_x()}x{self.root.winfo_y()}"

        with open(settings_file, 'w') as f:
            json.dump(self.settings, f, indent=4)

    def apply_saved_theme(self):
        """Applies the theme saved in the JSON settings."""
        theme = self.settings.get("theme", "blue")  # Default to blue if no theme is saved
        if theme == "orange":
            self.apply_orange_theme()
        elif theme == "pink":
            self.apply_pink_theme()
        elif theme == "red":
            self.apply_red_theme()
        elif theme == "yellow":
            self.apply_yellow_theme()
        elif theme == "purple":
            self.apply_purple_theme()
        else:
            self.apply_blue_theme()

# Set up the main Tkinter window
root = ctk.CTk()

# Override the close button to ensure it properly closes the app
def on_closing():
    # Save window position before quitting
    app.save_settings()
    root.quit()  # Ends the mainloop properly, avoiding task killing issues


root.protocol("WM_DELETE_WINDOW", on_closing)

app = FBXToAnimConverterApp(root)
root.mainloop()
