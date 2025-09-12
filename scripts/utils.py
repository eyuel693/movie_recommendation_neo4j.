import yaml
import logging
from neo4j import GraphDatabase
import pandas as pd
import re

# Configure logging
logging.basicConfig(
    filename='outputs/logs/app.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def load_config(config_path="config/neo4j_config.yaml"):
    """Load Neo4j configuration from YAML."""
    try:
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        logging.error(f"Failed to load config: {e}")
        raise

def normalize_duration(duration_str):
    """Normalize duration (e.g., '90 min' -> '90', '1 Season' -> '1_season')."""
    if pd.isna(duration_str) or not duration_str:
        return 'Unknown'
    if 'Season' in duration_str:
        match = re.search(r'(\d+)', duration_str)
        return f"{match.group(1)}_season" if match else 'Unknown'
    match = re.search(r'(\d+)', duration_str)
    return match.group(1) if match else 'Unknown'

def run_cypher_file(driver, cypher_file, params=None):
    """Execute a Cypher file with optional parameters."""
    try:
        with open(cypher_file, 'r') as f:
            query = f.read()
        with driver.session() as session:
            result = session.run(query, params or {})
            return [dict(record) for record in result]
    except Exception as e:
        logging.error(f"Error running {cypher_file}: {e}")
        raise