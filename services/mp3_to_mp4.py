#!/usr/bin/env python3
"""
Script to combine an image from thumbnails folder with an MP3 from songs folder
to create an MP4 video with the image as a static background.
"""

import sys
from pathlib import Path

def create_mp4_from_image_and_audio(image_path, audio_path, output_path):
    """
    Create MP4 video from image and audio using ffmpeg with progress display
    """
    try:
        import subprocess
        import re
        import sys
        
        # First, get the duration of the audio file
        duration_cmd = [
            'ffprobe', '-v', 'quiet', '-show_entries', 'format=duration',
            '-of', 'csv=p=0', str(audio_path)
        ]
        
        try:
            duration_result = subprocess.run(duration_cmd, capture_output=True, text=True)
            total_duration = float(duration_result.stdout.strip())
        except:
            total_duration = 0
            print("⚠️ Could not determine audio duration")
        
        cmd = [
            'ffmpeg',
            '-loop', '1',  # Loop the image
            '-i', str(image_path),  # Input image
            '-i', str(audio_path),  # Input audio
            '-c:v', 'libx264',  # Video codec
            '-c:a', 'aac',  # Audio codec
            '-b:a', '192k',  # Audio bitrate
            '-vf', 'scale=trunc(iw/2)*2:trunc(ih/2)*2',  # Ensure dimensions are even
            '-pix_fmt', 'yuv420p',  # Pixel format for compatibility
            '-shortest',  # End when shortest stream ends
            '-progress', 'pipe:1',  # Output progress to stdout
            '-y',  # Overwrite output file
            str(output_path)
        ]
        
        print("🎬 Starting video conversion...")
        if total_duration > 0:
            minutes = int(total_duration // 60)
            seconds = int(total_duration % 60)
            print(f"📏 Audio duration: {minutes}m {seconds}s")
        
        # Run ffmpeg with real-time progress
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
                                 universal_newlines=True, bufsize=1)
        
        # Track progress
        current_time = 0
        last_progress = 0
        
        for line in process.stdout:
            line = line.strip()
            
            # Parse time progress from ffmpeg output
            if line.startswith('out_time_ms='):
                try:
                    time_ms = int(line.split('=')[1])
                    current_time = time_ms / 1000000  # Convert microseconds to seconds
                    
                    if total_duration > 0:
                        progress = min((current_time / total_duration) * 100, 100)
                        
                        # Only update every 5% to avoid spam
                        if progress - last_progress >= 5 or progress >= 99:
                            current_minutes = int(current_time // 60)
                            current_seconds = int(current_time % 60)
                            total_minutes = int(total_duration // 60)
                            total_seconds = int(total_duration % 60)
                            
                            progress_bar = "█" * int(progress // 5) + "░" * (20 - int(progress // 5))
                            print(f"\r🎬 Progress: [{progress_bar}] {progress:.1f}% ({current_minutes}:{current_seconds:02d}/{total_minutes}:{total_seconds:02d})", end='', flush=True)
                            last_progress = progress
                except (ValueError, IndexError):
                    pass
        
        # Wait for process to complete
        process.wait()
        print()  # New line after progress bar
        
        if process.returncode == 0:
            print(f"✅ Successfully created: {output_path}")
            return True
        else:
            stderr = process.stderr.read()
            print(f"❌ Error creating video: {stderr}")
            return False
            
    except FileNotFoundError:
        print("❌ Error: ffmpeg not found. Please install ffmpeg first.")
        print("  On macOS: brew install ffmpeg")
        print("  On Ubuntu: sudo apt install ffmpeg")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def get_files_in_folder(folder_path, extensions):
    """Get all files with specified extensions from a folder"""
    folder = Path(folder_path)
    if not folder.exists():
        return []
    
    files = []
    for ext in extensions:
        files.extend(folder.glob(f"*.{ext}"))
        files.extend(folder.glob(f"*.{ext.upper()}"))
    
    return sorted(files)

def convert_audio_to_video(audio_file, image_file=None, output_file=None):
    """
    Convert audio file to MP4 video with image background
    
    Args:
        audio_file: Path to the audio file
        image_file: Path to the image file (if None, looks for matching image)
        output_file: Output path for MP4 (if None, auto-generates)
    
    Returns:
        Path to created MP4 file or None if failed
    """
    from pathlib import Path
    
    audio_path = Path(audio_file)
    if not audio_path.exists():
        print(f"❌ Audio file not found: {audio_file}")
        return None
    
    # Try to find matching image if not provided
    if image_file is None:
        thumbnails_folder = Path('thumbnails')
        if thumbnails_folder.exists():
            # Look for image with same name as audio file
            audio_stem = audio_path.stem
            image_extensions = ['png', 'jpg', 'jpeg', 'bmp', 'tiff']
            
            for ext in image_extensions:
                potential_path = thumbnails_folder / f"{audio_stem}.{ext}"
                if potential_path.exists():
                    image_file = potential_path
                    break
            
            # If no matching image found, use the first available image
            if image_file is None:
                images = get_files_in_folder(thumbnails_folder, image_extensions)
                if images:
                    image_file = images[0]
                    print(f"🖼️ Using default image: {image_file}")
    
    if image_file is None:
        print("❌ No image file found")
        return None
    
    image_path = Path(image_file)
    if not image_path.exists():
        print(f"❌ Image file not found: {image_file}")
        return None
    
    # Generate output filename if not provided
    if output_file is None:
        videos_folder = Path('videos')
        videos_folder.mkdir(parents=True, exist_ok=True)
        output_file = videos_folder / f"{audio_path.stem}.mp4"
    else:
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_file = output_path
    
    print(f"🎬 Creating video:")
    print(f"  🎵 Audio: {audio_path}")
    print(f"  🖼️  Image: {image_path}")
    print(f"  📹 Output: {output_file}")
    
    # Create the video
    success = create_mp4_from_image_and_audio(image_path, audio_path, output_file)
    
    if success:
        print(f"✅ Video created successfully: {output_file}")
        return str(output_file)
    else:
        print("❌ Failed to create video")
        return None
