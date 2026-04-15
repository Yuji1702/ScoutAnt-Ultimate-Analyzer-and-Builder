import sys
import os

# Add project root to path
sys.path.append('C:/Users/dhruv/OneDrive/Desktop/ScoutAnt-Ultimate-Analyzer-and-Builder')

try:
    from analytics_system.chatbot import ValorantChatbot

    bot = ValorantChatbot()

    test_queries = [
        "What is the best agent for Tenz on Bind?",
        "How to counter Fade on Bind?",
        "Tell me about Aspas",
        "Predict Tenz vs PatMen on Bind",
        "Optimize team for Tenz, Aspas, Leo, Less, Saadhak on Bind",
        "I want to know who wins a match between Tenz and PatMen on Bind",
        "What's the best way to stop a Raze on Bind?"
    ]

    print("--- VALORANT CHATBOT INTEGRATION TEST ---")
    for query in test_queries:
        print(f"\nUser: {query}")
        print(f"Bot: {bot.handle_query(query)}")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
