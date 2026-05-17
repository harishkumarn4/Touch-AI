import speech_recognition as sr
import subprocess
import os
import sys
import datetime
import os
import sys

# Add backend directory to sys.path so we can import from automation
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from automation.desktop_env import open_application, search_youtube, play_music, set_volume, shutdown_system


def speak(text):
    """
    Convert text to speech and print it to the console.
    Using PowerShell's built-in SpeechSynthesizer which is 100% thread-safe 
    on Windows, completely avoiding the pyttsx3 'run loop already started' crash.
    """
    print("Touch AI:", text)
    # Escape quotes
    safe_text = str(text).replace('"', "'")
    ps_cmd = f'Add-Type -AssemblyName System.Speech; $synth = New-Object System.Speech.Synthesis.SpeechSynthesizer; $synth.Rate = 1; $synth.Speak("{safe_text}")'
    subprocess.run(["powershell", "-Command", ps_cmd], creationflags=subprocess.CREATE_NO_WINDOW)


def process_command(command):
    """Processes the parsed voice command and executes automation."""
    if not command:
        return

    # Basic Info
    if "hello" in command or "hi" in command:
        speak("Hello! I am Touch AI, your futuristic assistant.")
    elif "time" in command:
        current_time = datetime.datetime.now().strftime("%I:%M %p")
        speak(f"The time is {current_time}")
    elif "date" in command or "today" in command:
        today = datetime.datetime.now().strftime("%d %B %Y")
        speak(f"Today's date is {today}")
    elif "your name" in command:
        speak("My name is Touch AI.")
        
    # Automation Commands
    elif "open" in command:
        # e.g. "open chrome"
        app_name = command.replace("open", "").strip()
        if app_name:
            result = open_application(app_name)
            speak(result)
        else:
            speak("What application should I open?")
            
    elif "search youtube" in command:
        # e.g. "search youtube for python tutorials"
        query = command.replace("search youtube for", "").replace("search youtube", "").strip()
        if query:
            result = search_youtube(query)
            speak(result)
        else:
            speak("What should I search for on YouTube?")
            
    elif "play music" in command or "pause music" in command:
        result = play_music()
        speak(result)
        
    elif "increase volume" in command or "volume up" in command:
        result = set_volume("up")
        speak(result)
        
    elif "decrease volume" in command or "volume down" in command:
        result = set_volume("down")
        speak(result)
        
    elif "mute" in command:
        result = set_volume("mute")
        speak(result)
        
    elif "shutdown system" in command or "shut down system" in command:
        # Only issue actual shutdown if we have confirmation logic, 
        # for now let's just warn or do it if they really say "shutdown system please"
        if "please" in command:
            result = shutdown_system(confirm=True)
            speak(result)
        else:
            speak("Please say 'shutdown system please' to confirm.")
            
    # Unknown
    else:
        speak("I heard " + command + " but I don't know how to do that yet.")


def start_voice_assistant():
    """
    Start the voice assistant:
    - Listens to microphone input
    - Recognizes speech using Google Speech Recognition
    - Responds to basic commands
    """

    recognizer = sr.Recognizer()

    # Speak startup message
    speak("Voice assistant is online. Listening for commands.")

    # Listen from microphone
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=1)
        print("Listening...")

        try:
            # Wait up to 5 seconds for user to start speaking
            # Limit speech to 5 seconds
            audio = recognizer.listen(
                source,
                timeout=5,
                phrase_time_limit=5
            )
        except sr.WaitTimeoutError:
            print("Did not hear anything.")
            return

    try:
        # Convert speech to text
        command = recognizer.recognize_google(audio).lower()
        print("You said:", command)
        
        # Process the command
        process_command(command)

    except sr.UnknownValueError:
        speak("Sorry, I could not understand.")

    except sr.RequestError:
        speak("Speech recognition service is unavailable.")

    except Exception as e:
        print("Error:", e)
        speak("An unexpected error occurred.")