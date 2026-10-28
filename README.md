# Recruiter Bot

A small backend service that ranks candidates for jobs (and jobs for candidates).
Python + Flask + SQLite, using only hand-written raw SQL (no ORM or query builder).

## Setup

```bash
python -m venv venv
venv\Scripts\activate        # Mac/Linux: source venv/bin/activate
pip install -r requirements.txt

python db.py       # create tables
python seed.py     # load 15 candidates and 6 jobs
python app.py      # start server on http://127.0.0.1:5000
```

## API

```bash
curl http://127.0.0.1:5000/jobs/1/matches
curl http://127.0.0.1:5000/candidates/1/matches
```

Both return a ranked list with a `score` (0-100) and a short `reason`.
Unknown ids return 404.

## Schema

Skills, traits and culture keywords are normalized into join tables
(`candidate_skills`, `job_skills`, `candidate_traits`, `job_culture`) so skill
overlap is a plain SQL JOIN + COUNT. Skills share one `skills` table, so a skill
like `public-speaking` is a single row used by both candidates and jobs.
Availability is a constrained value (`immediate`, `2_weeks`, `not_looking`).

## Matching algorithm

Score out of 100:

| Part | Points | Rule |
|---|---|---|
| Skill overlap | 60 | matched skills / required skills x 60 |
| Experience fit | 25 | full points if experience >= minimum, otherwise proportional |
| Availability | 10 | immediate 10, 2 weeks 6, not looking 0 |
| Culture fit | 5 | traits matching job culture keywords / keywords x 5 |

Decisions and trade-offs:

- **Skills weigh most** because they decide whether someone can do the job.
  Experience is second. Availability and culture only nudge the ranking.
- **Zero skill overlap means no match.** Without this, someone with no relevant
  skills could still score points for experience and availability.
- **Under-experienced candidates get partial credit** instead of being excluded,
  since a strong skill match with slightly fewer years may still be worth a look.
- **Ties** are broken by more experience, then name, so the order is deterministic.
- **Scores are computed on request**, not stored. With 90 possible pairs this is
  cheap, and results never go stale when data changes. At large scale I would
  precompute and cache them.
- **SQL fetches the counts, Python applies the weights.** All weights live in
  one place (`matching.py`), so tuning them is a one-line change.
- **Known limitations:** skills are matched by exact name (no synonyms), and
  all required skills count equally.

## Part 2: SQL Detective

Answers are in `Part2/sql_detective.sql`, one query per question.
To run them: `cd Part2`, then `python load_detective.py`, then `python run_detective.py`.
Q3 groups by lowercased email because the same person appears with different casing.

