Hybrid AI Travel Assistant

A sophisticated Hybrid AI Travel Assistant developed as a technical challenge for Blue Enigma Labs. This project implements a Retrieval-Augmented Generation (RAG) system that combines semantic search with a knowledge graph to provide intelligent and factually-grounded travel recommendations for Vietnam.

Architecture Overview

This system leverages a hybrid RAG architecture to overcome the limitations of traditional LLMs. Instead of relying on the model's internal knowledge alone, it retrieves rich, contextual data from two specialized databases before generating a response.

Pinecone (Vector Database): Serves as the semantic search engine. It stores vector embeddings of travel data and finds the most relevant locations and activities based on the meaning of a user's query (the "what").

Neo4j (Knowledge Graph): Provides the structural and factual context. It stores the explicit relationships between the items found by Pinecone, such as which city an attraction is located in or what activities are nearby (the "how").

Google Gemini (LLM): Acts as the final reasoning engine. It takes the context from both Pinecone and Neo4j to synthesize a coherent, accurate, and creative response.

graph TD
    A[User Query] --> B(Generate Query Embedding);
    B --> C{Pinecone};
    C --> D[Top-K Semantic Results];
    D --> E{Neo4j};
    E --> F[Graph Context];
    D & F --> G{Google Gemini LLM};
    G --> H[Final Answer];

.

Setup and Installation

Follow these steps to get the project running locally.

Prerequisites

Python 3.9+

Neo4j Desktop with an active database.

1. Clone the Repository

git clone <your-repository-url>
cd hybrid-ai-challenge



2. Set Up a Virtual Environment

# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate



3. Install Dependencies

pip install -r requirements.txt



4. Configure API Keys

Make a copy of config_example.py and rename it to config.py.

Open config.py and fill in your credentials for:

Neo4j (URI, User, Password)

Pinecone API Key

Google Gemini API Key

Usage

The project includes an all-in-one script to set up the databases and a separate script to run the chat interface.

1. Run the Setup Script

This script will load the data into Neo4j, create embeddings and upload them to Pinecone, and generate an interactive visualization of the knowledge graph.

python main.py



2. Start the Chat Assistant

Once the setup is complete, you can start interacting with the AI travel assistant.

python hybrid_chat.py
