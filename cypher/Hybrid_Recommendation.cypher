// Hybrid Recommendation
MATCH (u1:User {userId: 5})-[:RATED]->(s:Show)<-[:RATED]-(u2:User)
WHERE u1 <> u2
WITH u1, u2, count(s) AS commonShows
WHERE commonShows > 2
MATCH (u2)-[r:RATED]->(rec:Show)
WHERE NOT (u1)-[:RATED]->(rec)
WITH u1, rec, avg(r.score) AS cfScore, commonShows
OPTIONAL MATCH (rec)<-[:ACTED_IN]-(a:Actor)-[:ACTED_IN]->(s:Show)<-[r1:RATED]-(u1)
WHERE r1.score >= 4
WITH rec, cfScore, commonShows, count(DISTINCT a) AS actorOverlap
RETURN rec.title AS recommendation,
       cfScore + actorOverlap AS finalScore,
       cfScore,
       actorOverlap,
       commonShows
ORDER BY finalScore DESC
LIMIT 10;