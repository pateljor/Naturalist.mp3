from stability_official_api import stability_lofi_generation
from audio_stitcher import stitch_audio_files
from mp3_to_mp4 import convert_audio_to_video
import json
import random

def main(index):
    print("🎵 Reading JSON Data for Lofi Plalists")
    print("Make sure to set the index of the playlist you want")
    print("=" * 60)
    print()

    # Setup lofi json data
    with open('/Users/jordanpatel/Git/lofi-channel/lofi_playlist_data.json', 'r') as f:
        lofi_playlist_data = json.load(f)

    playlist_data = lofi_playlist_data[index] # set index to what playlist you want
    playlist_name = playlist_data['title']
    playlist_songs = playlist_data['song_names']

    ## API CALLS
    
    # Stability API        
    print("🎵 Stability AI Stable Audio 2.0 - Official API")
    print("🎵 ...Logic for Music GPT comming soon")
    print("=" * 60)
    print()

        
    for song in playlist_songs:
        
        #TODO have prompt design here
    
        stability_lofi_generation(
            song_name=song,
            prompt=f"chill lofi hip hop beat, mellow jazzy piano chords, relaxing atmosphere, slow tempo, match the vibe of the song match the song_name: {song}",
            duration=random.randint(int(150), int(190)) # random time intervals, stable caps at 190 for longest song
        ) 

        #TODO Add logic for MusciGPT API
        
        # Ideally one half of songs are musicGPT other half are stability or can A/B test performance

    # Call stitcher
    print("🎵 Audio Stitcher (FFmpeg) - LoFi Mix Generator")
    print("=" * 60)
    
    # Run the stitching process
    result = stitch_audio_files(
        playlist_title=playlist_name,
        input_folder="songs",
        fade_duration=5,  # 5 seconds crossfade
        silence_duration=8  # 8 seconds of silence after each fade
    )
    
    if result:
        print(f"\n🎉 Audio stitching complete!")
    else:
        print("\n❌ Audio stitching failed!")

    # Call mp3_to_mp4
    print("🎬 MP3 to MP4 Converter")
    print("=" * 40)

    # Example usage - modify these paths as needed
    audio_file = f"playlists/{str(index)}_{playlist_name}"  # Change this to your audio file
    image_file = None  # Will auto-find matching image
    output_file = None  # Will auto-generate filename

    # Convert audio to video
    result = convert_audio_to_video(
        audio_file=audio_file,
        image_file=image_file,
        output_file=output_file
    )

    if result:
        print(f"\n🎉 Conversion complete!")
        print(f"📹 Video saved as: {result}")
    else:
        print("\n❌ Conversion failed!")
        
if __name__ == "__main__":
    main(index=1)