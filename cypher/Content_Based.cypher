// Content-Based Recommendation
MATCH (u:User {userId: 5})-[r:RATED]->(s:Show)
WITH u, COLLECT(s) AS userShows

// Similar by actors
UNWIND userShows AS s
OPTIONAL MATCH (s)-[:FEATURES]->(a:Actor)<-[:FEATURES]-(rec:Show)
WHERE NOT (u)-[:RATED]->(rec)
WITH u, rec, COUNT(DISTINCT a) AS actorScore

// Similar by directors
OPTIONAL MATCH (s)-[:DIRECTED_BY]->(d:Director)<-[:DIRECTED_BY]-(rec)
WITH u, rec, actorScore, COUNT(DISTINCT d) AS directorScore

// Similar by genres
OPTIONAL MATCH (s)-[:IN_GENRE]->(g:Genre)<-[:IN_GENRE]-(rec)
WITH rec, 
     actorScore, 
     directorScore, 
     COUNT(DISTINCT g) AS genreScore

WITH rec, (actorScore + directorScore + genreScore) AS contentScore
WHERE contentScore > 0
RETURN rec.showId AS showId,
       rec.title AS title,
       rec.type AS type,
       contentScore
ORDER BY contentScore DESC
LIMIT 10;
