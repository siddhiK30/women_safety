// Global state
let isSOSActive = false;
let activityChart = null;
startMic();
let isSirenPlaying = false; // Move this to the top of the script
let audioContext;
let sirenOscillator;
let gainNode;


// Event listener for SOS button click
document.getElementById('sosButton').addEventListener('click', function () {
    isSOSActive = true;
    startVideo();
    
    // Show the "Ask All for Help" button
    const askAllButton = document.getElementById('askAllForHelp');
    askAllButton.classList.remove('hidden');
    askAllButton.classList.add('visible');

    // Add location fetching and sending SOS SMS
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            (position) => {
                const { latitude, longitude } = position.coords;

                // Send SOS message to the backend
                fetch("/send-sos/", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": getCookie("csrftoken"),
                    },
                    body: JSON.stringify({ latitude, longitude }),
                })
                    .then((response) => response.json())
                    .then((data) => {
                        alert(data.message); // Notify user
                    })
                    .catch((error) => {
                        console.error("Error:", error);
                    });

                // Additionally, send location as part of the SOS alert
                sendSOSAlert(latitude, longitude);
            },
            (error) => {
                alert("Unable to fetch location. Please enable GPS.");
            }
        );
    } else {
        alert("Geolocation is not supported by this browser.");
    }
});

async function askAllForHelp() {
    const button = document.getElementById('askAllForHelp');
    button.disabled = true;
    button.textContent = 'Sending Alerts...';
    button.classList.add('bg-yellow-500');
    button.classList.remove('bg-blue-500');

    try {
        const location = await getCurrentLocation();
        const users = Array.from(document.querySelectorAll('#nearby-user-list p.text-lg'))
                          .map(p => p.textContent.trim());

        const response = await fetch('/api/send-emergency-alert/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'),
            },
            body: JSON.stringify({
                users: users,
                location: location
            })
        });

        const data = await response.json();

        if (data.status === 'success') {
            button.textContent = 'Help Alerts Sent';
            button.classList.remove('bg-yellow-500');
            button.classList.add('bg-green-500');
            
            showNotification('Alert sent successfully to ${users.length} nearby users', 'success');
        } else {
            throw new Error(data.message || 'Failed to send alerts');
        }
    } catch (error) {
        console.error('Error sending alerts:', error);
        button.textContent = 'Failed - Try Again';
        button.classList.remove('bg-yellow-500');
        button.classList.add('bg-red-500');
        button.disabled = false;
        
        showNotification('Failed to send help alerts. Please try again.', 'error');
    }

    // Reset button after 3 seconds
    setTimeout(() => {
        button.textContent = 'Ask All for Help';
        button.classList.remove('bg-yellow-500', 'bg-green-500', 'bg-red-500');
        button.classList.add('bg-blue-500');
        button.disabled = false;
    }, 60000);
}

// Helper function to get CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split("; ");
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].split("=");
            if (cookie[0] === name) {
                cookieValue = decodeURIComponent(cookie[1]);
                break;
            }
        }
    }
    return cookieValue;
}

// Function to start the microphone
function startMic() {
   
    navigator.mediaDevices.getUserMedia({ audio: true })
        .then(function(stream) {
            console.log('Microphone is active');
            // Add code to use microphone stream
        })
        .catch(function(err) {
            console.error('Microphone error: ' + err);
        });
}


// Function to start video
function startVideo() {
    alert("Video recording will start");
    navigator.mediaDevices.getUserMedia({ video: true })
        .then(function(stream) {
            console.log('Video is active');
            // Add code to use video stream
        })
        .catch(function(err) {
            console.error('Video error: ' + err);
        });
}

// Theme Toggle
const themeToggle = document.getElementById('themeToggle');
const html = document.documentElement;

themeToggle.addEventListener('click', () => {
    if (html.getAttribute('data-theme') === 'dark') {
        html.removeAttribute('data-theme');
    } else {
        html.setAttribute('data-theme', 'dark');
    }
    updateChartColors();
});

// Activity Chart Functions
function updateChartColors() {
    const isDark = html.getAttribute('data-theme') === 'dark';
    const textColor = isDark ? '#F3F4F6' : '#1F2937';
    
    if (activityChart) {
        activityChart.options.scales.x.ticks.color = textColor;
        activityChart.options.scales.y.ticks.color = textColor;
        activityChart.options.scales.x.grid.color = isDark ? '#374151' : '#E5E7EB';
        activityChart.options.scales.y.grid.color = isDark ? '#374151' : '#E5E7EB';
        activityChart.update();
    }
}

// Initialize Activity Chart
window.addEventListener('load', function() {
    const ctx = document.getElementById('activityChart').getContext('2d');
    activityChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: ['1/10/2024', '2/10/2024', '3/10/2024', '4/10/2024', '5/10/2024', '6/10/2024'],
            datasets: [{
                data: [4, 3, 5, 4, 4, 4],
                borderColor: '#8B5CF6',
                tension: 0.4,
                pointRadius: 4,
                pointBackgroundColor: '#fff',
                pointBorderColor: '#8B5CF6',
                pointBorderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 8,
                    ticks: {
                        stepSize: 2
                    }
                }
            }
        }
    });
    updateChartColors();
});

// Chatbot Functions
async function sendMessage() {
    const input = document.getElementById('chatInput');
    const message = input.value.trim();

    if (message) {
        const messagesContainer = document.getElementById('chatMessages');

        // Add user message
        const userDiv = document.createElement('div');
        userDiv.className = 'message user-message';
        userDiv.textContent = message;
        messagesContainer.appendChild(userDiv);

        // Clear input
        input.value = '';

        try {
            // Try to get location
            const location = await getCurrentLocationChat().catch(() => null);
            
            // Prepare request data
            const requestData = {
                message: message,
                latitude: location?.latitude,
                longitude: location?.longitude
            };

            // Send message to Django backend
            const response = await fetch('/chatbot-api/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken'),
                },
                body: JSON.stringify(requestData)
            });

            const data = await response.json();

            // Display bot response
            const botDiv = document.createElement('div');
            botDiv.className = 'message bot-message';
            
            // Format the response with proper line breaks
            const formattedReply = data.reply.replace(/\n/g, '<br>');
            botDiv.innerHTML = formattedReply;
            
            messagesContainer.appendChild(botDiv);

        } catch (error) {
            console.error('Error:', error);
            const botDiv = document.createElement('div');
            botDiv.className = 'message bot-message';
            botDiv.textContent = 'An error occurred while contacting the chatbot API.';
            messagesContainer.appendChild(botDiv);
        }

        // Scroll to bottom
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
}

function getCurrentLocationChat() {
    return new Promise((resolve, reject) => {
        if (!navigator.geolocation) {
            reject(new Error('Geolocation is not supported by your browser'));
            return;
        }

        // Show loading message in chat
        const messagesContainer = document.getElementById('chatMessages');
        const loadingDiv = document.createElement('div');
        loadingDiv.className = 'message bot-message';
        loadingDiv.textContent = 'Fetching your location for personalized safety advice...';
        messagesContainer.appendChild(loadingDiv);

        navigator.geolocation.getCurrentPosition(
            (position) => {
                // Remove loading message
                loadingDiv.remove();
                resolve({
                    latitude: position.coords.latitude,
                    longitude: position.coords.longitude
                });
            },
            (error) => {
                // Remove loading message and show error
                loadingDiv.remove();
                const errorDiv = document.createElement('div');
                errorDiv.className = 'message bot-message';
                errorDiv.textContent = 'Unable to access your location. Providing general safety advice instead.';
                messagesContainer.appendChild(errorDiv);
                reject(error);
            },
            {
                enableHighAccuracy: true,
                timeout: 5000,
                maximumAge: 0
            }
        );
    });
}

// Helper Functions
function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
}

function toggleChatbot() {
    const overlay = document.getElementById('chatbotOverlay');
    if (overlay.classList.contains('active')) {
        overlay.classList.remove('active');
    } else {
        overlay.classList.add('active');
        document.getElementById('chatInput').focus();
    }
}

// Nearby Users and Help Functions
function updateNearbyUsers() {
    fetch(window.location.href, {
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        const container = document.getElementById('nearby-user-list');
        container.innerHTML = '';

        if (data.length > 0) {
            data.forEach(user => {
                const userDiv = document.createElement('div');
                userDiv.className = 'p-4 bg-gray-100 rounded-lg shadow-md mb-4';

                userDiv.innerHTML = `
                    <p class="text-sm font-medium">${user.username}</p>
                    <p class="text-xs text-gray-500">${user.distance} km away</p>
                `;

                container.appendChild(userDiv);
            });
        } else {
            container.innerHTML = '<p>No nearby users found.</p>';
        }
    })
   
}

function getCurrentLocation() {
    return new Promise((resolve, reject) => {
        if (!navigator.geolocation) {
            reject(new Error('Geolocation is not supported by your browser'));
            return;
        }

        navigator.geolocation.getCurrentPosition(
            (position) => {
                resolve({
                    latitude: position.coords.latitude,
                    longitude: position.coords.longitude
                });
            },
            (error) => {
                reject(error);
            }
        );
    });
}

// Button States
const BUTTON_STATES = {
    INITIAL: {
        text: 'Ask for Help',
        classes: ['bg-blue-500', 'hover:bg-blue-600']
    },
    SENDING: {
        text: 'Sending Alert...',
        classes: ['bg-yellow-500']
    },
    SUCCESS: {
        text: 'Help Alert Sent',
        classes: ['bg-green-500']
    },
    ERROR: {
        text: 'Failed - Try Again',
        classes: ['bg-red-500', 'hover:bg-red-600']
    }
};

// Ask for Help Function
async function askForHelp(username) {
    console.log('Asking help for user:', username);
    const button = document.querySelector(`button[data-username="${username}"]`);
    if (!button) {
        console.error('Help button not found for user:', username);
        return;
    }

    button.disabled = true;
    updateButtonState(button, BUTTON_STATES.SENDING);

    try {
        const location = await getCurrentLocation();
        
        const response = await fetch('/api/send-emergency-alert/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'),
            },
            body: JSON.stringify({
                username: username,
                location: location
            })
        });

        const data = await response.json();

        if (data.status === 'success') {
            updateButtonState(button, BUTTON_STATES.SUCCESS);
            
            let messageText = `Alert sent successfully to ${username}`;
            if (data.trusted_contact_messages?.length > 0) {
                messageText += ` and ${data.trusted_contact_messages.length} trusted contacts`;
            }
            showNotification(messageText, 'success');
        } else {
            throw new Error(data.message || 'Failed to send alert');
        }
    } catch (error) {
        console.error('Error sending alert:', error);
        updateButtonState(button, BUTTON_STATES.ERROR);
        button.disabled = false;
        showNotification('Failed to send help alert. Please try again.', 'error');
    }
}

// Button State Update Function
function updateButtonState(button, state) {
    button.classList.remove(
        'bg-blue-500', 'hover:bg-blue-600',
        'bg-yellow-500',
        'bg-green-500',
        'bg-red-500', 'hover:bg-red-600'
    );
    
    button.classList.add(...state.classes);
    button.textContent = state.text;
}

// Notification Function
function showNotification(message, type = 'info') {
    const colors = {
        success: 'bg-green-500',
        error: 'bg-red-500',
        warning: 'bg-yellow-500',
        info: 'bg-blue-500'
    };

    const notification = document.createElement('div');
    notification.className = `fixed bottom-4 right-4 p-4 rounded-lg shadow-lg ${colors[type]} text-white z-50 animate-fade-in`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.classList.add('animate-fade-out');
        setTimeout(() => notification.remove(), 500);
    }, 4500);
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    // Initial update of nearby users
    updateNearbyUsers();
    
    // Set up periodic updates
    setInterval(updateNearbyUsers, 30000); // Update every 30 seconds
});

function toggleEmergencyContacts() {
    const overlay = document.getElementById('emergencyContactsOverlay');
    overlay.classList.toggle('active');
}

function callNumber(number) {
    window.location.href = `tel:${number}`;
}

// Update your emergency contacts button click handler
document.querySelector('a[href="{% url \'trusted_contacts\' %}"]').onclick = function(e) {
    e.preventDefault();
    toggleEmergencyContacts();
};

function makeEmergencyCall() {
    fetch('/make-call/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken(), // Include CSRF token
        },
    })
    .then(response => {
        if (response.ok) {
            alert('Call initiated successfully!');
        } else {
            alert('Failed to initiate the call.');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred while trying to make the call.');
    });
}

function getCSRFToken() {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.startsWith('csrftoken=')) {
            return cookie.substring('csrftoken='.length);
        }
    }
    return '';
}

function createSiren() {
    if (!audioContext) {
        audioContext = new (window.AudioContext || window.webkitAudioContext)();
        gainNode = audioContext.createGain();
        gainNode.connect(audioContext.destination);
    }

    if (audioContext.state === 'suspended') {
        audioContext.resume();
    }
}

function startSiren() {
    if (!isSirenPlaying) {
        createSiren();
        
        sirenOscillator = audioContext.createOscillator();
        sirenOscillator.type = 'sine';
        sirenOscillator.frequency.setValueAtTime(440, audioContext.currentTime);
        sirenOscillator.connect(gainNode);
        sirenOscillator.start();

        sirenInterval = setInterval(() => {
            if (isSirenPlaying) {
                sirenOscillator.frequency.exponentialRampToValueAtTime(
                    880, audioContext.currentTime + 0.5
                );
                setTimeout(() => {
                    if (isSirenPlaying) {
                        sirenOscillator.frequency.exponentialRampToValueAtTime(
                            440, audioContext.currentTime + 0.5
                        );
                    }
                }, 500);
            }
        }, 1000);

        isSirenPlaying = true;
    }
}

function stopSiren() {
    if (isSirenPlaying && sirenOscillator) {
        sirenOscillator.stop();
        sirenOscillator.disconnect();
        sirenOscillator = null;
        clearInterval(sirenInterval);
        isSirenPlaying = false;
    }
}

function toggleSiren() {
    console.log("Siren button clicked");
    console.log("isSirenPlaying:", isSirenPlaying); // Add this for debugging
    const button = document.querySelector('[data-siren-button]');
    console.log("Button found:", button);

    if (!isSirenPlaying) {
        button.classList.add('active');
        startSiren();
    } else {
        button.classList.remove('active');
        stopSiren();
    }
}


window.addEventListener('beforeunload', () => {
    if (isSirenPlaying) {
        stopSiren();
    }
});


// Add these variables at the top of your JavaScript file
let isLocationSharing = false;
let locationWatchId = null;
let currentLocationInterval = null;

// Function to handle location sharing
function toggleLocationSharing() {
    const shareButton = document.getElementById('smsButton');
    
    if (!isLocationSharing) {
        // Start sharing
        startLocationSharing();
        shareButton.textContent = 'Stop Sharing';
        shareButton.classList.remove('bg-purple-100', 'text-purple-600');
        shareButton.classList.add('bg-red-100', 'text-red-600');
    } else {
        // Stop sharing
        stopLocationSharing();
        shareButton.textContent = 'Start Share';
        shareButton.classList.remove('bg-red-100', 'text-red-600');
        shareButton.classList.add('bg-purple-100', 'text-purple-600');
    }
    
    isLocationSharing = !isLocationSharing;
}

// Function to start location sharing
function startLocationSharing() {
    if (navigator.geolocation) {
        // Get initial location
        navigator.geolocation.getCurrentPosition(
            position => sendLocation(position),
            error => {
                console.error("Error getting location:", error);
                alert("Unable to get your location. Please enable GPS.");
            }
        );
        
        // Start watching location
        locationWatchId = navigator.geolocation.watchPosition(
            position => sendLocation(position),
            error => console.error("Error watching location:", error),
            {
                enableHighAccuracy: true,
                timeout: 10000,
                maximumAge: 0
            }
        );
        
        // Set interval to update location every 5 minutes
        currentLocationInterval = setInterval(() => {
            navigator.geolocation.getCurrentPosition(
                position => sendLocation(position),
                error => console.error("Error updating location:", error)
            );
        }, 300000); // 5 minutes
    } else {
        alert("Geolocation is not supported by this browser.");
    }
}

// Function to stop location sharing
function stopLocationSharing() {
    if (locationWatchId !== null) {
        navigator.geolocation.clearWatch(locationWatchId);
        locationWatchId = null;
    }
    
    if (currentLocationInterval !== null) {
        clearInterval(currentLocationInterval);
        currentLocationInterval = null;
    }
    
    // Notify backend to stop sharing
    fetch('/stop-location-sharing/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            showNotification('Location sharing stopped', 'info');
        }
    })
    .catch(error => console.error('Error stopping location sharing:', error));
}

// Function to send location to backend
function sendLocation(position) {
    const { latitude, longitude } = position.coords;
    
    fetch('/share-location/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
        },
        body: JSON.stringify({
            latitude,
            longitude,
            timestamp: new Date().toISOString()
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            showNotification('Location shared successfully', 'success');
        }
    })
    .catch(error => console.error('Error sharing location:', error));
}

// Add event listener to the share button
document.getElementById('smsButton').addEventListener('click', toggleLocationSharing);
function askForHelp(username) {
    alert(`You have requested help from ${username}!`);
    // Add your logic to send a help request, such as an AJAX call or form submission.
}
function handleLogout() {
// Redirect to Django's logout URL
window.location.href = '/logout/';
}
window.onload = function() {
if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
    navigator.mediaDevices.getUserMedia({ audio: true })
        .then(function(stream) {
            console.log('Microphone access granted');
        })
        .catch(function(err) {
            console.error('Error accessing microphone:', err);
            alert('Please allow microphone access for voice detection to work');
        });
}
};