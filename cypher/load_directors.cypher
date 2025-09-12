LOAD CSV WITH HEADERS FROM 'file:///netflix_data.csv' AS row
WITH row WHERE row.show_id IS NOT NULL AND row.director IS NOT NULL AND row.director <> ''
MATCH (s:Show {showId: row.show_id})
UNWIND split(row.director, ',') AS director
WITH s, trim(director) AS director_name
WHERE director_name <> ''
MERGE (d:Director {name: director_name})
MERGE (s)-[:DIRECTED_BY]->(d)
RETURN count(d) AS directors_loaded;
