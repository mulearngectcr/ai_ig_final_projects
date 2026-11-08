import streamlit as st
from api_client import ask_assistant

st.set_page_config(
    page_title="Shopping List",
    page_icon="🛒",
    layout="wide"
)

st.title("🛒 Shopping List")
st.write("Generate a combined shopping list from your recipes.")

st.info(
    "💡 You can ask for ingredients from recipes in your uploaded PDFs "
    "or enter dish names to generate a combined shopping list."
)

st.page_link(
    "pages/3_Recipe_Library.py",
    label=" Go to Recipe Library to Upload PDFs",
    icon="📚"
)
st.divider()

# ---------------------------------
# ENTER RECIPES
# ---------------------------------

st.subheader("Enter Dish Names or Ask About Your Uploaded Recipes")

recipes = st.text_area(
    "Recipe names",
    placeholder="Example:\nChicken biryani\nPaneer butter masala\nOr ask about your uploaded recipes, e.g., 'What ingredients are needed for my uploaded lasagna recipe?'",
    height=200
)

# ---------------------------------
# GENERATE SHOPPING LIST
# ---------------------------------

if st.button("Generate Shopping List"):

    if not recipes.strip():
        st.warning("Please enter at least one recipe.")

    else:

        prompt = f"""
You are a helpful cooking assistant.

Create a combined shopping list for these recipes:

{recipes}

Requirements:
1. List all required ingredients.
2. Combine duplicate ingredients.
3. Mention approximate quantities.
4. Group ingredients into these categories:
   - Vegetables
   - Fruits
   - Meat and Dairy
   - Spices
   - Grains
   - Other Ingredients

5. Use clear headings and bullet points.
6. Do not include cooking instructions.
7. If exact quantities are unavailable, provide reasonable estimates.

Generate only the shopping list.
"""

        with st.spinner("Generating your shopping list..."):

            try:
                result = ask_assistant(prompt)

                if isinstance(result, dict) and result.get("answer"):

                    st.session_state["shopping_list"] = result["answer"]

                else:
                    st.error("The AI returned an empty or unexpected response.")

            except Exception as e:
                st.error(f"Could not generate shopping list: {e}")


# ---------------------------------
# DISPLAY SHOPPING LIST
# ---------------------------------

if st.session_state.get("shopping_list"):

    st.divider()

    st.subheader("🛒 Your Shopping List")

    st.markdown(st.session_state["shopping_list"])

    if st.button("Clear Shopping List"):
        st.session_state.pop("shopping_list", None)
        st.rerun()