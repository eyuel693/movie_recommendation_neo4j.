MATCH (u1:User {userId: $userId})-[:RATED]->(s:Show)<-[:RATED]-(u2:User)
WHERE u1 <> u2
WITH u1, u2, COUNT(s) AS commonShows
WHERE commonShows > 0
MATCH (u2)-[r:RATED]->(rec:Show)
WHERE NOT EXISTS((u1)-[:RATED]->(rec))
RETURN rec.showId AS showId,
       rec.title AS title,
       rec.type AS type,
       AVG(r.score) AS predictedScore,
       COUNT(r) AS numRatings,
       commonShows
ORDER BY predictedScore DESC, numRatings DESC
LIMIT 10;