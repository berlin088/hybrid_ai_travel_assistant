from neo4j import GraphDatabase
import json
from typing import Dict, List
import os
from dotenv import load_dotenv

load_dotenv()

class Neo4jManager:
    def __init__(self):
        self.uri = os.getenv("NEO4J_URI")
        self.user = os.getenv("NEO4J_USER")
        self.password = os.getenv("NEO4J_PASSWORD")
        self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))

    def close(self):
        self.driver.close()

    def create_location_node(self, tx, location: Dict):
        query = """
        CREATE (l:Location {
            name: $name,
            type: $type,
            country: $country,
            description: $description
        })
        """
        tx.run(query, **location)

    def create_relationship(self, tx, location1: str, location2: str, relationship_type: str):
        query = """
        MATCH (l1:Location {name: $loc1})
        MATCH (l2:Location {name: $loc2})
        CREATE (l1)-[r:%s]->(l2)
        """ % relationship_type
        tx.run(query, loc1=location1, loc2=location2)

    def load_locations(self, locations_file: str):
        with open(locations_file, 'r') as f:
            locations = json.load(f)
        
        with self.driver.session() as session:
            for location in locations:
                session.execute_write(self.create_location_node, location)

    def query_location(self, name: str) -> Dict:
        with self.driver.session() as session:
            result = session.run(
                "MATCH (l:Location {name: $name}) RETURN l",
                name=name
            )
            return result.single()[0] if result.peek() else None