import subprocess
import json
import os
from typing import List, Dict, Optional, Tuple

def get_subtitle_tracks(video_path: str) -> List[Dict]:
    """
    Extract subtitle track information from a video file using ffprobe.
    
    Args:
        video_path (str): Path to the video file
        
    Returns:
        List[Dict]: List of subtitle track information dictionaries
    """
    if not os.path.exists(video_path):
        return []
    
    try:
        # Get ffprobe path
        script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        ffprobe_path = os.path.join(script_dir, "resources", "ffmpeg-bin", "ffprobe")
        
        # Add .exe extension on Windows
        from functions.get_platform import platform
        if platform == "Windows":
            ffprobe_path += ".exe"
        
        if not os.path.exists(ffprobe_path):
            return []
        
        # Run ffprobe to get stream information
        cmd = [
            ffprobe_path,
            "-v", "quiet",
            "-print_format", "json",
            "-show_streams",
            "-select_streams", "s",  # Select only subtitle streams
            video_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode != 0:
            return []
        
        data = json.loads(result.stdout)
        streams = data.get("streams", [])
        
        subtitle_tracks = []
        for i, stream in enumerate(streams):
            if stream.get("codec_type") == "subtitle":
                track_info = {
                    "index": stream.get("index", i),
                    "codec_name": stream.get("codec_name", "unknown"),
                    "language": stream.get("tags", {}).get("language", "unknown"),
                    "title": stream.get("tags", {}).get("title", ""),
                    "display_name": f"Track {i + 1}"
                }
                
                # Create a more descriptive display name
                parts = [f"Track {i + 1}"]
                if track_info["language"] != "unknown":
                    parts.append(f"({track_info['language']})")
                if track_info["title"]:
                    parts.append(f"- {track_info['title']}")
                if track_info["codec_name"] != "unknown":
                    parts.append(f"[{track_info['codec_name']}]")
                
                track_info["display_name"] = " ".join(parts)
                subtitle_tracks.append(track_info)
        
        return subtitle_tracks
        
    except Exception as e:
        print(f"Error getting subtitle tracks: {e}")
        return []

def extract_subtitle_track(video_path: str, track_index: int, output_path: str, 
                          codec_name: str = "subrip") -> bool:
    """
    Extract a specific subtitle track from a video file.
    
    Args:
        video_path (str): Path to the video file
        track_index (int): Index of the subtitle track to extract
        output_path (str): Path where the extracted subtitle should be saved
        codec_name (str): Codec name for the subtitle format
        
    Returns:
        bool: True if extraction was successful, False otherwise
    """
    try:
        # Get ffmpeg path
        script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        ffmpeg_path = os.path.join(script_dir, "resources", "ffmpeg-bin", "ffmpeg")
        
        # Add .exe extension on Windows
        from functions.get_platform import platform
        if platform == "Windows":
            ffmpeg_path += ".exe"
        
        if not os.path.exists(ffmpeg_path):
            return False
        
        # Determine output format based on codec
        format_map = {
            "subrip": "srt",
            "ass": "ass", 
            "webvtt": "vtt",
            "mov_text": "srt"
        }
        
        output_format = format_map.get(codec_name, "srt")
        
        # Ensure output path has correct extension
        base_path = os.path.splitext(output_path)[0]
        output_path = f"{base_path}.{output_format}"
        
        # Build ffmpeg command
        cmd = [
            ffmpeg_path,
            "-i", video_path,
            "-map", f"0:s:{track_index}",  # Map specific subtitle stream
            "-c:s", "copy" if codec_name == "ass" else "srt",
            "-y",  # Overwrite output file
            output_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        return result.returncode == 0 and os.path.exists(output_path)
        
    except Exception as e:
        print(f"Error extracting subtitle track: {e}")
        return False

def get_best_subtitle_track(tracks: List[Dict], preferred_language: str = "en") -> Optional[int]:
    """
    Get the best subtitle track based on language preference and other criteria.
    
    Args:
        tracks (List[Dict]): List of subtitle track information
        preferred_language (str): Preferred language code
        
    Returns:
        Optional[int]: Index of the best track, or None if no tracks available
    """
    if not tracks:
        return None
    
    # First, try to find preferred language
    for i, track in enumerate(tracks):
        if track.get("language", "").lower() == preferred_language.lower():
            return i
    
    # If no preferred language found, return the first track
    return 0