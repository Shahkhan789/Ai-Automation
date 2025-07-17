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
    pattern = r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/|youtube\.com\/v\/)([^&\n?#]+)'
    match = re.search(pattern, youtube_url)
    return match.group(1) if match else None

def detect_platform(url):
    """Detect the social media platform from URL"""
    url_lower = url.lower()
    if 'youtube.com' in url_lower or 'youtu.be' in url_lower:
        return 'youtube'
    elif 'tiktok.com' in url_lower:
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

def analyze_youtube_video(url):
    """Analyze YouTube video and return metadata"""
    try:
        yt = YouTube(url)
        video_id = extract_video_id(url)
        
        # Check if transcript is available
        transcript_available = False
        try:
            YouTubeTranscriptApi.get_transcript(video_id)
            transcript_available = True
        except:
            pass
        
        # Get available formats
        formats = []
        for stream in yt.streams:
            if stream.mime_type:
                formats.append({
                    'itag': stream.itag,
                    'quality': stream.resolution or stream.abr,
                    'type': 'video' if stream.resolution else 'audio',
                    'mime_type': stream.mime_type,
                    'filesize': stream.filesize
                })
        
        return jsonify({
            'platform': 'youtube',
            'title': yt.title,
            'thumbnail': yt.thumbnail_url,
            'duration': yt.length,
            'formats': formats,
            'transcript_available': transcript_available,
            'video_id': video_id
        })
    
    except Exception as e:
        return jsonify({'error': f'Failed to analyze YouTube video: {str(e)}'}), 500

def analyze_tiktok_video(url):
    """Analyze TikTok video and return metadata"""
    try:
        from tiktok_downloader import TikTokDownloader
        downloader = TikTokDownloader()
        
        # Extract video info without downloading
        video_info = downloader.extract_video_info(url)
        
        return jsonify({
            'platform': 'tiktok',
            'title': video_info.get('title', 'TikTok Video'),
            'thumbnail': video_info.get('thumbnail'),
            'duration': video_info.get('duration'),
            'formats': [
                {'quality': 'default', 'type': 'video', 'mime_type': 'video/mp4'}
            ],
            'transcript_available': False
        })
    
    except Exception as e:
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
        yt = YouTube(url)
        
        # Generate unique filename
        safe_title = re.sub(r'[^\w\s-]', '', yt.title)[:50]
        filename = f"{safe_title}_{uuid.uuid4().hex[:8]}"
        
        if format_type == 'audio':
            stream = yt.streams.filter(only_audio=True).first()
            file_path = os.path.join(UPLOAD_FOLDER, f"{filename}.mp3")
        else:
            if quality == 'highest':
                stream = yt.streams.get_highest_resolution()
            elif quality == 'lowest':
                stream = yt.streams.get_lowest_resolution()
            else:
                stream = yt.streams.filter(res=quality).first() or yt.streams.get_highest_resolution()
            
            file_path = os.path.join(UPLOAD_FOLDER, f"{filename}.mp4")
        
        if not stream:
            return jsonify({'error': 'No suitable stream found'}), 400
        
        # Download the file
        stream.download(output_path=UPLOAD_FOLDER, filename=os.path.basename(file_path))
        
        return jsonify({
            'success': True,
            'filename': os.path.basename(file_path),
            'download_url': f'/api/file/{os.path.basename(file_path)}',
            'filesize': stream.filesize
        })
    
    except Exception as e:
        return jsonify({'error': f'Failed to download YouTube video: {str(e)}'}), 500

def download_tiktok_video(url):
    """Download TikTok video using the TikTok downloader"""
    try:
        from tiktok_downloader import TikTokDownloader
        downloader = TikTokDownloader()
        
        # Process TikTok URL and download video
        result = downloader.process_tiktok_url(url, UPLOAD_FOLDER)
        
        return jsonify({
            'success': True,
            'filename': result['filename'],
            'download_url': f'/api/file/{result["filename"]}',
            'filesize': result.get('filesize', 0)
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