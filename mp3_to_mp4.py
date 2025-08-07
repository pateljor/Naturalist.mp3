#!/usr/bin/env python3
"""
Script to combine an image from thumbnails folder with an MP3 from songs folder
to create an MP4 video with the image as a static background.
"""

import sys
import argparse
from pathlib import Path

def create_mp4_from_image_and_audio(image_path, audio_path, output_path):
    """
    Create MP4 video from image and audio using ffmpeg
    """
    try:
        import subprocess
        
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
            '-y',  # Overwrite output file
            str(output_path)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f" Successfully created: {output_path}")
            return True
        else:
            print(f" Error creating video: {result.stderr}")
            return False
            
    except FileNotFoundError:
        print(" Error: ffmpeg not found. Please install ffmpeg first.")
        print("  On macOS: brew install ffmpeg")
        print("  On Ubuntu: sudo apt install ffmpeg")
        return False
    except Exception as e:
        print(f" Unexpected error: {e}")
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

def main():
    parser = argparse.ArgumentParser(description='Combine image and MP3 into MP4 video')
    parser.add_argument('name', nargs='?', help='Name to match PNG and MP3 files (e.g., "Denali" matches Denali.png and Denali.mp3)')
    parser.add_argument('--image', help='Specific image file to use')
    parser.add_argument('--audio', help='Specific MP3 file to use')
    parser.add_argument('--output', help='Output MP4 file name')
    
    args = parser.parse_args()
    
    # Define folders
    thumbnails_folder = Path('thumbnails')
    songs_folder = Path('songs')
    
    # Check if folders exist
    if not thumbnails_folder.exists():
        print(" Error: 'thumbnails' folder not found")
        return 1
    
    if not songs_folder.exists():
        print(" Error: 'songs' folder not found")
        return 1
    
    # Handle name-based matching
    if args.name:
        # Look for matching PNG and MP3 files
        image_extensions = ['png', 'jpg', 'jpeg', 'bmp', 'tiff']
        audio_extensions = ['mp3', 'wav', 'flac', 'm4a']
        
        # Find matching image
        image_path = None
        for ext in image_extensions:
            potential_path = thumbnails_folder / f"{args.name}.{ext}"
            if potential_path.exists():
                image_path = potential_path
                break
        
        if not image_path:
            print(f" Error: No image file found for '{args.name}' in thumbnails folder")
            return 1
        
        # Find matching audio
        audio_path = None
        for ext in audio_extensions:
            potential_path = songs_folder / f"{args.name}.{ext}"
            if potential_path.exists():
                audio_path = potential_path
                break
        
        if not audio_path:
            print(f" Error: No audio file found for '{args.name}' in songs folder")
            return 1
        
        # Set output path to same name
        output_path = Path(f"videos/{args.name}.mp4")
        
        # Skip to video creation since we have both files
        print(f"Creating video from:")
        print(f"  Image: {image_path}")
        print(f"  Audio: {audio_path}")
        print(f"  Output: {output_path}")
        
        # Create videos directory if it doesn't exist
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create the video
        success = create_mp4_from_image_and_audio(image_path, audio_path, output_path)
        return 0 if success else 1
        
    # Get image file
    elif args.image:
        image_path = Path(args.image)
        if not image_path.exists():
            print(f" Error: Image file '{args.image}' not found")
            return 1
    else:
        # Find images in thumbnails folder
        image_extensions = ['jpg', 'jpeg', 'png', 'bmp', 'tiff']
        images = get_files_in_folder(thumbnails_folder, image_extensions)
        
        if not images:
            print(" No image files found in 'thumbnails' folder")
            return 1
        
        if len(images) == 1:
            image_path = images[0]
        else:
            print("Available images:")
            for i, img in enumerate(images, 1):
                print(f"  {i}. {img.name}")
            
            try:
                choice = int(input("Select image number: ")) - 1
                if 0 <= choice < len(images):
                    image_path = images[choice]
                else:
                    print(" Invalid selection")
                    return 1
            except (ValueError, KeyboardInterrupt):
                print("\n Operation cancelled")
                return 1
    
    # Get audio file
    if args.audio:
        audio_path = Path(args.audio)
        if not audio_path.exists():
            print(f" Error: Audio file '{args.audio}' not found")
            return 1
    else:
        # Find MP3 files in songs folder
        audio_extensions = ['mp3', 'wav', 'flac', 'm4a']
        audio_files = get_files_in_folder(songs_folder, audio_extensions)
        
        if not audio_files:
            print(" No audio files found in 'songs' folder")
            return 1
        
        if len(audio_files) == 1:
            audio_path = audio_files[0]
        else:
            print("Available audio files:")
            for i, audio in enumerate(audio_files, 1):
                print(f"  {i}. {audio.name}")
            
            try:
                choice = int(input("Select audio number: ")) - 1
                if 0 <= choice < len(audio_files):
                    audio_path = audio_files[choice]
                else:
                    print(" Invalid selection")
                    return 1
            except (ValueError, KeyboardInterrupt):
                print("\n Operation cancelled")
                return 1
    
    # Determine output path (skip if already set by name matching)
    if not args.name:
        if args.output:
            output_path = Path(f"videos/{args.output}")
        else:
            # Generate output filename based on input files
            audio_name = audio_path.stem
            image_name = image_path.stem
            output_path = Path(f"videos/{audio_name}_{image_name}.mp4")
    
    print(f"Creating video from:")
    print(f"  Image: {image_path}")
    print(f"  Audio: {audio_path}")
    print(f"  Output: {output_path}")
    
    # Create the video
    success = create_mp4_from_image_and_audio(image_path, audio_path, output_path)
    
    return 0 if success else 1

if __name__ == '__main__':
    sys.exit(main())
    
# python3 mp3_to_mp4.py --image thumbnails/cover.jpg --audio songs/track.mp3 --output my_video.mp4