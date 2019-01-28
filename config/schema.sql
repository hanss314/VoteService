DROP TABLE IF EXISTS guilds;
DROP TABLE IF EXISTS responses;
DROP TABLE IF EXISTS votes;
CREATE TABLE guilds (
  id VARCHAR(20) UNIQUE,
  deadline TIMESTAMP,
  length INT,
  canvote BOOLEAN
);

CREATE TABLE responses (
  guild VARCHAR(20),
  ind INT,
  author TEXT,
  content TEXT
);

CREATE TABLE votes (
  guild VARCHAR(20),
  voter VARCHAR(20),
  responses INT[]
);