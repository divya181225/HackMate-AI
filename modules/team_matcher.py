
"""Module 6: Hackathon Team Skill-Complement Matcher."""

def match_team_skills(required_skills, team_members):
    """Find skills covered by the team and skills still missing."""

    required = {skill.strip().lower(): skill.strip()
                for skill in required_skills if skill.strip()}

    covered = set()
    for skills in team_members.values():
        covered.update(skill.strip().lower() for skill in skills if skill.strip())

    available = [name for key, name in required.items() if key in covered]
    missing = [name for key, name in required.items() if key not in covered]

    return {
        "available_skills": available,
        "missing_skills": missing,
        "recommendation": (
            "Look for a teammate with: " + ", ".join(missing)
            if missing else "Your team covers all listed required skills."
        ),
    }
