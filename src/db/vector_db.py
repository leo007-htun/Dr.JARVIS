import ollama
from src.db.database import client
from tqdm import tqdm
from colorama import Fore
import ast
from src.utils.libraries import convo

# Function to create a vector database from conversations
def create_vector_db(conversations):
    """Creates a vector database from existing conversations."""
    vector_db_name = 'conversations'

    # Attempt to delete the existing collection if it exists
    try:
        client.delete_collection(name=vector_db_name)
    except ValueError:
        pass

    vector_db = client.create_collection(name=vector_db_name)

    for c in conversations:
        serialized_convo = f"prompt: {c['prompt']} response: {c['response']}"
        response = ollama.embeddings(model='nomic-embed-text', prompt=serialized_convo)
        embedding = response['embedding']

        vector_db.add(
            ids=[str(c['id'])],
            embeddings=[embedding],
            documents=[serialized_convo]
        )

# Function to create queries for the embedding database
def create_queries(prompt):
    """Creates a list of search queries to retrieve relevant conversations."""
    query_msg = (
        'You are a first-principles reasoning search query AI agent. '
        'Your list of search queries will be run on an embedding database of all conversations you have had with the user. '
        'With first principles, create a Python list of queries to search the embeddings database for any data that would be necessary to correctly respond to the prompt. '
        'Your response must be a Python list with no syntax errors. '
        'Do not explain anything and do not generate anything but a perfect syntax Python list.'
    )

    query_convo = [
        {'role': 'system', 'content': query_msg},
        {'role': 'user', 'content': 'What is machine learning?'},
        {'role': 'assistant', 'content': 'Machine learning is a field of AI focused on enabling systems to learn from data and improve over time without being explicitly programmed.'},
        {'role': 'user', 'content': 'Can you give an example of machine learning?'},
        {'role': 'assistant', 'content': 'Sure! A common example is spam filtering in emails. The system learns to classify emails as spam or not spam based on patterns in previous emails.'},
        {'role': 'user', 'content': prompt}
    ]

    response = ollama.chat(model='llama3', messages=query_convo)
    print(Fore.YELLOW + f'\nVector database queries: {response["message"]["content"]}\n')

    try:
        return ast.literal_eval(response['message']['content'])
    except Exception as e:
        print(f"Error parsing response: {e}")
        return [prompt]

# Function to retrieve relevant embeddings based on queries
def retrieve_embeddings(queries, results_per_query=2):
    """Retrieves embeddings from the vector database based on the queries."""
    embeddings = set()

    for query in tqdm(queries, desc='Processing queries to vector database'):
        response = ollama.embeddings(model='nomic-embed-text', prompt=query)
        query_embedding = response['embedding']
        vector_db = client.get_collection(name='conversations')
        results = vector_db.query(query_embeddings=[query_embedding], n_results=results_per_query)
        best_embeddings = results['documents'][0]

        for best in best_embeddings:
            if best not in embeddings:
                if 'yes' in classify_embedding(query=query, context=best):
                    embeddings.add(best)

    return embeddings

# Function to classify embeddings based on query relevance
def classify_embedding(query, context):
    """Classifies whether the context is relevant to the search query."""
    classify_msg = (
        'You are an embedding classification AI agent. Your input will be a prompt and one embedded chunk of text. '
        'You will not respond as an AI assistant. You only respond "yes" or "no". '
        'Determine whether the context contains data that directly relates to the search query. '
        'If the context is exactly what the search query needs, respond "yes"; otherwise respond "no".'
    )

    classify_convo = [
        {'role': 'system', 'content': classify_msg},
        {'role': 'user', 'content': f'SEARCH QUERY: {query}\nEMBEDDED CONTEXT: {context}'}
    ]

    response = ollama.chat(model='llama3', messages=classify_convo)
    return response['message']['content'].strip().lower()

# Function to recall memories based on the user prompt
def recall(prompt):
    """Recalls memories related to the user prompt."""
    queries = create_queries(prompt=prompt)
    embeddings = retrieve_embeddings(queries=queries)
    convo.append({'role': 'user', 'content': f'MEMORIES: {embeddings}\n\nUSER PROMPT: {prompt}'})
    print(f'\n{len(embeddings)} message:response embeddings added for context')
