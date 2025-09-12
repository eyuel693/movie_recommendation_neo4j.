LOAD CSV WITH HEADERS FROM 'file:///netflix_data.csv' AS row
WITH row WHERE row.show_id IS NOT NULL AND row.cast IS NOT NULL AND row.cast <> ''
MATCH (s:Show {showId: row.show_id})
UNWIND split(row.cast, ',') AS actor
WITH s, trim(actor) AS actor_name
WHERE actor_name <> ''
MERGE (a:Actor {name: actor_name})
MERGE (s)-[:FEATURES]->(a)
RETURN count(a) AS actors_loaded;
