# ingest/fetch_and_load.py
import os
import tweepy
from dotenv import load_dotenv
from db.connect import get_connection
from utils.logging_config import setup_logger

logger = setup_logger(__name__)
load_dotenv()

def get_client():
    token = os.getenv("X_BEARER_TOKEN")
    if not token:
        raise RuntimeError("X_BEARER_TOKEN not found in .env")
    return tweepy.Client(bearer_token=token, wait_on_rate_limit=True)

def insert_user(cur, u):
    cur.execute("""
        INSERT INTO users (user_id, username, display_name, created_at, followers_count, verified)
        VALUES (%s,%s,%s,%s,%s,%s)
        ON CONFLICT (user_id) DO UPDATE SET
            username = EXCLUDED.username,
            display_name = EXCLUDED.display_name
    """, (u.id, u.username, u.name, u.created_at, u.public_metrics.get('followers_count'), u.verified))

def insert_tweet(cur, t):
    pm = t.public_metrics or {}
    cur.execute("""
        INSERT INTO tweets (tweet_id, user_id, text, created_at, lang, like_count, retweet_count, reply_count, quote_count)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
        ON CONFLICT (tweet_id) DO NOTHING
    """, (t.id, t.author_id, t.text, t.created_at, t.lang,
          pm.get('like_count'), pm.get('retweet_count'),
          pm.get('reply_count'), pm.get('quote_count')))

def insert_hashtags(cur, t):
    if t.entities and 'hashtags' in t.entities:
        for tag in t.entities['hashtags']:
            text = tag.get('tag')
            cur.execute("""
                INSERT INTO hashtags (tweet_id, tag)
                VALUES (%s, %s)
                ON CONFLICT (tweet_id, tag) DO NOTHING
            """, (t.id, text))

def insert_topic(cur, query):
    cur.execute("INSERT INTO topics (query) VALUES (%s) RETURNING topic_id", (query,))
    return cur.fetchone()[0]

def insert_tweet_topic(cur, topic_id, tweet_id):
    cur.execute("""
        INSERT INTO tweet_topics (topic_id, tweet_id)
        VALUES (%s, %s)
        ON CONFLICT (topic_id, tweet_id) DO NOTHING
    """, (topic_id, tweet_id))

def fetch_and_store(query: str, max_results: int = 20):
    client = get_client()
    conn = get_connection()
    logger.info(f"Fetching tweets for query: {query}")

    response = client.search_recent_tweets(
        query=query,
        tweet_fields=["created_at", "lang", "public_metrics", "entities"],
        user_fields=["created_at", "public_metrics", "username", "name", "verified"],
        expansions=["author_id"],
        max_results=max_results
    )

    if not response.data:
        logger.warning("No tweets found.")
        return

    users_dict = {u.id: u for u in response.includes.get("users", [])}

    with conn:
        with conn.cursor() as cur:
            topic_id = insert_topic(cur, query)
            for t in response.data:
                # insert user
                if t.author_id and t.author_id in users_dict:
                    insert_user(cur, users_dict[t.author_id])
                # insert tweet
                insert_tweet(cur, t)
                insert_hashtags(cur, t)
                insert_tweet_topic(cur, topic_id, t.id)

    logger.info(f"Ingestion completed for query: {query} — {len(response.data)} tweets stored.")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", required=True, help="Search query for tweets")
    parser.add_argument("--max", type=int, default=20, help="Max results")
    args = parser.parse_args()

    fetch_and_store(args.query, args.max)
