
#only text

from flask import Flask, request, jsonify, render_template
from flask import send_from_directory
import os
import pyttsx3
import threading
import speech_recognition as sr  # 🔥 NEW

from weather import get_weather
from datetime import datetime, timedelta
from pytz import timezone

# Import your other modules
from reminder import (
    parse_reminder_input,
    parse_date_expression,
    parse_time_expression,
    set_reminder,
    check_reminders,
    speak
)

from gcalendar import (
    get_calendar_service,
    create_event,
    parse_command,
    extract_date,
    extract_time
)

# Create Flask app
app = Flask(__name__, static_folder='static')

# Initialize TTS engine
def init_tts():
    global tts_engine
    if not hasattr(app, 'tts_engine'):
        app.tts_engine = pyttsx3.init()
    return app.tts_engine

# Store reminders
app.reminders = []
app.recurring_reminders = []

def drop_message(message):
    print("\n" + "=" * 40)
    print(f"REMINDER: {message}")
    print("=" * 40 + "\n")
    engine = init_tts()
    engine.say(f"Reminder: {message}")
    engine.runAndWait()

# Serve static files
@app.route('/<path:path>')
def serve_static(path):
    if os.path.exists(path):
        return send_from_directory('.', path)
    return app.send_static_file(path)

# Home page
@app.route("/")
def index():
    return render_template("index.html")

# Weather
@app.route("/get_weather", methods=["POST"])
def weather():
    city = request.form["city"]
    weather_info = get_weather(city)
    return jsonify({"weather": weather_info})

# Reminder
@app.route("/set_reminder", methods=["POST"])
def set_reminder_route():
    try:
        data = request.json
        input_text = data['input_text']
        response = set_reminder(input_text)
        return jsonify({'status': 'success', 'message': response})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

# Schedule meeting
@app.route("/schedule_meeting", methods=["POST"])
def schedule_meeting():
    try:
        data = request.get_json()
        command = data['command']
        summary, start_time = parse_command(command)

        end_time = start_time + timedelta(hours=1)
        india_tz = timezone('Asia/Kolkata')

        if start_time.tzinfo is None:
            start_time = india_tz.localize(start_time)
        if end_time.tzinfo is None:
            end_time = india_tz.localize(end_time)

        success, message = create_event(
            start_time=start_time,
            end_time=end_time,
            summary=summary
        )

        return jsonify({'status': 'success', 'message': message})

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

#  NEW VOICE COMMAND FEATURE
@app.route("/voice_command")
def voice_command():
    recognizer = sr.Recognizer()

    try:
        with sr.Microphone() as source:
            print("Listening...")
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source)

        command = recognizer.recognize_google(audio).lower()
        print("You said:", command)

        # Logic
        if "weather" in command:
            if "in" in command:
                city = command.split("in")[-1].strip()
            else:
                city = "Pune"
            result = get_weather(city)
            return jsonify({"message": result})

        elif "reminder" in command:
            response = set_reminder(command)
            return jsonify({"message": response})

        elif "time" in command:
            now = datetime.now().strftime("%H:%M:%S")
            return jsonify({"message": f"Current time is {now}"})

        else:
            return jsonify({"message": f"You said: {command}"})

    except Exception as e:
        return jsonify({"message": str(e)})

# Run app
if __name__ == "__main__":
    reminder_thread = threading.Thread(target=check_reminders, daemon=True)
    reminder_thread.start()

    app.run(debug=True)



