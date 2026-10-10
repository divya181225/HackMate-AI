
"""Module 5: Simple neural-style problem classifier."""

import re

TRAINING_DATA = {
    "AI / Machine Learning": [
        "predict disease using machine learning",
        "train an artificial intelligence model",
        "use neural networks for image recognition",
        "build a chatbot using natural language processing",
    ],
    "Web Development": [
        "build a website for online shopping",
        "create a web application using html css javascript",
        "develop a student portal",
        "design a frontend and backend system",
    ],
    "Data Science": [
        "analyze data and visualize trends",
        "predict sales using historical data",
        "clean datasets and create reports",
        "study statistics and data patterns",
    ],
    "Cybersecurity": [
        "detect cyber attacks and security threats",
        "protect networks from hackers",
        "identify phishing and malicious activity",
        "build a secure authentication system",
    ],
    "Internet of Things": [
        "connect sensors to monitor devices",
        "build a smart home using iot",
        "monitor temperature using embedded systems",
        "create a sensor based automation system",
    ],
}


def tokenize(text):
    return re.findall(r"[a-z0-9]+", text.lower())


def classify_problem(problem):
    """Classify text using a trained multiclass perceptron."""
    if not problem or len(tokenize(problem)) < 3:
        return {
            "category": "More details needed",
            "matched_words": [],
        }

    examples = []
    for category, statements in TRAINING_DATA.items():
        for statement in statements:
            examples.append((tokenize(statement), category))

    vocabulary = sorted({
        word
        for words, _ in examples
        for word in words
    })

    categories = list(TRAINING_DATA)
    weights = {
        category: [0.0] * len(vocabulary)
        for category in categories
    }
    word_index = {word: i for i, word in enumerate(vocabulary)}

    # Train a small multiclass perceptron on built-in examples.
    for _ in range(15):
        for words, correct in examples:
            features = set(words)

            scores = {}
            for category in categories:
                scores[category] = sum(
                    weights[category][word_index[word]]
                    for word in features
                    if word in word_index
                )

            predicted = max(categories, key=lambda c: scores[c])

            if predicted != correct:
                for word in features:
                    if word in word_index:
                        index = word_index[word]
                        weights[correct][index] += 1.0
                        weights[predicted][index] -= 1.0

    input_words = set(tokenize(problem))
    scores = {}

    for category in categories:
        scores[category] = sum(
            weights[category][word_index[word]]
            for word in input_words
            if word in word_index
        )

    best = max(categories, key=lambda c: scores[c])
    matched = sorted(input_words.intersection(vocabulary))

    if not matched or scores[best] <= 0:
        best = "More details needed"

    return {
        "category": best,
        "matched_words": matched,
    }
