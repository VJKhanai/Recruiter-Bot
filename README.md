# Recruiter Bot

A small backend service that ranks candidates for a job, and jobs for a candidate.
Python + Flask + SQLite. All database access is hand-written SQL (no ORM, no query builder).

## Setup

Needs Python 3.9 or newer (tested on 3.13). No database server to install, SQLite comes with Python.

```bash
python -m venv venv
venv\Scripts\activate          # Mac/Linux: source venv/bin/activate
pip install -r requirements.txt

python db.py       # creates the tables from schema.sql
python seed.py     # loads 15 candidates and 6 jobs, then scores every pair
python app.py      # starts the server on http://127.0.0.1:5000
```

Run the tests with `python -m pytest -v` (17 tests).

## API

Ids are easy to look up, so you don't need to remember them:

```bash
curl http://127.0.0.1:5000/jobs
curl http://127.0.0.1:5000/candidates
curl "http://127.0.0.1:5000/jobs?q=detective"
curl "http://127.0.0.1:5000/candidates?q=sherlock"
```

Ranked matches:

```bash
curl http://127.0.0.1:5000/jobs/1/matches          # candidates for a job
curl http://127.0.0.1:5000/candidates/1/matches    # jobs for a candidate
```

Example (`/jobs/1/matches`, shortened):

```json
{
  "job_id": 1,
  "title": "Backend Detective",
  "matches": [
    {
      "candidate_id": 1,
      "name": "Sherlock H.",
      "score": 97.5,
      "reason": "Skills 3/3 (deduction, forensics, pattern-recognition); 8 yrs meets 3 min; immediate; culture 1/2"
    }
  ]
}
```

An unknown id returns 404 with `{"error": "job not found"}` (or `candidate not found`).
On PowerShell use `curl.exe`, because plain `curl` is an alias for something else.

## Schema

- `candidates`, `jobs`: one row each.
- `skills`: every skill name stored once. `candidate_skills` and `job_skills` link to it, so
  "which skills do they share" is a plain JOIN + COUNT instead of string parsing.
- `candidate_traits` and `job_culture`: small lists of words.
- `matches`: one row per scored (job, candidate) pair, with the score and the reason text.

Availability is limited by a CHECK constraint to `immediate`, `2_weeks` or `not_looking`,
so the scoring never meets a value it doesn't know.

## Matching algorithm

Score out of 100:

| Part | Points | Rule |
|---|---|---|
| Skill overlap | 60 | matched skills / required skills x 60 |
| Experience | 25 | full points if the candidate meets the minimum, otherwise proportional |
| Availability | 10 | immediate 10, 2 weeks 6, not looking 0 |
| Culture | 5 | traits matching the job's culture keywords / keywords x 5 |

Decisions and trade-offs:

- **Skills weigh the most**, because they decide whether someone can do the job. Experience
  comes second. Availability and culture only nudge the ranking.
- **No skill overlap means no match.** Without this, a candidate with zero relevant skills
  could still score 35 points from experience and availability and appear in the list.
- **Under-experienced candidates get partial credit** instead of being dropped.
- **Ties** are broken by more experience, then by name, so the order is always the same.
- **Matches are precomputed** and stored in the `matches` table by `seed.py`. The API only
  reads them with an indexed ORDER BY. Trade-off: reads are fast, but the table has to be
  refreshed (`matching.refresh_matches()`) whenever candidates or jobs change.
- **SQL fetches the counts, Python applies the weights.** All weights sit at the top of
  `matching.py`, so tuning them is a one-line change.

Known limitations: skills match by exact name (no synonyms), every required skill counts
equally, and a weak skill match can still score around 45-55 because experience and
availability add points. A minimum skill ratio would fix that.

## Part 2: SQL Detective

Answers are in `Part2/sql_detective.sql`, one query per question. To run them:

```bash
cd Part2
python load_detective.py
python run_detective.py
```

Expected output is saved in `Part2/sql_detective_results.txt`.
Q3 groups by the lowercased email, because Ananya Rao appears twice with different casing.

## Project layout

```
app.py          Flask routes
db.py           database connection and schema loader
schema.sql      table definitions
seed.py         sample data + first scoring run
matching.py     scoring logic and ranking queries
conftest.py     test setup (temporary database)
tests/          pytest tests
Part2/          SQL Detective files
```

## AI tools

Write this yourself, honestly. For example: "I used Claude as a tutor and pair-programmer.
It helped me design the schema and scoring and explained each step. I ran and tested every
part myself and can explain it."