from models.chatbot_responses import MentalHealthChatbot
import time

def test_chatbot():
    print("Initializing chatbot... This may take a few moments to download the model.")
    chatbot = MentalHealthChatbot()
    print("\nChatbot is ready! You can start chatting. Type 'quit' to exit.\n")

    while True:
        user_input = input("\nYou: ")
        
        if user_input.lower() == 'quit':
            print("\nGoodbye! Take care!")
            break
        
        print("\nProcessing...")
        start_time = time.time()
        
        response = chatbot.get_response(user_input)
        
        # Get suggestions for next messages
        suggestions = chatbot.get_suggestions()
        
        print(f"\nAI Health Assistant: {response}\n")
        print("Suggested responses:")
        for i, suggestion in enumerate(suggestions, 1):
            print(f"{i}. {suggestion}")
        
        end_time = time.time()
        print(f"\nResponse time: {end_time - start_time:.2f} seconds")

if __name__ == "__main__":
    try:
        test_chatbot()
    except KeyboardInterrupt:
        print("\n\nChat ended by user. Take care!")
    except Exception as e:
        print(f"\nAn error occurred: {str(e)}")
        print("Please make sure you have installed all required packages:")
        print("pip install transformers torch") 