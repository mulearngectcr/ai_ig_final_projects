import streamlit as st

from hero_slideshow import render_hero_slideshow

st.set_page_config(
    page_title="RecipePilot",
    page_icon="🍳",
    layout="wide"
)

# Page styling: top padding + feature cards
st.markdown(
    """
    <style>
    .block-container { padding-top: 1.5rem; }

    /* Feature cards (containers created with key="fcard_...") */
    [class*="st-key-fcard_"] {
        border-radius: 18px !important;
        border: 1px solid rgba(242, 177, 52, 0.45) !important;
        padding: 0.4rem 0.6rem;
        position: relative;
        cursor: pointer;
        transition: transform .2s ease, box-shadow .2s ease, border-color .2s ease;
    }
    [class*="st-key-fcard_"]:hover {
        transform: translateY(-3px);
        border-color: #F2B134 !important;
        box-shadow: 0 10px 26px rgba(242, 177, 52, 0.22);
    }
    /* The page link covers the whole card, so the card itself is the button */
    /* Streamlit's element wrappers are positioned; make the card the reference box */
    [class*="st-key-fcard_"] [data-testid="stElementContainer"],
    [class*="st-key-fcard_"] .stElementContainer {
        position: static !important;
    }
    [class*="st-key-fcard_"] [data-testid="stPageLink"] {
        position: absolute !important;
        top: 0 !important;
        left: 0 !important;
        width: 100% !important;
        height: 100% !important;
        z-index: 2;
        margin: 0 !important;
    }
    [class*="st-key-fcard_"] [data-testid="stPageLink"] > div,
    [class*="st-key-fcard_"] [data-testid="stPageLink-NavLink"] {
        display: block !important;
        width: 100% !important;
        height: 100% !important;
        opacity: 0;               /* label stays in the DOM for screen readers */
        border-radius: 18px;
    }
    [class*="st-key-fcard_"]:has(a:focus-visible) {
        outline: 3px solid #F2B134;
        outline-offset: 2px;
    }
    .fcard-icon  { font-size: 2.1rem; line-height: 1.1; margin-bottom: .25rem; }
    .fcard-title { font-size: 1.15rem; font-weight: 600; margin-bottom: .15rem; }
    .fcard-desc  { font-size: .92rem; opacity: .75; min-height: 4.4em; margin-bottom: .4rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🍳 Welcome to RecipePilot")

st.subheader("Your AI-powered cooking companion")

# Hero slideshow (TheMealDB images, 5 s autoplay) below the heading
render_hero_slideshow()

st.divider()
st.header("Explore Features")

FEATURES = [
    ("pages/1_Recipe_Finder.py", "🔍", "Recipe Finder",
     "Search for recipes by name and explore their ingredients and cooking instructions."),
    ("pages/2_Recipe_Assistant.py", "🤖", "Recipe Assistant",
     "Ask cooking questions and get AI-powered answers."),
    ("pages/3_Recipe_Library.py", "📚", "Recipe Library",
     "Upload recipe PDFs and ask questions about your saved recipes."),
    ("pages/4_AI_Meal_Planner.py", "🥗", "AI Meal Planner",
     "Generate personalized meal plans based on your diet, budget, and goals."),
    ("pages/5_Shopping_List.py", "🛒", "Shopping List",
     "Create a combined shopping list from multiple recipes."),
]


def feature_card(path, icon, title, desc, index):
    try:
        box = st.container(border=True, key=f"fcard_{index}")
    except TypeError:  # older Streamlit without container keys: still works, just unstyled
        box = st.container(border=True)
    with box:
        st.markdown(
            f'<div class="fcard-icon">{icon}</div>'
            f'<div class="fcard-title">{title}</div>'
            f'<div class="fcard-desc">{desc}</div>',
            unsafe_allow_html=True,
        )
        st.page_link(path, label=title)


row1 = st.columns(3)
row2 = st.columns(3)
slots = row1 + row2[:2]

for i, (slot, feature) in enumerate(zip(slots, FEATURES)):
    with slot:
        feature_card(*feature, index=i)