"""
app.py
Friday - Desktop assistant with BOTH text chat and voice ("Hey Friday").
Uses the real Gemini-powered Agent (agent.py) as the brain for both.
"""

import sys
import threading
import time

import webview
import speech_recognition as sr
import pyttsx3
import pyaudiowpatch as pyaudio

from agent import Agent

sys.modules["pyaudio"] = pyaudio


class Api:
    def __init__(self):
        self.agent = Agent()
        self.engine = pyttsx3.init()
        self.engine.setProperty("rate", 165)
        self.engine.setProperty("volume", 1.0)

        self.running = True
        self.is_speaking = threading.Event()
        self.speak_lock = threading.Lock()

        self.wake_thread = threading.Thread(target=self.wake_word_loop, daemon=True)
        self.wake_thread.start()

    def send_message(self, message: str) -> str:
        try:
            return self.agent.chat(message)
        except Exception as e:
            return f"Error: {e}"

    def speak(self, text):
        with self.speak_lock:
            self.is_speaking.set()
            try:
                print("Friday:", text)
                self.engine.stop()
                self.engine.say(text)
                self.engine.runAndWait()
            except Exception as e:
                print("Speech error:", e)
            finally:
                time.sleep(0.5)
                self.is_speaking.clear()

    def listen_once(self, timeout=7, phrase_time_limit=10):
        recognizer = sr.Recognizer()
        try:
            with sr.Microphone() as source:
                print("Listening...")
                recognizer.adjust_for_ambient_noise(source, duration=0.3)
                audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
            text = recognizer.recognize_google(audio)
            print("You said:", text)
            return text
        except (sr.WaitTimeoutError, sr.UnknownValueError):
            return ""
        except sr.RequestError as e:
            print("Speech recognition service error:", e)
            return ""
        except Exception as e:
            print("Voice error:", e)
            return ""

    def listen_voice(self):
        try:
            command = self.listen_once()
            if not command:
                return "I didn't catch that. Try again."
            reply = self.agent.chat(command)
            self.speak(reply)
            return reply
        except Exception as e:
            return f"Voice error: {e}"

    def wake_word_loop(self):
        recognizer = sr.Recognizer()
        print("\nSay 'Hey Friday' to activate voice mode.\n")

        while self.running:
            try:
                if self.is_speaking.is_set():
                    time.sleep(0.2)
                    continue

                with sr.Microphone() as source:
                    audio = recognizer.listen(source, phrase_time_limit=5)

                if self.is_speaking.is_set():
                    continue

                try:
                    text = recognizer.recognize_google(audio).lower()
                except sr.UnknownValueError:
                    continue
                except sr.RequestError:
                    time.sleep(2)
                    continue

                if "hey friday" in text:
                    self.speak("Yes? How can I help?")
                    command = self.listen_once()

                    if command:
                        reply = self.agent.chat(command)
                        self.speak(reply)
                    else:
                        self.speak("I didn't catch that.")

                    print("\nWaiting for 'Hey Friday'...\n")

            except Exception as e:
                print("Wake listener error:", e)
                time.sleep(1)


if __name__ == "__main__":
    api = Api()
    window = webview.create_window(
        "Friday - Personal AI Assistant",
        "ui.html",
        js_api=api,
        width=900,
        height=650,
        min_size=(500, 400)
    )
    webview.start()
    api.running = False