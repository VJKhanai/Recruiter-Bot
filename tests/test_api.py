def test_job_matches_returns_ranked_candidates(client):
    res = client.get("/jobs/1/matches")
    assert res.status_code == 200
    data = res.get_json()
    assert data["title"] == "Backend Detective"
    assert data["matches"][0]["name"] == "Sherlock H."
    assert "reason" in data["matches"][0]


def test_candidate_matches_returns_ranked_jobs(client):
    res = client.get("/candidates/1/matches")
    assert res.status_code == 200
    data = res.get_json()
    assert data["name"] == "Sherlock H."
    assert data["matches"][0]["title"] == "Backend Detective"


def test_unknown_job_returns_404(client):
    res = client.get("/jobs/999/matches")
    assert res.status_code == 404
    assert res.get_json()["error"] == "job not found"


def test_unknown_candidate_returns_404(client):
    res = client.get("/candidates/999/matches")
    assert res.status_code == 404


def test_list_all_jobs(client):
    res = client.get("/jobs")
    assert len(res.get_json()) == 6


def test_search_jobs_by_title(client):
    res = client.get("/jobs?q=detective")
    data = res.get_json()
    assert len(data) == 1
    assert data[0]["title"] == "Backend Detective"


def test_search_candidates_by_name(client):
    res = client.get("/candidates?q=sherlock")
    data = res.get_json()
    assert len(data) == 1
    assert data[0]["name"] == "Sherlock H."