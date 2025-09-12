from neo4j import GraphDatabase
from scripts.utils import load_config, run_cypher_file, normalize_duration
import pandas as pd
import logging

class NetflixLoader:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
    
    def close(self):
        self.driver.close()
    
    def load_data(self, csv_path):
        """Load CSV data into Neo4j."""
        logging.info(f"Loading data from {csv_path}")
        try:
            # Create indexes
            run_cypher_file(self.driver, "cypher/index.cypher")
            logging.info("Indexes created")
            
            # Load data
            run_cypher_file(self.driver, "cypher/import_data.cypher")
            logging.info("Data imported successfully")
            
        except Exception as e:
            logging.error(f"Data loading failed: {e}")
            raise

if __name__ == "__main__":
    config = load_config()
    loader = NetflixLoader(
         config["neo4j"]["localhost:7687"],
        config["neo4j"]["neo4j"],
        config["neo4j"]["321654987"]
    )
    loader.load_data("data/raw/netflix_data.csv")
    loader.close()