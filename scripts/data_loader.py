import os
import time
import logging
from neo4j import GraphDatabase
from dotenv import load_dotenv

# Load .env
load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

class Neo4jConnection:
    def __init__(self):
        self.uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.user = os.getenv("NEO4J_USER", "neo4j")
        self.password = os.getenv("NEO4J_PASSWORD", "password")
        self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
        logger.info(f"Connected to Neo4j at {self.uri}")

    def close(self):
        self.driver.close()
        logger.info("Neo4j connection closed.")

    def execute_write(self, query, params=None):
        with self.driver.session() as session:
            return session.write_transaction(lambda tx: list(tx.run(query, params)))

def load_cypher_file(file_path):
    try:
        with open(file_path, 'r') as f:
            return f.read()
    except Exception as e:
        logger.error(f"Error reading {file_path}: {e}")
        return None

def run_cypher_file(conn, file_path, description):
    query = load_cypher_file(file_path)
    if not query:
        logger.error(f"Failed to load {description}")
        return False
    logger.info(f"Running {description}...")
    result = conn.execute_write(query)
    if result and len(result) > 0:
        key = list(result[0].keys())[0]
        logger.info(f"{description}: {result[0][key]}")
    else:
        logger.info(f"{description} completed")
    return True

def main():
    conn = Neo4jConnection()
    try:
        steps = [
            ("cypher/clear_database.cypher", "Clear database"),
            ("cypher/create_indexes.cypher", "Create indexes"),
            ("cypher/load_shows.cypher", "Load shows"),
            ("cypher/load_directors.cypher", "Load directors"),
            ("cypher/load_actors.cypher", "Load actors"),
            ("cypher/load_countries.cypher", "Load countries"),
            ("cypher/load_genres.cypher", "Load genres"),
            ("cypher/load_ratings.cypher", "Load ratings"),
            ("cypher/create_users.cypher", "Create users")
        ]

        for file_path, desc in steps:
            run_cypher_file(conn, file_path, desc)
            time.sleep(0.5)

        # Create synthetic ratings in batches
        logger.info("Creating synthetic ratings in batches...")
        for i in range(20):
            run_cypher_file(conn, "cypher/10_create_synthetic_ratings.cypher", f"Ratings batch {i+1}")
            time.sleep(0.5)

        logger.info("Data loading complete!")
    finally:
        conn.close()

if __name__ == "__main__":
    main()
