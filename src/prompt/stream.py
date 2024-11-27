# Function to stream the assistant's response
from src.db.vector_db import ollama, Fore
from src.db.database import store_conversations
from src.utils.libraries import convo

def stream_response(prompt):
    """Streams the assistant's response to a prompt."""
    response = ''
    stream = ollama.chat(model='llama3',  messages=convo, stream=True, options={
        "temperature": 0.5,  # Adjusted temperature
        "top_k": 100,
        "top_p": 0.5,
        "prompt_eval_count": 26
        # Add other options as needed
    })
    print(Fore.LIGHTGREEN_EX + '\nASSISTANT:')

    for chunk in stream:
        content = chunk['message']['content']
        response += content
        print(content, end='', flush=True)

    print('\n')
    store_conversations(prompt=prompt, response=response)
    convo.append({'role': 'assistant', 'content': response})