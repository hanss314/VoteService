DROP TABLE IF EXISTS guilds;
DROP TABLE IF EXISTS responses;
CREATE TABLE guilds (
  id VARCHAR(20),
  deadline TIMESTAMP,
  settings INT
);

CREATE TABLE responses (
  guild VARCHAR(20),
  ind INT,
  author TEXT,
  content TEXT
);
