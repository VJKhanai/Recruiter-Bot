from flask import Flask, jsonify, request

import db
import matching

app = Flask(__name__)


def find_name(table, column, row_id):
    """Return the name/title for an id, or None if the id doesn't exist.
    table and column are hardcoded below, never user input."""
    conn = db.get_conn()
    row = conn.execute(
        f"SELECT {column} FROM {table} WHERE id = ?", (row_id,)
    ).fetchone()
    conn.close()
    return row[0] if row else None


@app.route("/jobs")
def list_jobs():
    q = request.args.get("q", "").strip()
    conn = db.get_conn()
    rows = conn.execute(
        "SELECT id, title, min_experience FROM jobs "
        "WHERE title LIKE ? ORDER BY id",
        (f"%{q}%",),
    ).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


@app.route("/candidates")
def list_candidates():
    q = request.args.get("q", "").strip()
    conn = db.get_conn()
    rows = conn.execute(
        "SELECT id, name, experience_years, availability FROM candidates "
        "WHERE name LIKE ? ORDER BY id",
        (f"%{q}%",),
    ).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


@app.route("/jobs/<int:job_id>/matches")
def job_matches(job_id):
    title = find_name("jobs", "title", job_id)
    if title is None:
        return jsonify({"error": "job not found"}), 404
    return jsonify({
        "job_id": job_id,
        "title": title,
        "matches": matching.rank_candidates_for_job(job_id),
    })


@app.route("/candidates/<int:candidate_id>/matches")
def candidate_matches(candidate_id):
    name = find_name("candidates", "name", candidate_id)
    if name is None:
        return jsonify({"error": "candidate not found"}), 404
    return jsonify({
        "candidate_id": candidate_id,
        "name": name,
        "matches": matching.rank_jobs_for_candidate(candidate_id),
    })


if __name__ == "__main__":
    app.run(debug=True)