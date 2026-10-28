import matching

# A perfect-fit row, used as a starting point. Each test changes one thing.
BASE = {
    "required_count": 3,
    "matched_count": 3,
    "matched_skills": "a, b, c",
    "min_experience": 3,
    "experience_years": 8,
    "availability": "immediate",
    "culture_count": 2,
    "trait_matches": 2,
}


def make_row(**changes):
    row = dict(BASE)
    row.update(changes)
    return row


# ---------- scoring math (no database needed) ----------

def test_perfect_match_scores_100():
    score, _ = matching.score_pair(make_row())
    assert score == 100.0


def test_under_experienced_gets_partial_credit():
    # 2 yrs for a 4 yr job: 25 * 2/4 = 12.5, so 60 + 12.5 + 0 + 0 = 72.5
    row = make_row(experience_years=2, min_experience=4,
                   availability="not_looking", trait_matches=0)
    score, reason = matching.score_pair(row)
    assert score == 72.5
    assert "below" in reason


def test_immediate_beats_two_weeks_by_four_points():
    now, _ = matching.score_pair(make_row(availability="immediate"))
    later, _ = matching.score_pair(make_row(availability="2_weeks"))
    assert now - later == 4


def test_job_without_culture_keywords_does_not_crash():
    row = make_row(culture_count=0, trait_matches=0)
    score, _ = matching.score_pair(row)
    assert score == 95.0  # 60 + 25 + 10 + 0


def test_job_without_required_skills_does_not_crash():
    row = make_row(required_count=0, matched_count=0)
    score, _ = matching.score_pair(row)
    assert score == 40.0  # 0 + 25 + 10 + 5


# ---------- ranking on the seeded data ----------

def test_zero_overlap_candidates_are_excluded(seeded_db):
    names = [r["name"] for r in matching.rank_candidates_for_job(1)]
    assert names == ["Sherlock H.", "Sheldon C."]  # Ron etc. are not listed


def test_sherlock_is_top_match_for_backend_detective(seeded_db):
    top = matching.rank_candidates_for_job(1)[0]
    assert top["name"] == "Sherlock H."
    assert top["score"] == 97.5


def test_michael_best_job_is_sales_engineer(seeded_db):
    best = matching.rank_jobs_for_candidate(11)[0]
    assert best["title"] == "Sales Engineer"
    assert best["score"] == 67.5


def test_dwight_ranks_above_michael_for_sales_engineer(seeded_db):
    # Job 6 is Sales Engineer. Dwight is available now, Michael is not looking.
    names = [r["name"] for r in matching.rank_candidates_for_job(6)]
    assert names.index("Dwight S.") < names.index("Michael S.")


def test_ties_are_broken_by_experience(seeded_db):
    # Leslie (6 yrs) and Elle (3 yrs) both score 55.0 for job 6
    ranked = matching.rank_candidates_for_job(6)
    scores = {r["name"]: r["score"] for r in ranked}
    assert scores["Leslie K."] == scores["Elle W."]
    names = [r["name"] for r in ranked]
    assert names.index("Leslie K.") < names.index("Elle W.")