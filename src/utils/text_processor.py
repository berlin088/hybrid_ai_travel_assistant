import re
from typing import List, Dict
import json

class TextProcessor:
    @staticmethod
    def clean_text(text: str) -> str:
        """Clean and normalize text"""
        # Remove special characters and extra whitespace
        text = re.sub(r'[^\w\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip().lower()

    @staticmethod
    def chunk_text(text: str, chunk_size: int = 1000) -> List[str]:
        """Split text into smaller chunks for processing"""
        words = text.split()
        chunks = []
        current_chunk = []
        current_length = 0

        for word in words:
            if current_length + len(word) + 1 <= chunk_size:
                current_chunk.append(word)
                current_length += len(word) + 1
            else:
                chunks.append(' '.join(current_chunk))
                current_chunk = [word]
                current_length = len(word)

        if current_chunk:
            chunks.append(' '.join(current_chunk))
        return chunks

    @staticmethod
    def parse_location_data(file_path: str) -> List[Dict]:
        """Parse location data from JSON file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format in {file_path}: {str(e)}")
        except FileNotFoundError:
            raise FileNotFoundError(f"Location data file not found: {file_path}")

    @staticmethod
    def extract_relationships(locations: List[Dict]) -> List[Dict]:
        """Extract relationships between locations"""
        relationships = []
        for loc in locations:
            if 'connected_to' in loc:
                for connection in loc['connected_to']:
                    relationships.append({
                        'source': loc['name'],
                        'target': connection['name'],
                        'type': connection.get('type', 'CONNECTS_TO')
                    })
        return relationships