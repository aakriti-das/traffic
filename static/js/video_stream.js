let videoStream = false;
let statsInterval = null;
let retryCount = 0;
const MAX_RETRIES = 3;
let isManuallyStopped = false;

// DOM Elements
const $ = id => document.getElementById(id);
const video = $('video-stream');
const errorBox = $('video-error');
const loader = $('loading-indicator');
const startBtn = document.querySelector('.start-camera');
const stopBtn = document.querySelector('.stop-camera');
const statusDot = document.querySelector('.status-dot');
const vehicleCount = $('vehicle-count');
const currentSpeed = $('current-speed');

const show = el => el && (el.style.display = 'flex');
const hide = el => el && (el.style.display = 'none');
const resetUI = () => {
    hide(errorBox);
    hide(loader);
};

function handleVideoError(e) {
    console.error('Stream error:', e);
    if (isManuallyStopped) return;
    if (++retryCount <= MAX_RETRIES) {
        console.log(`Retrying (${retryCount}/${MAX_RETRIES})...`);
        setTimeout(startCamera, 1000);
    } else {
        show(errorBox);
        stopCamera();
    }
}

function handleVideoLoad() {
    console.log('Stream loaded');
    resetUI();
    retryCount = 0;
}

function startCamera() {
    if (videoStream) return;

    show(loader);
    isManuallyStopped = false;
    video.src = `/video_feed/?t=${Date.now()}`;
    videoStream = true;

    startBtn.disabled = true;
    stopBtn.disabled = false;
    statusDot.style.backgroundColor = 'var(--success-color)';

    statsInterval = statsInterval || setInterval(updateStats, 5000);
}

function stopCamera() {
    if (!videoStream) return;

    isManuallyStopped = true;
    video.removeAttribute('src');
    video.load();
    videoStream = false;

    startBtn.disabled = false;
    stopBtn.disabled = true;
    statusDot.style.backgroundColor = 'var(--danger-color)';
    vehicleCount.textContent = '0';
    currentSpeed.textContent = '0';

    clearInterval(statsInterval);
    statsInterval = null;
    resetUI();
    retryCount = 0;
}

document.addEventListener('DOMContentLoaded', () => {
    console.log('Initializing...');
    stopBtn.disabled = true;
    statusDot.style.backgroundColor = 'var(--danger-color)';
    resetUI();

    video.addEventListener('error', handleVideoError);
    video.addEventListener('load', handleVideoLoad);
    startBtn.addEventListener('click', startCamera);
    stopBtn.addEventListener('click', stopCamera);
});

// CSRF token fetcher
const getCSRF = () => {
    const match = document.cookie.match(/csrftoken=([^;]+)/);
    return match ? decodeURIComponent(match[1]) : '';
};

// Periodic stats update
async function updateStats() {
    if (!videoStream) return;

    try {
        const res = await fetch('/speed_estimation/get_stats/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCSRF(),
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: '{}'
        });

        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        if (data.error) throw new Error(data.error);

        vehicleCount.textContent = data.vehicle_count;
        currentSpeed.textContent = data.current_speed;
    } catch (err) {
        console.error('Stats update failed:', err);
        if (/Failed to fetch|NetworkError/.test(err.message)) stopCamera();
    }
}
