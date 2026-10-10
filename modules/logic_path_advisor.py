
"""Rule-based Hackathon Learning Path Advisor for AISC Module 3."""

import re

TOPIC_KEYWORDS = {
    "Artificial Intelligence": [
        "artificial intelligence", " AI ", "generative ai",
        "large language model", "llm", "natural language processing",
        "deep learning",
    ],
    "Machine Learning": [
        "machine learning", " ML ", "model training",
        "prediction", "classification", "regression",
        "scikit-learn",
    ],
    "Data Science": [
        "data science", "data analysis", "data analytics",
        "data cleaning", "visualization", "statistics",
        "pandas", "numpy",
    ],
    "Python": ["python", "pandas", "numpy", "scikit-learn"],
    "Web Development": [
        "web development", "html", "css", "javascript",
        "frontend", "front-end", "backend", "back-end",
        "website", "web application",
    ],
    "Cloud Computing": [
        "cloud computing", "aws", "azure",
        "cloud deployment", "google cloud",
    ],
    "Cybersecurity": [
        "cybersecurity", "cyber security", "network security",
        "ethical hacking", "penetration testing",
    ],
    "Internet of Things": [
        "internet of things", "iot", "embedded systems",
        "sensors",
    ],
    "Blockchain": ["blockchain", "smart contracts", "web3"],
    "UI/UX Design": [
        "ui/ux", "user interface", "user experience",
        "wireframe", "prototyping",
    ],
}

GOAL_RULES = {
    "Machine Learning": {"Machine Learning"},
    "Data Analysis": {"Data Science"},
    "Build websites": {"Web Development"},
    "Learn cloud": {"Cloud Computing"},
    "Explore AI": {"Artificial Intelligence", "Machine Learning"},
    "Explore cybersecurity": {"Cybersecurity"},
    "Explore IoT": {"Internet of Things"},
    "Explore blockchain": {"Blockchain"},
    "Explore UI/UX": {"UI/UX Design"},
}


"""Simple Hackathon Learning Advisor."""

TOPICS = {
    "AI / Machine Learning": [
        "ai", "artificial intelligence", "machine learning",
        "ml", "model training", "generative ai",
    ],
    "Data Science": [
        "data science", "data analysis", "data analytics",
        "pandas", "numpy", "visualization",
    ],
    "Web Development": [
        "web", "website", "html", "css", "javascript",
        "frontend", "backend",
    ],
    "Cloud Computing": ["cloud", "aws", "azure", "deployment"],
    "Cybersecurity": ["cybersecurity", "cyber security", "security"],
}


def compare_learning_paths(event_a, event_b, goal):
    results = []

    for event in (event_a, event_b):
        title = str(event.get("name", "Hackathon"))
        description = str(event.get("description", ""))
        skills = event.get("skills", [])
        text = (title + " " + description + " " +
                " ".join(str(s) for s in skills)).lower()

        found = []
        for topic, keywords in TOPICS.items():
            for word in keywords:
                if word == "ai" or word == "ml" or word == "web":
                    matched = any(
                        word in token
                        for token in text.replace("/", " ").split()
                    )
                else:
                    matched = word in text

                if matched:
                    found.append(topic)
                    break

        goal_topics = {
            "Machine Learning": ["AI / Machine Learning"],
            "Data Analysis": ["Data Science"],
            "Build websites": ["Web Development"],
            "Learn cloud": ["Cloud Computing"],
            "Explore AI": ["AI / Machine Learning"],
        }.get(goal, [])

        matched_goal = any(topic in found for topic in goal_topics)

        results.append({
            "event_name": title,
            "topics_found": found,
            "learning_outcomes": [
                "Explore " + topic + " concepts through the challenge."
                for topic in found
            ] or [
                "The listing does not contain enough technical details yet."
            ],
            "evidence_level": (
                "Keywords found in title or available listing details"
                if found else "Insufficient technical details"
            ),
            "forward_chaining": {
                "matched": matched_goal,
                "rule": "IF relevant topic is mentioned, THEN it may support your goal."
            },
            "backward_chaining": {
                "proved": matched_goal,
                "explanation": (
                    "A relevant topic matches your goal."
                    if matched_goal else
                    "The available text does not confirm your goal."
                ),
            },
        })

    return results
