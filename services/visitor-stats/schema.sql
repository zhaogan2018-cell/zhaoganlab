CREATE TABLE IF NOT EXISTS visits (id TEXT PRIMARY KEY, country TEXT NOT NULL, created TEXT NOT NULL);
CREATE INDEX IF NOT EXISTS visits_created ON visits(created);
CREATE TABLE IF NOT EXISTS countries (country TEXT PRIMARY KEY, count INTEGER NOT NULL DEFAULT 0);
CREATE TABLE IF NOT EXISTS metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL);
CREATE TRIGGER IF NOT EXISTS count_visit AFTER INSERT ON visits BEGIN
 INSERT INTO countries(country,count) VALUES (NEW.country,1) ON CONFLICT(country) DO UPDATE SET count=count+1;
 INSERT OR IGNORE INTO metadata(key,value) VALUES ('started_at',NEW.created);
END;
