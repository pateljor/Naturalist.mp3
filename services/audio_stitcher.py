#!/usr/bin/env python3
"""
Audio Stitcher using FFmpeg - Combines multiple audio files with fade transitions
Requires ffmpeg to be installed on the system
"""

import os
import glob
import subprocess
import tempfile
from datetime import datetime

def get_audio_duration(file_path):
    """Get duration of audio file using ffprobe"""
    try:
        cmd = [
            'ffprobe', '-v', 'quiet', '-show_entries', 'format=duration',
            '-of', 'csv=p=0', file_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return float(result.stdout.strip())
    except:
        return 0

def format_timestamp(seconds):
    """Format seconds into MM:SS or HH:MM:SS timestamp format"""
    if seconds >= 3600:  # 1 hour or more
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hours}:{minutes:02d}:{secs:02d}"
    else:
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes:02d}:{secs:02d}"

def extract_song_title(filename):
    """Extract clean song title from filename"""
    # Remove file extension
    name = os.path.splitext(os.path.basename(filename))[0]
    
    # Try to remove common prefixes like timestamps and "table_audio_lofi_"
    if "table_audio_lofi_" in name:
        # Split by underscore and try to find the actual title
        parts = name.split("_")
        # Look for parts that aren't timestamps or common prefixes
        title_parts = []
        skip_next = False
        for i, part in enumerate(parts):
            if skip_next:
                skip_next = False
                continue
            if part in ["table", "audio", "lofi"] or part.isdigit() or (len(part) == 6 and part.isdigit()):
                continue
            if len(part) == 8 and part.isdigit():  # Date format YYYYMMDD
                continue
            if len(part) == 6 and part.isdigit():  # Time format HHMMSS
                continue
            title_parts.append(part)
        
        if title_parts:
            return " ".join(title_parts).replace("_", " ").title()
    
    # If no special processing needed, just clean up the filename
    return name.replace("_", " ").title()

def calculate_timestamps(audio_files, fade_duration, silence_duration=0):
    """Calculate when each song starts in the final mix"""
    timestamps = []
    current_time = 0.0
    
    for i, audio_file in enumerate(audio_files):
        duration = get_audio_duration(audio_file)
        title = extract_song_title(audio_file)
        
        timestamps.append({
            'file': audio_file,
            'title': title,
            'start_time': current_time,
            'duration': duration
        })
        
        if i == 0:
            # First song plays in full minus fade_duration, then silence
            current_time += duration - fade_duration + silence_duration
        else:
            # Subsequent songs: fade overlap + remaining duration + silence
            current_time += duration - fade_duration + silence_duration
    
    return timestamps

def stitch_audio_files(playlist_title, input_folder="songs", output_file=None, fade_duration=5, silence_duration=0):
    """
    Stitch together all audio files from a folder with fade transitions using FFmpeg
    
    Args:
        playlist_title: Title for the playlist (used in output filename)
        input_folder: Folder containing audio files
        output_file: Output filename (if None, auto-generates with timestamp)
        fade_duration: Fade duration in seconds (default 5)
        silence_duration: Silence duration after each fade out in seconds (default 0)
    """
    
    # Check if input folder exists
    if not os.path.exists(input_folder):
        print(f"❌ Folder '{input_folder}' not found!")
        return None
    
    # Check if ffmpeg is available
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ FFmpeg not found! Please install ffmpeg:")
        print("  macOS: brew install ffmpeg")
        print("  Ubuntu: sudo apt install ffmpeg")
        print("  Windows: Download from https://ffmpeg.org/")
        return None
    
    # Find all audio files in the folder
    audio_extensions = ['*.mp3', '*.wav', '*.m4a', '*.flac', '*.aac']
    audio_files = []
    
    for extension in audio_extensions:
        pattern = os.path.join(input_folder, extension)
        audio_files.extend(glob.glob(pattern))
    
    if not audio_files:
        print(f"❌ No audio files found in '{input_folder}'!")
        return None
    
    # Sort files alphabetically for consistent order
    audio_files.sort()
    
    # Calculate timestamps for each song
    timestamps = calculate_timestamps(audio_files, fade_duration, silence_duration)
    
    print(f"🎵 Found {len(audio_files)} audio files:")
    for i, ts in enumerate(timestamps, 1):
        print(f"  {i}. {os.path.basename(ts['file'])} ({ts['duration']:.1f}s)")
    
    # Generate output filename if not provided
    if output_file is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"playlists/{playlist_title}_{timestamp}.mp3"
    
    if silence_duration > 0:
        print(f"\n🔧 Stitching with {fade_duration}s crossfade transitions and {silence_duration}s silence gaps...")
    else:
        print(f"\n🔧 Stitching with {fade_duration}s crossfade transitions...")
    
    try:
        # Create temporary file list for ffmpeg concat
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            concat_file = f.name
            for audio_file in audio_files:
                # Use absolute path to avoid issues
                abs_path = os.path.abspath(audio_file)
                f.write(f"file '{abs_path}'\n")
        
        # Build ffmpeg command with crossfade filter and optional silence
        if len(audio_files) == 1:
            # Single file, just convert (add silence at end if specified)
            if silence_duration > 0:
                cmd = [
                    'ffmpeg', '-i', audio_files[0],
                    '-filter_complex', f'[0]apad=pad_dur={silence_duration}[out]',
                    '-map', '[out]', '-c:a', 'mp3', '-b:a', '320k',
                    '-y', output_file
                ]
            else:
                cmd = [
                    'ffmpeg', '-i', audio_files[0], '-c:a', 'mp3', '-b:a', '320k',
                    '-y', output_file
                ]
        elif len(audio_files) == 2:
            # Two files, crossfade with optional silence
            if silence_duration > 0:
                cmd = [
                    'ffmpeg',
                    '-i', audio_files[0],
                    '-i', audio_files[1],
                    '-filter_complex',
                    f'[0]apad=pad_dur={silence_duration}[a0];[1]adelay={int((get_audio_duration(audio_files[0]) - fade_duration + silence_duration) * 1000)}|{int((get_audio_duration(audio_files[0]) - fade_duration + silence_duration) * 1000)}[a1];[a0][a1]amix=inputs=2:duration=longest:normalize=0[mixed];[mixed]dynaudnorm[out]',
                    '-map', '[out]', '-c:a', 'mp3', '-b:a', '320k',
                    '-y', output_file
                ]
            else:
                cmd = [
                    'ffmpeg',
                    '-i', audio_files[0],
                    '-i', audio_files[1],
                    '-filter_complex',
                    f'[0][1]acrossfade=d={fade_duration}',
                    '-c:a', 'mp3', '-b:a', '320k',
                    '-y', output_file
                ]
        else:
            # Multiple files, chain crossfades with silence
            filter_complex = ""
            
            # Load all inputs
            inputs = []
            for i, audio_file in enumerate(audio_files):
                inputs.extend(['-i', audio_file])
            
            if silence_duration > 0:
                # More complex filter chain with silence padding
                current_time = 0
                filter_parts = []
                
                for i, audio_file in enumerate(audio_files):
                    duration = get_audio_duration(audio_file)
                    if i == 0:
                        # First file: add silence padding
                        filter_parts.append(f'[{i}]apad=pad_dur={silence_duration}[a{i}]')
                        current_time = duration + silence_duration
                    else:
                        # Subsequent files: delay to start at right time
                        delay_ms = int(current_time * 1000)
                        filter_parts.append(f'[{i}]adelay={delay_ms}|{delay_ms}[a{i}]')
                        current_time += duration - fade_duration + silence_duration
                
                # Mix all streams together with volume normalization
                stream_refs = ''.join([f'[a{i}]' for i in range(len(audio_files))])
                filter_parts.append(f'{stream_refs}amix=inputs={len(audio_files)}:duration=longest:normalize=0[mixed]')
                filter_parts.append('[mixed]dynaudnorm[out]')
                
                filter_complex = ';'.join(filter_parts)
                
                cmd = [
                    'ffmpeg'
                ] + inputs + [
                    '-filter_complex', filter_complex,
                    '-map', '[out]',
                    '-c:a', 'mp3', '-b:a', '320k',
                    '-y', output_file
                ]
            else:
                # Original crossfade logic without silence
                current_stream = "[0]"
                for i in range(1, len(audio_files)):
                    if i == 1:
                        filter_complex += f"{current_stream}[{i}]acrossfade=d={fade_duration}[cf{i}];"
                        current_stream = f"[cf{i}]"
                    else:
                        filter_complex += f"{current_stream}[{i}]acrossfade=d={fade_duration}[cf{i}];"
                        current_stream = f"[cf{i}]"
                
                # Remove trailing semicolon
                filter_complex = filter_complex.rstrip(';')
                
                cmd = [
                    'ffmpeg'
                ] + inputs + [
                    '-filter_complex', filter_complex,
                    '-map', current_stream,
                    '-c:a', 'mp3', '-b:a', '320k',
                    '-y', output_file
                ]
        
        print(f"🚀 Running FFmpeg command...")
        
        # Run ffmpeg command
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            # Success! Show stats
            if os.path.exists(output_file):
                file_size = os.path.getsize(output_file) / (1024 * 1024)  # Convert to MB
                total_duration = get_audio_duration(output_file)
                
                print(f"✅ Successfully created stitched audio!")
                print(f"📁 File: {output_file}")
                print(f"⏱️  Total duration: {total_duration//60:.0f}m {total_duration%60:.0f}s")
                print(f"💾 File size: {file_size:.2f} MB")
                print(f"🎵 Tracks combined: {len(audio_files)}")
                
                # Print timestamp tracklist
                print(f"\n📋 Tracklist with Timestamps:")
                print(f"=" * 50)
                for i, ts in enumerate(timestamps, 1):
                    timestamp_str = format_timestamp(ts['start_time'])
                    print(f"{timestamp_str} - {i:02d}. {ts['title']}")
                
                # Also save tracklist to a text file
                tracklist_file = output_file.replace('.mp3', '_tracklist.txt')
                with open(tracklist_file, 'w') as f:
                    f.write(f"Tracklist for: {output_file}\n")
                    f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                    for i, ts in enumerate(timestamps, 1):
                        timestamp_str = format_timestamp(ts['start_time'])
                        f.write(f"{timestamp_str} - {i:02d}. {ts['title']}\n")
                print(f"📝 Tracklist saved to: {tracklist_file}")
                
                return output_file
            else:
                print("❌ Output file was not created")
                return None
        else:
            print(f"❌ FFmpeg error:")
            print(f"stdout: {result.stdout}")
            print(f"stderr: {result.stderr}")
            return None
            
    except Exception as e:
        print(f"❌ Error during processing: {e}")
        return None
    
    finally:
        # Clean up temporary file
        try:
            os.unlink(concat_file)
        except:
            pass