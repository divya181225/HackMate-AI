import re


def rank_search_results(events, query):
    """Rank event listings by relevance to a search query."""
    query = query.strip().lower()

    if not query:
        return list(events)

    query_terms = set(re.findall(r"\w+", query))
    ranked = []

    for event in events:
        title = str(event.get("name", "")).lower()
        category = str(event.get("category", "")).lower()
        skills = " ".join(event.get("skills") or []).lower()
        description = str(event.get("description", "")).lower()

        score = 0

        if query == title:
            score += 10
        elif query in title:
            score += 6

        if query in category:
            score += 4
        if query in skills:
            score += 4
        if query in description:
            score += 2

        searchable = f"{title} {category} {skills} {description}"
        score += sum(1 for term in query_terms if term in searchable)

        if score > 0:
            ranked.append((score, event))

    ranked.sort(key=lambda item: item[0], reverse=True)
    return [event for _, event in ranked]
