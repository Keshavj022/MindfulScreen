let showcaseStream;
let showcaseInterval;
let showcaseChart;
let sentimentChart;
let contentChart;
let appStats = {};
let sentimentStats = { positive: 0, negative: 0, neutral: 0, mixed: 0 };
let contentStats = {};
let analysisHistory = [];

document.getElementById('showcaseStartBtn').addEventListener('click', startShowcase);
document.getElementById('showcaseStopBtn').addEventListener('click', stopShowcase);

async function startShowcase() {
    try {
        showcaseStream = await navigator.mediaDevices.getDisplayMedia({
            video: { mediaSource: 'screen' }
        });

        const canvas = document.getElementById('showcaseCanvas');
        const video = document.createElement('video');
        video.srcObject = showcaseStream;
        await video.play();

        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;

        const ctx = canvas.getContext('2d');

        document.getElementById('showcaseStartBtn').style.display = 'none';
        document.getElementById('showcaseStopBtn').style.display = 'inline-block';

        // Reset stats
        appStats = {};
        sentimentStats = { positive: 0, negative: 0, neutral: 0, mixed: 0 };
        contentStats = {};
        analysisHistory = [];

        initAllCharts();
        updateAnalysisStatus('Analyzing...', 'info');

        showcaseInterval = setInterval(async () => {
            ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
            updateAnalysisStatus('Capturing frame...', 'warning');

            canvas.toBlob(async (blob) => {
                await analyzeShowcaseFrame(blob);
            }, 'image/jpeg', 0.9);
        }, 3000);
    } catch (err) {
        alert('Permission denied for screen capture. Please allow screen sharing to use this feature.');
    }
}

async function analyzeShowcaseFrame(blob) {
    const formData = new FormData();
    formData.append('session_id', 1);
    formData.append('frame_number', Math.floor(Date.now() / 1000));
    formData.append('timestamp', Date.now() / 1000);
    formData.append('frame', blob, 'frame.jpg');

    updateAnalysisStatus('AI analyzing...', 'primary');

    try {
        const res = await fetch('/analyzer/api/upload-frame', {
            method: 'POST',
            body: formData
        });

        const data = await res.json();
        if (data.success) {
            updateShowcaseUI(data.analysis);
            updateAnalysisStatus('Analysis complete', 'success');
        } else {
            updateAnalysisStatus('Analysis failed', 'danger');
        }
    } catch (err) {
        console.error('Analysis error:', err);
        updateAnalysisStatus('Connection error', 'danger');
    }
}

function updateAnalysisStatus(message, type) {
    const statusEl = document.getElementById('analysisStatus');
    if (statusEl) {
        statusEl.innerHTML = `<span class="badge bg-${type}">${message}</span>`;
    }
}

function updateShowcaseUI(analysis) {
    // Update detected app with badge color based on wellness
    const appBadge = document.getElementById('detectedApp');
    appBadge.textContent = analysis.app || 'Unknown';
    appBadge.className = `badge bg-${getWellnessColor(analysis.wellness_impact)}`;

    // Update content type
    const contentBadge = document.getElementById('contentType');
    contentBadge.textContent = formatContentType(analysis.content_type) || 'Unknown';
    contentBadge.className = 'badge bg-info';

    // Update sentiment with appropriate color
    const sentimentBadge = document.getElementById('sentiment');
    sentimentBadge.textContent = capitalizeFirst(analysis.sentiment) || 'Neutral';
    sentimentBadge.className = `badge bg-${getSentimentColor(analysis.sentiment)}`;

    // Update wellness impact
    const wellnessBadge = document.getElementById('wellnessImpact');
    wellnessBadge.textContent = capitalizeFirst(analysis.wellness_impact) || 'Neutral';
    wellnessBadge.className = `badge bg-${getWellnessColor(analysis.wellness_impact)}`;

    // Update extracted text - show properly formatted
    const extractedTextEl = document.getElementById('extractedText');
    if (analysis.extracted_text && analysis.extracted_text.length > 0) {
        const textParts = analysis.extracted_text.split('|').filter(t => t.trim());
        extractedTextEl.innerHTML = textParts.map(t =>
            `<span class="d-block mb-1 text-dark">${escapeHtml(t.trim())}</span>`
        ).join('');
    } else {
        extractedTextEl.innerHTML = '<span class="text-muted fst-italic">No text detected</span>';
    }

    // Update content description
    const descEl = document.getElementById('contentDescription');
    if (descEl && analysis.content_description) {
        descEl.textContent = analysis.content_description;
    }

    // Update objects detected
    const objectsEl = document.getElementById('objectsList');
    if (analysis.engagement_indicators || (analysis.objects_detected && analysis.objects_detected.length > 0)) {
        let objectsHtml = '';

        // Show engagement indicators
        if (analysis.engagement_indicators) {
            const ei = analysis.engagement_indicators;
            if (ei.has_notifications) objectsHtml += '<span class="badge bg-warning me-1 mb-1"><i class="fas fa-bell"></i> Notifications</span>';
            if (ei.has_comments) objectsHtml += '<span class="badge bg-info me-1 mb-1"><i class="fas fa-comment"></i> Comments</span>';
            if (ei.has_likes) objectsHtml += '<span class="badge bg-danger me-1 mb-1"><i class="fas fa-heart"></i> Likes</span>';
            if (ei.is_video_playing) objectsHtml += '<span class="badge bg-primary me-1 mb-1"><i class="fas fa-play"></i> Video</span>';
            if (ei.is_scrollable_feed) objectsHtml += '<span class="badge bg-secondary me-1 mb-1"><i class="fas fa-scroll"></i> Feed</span>';
        }

        // Show objects
        if (analysis.objects_detected && analysis.objects_detected.length > 0) {
            objectsHtml += analysis.objects_detected.slice(0, 8).map(obj =>
                `<span class="badge bg-light text-dark me-1 mb-1">${escapeHtml(obj)}</span>`
            ).join('');
        }

        objectsEl.innerHTML = objectsHtml || '<span class="text-muted">None detected</span>';
    }

    // Update concerns if any
    const concernsEl = document.getElementById('concernsList');
    if (concernsEl && analysis.potential_concerns && analysis.potential_concerns.length > 0) {
        concernsEl.innerHTML = analysis.potential_concerns.map(c =>
            `<span class="badge bg-warning text-dark me-1 mb-1"><i class="fas fa-exclamation-triangle"></i> ${escapeHtml(c)}</span>`
        ).join('');
    } else if (concernsEl) {
        concernsEl.innerHTML = '<span class="text-success"><i class="fas fa-check-circle"></i> No concerns</span>';
    }

    // Update statistics
    const app = analysis.app || 'Unknown';
    appStats[app] = (appStats[app] || 0) + 1;

    const sentiment = analysis.sentiment || 'neutral';
    sentimentStats[sentiment] = (sentimentStats[sentiment] || 0) + 1;

    const contentType = analysis.content_type || 'other';
    contentStats[contentType] = (contentStats[contentType] || 0) + 1;

    // Add to history
    analysisHistory.push({
        time: new Date().toLocaleTimeString(),
        app: analysis.app,
        sentiment: analysis.sentiment,
        wellness: analysis.wellness_impact
    });

    updateAllCharts();
    updateHistoryList();
}

function initAllCharts() {
    // App Usage Chart
    const appCtx = document.getElementById('realtimeChart');
    if (showcaseChart) showcaseChart.destroy();
    showcaseChart = new Chart(appCtx, {
        type: 'bar',
        data: {
            labels: [],
            datasets: [{
                label: 'App Usage',
                data: [],
                backgroundColor: '#6366f1',
                borderRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: { stepSize: 1 }
                }
            }
        }
    });

    // Sentiment Chart
    const sentimentCtx = document.getElementById('sentimentLiveChart');
    if (sentimentCtx) {
        if (sentimentChart) sentimentChart.destroy();
        sentimentChart = new Chart(sentimentCtx, {
            type: 'doughnut',
            data: {
                labels: ['Positive', 'Negative', 'Neutral', 'Mixed'],
                datasets: [{
                    data: [0, 0, 0, 0],
                    backgroundColor: ['#10b981', '#ef4444', '#94a3b8', '#f59e0b'],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: { usePointStyle: true, padding: 10 }
                    }
                }
            }
        });
    }

    // Content Type Chart
    const contentCtx = document.getElementById('contentLiveChart');
    if (contentCtx) {
        if (contentChart) contentChart.destroy();
        contentChart = new Chart(contentCtx, {
            type: 'polarArea',
            data: {
                labels: [],
                datasets: [{
                    data: [],
                    backgroundColor: [
                        'rgba(99, 102, 241, 0.7)',
                        'rgba(16, 185, 129, 0.7)',
                        'rgba(245, 158, 11, 0.7)',
                        'rgba(239, 68, 68, 0.7)',
                        'rgba(139, 92, 246, 0.7)',
                        'rgba(59, 130, 246, 0.7)'
                    ]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: { usePointStyle: true, padding: 8, font: { size: 10 } }
                    }
                }
            }
        });
    }
}

function updateAllCharts() {
    // Update App Chart
    if (showcaseChart) {
        showcaseChart.data.labels = Object.keys(appStats);
        showcaseChart.data.datasets[0].data = Object.values(appStats);
        showcaseChart.update();
    }

    // Update Sentiment Chart
    if (sentimentChart) {
        sentimentChart.data.datasets[0].data = [
            sentimentStats.positive,
            sentimentStats.negative,
            sentimentStats.neutral,
            sentimentStats.mixed
        ];
        sentimentChart.update();
    }

    // Update Content Chart
    if (contentChart) {
        contentChart.data.labels = Object.keys(contentStats).map(formatContentType);
        contentChart.data.datasets[0].data = Object.values(contentStats);
        contentChart.update();
    }
}

function updateHistoryList() {
    const historyEl = document.getElementById('analysisHistory');
    if (!historyEl) return;

    const recent = analysisHistory.slice(-5).reverse();
    historyEl.innerHTML = recent.map(item => `
        <div class="d-flex justify-content-between align-items-center py-2 border-bottom">
            <div>
                <small class="text-muted">${item.time}</small>
                <div class="fw-medium">${item.app || 'Unknown'}</div>
            </div>
            <div>
                <span class="badge bg-${getSentimentColor(item.sentiment)} me-1">${capitalizeFirst(item.sentiment)}</span>
                <span class="badge bg-${getWellnessColor(item.wellness)}">${capitalizeFirst(item.wellness)}</span>
            </div>
        </div>
    `).join('');
}

function stopShowcase() {
    clearInterval(showcaseInterval);

    if (showcaseStream) {
        showcaseStream.getTracks().forEach(track => track.stop());
    }

    document.getElementById('showcaseStartBtn').style.display = 'inline-block';
    document.getElementById('showcaseStopBtn').style.display = 'none';
    updateAnalysisStatus('Stopped', 'secondary');
}

// Utility functions
function getWellnessColor(impact) {
    const colors = {
        'positive': 'success',
        'neutral': 'secondary',
        'negative': 'danger',
        'high_risk': 'danger'
    };
    return colors[impact] || 'secondary';
}

function getSentimentColor(sentiment) {
    const colors = {
        'positive': 'success',
        'negative': 'danger',
        'neutral': 'secondary',
        'mixed': 'warning'
    };
    return colors[sentiment] || 'secondary';
}

function formatContentType(type) {
    if (!type) return 'Unknown';
    return type.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ');
}

function capitalizeFirst(str) {
    if (!str) return '';
    return str.charAt(0).toUpperCase() + str.slice(1);
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
