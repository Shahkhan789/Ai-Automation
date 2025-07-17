// Application state
let currentVideoData = null;
let isDownloading = false;

// DOM Elements
const elements = {
    videoUrl: document.getElementById('videoUrl'),
    analyzeBtn: document.getElementById('analyzeBtn'),
    loadingSpinner: document.getElementById('loadingSpinner'),
    videoPreview: document.getElementById('videoPreview'),
    downloadProgress: document.getElementById('downloadProgress'),
    downloadComplete: document.getElementById('downloadComplete'),
    errorMessage: document.getElementById('errorMessage'),
    transcriptModal: document.getElementById('transcriptModal'),
    
    // Preview elements
    thumbnailImg: document.getElementById('thumbnailImg'),
    platformIcon: document.getElementById('platformIcon'),
    platformName: document.getElementById('platformName'),
    videoTitle: document.getElementById('videoTitle'),
    videoDuration: document.getElementById('videoDuration'),
    videoSize: document.getElementById('videoSize'),
    
    // Control elements
    formatTabs: document.querySelectorAll('.format-tab'),
    qualitySelect: document.getElementById('qualitySelect'),
    downloadBtn: document.getElementById('downloadBtn'),
    transcriptBtn: document.getElementById('transcriptBtn'),
    
    // Progress elements
    progressFill: document.getElementById('progressFill'),
    progressPercentage: document.getElementById('progressPercentage'),
    progressStatus: document.getElementById('progressStatus'),
    
    // Success elements
    downloadLink: document.getElementById('downloadLink'),
    
    // Modal elements
    closeModal: document.getElementById('closeModal'),
    transcriptContent: document.getElementById('transcriptContent'),
    copyTranscript: document.getElementById('copyTranscript'),
    downloadTranscript: document.getElementById('downloadTranscript'),
    
    // Error elements
    errorText: document.getElementById('errorText'),
    retryBtn: document.getElementById('retryBtn')
};

// Platform configurations
const platformConfig = {
    youtube: {
        icon: 'fab fa-youtube',
        name: 'YouTube',
        color: '#FF0000'
    },
    tiktok: {
        icon: 'fab fa-tiktok',
        name: 'TikTok',
        color: '#000000'
    },
    twitter: {
        icon: 'fab fa-twitter',
        name: 'Twitter',
        color: '#1DA1F2'
    },
    facebook: {
        icon: 'fab fa-facebook',
        name: 'Facebook',
        color: '#1877F2'
    },
    instagram: {
        icon: 'fab fa-instagram',
        name: 'Instagram',
        color: '#E4405F'
    }
};

// Utility functions
function showElement(element, animationClass = 'fadeInScale') {
    element.classList.remove('hidden');
    element.style.animation = `${animationClass} 0.5s ease-out`;
}

function hideElement(element) {
    element.classList.add('hidden');
}

function hideAllSections() {
    const sections = [
        elements.loadingSpinner,
        elements.videoPreview,
        elements.downloadProgress,
        elements.downloadComplete,
        elements.errorMessage
    ];
    sections.forEach(hideElement);
}

function formatDuration(seconds) {
    if (!seconds) return 'Unknown';
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    
    if (hours > 0) {
        return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }
    return `${minutes}:${secs.toString().padStart(2, '0')}`;
}

function formatFileSize(bytes) {
    if (!bytes) return 'Unknown';
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    if (bytes === 0) return '0 Byte';
    const i = parseInt(Math.floor(Math.log(bytes) / Math.log(1024)));
    return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
}

function showError(message) {
    hideAllSections();
    elements.errorText.textContent = message;
    showElement(elements.errorMessage);
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
        <span>${message}</span>
    `;
    
    // Add to body
    document.body.appendChild(notification);
    
    // Animate in
    setTimeout(() => notification.classList.add('show'), 100);
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => document.body.removeChild(notification), 300);
    }, 3000);
}

// API functions
async function analyzeVideo(url) {
    try {
        const response = await fetch('/api/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ url })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Failed to analyze video');
        }
        
        return data;
    } catch (error) {
        throw new Error(error.message || 'Network error occurred');
    }
}

async function downloadVideo(url, quality, format) {
    try {
        const response = await fetch('/api/download', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
                url, 
                quality, 
                format 
            })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Failed to download video');
        }
        
        return data;
    } catch (error) {
        throw new Error(error.message || 'Network error occurred');
    }
}

async function getTranscript(url) {
    try {
        const response = await fetch('/api/transcript', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ url })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Failed to get transcript');
        }
        
        return data;
    } catch (error) {
        throw new Error(error.message || 'Network error occurred');
    }
}

// Event handlers
async function handleAnalyze() {
    const url = elements.videoUrl.value.trim();
    
    if (!url) {
        showError('Please enter a video URL');
        return;
    }
    
    // Validate URL format
    try {
        new URL(url);
    } catch {
        showError('Please enter a valid URL');
        return;
    }
    
    // Show loading
    hideAllSections();
    showElement(elements.loadingSpinner);
    elements.analyzeBtn.disabled = true;
    elements.analyzeBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Analyzing...';
    
    try {
        const videoData = await analyzeVideo(url);
        currentVideoData = videoData;
        
        // Update preview
        updateVideoPreview(videoData);
        
        // Show preview
        hideAllSections();
        showElement(elements.videoPreview);
        
        showNotification('Video analyzed successfully!', 'success');
        
    } catch (error) {
        showError(error.message);
    } finally {
        elements.analyzeBtn.disabled = false;
        elements.analyzeBtn.innerHTML = '<i class="fas fa-search"></i> Analyze';
    }
}

function updateVideoPreview(data) {
    // Update thumbnail
    if (data.thumbnail) {
        elements.thumbnailImg.src = data.thumbnail;
        elements.thumbnailImg.style.display = 'block';
    } else {
        elements.thumbnailImg.style.display = 'none';
    }
    
    // Update platform badge
    const config = platformConfig[data.platform] || { icon: 'fas fa-video', name: 'Video' };
    elements.platformIcon.className = config.icon;
    elements.platformName.textContent = config.name;
    
    // Update details
    elements.videoTitle.textContent = data.title || 'Video Title';
    elements.videoDuration.innerHTML = `<i class="fas fa-clock"></i> ${formatDuration(data.duration)}`;
    
    // Show additional info for TikTok videos
    if (data.platform === 'tiktok' && data.resolved_url) {
        elements.videoTitle.innerHTML += ` <small style="color: #666; font-size: 0.8em;">(Resolved from short URL)</small>`;
    }
    
    // Update quality options
    updateQualityOptions(data.formats);
    
    // Show/hide transcript button
    if (data.transcript_available) {
        elements.transcriptBtn.classList.remove('hidden');
    } else {
        elements.transcriptBtn.classList.add('hidden');
    }
    
    // Calculate estimated file size
    const selectedFormat = getSelectedFormat();
    const estimatedSize = estimateFileSize(data, selectedFormat);
    elements.videoSize.innerHTML = `<i class="fas fa-file"></i> ~${formatFileSize(estimatedSize)}`;
}

function updateQualityOptions(formats) {
    // Clear existing options
    elements.qualitySelect.innerHTML = '';
    
    if (formats && formats.length > 0) {
        // Get unique qualities
        const qualities = [...new Set(formats.map(f => f.quality))].filter(q => q);
        
        qualities.forEach(quality => {
            const option = document.createElement('option');
            option.value = quality;
            option.textContent = quality.includes('p') ? `${quality} HD` : quality;
            elements.qualitySelect.appendChild(option);
        });
        
        // Add default options if no specific qualities found
        if (qualities.length === 0) {
            const defaultOptions = ['highest', '720p', '480p', '360p', 'lowest'];
            defaultOptions.forEach(quality => {
                const option = document.createElement('option');
                option.value = quality;
                option.textContent = quality === 'highest' ? 'Highest Quality' : 
                                   quality === 'lowest' ? 'Lowest Quality' : 
                                   quality.includes('p') ? `${quality} HD` : quality;
                elements.qualitySelect.appendChild(option);
            });
        }
    }
}

function getSelectedFormat() {
    const activeTab = document.querySelector('.format-tab.active');
    return activeTab ? activeTab.dataset.format : 'video';
}

function estimateFileSize(data, format) {
    // Simple estimation based on duration and quality
    if (!data.duration) return 0;
    
    const quality = elements.qualitySelect.value;
    const duration = data.duration;
    
    // Rough estimates in bytes per second
    const bitrateEstimates = {
        'highest': format === 'video' ? 2000000 : 320000,
        '720p': format === 'video' ? 1500000 : 256000,
        '480p': format === 'video' ? 1000000 : 192000,
        '360p': format === 'video' ? 500000 : 128000,
        'lowest': format === 'video' ? 250000 : 96000
    };
    
    const bitrate = bitrateEstimates[quality] || bitrateEstimates['720p'];
    return duration * (bitrate / 8); // Convert to bytes
}

async function handleDownload() {
    if (!currentVideoData || isDownloading) return;
    
    const url = elements.videoUrl.value.trim();
    const quality = elements.qualitySelect.value;
    const format = getSelectedFormat();
    
    isDownloading = true;
    elements.downloadBtn.disabled = true;
    elements.downloadBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Preparing...';
    
    // Show progress
    hideAllSections();
    showElement(elements.downloadProgress);
    
    // Simulate progress (since we can't get real progress from the backend easily)
    simulateProgress();
    
    try {
        const result = await downloadVideo(url, quality, format);
        
        // Show success
        hideAllSections();
        elements.downloadLink.href = result.download_url;
        elements.downloadLink.download = result.filename;
        showElement(elements.downloadComplete);
        
        showNotification('Download completed successfully!', 'success');
        
    } catch (error) {
        showError(error.message);
    } finally {
        isDownloading = false;
        elements.downloadBtn.disabled = false;
        elements.downloadBtn.innerHTML = '<i class="fas fa-download"></i> Download Video';
    }
}

function simulateProgress() {
    let progress = 0;
    const interval = setInterval(() => {
        progress += Math.random() * 15;
        
        if (progress >= 95 || !isDownloading) {
            progress = 95;
            clearInterval(interval);
        }
        
        elements.progressFill.style.width = `${progress}%`;
        elements.progressPercentage.textContent = `${Math.round(progress)}%`;
        
        // Update status message
        if (progress < 30) {
            elements.progressStatus.textContent = 'Preparing download...';
        } else if (progress < 70) {
            elements.progressStatus.textContent = 'Downloading video...';
        } else {
            elements.progressStatus.textContent = 'Finalizing download...';
        }
    }, 500);
}

async function handleTranscript() {
    if (!currentVideoData) return;
    
    const url = elements.videoUrl.value.trim();
    elements.transcriptBtn.disabled = true;
    elements.transcriptBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Loading...';
    
    try {
        const result = await getTranscript(url);
        
        // Display transcript in modal
        displayTranscript(result.transcript);
        showElement(elements.transcriptModal);
        
    } catch (error) {
        showNotification(error.message, 'error');
    } finally {
        elements.transcriptBtn.disabled = false;
        elements.transcriptBtn.innerHTML = '<i class="fas fa-closed-captioning"></i> Get Transcript';
    }
}

function displayTranscript(transcript) {
    elements.transcriptContent.innerHTML = '';
    
    transcript.forEach(entry => {
        const div = document.createElement('div');
        div.className = 'transcript-entry';
        
        const timeDiv = document.createElement('div');
        timeDiv.className = 'transcript-time';
        timeDiv.textContent = formatTimestamp(entry.start);
        
        const textDiv = document.createElement('div');
        textDiv.textContent = entry.text;
        
        div.appendChild(timeDiv);
        div.appendChild(textDiv);
        elements.transcriptContent.appendChild(div);
    });
}

function formatTimestamp(seconds) {
    const minutes = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${minutes}:${secs.toString().padStart(2, '0')}`;
}

function copyTranscriptToClipboard() {
    const entries = elements.transcriptContent.querySelectorAll('.transcript-entry');
    let text = '';
    
    entries.forEach(entry => {
        const time = entry.querySelector('.transcript-time').textContent;
        const content = entry.lastChild.textContent;
        text += `[${time}] ${content}\n`;
    });
    
    navigator.clipboard.writeText(text).then(() => {
        showNotification('Transcript copied to clipboard!', 'success');
    }).catch(() => {
        showNotification('Failed to copy transcript', 'error');
    });
}

function downloadTranscriptAsText() {
    const entries = elements.transcriptContent.querySelectorAll('.transcript-entry');
    let text = `Transcript - ${currentVideoData?.title || 'Video'}\n\n`;
    
    entries.forEach(entry => {
        const time = entry.querySelector('.transcript-time').textContent;
        const content = entry.lastChild.textContent;
        text += `[${time}] ${content}\n`;
    });
    
    const blob = new Blob([text], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `transcript-${Date.now()}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    showNotification('Transcript downloaded!', 'success');
}

// Event listeners
document.addEventListener('DOMContentLoaded', function() {
    // URL input - Enter key
    elements.videoUrl.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            handleAnalyze();
        }
    });
    
    // Analyze button
    elements.analyzeBtn.addEventListener('click', handleAnalyze);
    
    // Format tabs
    elements.formatTabs.forEach(tab => {
        tab.addEventListener('click', function() {
            // Remove active class from all tabs
            elements.formatTabs.forEach(t => t.classList.remove('active'));
            // Add active class to clicked tab
            this.classList.add('active');
            
            // Update estimated file size
            if (currentVideoData) {
                const selectedFormat = getSelectedFormat();
                const estimatedSize = estimateFileSize(currentVideoData, selectedFormat);
                elements.videoSize.innerHTML = `<i class="fas fa-file"></i> ~${formatFileSize(estimatedSize)}`;
            }
        });
    });
    
    // Quality selector
    elements.qualitySelect.addEventListener('change', function() {
        if (currentVideoData) {
            const selectedFormat = getSelectedFormat();
            const estimatedSize = estimateFileSize(currentVideoData, selectedFormat);
            elements.videoSize.innerHTML = `<i class="fas fa-file"></i> ~${formatFileSize(estimatedSize)}`;
        }
    });
    
    // Download button
    elements.downloadBtn.addEventListener('click', handleDownload);
    
    // Transcript button
    elements.transcriptBtn.addEventListener('click', handleTranscript);
    
    // Modal close
    elements.closeModal.addEventListener('click', function() {
        hideElement(elements.transcriptModal);
    });
    
    // Modal background click
    elements.transcriptModal.addEventListener('click', function(e) {
        if (e.target === this) {
            hideElement(elements.transcriptModal);
        }
    });
    
    // Copy transcript
    elements.copyTranscript.addEventListener('click', copyTranscriptToClipboard);
    
    // Download transcript
    elements.downloadTranscript.addEventListener('click', downloadTranscriptAsText);
    
    // Retry button
    elements.retryBtn.addEventListener('click', function() {
        hideAllSections();
        elements.videoUrl.focus();
    });
    
    // Escape key to close modal
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && !elements.transcriptModal.classList.contains('hidden')) {
            hideElement(elements.transcriptModal);
        }
    });
});

// Add notification styles dynamically
const notificationStyles = `
    .notification {
        position: fixed;
        top: 20px;
        right: 20px;
        background: white;
        padding: 1rem 1.5rem;
        border-radius: 10px;
        box-shadow: 0 5px 20px rgba(0, 0, 0, 0.1);
        display: flex;
        align-items: center;
        gap: 0.5rem;
        transform: translateX(400px);
        transition: transform 0.3s ease;
        z-index: 2000;
        max-width: 350px;
    }
    
    .notification.show {
        transform: translateX(0);
    }
    
    .notification-success {
        border-left: 4px solid #00b894;
        color: #00b894;
    }
    
    .notification-error {
        border-left: 4px solid #e74c3c;
        color: #e74c3c;
    }
    
    .notification-info {
        border-left: 4px solid #667eea;
        color: #667eea;
    }
`;

// Add styles to head
const style = document.createElement('style');
style.textContent = notificationStyles;
document.head.appendChild(style);