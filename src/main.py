from src.db.database import fetch_conversations, remove_last_conversation, store_conversations, connect_db
from src.db.vector_db import create_vector_db, Fore, recall
from src.prompt.stream import stream_response
from src.utils.libraries import convo

# Main execution flow
if __name__ == "__main__":

    conversations = fetch_conversations()

    if connect_db():
        print('\nCONNECTION ESTABLISHED ...\n\nLOADING PARAMETERS ...\n')

    create_vector_db(conversations=conversations)



    while True:
        # Prompt user for input
        prompt = input(Fore.WHITE + 'YOU:\n')

        # Check if the input is a recall command
        if prompt.lower().startswith('/recall'):
            prompt = prompt[8:]  # Remove the command prefix
            recall(prompt=prompt)  # Recall memories related to the prompt

        elif prompt.lower().startswith('/forget'):
            remove_last_conversation()
            convo.pop()  # Remove the last assistant response
            convo.pop()  # Remove the last user input
            print('\n')

        elif prompt.lower().startswith('/memorize'):
            prompt = prompt[10:]  # Remove the command prefix
            store_conversations(prompt=prompt, response='Memory Stored!!!')
            print('\n')

        else:
            convo.append({'role': 'user', 'content': prompt})  # Add user input to the conversation

        # Generate and stream the response
        stream_response(prompt=prompt)