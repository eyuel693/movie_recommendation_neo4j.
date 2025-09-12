// Load Shows
LOAD CSV WITH HEADERS FROM 'file:///netflix_data.csv' AS row
MERGE (s:Show {showId: row.show_id})
SET s.title = coalesce(row.title, 'Unknown'),
    s.type = coalesce(row.type, 'Unknown'),
    s.date_added = coalesce(row.date_added, null),
    s.release_year = toInteger(coalesce(row.release_year, 0)),
    s.duration = coalesce(row.duration, 'Unknown');

// Load Directors
LOAD CSV WITH HEADERS FROM 'file:///netflix_data.csv' AS row
MATCH (s:Show {showId: row.show_id})
WHERE row.director IS NOT NULL AND row.director <> ''
UNWIND split(row.director, ',') AS dir
WITH s, trim(dir) AS director_name
WHERE director_name <> ''
MERGE (d:Director {name: director_name})
MERGE (s)-[:DIRECTED]->(d);

// Load Actors
LOAD CSV WITH HEADERS FROM 'file:///netflix_data.csv' AS row
MATCH (s:Show {showId: row.show_id})
WHERE row.cast IS NOT NULL AND row.cast <> ''
UNWIND split(row.cast, ',') AS actor
WITH s, trim(actor) AS actor_name
WHERE actor_name <> ''
MERGE (a:Actor {name: actor_name})
MERGE (s)-[:ACTED_IN]->(a);

// Load Countries
LOAD CSV WITH HEADERS FROM 'file:///netflix_data.csv' AS row
MATCH (s:Show {showId: row.show_id})
WHERE row.country IS NOT NULL AND row.country <> ''
UNWIND split(row.country, ',') AS ctry
WITH s, trim(ctry) AS country_name
WHERE country_name <> ''
MERGE (c:Country {name: country_name})
MERGE (s)-[:PRODUCED_IN]->(c);

// Load Genres
LOAD CSV WITH HEADERS FROM 'file:///netflix_data.csv' AS row
MATCH (s:Show {showId: row.show_id})
WHERE row.listed_in IS NOT NULL AND row.listed_in <> ''
UNWIND split(row.listed_in, ',') AS genre
WITH s, trim(genre) AS genre_name
WHERE genre_name <> ''
MERGE (g:Genre {name: genre_name})
MERGE (s)-[:HAS_GENRE]->(g);

// Load Content Ratings
LOAD CSV WITH HEADERS FROM 'file:///netflix_data.csv' AS row
MATCH (s:Show {showId: row.show_id})
WHERE row.rating IS NOT NULL AND row.rating <> ''
MERGE (r:Rating {name: row.rating})
MERGE (s)-[:HAS_RATING]->(r);

// Create Synthetic Users
UNWIND range(1, 1000) AS userId
MERGE (u:User {userId: userId});

// Create Synthetic Ratings (Limited Scope)
MATCH (u:User)
WHERE NOT EXISTS((u)-[:RATED]->())
WITH u
LIMIT 100
WITH u, toInteger(rand() * 50) + 10 AS numRatings
MATCH (s:Show)
WITH u, numRatings, s
ORDER BY rand()
LIMIT 1000
WITH u, numRatings, collect(s) AS allShows
WITH u, allShows[0..numRatings] AS showsToRate
UNWIND showsToRate AS show
MERGE (u)-[r:RATED]->(show)
SET r.score = toFloat(round(rand() * 4 + 1, 1));