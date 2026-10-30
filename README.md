# Recruiter Bot

Recruiter Bot is a Python backend application that matches candidates with suitable job openings based on their skills, work experience, availability, and personality traits.

The main idea behind this project is simple: given a job, the application finds and ranks the most suitable candidates. It also works the other way around, allowing us to find suitable jobs for a particular candidate.

I built this project using **Python, Flask, and SQLite3**. Flask is used to create the API, while SQLite stores the candidate details, job requirements, and matching results.

All database operations are written using raw SQL queries, without using an ORM or query builder.

## 1. Technologies Used

- **Python:** Handles the application logic and calculates matching scores.
- **Flask:** Creates the REST API endpoints.
- **SQLite3:** Stores candidate information, job openings, skills, and matching results.
- **SQL:** Used to create tables, manage relationships, and retrieve data.
- **Pytest:** Used to test the API and matching functionality.

SQLite is included with Python, so there is no need to install a separate database server.

## 2. Project Structure

The project contains the following files:

```text
Recruiter-Bot/
│
├── app.py
├── db.py
├── schema.sql
├── seed.py
├── matching.py
├── conftest.py
├── requirements.txt
├── README.md
│
├── tests/
│
└───Part2/
    ├── sql_detective.sql
    ├── sql_detective_data.sql
    ├── load_detective.py
    ├── run_detective.py
    └── sql_detective_results.txt
```

### What each file does

- **app.py:** Contains the Flask API routes used to retrieve candidates, jobs, and matching results.
- **db.py:** Establishes the SQLite database connection and creates the database tables.
- **schema.sql:** Contains the SQL queries for creating tables and defining relationships.
- **seed.py:** Inserts the sample candidate and job data and generates the initial matching scores.
- **matching.py:** Contains the matching algorithm and queries used to rank candidates and jobs.
- **conftest.py:** Sets up a temporary database for testing.
- **tests/:** Contains the automated tests.
- **Part2/:** Contains the SQL Detective assignment and its queries.

## 3. How to Run the Project

Follow these steps to set up and run the application on your computer.

### Step 1: Open the project

Download or clone the project using https://github.com/VJKhanai/Recruiter-Bot.git
and open the `Recruiter-Bot` folder in any code Editor

Open a new terminal in VS Code using:

**Terminal → New Terminal**

Make sure the terminal is opened in the project's main directory.

### Step 2: Create a virtual environment

The project requires Python 3.9 or newer. It has been tested using Python 3.13.

Run:

```bash
python -m venv venv
```

This creates a virtual environment named `venv` to keep the project's dependencies separate from other Python projects.

Activate it using the appropriate command.

For Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

For Windows Command Prompt:

```cmd
venv\Scripts\activate.bat
```

For macOS or Linux:

```bash
source venv/bin/activate
```

Once activated, the terminal should show `(venv)` at the beginning of the line.

### Step 3: Install dependencies

Run:

```bash
pip install -r requirements.txt
```

This installs the Python packages required to run the application.

### Step 4: Create the database

Run:

```bash
python db.py
```

This executes the SQL statements from `schema.sql` and creates the required database tables.

The project uses SQLite, so the database is stored locally in a file named `recruiter.db`.

### Step 5: Insert sample data

Run:

```bash
python seed.py
```

This loads the sample data containing:

- 15 candidates
- 6 job openings
- Candidate skills and traits
- Job requirements and culture keywords

It also runs the matching algorithm and stores the calculated results in the `matches` table.

**Note:** Running `seed.py` again clears and reloads the sample data. It should not be rerun if you want to preserve changes made to the database.

### Step 6: Start the Flask server

Run:

```bash
python app.py
```

The application should start locally at:

```text
http://127.0.0.1:5000
```

Keep this terminal running while testing the API.

The server must remain active for the API endpoints to work.

## 4. Testing the API

The application provides REST API endpoints for retrieving candidates, jobs, and ranked matching results.

You can test these endpoints directly through a browser, Postman, or the VS Code terminal using `curl`.

For Windows PowerShell, use `curl.exe` instead of `curl`.

### Get all jobs

```bash
curl http://127.0.0.1:5000/jobs
```

This returns a list of available job openings.

### Get all candidates

```bash
curl http://127.0.0.1:5000/candidates
```

This returns the candidates stored in the database.

### Search for a job

```bash
curl "http://127.0.0.1:5000/jobs?q=detective"
```

This searches for jobs matching the word `detective`.

### Search for a candidate

```bash
curl "http://127.0.0.1:5000/candidates?q=sherlock"
```

This searches for candidates whose names match `sherlock`.

### Find candidates matching a job

```bash
curl http://127.0.0.1:5000/jobs/1/matches
```

This endpoint finds candidates suitable for the job with ID `1`.

The results are arranged according to their matching scores, with the highest-scoring candidates appearing first.

Example response:

```json
{
  "job_id": 1,
  "title": "Backend Detective",
  "matches": [
    {
      "candidate_id": 1,
      "name": "Sherlock H.",
      "score": 97.5,
      "reason": "Skills 3/3 (deduction, forensics, pattern-recognition); 8 years meets 3 minimum; immediate; culture 1/2"
    }
  ]
}
```

This response shows the candidate's name, matching score, and the reason behind the score.

The example is shortened for readability.

### Find jobs matching a candidate

```bash
curl http://127.0.0.1:5000/candidates/1/matches
```

This endpoint finds jobs suitable for the candidate with ID `1`.

Just like the previous endpoint, the jobs are ranked from the highest matching score to the lowest.

### Handling invalid IDs

If a requested job or candidate does not exist, the API returns a `404 Not Found` response.

For example:

```bash
curl http://127.0.0.1:5000/jobs/979/matches
```

Response:

```json
{
  "error": "job not found"
}
```

This makes it easier to identify invalid requests instead of returning incorrect data.

## 5. Database Design

I designed the database using separate tables for candidates, jobs, skills, and their relationships.

The main tables are:

| Table            | Purpose                                                 |
| ---------------- | ------------------------------------------------------- |
| candidates       | Stores candidate details, experience, and availability  |
| jobs             | Stores job openings and minimum experience requirements |
| skills           | Stores unique skill names                               |
| candidate_skills | Connects candidates with their skills                   |
| job_skills       | Connects jobs with their required skills                |
| candidate_traits | Stores candidate personality traits                     |
| job_culture      | Stores culture-related keywords for jobs                |
| matches          | Stores candidate-job matching scores and explanations   |

Instead of storing all skills as comma-separated text, I used separate relationship tables.

This makes it easier to compare candidate skills with job requirements using SQL JOIN operations.

It also avoids storing the same skill name repeatedly.

Candidate availability is restricted to three values:

- `immediate`
- `2_weeks`
- `not_looking`

This restriction is defined in the database schema to prevent invalid availability values from being stored.

## 6. Matching Algorithm and Design Decisions

The matching algorithm compares candidates with job requirements and calculates a score out of 100.

I divided the score into four parts:

| Factor                | Maximum Points |
| --------------------- | -------------: |
| Skills                |             60 |
| Experience            |             25 |
| Availability          |             10 |
| Culture compatibility |              5 |
| **Total**             |        **100** |

### Skill Matching (60 points)

Skills have the highest weight because they are the most important factor in deciding whether a candidate is suitable for a job.

The score depends on how many required skills the candidate possesses.

For example, if a job requires four skills and the candidate has three of them:

```text
Skill score = (3 / 4) × 60 = 45 points
```

If a candidate has no matching skills, the algorithm excludes that candidate from the matching results.

### Experience (25 points)

The algorithm compares the candidate's experience with the minimum experience required for the job.

If the candidate meets or exceeds the required experience, they receive all 25 points.

If they have less experience, they receive a proportional score.

For example, a candidate with two years of experience applying for a job requiring four years receives:

```text
Experience score = (2 / 4) × 25 = 12.5 points
```

I chose this approach because candidates who have slightly less experience may still be suitable if they have the required skills.

### Availability (10 points)

Candidates receive points based on how soon they are available to join.

| Availability   | Points |
| -------------- | -----: |
| Immediate      |     10 |
| Within 2 weeks |      6 |
| Not looking    |      0 |

This gives a small advantage to candidates who can join earlier.

### Culture Compatibility (5 points)

The algorithm also compares candidate traits with the culture keywords associated with a job.

For example, if a job expects someone who is analytical and autonomous, a candidate with one matching trait receives partial points.

Culture compatibility has a smaller weight because technical skills and experience are more important for the ranking.

### Final Score

The final score is calculated by adding the points from all four factors.

```text
Final Score = Skill Score
            + Experience Score
            + Availability Score
            + Culture Score
```
**Michael Scott.** The brief says he is applying for Sales Engineer, but his availability
is "Not looking". I didn't hide him. Availability is worth only 10 of the 100 points, so
he still ranks second for Sales Engineer (67.5), behind Dwight (75.0), who can start now.
Candidates and jobs are ranked according to this score.

When candidates have equal scores, experience and then name are used to determine the order. When jobs are ranked for a candidate, the job title is used instead of the name.

### The Michael Scott case

The brief says Michael Scott is applying for Sales Engineer, but his availability is "Not looking". I didn't hide him. Availability is worth only 10 of the 100 points, so he still ranks second for Sales Engineer (67.5), behind Dwight (75.0), who can start now.

## 7. Storing and Retrieving Matches

After inserting the sample data, `seed.py` runs the matching algorithm and saves the results in the `matches` table.

Each stored match contains the job ID, candidate ID, calculated score, and a short explanation.

When an API request is made, the application reads these stored results instead of recalculating every score.

This keeps API responses fast and avoids unnecessary calculations.

One limitation is that if candidate or job information changes, the stored scores must be updated.

For that, the project provides:

```python
matching.refresh_matches()
```

This recalculates and stores the matching results.

## 8. Automated Testing

I also included automated tests using Pytest.

To run the tests, open a terminal in the main project folder and execute:

```bash
python -m pytest -v
```

The test suite contains 17 tests.

The tests help check whether the application works as expected and whether changes to the code affect existing functionality.

A temporary database is used during testing, so the actual `recruiter.db` file is not modified.

## 9. Part 2 — SQL Detective

The second part of the assignment focuses on solving database problems using SQL queries.

All the SQL answers are written in:

```text
Part2/sql_detective.sql
```

To run this part, open the terminal and navigate to the `Part2` folder:

```bash
cd Part2
```

Load the required data:

```bash
python load_detective.py
```

Then execute the SQL queries:

```bash
python run_detective.py
```

The expected results are available in:

```text
Part2/sql_detective_results.txt
```

For Question 3, I used the lowercase version of the email address when grouping records. This handles cases where the same email address appears with different capitalization, such as the records for Ananya Rao.

## 10. Limitations and Possible Improvements

The current application works with the provided sample data, but a few things could be improved.

- **Exact skill names.** Skills are matched by exact name, so similar skills with different names are treated as different skills.
- **Weak skill matches can still score fairly well.** Candidates with no matching skills are excluded, but a candidate with only one of three required skills can still score around 45 to 55, because experience and availability add points. A minimum percentage of matching skills would fix this. I tested multiplying the whole score by the skill ratio, but kept the simpler formula, because the multiplier counted skills twice and made the scores harder to explain.
- **Scores can go stale.** The stored scores must be recalculated with `matching.refresh_matches()` whenever candidate or job data changes. For a larger system I would refresh them automatically.

## 11. AI Tools Used

## 11. AI Tools Used

I used Claude as a learning and development assistant while building this project.

I started by explaining my own outline of the project: the tables, the scoring idea and the API endpoints. Claude then suggested alternative approaches, for example different ways to design the schema, other scoring formulas (an experience bonus and a skill multiplier), and ways to structure the Flask routes. I compared the options, tried some of them on the sample data, and chose the ones I could explain and defend.

It also helped me with documentation. I used it to organise this README, explain my decisions clearly, and write the SQL Detective notes.

I did not accept suggestions as they came. I questioned each one, thought it through, and proposed my own idea before going ahead. For example, I switched from MySQL back to SQLite so a reviewer does not have to install a database server, I undid a more detailed response format because it was too hard to read, and I kept the simpler scoring formula after testing the alternatives. I ran every step myself and checked the results with curl requests and automated tests, so I can explain how each part works.