/**
 * VideoHQ Pro - Interactive JavaScript
 * Advanced video downloader with AI enhancement simulation
 */

class VideoHQPro {
    constructor() {
        this.currentPlatform = null;
        this.selectedQuality = null;
        this.currentProcessId = null;
        this.adTimer = null;
        this.processingInterval = null;
        
        this.init();
    }

    init() {
        this.bindEvents();
        this.initAnimations();
    }

    bindEvents() {
        // URL input events
        const urlInput = document.getElementById('videoUrl');
        const detectBtn = document.getElementById('detectBtn');
        
        urlInput.addEventListener('input', this.onUrlInput.bind(this));
        urlInput.addEventListener('paste', this.onUrlPaste.bind(this));
        detectBtn.addEventListener('click', this.detectPlatform.bind(this));
        
        // Process button
        document.getElementById('processBtn').addEventListener('click', this.startProcessing.bind(this));
        
        // Download button
        document.getElementById('downloadBtn').addEventListener('click', this.downloadVideo.bind(this));
        
        // Ad modal events
        document.getElementById('adCompleteBtn').addEventListener('click', this.completeAd.bind(this));
    }

    initAnimations() {
        // Add subtle hover effects to quality cards when they're created
        // This will be called after quality cards are populated
    }

    async onUrlInput(event) {
        const url = event.target.value.trim();
        
        if (url.length > 10) {
            // Auto-detect platform as user types
            this.autoDetectPlatform(url);
        } else {
            this.hidePlatformInfo();
        }
    }

    async onUrlPaste(event) {
        // Small delay to let paste complete
        setTimeout(() => {
            this.detectPlatform();
        }, 100);
    }

    autoDetectPlatform(url) {
        const input = document.getElementById('videoUrl');
        
        // Add visual feedback based on detected platform
        input.classList.remove('tiktok', 'youtube', 'instagram');
        
        if (url.includes('tiktok.com') || url.includes('vm.tiktok.com')) {
            input.classList.add('tiktok');
        } else if (url.includes('youtube.com') || url.includes('youtu.be')) {
            input.classList.add('youtube');
        } else if (url.includes('instagram.com')) {
            input.classList.add('instagram');
        }
    }

    async detectPlatform() {
        const url = document.getElementById('videoUrl').value.trim();
        const detectBtn = document.getElementById('detectBtn');
        
        if (!url) {
            this.showError('Please enter a video URL');
            return;
        }

        // Show loading state
        detectBtn.innerHTML = '<div class="loading"></div>';
        detectBtn.disabled = true;

        try {
            const response = await fetch('/api/platform-detect', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url })
            });

            const data = await response.json();

            if (response.ok) {
                this.currentPlatform = data;
                this.showPlatformInfo(data);
                await this.analyzeVideo(url);
            } else {
                this.showError(data.error);
            }
        } catch (error) {
            this.showError('Platform detection failed');
        } finally {
            detectBtn.innerHTML = '<i class="fas fa-search"></i>';
            detectBtn.disabled = false;
        }
    }

    showPlatformInfo(data) {
        const platformInfo = document.getElementById('platformInfo');
        const platformDetails = document.getElementById('platformDetails');
        
        const confidence = Math.round(data.confidence * 100);
        
        platformDetails.innerHTML = `
            <div style="display: flex; align-items: center; gap: 10px;">
                <span style="font-size: 1.5rem;">${data.icon}</span>
                <div>
                    <strong>${data.platform.charAt(0).toUpperCase() + data.platform.slice(1)} detected</strong>
                    <div style="font-size: 0.9rem; color: var(--text-muted);">
                        Confidence: ${confidence}% • Analyzing video...
                    </div>
                </div>
            </div>
        `;
        
        platformInfo.style.display = 'block';
    }

    hidePlatformInfo() {
        document.getElementById('platformInfo').style.display = 'none';
        document.getElementById('qualitySection').style.display = 'none';
    }

    async analyzeVideo(url) {
        try {
            const response = await fetch('/api/analyze-smart', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url })
            });

            const data = await response.json();

            if (response.ok) {
                this.showVideoAnalysis(data);
                this.populateQualityOptions(data);
            } else {
                this.showError(data.error);
            }
        } catch (error) {
            this.showError('Video analysis failed');
        }
    }

    showVideoAnalysis(data) {
        const platformDetails = document.getElementById('platformDetails');
        
        const duration = data.duration ? this.formatDuration(data.duration) : 'Unknown';
        const enhancement = data.enhancement_potential || 'Standard';
        
        platformDetails.innerHTML = `
            <div style="display: flex; align-items: center; gap: 15px; margin-bottom: 15px;">
                <span style="font-size: 1.5rem;">${this.currentPlatform.icon}</span>
                <div style="flex: 1;">
                    <strong>${data.title || 'Video detected'}</strong>
                    <div style="font-size: 0.9rem; color: var(--text-muted);">
                        Duration: ${duration} • Enhancement potential: ${enhancement}
                    </div>
                </div>
            </div>
            <div style="padding: 10px; background: rgba(99, 102, 241, 0.1); border-radius: 8px; font-size: 0.9rem;">
                ✨ AI Enhancement available: ${data.ai_enhancements?.potential_quality_gain || '3-5x resolution improvement'}
            </div>
        `;
    }

    populateQualityOptions(videoData) {
        const qualityGrid = document.getElementById('qualityGrid');
        const qualitySection = document.getElementById('qualitySection');
        
        const qualityConfigs = this.currentPlatform.quality_configs;
        const recommendedQualities = this.currentPlatform.recommended_qualities;
        
        let qualityHTML = '';
        
        recommendedQualities.forEach(quality => {
            const config = qualityConfigs[quality];
            if (!config) return;
            
            const adRequired = config.ad_required > 0;
            const isPremium = config.premium;
            
            qualityHTML += `
                <div class="quality-card ${isPremium ? 'premium' : ''}" 
                     data-quality="${quality}" 
                     onclick="videoHQ.selectQuality('${quality}')">
                    ${adRequired ? `<div class="ad-badge">${config.ad_required}s ad</div>` : ''}
                    ${isPremium ? '<div class="premium-badge">👑 Premium</div>' : ''}
                    
                    <div class="quality-icon">${config.icon}</div>
                    <div class="quality-label">${quality} ${config.label}</div>
                    <div class="quality-details">
                        ${isPremium ? 'Premium only' : adRequired ? `Watch ${config.ad_required}s ad` : 'Free'}
                        <br>
                        <small>~${config.processing_time}s processing</small>
                    </div>
                </div>
            `;
        });
        
        qualityGrid.innerHTML = qualityHTML;
        qualitySection.style.display = 'block';
        
        // Animate in
        setTimeout(() => {
            qualitySection.style.animation = 'slideInScale 0.5s ease both';
        }, 100);
    }

    selectQuality(quality) {
        // Remove previous selection
        document.querySelectorAll('.quality-card').forEach(card => {
            card.classList.remove('selected');
        });
        
        // Add selection to clicked card
        const selectedCard = document.querySelector(`[data-quality="${quality}"]`);
        selectedCard.classList.add('selected');
        
        this.selectedQuality = quality;
        
        // Update process button
        const processBtn = document.getElementById('processBtn');
        const config = this.currentPlatform.quality_configs[quality];
        
        if (config.premium) {
            processBtn.innerHTML = `
                <i class="fas fa-crown"></i>
                Upgrade to Premium for ${quality}
            `;
        } else if (config.ad_required > 0) {
            processBtn.innerHTML = `
                <i class="fas fa-play"></i>
                Watch ${config.ad_required}s Ad → Start ${quality} Enhancement
            `;
        } else {
            processBtn.innerHTML = `
                <i class="fas fa-magic"></i>
                Start ${quality} AI Enhancement
            `;
        }
        
        // Add selection animation
        selectedCard.style.transform = 'scale(1.05)';
        setTimeout(() => {
            selectedCard.style.transform = '';
        }, 200);
    }

    async startProcessing() {
        if (!this.selectedQuality) {
            this.showError('Please select a quality first');
            return;
        }

        const url = document.getElementById('videoUrl').value.trim();
        const config = this.currentPlatform.quality_configs[this.selectedQuality];

        // Check if premium required
        if (config.premium) {
            this.showPremiumOffer();
            return;
        }

        // Check if ad required
        if (config.ad_required > 0) {
            await this.showAdModal(this.selectedQuality);
            return;
        }

        // Start processing directly
        this.processVideo(url, this.selectedQuality);
    }

    async showAdModal(quality) {
        const adModal = document.getElementById('adModal');
        const adTimer = document.getElementById('adTimer');
        const adQuality = document.getElementById('adQuality');
        const adCompleteBtn = document.getElementById('adCompleteBtn');
        
        adQuality.textContent = quality;
        adModal.style.display = 'flex';
        
        // Request ad content
        try {
            const response = await fetch('/api/request-ad', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ quality })
            });
            
            const adData = await response.json();
            
            if (adData.premium_user) {
                // Skip ad for premium users
                adModal.style.display = 'none';
                this.processVideo(document.getElementById('videoUrl').value, quality);
                return;
            }
            
            // Start ad timer
            let timeLeft = adData.duration;
            adTimer.textContent = timeLeft;
            
            this.adTimer = setInterval(() => {
                timeLeft--;
                adTimer.textContent = timeLeft;
                
                if (timeLeft <= 0) {
                    clearInterval(this.adTimer);
                    adCompleteBtn.classList.remove('hidden');
                    adTimer.textContent = '✓';
                }
            }, 1000);
            
            // Store ad session for completion
            this.currentAdSession = adData.ad_session_id;
            
        } catch (error) {
            this.showError('Failed to load ad');
        }
    }

    async completeAd() {
        try {
            const response = await fetch('/api/complete-ad', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    ad_session_id: this.currentAdSession,
                    watch_duration: this.currentPlatform.quality_configs[this.selectedQuality].ad_required
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                // Close ad modal and start processing
                document.getElementById('adModal').style.display = 'none';
                this.processVideo(document.getElementById('videoUrl').value, this.selectedQuality);
                
                // Show success message
                this.showSuccess(`${result.quality_unlocked} unlocked for ${Math.round(result.unlock_duration / 60)} minutes!`);
            } else {
                this.showError(result.message);
            }
            
        } catch (error) {
            this.showError('Failed to complete ad viewing');
        }
    }

    async processVideo(url, quality) {
        // Hide other sections and show processing
        document.getElementById('qualitySection').style.display = 'none';
        document.getElementById('processingScreen').style.display = 'block';
        
        // Reset processing state
        document.getElementById('progressFill').style.width = '0%';
        document.getElementById('processingStep').textContent = 'Initializing...';
        
        try {
            const response = await fetch('/api/process-video', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url, quality })
            });
            
            const result = await response.json();
            
            if (response.ok) {
                this.currentProcessId = result.process_id;
                this.startProgressTracking();
            } else {
                if (response.status === 403 && result.premium_offer) {
                    this.showPremiumOffer();
                } else if (response.status === 402) {
                    await this.showAdModal(quality);
                } else {
                    this.showError(result.error);
                }
            }
            
        } catch (error) {
            this.showError('Failed to start processing');
        }
    }

    startProgressTracking() {
        this.processingInterval = setInterval(async () => {
            try {
                const response = await fetch(`/api/processing-status/${this.currentProcessId}`);
                const status = await response.json();
                
                if (response.ok) {
                    this.updateProcessingStatus(status);
                    
                    if (status.status === 'completed') {
                        clearInterval(this.processingInterval);
                        this.showResults(status.result);
                    } else if (status.status === 'error') {
                        clearInterval(this.processingInterval);
                        this.showError(status.error);
                    }
                }
                
            } catch (error) {
                console.error('Failed to fetch processing status:', error);
            }
        }, 1000);
    }

    updateProcessingStatus(status) {
        // Update progress bar
        document.getElementById('progressFill').style.width = `${status.progress}%`;
        
        // Update processing step
        if (status.enhancement_step) {
            document.getElementById('processingStep').textContent = status.enhancement_step;
        }
        
        // Update live metrics
        if (status.live_metrics) {
            document.getElementById('neuronsActive').textContent = status.live_metrics.neurons_active;
            document.getElementById('gpuUtilization').textContent = status.live_metrics.gpu_utilization;
            document.getElementById('framesProcessed').textContent = status.live_metrics.frames_processed;
        }
        
        // Update ETA
        if (status.eta) {
            const eta = Math.round(status.eta);
            document.getElementById('etaTime').textContent = `${eta}s`;
        }
    }

    showResults(result) {
        // Hide processing screen and show results
        document.getElementById('processingScreen').style.display = 'none';
        document.getElementById('resultsScreen').style.display = 'block';
        
        // Populate result data
        document.getElementById('originalStats').innerHTML = `
            <div style="margin: 10px 0;">
                <strong>${this.formatFileSize(result.original_size)}</strong><br>
                <small>Original quality</small>
            </div>
        `;
        
        document.getElementById('enhancedStats').innerHTML = `
            <div style="margin: 10px 0;">
                <strong>${this.formatFileSize(result.enhanced_size)}</strong><br>
                <small>${result.quality_improvement}</small>
            </div>
            <div style="margin-top: 15px; padding: 10px; background: rgba(16, 185, 129, 0.2); border-radius: 8px; font-size: 0.9rem;">
                ✨ ${Math.round(result.enhanced_size / result.original_size)}x quality improvement
            </div>
        `;
        
        // Animate results in
        document.getElementById('resultsScreen').style.animation = 'slideInScale 0.6s ease both';
    }

    async downloadVideo() {
        if (!this.currentProcessId) return;
        
        const downloadBtn = document.getElementById('downloadBtn');
        const originalText = downloadBtn.innerHTML;
        
        downloadBtn.innerHTML = '<div class="loading"></div> Preparing download...';
        downloadBtn.disabled = true;
        
        try {
            // Create download link
            const downloadUrl = `/api/download-result/${this.currentProcessId}`;
            
            // Create temporary link and trigger download
            const link = document.createElement('a');
            link.href = downloadUrl;
            link.download = '';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            
            this.showSuccess('Download started!');
            
        } catch (error) {
            this.showError('Download failed');
        } finally {
            downloadBtn.innerHTML = originalText;
            downloadBtn.disabled = false;
        }
    }

    showPremiumOffer() {
        document.getElementById('premiumOffer').style.display = 'block';
    }

    closePremiumOffer() {
        document.getElementById('premiumOffer').style.display = 'none';
    }

    showError(message) {
        this.showNotification(message, 'error');
    }

    showSuccess(message) {
        this.showNotification(message, 'success');
    }

    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: ${type === 'error' ? 'var(--error)' : type === 'success' ? 'var(--success)' : 'var(--primary)'};
            color: white;
            padding: 15px 20px;
            border-radius: 8px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
            z-index: 1000;
            font-weight: 500;
            animation: slideInRight 0.3s ease;
        `;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        // Remove after 3 seconds
        setTimeout(() => {
            notification.style.animation = 'slideOutRight 0.3s ease';
            setTimeout(() => {
                document.body.removeChild(notification);
            }, 300);
        }, 3000);
    }

    formatDuration(seconds) {
        const minutes = Math.floor(seconds / 60);
        const remainingSeconds = seconds % 60;
        return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
    }

    formatFileSize(bytes) {
        const sizes = ['B', 'KB', 'MB', 'GB'];
        if (bytes === 0) return '0 B';
        const i = Math.floor(Math.log(bytes) / Math.log(1024));
        return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
    }
}

// Initialize the application
const videoHQ = new VideoHQPro();

// Add some CSS animations dynamically
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    @keyframes slideOutRight {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
`;
document.head.appendChild(style);

// Global function for premium offer
window.closePremiumOffer = () => videoHQ.closePremiumOffer();