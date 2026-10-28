import db
import matching

CANDIDATES = [
    # name, experience, availability, quirk, skills, traits
    ("Sherlock H.", 8, "immediate",
     "Solves problems by eliminating the impossible; occasionally insufferable in standups.",
     ["deduction", "pattern-recognition", "forensics"], ["analytical", "blunt"]),
    ("Hermione G.", 4, "2_weeks",
     "Reads the entire documentation before writing a single line of code.",
     ["research", "time-management", "public-speaking"], ["detail-oriented", "overachiever"]),
    ("Tony S.", 12, "not_looking",
     "Ships an MVP overnight, refuses to write tests.",
     ["systems-design", "rapid-prototyping", "leadership"], ["confident", "innovative"]),
    ("Leslie K.", 6, "immediate",
     "Has a binder for everything, including the binder.",
     ["project-management", "stakeholder-management", "public-speaking"], ["tenacious", "organized"]),
    ("Ron S.", 15, "not_looking",
     "Refuses to use more than one monitor.",
     ["woodworking", "minimalism", "negotiation"], ["stubborn", "principled"]),
    ("Rick S.", 20, "immediate",
     "Solution works, mechanism deeply concerning.",
     ["systems-design", "rapid-prototyping", "chemistry"], ["genius", "reckless"]),
    ("Elle W.", 3, "immediate",
     "Underestimated in every standup, correct in every retro.",
     ["persuasion", "research", "public-speaking"], ["optimistic", "sharp"]),
    ("MacGyver", 10, "2_weeks",
     "Fixes production outages with duct tape and a paperclip metaphor.",
     ["rapid-prototyping", "resourcefulness", "chemistry", "systems-design"], ["calm", "improviser"]),
    ("Sheldon C.", 9, "immediate",
     "Correct 95% of the time, insufferable 100% of the time.",
     ["theoretical-analysis", "pattern-recognition", "research"], ["rigid", "brilliant"]),
    ("Katniss E.", 5, "immediate",
     "Excellent under pressure, terrible with public speaking.",
     ["precision", "strategy", "crisis-management"], ["resilient", "decisive"]),
    ("Michael S.", 11, "not_looking",
     "World's best boss, according to a mug he bought himself.",
     ["sales", "public-speaking", "team-building"], ["enthusiastic", "chaotic"]),
    ("Olivia P.", 13, "2_weeks",
     "Handles it. Whatever it is.",
     ["crisis-management", "negotiation", "strategy", "leadership"], ["decisive", "intense"]),
    ("Ted L.", 7, "immediate",
     "Turns every technical setback into a folksy metaphor.",
     ["team-building", "optimism", "mentorship", "public-speaking"], ["empathetic", "persistent"]),
    ("Miranda P.", 18, "not_looking",
     "Reviews every PR personally. Says nothing. Everyone panics.",
     ["leadership", "negotiation", "stakeholder-management", "precision"], ["demanding", "decisive"]),
    ("Dwight S.", 9, "immediate",
     "Assistant to the regional backend engineer.",
     ["sales", "negotiation", "security", "loyalty"], ["intense", "loyal"]),
]

JOBS = [
    # title, min_experience, tagline, required skills, culture keywords
    ("Backend Detective", 3,
     "We have a bug. We have no leads. We have you.",
     ["deduction", "pattern-recognition", "forensics"], ["analytical", "autonomous"]),
    ("Rapid Prototyping Engineer", 2,
     "Ship first, document never (kidding - please document).",
     ["rapid-prototyping", "systems-design"], ["innovative", "fast-paced"]),
    ("Developer Relations Lead", 2,
     "Explain complex things to confused humans, cheerfully.",
     ["public-speaking", "research"], ["energetic", "curious"]),
    ("Engineering Manager, Chaos Team", 5,
     "Herd cats. The cats are senior engineers.",
     ["team-building", "stakeholder-management", "leadership"], ["empathetic", "organized"]),
    ("Incident Commander", 4,
     "3am page. You're the one who picks up.",
     ["crisis-management", "strategy", "negotiation"], ["decisive", "calm-under-pressure"]),
    ("Sales Engineer", 3,
     "Sell the vision, then go build it.",
     ["sales", "public-speaking", "negotiation"], ["enthusiastic", "persistent"]),
]


def seed():
    conn = db.get_conn()

    # Clear old data so the script can be re-run safely (children first)
    for table in ["matches", "candidate_skills", "candidate_traits", "job_skills",
                  "job_culture", "candidates", "jobs", "skills"]:
        conn.execute(f"DELETE FROM {table}")

    # Candidates
    for name, exp, avail, quirk, skills, traits in CANDIDATES:
        cur = conn.execute(
            "INSERT INTO candidates (name, experience_years, availability, quirk) "
            "VALUES (?, ?, ?, ?)",
            (name, exp, avail, quirk),
        )
        cand_id = cur.lastrowid
        for skill in skills:
            conn.execute("INSERT OR IGNORE INTO skills (name) VALUES (?)", (skill,))
            conn.execute(
                "INSERT INTO candidate_skills (candidate_id, skill_id) "
                "SELECT ?, id FROM skills WHERE name = ?",
                (cand_id, skill),
            )
        for trait in traits:
            conn.execute(
                "INSERT INTO candidate_traits (candidate_id, trait) VALUES (?, ?)",
                (cand_id, trait),
            )

    # Jobs
    for title, min_exp, tagline, skills, culture in JOBS:
        cur = conn.execute(
            "INSERT INTO jobs (title, min_experience, tagline) VALUES (?, ?, ?)",
            (title, min_exp, tagline),
        )
        job_id = cur.lastrowid
        for skill in skills:
            conn.execute("INSERT OR IGNORE INTO skills (name) VALUES (?)", (skill,))
            conn.execute(
                "INSERT INTO job_skills (job_id, skill_id) "
                "SELECT ?, id FROM skills WHERE name = ?",
                (job_id, skill),
            )
        for keyword in culture:
            conn.execute(
                "INSERT INTO job_culture (job_id, keyword) VALUES (?, ?)",
                (job_id, keyword),
            )

    conn.commit()
    conn.close()

    matching.refresh_matches()
    print("Seeded: 15 candidates, 6 jobs. Matches computed.")


if __name__ == "__main__":
    seed()