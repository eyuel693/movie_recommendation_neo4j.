LOAD CSV WITH HEADERS FROM 'file:///netflix_data.csv' AS row
WITH row WHERE row.show_id IS NOT NULL AND row.listed_in IS NOT NULL AND row.listed_in <> ''
MATCH (s:Show {showId: row.show_id})
UNWIND split(row.listed_in, ',') AS genre
WITH s, trim(genre) AS genre_name
WHERE genre_name <> ''
MERGE (g:Genre {name: genre_name})
MERGE (s)-[:IN_GENRE]->(g)
RETURN count(g) AS genres_loaded;
