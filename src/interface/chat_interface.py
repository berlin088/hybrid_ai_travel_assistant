import streamlit as st
from src.database.neo4j_manager import Neo4jManager
from src.database.pinecone_manager import PineconeManager
from src.models.llm_handler import LLMHandler

class ChatInterface:
    def __init__(self):
        self.neo4j = Neo4jManager()
        self.pinecone = PineconeManager()
        self.llm = LLMHandler()

    def initialize_session(self):
        if 'messages' not in st.session_state:
            st.session_state.messages = []

    def display_chat(self):
        st.title("Travel Assistant")
        self.initialize_session()

        # Display chat history
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Chat input
        if prompt := st.chat_input("What would you like to know?"):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            # Get context from both sources
            neo4j_context = self.neo4j.query_location(prompt)
            pinecone_context = self.pinecone.query(prompt)

            # Generate response
            response = self.llm.generate_response(prompt, neo4j_context, pinecone_context)

            # Display assistant response
            with st.chat_message("assistant"):
                st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    chat_interface = ChatInterface()
    chat_interface.display_chat()