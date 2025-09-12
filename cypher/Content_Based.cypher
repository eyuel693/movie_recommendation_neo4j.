// Content-Based Recommendation
MATCH (u:User {userId: 5})-[r:RATED]->(s:Show)
OPTIONAL MATCH (s)<-[:ACTED_IN]-(a:Actor)-[:ACTED_IN]->(rec:Show)
OPTIONAL MATCH (s)<-[:DIRECTED]-(d:Director)-[:DIRECTED]->(rec)
OPTIONAL MATCH (s)-[:PRODUCED_IN]->(c:Country)<-[:PRODUCED_IN]-(rec)
OPTIONAL MATCH (s)-[:HAS_RATING]->(rat:Rating)<-[:HAS_RATING]-(rec)
WHERE rec <> s
WITH rec, count(DISTINCT a) + count(DISTINCT d) + count(DISTINCT c) + count(DISTINCT rat) AS similarityScore
WHERE similarityScore > 0
RETURN rec.title AS recommendation,
       similarityScore
ORDER BY similarityScore DESC
LIMIT 10;