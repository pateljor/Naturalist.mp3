#!/usr/bin/env python3
"""
MusicGPT API Integration with Webhook Support
Generates lofi music using MusicGPT's AI music generation API
"""

import os
import time
import json
import requests
import threading
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

class WebhookServer:
    """Simple webhook server to receive MusicGPT results"""
    
    def __init__(self, port=8000):
        self.port = port
        self.results = {}
        self.server = None
        self.server_thread = None
    
    def start_server(self):
        """Start the webhook server in a separate thread"""
        
        webhook_handler = self
        
        class WebhookHandler(BaseHTTPRequestHandler):
            def do_POST(self):
                content_length = int(self.headers.get('Content-Length', 0))
                post_data = self.rfile.read(content_length)
                
                try:
                    webhook_data = json.loads(post_data.decode('utf-8'))
                    
                    # Store the result
                    task_id = webhook_data.get('task_id')
                    if task_id:
                        webhook_handler.results[task_id] = webhook_data
                        print(f"📨 Webhook received for task: {task_id}")
                        
                        # Print result summary
                        if webhook_data.get('success'):
                            print("✅ Generation completed successfully!")
                            if 'music_url_1' in webhook_data:
                                print(f"🎵 Music Track 1: {webhook_data['music_url_1']}")
                            if 'music_url_2' in webhook_data:
                                print(f"🎵 Music Track 2: {webhook_data['music_url_2']}")
                        else:
                            print(f"❌ Generation failed: {webhook_data.get('error', 'Unknown error')}")
                    
                    # Send response
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({"status": "received"}).encode())
                    
                except Exception as e:
                    print(f"❌ Webhook error: {e}")
                    self.send_response(400)
                    self.end_headers()
            
            def log_message(self, format, *args):
                # Suppress default logging
                pass
        
        try:
            self.server = HTTPServer(('localhost', self.port), WebhookHandler)
            self.server_thread = threading.Thread(target=self.server.serve_forever)
            self.server_thread.daemon = True
            self.server_thread.start()
            print(f"🎣 Webhook server started on http://localhost:{self.port}")
            return True
        except Exception as e:
            print(f"❌ Failed to start webhook server: {e}")
            return False
    
    def stop_server(self):
        """Stop the webhook server"""
        if self.server:
            self.server.shutdown()
            self.server.server_close()
            print("🛑 Webhook server stopped")
    
    def get_result(self, task_id, timeout=300):
        """Wait for webhook result"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if task_id in self.results:
                return self.results[task_id]
            time.sleep(2)
        
        return None

class MusicGPTAPI:
    """MusicGPT API client with webhook support"""
    
    def __init__(self, api_key=None):
        self.api_key = "xxxx"
        self.base_url = "https://api.musicgpt.com/api/public/v1"
        self.webhook_server = None
    
    def generate_music(self, prompt=None, music_style=None, lyrics=None, 
                      make_instrumental=False, vocal_only=False, 
                      use_webhook=True, webhook_port=8000):
        """
        Generate music using MusicGPT API
        
        Args:
            prompt: Natural language prompt for music generation
            music_style: Musical genre (e.g., "Lofi Hip Hop", "Jazz")
            lyrics: Custom lyrics for the song
            make_instrumental: Generate instrumental-only track
            vocal_only: Generate vocals-only track
            use_webhook: Whether to use webhook for async results
            webhook_port: Port for webhook server
        """
        
        if not self.api_key:
            raise ValueError("API key not found! Set MUSICGPT_API_KEY environment variable")
        
        # Setup webhook if requested
        webhook_url = None
        if use_webhook:
            self.webhook_server = WebhookServer(webhook_port)
            if self.webhook_server.start_server():
                webhook_url = f"http://localhost:{webhook_port}"
                print(f"🎯 Using webhook: {webhook_url}")
            else:
                print("⚠️ Webhook setup failed, proceeding without webhook")
        
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
        if webhook_url:
            payload["webhook_url"] = webhook_url
        
        print(f"🎵 Generating music with MusicGPT...")
        if prompt:
            print(f"📝 Prompt: '{prompt}'")
        if music_style:
            print(f"🎼 Style: {music_style}")
        if lyrics:
            print(f"🎤 Lyrics: {lyrics[:100]}{'...' if len(lyrics) > 100 else ''}")
        print(f"🎛️  Instrumental: {make_instrumental}, Vocal Only: {vocal_only}")
        
        try:
            # Send request
            response = requests.post(
                f"{self.base_url}/MusicAI",
                headers=headers,
                json=payload
            )
            
            print(f"📡 Response status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get("success"):
                    task_id = result.get("task_id")
                    eta = result.get("eta", "unknown")
                    
                    print(f"✅ Generation started!")
                    print(f"🆔 Task ID: {task_id}")
                    print(f"⏱️  ETA: {eta} seconds")
                    print(f"🎵 Track 1 ID: {result.get('conversion_id_1', 'N/A')}")
                    print(f"🎵 Track 2 ID: {result.get('conversion_id_2', 'N/A')}")
                    
                    # Wait for webhook result if using webhook
                    if use_webhook and self.webhook_server and task_id:
                        print(f"⏳ Waiting for webhook result...")
                        webhook_result = self.webhook_server.get_result(task_id, eta + 60)
                        
                        if webhook_result:
                            return self._process_webhook_result(webhook_result)
                        else:
                            print("⏰ Webhook timeout")
                            return {"task_id": task_id, "status": "timeout"}
                    
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
        
        finally:
            # Cleanup webhook server
            if self.webhook_server:
                self.webhook_server.stop_server()
    
    def _process_webhook_result(self, webhook_data):
        """Process webhook result and download music files"""
        
        if not webhook_data.get('success'):
            return webhook_data
        
        downloaded_files = []
        
        # Download music tracks
        for i in [1, 2]:
            music_url = webhook_data.get(f'music_url_{i}')
            if music_url:
                filename = self._download_music(music_url, f"track_{i}")
                if filename:
                    downloaded_files.append(filename)
        
        webhook_data['downloaded_files'] = downloaded_files
        return webhook_data
    
    def _download_music(self, url, track_name):
        """Download music file from URL"""
        try:
            print(f"⬇️ Downloading {track_name}...")
            
            response = requests.get(url)
            response.raise_for_status()
            
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"musicgpt_{track_name}_{timestamp}.mp3"
            
            with open(filename, 'wb') as f:
                f.write(response.content)
            
            file_size = len(response.content) / (1024 * 1024)
            print(f"✅ Downloaded: {filename} ({file_size:.2f} MB)")
            
            return filename
            
        except Exception as e:
            print(f"❌ Download error for {track_name}: {e}")
            return None

def test_musicgpt_lofi():
    """Test MusicGPT with lofi prompts"""
    
    api = MusicGPTAPI()
    
    # Lofi test prompts
    test_cases = [
        {
            "name": "Prompt-Based Lofi",
            "prompt": "Create a chill lofi hip hop beat with jazzy piano chords, soft vinyl crackle, and a relaxing atmosphere perfect for studying",
            "make_instrumental": True
        }
    ]
    
    print("🎵 MusicGPT API Test - LoFi Generation")
    print("=" * 60)
    print("⚙️  Make sure MUSICGPT_API_KEY environment variable is set!")
    print()
    
    # Test with first case
    test_case = test_cases[0]
    print(f"🎯 Testing: {test_case['name']}")
    print("-" * 40)
    
    result = api.generate_music(
        prompt=test_case.get('prompt'),
        music_style=test_case.get('music_style'),
        lyrics=test_case.get('lyrics'),
        make_instrumental=test_case.get('make_instrumental', False),
        use_webhook=True,
        webhook_port=8000
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
        print("3. ✓ Ensure your network allows webhook connections")
        print("4. ✓ Try running without webhook if connection issues persist")
    
    return result

def generate_custom_lofi(prompt, instrumental=True):
    """Generate custom lofi track"""
    
    api = MusicGPTAPI()
    
    print(f"🎵 Custom LoFi Generation with MusicGPT")
    print(f"📝 Prompt: {prompt}")
    print(f"🎼 Instrumental: {instrumental}")
    
    result = api.generate_music(
        prompt=prompt,
        make_instrumental=instrumental,
        use_webhook=True
    )
    
    return result

if __name__ == "__main__":
    print("🎵 MusicGPT API Test - Lofi Music Generation")
    print("=" * 60)
    print("📋 Setup:")
    print("1. Get API key: https://musicgpt.com/")
    print("2. Set environment: set MUSICGPT_API_KEY=your-key-here")
    print("3. Ensure you have credits in your account")
    print("4. Allow incoming connections on port 8000 for webhook")
    print()
    
    # Run the test
    test_musicgpt_lofi()
    
    # Uncomment to test custom generation:
    # generate_custom_lofi("Dreamy lofi beats with saxophone and rain sounds, perfect for late night studying", True)