import time
import logging
from audio_manager import AudioManager
from gemini_agent import GeminiAgent
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    logging.info("Starting Gemini Windows Assistant...")
    
    # Check for API Key
    if not os.getenv("GEMINI_API_KEY"):
        logging.error("GEMINI_API_KEY not found. Please set it in a .env file or environment variables.")
        print("Error: GEMINI_API_KEY not found.")
        return

    try:
        audio = AudioManager()
        agent = GeminiAgent()
        
        audio.speak("Olá, eu sou o seu assistente Windows. Como posso ajudar?")
        
        while True:
            # Listen for command
            user_input = audio.listen()
            
            if user_input:
                # Check for exit command
                if "sair" in user_input.lower() or "encerrar" in user_input.lower():
                    audio.speak("Até logo!")
                    break
                
                # Send to Gemini
                response = agent.send_message(user_input)
                
                # Speak response
                if response:
                    audio.speak(response)
            
            # Small delay to prevent CPU hogging if listen returns immediately (though it shouldn't)
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        logging.info("Stopped by user.")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        audio.speak("Ocorreu um erro inesperado.")

if __name__ == "__main__":
    main()
