import requests
import re
import json
import uuid
import os
from urllib.parse import unquote

class TikTokDownloader:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Linux; Android 5.0; SM-G900P Build/LRX21T) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Mobile Safari/537.36',
            'Referer': 'https://www.tiktok.com/',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9',
        })

    def get_content(self, url):
        """Get content from URL"""
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return response.text
        except Exception as e:
            raise Exception(f"Failed to get content: {str(e)}")

    def extract_video_info(self, url):
        """Extract video information from TikTok URL"""
        try:
            content = self.get_content(url)
            
            # Look for JSON data in the page
            json_pattern = r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>'
            json_match = re.search(json_pattern, content, re.DOTALL)
            
            if json_match:
                try:
                    json_data = json.loads(json_match.group(1))
                    # Navigate through the JSON structure to find video data
                    props = json_data.get('props', {})
                    page_props = props.get('pageProps', {})
                    item_info = page_props.get('itemInfo', {})
                    item_struct = item_info.get('itemStruct', {})
                    
                    if item_struct:
                        video_info = {
                            'title': item_struct.get('desc', 'TikTok Video'),
                            'video_url': None,
                            'thumbnail': None,
                            'duration': None
                        }
                        
                        # Extract video URL
                        video_data = item_struct.get('video', {})
                        if video_data:
                            play_addr = video_data.get('playAddr')
                            if play_addr:
                                video_info['video_url'] = play_addr
                            
                            # Get thumbnail
                            cover = video_data.get('cover')
                            if cover:
                                video_info['thumbnail'] = cover
                            
                            # Get duration
                            duration = video_data.get('duration')
                            if duration:
                                video_info['duration'] = duration / 1000  # Convert to seconds
                        
                        return video_info
                except json.JSONDecodeError:
                    pass
            
            # Fallback method - look for downloadAddr pattern
            download_addr_pattern = r'"downloadAddr":"([^"]+)"'
            match = re.search(download_addr_pattern, content)
            
            if match:
                video_url = match.group(1)
                # Decode URL
                video_url = video_url.replace('\\u002F', '/')
                video_url = unquote(video_url)
                
                return {
                    'title': 'TikTok Video',
                    'video_url': video_url,
                    'thumbnail': None,
                    'duration': None
                }
            
            raise Exception("Could not extract video information")
            
        except Exception as e:
            raise Exception(f"Failed to extract video info: {str(e)}")

    def get_video_key(self, playable_url):
        """Get video key from playable URL"""
        try:
            headers = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept-Language': 'en-US,en;q=0.9',
                'Range': 'bytes=0-200000'
            }
            
            response = self.session.get(playable_url, headers=headers, timeout=30)
            content = response.text
            
            # Extract key from content
            if 'vid:' in content:
                key_match = re.search(r'vid:([^%]+)', content)
                if key_match:
                    return key_match.group(1).strip()
            
            return ""
        except Exception:
            return ""

    def download_video(self, video_url, output_dir='downloads'):
        """Download video from URL"""
        try:
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            headers = {
                'Range': 'bytes=0-',
                'User-Agent': 'okhttp',
                'Referer': 'https://www.tiktok.com/',
            }
            
            response = self.session.get(video_url, headers=headers, stream=True, timeout=60)
            response.raise_for_status()
            
            # Generate unique filename
            filename = f"tiktok_{uuid.uuid4().hex[:8]}.mp4"
            filepath = os.path.join(output_dir, filename)
            
            # Download the file
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            return {
                'success': True,
                'filename': filename,
                'filepath': filepath,
                'filesize': os.path.getsize(filepath)
            }
            
        except Exception as e:
            raise Exception(f"Failed to download video: {str(e)}")

    def process_tiktok_url(self, url, output_dir='downloads'):
        """Main method to process TikTok URL and download video"""
        try:
            # Extract video information
            video_info = self.extract_video_info(url)
            
            if not video_info.get('video_url'):
                raise Exception("Could not find video download URL")
            
            # Download the video
            download_result = self.download_video(video_info['video_url'], output_dir)
            
            # Combine results
            result = {
                **video_info,
                **download_result
            }
            
            return result
            
        except Exception as e:
            raise Exception(f"Failed to process TikTok URL: {str(e)}")

# Example usage
if __name__ == "__main__":
    downloader = TikTokDownloader()
    
    # Test URL (replace with actual TikTok URL)
    test_url = "https://www.tiktok.com/@username/video/1234567890123456789"
    
    try:
        result = downloader.process_tiktok_url(test_url)
        print("Download successful!")
        print(f"Title: {result['title']}")
        print(f"Filename: {result['filename']}")
        print(f"File size: {result['filesize']} bytes")
    except Exception as e:
        print(f"Error: {e}")