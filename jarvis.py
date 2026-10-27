
import webbrowser
import subprocess

import pyttsx3
import pywhatkit
import speech_recognition as sr


# Initialize JARVIS voice
engine = pyttsx3.init()
engine.setProperty("rate", 175)

recognizer = sr.Recognizer()


def speak(message):
    """Speak a message and display it."""
    print(f"JARVIS: {message}")
    engine.say(message)
    engine.runAndWait()


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
        speak(
            "You can ask me to play a song, "
            "open YouTube, open Google, "
            "or open Notepad. Say exit to quit."
        )
        return True

    speak("That command is not supported yet.")
    return True


def main():
    speak("Hello. I am JARVIS.")
    speak("Choose voice mode or text mode.")

    while True:
        mode = input("\nChoose V for voice or T for text: ")
        mode = mode.lower().strip()

        if mode in ("v", "t"):
            break

        print("Please enter V or T.")

    speak("JARVIS is ready.")

    while True:
        if mode == "v":
            command = listen()
        else:
            command = input("\nYOU: ").lower().strip()

        if not handle_command(command):
            break


if __name__ == "__main__":
    main()
