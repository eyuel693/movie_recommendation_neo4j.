LOAD CSV WITH HEADERS FROM 'file:///netflix_data.csv' AS row
WITH row WHERE row.show_id IS NOT NULL AND row.rating IS NOT NULL AND row.rating <> ''
MATCH (s:Show {showId: row.show_id})
MERGE (r:Rating {name: row.rating})
MERGE (s)-[:HAS_RATING]->(r)
RETURN count(r) AS ratings_loaded;
