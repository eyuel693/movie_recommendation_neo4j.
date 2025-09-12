LOAD CSV WITH HEADERS FROM 'file:///netflix_data.csv' AS row
WITH row WHERE row.show_id IS NOT NULL AND row.country IS NOT NULL AND row.country <> ''
MATCH (s:Show {showId: row.show_id})
UNWIND split(row.country, ',') AS country
WITH s, trim(country) AS country_name
WHERE country_name <> ''
MERGE (c:Country {name: country_name})
MERGE (s)-[:PRODUCED_IN]->(c)
RETURN count(c) AS countries_loaded;
