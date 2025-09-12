MATCH (u:User {userId: $userId})-[r:RATED]->(s:Show)-[:IN_GENRE]->(favGenre:Genre)
WHERE r.score >= 3.5
WITH collect(DISTINCT favGenre) AS favGenres, u

CALL {
    WITH favGenres, u
    // If user has no favorite genres, pick top 3 most popular genres
    WITH CASE WHEN size(favGenres) = 0 
              THEN [g IN [(s:Show)-[:IN_GENRE]->(g:Genre) | g] | g][0..3] 
              ELSE favGenres END AS genres, u

    MATCH (rec:Show)-[:IN_GENRE]->(g:Genre)
    WHERE g IN genres
      AND NOT EXISTS((u)-[:RATED]->(rec))
    RETURN rec.title AS recommendation,
           rec.type AS type,
           g.name AS genre,
           "Based on your favorite genres" AS reason,
           rec.release_year AS year
    ORDER BY rec.release_year DESC
    LIMIT 10
}

RETURN recommendation, type, genre, reason, year;
