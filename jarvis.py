
import webbrowser
import subprocess
import threading
import queue

import pyttsx3
import pywhatkit
import speech_recognition as sr

from calendar_reminders import start_reminder_monitor

# Initialize JARVIS speech queue
speech_queue = queue.Queue()

recognizer = sr.Recognizer()




def speech_worker():
    """Handle all speech using one dedicated thread."""
    try:
        engine = pyttsx3.init()
        engine.setProperty("rate", 175)

        while True:
            item = speech_queue.get()

            if item is None:
                speech_queue.task_done()
                break

            message, done_event = item

            try:
                engine.say(message)
                engine.runAndWait()

            except Exception as error:
                print(f"Voice engine error: {error}")
            finally:
                done_event.set()
                speech_queue.task_done()

    except Exception as error:
        print(f"Voice worker failed: {error}")



def speak(message):
    """Display a message and speak it safely."""
    print(f"JARVIS: {message}")

    done_event = threading.Event()
    speech_queue.put((message, done_event))
    done_event.wait()


def listen():
    """Listen for an English voice command."""
    try:
        with sr.Microphone() as source:
            print("\nListening... Speak now.")
            recognizer.adjust_for_ambient_noise(
                source, duration=0.5
            )
            audio = recognizer.listen(
                source,
                timeout=5,
                phrase_time_limit=8
            )

        command = recognizer.recognize_google(
            audio, language="en-US"
        )
        print(f"YOU: {command}")
        return command.lower().strip()

    except sr.WaitTimeoutError:
        print("No speech detected.")
    except sr.UnknownValueError:
        speak("Sorry, I did not understand.")
    except sr.RequestError:
        speak("Speech recognition needs an internet connection.")
    except OSError:
        speak("I cannot access the microphone.")

    return ""


def handle_command(command):
    """Handle supported commands."""

    if not command:
        return True

    if command in ("exit", "quit", "goodbye"):
        speak("Goodbye. JARVIS is shutting down.")
        return False

    if command.startswith("play "):
        song = command[5:].strip()

        if song:
            speak(f"Searching YouTube for {song}.")
            try:
                pywhatkit.playonyt(song)
                speak("I have opened the song.")
            except Exception as error:
                print(f"Playback error: {error}")
                speak("Sorry, I could not play that song.")

        return True

    if command in ("open youtube", "youtube"):
        webbrowser.open("https://www.youtube.com")
        speak("Opening YouTube.")
        return True

    if command in ("open google", "google"):
        webbrowser.open("https://www.google.com")
        speak("Opening Google.")
        return True

    if command in ("open notepad", "start notepad"):
        subprocess.Popen(["notepad.exe"])
        speak("Opening Notepad.")
        return True

    if command in ("help", "what can you do"):
        message = (
        "You can ask me to play a song, "
        "open YouTube, open Google, "
        "or open Notepad. Say exit to quit."
    )

    print(f"JARVIS: {message}")

    test_engine = pyttsx3.init()
    test_engine.setProperty("rate", 175)
    test_engine.say(message)
    test_engine.runAndWait()
    test_engine.stop()

    return True

    speak("That command is not supported yet.")
    return True


def main():
    voice_thread = threading.Thread(
        target=speech_worker,
        daemon=True,
    )
    voice_thread.start()

    speak("Hello. I am JARVIS.")

    reminder_stop_event = threading.Event()
    reminder_stop_event = start_reminder_monitor(speak)
    
    speak("Choose voice mode or text mode.")

    while True:
        mode = input("\nChoose V for voice or T for text: ")
        mode = mode.lower().strip()

        if mode in ("v", "t"):
            break

        print("Please enter V or T.")

    speak("JARVIS is ready.")

    try:
        while True:
            if mode == "v":
                command = listen()
            else:
                command = input("\nYOU: ").lower().strip()

            if not handle_command(command):
                break

    finally:
        reminder_stop_event.set()
        speak("JARVIS reminder monitor stopped.")


if __name__ == "__main__":
    main()
