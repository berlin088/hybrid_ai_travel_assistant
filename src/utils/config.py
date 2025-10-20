import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Neo4j Configuration
    NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
    NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

    # Pinecone Configuration
    PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
    PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT")
    PINECONE_INDEX_NAME = "travel-knowledge"
    PINECONE_DIMENSION = 1536  # For OpenAI embeddings

    # OpenAI Configuration
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL = "gpt-4"
    EMBEDDING_MODEL = "text-embedding-ada-002"

    # Application Configuration
    BATCH_SIZE = 100
    MAX_TOKENS = 500
    TEMPERATURE = 0.7
    TOP_K_RESULTS = 5