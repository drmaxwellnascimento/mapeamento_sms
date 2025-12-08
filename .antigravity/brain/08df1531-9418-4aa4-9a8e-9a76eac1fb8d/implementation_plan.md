# Implementation Plan - Gemini Windows Voice Assistant

## Goal Description
Create a semi-autonomous voice assistant for Windows using Google's Gemini model. The assistant will listen for voice commands, process them using Gemini, and execute Windows actions (opening apps, system control) or reply via voice "just in time".

## User Review Required
> [!IMPORTANT]
> **API Key**: The user will need to provide a valid Google Gemini API key.
> **Microphone/Speakers**: Ensure the system has a working microphone and speakers.

## Proposed Changes

### Project Structure
We will create a new Python project in `C:\Users\drmax\.gemini\antigravity\scratch\gemini_assistant`.

#### [NEW] [requirements.txt](file:///C:/Users/drmax/.gemini/antigravity/scratch/gemini_assistant/requirements.txt)
- `google-generativeai`: For Gemini API.
- `SpeechRecognition`: For converting speech to text.
- `pyttsx3`: For text-to-speech (offline, low latency).
- `pyaudio`: Audio I/O dependency.
- `pyautogui`: For basic UI automation.
- `python-dotenv`: To manage API keys.

#### [NEW] [audio_manager.py](file:///C:/Users/drmax/.gemini/antigravity/scratch/gemini_assistant/audio_manager.py)
- `listen()`: Captures audio from microphone and converts to text.
- `speak(text)`: Converts text to speech.

#### [NEW] [windows_tools.py](file:///C:/Users/drmax/.gemini/antigravity/scratch/gemini_assistant/windows_tools.py)
- Defines tools that Gemini can call:
    - `open_application(app_name)`
    - `minimize_windows()`
    - `type_text(text)`
    - `press_hotkey(keys)`
    - `get_system_time()`

#### [NEW] [gemini_agent.py](file:///C:/Users/drmax/.gemini/antigravity/scratch/gemini_assistant/gemini_agent.py)
- Initializes the Gemini model with system instructions.
- Manages chat history.
- Handles function calling execution.

#### [NEW] [main.py](file:///C:/Users/drmax/.gemini/antigravity/scratch/gemini_assistant/main.py)
- Main loop:
    1. Listen for input.
    2. Send to Gemini.
    3. Execute tool calls (if any).
    4. Speak response.

## Verification Plan

### Automated Tests
- We will create a simple script to verify microphone input and TTS output.
- We will test the Gemini connection with a "Hello World" prompt.

### Manual Verification
- Run the assistant and ask it to "Open Notepad".
- Ask general questions to verify voice response.
