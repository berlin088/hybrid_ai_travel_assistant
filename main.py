import os
import sys
import logging
from dotenv import load_dotenv
import streamlit as st
from src.database.neo4j_manager import Neo4jManager
from src.database.pinecone_manager import PineconeManager
from src.models.llm_handler import LLMHandler
from src.utils.text_processor import TextProcessor
from src.interface.chat_interface import ChatInterface

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ...existing code...

class TravelAssistantSetup:
    def __init__(self):
        load_dotenv()
        self.verify_pinecone_setup()  # Add verification before initializing
        self.neo4j = Neo4jManager()
        self.pinecone = PineconeManager()
        self.text_processor = TextProcessor()
        self.chat_interface = ChatInterface()

    def verify_pinecone_setup(self):
        """Verify Pinecone configuration before initialization"""
        logger.info("Verifying Pinecone configuration...")
        
        # Check API key format
        api_key = os.getenv('PINECONE_API_KEY')
        if not api_key or len(api_key) < 32:  # Pinecone API keys are typically longer
            raise ValueError("Invalid Pinecone API key format. Please check your .env file")
            
        # Verify environment
        env = os.getenv('PINECONE_ENVIRONMENT')
        if env != 'gcp-starter':
            logger.warning(f"Pinecone environment is set to '{env}'. For free tier, use 'gcp-starter'")
        
        try:
            # Test Pinecone connection
            import pinecone
            pinecone.init(api_key=api_key, environment=env)
            
            # Check existing indexes
            existing_indexes = pinecone.list_indexes()
            if existing_indexes:
                logger.warning(f"Found existing Pinecone indexes: {existing_indexes}")
                logger.warning("Consider deleting unused indexes in Pinecone console: https://app.pinecone.io")
            
            logger.info("Pinecone configuration verified successfully")
            
        except Exception as e:
            raise ConnectionError(f"Failed to connect to Pinecone: {str(e)}")

    # ...existing code...

    def check_environment_variables(self):
        """Check if all required environment variables are set"""
        required_vars = [
            'NEO4J_URI', 'NEO4J_USER', 'NEO4J_PASSWORD',
            'PINECONE_API_KEY', 'PINECONE_ENVIRONMENT',
            'OPENAI_API_KEY'
        ]
        
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        if missing_vars:
            raise EnvironmentError(f"Missing environment variables: {', '.join(missing_vars)}")

    def load_location_data(self):
        """Load location data into Neo4j"""
        try:
            logger.info("Loading location data into Neo4j...")
            locations = self.text_processor.parse_location_data('data/locations.json')
            self.neo4j.load_locations('data/locations.json')
            logger.info("Location data loaded successfully")
            return locations
        except Exception as e:
            logger.error(f"Error loading location data: {str(e)}")
            raise

    def process_travel_info(self):
        """Process and load travel information into Pinecone"""
        try:
            logger.info("Processing travel information...")
            with open('data/travel_info.txt', 'r', encoding='utf-8') as f:
                text = f.read()
            
            # Clean and chunk the text
            cleaned_text = self.text_processor.clean_text(text)
            chunks = self.text_processor.chunk_text(cleaned_text)
            
            # Prepare documents for Pinecone
            documents = [{"content": chunk, "type": "travel_info"} for chunk in chunks]
            
            # Upload to Pinecone
            logger.info("Uploading data to Pinecone...")
            self.pinecone.upsert_texts(documents)
            logger.info("Travel information processed and uploaded successfully")
        except Exception as e:
            logger.error(f"Error processing travel information: {str(e)}")
            raise

    def run_tests(self):
        """Run unit tests"""
        try:
            logger.info("Running unit tests...")
            import unittest
            from tests.test_managers import TestNeo4jManager, TestPineconeManager, TestTextProcessor
            
            test_loader = unittest.TestLoader()
            test_suite = unittest.TestSuite()
            
            test_suite.addTests(test_loader.loadTestsFromTestCase(TestNeo4jManager))
            test_suite.addTests(test_loader.loadTestsFromTestCase(TestPineconeManager))
            test_suite.addTests(test_loader.loadTestsFromTestCase(TestTextProcessor))
            
            runner = unittest.TextTestRunner(verbosity=2)
            result = runner.run(test_suite)
            
            if not result.wasSuccessful():
                raise Exception("Unit tests failed")
            
            logger.info("All tests passed successfully")
        except Exception as e:
            logger.error(f"Error running tests: {str(e)}")
            raise

    def run_application(self):
        """Run the Streamlit chat interface"""
        try:
            logger.info("Starting chat interface...")
            self.chat_interface.display_chat()
        except Exception as e:
            logger.error(f"Error running chat interface: {str(e)}")
            raise

def main():
    try:
        setup = TravelAssistantSetup()
        
        # Step 1: Check environment variables
        logger.info("Checking environment variables...")
        setup.check_environment_variables()
        
        # Step 2: Run unit tests
        setup.run_tests()
        
        # Step 3: Load location data into Neo4j
        setup.load_location_data()
        
        # Step 4: Process and load travel information into Pinecone
        setup.process_travel_info()
        
        # Step 5: Run the chat interface
        setup.run_application()
        
    except Exception as e:
        logger.error(f"Application failed to start: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()