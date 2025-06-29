import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Dict, Optional, Callable
from functions.subtitle_track_selector import get_subtitle_tracks

class SubtitleTrackSelector:
    """UI component for selecting subtitle tracks from video files."""
    
    def __init__(self, parent, on_selection_change: Optional[Callable] = None):
        self.parent = parent
        self.on_selection_change = on_selection_change
        self.current_tracks = []
        self.selected_track_index = 0
        
        # Create UI elements
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the subtitle track selection UI."""
        # Frame for subtitle track selection
        self.track_frame = ttk.Frame(self.parent)
        
        # Label
        self.track_label = ttk.Label(
            self.track_frame, 
            text="Subtitle Track:"
        )
        self.track_label.pack(side=tk.LEFT, padx=(0, 5))
        
        # Combobox for track selection
        self.track_combobox = ttk.Combobox(
            self.track_frame,
            state="readonly",
            width=40
        )
        self.track_combobox.pack(side=tk.LEFT, padx=(0, 5))
        self.track_combobox.bind("<<ComboboxSelected>>", self._on_track_selected)
        
        # Refresh button
        self.refresh_button = ttk.Button(
            self.track_frame,
            text="↻",
            width=3,
            command=self.refresh_tracks
        )
        self.refresh_button.pack(side=tk.LEFT)
        
        # Initially hide the frame
        self.hide()
        
    def show(self):
        """Show the subtitle track selector."""
        self.track_frame.pack(fill=tk.X, pady=(5, 0))
        
    def hide(self):
        """Hide the subtitle track selector."""
        self.track_frame.pack_forget()
        
    def update_video_file(self, video_path: str):
        """
        Update the available subtitle tracks based on the video file.
        
        Args:
            video_path (str): Path to the video file
        """
        if not video_path or not video_path.strip():
            self.hide()
            return
            
        # Get subtitle tracks from the video
        self.current_tracks = get_subtitle_tracks(video_path)
        
        if not self.current_tracks:
            self.hide()
            return
            
        # Update combobox with track options
        track_options = [track["display_name"] for track in self.current_tracks]
        self.track_combobox['values'] = track_options
        
        # Select first track by default
        if track_options:
            self.track_combobox.current(0)
            self.selected_track_index = 0
            
        # Show the selector if there are multiple tracks
        if len(self.current_tracks) > 1:
            self.show()
        else:
            self.hide()
            
        # Notify about selection change
        if self.on_selection_change:
            self.on_selection_change(self.get_selected_track())
            
    def refresh_tracks(self):
        """Refresh the subtitle tracks for the current video."""
        # This would typically be called when the video file changes
        # For now, we'll just update the display
        if hasattr(self.parent, 'current_video_path'):
            self.update_video_file(self.parent.current_video_path)
            
    def get_selected_track(self) -> Optional[Dict]:
        """
        Get the currently selected subtitle track.
        
        Returns:
            Optional[Dict]: Selected track information, or None if no selection
        """
        if not self.current_tracks:
            return None
            
        try:
            return self.current_tracks[self.selected_track_index]
        except IndexError:
            return None
            
    def get_selected_track_index(self) -> int:
        """
        Get the index of the currently selected subtitle track.
        
        Returns:
            int: Index of the selected track
        """
        return self.selected_track_index
        
    def _on_track_selected(self, event=None):
        """Handle track selection change."""
        selection = self.track_combobox.current()
        if selection >= 0:
            self.selected_track_index = selection
            
            # Notify about selection change
            if self.on_selection_change:
                self.on_selection_change(self.get_selected_track())

class SubtitleTrackDialog:
    """Dialog for selecting subtitle tracks when multiple are available."""
    
    def __init__(self, parent, tracks: List[Dict], title: str = "Select Subtitle Track"):
        self.parent = parent
        self.tracks = tracks
        self.selected_index = 0
        self.result = None
        
        # Create dialog
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("500x300")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.geometry("+%d+%d" % (
            parent.winfo_rootx() + 50,
            parent.winfo_rooty() + 50
        ))
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the dialog UI."""
        # Main frame
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title label
        title_label = ttk.Label(
            main_frame,
            text="Multiple subtitle tracks found. Please select one:",
            font=("TkDefaultFont", 10, "bold")
        )
        title_label.pack(pady=(0, 10))
        
        # Listbox for track selection
        listbox_frame = ttk.Frame(main_frame)
        listbox_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(listbox_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Listbox
        self.listbox = tk.Listbox(
            listbox_frame,
            yscrollcommand=scrollbar.set,
            selectmode=tk.SINGLE
        )
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.listbox.yview)
        
        # Populate listbox
        for track in self.tracks:
            self.listbox.insert(tk.END, track["display_name"])
            
        # Select first item by default
        if self.tracks:
            self.listbox.selection_set(0)
            
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        # Buttons
        ttk.Button(
            button_frame,
            text="Cancel",
            command=self.cancel
        ).pack(side=tk.RIGHT, padx=(5, 0))
        
        ttk.Button(
            button_frame,
            text="OK",
            command=self.ok
        ).pack(side=tk.RIGHT)
        
        # Bind double-click
        self.listbox.bind("<Double-Button-1>", lambda e: self.ok())
        
        # Bind Enter key
        self.dialog.bind("<Return>", lambda e: self.ok())
        self.dialog.bind("<Escape>", lambda e: self.cancel())
        
    def ok(self):
        """Handle OK button click."""
        selection = self.listbox.curselection()
        if selection:
            self.selected_index = selection[0]
            self.result = self.tracks[self.selected_index]
        else:
            self.result = self.tracks[0] if self.tracks else None
            
        self.dialog.destroy()
        
    def cancel(self):
        """Handle Cancel button click."""
        self.result = None
        self.dialog.destroy()
        
    def show(self) -> Optional[Dict]:
        """
        Show the dialog and return the selected track.
        
        Returns:
            Optional[Dict]: Selected track information, or None if cancelled
        """
        self.dialog.wait_window()
        return self.result

def show_track_selection_dialog(parent, tracks: List[Dict]) -> Optional[Dict]:
    """
    Show a dialog for selecting subtitle tracks.
    
    Args:
        parent: Parent window
        tracks (List[Dict]): List of available subtitle tracks
        
    Returns:
        Optional[Dict]: Selected track information, or None if cancelled
    """
    if not tracks:
        return None
        
    if len(tracks) == 1:
        return tracks[0]
        
    dialog = SubtitleTrackDialog(parent, tracks)
    return dialog.show()