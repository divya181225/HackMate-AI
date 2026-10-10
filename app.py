
import streamlit as st

st.set_page_config(
    page_title="HackMate AI",
    page_icon="🎯",
    layout="wide"
)

# ---------------- SAMPLE HACKATHON DATA ----------------
# These are demonstration records, NOT verified live events.
HACKATHONS = [
    {
        "name": "AI Innovation Challenge",
        "category": "AI / ML",
        "skills": ["Python", "Machine Learning"],
        "fee": 0,
        "format": "Online",
        "days": 3,
        "complexity": 2,
        "prerequisites": 2,
        "deliverables": 2,
        "time_pressure": 2,
        "description": "Build a prototype that explores an AI or ML problem.",
        "url": "https://devpost.com/hackathons"
    },
    {
        "name": "Data Science Sprint",
        "category": "Data Science",
        "skills": ["Python", "SQL", "Data Analysis"],
        "fee": 0,
        "format": "Online",
        "days": 2,
        "complexity": 3,
        "prerequisites": 3,
        "deliverables": 3,
        "time_pressure": 4,
        "description": "Analyze data and present useful insights.",
        "url": "https://unstop.com/hackathons"
    },
    {
        "name": "Cloud and AI Buildathon",
        "category": "Cloud / AI",
        "skills": ["Python", "Cloud", "APIs"],
        "fee": 500,
        "format": "Offline",
        "days": 2,
        "complexity": 5,
        "prerequisites": 5,
        "deliverables": 4,
        "time_pressure": 5,
        "description": "Design a cloud-connected AI solution.",
        "url": "https://www.mlh.com/"
    },
    {
        "name": "Student App Design Jam",
        "category": "App Development",
        "skills": ["UI Design", "Python"],
        "fee": 0,
        "format": "Online",
        "days": 5,
        "complexity": 1,
        "prerequisites": 1,
        "deliverables": 2,
        "time_pressure": 1,
        "description": "Turn a student problem into a simple prototype.",
        "url": "https://devpost.com/hackathons"
    }
]

# ---------------- FUZZY LOGIC ----------------
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


def analyze_difficulty(event):
    factors = [
        event["complexity"],
        event["prerequisites"],
        event["deliverables"],
        event["time_pressure"]
    ]

    score = sum(factors) / len(factors)

    memberships = {
        "Beginner": triangle_membership(score, 1, 1, 3),
        "Moderate": triangle_membership(score, 2, 3.5, 5),
        "Hard": triangle_membership(score, 3, 5, 5)
    }

    level = max(memberships, key=memberships.get)

    reasons = []
    if event["complexity"] >= 4:
        reasons.append("High technical complexity")
    elif event["complexity"] <= 2:
        reasons.append("Lower technical complexity")

    if event["prerequisites"] >= 4:
        reasons.append("Advanced prerequisites")
    if event["deliverables"] >= 4:
        reasons.append("Demanding deliverables")
    if event["time_pressure"] >= 4:
        reasons.append("High time pressure")
    if not reasons:
        reasons.append("Requirements appear manageable")

    return score, level, reasons



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

max_fee = st.sidebar.slider(
    "Maximum participation fee (₹)",
    min_value=0,
    max_value=2000,
    value=500,
    step=100
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
    "DEMO MODE: The listings below are sample records for testing. "
    "They are not verified upcoming hackathons."
)

# ---------------- DASHBOARD ----------------
c1, c2, c3 = st.columns(3)
c1.metric("Sample listings", len(HACKATHONS))
c2.metric("Selected skills", len(student_skills))
c3.metric("Selected interests", len(interests))

st.divider()
st.subheader("🔎 Smart Hackathon Finder")

search_text = st.text_input(
    "Search by name, topic or skill",
    placeholder="Try Python, AI, data science..."
)

results = []

for event in HACKATHONS:
    if event["fee"] > max_fee:
        continue

    if preferred_format != "Any" and event["format"] != preferred_format:
        continue

    if interests and event["category"] not in interests:
        continue

    searchable = (
        event["name"] + " " + event["category"] + " "
        + " ".join(event["skills"]) + " " + event["description"]
    ).lower()

    if search_text and search_text.lower() not in searchable:
        continue

    matched = set(student_skills).intersection(event["skills"])
    match_score = round(
        100 * len(matched) / max(len(event["skills"]), 1)
    )

    score, level, reasons = analyze_difficulty(event)

    results.append({
        "event": event,
        "matched": matched,
        "match_score": match_score,
        "difficulty": level,
        "score": score,
        "reasons": reasons
    })

results.sort(key=lambda item: item["match_score"], reverse=True)

if not results:
    st.warning(
        "No sample listings match your filters. "
        "Try changing your interests, budget or search."
    )

for item in results:
    event = item["event"]

    with st.container(border=True):
        left, right = st.columns([3, 1])

        with left:
            st.subheader(event["name"])
            st.write(event["description"])
            st.caption(
                f"{event['category']} · {event['format']} · "
                f"{event['days']} days · Fee: ₹{event['fee']}"
            )
            st.write("**Required skills:** " + ", ".join(event["skills"]))
            st.write(
                "**Your matching skills:** "
                + (
                    ", ".join(sorted(item["matched"]))
                    if item["matched"]
                    else "No matching skills selected"
                )
            )
            st.write("**Difficulty factors:** " + "; ".join(item["reasons"]))

        with right:
            st.metric("Skill match", f"{item['match_score']}%")
            st.metric("Estimated difficulty", item["difficulty"])
            st.caption(f"Factor score: {item['score']:.1f}/5")
            st.link_button("Explore listings", event["url"])

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

    missing = sorted(
        set(chosen["event"]["skills"]) - set(student_skills)
    )

    if missing:
        st.write("Skills you could learn before participating:")
        for skill in missing:
            st.write(f"- **{skill}**")
    else:
        st.success(
            "Your selected skills cover all skills listed for this demo event."
        )

st.divider()
st.caption(
    "HackMate AI · Student project prototype. "
    "Scores are guidance only, not guarantees."
)
