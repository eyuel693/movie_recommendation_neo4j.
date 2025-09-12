// Collaborative Filtering Recommendation
// Find users who rated similar shows and recommend unseen ones
MATCH (u1:User {userId: 5})-[:RATED]->(s:Show)<-[:RATED]-(u2:User)
WHERE u1 <> u2
WITH u1, u2, count(s) AS commonShows
WHERE commonShows > 2
MATCH (u2)-[r:RATED]->(rec:Show)
WHERE NOT (u1)-[:RATED]->(rec)
RETURN rec.title AS recommendation,
       avg(r.score) AS predictedScore,
       commonShows
ORDER BY predictedScore DESC, commonShows DESC
LIMIT 10;