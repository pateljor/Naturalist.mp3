#!/usr/bin/env python3
"""
Official Stability AI Stable Audio 2.0 API Integration
Based on the official API documentation from platform.stability.ai
"""

import os
import requests
import json
from datetime import datetime
import random
from dotenv import load_dotenv

# load env file
load_dotenv(dotenv_path=".env.local")

class StabilityAudioAPI:
    def __init__(self, api_key=None):
        self.api_key = os.getenv("STABILITY_AUDIO_API_KEY")
        self.endpoint = "https://api.stability.ai/v2beta/audio/stable-audio-2/text-to-audio"
    
    def generate_audio(self, prompt, song_name, duration, model="stable-audio-2", output_format="mp3", 
                      steps=50, cfg_scale=7, seed=None):
        """
        Generate audio using Stability AI's official Stable Audio 2.0 API
        
        Args:
            prompt: Text description (up to 10,000 chars)
            duration: Duration in seconds (1-190, default 190)
            model: "stable-audio-2" or "stable-audio-2.5"
            output_format: "mp3" or "wav"
            steps: Sampling steps (30-100 for v2, 4 or 8 for v2.5)
            cfg_scale: Adherence to prompt (1-25)
            seed: Random seed (0-4294967294, None for random)
        """
        
        if not self.api_key:
            raise ValueError("API key not found! Set STABILITY_API_KEY environment variable")
        
        # Prepare headers (DON'T set content-type - let requests handle multipart/form-data)
        headers = {
            "authorization": f"Bearer {self.api_key}",
            "accept": "audio/*",  # Get audio bytes directly
            "stability-client-id": "lofi-channel-generator",
            "stability-client-version": "1.0.0"
        }
        
        # Prepare form data as files dict for proper multipart encoding
        files = {
            "prompt": (None, prompt),
            "duration": (None, str(duration)),
            "model": (None, model),
            "output_format": (None, output_format),
            "steps": (None, str(steps)),
            "cfg_scale": (None, str(cfg_scale))
        }
        
        if seed is not None:
            files["seed"] = (None, str(seed))
        
        print(f"🎵 Generating audio with Stability AI...")
        print(f"📝 Prompt: '{prompt}'")
        print(f"⏱️  Duration: {duration}s")
        print(f"🤖 Model: {model}")
        print(f"🎛️  Steps: {steps}, CFG Scale: {cfg_scale}")
        print(f"💰 Credits: ~{17 + 0.06 * steps:.0f}")
        
        try:
            # Send POST request with files for proper multipart/form-data
            response = requests.post(
                self.endpoint,
                headers=headers,
                files=files  # This creates proper multipart/form-data with boundary
            )
            
            print(f"📡 Response status: {response.status_code}")
            
            if response.status_code == 200:
                # Success - got audio bytes
                return self._save_audio(song_name, response.content, output_format)
            
            elif response.status_code == 400:
                print(f"❌ Invalid parameters: {response.text}")
                return None
            
            elif response.status_code == 403:
                print("❌ Content flagged by moderation system")
                return None
            
            elif response.status_code == 422:
                print(f"❌ Request rejected: {response.text}")
                return None
            
            elif response.status_code == 429:
                print("❌ Rate limit exceeded (150 requests in 10 seconds)")
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
    
    def _save_audio(self, song_name, audio_data, format_ext):
        """Save audio data to file"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"songs/{song_name}_{timestamp}.{format_ext}"
            
            with open(filename, 'wb') as f:
                f.write(audio_data)
            
            file_size = len(audio_data) / (1024 * 1024)  # MB
            duration_estimate = len(audio_data) / (44100 * 2 * 2)  # Rough estimate for stereo 16-bit
            
            print(f"✅ Audio saved: {filename}")
            print(f"📁 File size: {file_size:.2f} MB")
            print(f"⏱️  Estimated duration: {duration_estimate:.1f}s")
            
            return filename
            
        except Exception as e:
            print(f"❌ Error saving audio: {e}")
            return None

def stability_lofi_generation(song_name, prompt, duration):
    """Test lofi beat generation with various prompts"""
    
    api = StabilityAudioAPI()
    
    print("🎵 Stability AI Official API - LoFi Beat Generator")
    print("=" * 60)
    print("⚙️  Make sure STABILITY_API_KEY environment variable is set!")
    print()
    
    generated_files = []
    
    print(f"🎯 Running: {song_name}")
    print("-" * 40)
    
    filename = api.generate_audio(
        prompt=prompt,
        song_name=song_name,
        duration=duration,
        model="stable-audio-2",  # Use stable-audio-2 for testing
        output_format="mp3",
        steps=100,  # Default quality
        cfg_scale=7  # Good balance
    )
    
    if filename:
        generated_files.append(filename)
        print(f"🎉 Success! Generated: {filename}")
        
        print(f"\n🔊 You can now play the generated lofi beat!")
        print(f"🎵 Try different prompts by modifying the script")
    else:
        print("❌ Generation failed!")
        print("\n🔧 Troubleshooting:")
        print("1. ✓ Check your API key is valid: https://platform.stability.ai/")
        print("2. ✓ Verify you have sufficient credits")
        print("3. ✓ Try a simpler prompt if content was flagged")
        print("4. ✓ Check rate limits (150 req/10 seconds)")
    
    return generated_files


