"""
Instagram Video Downloader API
Flask implementation mimicking the Node.js Express server
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
from instagram_downloader import snapsave

# Create Flask app
app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route("/", methods=['GET'])
def hello_world():
    """Root endpoint"""
    return jsonify({"message": "Hello World!"})

@app.route("/igdl", methods=['GET'])
def instagram_download():
    """Instagram video download endpoint - matches Node.js /igdl route"""
    try:
        url = request.args.get('url')
        
        if not url:
            return jsonify({"error": "URL parameter is missing"}), 400
        
        # Use the snapsave function (Python equivalent)
        result = snapsave(url)
        
        if result.get('success'):
            return jsonify({
                "url": result['url'],
                "title": result.get('title', 'Instagram Video'),
                "thumbnail": result.get('thumbnail'),
                "success": True
            })
        else:
            return jsonify({
                "error": result.get('error', 'Failed to extract video'),
                "success": False
            }), 500
        
    except Exception as err:
        logger.error(f"Error in /igdl: {str(err)}")
        return jsonify({"error": "Internal Server Error"}), 500

@app.route("/api/instagram/analyze", methods=['POST'])
def analyze_instagram():
    """Enhanced Instagram analysis endpoint for VideoHQ Pro integration"""
    try:
        data = request.get_json()
        url = data.get('url')
        
        if not url:
            return jsonify({"error": "URL is required"}), 400
        
        from instagram_downloader import InstagramDownloader
        downloader = InstagramDownloader()
        
        # Extract video information
        video_info = downloader.extract_video_info(url)
        
        return jsonify({
            "success": True,
            "platform": "instagram",
            "title": video_info.get('title', 'Instagram Video'),
            "video_url": video_info.get('video_url'),
            "thumbnail": video_info.get('thumbnail'),
            "duration": video_info.get('duration'),
            "available_qualities": [
                {"resolution": "480p", "type": "mobile"},
                {"resolution": "720p", "type": "hd"},
                {"resolution": "1080p", "type": "full_hd"}
            ],
            "enhancement_potential": "Good - Instagram videos benefit from AI upscaling"
        })
        
    except Exception as err:
        logger.error(f"Error in Instagram analysis: {str(err)}")
        return jsonify({
            "error": str(err),
            "success": False
        }), 500

@app.route("/api/instagram/download", methods=['POST'])
def download_instagram():
    """Instagram video download endpoint with full processing"""
    try:
        data = request.get_json()
        url = data.get('url')
        quality = data.get('quality', '720p')
        
        if not url:
            return jsonify({"error": "URL is required"}), 400
        
        from instagram_downloader import InstagramDownloader
        downloader = InstagramDownloader()
        
        # Process the Instagram URL and download
        result = downloader.process_instagram_url(url)
        
        return jsonify({
            "success": True,
            "title": result['title'],
            "filename": result['filename'],
            "filesize": result['filesize'],
            "download_url": f"/download/{result['filename']}",
            "quality": quality,
            "platform": "instagram"
        })
        
    except Exception as err:
        logger.error(f"Error in Instagram download: {str(err)}")
        return jsonify({
            "error": str(err),
            "success": False
        }), 500

@app.route("/download/<filename>", methods=['GET'])
def serve_download(filename):
    """Serve downloaded files"""
    try:
        from flask import send_file
        import os
        
        filepath = os.path.join('downloads', filename)
        if os.path.exists(filepath):
            return send_file(filepath, as_attachment=True)
        else:
            return jsonify({"error": "File not found"}), 404
            
    except Exception as err:
        logger.error(f"Error serving file: {str(err)}")
        return jsonify({"error": "File serving error"}), 500

@app.route("/health", methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "Instagram Video Downloader API",
        "version": "1.0.0"
    })

if __name__ == "__main__":
    print("Instagram Video Downloader API")
    print("Starting server at http://localhost:3000")
    print("Endpoints:")
    print("  GET  /           - Hello World")
    print("  GET  /igdl       - Instagram Download (Node.js compatible)")
    print("  POST /api/instagram/analyze   - Video Analysis")
    print("  POST /api/instagram/download  - Video Download")
    print("  GET  /health     - Health Check")
    
    # Run on port 3000 to match Node.js server
    app.run(debug=True, host='0.0.0.0', port=3000)