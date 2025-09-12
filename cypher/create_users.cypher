UNWIND range(1, 100) AS userId
MERGE (u:User {userId: userId})
RETURN count(u) AS users_created;
