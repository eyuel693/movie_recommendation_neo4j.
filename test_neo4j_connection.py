from neo4j import GraphDatabase
import os
from dotenv import load_dotenv


load_dotenv()

# Set your Neo4j connection details here (or use environment variables)
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "your_password_here")

# Create the Neo4j driver
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

def test_connection():
    try:
        with driver.session() as session:
            greeting = session.run("RETURN '✅ Connected to Neo4j!' AS message")
            print(greeting.single()["message"])
    except Exception as e:
        print("❌ Failed to connect to Neo4j:", e)

if __name__ == "__main__":
    test_connection()