from neo4j import GraphDatabase
from scripts.utils import load_config, run_cypher_file
import sys
import json
import logging

class Recommender:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
    
    def close(self):
        self.driver.close()
    
    def get_recommendations(self, user_id, rec_type):
        """Run recommendation query based on type."""
        query_map = {
            'content': 'cypher/Content_Based.cypher',
            'collaborative': 'cypher/Collaborative_Filtering.cypher',
            'genre': 'cypher/gener_based.cypher',
            'hybrid': 'cypher/hybrid_recommendation.cypher'
        }
        if rec_type not in query_map:
            raise ValueError(f"Unknown recommendation type: {rec_type}")
        
        results = run_cypher_file(self.driver, query_map[rec_type], {'userId': user_id})
        return results

if __name__ == "__main__":
    config = load_config()
    recommender = Recommender(
        config["neo4j"]["localhost:7687"],
        config["neo4j"]["neo4j"],
        config["neo4j"]["321654987"]
    )
    
    if len(sys.argv) != 3:
        print("Usage: python scripts/recommender.py <content|collaborative|genre|hybrid> <userId>")
        sys.exit(1)
    
    rec_type = sys.argv[1]
    user_id = sys.argv[2]
    
    try:
        recs = recommender.get_recommendations(user_id, rec_type)
        output_path = f"outputs/recommendations/{rec_type}_{user_id}.json"
        with open(output_path, 'w') as f:
            json.dump(recs, f, indent=2)
        logging.info(f"Recommendations saved to {output_path}")
        
        print(f"Top recommendations for user {user_id} ({rec_type}):")
        for rec in recs:
            title = rec['recommendation']
            score = rec.get('similarityScore', rec.get('predictedScore', rec.get('finalScore', 'N/A')))
            print(f"- {title} (Score: {score})")
    except Exception as e:
        logging.error(f"Recommendation failed: {e}")
        print(f"Error: {e}")
    finally:
        recommender.close()