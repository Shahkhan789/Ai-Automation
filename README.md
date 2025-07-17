# Universal Video Downloader

A modern, feature-rich web application for downloading videos from multiple social media platforms including YouTube, TikTok, Twitter, Facebook, Instagram, and more. Built with Flask, featuring a beautiful UI with animations and comprehensive functionality.

## 🌟 Features

### Supported Platforms
- **YouTube** - Full support with quality options and transcript extraction
- **TikTok** - Video download with metadata extraction
- **Twitter** - Video download support
- **Facebook** - Video download support
- **Instagram** - Video/photo download support
- **More platforms** - Easily extensible architecture

### Key Features
- 🎨 **Modern UI/UX** - Beautiful, responsive design with smooth animations
- 📱 **Mobile Responsive** - Works perfectly on all devices
- 🎥 **Multiple Formats** - Download videos or extract audio only
- 📝 **Transcript Support** - Extract and download video transcripts (YouTube)
- 🔄 **Real-time Progress** - Visual download progress indicators
- 📊 **Video Analysis** - Preview thumbnails, duration, and file sizes
- 🎯 **Quality Options** - Choose from multiple quality levels
- 💾 **Batch Processing** - Support for multiple downloads
- ⚡ **Fast & Reliable** - Optimized for performance

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd universal-video-downloader
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Create required directories**
   ```bash
   mkdir downloads temp
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Access the application**
   Open your browser and go to `http://localhost:5000`

## 📖 Usage

### Basic Usage

1. **Paste Video URL**
   - Copy any supported video URL
   - Paste it into the input field
   - Click "Analyze" or press Enter

2. **Choose Options**
   - Select video or audio-only format
   - Choose quality level
   - Preview video information

3. **Download**
   - Click "Download Video"
   - Monitor progress
   - Access downloaded file

### Advanced Features

#### Transcript Extraction (YouTube)
- Automatically detects if transcripts are available
- View transcripts in a modal dialog
- Copy to clipboard or download as text file
- Timestamps included for easy navigation

#### Quality Selection
- **Highest Quality** - Best available resolution
- **720p HD** - High definition
- **480p** - Standard definition
- **360p** - Mobile friendly
- **Lowest Quality** - Smallest file size

#### Format Options
- **Video** - Complete video with audio
- **Audio Only** - Extract audio track (MP3)

## 🛠️ Configuration

### YouTube API
The application uses the YouTube Data API for enhanced functionality. The API key is already configured, but you can update it in `app.py`:

```python
YOUTUBE_API_KEY = "your-api-key-here"
```

### Environment Variables
Create a `.env` file for custom configurations:

```env
FLASK_ENV=development
UPLOAD_FOLDER=downloads
TEMP_FOLDER=temp
```

### Storage Configuration
Downloaded files are stored in the `downloads` folder by default. You can change this in `app.py`:

```python
UPLOAD_FOLDER = 'your-custom-folder'
```

## 🏗️ Architecture

### Backend (Flask)
- **app.py** - Main Flask application
- **tiktok_downloader.py** - TikTok-specific downloading logic
- **API Endpoints** - RESTful API for frontend communication

### Frontend
- **HTML5** - Semantic markup with accessibility features
- **CSS3** - Modern styling with animations and responsive design
- **JavaScript** - Dynamic interactions and API communication

### File Structure
```
universal-video-downloader/
├── app.py                 # Main Flask application
├── tiktok_downloader.py   # TikTok downloader implementation
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── templates/
│   └── index.html        # Main HTML template
├── static/
│   ├── css/
│   │   └── style.css     # Stylesheet
│   ├── js/
│   │   └── app.js        # JavaScript application
│   └── images/           # Static images
├── downloads/            # Downloaded files
└── temp/                # Temporary files
```

## 🔧 API Documentation

### Analyze Video
**POST** `/api/analyze`

Analyze a video URL and return metadata.

```json
{
  "url": "https://www.youtube.com/watch?v=example"
}
```

**Response:**
```json
{
  "platform": "youtube",
  "title": "Video Title",
  "thumbnail": "https://...",
  "duration": 180,
  "formats": [...],
  "transcript_available": true
}
```

### Download Video
**POST** `/api/download`

Download a video with specified options.

```json
{
  "url": "https://www.youtube.com/watch?v=example",
  "quality": "720p",
  "format": "video"
}
```

### Get Transcript
**POST** `/api/transcript`

Extract video transcript (YouTube only).

```json
{
  "url": "https://www.youtube.com/watch?v=example"
}
```

### Health Check
**GET** `/api/health`

Check application status.

## 🎨 UI Components

### Animations
- **Fade In/Out** - Smooth element transitions
- **Scale Effects** - Interactive button feedback
- **Progress Bars** - Visual download progress
- **Background Blobs** - Animated background elements

### Responsive Design
- **Mobile First** - Optimized for mobile devices
- **Tablet Support** - Perfect tablet experience
- **Desktop Enhanced** - Full desktop functionality

### Accessibility
- **Keyboard Navigation** - Full keyboard support
- **Screen Reader** - ARIA labels and semantic HTML
- **High Contrast** - Accessible color schemes

## 🔒 Security Features

- **Input Validation** - URL and parameter validation
- **File Type Checking** - Secure file handling
- **Rate Limiting** - Protection against abuse
- **CORS Configuration** - Proper cross-origin handling

## 🐛 Troubleshooting

### Common Issues

1. **"Module not found" error**
   ```bash
   pip install -r requirements.txt
   ```

2. **"Permission denied" error**
   ```bash
   chmod 755 downloads temp
   ```

3. **"No video found" error**
   - Check if the URL is valid
   - Ensure the video is publicly accessible
   - Try a different quality setting

4. **YouTube download fails**
   - Check if pytube is up to date
   - Some videos may be region-restricted

### Debug Mode
Enable debug mode for detailed error messages:

```python
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
```

## 📊 Performance

### Optimization Features
- **Lazy Loading** - Load content as needed
- **Caching** - Intelligent caching strategies
- **Compression** - Optimized file sizes
- **Async Operations** - Non-blocking downloads

### Resource Usage
- **Memory** - Efficient memory management
- **Storage** - Automatic cleanup of temporary files
- **Network** - Optimized API calls

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

### Code Style
- Follow PEP 8 for Python code
- Use meaningful variable names
- Comment complex logic
- Keep functions focused and small

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🔗 Links

- **Repository**: [GitHub Repository]
- **Issues**: [Report Issues]
- **Documentation**: [Full Documentation]

## 🙏 Acknowledgments

- **pytube** - YouTube downloading functionality
- **Flask** - Web framework
- **Font Awesome** - Icons
- **Inter Font** - Typography

---

**Made with ❤️ for the community**