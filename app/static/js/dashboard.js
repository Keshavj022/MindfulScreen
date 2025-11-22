let charts = {};
let appDetailsModal;

document.addEventListener('DOMContentLoaded', () => {
    appDetailsModal = new bootstrap.Modal(document.getElementById('appDetailsModal'));
    initializeDashboard();
});

async function initializeDashboard() {
    await Promise.all([
        loadStats(),
        loadTrends(),
        loadSentiment(),
        loadContent(),
        loadAppUsage(),
        loadQuickInsights(),
        loadWellnessAlerts(),
        loadRecentSessions(),
        loadHeatmap(),
        loadAppTimeline()
    ]);
}

async function loadStats() {
    try {
        const data = await fetchData('/dashboard/api/stats');
        if (!data) return;

        document.getElementById('totalSessions').textContent = data.total_sessions || 0;

        // Handle null values for new users with no data
        if (data.avg_wellness === null || data.no_data) {
            document.getElementById('avgWellness').textContent = '--';
        } else {
            document.getElementById('avgWellness').textContent = data.avg_wellness.toFixed(1);
        }

        if (data.avg_productivity === null || data.no_data) {
            document.getElementById('avgProductivity').textContent = '--';
        } else {
            document.getElementById('avgProductivity').textContent = data.avg_productivity.toFixed(1);
        }

        const totalMinutes = Math.floor((data.total_duration || 0) / 60);
        const hours = Math.floor(totalMinutes / 60);
        const minutes = totalMinutes % 60;
        document.getElementById('totalTime').textContent = hours > 0 ? `${hours}h ${minutes}m` : `${minutes}m`;

        // Calculate risk and productive percentages from content analysis
        const contentData = await fetchData('/dashboard/api/content-analysis');
        if (contentData && contentData.content_types) {
            const total = Object.values(contentData.content_types).reduce((a, b) => a + b, 0);
            const productive = (contentData.content_types.work || 0) + (contentData.content_types.educational || 0);
            const risky = (contentData.content_types.social_media || 0) + (contentData.content_types.gaming || 0);

            document.getElementById('productiveTime').textContent = total > 0 ? Math.round(productive / total * 100) + '%' : '0%';
            document.getElementById('riskTime').textContent = total > 0 ? Math.round(risky / total * 100) + '%' : '0%';
        }
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

async function loadTrends() {
    try {
        const data = await fetchData('/dashboard/api/wellness-trends');
        if (!data || data.length === 0) {
            document.querySelector('#trendsChart').parentElement.innerHTML =
                '<p class="text-center text-muted py-5">No trend data available. Start analyzing to see your trends!</p>';
            return;
        }

        renderChart('trendsChart', {
            type: 'line',
            data: {
                labels: data.map(d => formatDate(d.date)),
                datasets: [
                    {
                        label: 'Wellness',
                        data: data.map(d => d.wellness_score),
                        borderColor: '#10b981',
                        backgroundColor: 'rgba(16, 185, 129, 0.1)',
                        fill: true,
                        tension: 0.4,
                        borderWidth: 3,
                        pointRadius: 4,
                        pointHoverRadius: 6
                    },
                    {
                        label: 'Productivity',
                        data: data.map(d => d.productivity_score),
                        borderColor: '#6366f1',
                        backgroundColor: 'rgba(99, 102, 241, 0.1)',
                        fill: true,
                        tension: 0.4,
                        borderWidth: 3,
                        pointRadius: 4,
                        pointHoverRadius: 6
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                        labels: { usePointStyle: true, padding: 15, font: { size: 12, weight: '600' } }
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false,
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        padding: 12
                    }
                },
                scales: {
                    y: { beginAtZero: true, max: 10, grid: { color: 'rgba(0, 0, 0, 0.05)' } },
                    x: { grid: { display: false } }
                }
            }
        });
    } catch (error) {
        console.error('Error loading trends:', error);
    }
}

async function loadSentiment() {
    try {
        const data = await fetchData('/dashboard/api/content-analysis');
        if (!data || !data.sentiment_distribution) {
            document.querySelector('#sentimentChart').parentElement.innerHTML =
                '<p class="text-center text-muted py-4">No sentiment data</p>';
            return;
        }

        const sentiment = data.sentiment_distribution;
        const total = Object.values(sentiment).reduce((a, b) => a + b, 0);

        renderChart('sentimentChart', {
            type: 'doughnut',
            data: {
                labels: ['Positive', 'Negative', 'Neutral', 'Mixed'],
                datasets: [{
                    data: [
                        sentiment.positive || 0,
                        sentiment.negative || 0,
                        sentiment.neutral || 0,
                        sentiment.mixed || 0
                    ],
                    backgroundColor: ['#10b981', '#ef4444', '#94a3b8', '#f59e0b'],
                    borderWidth: 0,
                    hoverOffset: 10
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: { padding: 12, usePointStyle: true, font: { size: 11 } }
                    },
                    tooltip: {
                        callbacks: {
                            label: (context) => {
                                const pct = total > 0 ? Math.round(context.parsed / total * 100) : 0;
                                return `${context.label}: ${context.parsed} (${pct}%)`;
                            }
                        }
                    }
                }
            }
        });
    } catch (error) {
        console.error('Error loading sentiment:', error);
    }
}

async function loadContent() {
    try {
        const data = await fetchData('/dashboard/api/content-analysis');
        if (!data || !data.content_types || Object.keys(data.content_types).length === 0) {
            document.querySelector('#contentChart').parentElement.innerHTML =
                '<p class="text-center text-muted py-4">No content data</p>';
            return;
        }

        const labels = Object.keys(data.content_types).map(key =>
            key.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')
        );

        const colors = [
            '#6366f1', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6',
            '#3b82f6', '#14b8a6', '#f97316', '#ec4899', '#06b6d4'
        ];

        renderChart('contentChart', {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    data: Object.values(data.content_types),
                    backgroundColor: colors.slice(0, labels.length),
                    borderRadius: 6,
                    maxBarThickness: 40
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                indexAxis: 'y',
                plugins: { legend: { display: false } },
                scales: {
                    x: { beginAtZero: true, grid: { color: 'rgba(0, 0, 0, 0.05)' } },
                    y: { grid: { display: false } }
                }
            }
        });
    } catch (error) {
        console.error('Error loading content:', error);
    }
}

async function loadAppUsage() {
    try {
        const data = await fetchData('/dashboard/api/app-usage');
        if (!data || !data.apps || data.apps.length === 0) {
            document.getElementById('appUsageContainer').innerHTML =
                '<p class="text-center text-muted small py-4">No app usage data</p>';
            return;
        }

        renderChart('appUsageChart', {
            type: 'doughnut',
            data: {
                labels: data.apps.map(app => app.name),
                datasets: [{
                    data: data.apps.map(app => app.percentage),
                    backgroundColor: [
                        '#6366f1', '#8b5cf6', '#ec4899', '#f59e0b', '#10b981',
                        '#3b82f6', '#14b8a6', '#f97316', '#a855f7', '#06b6d4'
                    ],
                    borderWidth: 0,
                    hoverOffset: 8
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            label: (context) => `${context.label}: ${context.parsed}%`
                        }
                    }
                },
                onClick: (event, elements) => {
                    if (elements.length > 0) {
                        const index = elements[0].index;
                        const appName = data.apps[index].name;
                        showAppDetails(appName);
                    }
                }
            }
        });

        // Render app list
        const appListHtml = data.apps.slice(0, 5).map((app, i) => {
            const colors = ['#6366f1', '#8b5cf6', '#ec4899', '#f59e0b', '#10b981'];
            return `
                <div class="d-flex justify-content-between align-items-center mb-2 cursor-pointer" onclick="showAppDetails('${app.name}')">
                    <div class="d-flex align-items-center">
                        <span class="badge me-2" style="background: ${colors[i]}">&nbsp;</span>
                        <span class="small">${app.name}</span>
                    </div>
                    <span class="badge bg-light text-dark">${app.percentage}%</span>
                </div>
            `;
        }).join('');

        document.getElementById('appUsageList').innerHTML = appListHtml;
    } catch (error) {
        console.error('Error loading app usage:', error);
    }
}

async function loadQuickInsights() {
    try {
        const data = await fetchData('/dashboard/api/quick-insights');
        const container = document.getElementById('quickInsights');

        if (!data || data.length === 0) {
            container.innerHTML = `
                <div class="insight-item">
                    <div class="d-flex align-items-start">
                        <span class="insight-icon bg-info text-white me-2"><i class="fas fa-info"></i></span>
                        <div>
                            <strong>Get Started</strong>
                            <p class="small text-muted mb-0">Start analyzing your screen time to get personalized insights.</p>
                        </div>
                    </div>
                </div>
            `;
            return;
        }

        container.innerHTML = data.map(insight => `
            <div class="insight-item mb-3">
                <div class="d-flex align-items-start">
                    <span class="insight-icon bg-${insight.type} text-white me-2">
                        <i class="fas ${insight.icon}"></i>
                    </span>
                    <div>
                        <strong>${insight.title}</strong>
                        <p class="small text-muted mb-0">${insight.message}</p>
                    </div>
                </div>
            </div>
        `).join('');
    } catch (error) {
        console.error('Error loading quick insights:', error);
    }
}

async function loadWellnessAlerts() {
    try {
        const data = await fetchData('/dashboard/api/wellness-alerts');
        const container = document.getElementById('wellnessAlerts');

        if (!data || data.length === 0) {
            container.innerHTML = `
                <div class="alert alert-success small mb-0">
                    <i class="fas fa-check-circle me-1"></i>
                    All clear! No wellness concerns at this time.
                </div>
            `;
            return;
        }

        container.innerHTML = data.map(alert => `
            <div class="alert alert-${alert.type} small mb-2">
                <i class="fas fa-exclamation-triangle me-1"></i>
                ${alert.message}
            </div>
        `).join('');
    } catch (error) {
        console.error('Error loading wellness alerts:', error);
    }
}

async function loadRecentSessions() {
    try {
        const data = await fetchData('/dashboard/api/recent-sessions');
        const tbody = document.getElementById('recentSessions');

        if (!data || data.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="7" class="text-center py-4 text-muted">
                        No sessions yet. <a href="/analyzer">Start your first analysis!</a>
                    </td>
                </tr>
            `;
            return;
        }

        tbody.innerHTML = data.map(session => {
            const date = new Date(session.created_at);
            const duration = Math.floor((session.duration_seconds || 0) / 60);
            const wellnessClass = session.wellness_score >= 7 ? 'success' : session.wellness_score >= 4 ? 'warning' : 'danger';
            const prodClass = session.productivity_score >= 7 ? 'success' : session.productivity_score >= 4 ? 'warning' : 'danger';

            return `
                <tr>
                    <td><strong>${session.name}</strong></td>
                    <td>${date.toLocaleDateString()}</td>
                    <td>${duration}m</td>
                    <td><span class="badge bg-${wellnessClass}">${(session.wellness_score || 0).toFixed(1)}</span></td>
                    <td><span class="badge bg-${prodClass}">${(session.productivity_score || 0).toFixed(1)}</span></td>
                    <td><span class="badge bg-info">${session.top_app}</span></td>
                    <td>
                        <button class="btn btn-sm btn-outline-primary" onclick="showAppDetails('${session.top_app}')">
                            <i class="fas fa-eye"></i>
                        </button>
                    </td>
                </tr>
            `;
        }).join('');
    } catch (error) {
        console.error('Error loading recent sessions:', error);
    }
}

async function loadHeatmap() {
    const container = document.getElementById('heatmapChart');
    if (!container) return;

    // Get actual session data to build heatmap
    const trendsData = await fetchData('/dashboard/api/wellness-trends');

    // If no data, show empty heatmap with message
    if (!trendsData || trendsData.length === 0) {
        container.innerHTML = `
            <div class="text-center py-4 text-muted">
                <i class="fas fa-calendar-times fa-2x mb-2"></i>
                <p class="mb-0">No activity data yet. Start analyzing your screen time to see your weekly activity patterns.</p>
            </div>
        `;
        return;
    }

    // Build activity data from sessions
    const activityMap = {};
    trendsData.forEach(session => {
        const date = new Date(session.date);
        const dayIndex = date.getDay(); // 0-6 (Sun-Sat)
        const hour = date.getHours();
        const timeSlot = Math.floor(hour / 4); // 0-5 (6 time slots per day)
        const key = `${dayIndex}-${timeSlot}`;

        if (!activityMap[key]) {
            activityMap[key] = { count: 0, totalWellness: 0 };
        }
        activityMap[key].count++;
        activityMap[key].totalWellness += session.wellness_score || 5;
    });

    // Simplified heatmap visualization
    const days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

    let html = '<div class="d-flex flex-wrap justify-content-center gap-1">';
    days.forEach((day, dayIndex) => {
        html += `<div class="text-center" style="width: 13%">
            <small class="text-muted">${day}</small>
            <div class="d-flex flex-column gap-1 mt-1">`;
        for (let slot = 0; slot < 6; slot++) {
            const key = `${dayIndex}-${slot}`;
            const activity = activityMap[key];
            let color = '#e5e7eb'; // Default: no activity

            if (activity) {
                const avgWellness = activity.totalWellness / activity.count;
                // Color based on wellness score (inverted: high wellness = green)
                if (avgWellness >= 7) color = '#10b981';
                else if (avgWellness >= 5) color = '#f59e0b';
                else color = '#ef4444';
            }

            const hourStart = slot * 4;
            const hourEnd = hourStart + 4;
            html += `<div style="height: 8px; background: ${color}; border-radius: 2px;" title="${day} ${hourStart}:00-${hourEnd}:00"></div>`;
        }
        html += '</div></div>';
    });
    html += '</div>';
    html += '<div class="d-flex justify-content-center gap-3 mt-3 small text-muted">';
    html += '<span><span style="display:inline-block;width:12px;height:12px;background:#e5e7eb;border-radius:2px;"></span> No Data</span>';
    html += '<span><span style="display:inline-block;width:12px;height:12px;background:#10b981;border-radius:2px;"></span> Good Wellness</span>';
    html += '<span><span style="display:inline-block;width:12px;height:12px;background:#f59e0b;border-radius:2px;"></span> Moderate</span>';
    html += '<span><span style="display:inline-block;width:12px;height:12px;background:#ef4444;border-radius:2px;"></span> Needs Attention</span>';
    html += '</div>';

    container.innerHTML = html;
}

async function loadAppTimeline() {
    const canvas = document.getElementById('appTimelineChart');
    if (!canvas) return;

    try {
        const data = await fetchData('/dashboard/api/wellness-trends');
        if (!data || data.length === 0) {
            canvas.parentElement.innerHTML = '<p class="text-center text-muted py-4">No timeline data available</p>';
            return;
        }

        renderChart('appTimelineChart', {
            type: 'bar',
            data: {
                labels: data.map(d => formatDate(d.date)),
                datasets: [
                    {
                        label: 'Wellness',
                        data: data.map(d => d.wellness_score),
                        backgroundColor: 'rgba(16, 185, 129, 0.8)',
                        borderRadius: 4
                    },
                    {
                        label: 'Productivity',
                        data: data.map(d => d.productivity_score),
                        backgroundColor: 'rgba(99, 102, 241, 0.8)',
                        borderRadius: 4
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'top', labels: { usePointStyle: true } }
                },
                scales: {
                    y: { beginAtZero: true, max: 10 },
                    x: { grid: { display: false } }
                }
            }
        });
    } catch (error) {
        console.error('Error loading app timeline:', error);
    }
}

async function showAppDetails(appName) {
    document.getElementById('modalAppName').textContent = appName;
    document.getElementById('modalAppBody').innerHTML = `
        <div class="text-center py-4">
            <div class="spinner-border text-primary"></div>
            <p class="mt-2 text-muted">Loading details...</p>
        </div>
    `;
    appDetailsModal.show();

    try {
        const data = await fetchData(`/dashboard/api/app-details/${encodeURIComponent(appName)}`);

        if (!data || data.error) {
            document.getElementById('modalAppBody').innerHTML = `
                <div class="alert alert-info mb-0">
                    <i class="fas fa-info-circle me-2"></i>No detailed information available for this app.
                </div>
            `;
            return;
        }

        const contentHtml = Object.entries(data.content_types || {})
            .map(([type, count]) => `
                <div class="d-flex justify-content-between align-items-center mb-2">
                    <span class="text-capitalize">${type.replace('_', ' ')}</span>
                    <span class="badge bg-primary rounded-pill">${count}</span>
                </div>
            `).join('');

        const sentimentHtml = Object.entries(data.sentiments || {})
            .map(([type, count]) => {
                const color = type === 'positive' ? 'success' : type === 'negative' ? 'danger' : 'secondary';
                return `
                    <div class="d-flex justify-content-between align-items-center mb-2">
                        <span class="text-capitalize">${type}</span>
                        <span class="badge bg-${color} rounded-pill">${count}</span>
                    </div>
                `;
            }).join('');

        document.getElementById('modalAppBody').innerHTML = `
            <div class="row g-4">
                <div class="col-md-6">
                    <h6 class="fw-bold mb-3"><i class="fas fa-layer-group me-2"></i>Content Types</h6>
                    ${contentHtml || '<p class="text-muted small">No content data</p>'}
                </div>
                <div class="col-md-6">
                    <h6 class="fw-bold mb-3"><i class="fas fa-smile me-2"></i>Sentiments</h6>
                    ${sentimentHtml || '<p class="text-muted small">No sentiment data</p>'}
                </div>
            </div>
            <hr class="my-4">
            <div class="d-flex justify-content-around text-center">
                <div>
                    <h4 class="text-primary mb-0">${data.total_frames || 0}</h4>
                    <small class="text-muted">Total Frames</small>
                </div>
                <div>
                    <h4 class="text-success mb-0">${(data.avg_sentiment_score || 0).toFixed(2)}</h4>
                    <small class="text-muted">Avg Sentiment</small>
                </div>
            </div>
        `;
    } catch (error) {
        console.error('Error loading app details:', error);
        document.getElementById('modalAppBody').innerHTML = `
            <div class="alert alert-danger mb-0">
                <i class="fas fa-exclamation-circle me-2"></i>Error loading app details. Please try again.
            </div>
        `;
    }
}

async function fetchData(url) {
    try {
        const response = await fetch(url);
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        return await response.json();
    } catch (error) {
        console.error(`Error fetching ${url}:`, error);
        return null;
    }
}

function renderChart(canvasId, config) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;

    if (charts[canvasId]) {
        charts[canvasId].destroy();
    }

    charts[canvasId] = new Chart(canvas, config);
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
}
