

// function showResponse(elementId, message, isLoading = false) {
//     const element = document.getElementById(elementId);
//     element.style.display = 'block';
//     element.classList.add('visible');
//     element.innerHTML = isLoading ? 
//         `<i class="fas fa-spinner loading"></i> ${message}` : message;
// }

// // 🌦 WEATHER
// async function getWeather() {
//     const city = document.getElementById('city').value;
//     if (!city) {
//         showResponse('weatherResponse', 'Please enter a city name');
//         return;
//     }

//     showResponse('weatherResponse', 'Getting weather information...', true);

//     try {
//         const response = await fetch('/get_weather', {
//             method: 'POST',
//             headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
//             body: new URLSearchParams({ 'city': city })
//         });
//         const data = await response.json();
//         showResponse('weatherResponse', data.weather);
//     } catch (error) {
//         showResponse('weatherResponse', 'Error getting weather information');
//     }
// }

// // 🔔 REMINDER
// async function setReminder() {
//     const reminderInput = document.getElementById('reminder_input').value;
//     if (!reminderInput) {
//         showResponse('reminderResponse', 'Please enter a reminder');
//         return;
//     }

//     showResponse('reminderResponse', 'Setting reminder...', true);

//     try {
//         const response = await fetch('/set_reminder', {
//             method: 'POST',
//             headers: { 'Content-Type': 'application/json' },
//             body: JSON.stringify({ 'input_text': reminderInput })
//         });
//         const data = await response.json();
//         showResponse('reminderResponse', data.message);
//     } catch (error) {
//         showResponse('reminderResponse', 'Error setting reminder');
//     }
// }

// // 📅 MEETING
// async function scheduleMeeting() {
//     const command = document.getElementById('meeting-command').value;
//     if (!command) {
//         showResponse('meetingResponse', 'Please enter meeting details');
//         return;
//     }

//     const description = document.getElementById('meeting-description').value;
//     const location = document.getElementById('meeting-location').value;

//     showResponse('meetingResponse', 'Scheduling meeting...', true);

//     try {
//         const response = await fetch('/schedule_meeting', {
//             method: 'POST',
//             headers: { 'Content-Type': 'application/json' },
//             body: JSON.stringify({
//                 command,
//                 description,
//                 location
//             })
//         });
//         const data = await response.json();
//         showResponse('meetingResponse', data.status === 'success' ? 
//             data.message : 'Error: ' + data.message);
//     } catch (error) {
//         showResponse('meetingResponse', 'Error scheduling meeting');
//     }
// }

// // 🎤 VOICE ASSISTANT (NEW FEATURE 🔥)
// async function startVoiceAssistant() {
//     showResponse('voiceResponse', 'Listening...', true);

//     try {
//         const response = await fetch('/voice_command');
//         const data = await response.json();

//         showResponse('voiceResponse', data.message);

//     } catch (error) {
//         showResponse('voiceResponse', 'Error in voice assistant');
//     }
// }

function showResponse(elementId, message, isLoading = false) {
    const element = document.getElementById(elementId);

    if (!element) {
        console.error("Element not found:", elementId);
        return;
    }

    element.style.display = 'block';
    element.classList.add('visible');

    element.innerHTML = isLoading 
        ? `<i class="fas fa-spinner loading"></i> ${message}` 
        : message;
}

// 🌦 WEATHER
async function getWeather() {
    const city = document.getElementById('city').value;

    if (!city) {
        showResponse('weatherResponse', 'Enter city name');
        return;
    }

    showResponse('weatherResponse', 'Getting weather...', true);

    try {
        const response = await fetch('/get_weather', {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: new URLSearchParams({ city })
        });

        const data = await response.json();
        showResponse('weatherResponse', data.weather);

    } catch {
        showResponse('weatherResponse', 'Error fetching weather');
    }
}

// 🔔 REMINDER
async function setReminder() {
    const input = document.getElementById('reminder_input').value;

    if (!input) {
        showResponse('reminderResponse', 'Enter reminder');
        return;
    }

    showResponse('reminderResponse', 'Setting...', true);

    try {
        const response = await fetch('/set_reminder', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ input_text: input })
        });

        const data = await response.json();
        showResponse('reminderResponse', data.message);

    } catch {
        showResponse('reminderResponse', 'Error setting reminder');
    }
}

// 📅 MEETING
async function scheduleMeeting() {
    const command = document.getElementById('meeting-command').value;
    const description = document.getElementById('meeting-description').value;
    const location = document.getElementById('meeting-location').value;

    if (!command) {
        showResponse('meetingResponse', 'Enter meeting details');
        return;
    }

    showResponse('meetingResponse', 'Scheduling...', true);

    try {
        const response = await fetch('/schedule_meeting', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ command, description, location })
        });

        const data = await response.json();
        showResponse('meetingResponse', data.message);

    } catch {
        showResponse('meetingResponse', 'Error scheduling meeting');
    }
}

// 🎤 VOICE
async function startVoiceAssistant() {
    showResponse('voiceResponse', 'Listening...', true);

    try {
        const response = await fetch('/voice_command');
        const data = await response.json();

        showResponse('voiceResponse', data.message);

    } catch {
        showResponse('voiceResponse', 'Voice error');
    }
}