import speech_recognition as sr
import pyttsx3
import datetime
import requests

# Initialize the recognizer and text-to-speech engine
recognizer = sr.Recognizer()
engine = pyttsx3.init()

# WeatherAPI key
API_KEY = "f21f764ed5f0414694a81456242408"  # Replace with your actual WeatherAPI key

def speak(text):
    """Speak the given text."""
    engine.say(text)
    engine.runAndWait()

def listen():
    """Capture and recognize user's voice."""
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source, duration=2)  # Adjust for background noise
        audio = recognizer.listen(source)  # Capture audio input
        try:
            print("Recognizing...")
            query = recognizer.recognize_google(audio, language='en-US')
            print(f"User said: {query}")
            return query.lower()
        except sr.UnknownValueError:
            print("Sorry, I didn't catch that. Can you please repeat?")
            return ""
        except sr.RequestError:
            print("Sorry, my speech service is down.")
            return ""

def get_weather(city):
    """Fetch and return weather information for the given city."""
    base_url = "http://api.weatherapi.com/v1/current.json"
    params = {
        "key": API_KEY,
        "q": city,
        "aqi": "no"  # Optional: set to "yes" if you want air quality information
    }
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        data = response.json()
        temperature = data['current']['temp_c']
        description = data['current']['condition']['text']
        return f"The current temperature in {city} is {temperature}°C with {description}."
    else:
        return "Sorry, I couldn't fetch the weather information at the moment."

def process_command(command):
    """Process the given command."""
    if "weather" in command:
        speak("Sure, for which city would you like the weather update?")
        city = listen()
        if city:
            weather_info = get_weather(city)
            speak(weather_info)

    elif "time" in command:
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        speak(f"The current time is {current_time}")

    elif "date" in command:
        current_date = datetime.date.today().strftime("%B %d, %Y")
        speak(f"Today's date is {current_date}")

    elif "exit" in command or "bye" in command:
        speak("Goodbye! Have a great day!")
        return False

    else:
        speak("I'm not sure how to help with that. Can you please try again?")
    return True

# Main program
speak("Hello! I'm your AI assistant. How can I help you today?")

last_command = None  # Variable to track the last processed command

while True:
    command = listen()
    if command and command != last_command:  # Process only unique commands
        last_command = command
        if not process_command(command):
            break
