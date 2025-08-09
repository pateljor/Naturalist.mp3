#!/usr/bin/env python3
"""
Script to combine an image from thumbnails folder with an MP3 from songs folder
to create an MP4 video with the image as a static background.
"""

import sys
from pathlib import Path
from moviepy.editor import ImageClip, AudioFileClip, CompositeVideoClip

def create_mp4_from_image_and_audio(image_path, audio_path, output_path):
    """
    Create MP4 video from image and audio using MoviePy (much faster than FFmpeg)
    """
    try:
        import time
        
        # Validate input files
        if not image_path.exists():
            print(f"❌ Image file not found: {image_path}")
            return False
        if not audio_path.exists():
            print(f"❌ Audio file not found: {audio_path}")
            return False
            
        # Check file sizes (0 bytes indicates corruption)
        if image_path.stat().st_size == 0:
            print(f"❌ Image file is empty: {image_path}")
            return False
        if audio_path.stat().st_size == 0:
            print(f"❌ Audio file is empty: {audio_path}")
            return False
            
        print(f"🔍 Input validation passed:")
        print(f"  🖼️  Image: {image_path} ({image_path.stat().st_size / 1024:.1f} KB)")
        print(f"  🎵 Audio: {audio_path} ({audio_path.stat().st_size / 1024:.1f} KB)")
        
        print("🎬 Starting video conversion with MoviePy...")
        start_time = time.time()
        
        # Load audio clip to get duration
        print("🎵 Loading audio...")
        audio_clip = AudioFileClip(str(audio_path))
        duration = audio_clip.duration
        
        minutes = int(duration // 60)
        seconds = int(duration % 60)
        print(f"📏 Audio duration: {minutes}m {seconds}s")
        
        # Load image and set duration to match audio
        print("🖼️  Loading image...")
        image_clip = ImageClip(str(image_path), duration=duration)
        
        # Combine image and audio
        print("🎬 Compositing video...")
        video_clip = image_clip.set_audio(audio_clip)
        
        # Progress callback function
        def progress_callback(get_frame, t):
            progress = (t / duration) * 100 if duration > 0 else 0
            elapsed = time.time() - start_time
            if int(progress) % 5 == 0:  # Update every 5%
                current_minutes = int(t // 60)
                current_seconds = int(t % 60)
                total_minutes = int(duration // 60)
                total_seconds = int(duration % 60)
                
                progress_bar = "█" * int(progress // 5) + "░" * (20 - int(progress // 5))
                print(f"\r🎬 Progress: [{progress_bar}] {progress:.1f}% ({current_minutes}:{current_seconds:02d}/{total_minutes}:{total_seconds:02d}) - {elapsed:.1f}s elapsed", end='', flush=True)
            
            return get_frame(t)
        
        # Write video file
        print("💾 Writing video file...")
        video_clip.write_videofile(
            str(output_path),
            fps=1,  # Very low FPS since it's a static image
            codec='libx264',
            audio_codec='aac',
            temp_audiofile='temp-audio.m4a',
            remove_temp=True,
            verbose=False,
            logger=None  # Suppress moviepy's verbose output
        )
        
        # Clean up clips
        audio_clip.close()
        image_clip.close()
        video_clip.close()
        
        elapsed_time = time.time() - start_time
        print(f"\n✅ Successfully created: {output_path}")
        print(f"⏱️  Total time: {elapsed_time:.1f}s")
        return True
        
    except ImportError:
        print("❌ Error: MoviePy not found. Installing...")
        import subprocess
        subprocess.run([sys.executable, "-m", "pip", "install", "moviepy"])
        print("✅ MoviePy installed. Please run the script again.")
        return False
    except Exception as e:
        print(f"❌ Error creating video: {e}")
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
