import unittest
from src.database.neo4j_manager import Neo4jManager
from src.database.pinecone_manager import PineconeManager
from src.models.llm_handler import LLMHandler
from src.utils.text_processor import TextProcessor
import os

class TestNeo4jManager(unittest.TestCase):
    def setUp(self):
        self.neo4j = Neo4jManager()
        self.test_location = {
            "name": "Test City",
            "type": "city",
            "country": "Test Country",
            "description": "Test description"
        }

    def test_create_and_query_location(self):
        with self.neo4j.driver.session() as session:
            session.execute_write(self.neo4j.create_location_node, self.test_location)
            result = self.neo4j.query_location("Test City")
            self.assertIsNotNone(result)
            self.assertEqual(result['name'], "Test City")

    def tearDown(self):
        with self.neo4j.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
        self.neo4j.close()

class TestPineconeManager(unittest.TestCase):
    def setUp(self):
        self.pinecone = PineconeManager()
        self.test_texts = [
            {"content": "Test content 1", "type": "description"},
            {"content": "Test content 2", "type": "description"}
        ]

    def test_upsert_and_query(self):
        self.pinecone.upsert_texts(self.test_texts)
        results = self.pinecone.query("Test content", top_k=1)
        self.assertGreater(len(results), 0)

    def tearDown(self):
        # Clean up test vectors
        self.pinecone.index.delete(delete_all=True)

class TestTextProcessor(unittest.TestCase):
    def test_clean_text(self):
        text = "Hello, World!  This is a Test..."
        cleaned = TextProcessor.clean_text(text)
        self.assertEqual(cleaned, "hello world this is a test")

    def test_chunk_text(self):
        text = "This is a long text that needs to be chunked into smaller pieces"
        chunks = TextProcessor.chunk_text(text, chunk_size=20)
        self.assertTrue(all(len(chunk) <= 20 for chunk in chunks))

    def test_parse_location_data(self):
        test_data = '[{"name": "Test"}]'
        with open('test_locations.json', 'w') as f:
            f.write(test_data)
        
        locations = TextProcessor.parse_location_data('test_locations.json')
        self.assertEqual(len(locations), 1)
        self.assertEqual(locations[0]['name'], "Test")
        
        os.remove('test_locations.json')

if __name__ == '__main__':
    unittest.main()