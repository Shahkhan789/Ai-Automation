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
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0',
        })

    def resolve_shortened_url(self, url):
        """Resolve shortened TikTok URLs (vm.tiktok.com, vt.tiktok.com, etc.) to actual URLs"""
        try:
            # Check if it's a shortened URL
            shortened_domains = ['vm.tiktok.com', 'vt.tiktok.com', 'm.tiktok.com']
            
            if any(domain in url for domain in shortened_domains):
                # Follow redirects to get the actual URL
                headers = {
                    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Mobile/15E148 Safari/604.1',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Accept-Encoding': 'gzip, deflate',
                    'Connection': 'keep-alive',
                }
                
                response = self.session.get(url, headers=headers, allow_redirects=True, timeout=15)
                final_url = response.url
                
                print(f"URL Resolution: {url} -> {final_url}")
                return final_url
            
            return url
        except Exception as e:
            print(f"Failed to resolve URL {url}: {str(e)}")
            # If resolution fails, try with the original URL
            return url

    def get_content(self, url):
        """Get content from URL"""
        try:
            # First resolve shortened URLs
            resolved_url = self.resolve_shortened_url(url)
            response = self.session.get(resolved_url, timeout=30)
            response.raise_for_status()
            return response.text
        except Exception as e:
            raise Exception(f"Failed to get content: {str(e)}")

    def extract_video_info(self, url):
        """Extract video information from TikTok URL"""
        try:
            # First resolve any shortened URLs
            resolved_url = self.resolve_shortened_url(url)
            print(f"Original URL: {url}")
            print(f"Resolved URL: {resolved_url}")
            
            content = self.get_content(resolved_url)
            
            # Try multiple patterns to extract video information
            video_info = None
            
            # Method 1: Look for JSON data in __NEXT_DATA__
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
                        
                        if video_info['video_url']:
                            return video_info
                except json.JSONDecodeError:
                    pass
            
            # Method 2: Look for SIGI_STATE data
            sigi_pattern = r'<script id="SIGI_STATE" type="application/json">(.*?)</script>'
            sigi_match = re.search(sigi_pattern, content, re.DOTALL)
            
            if sigi_match:
                try:
                    sigi_data = json.loads(sigi_match.group(1))
                    # Navigate through SIGI_STATE structure
                    app_context = sigi_data.get('AppContext', {})
                    item_module = sigi_data.get('ItemModule', {})
                    
                    for key, item in item_module.items():
                        if isinstance(item, dict) and 'video' in item:
                            video_data = item.get('video', {})
                            if video_data:
                                video_info = {
                                    'title': item.get('desc', 'TikTok Video'),
                                    'video_url': video_data.get('playAddr', ''),
                                    'thumbnail': video_data.get('cover', ''),
                                    'duration': video_data.get('duration', 0) / 1000 if video_data.get('duration') else None
                                }
                                if video_info['video_url']:
                                    return video_info
                except json.JSONDecodeError:
                    pass
            
            # Method 3: Look for video data in various script tags
            script_patterns = [
                r'window\.__INITIAL_STATE__\s*=\s*({.*?});',
                r'window\.__DEFAULT_SCOPE__\s*=\s*({.*?});',
                r'window\.SIGI_STATE\s*=\s*({.*?});'
            ]
            
            for pattern in script_patterns:
                matches = re.findall(pattern, content, re.DOTALL)
                for match in matches:
                    try:
                        data = json.loads(match)
                        # Look for video information in the data structure
                        video_info = self.extract_from_data_structure(data)
                        if video_info and video_info.get('video_url'):
                            return video_info
                    except:
                        continue
            
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
            
            # Final fallback - try to extract any video-like URLs
            video_url_patterns = [
                r'"playAddr":"([^"]+)"',
                r'"downloadAddr":"([^"]+)"',
                r'"playURL":"([^"]+)"',
                r'https://[^"]*\.mp4[^"]*'
            ]
            
            for pattern in video_url_patterns:
                matches = re.findall(pattern, content)
                for match in matches:
                    if isinstance(match, str) and ('tiktokcdn' in match or 'tiktokvideo' in match or '.mp4' in match):
                        video_url = match.replace('\\u002F', '/').replace('\\', '')
                        video_url = unquote(video_url)
                        
                        # Extract title if possible
                        title_patterns = [
                            r'"desc":"([^"]+)"',
                            r'"title":"([^"]+)"',
                            r'<title>([^<]+)</title>'
                        ]
                        
                        title = 'TikTok Video'
                        for title_pattern in title_patterns:
                            title_match = re.search(title_pattern, content)
                            if title_match:
                                title = title_match.group(1)
                                break
                        
                        return {
                            'title': title,
                            'video_url': video_url,
                            'thumbnail': None,
                            'duration': None
                        }
            
            raise Exception("Could not extract video information")
            
        except Exception as e:
            raise Exception(f"Failed to extract video info: {str(e)}")

    def extract_from_data_structure(self, data):
        """Extract video information from nested data structures"""
        try:
            def search_dict(obj, target_keys=['playAddr', 'downloadAddr', 'playURL']):
                """Recursively search for video URLs in nested dictionaries"""
                if isinstance(obj, dict):
                    for key, value in obj.items():
                        if key in target_keys and isinstance(value, str) and value.startswith('http'):
                            # Found a video URL, now look for associated metadata
                            parent_obj = obj
                            return {
                                'video_url': value,
                                'title': parent_obj.get('desc', parent_obj.get('title', 'TikTok Video')),
                                'thumbnail': parent_obj.get('cover', parent_obj.get('thumbnail', '')),
                                'duration': parent_obj.get('duration', 0) / 1000 if parent_obj.get('duration') else None
                            }
                        elif isinstance(value, (dict, list)):
                            result = search_dict(value, target_keys)
                            if result:
                                return result
                elif isinstance(obj, list):
                    for item in obj:
                        result = search_dict(item, target_keys)
                        if result:
                            return result
                return None
            
            return search_dict(data)
        except:
            return None

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
            # First resolve any shortened URLs
            resolved_url = self.resolve_shortened_url(url)
            print(f"Processing TikTok URL: {url}")
            if resolved_url != url:
                print(f"Resolved to: {resolved_url}")
            
            # Extract video information
            video_info = self.extract_video_info(url)
            
            if not video_info.get('video_url'):
                raise Exception("Could not find video download URL")
            
            # Download the video
            download_result = self.download_video(video_info['video_url'], output_dir)
            
            # Combine results
            result = {
                **video_info,
                **download_result,
                'original_url': url,
                'resolved_url': resolved_url
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