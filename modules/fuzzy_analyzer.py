def triangle_membership(value, left, peak, right):
    """Calculate triangular fuzzy membership between 0 and 1."""
    if value < left or value > right:
        return 0.0
    if value == peak:
        return 1.0
    if value < peak:
        if peak == left:
            return 1.0
        return (value - left) / (peak - left)
    if right == peak:
        return 1.0
    return (right - value) / (right - peak)


def suggest_difficulty_factors(event):
    """
    Suggest difficulty factors from available event text.
    These are rule-based estimates, not predictions from a trained AI model.
    Unclear factors remain None.
    """
    text = " ".join([
        str(event.get("name") or ""),
        str(event.get("category") or ""),
        str(event.get("description") or ""),
    ]).lower()

    suggestions = {}

    # Technical complexity
    if any(word in text for word in [
        "beginner-friendly", "beginner friendly", "introductory",
        "no-code", "no code", "basic workshop"
    ]):
        suggestions["complexity"] = (
            1, "Beginner-friendly or introductory wording found"
        )
    elif any(word in text for word in [
        "advanced", "distributed systems", "deep learning research",
        "complex algorithms", "production-grade"
    ]):
        suggestions["complexity"] = (
            5, "Advanced or technically demanding wording found"
        )
    elif any(word in text for word in [
        "build an app", "develop a platform", "machine learning",
        "artificial intelligence", "blockchain", "prototype"
    ]):
        suggestions["complexity"] = (
            3, "A development or technical project is mentioned"
        )
    else:
        suggestions["complexity"] = (
            None, "Not enough technical detail to estimate"
        )

    # Prerequisites
    if any(word in text for word in [
        "no experience required", "no prior experience",
        "open to beginners", "no prerequisites", "all skill levels"
    ]):
        suggestions["prerequisites"] = (
            1, "The listing indicates that prior experience is not required"
        )
    elif any(word in text for word in [
        "prior experience required", "advanced knowledge required",
        "strong programming skills", "experienced developers",
        "expert knowledge"
    ]):
        suggestions["prerequisites"] = (
            5, "The listing explicitly requests advanced skills or experience"
        )
    elif any(word in text for word in [
        "python", "machine learning", "programming experience",
        "technical skills required"
    ]):
        suggestions["prerequisites"] = (
            3, "Some technical skills are mentioned, but the required level is unclear"
        )
    else:
        suggestions["prerequisites"] = (
            None, "Required prior skills are not specified clearly"
        )

    # Deliverables
    if any(word in text for word in [
        "working prototype", "minimum viable product", "mvp",
        "deploy a complete application", "functional product"
    ]):
        suggestions["deliverables"] = (
            5, "A working product or complete application is expected"
        )
    elif any(word in text for word in [
        "prototype", "demo", "presentation", "pitch",
        "proof of concept", "project submission"
    ]):
        suggestions["deliverables"] = (
            3, "A prototype, demonstration, or presentation is mentioned"
        )
    else:
        suggestions["deliverables"] = (
            None, "Expected final deliverables are not clear"
        )

    # Time pressure
    if any(word in text for word in [
        "24-hour", "24 hour", "24 hours", "48-hour",
        "48 hour", "48 hours", "36-hour", "36 hours",
        "overnight hackathon"
    ]):
        suggestions["time_pressure"] = (
            5, "A short, intensive event duration is mentioned"
        )
    elif any(word in text for word in [
        "weekend hackathon", "two-day hackathon",
        "2-day hackathon", "72-hour", "72 hours"
    ]):
        suggestions["time_pressure"] = (
            4, "A time-limited hackathon duration is mentioned"
        )
    elif any(word in text for word in [
        "self-paced", "self paced", "one month",
        "four weeks", "4 weeks"
    ]):
        suggestions["time_pressure"] = (
            2, "The listing indicates a longer or flexible work period"
        )
    else:
        suggestions["time_pressure"] = (
            None, "A reliable working duration is not available"
        )

    return suggestions


def analyze_difficulty(event):
    """Calculate fuzzy difficulty only when all four factors are available."""
    factor_names = [
        "complexity",
        "prerequisites",
        "deliverables",
        "time_pressure",
    ]

    factors = [event.get(name) for name in factor_names]

    if any(value is None for value in factors):
        missing = [
            name.replace("_", " ").title()
            for name in factor_names
            if event.get(name) is None
        ]
        return {
            "level": "Insufficient information",
            "score": None,
            "memberships": {},
            "reasons": [],
            "missing": missing,
        }

    score = sum(factors) / len(factors)

    memberships = {
        "Beginner": triangle_membership(score, 1, 1, 3),
        "Moderate": triangle_membership(score, 2, 3.5, 5),
        "Hard": triangle_membership(score, 3, 5, 5),
    }

    level = max(memberships, key=memberships.get)

    reasons = []
    if event["complexity"] >= 4:
        reasons.append("High technical complexity")
    elif event["complexity"] <= 2:
        reasons.append("Lower technical complexity")

    if event["prerequisites"] >= 4:
        reasons.append("Advanced prerequisites")
    elif event["prerequisites"] <= 2:
        reasons.append("Limited prior knowledge indicated")

    if event["deliverables"] >= 4:
        reasons.append("A substantial final deliverable is expected")

    if event["time_pressure"] >= 4:
        reasons.append("High time pressure")

    return {
        "level": level,
        "score": score,
        "memberships": memberships,
        "reasons": reasons,
        "missing": [],
    }