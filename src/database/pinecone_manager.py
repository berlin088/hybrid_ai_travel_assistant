import pinecone
import openai
import os
import time
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()

class PineconeManager:
    def __init__(self):
        self.api_key = os.getenv("PINECONE_API_KEY")
        self.environment = os.getenv("PINECONE_ENVIRONMENT")
        self.index_name = "travel-knowledge"
        
        if not self.api_key or not self.environment:
            raise ValueError("Pinecone API key and environment must be set in .env file")
        
        # Initialize Pinecone with error handling
        self._init_pinecone()

    def _init_pinecone(self):
        """Initialize Pinecone connection with error handling"""
        try:
            pinecone.init(
                api_key=self.api_key,
                environment=self.environment
            )
        except Exception as e:
            raise ConnectionError(f"Failed to initialize Pinecone: {str(e)}")

    def _initialize_index(self, max_retries=3):
        """Initialize Pinecone index with retry logic"""
        for attempt in range(max_retries):
            try:
                # First, check and delete existing index if it exists
                existing_indexes = pinecone.list_indexes()
                if self.index_name in existing_indexes:
                    print(f"Deleting existing index '{self.index_name}'...")
                    pinecone.delete_index(self.index_name)
                    time.sleep(20)  # Wait for deletion to complete
                
                # Create new index with starter (free tier) configuration
                print(f"Creating new index '{self.index_name}'...")
                pinecone.create_index(
                    name=self.index_name,
                    dimension=1536,
                    metric="cosine",
                    pod_type="starter"  # Changed to starter for free tier
                )
                # Wait for index to be ready
                time.sleep(20)
                
                self.index = pinecone.Index(self.index_name)
                print(f"Successfully initialized index '{self.index_name}'")
                break
                
            except Exception as e:
                if "no pod quota available" in str(e).lower():
                    print("Attempting to clean up and recreate index...")
                    # Delete all indexes to free up quota
                    for idx in pinecone.list_indexes():
                        pinecone.delete_index(idx)
                        time.sleep(20)
                    
                    if attempt == max_retries - 1:
                        raise Exception(
                            "Unable to create index. Please ensure:\n"
                            "1. You're using a valid API key\n"
                            "2. You've deleted any unused indexes\n"
                            "3. You're within the free tier limits\n"
                            "Visit https://app.pinecone.io to manage your indexes"
                        )
                    time.sleep(30)  # Wait longer before retry
                    continue
                
                raise Exception(f"Failed to initialize Pinecone index: {str(e)}")

    def get_embedding(self, text: str) -> List[float]:
        """Get embedding for text using OpenAI API"""
        try:
            response = openai.Embedding.create(
                input=text,
                model="text-embedding-ada-002"
            )
            return response['data'][0]['embedding']
        except Exception as e:
            raise Exception(f"Failed to generate embedding: {str(e)}")

    def upsert_texts(self, texts: List[Dict[str, str]], batch_size: int = 50):
        """Upsert texts to Pinecone index with smaller batch size"""
        vectors = []
        for i, text_dict in enumerate(texts):
            embedding = self.get_embedding(text_dict['content'])
            vectors.append((
                str(i),
                embedding,
                {"content": text_dict['content'], "type": text_dict['type']}
            ))
        
        # Upsert in smaller batches
        for i in range(0, len(vectors), batch_size):
            batch = vectors[i:i + batch_size]
            try:
                self.index.upsert(vectors=batch)
                print(f"Upserted batch {i//batch_size + 1}/{len(vectors)//batch_size + 1}")
            except Exception as e:
                raise Exception(f"Failed to upsert batch: {str(e)}")

    def query(self, query_text: str, top_k: int = 5) -> List[Dict]:
        """Query the Pinecone index"""
        try:
            query_embedding = self.get_embedding(query_text)
            results = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True
            )
            return [match.metadata for match in results.matches]
        except Exception as e:
            raise Exception(f"Failed to query index: {str(e)}")