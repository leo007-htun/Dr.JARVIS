import chromadb
import psycopg
from psycopg.rows import dict_row
import os
from dotenv import load_dotenv
import logging

client = chromadb.Client()

# Logging setup
#logging.basicConfig(level=logging.INFO)
#logger = logging.getLogger(__name__)

# Database connection parameters
load_dotenv()


# Now you can access your environment variables
DB_PARAMS = {
    'dbname': os.getenv('DB_NAME'),      
    'user': os.getenv('DB_USER'),         
    'password': os.getenv('DB_PASSWORD'), 
    'host': os.getenv('DB_HOST'),        
    'port': os.getenv('DB_PORT')       
}

# Function to connect to the database
"""Connects to the PostgreSQL database."""
def connect_db():

    connection = psycopg.connect(**DB_PARAMS)
    return connection

# Function to fetch conversations from the database
def fetch_conversations():
    """Fetches all conversations from the database."""
    conn = connect_db()
    with conn.cursor(row_factory=dict_row) as cursor:
        cursor.execute('SELECT * FROM conversations')
        conversations = cursor.fetchall()
    conn.close()
    return conversations

# Function to store conversations in the database
def store_conversations(prompt, response):
    """Stores a conversation prompt and response in the database."""
    conn = connect_db()
    with conn.cursor() as cursor:
        cursor.execute(
            'INSERT INTO conversations (timestamp, prompt, response) VALUES (CURRENT_TIMESTAMP, %s, %s)',
            (prompt, response)
        )
        conn.commit()
    conn.close()

# Function to remove the last conversation from the database
def remove_last_conversation():
    """Removes the last conversation from the database."""
    conn = connect_db()
    with conn.cursor() as cursor:
        cursor.execute('DELETE FROM conversations WHERE id = (SELECT MAX(id) FROM conversations)')
        conn.commit()
    conn.close()

