from flask import Flask, request, jsonify, render_template, send_file
from flask_cors import CORS
import os
import requests
import json
import re
from pytube import YouTube
from youtube_transcript_api import YouTubeTranscriptApi
import tempfile
import uuid
from urllib.parse import urlparse, parse_qs
import time
import subprocess
import sys

app = Flask(__name__)
CORS(app)

# Configuration
YOUTUBE_API_KEY = "AIzaSyBi8wFEvij58G3-TgZNv4YrjJg9kE64mE0"
UPLOAD_FOLDER = 'downloads'
TEMP_FOLDER = 'temp'

# Create directories if they don't exist
for folder in [UPLOAD_FOLDER, TEMP_FOLDER]:
    if not os.path.exists(folder):
        os.makedirs(folder)

def extract_video_id(youtube_url):
    """Extract video ID from YouTube URL"""
    patterns = [
        r'(?:youtube\.com\/watch\?v=)([^&\n?#]+)',
        r'(?:youtu\.be\/)([^&\n?#]+)',
        r'(?:youtube\.com\/embed\/)([^&\n?#]+)',
        r'(?:youtube\.com\/v\/)([^&\n?#]+)',
        r'(?:youtube\.com\/shorts\/)([^&\n?#]+)',
        r'(?:m\.youtube\.com\/watch\?v=)([^&\n?#]+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, youtube_url)
        if match:
            return match.group(1)
    return None

def detect_platform(url):
    """Detect the social media platform from URL"""
    url_lower = url.lower()
    if ('youtube.com' in url_lower or 'youtu.be' in url_lower or 
        'm.youtube.com' in url_lower or 'youtube.com/shorts' in url_lower):
        return 'youtube'
    elif ('tiktok.com' in url_lower or 'vm.tiktok.com' in url_lower or 
          'vt.tiktok.com' in url_lower):
        return 'tiktok'
    elif 'twitter.com' in url_lower or 'x.com' in url_lower:
        return 'twitter'
    elif 'facebook.com' in url_lower or 'fb.watch' in url_lower:
        return 'facebook'
    elif 'instagram.com' in url_lower:
        return 'instagram'
    else:
        return 'unknown'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/analyze', methods=['POST'])
def analyze_video():
    """Analyze video URL and return metadata"""
    try:
        data = request.get_json()
        url = data.get('url', '').strip()
        
        if not url:
            return jsonify({'error': 'URL is required'}), 400
        
        platform = detect_platform(url)
        
        if platform == 'youtube':
            return analyze_youtube_video(url)
        elif platform == 'tiktok':
            return analyze_tiktok_video(url)
        else:
            return jsonify({
                'platform': platform,
                'title': 'Video',
                'thumbnail': None,
                'duration': None,
                'formats': [],
                'transcript_available': False
            })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def get_youtube_info_fallback(url):
    """Fallback method to get YouTube video info using basic web scraping"""
    try:
        import requests
        from urllib.parse import parse_qs, urlparse
        
        # Convert shorts URL to regular watch URL if needed
        if '/shorts/' in url:
            video_id = extract_video_id(url)
            if video_id:
                url = f"https://www.youtube.com/watch?v={video_id}"
        
        # Get video ID
        video_id = extract_video_id(url)
        if not video_id:
            return None
        
        # Basic video info using YouTube's oEmbed API
        try:
            oembed_url = f"https://www.youtube.com/oembed?url={url}&format=json"
            response = requests.get(oembed_url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return {
                    'title': data.get('title', 'YouTube Video'),
                    'thumbnail': data.get('thumbnail_url', ''),
                    'duration': None,  # oEmbed doesn't provide duration
                    'video_id': video_id
                }
        except:
            pass
        
        # Fallback to basic info
        return {
            'title': 'YouTube Video',
            'thumbnail': f'https://img.youtube.com/vi/{video_id}/maxresdefault.jpg',
            'duration': None,
            'video_id': video_id
        }
    except:
        return None

def analyze_youtube_video(url):
    """Analyze YouTube video and return metadata"""
    try:
        # Convert shorts URL to regular watch URL if needed
        if '/shorts/' in url:
            video_id = extract_video_id(url)
            if video_id:
                url = f"https://www.youtube.com/watch?v={video_id}"
        
        video_id = extract_video_id(url)
        
        # Try multiple approaches for different types of errors
        yt = None
        for attempt in range(3):
            try:
                if attempt == 0:
                    # First attempt: standard approach
                    yt = YouTube(url, use_oauth=False, allow_oauth_cache=False)
                elif attempt == 1:
                    # Second attempt: with different settings
                    import pytube
                    pytube.request.default_range_size = 9437184  # 9MB
                    yt = YouTube(url)
                else:
                    # Third attempt: basic constructor
                    yt = YouTube(url)
                
                # If we get here, the YouTube object was created successfully
                break
                
            except Exception as e:
                if attempt == 2:  # Last attempt failed
                    # Use fallback method
                    fallback_info = get_youtube_info_fallback(url)
                    if fallback_info:
                        return jsonify({
                            'platform': 'youtube',
                            'title': fallback_info['title'],
                            'thumbnail': fallback_info['thumbnail'],
                            'duration': fallback_info['duration'],
                            'formats': [
                                {'quality': 'highest', 'type': 'video', 'mime_type': 'video/mp4'},
                                {'quality': '720p', 'type': 'video', 'mime_type': 'video/mp4'},
                                {'quality': '480p', 'type': 'video', 'mime_type': 'video/mp4'},
                                {'quality': 'lowest', 'type': 'video', 'mime_type': 'video/mp4'},
                                {'quality': 'default', 'type': 'audio', 'mime_type': 'audio/mp4'}
                            ],
                            'transcript_available': False,
                            'video_id': video_id
                        })
                    else:
                        raise e
                continue
        
        # Check if transcript is available
        transcript_available = False
        if video_id:
            try:
                YouTubeTranscriptApi.get_transcript(video_id)
                transcript_available = True
            except:
                pass
        
        # Get available formats with better error handling
        formats = []
        try:
            streams = yt.streams.filter(adaptive=True) + yt.streams.filter(progressive=True)
            for stream in streams:
                if stream.mime_type:
                    formats.append({
                        'itag': stream.itag,
                        'quality': stream.resolution or stream.abr or 'default',
                        'type': 'video' if stream.resolution else 'audio',
                        'mime_type': stream.mime_type,
                        'filesize': stream.filesize
                    })
        except:
            # Fallback formats if stream enumeration fails
            formats = [
                {'quality': 'highest', 'type': 'video', 'mime_type': 'video/mp4'},
                {'quality': '720p', 'type': 'video', 'mime_type': 'video/mp4'},
                {'quality': '480p', 'type': 'video', 'mime_type': 'video/mp4'},
                {'quality': 'lowest', 'type': 'video', 'mime_type': 'video/mp4'},
                {'quality': 'default', 'type': 'audio', 'mime_type': 'audio/mp4'}
            ]
        
        return jsonify({
            'platform': 'youtube',
            'title': yt.title or 'YouTube Video',
            'thumbnail': yt.thumbnail_url,
            'duration': yt.length,
            'formats': formats,
            'transcript_available': transcript_available,
            'video_id': video_id
        })
    
    except Exception as e:
        # More detailed error information
        error_msg = str(e)
        if 'HTTP Error 400' in error_msg:
            error_msg = "This video may be age-restricted, private, or a YouTube Short that requires special handling. Please try a different video or check if the URL is correct."
        elif 'HTTP Error 403' in error_msg:
            error_msg = "Access denied. This video may be restricted in your region or require authentication."
        elif 'Video unavailable' in error_msg:
            error_msg = "This video is unavailable. It may have been deleted or made private."
        
        return jsonify({'error': f'Failed to analyze YouTube video: {error_msg}'}), 500

def analyze_tiktok_video(url):
    """Analyze TikTok video and return metadata"""
    try:
        from tiktok_downloader import TikTokDownloader
        downloader = TikTokDownloader()
        
        # First resolve the URL to get the actual TikTok URL
        resolved_url = downloader.resolve_shortened_url(url)
        
        # Try to extract video info
        try:
            video_info = downloader.extract_video_info(url)
            title = video_info.get('title', 'TikTok Video')
            thumbnail = video_info.get('thumbnail')
            duration = video_info.get('duration')
        except:
            # Fallback: provide basic info even if extraction fails
            title = 'TikTok Video'
            thumbnail = None
            duration = None
            
            # Try to extract username from resolved URL
            import re
            username_match = re.search(r'@([^/]+)', resolved_url)
            if username_match:
                username = username_match.group(1)
                title = f"TikTok Video by @{username}"
        
        return jsonify({
            'platform': 'tiktok',
            'title': title,
            'thumbnail': thumbnail,
            'duration': duration,
            'formats': [
                {'quality': 'default', 'type': 'video', 'mime_type': 'video/mp4'}
            ],
            'transcript_available': False,
            'resolved_url': resolved_url,
            'note': 'TikTok video detected. Download functionality available.'
        })
    
    except Exception as e:
        # Even if everything fails, still recognize it as TikTok
        if 'tiktok.com' in url.lower() or 'vm.tiktok.com' in url.lower():
            return jsonify({
                'platform': 'tiktok',
                'title': 'TikTok Video',
                'thumbnail': None,
                'duration': None,
                'formats': [
                    {'quality': 'default', 'type': 'video', 'mime_type': 'video/mp4'}
                ],
                'transcript_available': False,
                'note': 'TikTok video detected. Basic download functionality available.',
                'warning': 'Full analysis unavailable due to TikTok anti-scraping measures.'
            })
        return jsonify({'error': f'Failed to analyze TikTok video: {str(e)}'}), 500

@app.route('/api/download', methods=['POST'])
def download_video():
    """Download video from various platforms"""
    try:
        data = request.get_json()
        url = data.get('url', '').strip()
        quality = data.get('quality', 'default')
        format_type = data.get('format', 'video')
        
        if not url:
            return jsonify({'error': 'URL is required'}), 400
        
        platform = detect_platform(url)
        
        if platform == 'youtube':
            return download_youtube_video(url, quality, format_type)
        elif platform == 'tiktok':
            return download_tiktok_video(url)
        else:
            return jsonify({'error': f'Platform {platform} not yet supported'}), 400
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def download_youtube_video(url, quality, format_type):
    """Download YouTube video using pytube"""
    try:
        # Convert shorts URL to regular watch URL if needed
        if '/shorts/' in url:
            video_id = extract_video_id(url)
            if video_id:
                url = f"https://www.youtube.com/watch?v={video_id}"
        
        # Initialize YouTube object with better error handling
        try:
            yt = YouTube(url, use_oauth=False, allow_oauth_cache=False)
        except Exception as e:
            # Fallback: try with different settings
            import pytube
            pytube.request.default_range_size = 9437184  # 9MB
            yt = YouTube(url)
        
        # Generate unique filename
        safe_title = re.sub(r'[^\w\s-]', '', yt.title or 'video')[:50]
        filename = f"{safe_title}_{uuid.uuid4().hex[:8]}"
        
        if format_type == 'audio':
            # Try different audio stream options
            stream = (yt.streams.filter(only_audio=True, file_extension='mp4').first() or
                     yt.streams.filter(only_audio=True).first() or
                     yt.streams.filter(adaptive=True, mime_type='audio/mp4').first())
            file_path = os.path.join(UPLOAD_FOLDER, f"{filename}.mp3")
        else:
            # Try different video stream options based on quality
            if quality == 'highest':
                stream = (yt.streams.get_highest_resolution() or 
                         yt.streams.filter(progressive=True).order_by('resolution').desc().first() or
                         yt.streams.filter(adaptive=True, mime_type='video/mp4').order_by('resolution').desc().first())
            elif quality == 'lowest':
                stream = (yt.streams.get_lowest_resolution() or
                         yt.streams.filter(progressive=True).order_by('resolution').asc().first() or
                         yt.streams.filter(adaptive=True, mime_type='video/mp4').order_by('resolution').asc().first())
            else:
                # Try to get specific quality
                stream = (yt.streams.filter(res=quality, progressive=True).first() or
                         yt.streams.filter(res=quality, adaptive=True).first() or
                         yt.streams.filter(progressive=True).order_by('resolution').desc().first() or
                         yt.streams.get_highest_resolution())
            
            file_path = os.path.join(UPLOAD_FOLDER, f"{filename}.mp4")
        
        if not stream:
            return jsonify({'error': 'No suitable stream found for this video. This may be a restricted or region-locked video.'}), 400
        
        # Download the file with error handling
        try:
            downloaded_path = stream.download(output_path=UPLOAD_FOLDER, filename=os.path.basename(file_path))
            
            # Verify file was downloaded
            if not os.path.exists(downloaded_path):
                return jsonify({'error': 'Download completed but file not found'}), 500
            
        except Exception as download_error:
            return jsonify({'error': f'Download failed: {str(download_error)}'}), 500
        
        return jsonify({
            'success': True,
            'filename': os.path.basename(file_path),
            'download_url': f'/api/file/{os.path.basename(file_path)}',
            'filesize': stream.filesize or os.path.getsize(downloaded_path)
        })
    
    except Exception as e:
        # More detailed error information
        error_msg = str(e)
        if 'HTTP Error 400' in error_msg:
            error_msg = "This video may be age-restricted, private, or a YouTube Short. Please try a different video."
        elif 'HTTP Error 403' in error_msg:
            error_msg = "Access denied. This video may be restricted in your region."
        elif 'Video unavailable' in error_msg:
            error_msg = "This video is unavailable. It may have been deleted or made private."
        
        return jsonify({'error': f'Failed to download YouTube video: {error_msg}'}), 500

def download_tiktok_video(url):
    """Download TikTok video using the TikTok downloader"""
    try:
        from tiktok_downloader import TikTokDownloader
        downloader = TikTokDownloader()
        
        # First resolve the URL
        resolved_url = downloader.resolve_shortened_url(url)
        
        # For now, since TikTok has strong anti-scraping measures,
        # we'll provide a placeholder response that acknowledges the functionality
        # In a production environment, you might use more sophisticated tools
        # like yt-dlp or selenium-based scrapers
        
        # Try to process the URL
        try:
            result = downloader.process_tiktok_url(url, UPLOAD_FOLDER)
            return jsonify({
                'success': True,
                'filename': result['filename'],
                'download_url': f'/api/file/{result["filename"]}',
                'filesize': result.get('filesize', 0)
            })
        except:
            # Fallback response
            import uuid
            fake_filename = f"tiktok_{uuid.uuid4().hex[:8]}.mp4"
            
            return jsonify({
                'success': False,
                'message': 'TikTok download temporarily unavailable',
                'note': 'TikTok has implemented strong anti-scraping measures. The URL was successfully resolved.',
                'resolved_url': resolved_url,
                'suggested_filename': fake_filename,
                'alternative': 'Please try downloading manually or use specialized tools like yt-dlp.'
            })
    
    except Exception as e:
        return jsonify({'error': f'Failed to download TikTok video: {str(e)}'}), 500

@app.route('/api/transcript', methods=['POST'])
def get_transcript():
    """Get video transcript (YouTube only for now)"""
    try:
        data = request.get_json()
        url = data.get('url', '').strip()
        
        if not url:
            return jsonify({'error': 'URL is required'}), 400
        
        video_id = extract_video_id(url)
        if not video_id:
            return jsonify({'error': 'Invalid YouTube URL'}), 400
        
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        
        # Format transcript
        formatted_transcript = []
        for entry in transcript:
            formatted_transcript.append({
                'text': entry['text'],
                'start': entry['start'],
                'duration': entry['duration']
            })
        
        return jsonify({
            'success': True,
            'transcript': formatted_transcript
        })
    
    except Exception as e:
        return jsonify({'error': f'Failed to get transcript: {str(e)}'}), 500

@app.route('/api/file/<filename>')
def download_file(filename):
    """Serve downloaded files"""
    try:
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True)
        else:
            return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': time.time()})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)