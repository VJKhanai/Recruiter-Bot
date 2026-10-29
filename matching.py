import db

# Scoring weights (they add up to 100)
W_SKILLS = 60
W_EXPERIENCE = 25
W_AVAILABILITY = 10
W_CULTURE = 5

AVAILABILITY_POINTS = {"immediate": 10, "2_weeks": 6, "not_looking": 0}

# One row per (job, candidate) pair, with all the counts we need
PAIR_SQL = """
SELECT
    j.id    AS job_id,
    j.title AS job_title,
    j.min_experience,
    c.id    AS candidate_id,
    c.name  AS candidate_name,
    c.experience_years,
    c.availability,
    (SELECT COUNT(*) FROM job_skills js
      WHERE js.job_id = j.id) AS required_count,
    (SELECT COUNT(*) FROM job_skills js
       JOIN candidate_skills cs ON cs.skill_id = js.skill_id
      WHERE js.job_id = j.id AND cs.candidate_id = c.id) AS matched_count,
    (SELECT group_concat(name, ', ') FROM (
        SELECT s.name AS name
          FROM job_skills js
          JOIN candidate_skills cs ON cs.skill_id = js.skill_id
          JOIN skills s ON s.id = js.skill_id
         WHERE js.job_id = j.id AND cs.candidate_id = c.id
         ORDER BY s.name)) AS matched_skills,
    (SELECT COUNT(*) FROM job_culture jc
      WHERE jc.job_id = j.id) AS culture_count,
    (SELECT COUNT(*) FROM job_culture jc
       JOIN candidate_traits ct ON ct.trait = jc.keyword
      WHERE jc.job_id = j.id AND ct.candidate_id = c.id) AS trait_matches
FROM jobs j
CROSS JOIN candidates c
"""


def _fetch_pairs():
    conn = db.get_conn()
    rows = conn.execute(PAIR_SQL).fetchall()
    conn.close()
    return rows


def score_pair(row):
    """Turn one (job, candidate) row into (score, reason)."""
    # 1. Skills
    if row["required_count"] > 0:
        skill_pts = W_SKILLS * row["matched_count"] / row["required_count"]
    else:
        skill_pts = 0

    # 2. Experience
    if row["experience_years"] >= row["min_experience"]:
        exp_pts = W_EXPERIENCE
        exp_text = f"{row['experience_years']} years meets {row['min_experience']} minimum"
    else:
        exp_pts = W_EXPERIENCE * row["experience_years"] / row["min_experience"]
        exp_text = f"{row['experience_years']} years is below {row['min_experience']} minimum"

    # 3. Availability
    avail_pts = AVAILABILITY_POINTS[row["availability"]]

    # 4. Culture
    if row["culture_count"] > 0:
        culture_pts = W_CULTURE * row["trait_matches"] / row["culture_count"]
    else:
        culture_pts = 0

    score = round(skill_pts + exp_pts + avail_pts + culture_pts, 1)
    reason = (
        f"Skills {row['matched_count']}/{row['required_count']} "
        f"({row['matched_skills']}); {exp_text}; "
        f"{row['availability'].replace('_', ' ')}; "
        f"culture {row['trait_matches']}/{row['culture_count']}"
    )
    return score, reason


def refresh_matches():
    """Recompute every score and store it in the matches table."""
    pairs = _fetch_pairs()
    conn = db.get_conn()
    conn.execute("DELETE FROM matches")
    for row in pairs:
        if row["matched_count"] == 0:
            continue  # no skill overlap, not a match
        score, reason = score_pair(row)
        conn.execute(
            "INSERT INTO matches (job_id, candidate_id, score, reason) "
            "VALUES (?, ?, ?, ?)",
            (row["job_id"], row["candidate_id"], score, reason),
        )
    conn.commit()
    conn.close()


def rank_candidates_for_job(job_id):
    conn = db.get_conn()
    rows = conn.execute(
        "SELECT c.id AS candidate_id, c.name, m.score, m.reason "
        "FROM matches m JOIN candidates c ON c.id = m.candidate_id "
        "WHERE m.job_id = ? "
        "ORDER BY m.score DESC, c.experience_years DESC, c.name ASC",
        (job_id,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def rank_jobs_for_candidate(candidate_id):
    conn = db.get_conn()
    rows = conn.execute(
        "SELECT j.id AS job_id, j.title, m.score, m.reason "
        "FROM matches m JOIN jobs j ON j.id = m.job_id "
        "WHERE m.candidate_id = ? "
        "ORDER BY m.score DESC, j.title ASC",
        (candidate_id,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]