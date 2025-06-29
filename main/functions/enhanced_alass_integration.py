import os
import subprocess
import tempfile
from typing import Optional, Dict, List
from functions.subtitle_track_selector import (
    get_subtitle_tracks, 
    extract_subtitle_track, 
    get_best_subtitle_track
)
from functions.subtitle_track_ui import show_track_selection_dialog

def extract_best_subtitle_for_alass(video_path: str, parent_window=None, 
                                   selected_track: Optional[Dict] = None,
                                   auto_select: bool = False,
                                   preferred_language: str = "en") -> Optional[str]:
    """
    Extract the best subtitle track from a video file for alass synchronization.
    
    Args:
        video_path (str): Path to the video file
        parent_window: Parent window for dialogs
        selected_track (Optional[Dict]): Pre-selected track information
        auto_select (bool): Whether to auto-select the best track
        preferred_language (str): Preferred language for auto-selection
        
    Returns:
        Optional[str]: Path to the extracted subtitle file, or None if failed
    """
    if not os.path.exists(video_path):
        return None
        
    # Get available subtitle tracks
    tracks = get_subtitle_tracks(video_path)
    
    if not tracks:
        return None
        
    # Determine which track to use
    selected_track_info = None
    
    if selected_track:
        # Use pre-selected track
        selected_track_info = selected_track
    elif auto_select or len(tracks) == 1:
        # Auto-select the best track
        best_index = get_best_subtitle_track(tracks, preferred_language)
        if best_index is not None:
            selected_track_info = tracks[best_index]
    else:
        # Show selection dialog
        if parent_window:
            selected_track_info = show_track_selection_dialog(parent_window, tracks)
        else:
            # Default to first track if no parent window
            selected_track_info = tracks[0]
            
    if not selected_track_info:
        return None
        
    # Create temporary file for extracted subtitle
    temp_dir = tempfile.gettempdir()
    video_name = os.path.splitext(os.path.basename(video_path))[0]
    temp_subtitle_path = os.path.join(
        temp_dir, 
        f"{video_name}_extracted_track_{selected_track_info['index']}.srt"
    )
    
    # Extract the selected subtitle track
    success = extract_subtitle_track(
        video_path,
        selected_track_info['index'],
        temp_subtitle_path,
        selected_track_info.get('codec_name', 'subrip')
    )
    
    if success and os.path.exists(temp_subtitle_path):
        return temp_subtitle_path
    else:
        return None

def run_alass_with_subtitle_track(video_path: str, subtitle_path: str, output_path: str,
                                 additional_args: List[str] = None,
                                 selected_track: Optional[Dict] = None,
                                 parent_window=None,
                                 auto_select_track: bool = False,
                                 preferred_language: str = "en") -> subprocess.Popen:
    """
    Run alass with automatic subtitle track extraction from video.
    
    Args:
        video_path (str): Path to the video file
        subtitle_path (str): Path to the subtitle file to sync
        output_path (str): Path for the output synchronized subtitle
        additional_args (List[str]): Additional arguments for alass
        selected_track (Optional[Dict]): Pre-selected subtitle track
        parent_window: Parent window for dialogs
        auto_select_track (bool): Whether to auto-select the best track
        preferred_language (str): Preferred language for auto-selection
        
    Returns:
        subprocess.Popen: The alass process
    """
    # Extract reference subtitle from video
    reference_subtitle_path = extract_best_subtitle_for_alass(
        video_path,
        parent_window=parent_window,
        selected_track=selected_track,
        auto_select=auto_select_track,
        preferred_language=preferred_language
    )
    
    if not reference_subtitle_path:
        # Fall back to using video directly (original behavior)
        reference_file = video_path
    else:
        reference_file = reference_subtitle_path
    
    # Get alass executable path
    script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    alass_path = os.path.join(script_dir, "resources", "alass-bin", "alass-cli")
    
    # Add .exe extension on Windows
    from functions.get_platform import platform
    if platform == "Windows":
        alass_path += ".exe"
    
    # Build alass command
    cmd = [alass_path, reference_file, subtitle_path, output_path]
    
    # Add additional arguments if provided
    if additional_args:
        cmd.extend(additional_args)
    
    # Start the process
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        creationflags=subprocess.CREATE_NO_WINDOW if platform == "Windows" else 0
    )
    
    return process

def cleanup_extracted_subtitle(subtitle_path: str):
    """
    Clean up extracted subtitle file.
    
    Args:
        subtitle_path (str): Path to the extracted subtitle file
    """
    try:
        if subtitle_path and os.path.exists(subtitle_path):
            # Only delete if it's in temp directory and has our naming pattern
            if (tempfile.gettempdir() in subtitle_path and 
                "_extracted_track_" in os.path.basename(subtitle_path)):
                os.remove(subtitle_path)
    except Exception as e:
        print(f"Warning: Could not clean up extracted subtitle: {e}")