import openai
import os
from typing import Dict, List
from dotenv import load_dotenv

load_dotenv()

class LLMHandler:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        openai.api_key = self.api_key

    def generate_response(self, 
                         query: str, 
                         neo4j_context: Dict, 
                         pinecone_context: List[Dict]) -> str:
        # Construct the prompt with context
        context = f"Neo4j Information: {neo4j_context}\n"
        context += f"Additional Context: {pinecone_context}\n"
        context += f"User Query: {query}\n"
        
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a knowledgeable travel assistant. Use the provided context to answer questions accurately."},
                {"role": "user", "content": context}
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        return response.choices[0].message.content