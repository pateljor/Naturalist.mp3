from stability_official_api import stability_lofi_generation
from audio_stitcher import stitch_audio_files
from mp3_to_mp4 import convert_audio_to_video
from description_generator import generate_description
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

    # ## API CALLS
    
    # # Stability API        
    # print("🎵 Stability AI Stable Audio 2.0 - Official API")
    # print("🎵 ...Logic for Music GPT comming soon")
    # print("=" * 60)
    # print()

        
    # for song in playlist_data['song_names']:
        
    #     #TODO have prompt design here
    
    #     stability_lofi_generation(
    #         song_name=song,
    #         prompt=f"chill lofi hip hop beat, mellow jazzy piano chords, relaxing atmosphere, slow tempo, match the vibe of the song match the song_name: {song}",
    #         duration=random.randint(int(150), int(190)) # random time intervals, stable caps at 190 for longest song
    #     ) 

    #     #TODO Add logic for MusciGPT API
        
    #     # Ideally one half of songs are musicGPT other half are stability or can A/B test performance

    # Call stitcher
    print("🎵 Audio Stitcher (FFmpeg) - LoFi Mix Generator")
    print("=" * 60)
    
    # Run the stitching process
    result_mp3 = stitch_audio_files(
        playlist_title=playlist_data['title'],
        input_folder="songs",
        fade_duration=5,  # 5 seconds crossfade
        silence_duration=8  # 8 seconds of silence after each fade
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
        output_file=result_mp3.replace(".mp3", ".mp4").replace("plalists/", "videos/")
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
    with open(result_mp4.replace(".mp4", "_description.txt").replace("videos/", "descriptions/"), 'w', encoding='utf-8') as f:
        f.write(description)
    
    print("\n📋 Generated Description:")
    print("=" * 50)
    print(f"\n🎉 Everythign is complete! 🎉")

    
        
if __name__ == "__main__":
    main(index=1)