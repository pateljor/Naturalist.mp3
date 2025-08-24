#!/usr/bin/env python3
import re

def load_and_clean_tracklist(tracklist_file):
    """Load tracklist from a text file"""
    try:
        with open(tracklist_file, 'r') as f:
            lines = f.readlines()
        
        # Skip header lines and extract timestamps
        timestamps = []
        for line in lines:
            line = line.strip()
            if ':' in line and '-' in line:
                # Format: "00:00 - 01. Song Title"
                parts = line.split(' - ', 1)
                if len(parts) == 2:
                    timestamp = parts[0].strip()
                    title = parts[1].strip()
                    timestamps.append(f"{timestamp} {title}")
        
        timestamps_cleaned = [re.sub(r"\s\d{8}.*", "", timestamp) for timestamp in timestamps]
        timestamps_str = "\n".join(timestamps_cleaned)
        
        return timestamps_str
    except FileNotFoundError:
        print(f"❌ Tracklist file not found: {tracklist_file}")
        return []

def generate_description(description, tracklist_file, hashtags):
    """
    Generate a complete video description
    
    Args:
        playlist_title: Title of the playlist to match
        tracklist_file: Path to tracklist file (optional, will try to find automatically)
        custom_description: Custom description to use instead of JSON data
    
    Returns:
        Complete description string
    """

    # Load timestamps if tracklist file exists
    timestamps_desc = load_and_clean_tracklist(tracklist_file)
    
    # Build final description
    final_description = f"""{description}

    
{timestamps_desc}
    
    
    
All music featured on this channel is produced by Naturalist.mp3.
Images are sourced from Unsplash and edited by Naturalist.mp3 before use.
    
    
    
    
    
    
    
    
    
    
{hashtags}
    """
    
    return final_description
