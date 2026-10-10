

import streamlit as st
import requests
import re
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
    """Convert a Brabble listing to HackMate AI's existing event format."""

    fee_raw = item.get("fee")
    fee_text = str(fee_raw).strip() if fee_raw is not None else ""
    fee_normalized = fee_text.lower().replace(",", "")

    if fee_normalized in {
        "free", "no fee", "₹0", "rs 0", "rs. 0",
        "inr 0", "0", "0.0", "0.00"
    }:
        fee = 0
    else:
        fee_match = re.fullmatch(
            r"(?:₹\s*|rs\.?\s*|inr\s*)?"
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

    deadline = item.get("deadline")
    description_parts = [
        f"Organizer: {item.get('organiser') or 'Not provided'}",
        f"Platform: {item.get('platform') or 'Not provided'}",
        f"Eligibility: {', '.join(item.get('eligibility') or []) or 'Not provided'}",
        f"Deadline: {deadline or 'Not provided'}",
    ]

    return {
        "name": item.get("title") or "Untitled hackathon",
        "category": item.get("type") or "Hackathon",
        "skills": [],
        "fee": fee,
        "fee_text": fee_text or "Not provided",
        "format": event_format,
        "days": None,
        "complexity": None,
        "prerequisites": None,
        "deliverables": None,
        "time_pressure": None,
        "description": " · ".join(description_parts),
        "url": item.get("url") or item.get("shareUrl") or "https://brabble.ai/",
        "platform": item.get("platform") or "Not provided",
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
        score, level, reasons = analyze_difficulty(event)
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

    event_skills = chosen["event"].get("skills", [])

    if not event_skills:
        st.info(
            "Required skills are not provided by the listing source. "
            "Open the event page to check its requirements."
        )
    else:
        missing = sorted(
            set(event_skills) - set(student_skills)
        )

        if missing:
            st.write("Skills you could learn before participating:")
            for skill in missing:
                st.write(f"- **{skill}**")
        else:
            st.success(
                "Your selected skills cover all skills listed for this event."
            )



st.divider()
st.caption(
    "HackMate AI · Student project prototype. "
    "Listings provided by Brabble; confirm details with the organizer. "
    "Difficulty scores are guidance only, not guarantees."
)
