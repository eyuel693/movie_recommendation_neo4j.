// Create Indexes and Constraints for Performance
CREATE CONSTRAINT FOR (s:Show) REQUIRE s.showId IS UNIQUE;
CREATE CONSTRAINT FOR (u:User) REQUIRE u.userId IS UNIQUE;
CREATE INDEX FOR (d:Director) ON (d.name);
CREATE INDEX FOR (a:Actor) ON (a.name);
CREATE INDEX FOR (c:Country) ON (c.name);
CREATE INDEX FOR (g:Genre) ON (g.name);
CREATE INDEX FOR (r:Rating) ON (r.name);
CREATE INDEX FOR (s:Show) ON (s.release_year);
CREATE INDEX FOR (s:Show) ON (s.type);