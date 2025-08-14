#!/usr/bin/env python3
"""
Script to rename songs in the 'songs' folder using song names from lofi_playlist_data.json
"""

import os
import json
import glob

def rename_songs(song_names):
    """Rename all MP3 files in songs folder using the song names"""
    # Get the song names from JSON
    
    if not song_names:
        print("Could not find song names for 'Rest under a tree and feel protected by nature' playlist")
        return
    
    # Get all MP3 files in songs folder
    songs_folder = 'songs'
    mp3_files = sorted(glob.glob(os.path.join(songs_folder, '*.mp3')))
    
    print(f"Found {len(mp3_files)} MP3 files")
    print(f"Found {len(song_names)} song names")
    
    if len(mp3_files) != len(song_names):
        print(f"Warning: Number of files ({len(mp3_files)}) doesn't match number of song names ({len(song_names)})")
        print("Using minimum of both lengths...")
    
    # Rename files
    min_count = min(len(mp3_files), len(song_names))
    
    for i in range(min_count):
        old_file = mp3_files[i]
        old_filename = os.path.basename(old_file)
        
        # Create new filename with proper extension
        new_filename = f"{song_names[i]}.mp3"
        new_file = os.path.join(songs_folder, new_filename)
        
        # Check if target already exists
        if os.path.exists(new_file):
            print(f"Skipping {old_filename} -> {new_filename} (target exists)")
            continue
        
        # Rename the file
        try:
            os.rename(old_file, new_file)
            print(f"Renamed: {old_filename} -> {new_filename}")
        except Exception as e:
            print(f"Error renaming {old_filename}: {e}")
