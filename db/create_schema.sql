CREATE TABLE IF NOT EXISTS users (
  user_id TEXT PRIMARY KEY,
  username TEXT,
  display_name TEXT,
  created_at TIMESTAMPTZ,
  followers_count INT,
  verified BOOLEAN
);

CREATE TABLE IF NOT EXISTS tweets (
  tweet_id TEXT PRIMARY KEY,
  user_id TEXT REFERENCES users(user_id),
  text TEXT,
  created_at TIMESTAMPTZ,
  lang TEXT,
  like_count INT,
  retweet_count INT,
  reply_count INT,
  quote_count INT
);

CREATE TABLE IF NOT EXISTS hashtags (
  tweet_id TEXT REFERENCES tweets(tweet_id),
  tag TEXT,
  PRIMARY KEY (tweet_id, tag)
);

CREATE TABLE IF NOT EXISTS topics (
  topic_id SERIAL PRIMARY KEY,
  query TEXT,
  run_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS tweet_topics (
  topic_id INT REFERENCES topics(topic_id),
  tweet_id TEXT REFERENCES tweets(tweet_id),
  PRIMARY KEY (topic_id, tweet_id)
);
