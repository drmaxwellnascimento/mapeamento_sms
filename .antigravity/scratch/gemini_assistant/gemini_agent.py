import os
import google.generativeai as genai
from google.generativeai.types import FunctionDeclaration, Tool
from dotenv import load_dotenv
import logging
from windows_tools import TOOLS_MAP

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class GeminiAgent:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            logging.warning("GEMINI_API_KEY not found in environment variables.")
        
        genai.configure(api_key=self.api_key)
        
        # Define tools for Gemini
        self.tools = self._define_tools()
        
        # Initialize model
        self.model = genai.GenerativeModel(
            model_name='gemini-1.5-flash', # Using flash for speed
            tools=self.tools,
            system_instruction="""You are a helpful Windows voice assistant. 
            You can control the computer using the provided tools. 
            Keep your responses concise and conversational, suitable for voice output.
            If a user asks to do something you can't do, explain why.
            Always confirm actions briefly before or after doing them.
            """
        )
        
        self.chat = self.model.start_chat(enable_automatic_function_calling=True)

    def _define_tools(self):
        """Defines the tools available to the model."""
        # In the Python SDK, we can pass the functions directly!
        return [
            TOOLS_MAP["open_application"],
            TOOLS_MAP["minimize_windows"],
            TOOLS_MAP["type_text"],
            TOOLS_MAP["press_hotkey"],
            TOOLS_MAP["get_system_time"]
        ]

    def send_message(self, message):
        """Sends a message to Gemini and returns the response text."""
        try:
            logging.info(f"Sending to Gemini: {message}")
            response = self.chat.send_message(message)
            return response.text
        except Exception as e:
            logging.error(f"Error communicating with Gemini: {e}")
            return "Sorry, I encountered an error communicating with my brain."

if __name__ == "__main__":
    # Test
    agent = GeminiAgent()
    if agent.api_key:
        print(agent.send_message("What time is it?"))
    else:
        print("No API key found. Please set GEMINI_API_KEY.")
