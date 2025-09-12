MATCH (u:User)
WITH u LIMIT 5
WITH u, toInteger(rand() * 20) + 5 AS numRatings
MATCH (s:Show)
WITH u, s ORDER BY rand() LIMIT numRatings
MERGE (u)-[r:RATED]->(s)
SET r.score = toFloat(round(rand() * 4 + 1, 1)),
    r.timestamp = timestamp()
RETURN count(r) AS ratings_created;
