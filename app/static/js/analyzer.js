let mediaRecorder;
let screenStream;
let audioStream;
let sessionId;
let frameCount = 0;
let recordingInterval;
let startTime;

function getCSRFToken() {
    return document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || '';
}

function startRecording() {
    startAnalysis();
}

async function startAnalysis() {
    try {
        screenStream = await navigator.mediaDevices.getDisplayMedia({
            video: { mediaSource: 'screen' }
        });

        audioStream = await navigator.mediaDevices.getUserMedia({
            audio: true
        });

        const sessionName = document.getElementById('sessionName').value;
        const res = await fetch('/analyzer/api/start-session', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body: JSON.stringify({ session_name: sessionName })
        });

        const data = await res.json();
        sessionId = data.session_id;

        document.getElementById('startBtn').style.display = 'none';
        document.getElementById('stopBtn').style.display = 'inline-block';
        document.getElementById('recordingStatus').style.display = 'block';

        startTime = Date.now();
        frameCount = 0;

        recordingInterval = setInterval(captureFrame, 2000);
        updateRecordingTime();
    } catch (err) {
        alert('Permission denied. Please allow screen and audio access.');
    }
}

async function captureFrame() {
    const video = document.createElement('video');
    video.srcObject = screenStream;
    await video.play();

    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0);

    canvas.toBlob(async (blob) => {
        frameCount++;
        const timestamp = (Date.now() - startTime) / 1000;

        const formData = new FormData();
        formData.append('session_id', sessionId);
        formData.append('frame_number', frameCount);
        formData.append('timestamp', timestamp);
        formData.append('frame', blob, 'frame.jpg');

        const res = await fetch('/analyzer/api/upload-frame', {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCSRFToken()
            },
            body: formData
        });

        const data = await res.json();
        if (data.success) {
            document.getElementById('framesAnalyzed').textContent = frameCount;

            const resultHtml = `
                <div class="alert alert-info">
                    <strong>Frame ${frameCount}:</strong>
                    App: <span class="badge bg-primary">${data.analysis.app}</span>
                    Content: <span class="badge bg-success">${data.analysis.content_type}</span>
                    Sentiment: <span class="badge bg-warning">${data.analysis.sentiment}</span>
                </div>
            `;

            document.getElementById('liveResults').innerHTML = resultHtml + document.getElementById('liveResults').innerHTML;
        }
    }, 'image/jpeg', 0.8);
}

function updateRecordingTime() {
    setInterval(() => {
        const elapsed = Math.floor((Date.now() - startTime) / 1000);
        const mins = Math.floor(elapsed / 60);
        const secs = elapsed % 60;
        document.getElementById('recordingTime').textContent =
            `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
    }, 1000);
}

async function stopAnalysis() {
    clearInterval(recordingInterval);

    if (screenStream) {
        screenStream.getTracks().forEach(track => track.stop());
    }
    if (audioStream) {
        audioStream.getTracks().forEach(track => track.stop());
    }

    const res = await fetch(`/analyzer/api/complete-session/${sessionId}`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCSRFToken()
        }
    });

    const data = await res.json();
    const summary = data.summary;

    document.getElementById('recordingStatus').style.display = 'none';
    document.getElementById('resultsSection').style.display = 'block';

    document.getElementById('resultWellness').textContent = summary.wellness_score.toFixed(1);
    document.getElementById('resultProductivity').textContent = summary.productivity_score.toFixed(1);
    document.getElementById('resultFrames').textContent = summary.total_frames;
    document.getElementById('resultDuration').textContent = summary.duration_seconds + 's';

    document.getElementById('stopBtn').style.display = 'none';
    document.getElementById('startBtn').style.display = 'inline-block';
}
