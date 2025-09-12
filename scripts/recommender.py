import os
import logging
from typing import List, Dict
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

class RecommendationEngine:
    def __init__(self):
        self.uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.user = os.getenv("NEO4J_USER", "neo4j")
        self.password = os.getenv("NEO4J_PASSWORD", "password")
        self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
        logger.info(f"Connected to Neo4j at {self.uri}")

    def close(self):
        self.driver.close()
        logger.info("Neo4j connection closed.")

    def execute_query(self, query: str, params: dict = None) -> List[Dict]:
        try:
            with self.driver.session() as session:
                return [dict(record) for record in session.run(query, params)]
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            return []

    def load_cypher_file(self, file_path: str) -> str:
        try:
            with open(file_path, 'r') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error reading {file_path}: {e}")
            return None

    def get_recommendations(self, cypher_file: str, user_id: int, limit: int = 10) -> List[Dict]:
        query = self.load_cypher_file(cypher_file)
        if not query:
            logger.error(f"Cannot load Cypher query from {cypher_file}")
            return []

        results = self.execute_query(query, {"userId": user_id})
        return results[:limit] if results else []

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--user-id", type=int, required=True, help="User ID")
    parser.add_argument("--strategy", choices=["collaborative", "content", "hybrid", "genre"], default="hybrid")
    args = parser.parse_args()

    strategy_files = {
        "collaborative": "cypher/collaborative_filtering.cypher",
        "content": "cypher/content_based.cypher",
        "hybrid": "cypher/hybrid_recommendation.cypher",
        "genre": "cypher/genre_based.cypher"
    }

    engine = RecommendationEngine()
    try:
        recs = engine.get_recommendations(strategy_files[args.strategy], args.user_id)
        if recs:
            for i, rec in enumerate(recs, 1):
                logger.info(f"{i}. {rec}")
        else:
            logger.info("No recommendations found.")
    finally:
        engine.close()
