// Genre-Based Recommendation
MATCH (u:User {userId: 5})-[r:RATED]->(s:Show)-[:HAS_GENRE]->(favGenre:Genre)
WHERE r.score >= 3.5
WITH favGenre, count(*) AS genreCount
ORDER BY genreCount DESC
LIMIT 3
WITH collect(favGenre) AS favGenres
MATCH (g:Genre)<-[:HAS_GENRE]-(rec:Show)
WHERE g IN favGenres
AND NOT EXISTS((:User {userId: 5})-[:RATED]->(rec))
RETURN rec.title AS recommendation,
       rec.type AS type,
       g.name AS genre,
       "Popular in your favorite genres" AS reason
ORDER BY rec.release_year DESC
LIMIT 10
UNION
// Fallback: Recommend recent shows from popular genres
MATCH (g:Genre)<-[:HAS_GENRE]-(rec:Show)
WHERE NOT EXISTS((:User {userId: 5})-[:RATED]->(rec))
WITH g, rec, count(*) AS showCount
ORDER BY showCount DESC
LIMIT 3
MATCH (g)<-[:HAS_GENRE]-(rec:Show)
WHERE NOT EXISTS((:User {userId: 5})-[:RATED]->(rec))
RETURN rec.title AS recommendation,
       rec.type AS type,
       g.name AS genre,
       "Popular genres (fallback)" AS reason
ORDER BY rec.release_year DESC
LIMIT 10;