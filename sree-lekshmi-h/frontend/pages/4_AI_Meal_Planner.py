import streamlit as st
from api_client import ask_assistant

st.set_page_config(
    page_title="AI Meal Planner",
    page_icon="🍽️",
    layout="wide"
)

st.title("🍽️ AI Meal Planner")
st.write("Generate personalized meal plans using AI.")

st.divider()

# User preferences
st.subheader("Your Preferences")

col1, col2 = st.columns(2)

with col1:
    diet = st.selectbox(
        "Diet preference",
        ["No preference", "Vegetarian", "Vegan", "Non-Vegetarian"]
    )

    meals = st.selectbox(
        "Meals per day",
        [2, 3, 4, 5]
    )

with col2:
    days = st.selectbox(
        "Plan duration",
        [1, 3, 5, 7]
    )

    budget = st.selectbox(
        "Budget",
        ["Low", "Medium", "High"]
    )

goal = st.selectbox(
    "Your goal",
    ["Balanced diet", "Weight management", "High protein", "Healthy eating"]
)

if st.button("Generate Meal Plan"):

    prompt = f"""
    Create a {days}-day meal plan.

    Diet preference: {diet}
    Meals per day: {meals}
    Budget: {budget}
    Goal: {goal}

    For each day, provide:
    - Breakfast
    - Lunch
    - Dinner (and snacks if appropriate)
    - Short descriptions of the meals.

    Keep the plan practical and affordable.
    """

    with st.spinner("Creating your meal plan..."):
        try:
            result = ask_assistant(prompt)
            st.subheader("Your Meal Plan")
            st.markdown(result["answer"])

        except Exception as e:
            st.error(f"Could not generate meal plan: {e}")