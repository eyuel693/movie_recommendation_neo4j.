LOAD CSV WITH HEADERS FROM 'file:///netflix_data.csv' AS row
WITH row WHERE row.show_id IS NOT NULL
MERGE (s:Show {showId: row.show_id})
SET s.title = coalesce(row.title, 'Unknown'),
    s.type = coalesce(row.type, 'Unknown'),
    s.date_added = coalesce(row.date_added, 'Unknown'),
    s.release_year = CASE WHEN row.release_year <> '' THEN toInteger(row.release_year) ELSE NULL END,
    s.duration = coalesce(row.duration, 'Unknown')
RETURN count(s) AS shows_loaded;
