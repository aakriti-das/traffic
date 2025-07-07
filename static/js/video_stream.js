let videoStream = false;
let statsInterval = null;
let retryCount = 0;
const MAX_RETRIES = 3;

// Enhanced notification system
let notificationInterval = null;
let lastAlertCount = 0;

// DOM Elements
const videoElement = document.getElementById('video-stream');
const errorElement = document.getElementById('video-error');
const loadingElement = document.getElementById('loading-indicator');
const startButton = document.querySelector('.start-camera');
const stopButton = document.querySelector('.stop-camera');
const bellButton = document.getElementById('notification-button');
const statusDot = document.querySelector('.status-dot');

function showError() {
    if (errorElement) errorElement.style.display = 'flex';
    if (loadingElement) loadingElement.style.display = 'none';
}

function showLoading() {
    if (errorElement) errorElement.style.display = 'none';
    if (loadingElement) loadingElement.style.display = 'flex';
}

function hideLoadingAndError() {
    if (errorElement) errorElement.style.display = 'none';
    if (loadingElement) loadingElement.style.display = 'none';
}

function handleVideoError(event) {
    console.error('Video stream error:', event);
    if (retryCount < MAX_RETRIES) {
        retryCount++;
        console.log(`Retrying video stream (${retryCount}/${MAX_RETRIES})...`);
        setTimeout(startCamera, 1000);
    } else {
        showError();
        stopCamera();
    }
}

function handleVideoLoad() {
    console.log('Video stream loaded successfully');
    hideLoadingAndError();
    retryCount = 0;
}

function startCamera() {
    console.log({ startButton, stopButton });
    if (!videoStream) {
        showLoading();
        // Add timestamp to prevent caching
        const timestamp = new Date().getTime();
        if (videoElement) {
            videoElement.src = `${videoElement.dataset.url}?t=${Date.now()}`;
            videoStream = true;
            // Add error handling for video element
            videoElement.onerror = function () {
                console.error('Video element error');
                handleVideoError(new Error('Video element failed to load'));
            };

            videoElement.onloadstart = function () {
                console.log('Video stream starting...');
            };
        }

        // Update UI
        if (startButton) startButton.disabled = true;
        if (stopButton) stopButton.disabled = false;
        if (statusDot) statusDot.style.backgroundColor = 'var(--success-color)';

        // Start stats updates
        if (!statsInterval) {
            statsInterval = setInterval(updateStats, 2000);
        }
        console.log('Camera started');
    }
}

function stopCamera() {
    console.log({ startButton, stopButton });
    if (videoStream) {
        if (videoElement) {
            videoElement.src = '';
            videoElement.removeAttribute('src');
        }
        videoStream = false;

        // Update UI
        if (startButton) startButton.disabled = false;
        if (stopButton) stopButton.disabled = true;
        if (statusDot) statusDot.style.backgroundColor = 'var(--danger-color)';

        // Reset stats and clear interval
        const vehicleCount = document.getElementById('vehicle-count');
        const currentSpeed = document.getElementById('current-speed');
        if (vehicleCount) vehicleCount.textContent = '0';
        if (currentSpeed) currentSpeed.textContent = '0';

        if (statsInterval) {
            clearInterval(statsInterval);
            statsInterval = null;
        }

        hideLoadingAndError();
        retryCount = 0;
    }
}

// Initialize everything when DOM is loaded
document.addEventListener('DOMContentLoaded', function () {
    console.log('Initializing video stream components...');

    // Initialize button states
    if (stopButton) stopButton.disabled = true;
    if (startButton) startButton.disabled = false;
    if (statusDot) statusDot.style.backgroundColor = 'var(--danger-color)';
    hideLoadingAndError();

    // Add event listeners
    if (videoElement) {
        videoElement.addEventListener('error', handleVideoError);
        videoElement.addEventListener('load', handleVideoLoad);
    }

    if (startButton) {
        startButton.addEventListener('click', startCamera);
    }

    if (stopButton) {
        stopButton.addEventListener('click', stopCamera);
    }

    // Optional: Auto-start with error recovery
    setTimeout(() => {
        console.log('Auto-starting video stream...');
        startCamera();

        // If auto-start fails, re-enable the start button after 5 seconds
        setTimeout(() => {
            if (!videoStream && startButton) {
                startButton.disabled = false;
                console.log('Auto-start failed - start button re-enabled');
            }
        }, 5000);
    }, 2000);

    // Start notification polling
    startNotificationPolling();

    // Request notification permission
    if ('Notification' in window && Notification.permission === 'default') {
        Notification.requestPermission();
    }

    // Initial fetch
    fetchNotifications();
});

// Get CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Update stats periodically with better error handling
async function updateStats() {
    if (!videoStream) return;

    try {
        const response = await fetch('/speed_estimation/get_stats/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify({})
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();

        // Handle different response formats
        if (data.status === 'error') {
            throw new Error(data.error);
        }

        const vehicleCount = document.getElementById('vehicle-count');
        const currentSpeed = document.getElementById('current-speed');

        if (vehicleCount) vehicleCount.textContent = data.vehicle_count || '0';
        if (currentSpeed) currentSpeed.textContent = data.current_speed || '0';

        console.log('Stats updated:', data);

    } catch (error) {
        console.error('Error updating stats:', error);
        // Don't stop camera on network errors, just log them
        if (error.message.includes('Failed to fetch') || error.message.includes('NetworkError')) {
            console.log('Network error - server might not be running');
        }
    }
}

// Enhanced notification system

// Function to update notification badge
function updateNotificationBadge(count) {
    const badge = document.getElementById('notification-count');
    if (badge) {
        if (count > 0) {
            badge.style.display = 'inline-block';
            badge.textContent = count;
            // Add animation for new alerts
            if (count > lastAlertCount) {
                badge.classList.add('pulse');
                setTimeout(() => badge.classList.remove('pulse'), 1000);
            }
        } else {
            badge.style.display = 'none';
        }
    }
    lastAlertCount = count;
}

// Function to fetch and display notifications
async function fetchNotifications() {
    try {
        const response = await fetch('/notifications/');
        const data = await response.json();
        const alerts = data.alerts || [];

        updateNotificationBadge(alerts.length);

        // Update notification list if dropdown is open
        const list = document.getElementById('notification-list');
        if (list && document.getElementById('notification-dropdown').style.display === 'block') {
            displayNotifications(alerts);
        }

        return data;
    } catch (error) {
        console.error('Error fetching notifications:', error);
        return { alerts: [], alert_count: 0 };
    }
}

// Function to display notifications in dropdown
function displayNotifications(alerts) {
    const list = document.getElementById('notification-list');
    if (!list) return;

    list.innerHTML = '';

    if (alerts.length > 0) {
        alerts.forEach(alert => {
            const li = document.createElement('li');
            li.className = `alert-item alert-${alert.type || 'warning'}`;

            // Create notification content with more details
            li.innerHTML = `
                <div class="alert-content">
                    <div class="alert-message">${alert.message}</div>
                    <div class="alert-meta">
                        <span class="alert-time">${new Date(alert.timestamp).toLocaleTimeString()}</span>
                        ${alert.speed ? `<span class="alert-speed">${alert.speed} km/h</span>` : ''}
                    </div>
                </div>
            `;

            list.appendChild(li);
        });
    } else {
        const li = document.createElement('li');
        li.textContent = 'No new notifications';
        li.className = 'no-alerts';
        list.appendChild(li);
    }
}

// Function to clear notifications
async function clearNotifications() {
    try {
        const response = await fetch('/notifications/clear/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'Content-Type': 'application/json'
            }
        });

        if (response.ok) {
            updateNotificationBadge(0);
            const list = document.getElementById('notification-list');
            if (list) {
                list.innerHTML = '<li class="no-alerts">No new notifications</li>';
            }
        }
    } catch (error) {
        console.error('Error clearing notifications:', error);
    }
}

// Enhanced bell button click handler
bellButton.addEventListener('click', async function () {
    const dropdown = document.getElementById('notification-dropdown');

    if (dropdown) {
        const isVisible = dropdown.style.display === 'block';
        dropdown.style.display = isVisible ? 'none' : 'block';

        if (!isVisible) {
            // Fetch fresh notifications when opening dropdown
            const data = await fetchNotifications();
            displayNotifications(data.alerts);
        }
    }
});

// Start notification polling
function startNotificationPolling() {
    if (!notificationInterval) {
        notificationInterval = setInterval(async () => {
            const data = await fetchNotifications();

            // Show desktop notification for new alerts
            if (data.alert_count > lastAlertCount && data.alert_count > 0) {
                showDesktopNotification('New Traffic Alert',
                    `${data.alert_count - lastAlertCount} new speeding violation(s) detected!`);
            }
        }, 5000); // Check every 5 seconds
    }
}

// Desktop notification function
function showDesktopNotification(title, message) {
    if ('Notification' in window && Notification.permission === 'granted') {
        new Notification(title, { body: message, icon: '/static/images/traffic_logo.png' });
    } else if ('Notification' in window && Notification.permission !== 'denied') {
        Notification.requestPermission().then(permission => {
            if (permission === 'granted') {
                new Notification(title, { body: message, icon: '/static/images/traffic_logo.png' });
            }
        });
    }
}

