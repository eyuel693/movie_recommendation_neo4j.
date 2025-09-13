import os
import logging
from typing import List, Dict
from neo4j import GraphDatabase
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Ensure log directory exists
os.makedirs('outputs/logs', exist_ok=True)

# Configure logging
logging.basicConfig(
    filename='outputs/logs/new_user_recommend.log',
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

class Neo4jRecommender:
    def __init__(self, uri: str, user: str, password: str):
        try:
            self.driver = GraphDatabase.driver(uri, auth=(user, password))
            logger.info(f"Connected to Neo4j at {uri}")
        except Exception as e:
            logger.error(f"Failed to connect to Neo4j: {e}")
            raise

    def close(self):
        try:
            self.driver.close()
            logger.info("Neo4j connection closed")
        except Exception as e:
            logger.error(f"Error closing Neo4j connection: {e}")

    def execute_query(self, query: str, params: dict = None) -> List[Dict]:
        try:
            with self.driver.session() as session:
                result = session.run(query, params or {})
                records = [dict(record) for record in result]
                logger.debug(f"Query result for {params}: {records}")
                return records
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            return []

    def validate_interests(self, genres: List[str] = None, actors: List[str] = None, directors: List[str] = None) -> Dict[str, List[str]]:
        """Validate that provided genres, actors, and directors exist in the database."""
        valid_interests = {"genres": [], "actors": [], "directors": []}
        try:
            with self.driver.session() as session:
                if genres:
                    query = "MATCH (g:Genre) WHERE g.name IN $items RETURN g.name AS name"
                    result = session.run(query, {"items": genres})
                    valid_interests["genres"] = [r["name"] for r in result if r["name"] in genres]
                    logger.info(f"Valid genres: {valid_interests['genres']}")
                if actors:
                    query = "MATCH (a:Actor) WHERE a.name IN $items RETURN a.name AS name"
                    result = session.run(query, {"items": actors})
                    valid_interests["actors"] = [r["name"] for r in result if r["name"] in actors]
                    logger.info(f"Valid actors: {valid_interests['actors']}")
                if directors:
                    query = "MATCH (d:Director) WHERE d.name IN $items RETURN d.name AS name"
                    result = session.run(query, {"items": directors})
                    valid_interests["directors"] = [r["name"] for r in result if r["name"] in directors]
                    logger.info(f"Valid directors: {valid_interests['directors']}")
            return valid_interests
        except Exception as e:
            logger.error(f"Error validating interests: {e}")
            return valid_interests

    def create_user(self, user_id: int, name: str = None) -> List[Dict]:
        query = """
        MERGE (u:User {userId: $userId})
        SET u.name = coalesce($name, u.name)
        RETURN u.userId AS userId
        """
        params = {"userId": user_id, "name": name}
        result = self.execute_query(query, params)
        logger.info(f"Created/Updated user {user_id} with name: {name}")
        return result

    def add_interests(self, user_id: int, genres: List[str] = None, actors: List[str] = None, directors: List[str] = None):
        valid_interests = self.validate_interests(genres, actors, directors)
        if not any(valid_interests.values()):
            logger.warning(f"No valid interests provided for user {user_id}")
            return

        if valid_interests["genres"]:
            query = """
            MATCH (u:User {userId: $userId})
            MATCH (g:Genre) WHERE g.name IN $genres
            MERGE (u)-[:INTERESTED_IN]->(g)
            """
            self.execute_query(query, {"userId": user_id, "genres": valid_interests["genres"]})
            logger.info(f"Added {len(valid_interests['genres'])} genres for user {user_id}")

        if valid_interests["actors"]:
            query = """
            MATCH (u:User {userId: $userId})
            MATCH (a:Actor) WHERE a.name IN $actors
            MERGE (u)-[:INTERESTED_IN]->(a)
            """
            self.execute_query(query, {"userId": user_id, "actors": valid_interests["actors"]})
            logger.info(f"Added {len(valid_interests['actors'])} actors for user {user_id}")

        if valid_interests["directors"]:
            query = """
            MATCH (u:User {userId: $userId})
            MATCH (d:Director) WHERE d.name IN $directors
            MERGE (u)-[:INTERESTED_IN]->(d)
            """
            self.execute_query(query, {"userId": user_id, "directors": valid_interests["directors"]})
            logger.info(f"Added {len(valid_interests['directors'])} directors for user {user_id}")

    def recommend_from_interests(self, user_id: int, limit: int = 10) -> List[Dict]:
        query = """
        MATCH (u:User {userId: $userId})-[:INTERESTED_IN]->(entity)
        MATCH (s:Show)
        WHERE (s)-[:FEATURES]->(entity) OR (s)-[:DIRECTED_BY]->(entity) OR (s)-[:IN_GENRE]->(entity)
          AND NOT EXISTS((u)-[:RATED]->(s))
        RETURN s.title AS title,
               s.type AS type,
               labels(entity)[0] AS entityType,
               entity.name AS matchedInterest,
               s.release_year AS year
        ORDER BY s.release_year DESC
        LIMIT $limit
        """
        params = {"userId": user_id, "limit": limit}
        result = self.execute_query(query, params)
        logger.info(f"Generated {len(result)} interest-based recommendations for user {user_id}")
        return result

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Add new user and recommend shows")
    parser.add_argument("--user-id", type=int, required=True, help="New user ID")
    parser.add_argument("--name", type=str, default=None, help="User name")
    parser.add_argument("--genres", nargs="*", default=[], help="List of favorite genres")
    parser.add_argument("--actors", nargs="*", default=[], help="List of favorite actors")
    parser.add_argument("--directors", nargs="*", default=[], help="List of favorite directors")
    parser.add_argument("--limit", type=int, default=10, help="Number of recommendations")
    args = parser.parse_args()

    recommender = Neo4jRecommender(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
    try:
        logger.info(f"Creating user {args.user_id}...")
        print(f"Creating user {args.user_id}...")
        recommender.create_user(args.user_id, args.name)

        logger.info(f"Adding interests for user {args.user_id}...")
        print("Adding interests...")
        recommender.add_interests(args.user_id, genres=args.genres, actors=args.actors, directors=args.directors)

        logger.info(f"Generating recommendations for user {args.user_id}...")
        print(f"Recommendations for user {args.user_id}:")
        recommendations = recommender.recommend_from_interests(args.user_id, args.limit)
        if recommendations:
            for i, rec in enumerate(recommendations, 1):
                print(f"{i}. {rec['title']} ({rec['type']}) - matched: {rec['matchedInterest']} [{rec['year']}]")
                logger.info(f"{i}. {rec}")
        else:
            print("No recommendations found.")
            logger.info("No recommendations found.")
    finally:
        recommender.close()