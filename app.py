from flask import Flask, jsonify

import db
import matching

app = Flask(__name__)


def exists(table, row_id):
    """Check if a row with this id exists. Table names are hardcoded below, never user input."""
    conn = db.get_conn()
    row = conn.execute(f"SELECT 1 FROM {table} WHERE id = ?", (row_id,)).fetchone()
    conn.close()
    return row is not None


@app.route("/jobs/<int:job_id>/matches")
def job_matches(job_id):
    if not exists("jobs", job_id):
        return jsonify({"error": "job not found"}), 404
    return jsonify({
        "job_id": job_id,
        "matches": matching.rank_candidates_for_job(job_id),
    })


@app.route("/candidates/<int:candidate_id>/matches")
def candidate_matches(candidate_id):
    if not exists("candidates", candidate_id):
        return jsonify({"error": "candidate not found"}), 404
    return jsonify({
        "candidate_id": candidate_id,
        "matches": matching.rank_jobs_for_candidate(candidate_id),
    })


if __name__ == "__main__":
    app.run(debug=True)