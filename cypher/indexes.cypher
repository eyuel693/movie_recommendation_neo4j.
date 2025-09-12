// Create indexes for better performance
CREATE INDEX IF NOT EXISTS FOR (s:Show) ON (s.showId);
CREATE INDEX IF NOT EXISTS FOR (s:Show) ON (s.title);
CREATE INDEX IF NOT EXISTS FOR (d:Director) ON (d.name);
CREATE INDEX IF NOT EXISTS FOR (a:Actor) ON (a.name);
CREATE INDEX IF NOT EXISTS FOR (c:Country) ON (c.name);
CREATE INDEX IF NOT EXISTS FOR (g:Genre) ON (g.name);
CREATE INDEX IF NOT EXISTS FOR (r:Rating) ON (r.name);
CREATE INDEX IF NOT EXISTS FOR (u:User) ON (u.userId);
