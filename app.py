

import streamlit as st
import requests
import re 
from modules.team_matcher import match_team_skills
from modules.neural_predictor import classify_problem
from modules.logic_path_advisor import compare_learning_paths
from modules.search_ranker import rank_search_results
from modules.fuzzy_analyzer import (
    triangle_membership,
    analyze_difficulty,
    suggest_difficulty_factors,
)
from modules.search_ranker import rank_search_results
from datetime import datetime, timezone


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_brabble_listings(api_key):
    """Fetch and cache current hackathon listings from Brabble."""
    response = requests.get(
        "https://brabble.ai/api/listings",
        headers={"Authorization": f"Bearer {api_key}"},
        params={"hub": "hackathons", "limit": 200},
        timeout=20,
    )
    response.raise_for_status()
    data = response.json()
    return data.get("listings", []), data.get("total", 0), data.get("refreshedAt")



def convert_brabble_event(item):
    """Convert a Brabble listing while preserving available source details."""

    fee_raw = item.get("fee")
    fee_text = str(fee_raw).strip() if fee_raw is not None else ""
    fee_normalized = fee_text.lower().replace(",", "").replace("₹", "")

    if fee_normalized in {
        "free", "no fee", "rs 0", "rs. 0",
        "inr 0", "0", "0.0", "0.00"
    }:
        fee = 0
    else:
        fee_match = re.fullmatch(
            r"(?:rs\.?\s*|inr\s*)?"
            r"(\d+(?:\.\d{1,2})?)"
            r"\s*(?:inr|rs\.?)?",
            fee_normalized,
        )
        fee = float(fee_match.group(1)) if fee_match else None

    mode = str(item.get("mode") or "").strip().upper()
    event_format = {
        "ONLINE": "Online",
        "OFFLINE": "Offline",
        "HYBRID": "Hybrid",
    }.get(mode, "Unknown")

    def clean_text(value):
        if isinstance(value, str):
            return value.strip()
        if isinstance(value, list):
            return ", ".join(
                str(x).strip() for x in value if x
            )
        if isinstance(value, dict):
            return "; ".join(
                f"{k}: {v}" for k, v in value.items() if v
            )
        return ""

    def first_available(*values):
        for value in values:
            text = clean_text(value)
            if text and text.lower() not in {"none", "null", "n/a"}:
                return text
        return ""

    description = first_available(
        item.get("description"),
        item.get("summary"),
        item.get("details"),
        item.get("problemStatement"),
        item.get("problem_statement"),
    )

    raw_skills = (
        item.get("skills")
        or item.get("technologies")
        or item.get("techStack")
        or item.get("tags")
        or []
    )
    skills_text = clean_text(raw_skills)
    skills = (
        [s.strip() for s in re.split(r"[,;|]", skills_text) if s.strip()]
        if skills_text else []
    )

    eligibility = first_available(item.get("eligibility")) or "Not provided"
    organizer = first_available(
        item.get("organiser"), item.get("organizer")
    ) or "Not provided"
    platform = first_available(item.get("platform")) or "Not provided"
    deadline = item.get("deadline") or "Not provided"

    description_parts = [
        f"Organizer: {organizer}",
        f"Platform: {platform}",
        f"Eligibility: {eligibility}",
        f"Event details: {description or 'Not provided'}",
        f"Deadline: {deadline}",
    ]

    # Preserve any additional source fields that may help the advisor.
    extra_details = []
    for key in (
        "problemStatement", "problem_statement", "requirements",
        "technologies", "techStack", "prizes", "deliverables",
        "themes", "tracks", "rules"
    ):
        value = clean_text(item.get(key))
        if value and value not in extra_details:
            extra_details.append(f"{key}: {value}")

    description_parts.extend(extra_details)

    return {
        "name": item.get("title") or "Untitled hackathon",
        "category": item.get("type") or "Hackathon",
        "skills": skills,
        "fee": fee,
        "fee_text": fee_text or "Not provided",
        "format": event_format,
        "days": None,
        "complexity": None,
        "prerequisites": first_available(
            item.get("prerequisites"), item.get("requirements")
        ) or None,
        "deliverables": first_available(
            item.get("deliverables"), item.get("submissionRequirements")
        ) or None,
        "time_pressure": None,
        "description": " · ".join(description_parts),
        "url": item.get("url") or item.get("shareUrl") or "https://brabble.ai/",
        "platform": platform,
        "deadline": deadline,
        "attribution": item.get("shareUrl") or "https://brabble.ai/",
    }
   

st.set_page_config(
    page_title="HackMate AI",
    page_icon="🎯",
    layout="wide"
)


# ---------------- LIVE HACKATHON DATA ----------------

try:
    api_key = st.secrets["BRABBLE_API_KEY"]
    raw_listings, total_listings, data_refreshed = fetch_brabble_listings(api_key)

    HACKATHONS = [
        convert_brabble_event(item)
        for item in raw_listings
        if item.get("title") and (item.get("url") or item.get("shareUrl"))
    ]

    st.caption(
        f"Data source: Brabble · {len(HACKATHONS)} listings loaded "
        f"from {total_listings} available · "
        f"Last source refresh: {data_refreshed or 'Not provided'}"
    )

except KeyError:
    HACKATHONS = []
    st.error(
        "Brabble API key is not configured. Add BRABBLE_API_KEY "
        "to .streamlit/secrets.toml."
    )

except requests.RequestException:
    HACKATHONS = []
    st.error(
        "Could not retrieve hackathons from Brabble. "
        "Please try again later."
    )

except (ValueError, TypeError):
    HACKATHONS = []
    st.error("Brabble returned data that could not be processed.")

# ---------------- CUSTOM DESIGN ----------------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #f8f5ff, #f0f4ff, #fff7fb);
    color: #24213a;
}

[data-testid="stAppViewContainer"] {
    color: #24213a;
}

[data-testid="stHeader"] {
    background: rgba(248, 245, 255, 0.95);
}

h1, h2, h3, h4 {
    color: #30204d !important;
}

.stApp p,
.stApp label,
.stApp [data-testid="stMarkdownContainer"],
.stApp [data-testid="stCaptionContainer"] {
    color: #352d48;
}

.hero {
    padding: 32px;
    border-radius: 22px;
    background: linear-gradient(115deg, #6541a5, #9760c8, #d47db8);
    color: #ffffff;
    margin-bottom: 22px;
    box-shadow: 0 8px 24px rgba(80, 45, 120, 0.16);
}

.hero h1, .hero p {
    color: #ffffff !important;
}

.event-card {
    background: #ffffff;
    color: #24213a;
    padding: 20px;
    border: 1px solid #e4d8f4;
    border-radius: 18px;
    margin-bottom: 12px;
}

.event-card h3,
.event-card p {
    color: #30204d !important;
}

[data-testid="stMetric"] {
    background: #ffffff;
    border: 1px solid #e4d8f4;
    border-radius: 16px;
    padding: 18px;
    box-shadow: 0 4px 14px rgba(60, 40, 90, 0.05);
}

[data-testid="stMetricLabel"] {
    color: #655477 !important;
}

[data-testid="stMetricValue"] {
    color: #56328c !important;
}

[data-testid="stVerticalBlockBorderWrapper"] {
    border-color: #e3d6f2 !important;
    border-radius: 16px !important;
}

[data-testid="stSidebar"] {
    background: #f0e9fb;
}

[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    color: #35204f !important;
}

[data-testid="stSidebar"] p,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] [data-testid="stCaptionContainer"] {
    color: #413452 !important;
}

.stTextInput input,
.stSelectbox div[data-baseweb="select"],
.stMultiSelect div[data-baseweb="select"] {
    border-radius: 10px;
}

.stButton button,
.stLinkButton a {
    border-radius: 10px;
}

[data-testid="stAlert"] {
    border-radius: 12px;
}

footer {
    visibility: hidden;
}
</style>
""", unsafe_allow_html=True)


# ---------------- SIDEBAR ----------------
st.sidebar.title("🎯 HackMate AI")
st.sidebar.caption("Your hackathon discovery companion")
st.sidebar.divider()

st.sidebar.subheader("Your student profile")

all_skills = [
    "Python", "Machine Learning", "SQL", "Data Analysis",
    "Cloud", "APIs", "UI Design", "Web Development"
]

student_skills = st.sidebar.multiselect(
    "What skills do you have?",
    all_skills,
    default=["Python"]
)

interests = st.sidebar.multiselect(
    "What interests you?",
    ["AI / ML", "Data Science", "Cloud / AI", "App Development"],
    default=["AI / ML"]
)



fee_filter = st.sidebar.selectbox(
    "Participation fee",
    ["Any", "Free", "Paid"],
    index=0,
)





preferred_format = st.sidebar.selectbox(
    "Preferred format",
    ["Any", "Online", "Offline"]
)

experience = st.sidebar.selectbox(
    "Experience level",
    ["Beginner", "Intermediate", "Advanced"]
)

# ---------------- MAIN HEADER ----------------
st.markdown("""
<div class="hero">
    <h1>Find your next big idea. ✨</h1>
    <p>Discover hackathons that match your skills, interests and goals.</p>
    <p>Understand difficulty, discover skill gaps and choose your next challenge.</p>
</div>
""", unsafe_allow_html=True)

st.info(
    "LIVE LISTINGS: Data fetched from Brabble. "
    "Listings and deadlines may change; confirm eligibility, fees "
    "and registration details on the organizer's website."
)


# ---------------- DASHBOARD ----------------
c1, c2, c3 = st.columns(3)
c1.metric("Live listings loaded", len(HACKATHONS))
c2.metric("Selected skills", len(student_skills))
c3.metric("Selected interests", len(interests))

st.divider()
st.subheader("🔎 Smart Hackathon Finder")

search_text = st.text_input(
    "Search by name, topic or skill",
    placeholder="Try Python, AI, data science..."
)

def event_matches_interest(event, selected_interests):
    if not selected_interests:
        return True

    text = (
        event.get("name", "") + " "
        + event.get("category", "") + " "
        + event.get("description", "")
    ).lower()

    keywords = {
        "AI / ML": ["ai", "artificial intelligence", "machine learning", "ml", "deep learning"],
        "Data Science": ["data science", "data analysis", "analytics", "data"],
        "Cloud / AI": ["cloud", "api", "infrastructure", "devops"],
        "App Development": ["app development", "application", "mobile app", "ui design", "web development"]
    }

    return any(
        keyword in text
        for interest in selected_interests
        for keyword in keywords.get(interest, [interest.lower()])
    )

def estimate_experience_level(event):
    """Estimate experience level from available listing text."""
    text = " ".join([
        str(event.get("name") or ""),
        str(event.get("category") or ""),
        str(event.get("description") or ""),
        str(event.get("fee_text") or ""),
    ]).lower()

    advanced_keywords = [
        "advanced", "expert", "professional",
        "senior-level", "complex challenge"
    ]
    beginner_keywords = [
        "beginner", "beginners", "introductory",
        "no experience", "novice", "school students"
    ]

    if any(word in text for word in advanced_keywords):
        return "Advanced"

    if any(word in text for word in beginner_keywords):
        return "Beginner"

    # The source does not provide enough information.
    return "Intermediate"


results = []


for event in HACKATHONS:
    fee = event.get("fee")




    # Filter hackathons using the source's fee label.
    fee_text = str(event.get("fee_text") or "").strip().lower()
    fee_value = event.get("fee")

    is_free = (
        fee_text in {"free", "no fee"}
        or fee_value == 0
    )

    is_paid = (
        "paid" in fee_text
        or (
            isinstance(fee_value, (int, float))
            and not isinstance(fee_value, bool)
            and fee_value > 0
        )
    )

    if fee_filter == "Free" and not is_free:
        continue
    elif fee_filter == "Paid" and not is_paid:
        continue

    estimated_level = estimate_experience_level(event)

    if experience != estimated_level:
        continue




    if (
        preferred_format != "Any"
        and event.get("format") != preferred_format
    ):
        continue

    if not event_matches_interest(event, interests):
        continue

    searchable = (
        event.get("name", "") + " "
        + event.get("category", "") + " "
        + " ".join(event.get("skills", [])) + " "
        + event.get("description", "")
    ).lower()

    if search_text and search_text.lower() not in searchable:
        continue
    skills = event.get("skills", [])
    matched = set(student_skills).intersection(skills)

    # Do not calculate a skill-match percentage when the source
    # does not provide required skills.
    match_score = (
        round(100 * len(matched) / len(skills))
        if skills else None
    )

    factors = [
        event.get("complexity"),
        event.get("prerequisites"),
        event.get("deliverables"),
        event.get("time_pressure")
    ]


    if all(isinstance(value, (int, float)) for value in factors):
        outcome = analyze_difficulty(event)
        score = outcome["score"]
        level = outcome["level"]
        reasons = outcome["reasons"]
    else:
        score, level = None, "Not yet assessed"
        reasons = ["Difficulty factors not provided by the source"]


    results.append({
        "event": event,
        "matched": matched,
        "match_score": match_score,
        "difficulty": level,
        "score": score,
        "reasons": reasons
    })

if search_text:
    ranked_events = rank_search_results(
        [item["event"] for item in results],
        search_text,
    )

    rank_order = {
        id(event): position
        for position, event in enumerate(ranked_events)
    }

    results = [
        item for item in results
        if id(item["event"]) in rank_order
    ]

    results.sort(
        key=lambda item: rank_order[id(item["event"])]
    )
else:
    results.sort(
        key=lambda item: (
            item["match_score"] is not None,
            item["match_score"] if item["match_score"] is not None else -1
        ),
        reverse=True
    )

if not results:
    st.warning(
        "No live listings match your current filters. "
        "Try changing your interests, budget, format or search."
    )

for item in results:
    event = item["event"]

    with st.container(border=True):
        left, right = st.columns([3, 1])

        with left:
            st.subheader(event["name"])
            st.write(event.get("description") or "No additional description provided.")

            fee_label = (
                f"₹{fee}"
                if (fee := event.get("fee")) is not None
                else event.get("fee_text", "Fee not confirmed")
            )

            st.caption(
                f"{event.get('category', 'Hackathon')} · "
                f"{event.get('format', 'Format not provided')} · "
                f"Fee: {fee_label}"
            )

            st.write(
                "**Required skills:** "
                + (
                    ", ".join(event["skills"])
                    if event.get("skills")
                    else "Not provided by the source"
                )
            )

            if item["match_score"] is None:
                st.write("**Your matching skills:** Cannot assess — required skills are unavailable.")
            else:
                st.write(
                    "**Your matching skills:** "
                    + (
                        ", ".join(sorted(item["matched"]))
                        if item["matched"]
                        else "No matching skills selected"
                    )
                )

            st.write("**Difficulty factors:** " + "; ".join(item["reasons"]))

            if event.get("deadline"):
                st.caption(f"Deadline: {event['deadline']}")

            if event.get("platform"):
                st.caption(f"Platform: {event['platform']}")

        with right:
            if item["match_score"] is not None:
                st.metric("Skill match", f"{item['match_score']}%")
            else:
                st.metric("Skill match", "Not assessed")

            st.metric("Estimated difficulty", item["difficulty"])

            if item["score"] is not None:
                st.caption(f"Factor score: {item['score']:.1f}/5")

            st.link_button(
                "View event",
                event["url"]
            )

        st.caption(
            "Listing source: Brabble · "
            "Confirm event details and eligibility on the organizer's page."
        )

        if event.get("attribution"):
            st.markdown(
                f"[View source listing]({event['attribution']})"
            )



# ---------------- SKILL-GAP ADVISOR ----------------
st.divider()
st.subheader("🧭 Your Skill-Gap Advisor")

if results:
    chosen_name = st.selectbox(
        "Choose a hackathon to review",
        [item["event"]["name"] for item in results]
    )

    chosen = next(
        item for item in results
        if item["event"]["name"] == chosen_name
    )
    selected_event = chosen["event"]

    event_skills = selected_event.get("skills", [])

    if not event_skills:
        st.info(
            "Required skills are not provided by the listing source. "
            "Open the event page to check its requirements."
        )
    else:
        missing = sorted(set(event_skills) - set(student_skills))

        if missing:
            st.write("Skills you could learn before participating:")
            for skill in missing:
                st.write(f"- **{skill}**")
        else:
            st.success(
                "Your selected skills cover all skills listed for this event."
            )

    # -------- HACKATHON LEARNING PATH ADVISOR --------
    st.divider()
    st.subheader("🧭 Hackathon Learning Path Advisor")
    st.write(
        "Compare two hackathons and discover which listed topics "
        "match your learning goal using logical reasoning."
    )

    if len(results) >= 2:
        event_names = list(dict.fromkeys(
            item["event"]["name"] for item in results
        ))
        event_lookup = {
            item["event"]["name"]: item["event"]
            for item in results
        }

        col1, col2 = st.columns(2)

        with col1:
            event_a_name = st.selectbox(
                "First hackathon",
                event_names,
                key="path_event_a",
            )

        with col2:
            event_b_options = [
                name for name in event_names if name != event_a_name
            ]
            event_b_name = st.selectbox(
                "Second hackathon",
                event_b_options,
                key="path_event_b",
            )

        goal = st.selectbox(
            "What do you want to learn?",
            [
                "Machine Learning",
                "Data Analysis",
                "Build websites",
                "Learn cloud",
                "Explore AI",
            ],
            key="path_learning_goal",
        )

        
        if st.button("Compare learning paths", key="run_path_comparison"):
            comparisons = compare_learning_paths(
                event_lookup[event_a_name],
                event_lookup[event_b_name],
                goal,
            )

            for comparison in comparisons:
                st.markdown(f"### {comparison['event_name']}")

                st.caption(
                    "Evidence: " + comparison["evidence_level"]
                )

                topics = comparison["topics_found"]
                st.write(
                    "**Topics found:** " +
                    (", ".join(topics) if topics else
                     "No technical topics identified in available details.")
                )

                st.write("**What you might learn:**")
                for outcome in comparison["learning_outcomes"]:
                    st.write("- " + outcome)

                forward = comparison["forward_chaining"]
                backward = comparison["backward_chaining"]

                if forward["matched"]:
                    st.success("Your learning goal matches a listed topic.")
                else:
                    st.warning(
                        "The available text does not confirm a direct match."
                    )

                st.caption("Forward chaining — " + forward["rule"])
                st.write("**Backward chaining:** " + backward["explanation"])

            st.info(
                "These are topic-based learning possibilities, not guaranteed "
                "outcomes. The current data source may omit full problem "
                "statements, technologies, and submission requirements."
            )

# -------- NEURAL NETWORK PROBLEM CLASSIFIER --------

# -------- TEAM SKILL-COMPLEMENT MATCHER --------

st.divider()
st.subheader("👥 Hackathon Team Skill-Complement Matcher")
st.write("Find which required skills your team still needs.")

required_text = st.text_input(
    "Required skills (comma-separated)",
    placeholder="Python, Machine Learning, UI/UX",
    key="team_required_skills",
)

member1_text = st.text_input(
    "Member 1 skills",
    placeholder="Python, SQL",
    key="team_member1_skills",
)

member2_text = st.text_input(
    "Member 2 skills",
    placeholder="Web Development, UI/UX",
    key="team_member2_skills",
)

if st.button("Check Team Skills", key="check_team_skills"):
    required = [s.strip() for s in required_text.split(",") if s.strip()]

    team = {
        "Member 1": [s.strip() for s in member1_text.split(",") if s.strip()],
        "Member 2": [s.strip() for s in member2_text.split(",") if s.strip()],
    }

    if not required:
        st.warning("Enter the hackathon's required skills.")
    else:
        result = match_team_skills(required, team)

        st.write("**Skills already covered:**")
        st.write(", ".join(result["available_skills"]) or "None")

        st.write("**Skills missing from your team:**")
        st.write(", ".join(result["missing_skills"]) or "None")

        st.info(result["recommendation"])

st.divider()
st.subheader("🧠 Neural Network Problem Classifier")
st.write(
    "Paste a hackathon problem statement to predict its technical category."
)

problem_text = st.text_area(
    "Hackathon problem statement",
    placeholder="Example: Build a system that detects diseases from medical images...",
    key="neural_problem_input",
)

if st.button("Predict Category", key="neural_predict_button"):
    if len(problem_text.strip()) < 10:
        st.warning("Please enter a longer problem statement.")
    else:
        prediction = classify_problem(problem_text)
        st.success("Predicted category: " + prediction["category"])

        if prediction["matched_words"]:
            st.write(
                "**Recognized words:** "
                + ", ".join(prediction["matched_words"])
            )

        st.caption(
            "Educational prototype: predictions depend on its small "
            "training examples and may be incorrect."
        )



# -------- FUZZY DIFFICULTY ANALYZER --------
st.divider()
st.subheader("🌫️ Fuzzy Difficulty Analyzer")
st.write(f"**Selected event:** {selected_event['name']}")
st.caption(
    "Suggestions use keywords from the available listing text. "
    "They are rule-based estimates, not predictions from a trained AI model."
)

suggestions = suggest_difficulty_factors(selected_event)

factor_labels = {
    "complexity": "Technical complexity",
    "prerequisites": "Prerequisites required",
    "deliverables": "Expected deliverables",
    "time_pressure": "Time pressure",
}

st.write("**Automatic suggestions and evidence**")

chosen_values = {}
for key, label in factor_labels.items():
    value, evidence = suggestions[key]
    chosen_values[key] = value

    if value is None:
        st.warning(f"**{label}:** Unknown — {evidence}")
    else:
        st.write(f"**{label}:** {value}/5 — {evidence}")

st.caption(
    "Scale: 1 = lower difficulty; 5 = higher difficulty. "
    "Verify details using the event organizer's page."
)

with st.form("confirm_fuzzy_factors"):
    st.write("**Review and confirm factor ratings**")
    st.caption(
        "Review unknown factors using the organizer's information. "
        "The app will not calculate a final result until you confirm "
        "that you reviewed each unknown factor."
    )

    factor_inputs = {}
    factor_confirmations = {}

    for key, label in factor_labels.items():
        suggested_value = chosen_values[key]

        if suggested_value is None:
            st.warning(
                f"{label}: No reliable automatic suggestion was found."
            )
            factor_confirmations[key] = st.checkbox(
                f"I reviewed the event details for {label.lower()}",
                key=f"confirm_{key}",
            )
            default_rating = 3
        else:
            default_rating = suggested_value

        factor_inputs[key] = st.select_slider(
            label,
            options=[1, 2, 3, 4, 5],
            value=default_rating,
            key=f"rating_{key}",
            help=(
                "No reliable suggestion found. Review event details and "
                "choose a rating."
                if suggested_value is None
                else "Automatic suggestion; review or adjust as needed."
            ),
        )

    confirmed = st.form_submit_button(
        "Calculate Fuzzy Difficulty",
        use_container_width=True,
    )

if confirmed:
    unconfirmed = [
        factor_labels[key]
        for key in factor_labels
        if chosen_values[key] is None
        and not factor_confirmations.get(key, False)
    ]

    if unconfirmed:
        st.error(
            "Review and confirm these unknown factors first: "
            + ", ".join(unconfirmed)
        )
    else:
        assessed_event = dict(selected_event)
        assessed_event.update(factor_inputs)

        outcome = analyze_difficulty(assessed_event)

        if outcome["score"] is None:
            st.warning(
                "A difficulty result could not be calculated. "
                "Please check that all four ratings are valid."
            )
        else:
            st.success(
                f"Estimated difficulty: {outcome['level']}"
            )
            st.metric(
                "Average factor score",
                f"{outcome['score']:.2f} / 5",
            )

            st.write("**Fuzzy membership values**")
            st.caption(
                "These values indicate membership in each fuzzy "
                "category; they are not probabilities."
            )

            for level, membership in outcome["memberships"].items():
                st.write(f"**{level}:** {membership * 100:.1f}%")
                st.progress(membership)

            if outcome["reasons"]:
                st.write("**Reasons**")
                for reason in outcome["reasons"]:
                    st.write(f"- {reason}")

            st.info(
                "This is an estimate based on the displayed factor "
                "ratings, not an official difficulty rating from "
                "the event organizer."
            )


st.divider()
st.caption(
"HackMate AI · Student project prototype. "
"Listings provided by Brabble; confirm details with the organizer. "
"Difficulty scores are guidance only, not guarantees."
)
