import os
import logging
from typing import List, Dict
from neo4j import GraphDatabase
from dotenv import load_dotenv
import argparse

# Load environment variables
load_dotenv()

# Ensure log directory exists
os.makedirs('outputs/logs', exist_ok=True)

# Configure logging to file and terminal
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler('outputs/logs/recommendation_engine.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Mock data for fallback
mock_recommendations = [
    {"title": "Inception", "type": "Movie", "score": 4.5, "year": 2010},
    {"title": "Stranger Things", "type": "TV Show", "score": 4.2, "year": 2016},
    {"title": "The Matrix", "type": "Movie", "score": 4.0, "year": 1999}
]

class RecommendationEngine:
    def __init__(self):
        self.uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.user = os.getenv("NEO4J_USER", "neo4j")
        self.password = os.getenv("NEO4J_PASSWORD", "password")
        self.driver = None
        try:
            self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
            logger.info(f"Connected to Neo4j at {self.uri}")
        except Exception as e:
            logger.error(f"Failed to initialize Neo4j driver: {e}. Using mock data.")
            self.driver = None

    def close(self):
        if self.driver:
            try:
                self.driver.close()
                logger.info("Neo4j connection closed.")
            except Exception as e:
                logger.error(f"Error closing Neo4j connection: {e}")

    def execute_query(self, query: str, params: dict = None) -> List[Dict]:
        if not self.driver:
            logger.warning("No Neo4j driver available. Returning mock data.")
            return mock_recommendations
        try:
            with self.driver.session() as session:
                result = session.run(query, params or {})
                records = [dict(record) for record in result]
                logger.debug(f"Query: {query}")
                logger.debug(f"Params: {params}")
                logger.debug(f"Result: {records}")
                return records
        except Exception as e:
            logger.error(f"Query execution failed: {e}. Returning mock data.")
            return mock_recommendations

    def load_cypher_file(self, file_path: str) -> str:
        try:
            abs_path = os.path.abspath(file_path)
            if not os.path.exists(abs_path):
                raise FileNotFoundError(f"Cypher file {abs_path} does not exist")
            with open(abs_path, 'r') as f:
                query = f.read()
                logger.info(f"Loaded Cypher file: {abs_path}")
                return query
        except FileNotFoundError as e:
            logger.error(f"{e}")
            return None
        except Exception as e:
            logger.error(f"Error reading {file_path}: {e}")
            return None

    def check_user_exists(self, user_id: int) -> bool:
        if not self.driver:
            logger.warning(f"Neo4j unavailable, assuming user {user_id} exists for mock data")
            return True
        query = "MATCH (u:User {userId: $userId}) RETURN u LIMIT 1"
        result = self.execute_query(query, {"userId": user_id})
        exists = bool(result)
        logger.info(f"User {user_id} exists: {exists}")
        return exists

    def validate_user_data(self, user_id: int) -> Dict:
        if not self.driver:
            logger.warning(f"Neo4j unavailable, returning mock user data for {user_id}")
            return {"rated_shows": 3, "genres": 3, "interests": 0}
        queries = {
            "rated_shows": "MATCH (u:User {userId: $userId})-[:RATED]->(s:Show) RETURN count(s) AS count",
            "genres": "MATCH (u:User {userId: $userId})-[:RATED]->(s:Show)-[:IN_GENRE]->(g:Genre) RETURN count(DISTINCT g) AS count",
            "interests": "MATCH (u:User {userId: $userId})-[:INTERESTED_IN]->(e) RETURN count(e) AS count"
        }
        result = {}
        try:
            with self.driver.session() as session:
                for key, query in queries.items():
                    res = session.run(query, {"userId": user_id}).single()
                    result[key] = res["count"] if res else 0
                logger.debug(f"User {user_id} data: {result}")
                return result
        except Exception as e:
            logger.error(f"Error validating user data for {user_id}: {e}. Returning mock data.")
            return {"rated_shows": 3, "genres": 3, "interests": 0}

    def get_recommendations(self, cypher_file: str, user_id: int, limit: int = 10) -> List[Dict]:
        if not self.check_user_exists(user_id):
            logger.error(f"User {user_id} does not exist in the database.")
            return mock_recommendations

        user_data = self.validate_user_data(user_id)
        if user_data.get("rated_shows", 0) == 0:
            logger.warning(f"User {user_id} has no rated shows, returning mock data.")
            return mock_recommendations[:limit]

        query = self.load_cypher_file(cypher_file)
        if not query:
            logger.error(f"Cannot load Cypher query from {cypher_file}. Returning mock data.")
            return mock_recommendations[:limit]

        results = self.execute_query(query, {"userId": user_id})
        if not results:
            logger.info(f"No recommendations found for user {user_id} with {cypher_file}. Returning mock data.")
            return mock_recommendations[:limit]

        # Filter invalid results
        valid_results = [rec for rec in results if 'title' in rec and rec['title'] is not None and 'type' in rec]
        if not valid_results:
            logger.warning(f"No valid recommendations for user {user_id} with {cypher_file}. Returning mock data.")
            return mock_recommendations[:limit]

        logger.info(f"Found {len(valid_results)} valid recommendations for user {user_id} with {cypher_file}")
        for rec in valid_results:
            if 'score' not in rec and 'reason' not in rec:
                logger.warning(f"Recommendation missing score/reason: {rec}")
        return valid_results[:limit]

def main():
    parser = argparse.ArgumentParser(description="Generate recommendations for a user")
    parser.add_argument("--user-id", type=int, required=True, help="User ID")
    parser.add_argument("--strategy", choices=["collaborative", "content", "hybrid", "genre"], default="hybrid")
    parser.add_argument("--limit", type=int, default=10, help="Number of recommendations")
    args = parser.parse_args()

    strategy_files = {
        "collaborative": "cypher/collaborative_filtering.cypher",
        "content": "cypher/content_based.cypher",
        "hybrid": "cypher/Hybrid_Recommendation.cypher",
        "genre": "cypher/Genre_Based.cypher"
    }

    engine = RecommendationEngine()
    try:
        cypher_file = strategy_files.get(args.strategy)
        if not cypher_file:
            logger.error(f"Invalid strategy: {args.strategy}")
            print(f"Error: Strategy '{args.strategy}' is not supported.")
            return

        recs = engine.get_recommendations(cypher_file, args.user_id, args.limit)
        if recs:
            print(f"Recommendations for user {args.user_id} (strategy: {args.strategy}):")
            for i, rec in enumerate(recs, 1):
                title = rec.get('title', rec.get('show_title', 'Unknown'))
                type_ = rec.get('type', 'N/A')
                score = rec.get('score', rec.get('reason', 'N/A'))
                print(f"{i}. Title: {title}, Type: {type_}, Score/Reason: {score}")
                logger.info(f"{i}. {rec}")
        else:
            print(f"No recommendations found for user {args.user_id} with strategy {args.strategy}.")
            logger.info(f"No recommendations found for user {args.user_id} with {cypher_file}")
    except Exception as e:
        logger.error(f"Error generating recommendations: {e}")
        print(f"Error: {str(e)}")
    finally:
        engine.close()

if __name__ == "__main__":
    main()