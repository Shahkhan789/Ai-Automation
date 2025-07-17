"""
Instagram Video Downloader for VideoHQ Pro
Python implementation of snapsave-like functionality
"""

import requests
import re
import json
import uuid
import os
from urllib.parse import urlparse, parse_qs
import logging

logger = logging.getLogger(__name__)

class InstagramDownloader:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Mobile/15E148 Safari/604.1',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })

    def extract_video_info(self, url):
        """Extract Instagram video information and download URL"""
        try:
            # Clean and validate URL
            clean_url = self.clean_instagram_url(url)
            
            # Try multiple extraction methods
            video_info = None
            
            # Method 1: Direct page scraping
            try:
                video_info = self.extract_from_page(clean_url)
                if video_info and video_info.get('video_url'):
                    return video_info
            except Exception as e:
                logger.warning(f"Page scraping failed: {e}")
            
            # Method 2: Instagram embed endpoint
            try:
                video_info = self.extract_from_embed(clean_url)
                if video_info and video_info.get('video_url'):
                    return video_info
            except Exception as e:
                logger.warning(f"Embed extraction failed: {e}")
            
            # Method 3: Instagram oEmbed API
            try:
                video_info = self.extract_from_oembed(clean_url)
                if video_info and video_info.get('video_url'):
                    return video_info
            except Exception as e:
                logger.warning(f"oEmbed extraction failed: {e}")
            
            raise Exception("Could not extract video information from any method")
            
        except Exception as e:
            raise Exception(f"Failed to extract Instagram video info: {str(e)}")

    def clean_instagram_url(self, url):
        """Clean and standardize Instagram URL"""
        # Remove query parameters and ensure proper format
        if 'instagram.com' not in url:
            raise Exception("Invalid Instagram URL")
        
        # Extract post ID pattern
        post_match = re.search(r'instagram\.com/(?:p|reel|tv)/([A-Za-z0-9_-]+)', url)
        if post_match:
            post_id = post_match.group(1)
            return f"https://www.instagram.com/p/{post_id}/"
        
        # For stories and other formats
        if '/stories/' in url:
            return url.split('?')[0]
        
        return url.split('?')[0]

    def extract_from_page(self, url):
        """Extract video info from Instagram page HTML"""
        try:
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            content = response.text
            
            # Look for JSON data in script tags
            json_patterns = [
                r'window\._sharedData\s*=\s*({.*?});',
                r'window\.__additionalDataLoaded\([^,]+,\s*({.*?})\);',
                r'"gql_data":({.*?"video_url".*?})',
            ]
            
            for pattern in json_patterns:
                matches = re.findall(pattern, content, re.DOTALL)
                for match in matches:
                    try:
                        data = json.loads(match)
                        video_info = self.extract_video_from_json(data)
                        if video_info:
                            return video_info
                    except json.JSONDecodeError:
                        continue
            
            # Look for direct video URL patterns
            video_url_patterns = [
                r'"video_url":"([^"]+)"',
                r'"videoUrl":"([^"]+)"',
                r'contentUrl":"([^"]+\.mp4[^"]*)"',
            ]
            
            for pattern in video_url_patterns:
                match = re.search(pattern, content)
                if match:
                    video_url = match.group(1).replace('\\u0026', '&').replace('\\/', '/')
                    
                    # Extract basic metadata
                    title_match = re.search(r'"caption":"([^"]*)"', content)
                    title = title_match.group(1) if title_match else "Instagram Video"
                    
                    return {
                        'title': title[:100] + '...' if len(title) > 100 else title,
                        'video_url': video_url,
                        'thumbnail': None,
                        'duration': None,
                        'platform': 'instagram'
                    }
            
            return None
            
        except Exception as e:
            logger.error(f"Page extraction failed: {e}")
            return None

    def extract_from_embed(self, url):
        """Extract video info from Instagram embed endpoint"""
        try:
            # Convert to embed URL
            post_id = re.search(r'/p/([A-Za-z0-9_-]+)', url)
            if not post_id:
                return None
            
            embed_url = f"https://www.instagram.com/p/{post_id.group(1)}/embed/"
            
            response = self.session.get(embed_url, timeout=15)
            response.raise_for_status()
            content = response.text
            
            # Look for video URL in embed page
            video_patterns = [
                r'"video_url":"([^"]+)"',
                r'src="([^"]*\.mp4[^"]*)"',
            ]
            
            for pattern in video_patterns:
                match = re.search(pattern, content)
                if match:
                    video_url = match.group(1).replace('\\u0026', '&').replace('\\/', '/')
                    
                    return {
                        'title': 'Instagram Video',
                        'video_url': video_url,
                        'thumbnail': None,
                        'duration': None,
                        'platform': 'instagram'
                    }
            
            return None
            
        except Exception as e:
            logger.error(f"Embed extraction failed: {e}")
            return None

    def extract_from_oembed(self, url):
        """Extract video info from Instagram oEmbed API"""
        try:
            oembed_url = f"https://www.instagram.com/oembed/?url={url}&format=json"
            
            response = self.session.get(oembed_url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if 'html' in data:
                html = data['html']
                
                # Extract video URL from embed HTML
                video_match = re.search(r'src="([^"]*\.mp4[^"]*)"', html)
                if video_match:
                    video_url = video_match.group(1)
                    
                    return {
                        'title': data.get('title', 'Instagram Video'),
                        'video_url': video_url,
                        'thumbnail': data.get('thumbnail_url'),
                        'duration': None,
                        'platform': 'instagram'
                    }
            
            return None
            
        except Exception as e:
            logger.error(f"oEmbed extraction failed: {e}")
            return None

    def extract_video_from_json(self, data):
        """Extract video information from JSON data structures"""
        try:
            def search_for_video(obj, path=""):
                """Recursively search for video URLs in nested JSON"""
                if isinstance(obj, dict):
                    # Check for video URL fields
                    for key in ['video_url', 'videoUrl', 'src', 'contentUrl']:
                        if key in obj and isinstance(obj[key], str):
                            if '.mp4' in obj[key] or 'video' in obj[key]:
                                return {
                                    'video_url': obj[key],
                                    'title': obj.get('caption', obj.get('title', 'Instagram Video')),
                                    'thumbnail': obj.get('display_url', obj.get('thumbnail')),
                                    'duration': obj.get('video_duration'),
                                    'platform': 'instagram'
                                }
                    
                    # Recursively search nested objects
                    for key, value in obj.items():
                        result = search_for_video(value, f"{path}.{key}")
                        if result:
                            return result
                
                elif isinstance(obj, list):
                    for i, item in enumerate(obj):
                        result = search_for_video(item, f"{path}[{i}]")
                        if result:
                            return result
                
                return None
            
            return search_for_video(data)
            
        except Exception as e:
            logger.error(f"JSON extraction failed: {e}")
            return None

    def download_video(self, video_url, output_dir='downloads'):
        """Download Instagram video from URL"""
        try:
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            # Use mobile headers for video download
            headers = {
                'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15',
                'Accept': 'video/mp4,video/*;q=0.9,*/*;q=0.8',
                'Referer': 'https://www.instagram.com/',
            }
            
            response = self.session.get(video_url, headers=headers, stream=True, timeout=60)
            response.raise_for_status()
            
            # Generate unique filename
            filename = f"instagram_{uuid.uuid4().hex[:8]}.mp4"
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
            raise Exception(f"Failed to download Instagram video: {str(e)}")

    def process_instagram_url(self, url, output_dir='downloads'):
        """Main method to process Instagram URL and download video"""
        try:
            print(f"Processing Instagram URL: {url}")
            
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
            }
            
            return result
            
        except Exception as e:
            raise Exception(f"Failed to process Instagram URL: {str(e)}")


# Snapsave-like API function for compatibility
def snapsave(url):
    """
    Snapsave-compatible function for Instagram video downloading
    Mimics the Node.js snapsave functionality
    """
    try:
        downloader = InstagramDownloader()
        result = downloader.process_instagram_url(url)
        
        # Return the video URL in snapsave format
        return {
            'url': result['video_url'],
            'title': result.get('title', 'Instagram Video'),
            'thumbnail': result.get('thumbnail'),
            'success': True
        }
        
    except Exception as e:
        logger.error(f"Snapsave extraction failed: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }


# Example usage
if __name__ == "__main__":
    downloader = InstagramDownloader()
    
    # Test URL (replace with actual Instagram URL)
    test_url = "https://www.instagram.com/p/example/"
    
    try:
        result = downloader.process_instagram_url(test_url)
        print("Download successful!")
        print(f"Title: {result['title']}")
        print(f"Filename: {result['filename']}")
        print(f"File size: {result['filesize']} bytes")
    except Exception as e:
        print(f"Error: {e}")