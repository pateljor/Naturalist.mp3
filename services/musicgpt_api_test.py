#!/usr/bin/env python3
"""
MusicGPT API Integration with Polling Support
Generates lofi music using MusicGPT's AI music generation API
"""

import os
import time
import requests
from datetime import datetime
from dotenv import load_dotenv

# load env file
load_dotenv(dotenv_path=".env.local")

class MusicGPTAPI:
    """MusicGPT API client with polling support"""
    
    def __init__(self):
        self.api_key = os.getenv("MUSICGPT_API_KEY")
        self.base_url = "https://api.musicgpt.com/api/public/v1"
    
    def generate_music(self, prompt=None, music_style=None, lyrics=None, 
                      make_instrumental=False, vocal_only=False, song_names=None):
        """
        Generate music using MusicGPT API
        
        Args:
            prompt: Natural language prompt for music generation
            music_style: Musical genre (e.g., "Lofi Hip Hop", "Jazz")
            lyrics: Custom lyrics for the song
            make_instrumental: Generate instrumental-only track
            vocal_only: Generate vocals-only track
            song_names: List of two strings to use as filenames for downloaded songs
        """
        
        if not self.api_key:
            raise ValueError("API key not found! Set MUSICGPT_API_KEY environment variable")
        
        # Prepare request
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {}
        
        if prompt:
            payload["prompt"] = prompt
        if music_style:
            payload["music_style"] = music_style
        if lyrics:
            payload["lyrics"] = lyrics
        if make_instrumental:
            payload["make_instrumental"] = True
        if vocal_only:
            payload["vocal_only"] = True
        
        print(f"🎵 Generating music with MusicGPT...")
        if prompt:
            print(f"📝 Prompt: '{prompt}'")
        if music_style:
            print(f"🎼 Style: {music_style}")
        if lyrics:
            print(f"🎤 Lyrics: {lyrics[:100]}{'...' if len(lyrics) > 100 else ''}")
        print(f"🎛️  Instrumental: {make_instrumental}, Vocal Only: {vocal_only}")
        
        # Debug: show exact payload being sent
        print(f"🔍 Payload: {payload}")
        print(f"🔍 Headers: {headers}")
        
        try:
            # Send request
            endpoint_url = f"{self.base_url}/MusicAI"
            print(f"🔍 Sending request to: {endpoint_url}")
            
            response = requests.post(
                endpoint_url,
                headers=headers,
                json=payload
            )
            
            print(f"📡 Response status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get("success"):
                    task_id = result.get("task_id")
                    eta = result.get("eta", 180)  # Default 3 minutes if not provided
                    
                    print(f"✅ Generation started!")
                    print(f"🆔 Task ID: {task_id}")
                    print(f"⏱️  ETA: {eta} seconds")
                    print(f"🎵 Track 1 ID: {result.get('conversion_id_1', 'N/A')}")
                    print(f"🎵 Track 2 ID: {result.get('conversion_id_2', 'N/A')}")
                    
                    # Use polling to get results
                    if task_id:
                        return self.poll_for_result(task_id, eta, song_names)
                    
                    # Return initial result if no task_id
                    return result
                
                else:
                    print(f"❌ Generation failed: {result}")
                    return None
            
            elif response.status_code == 402:
                print("❌ Insufficient credits")
                return None
            
            elif response.status_code == 500:
                print("❌ Internal server error")
                return None
            
            else:
                print(f"❌ Unexpected status {response.status_code}: {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Request error: {e}")
            return None
    
    
    def get_task_result(self, task_id):
        """Get task result by ID using the getById endpoint"""
        if not self.api_key:
            raise ValueError("API key not found!")
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.get(
                f"{self.base_url}/byId?conversionType=MUSIC_AI&task_id={task_id}",
                headers=headers
            )
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                return {"error": "Task not found", "status_code": 404}
            else:
                return {"error": f"API error: {response.status_code}", "status_code": response.status_code}
                
        except requests.exceptions.RequestException as e:
            return {"error": f"Request failed: {e}"}
    
    def poll_for_result(self, task_id, eta_seconds, song_names=None):
        """Poll for task completion using getById endpoint"""
        print(f"🔄 Polling for task completion...")
        print(f"⏱️  Initial wait: {eta_seconds + 20} seconds")
        
        # Wait for ETA + 20 seconds before first poll
        time.sleep(eta_seconds + 20)
        
        max_retries = 5
        retry_delay = 30  # 30 seconds between retries
        
        for attempt in range(max_retries):
            print(f"🔍 Polling attempt {attempt + 1}/{max_retries}")
            
            result = self.get_task_result(task_id)
            
            if "error" not in result:
                # Check if task is completed - handle the new response format
                conversion_data = result.get("conversion", {})
                if result.get("success") or conversion_data.get("status") == "COMPLETED":
                    print(f"✅ Task completed successfully!")
                    return self._process_polling_result(result, song_names)
                elif conversion_data.get("status") == "FAILED":
                    print(f"❌ Task failed: {conversion_data.get('message', 'Unknown error')}")
                    return result
                elif conversion_data.get("status") in ["PENDING", "PROCESSING", "IN_PROGRESS"]:
                    print(f"⏳ Task still processing... (attempt {attempt + 1}) - Status: {conversion_data.get('status')}")
                else:
                    print(f"🤔 Unexpected status: {conversion_data.get('status', 'unknown')}")
            else:
                print(f"❌ Polling error: {result.get('error')}")
            
            # Wait before next retry (except on last attempt)
            if attempt < max_retries - 1:
                print(f"⏸️  Waiting {retry_delay} seconds before next attempt...")
                time.sleep(retry_delay)
        
        print(f"⏰ Maximum polling attempts reached")
        return {"status": "timeout", "message": "Task did not complete within polling window"}
    
    def _process_polling_result(self, result_data, song_names=None):
        """Process polling result and download music files"""
        if not result_data.get('success'):
            return result_data
        
        conversion_data = result_data.get('conversion', {})
        downloaded_files = []
        
        # Download music tracks from conversion_path fields
        for i in [1, 2]:
            conversion_path = conversion_data.get(f'conversion_path_{i}')
            
            # Use custom song name if provided, otherwise use API title or default
            if song_names and len(song_names) >= i:
                track_title = song_names[i-1]  # i-1 because list is 0-indexed
            else:
                track_title = conversion_data.get(f'title_{i}', f'track_{i}')
            
            if conversion_path:
                filename = self._download_music(conversion_path, track_title, i)
                if filename:
                    downloaded_files.append(filename)
        
        result_data['downloaded_files'] = downloaded_files
        
        # Add some useful info from the conversion data
        result_data['track_titles'] = {
            'title_1': conversion_data.get('title_1'),
            'title_2': conversion_data.get('title_2')
        }
        result_data['durations'] = {
            'duration_1': conversion_data.get('conversion_duration_1'),
            'duration_2': conversion_data.get('conversion_duration_2')
        }
        
        return result_data
    
    def _download_music(self, url, track_name, track_number=None):
        """Download music file from URL"""
        try:
            print(f"⬇️ Downloading {track_name} from {url}...")
            
            response = requests.get(url)
            response.raise_for_status()
            
            print(f"📦 Response status: {response.status_code}, Content length: {len(response.content)} bytes")
            
            # Generate filename with track title
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            # Clean track name for filename
            clean_track_name = "".join(c for c in track_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
            clean_track_name = clean_track_name.replace(' ', '_')
            
            if track_number:
                filename = f"{clean_track_name}_{timestamp}_{track_number}.mp3"
            else:
                filename = f"{clean_track_name}_{timestamp}_.mp3"
            
            # Use absolute path in services directory
            full_path = os.path.join('songs/', filename)
            
            print(f"📁 Saving to: {full_path}")
            
            with open(full_path, 'wb') as f:
                f.write(response.content)
            
            # Verify file was created
            if os.path.exists(full_path):
                file_size = len(response.content) / (1024 * 1024)
                actual_size = os.path.getsize(full_path) / (1024 * 1024)
                print(f"✅ Downloaded: {filename} ({file_size:.2f} MB)")
                print(f"📂 File saved at: {full_path} ({actual_size:.2f} MB)")
                return full_path
            else:
                print(f"❌ File was not created: {full_path}")
                return None
            
        except Exception as e:
            print(f"❌ Download error for {track_name}: {e}")
            import traceback
            print(f"🔍 Full traceback: {traceback.format_exc()}")
            return None

def musicgpt_lofi_generation(prompt, music_style, song_names=None):
    """Test MusicGPT with lofi prompts
    
    Args:
        song_names: List of two strings to use as filenames for the downloaded songs
                   Example: ['My_Lofi_Track_1', 'My_Lofi_Track_2']
    """
    
    api = MusicGPTAPI()
    
    
    print("🎵 MusicGPT API Test - LoFi Generation")
    print("=" * 60)
    print("⚙️  Make sure MUSICGPT_API_KEY environment variable is set!")
    print()
    
    # Test lofi generation
    print(f"🎯 Testing: Lofi Hip Hop Generation")
    if song_names:
        print(f"🎼 Custom song names: {song_names[0]}, {song_names[1]}")
    print("-" * 40)
    
    result = api.generate_music(
        prompt=prompt,
        music_style=music_style,
        make_instrumental=True,
        song_names=song_names
    )
    
    if result and result.get('success'):
        print(f"🎉 Success! MusicGPT generation completed!")
        
        if 'downloaded_files' in result:
            print(f"📁 Downloaded files:")
            for file in result['downloaded_files']:
                print(f"   - {file}")
        
        print(f"\n🎵 You can now play your generated lofi tracks!")
        
    else:
        print("❌ Generation failed!")
        print("\n🔧 Troubleshooting:")
        print("1. ✓ Check your API key: https://musicgpt.com/")
        print("2. ✓ Verify you have sufficient credits")
        print("3. ✓ Check your network connection for API requests")
    
    return result
