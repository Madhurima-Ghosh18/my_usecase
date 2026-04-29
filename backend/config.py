import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Jira
    JIRA_SERVER    = os.getenv('JIRA_SERVER')
    JIRA_EMAIL     = os.getenv('JIRA_EMAIL')
    JIRA_API_TOKEN = os.getenv('JIRA_API_TOKEN')
    JIRA_PROJECT   = os.getenv('JIRA_PROJECT')

    # HuggingFace
    HUGGINGFACE_API_KEY = os.getenv('HUGGINGFACE_API_KEY')
    MODEL_NAME          = os.getenv('MODEL_NAME')

    # FAISS
    FAISS_DB_PATH       = os.getenv('FAISS_DB_PATH')
    EMBEDDING_MODEL      = os.getenv('EMBEDDING_MODEL')
    SIMILARITY_THRESHOLD = float(os.getenv('SIMILARITY_THRESHOLD', '0.3'))

    # SQLite
    DATABASE_PATH = os.getenv('DATABASE_PATH')