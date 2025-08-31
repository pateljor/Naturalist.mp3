from stability_api import stability_lofi_generation
from musicgpt_api import musicgpt_lofi_generation
from audio_stitcher import stitch_audio_files
from mp3_to_mp4 import convert_audio_to_video
from description_generator import generate_description
from rename_songs import rename_songs
import json
import random

HASHTAGS = """#backgroundmusicwithoutlimitations #coffeetime #coffeebreak #coffeeshopmusic #cafemusic #lofimusic #chillmusic #chillhop #lofihiphop #relaxingmusic #naturemusic #lofimusicforsleep #musicforsleep #studymusic #retromusic #lofichill #retrolofi #funk #funkopop #relaxation #relaxmusic #lofiremix #backgroundmusicforsleep #lofiforstudy"""

def main(index):
    print("🎵 Reading JSON Data for Lofi Plalists")
    print("Make sure to set the index of the playlist you want")
    print("=" * 60)
    print()

    # Setup lofi json data
    with open('/Users/jordanpatel/Git/lofi-channel/lofi_playlist_data.json', 'r') as f:
        lofi_playlist_data = json.load(f)

    playlist_data = lofi_playlist_data[index] # set index to what playlist you want
    song_names = playlist_data['song_names'][:30]
        
    ### MusicGPT Call - Deprecated showing for contextg    
    # for i in range(0, len(song_names), 2):
    #     musicgpt_lofi_generation(
    #         # prompt='Create a chill lofi hip hop beat with jazzy piano chords, soft vinyl crackle, and a relaxing atmosphere perfect for studying',
    #         prompt=f"A slightly upbeat lofi hip hop instrumental with a warm, cozy, and cheerful mood, slow tempo, simple melody, bright but soothing.",
    #         # prompt="A lo-fi instrumental which could suit walking outside in nature in the morning"
    #         music_style='Lofi',
    #         song_names = [playlist_data['song_names'][i], playlist_data['song_names'][i+1]]
    #     )
    
    ### Stability API Call - Deprecated showing for context     
    # print("🎵 Stability AI Stable Audio 2.0 - Official API")
    # print("🎵 ...Logic for Music GPT comming soon")
    # print("=" * 60)
    # print()

    # # Stability Call    
    # for song in playlist_data['song_names']:
    #     stability_lofi_generation(
    #         song_name=song,
    #         prompt=f"A slightly upbeat lofi hip hop instrumental at ~88 BPM, with a warm, cozy, and cheerful mood (uplifting yet relaxed). Featuring jazzy piano, soft vinyl crackle, gentle acoustic guitar plucks, mellow laid-back drums with light swing, smooth jazzy bass, and ambient background texture — bright but soothing.",
    #         duration=random.randint(int(150), int(190)) # random time intervals, stable caps at 190 for longest song
    #     ) 
        
    # Instead of using musicgpt or stability (poor audio quality), can use suno and manually (no api atm) move files to song folder, run below command to match the titles
    # to json for stitcher to work
    rename_songs(song_names)
    

    # Call stitcher
    print("🎵 Audio Stitcher (FFmpeg) - LoFi Mix Generator")
    print("=" * 60)
    
    # Run the stitching process
    result_mp3 = stitch_audio_files(
        playlist_title=playlist_data['title'],
        input_folder="songs",
        fade_duration=5,  # 5 seconds crossfade
        silence_duration=6,  # 8 seconds of silence after each fade
        producer_tag='producer_tags/intro_prod_tag_v2.mp3'
    )
    
    if result_mp3:
        print(f"\n🎉 Audio stitching complete!")
    else:
        print("\n❌ Audio stitching failed!")

    # Call mp3_to_mp4
    print("🎬 MP3 to MP4 Converter")
    print("=" * 40)


    # Convert audio to video
    result_mp4 = convert_audio_to_video(
        audio_file=result_mp3,
        image_file=None,
        output_file=result_mp3.replace(".mp3", ".mp4")
    )

    if result_mp4:
        print(f"\n🎉 Conversion complete!")
        print(f"📹 Video saved as: {result_mp4}")
    else:
        print("\n❌ Conversion failed!")
        
    # Call description generator and save
    description = generate_description(
        playlist_data['description'],
        result_mp3.replace(".mp3", "_tracklist.txt"),
        HASHTAGS
    )
    with open(result_mp4.replace(".mp4", "_description.txt"), 'w', encoding='utf-8') as f:
        f.write(description)
    
    print("\n📋 Generated Description:")
    print("=" * 50)
    print(f"\n🎉 Everythign is complete! 🎉")

    
        
if __name__ == "__main__":
    main(index=13)