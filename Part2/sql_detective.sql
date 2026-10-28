-- Q1: open job postings and who owns them
SELECT j.id, j.title, j.department, j.opened_date, r.name AS recruiter
FROM job_postings j
JOIN recruiters r ON r.id = j.recruiter_id
WHERE j.status = 'open'
ORDER BY j.id;

-- Q2: number of applicants who reached the Final stage, per posting
-- used LEFT JOIN so postings with 0 finalists still show up
-- the stage check has to be in ON, if it was in WHERE those postings would disappear
SELECT j.id, j.title, COUNT(DISTINCT i.applicant_id) AS finalists
FROM job_postings j
LEFT JOIN interviews i
       ON i.job_posting_id = j.id AND i.stage = 'Final'
GROUP BY j.id, j.title
ORDER BY j.id;

-- Q3: people who applied to more than one posting
-- Ananya Rao is in the table twice (ids 1 and 2) with different email casing
-- so i lowercase the email and group on that to treat her as one person
-- applicants has no posting column so i get the postings from interviews
SELECT LOWER(TRIM(a.email)) AS email,
       MIN(a.full_name) AS full_name,
       COUNT(DISTINCT i.job_posting_id) AS postings
FROM applicants a
JOIN interviews i ON i.applicant_id = a.id
GROUP BY LOWER(TRIM(a.email))
HAVING COUNT(DISTINCT i.job_posting_id) > 1
ORDER BY full_name;

-- Q4: final stage pass rate per recruiter (only if they had 3 or more finals)
-- 100.0 instead of 100 so the division is not rounded down to a whole number
SELECT r.id, r.name,
       COUNT(*) AS total_finals,
       SUM(CASE WHEN i.outcome = 'passed' THEN 1 ELSE 0 END) AS passed,
       ROUND(100.0 * SUM(CASE WHEN i.outcome = 'passed' THEN 1 ELSE 0 END) / COUNT(*), 1) AS pass_rate
FROM interviews i
JOIN job_postings j ON j.id = i.job_posting_id
JOIN recruiters r ON r.id = j.recruiter_id
WHERE i.stage = 'Final'
GROUP BY r.id, r.name
HAVING COUNT(*) >= 3
ORDER BY pass_rate DESC;

-- Q5 (bonus): top recruiter in each department by successful placements
-- a placement = passed the Final stage
-- using RANK() so if two recruiters tie, both are shown
WITH placed AS (
    SELECT j.department, r.name, COUNT(*) AS placements
    FROM interviews i
    JOIN job_postings j ON j.id = i.job_posting_id
    JOIN recruiters r ON r.id = j.recruiter_id
    WHERE i.stage = 'Final' AND i.outcome = 'passed'
    GROUP BY j.department, r.id, r.name
),
ranked AS (
    SELECT department, name, placements,
           RANK() OVER (PARTITION BY department ORDER BY placements DESC) AS rnk
    FROM placed
)
SELECT department, name, placements
FROM ranked
WHERE rnk = 1
ORDER BY department;
-- 