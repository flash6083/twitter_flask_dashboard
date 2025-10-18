# web/app.py
import math
from flask import Flask, render_template, request, redirect, url_for, flash
from dotenv import load_dotenv
from db.connect import get_connection
from utils.logging_config import setup_logger

logger = setup_logger(__name__)
load_dotenv()

app = Flask(__name__, template_folder="templates")
app.secret_key = "your_secret_key"  # required for flash messages

PAGE_SIZE = 20

@app.route("/", methods=["GET", "POST"])
def index():
    results = []
    total_count = 0
    filters = {"q": "", "hashtag": "", "username": "", "start": "", "end": ""}
    page = int(request.args.get("page", 1))

    if request.method == "POST":
        # redirect with GET query params for cleaner pagination
        q = request.form.get("q", "")
        hashtag = request.form.get("hashtag", "")
        username = request.form.get("username", "")
        start = request.form.get("start_date", "")
        end = request.form.get("end_date", "")

        return redirect(url_for("index",
                                q=q, hashtag=hashtag, username=username,
                                start=start, end=end, page=1))

    # filters from URL params
    filters["q"] = request.args.get("q", "")
    filters["hashtag"] = request.args.get("hashtag", "")
    filters["username"] = request.args.get("username", "")
    filters["start"] = request.args.get("start", "")
    filters["end"] = request.args.get("end", "")

    sql = """
        SELECT t.tweet_id, t.created_at, u.username, t.text,
               COALESCE(string_agg(h.tag, ','), '') AS hashtags,
               t.like_count, t.retweet_count
        FROM tweets t
        JOIN users u ON t.user_id = u.user_id
        LEFT JOIN hashtags h ON h.tweet_id = t.tweet_id
        WHERE 1=1
    """
    params = []

    if filters["q"]:
        sql += " AND t.text ILIKE %s"
        params.append(f"%{filters['q']}%")
    if filters["hashtag"]:
        sql += " AND EXISTS (SELECT 1 FROM hashtags h2 WHERE h2.tweet_id=t.tweet_id AND h2.tag ILIKE %s)"
        params.append(f"%{filters['hashtag']}%")
    if filters["username"]:
        sql += " AND u.username ILIKE %s"
        params.append(f"%{filters['username']}%")
    if filters["start"]:
        sql += " AND t.created_at >= %s"
        params.append(filters["start"])
    if filters["end"]:
        sql += " AND t.created_at <= %s"
        params.append(filters["end"])

    group_sql = """
        GROUP BY t.tweet_id, t.created_at, u.username, t.text, t.like_count, t.retweet_count
    """
    order_sql = " ORDER BY t.created_at DESC"

    count_sql = f"SELECT COUNT(*) FROM ({sql + group_sql}) sub"
    offset = (page - 1) * PAGE_SIZE
    limit_sql = f" LIMIT {PAGE_SIZE} OFFSET {offset}"

    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(count_sql, params)
        total_count = cur.fetchone()[0]
        total_pages = max(1, math.ceil(total_count / PAGE_SIZE))

        cur.execute(sql + group_sql + order_sql + limit_sql, params)
        results = cur.fetchall()

    if total_count == 0:
        flash("No tweets found for your query.", "warning")
    else:
        flash(f"Showing page {page} of {total_pages} — {total_count} results found.", "success")

    return render_template("index.html",
                           results=results,
                           filters=filters,
                           page=page,
                           total_pages=total_pages)

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)