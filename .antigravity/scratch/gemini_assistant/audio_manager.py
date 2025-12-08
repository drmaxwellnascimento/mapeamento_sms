import speech_recognition as sr
import pyttsx3
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class AudioManager:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.engine = pyttsx3.init()
        self._setup_voice()

    def _setup_voice(self):
        """Configures the TTS voice to be more natural if possible."""
        voices = self.engine.getProperty('voices')
        # Try to find a Portuguese voice if available, or a good English one
        for voice in voices:
            if "brazil" in voice.name.lower() or "portuguese" in voice.name.lower():
                self.engine.setProperty('voice', voice.id)
                break
        
        self.engine.setProperty('rate', 180) # Speed of speech

    def listen(self):
        """Listens to the microphone and returns the recognized text."""
        with sr.Microphone() as source:
            logging.info("Listening...")
            self.recognizer.adjust_for_ambient_noise(source)
            try:
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                logging.info("Processing audio...")
                text = self.recognizer.recognize_google(audio, language="pt-BR")
                logging.info(f"User said: {text}")
                return text
            except sr.WaitTimeoutError:
                logging.info("Listening timed out.")
                return None
            except sr.UnknownValueError:
                logging.info("Could not understand audio.")
                return None
            except sr.RequestError as e:
                logging.error(f"Could not request results; {e}")
                return None
            except Exception as e:
                logging.error(f"Error listening: {e}")
                return None

    def speak(self, text):
        """Converts text to speech."""
        if not text:
            return
        logging.info(f"Assistant: {text}")
        self.engine.say(text)
        self.engine.runAndWait()

if __name__ == "__main__":
    # Test
    audio = AudioManager()
    audio.speak("Olá, sistema de áudio iniciado.")
