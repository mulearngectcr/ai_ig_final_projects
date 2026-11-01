
import streamlit as st
from api_client import search_recipes, get_recipe_details

st.set_page_config(
    page_title="RecipePilot",
    page_icon="🍳",
    layout="wide"
)

st.title("🍳 RecipePilot")
st.subheader("Discover recipes and make cooking easier!")

st.divider()

st.header("🔍 Find Recipes")

name = st.text_input(
    "Enter a recipe name",
    placeholder="e.g. Chicken"
)

if "recipes" not in st.session_state:
    st.session_state["recipes"] = []

if "selected_recipe_id" not in st.session_state:
    st.session_state["selected_recipe_id"] = None

if "selected_recipe" not in st.session_state:
    st.session_state["selected_recipe"] = None


# Search recipes
if st.button("Search Recipes"):
    if name.strip():
        try:
            result = search_recipes(name)

            st.session_state["recipes"] = result["recipes"]
            st.session_state["selected_recipe_id"] = None
            st.session_state["selected_recipe"] = None

            if not result["recipes"]:
                st.warning("No recipes found. Try another name.")

        except Exception as e:
            st.error(f"Unable to connect to backend: {e}")


# Display recipes
recipes = st.session_state["recipes"]

if recipes:
    st.subheader("Search Results")

    for recipe in recipes:

        with st.container():
            col1, col2 = st.columns([1, 3])

            with col1:
                st.image(recipe["strMealThumb"], width=150)

            with col2:
                st.write(f"**{recipe['strMeal']}**")

                if st.button(
                    "View Recipe",
                    key=recipe["idMeal"]
                ):
                    try:
                        details = get_recipe_details(recipe["idMeal"])

                        st.session_state["selected_recipe"] = details
                        st.session_state["selected_recipe_id"] = recipe["idMeal"]

                    except Exception as e:
                        st.error(f"Error loading recipe: {e}")

            # Expand recipe directly below its search result
            if st.session_state["selected_recipe_id"] == recipe["idMeal"]:

                details = st.session_state["selected_recipe"]

                with st.expander(
                    "🍽️ Recipe Details",
                    expanded=True
                ):
                    st.image(details["image"], width=300)

                    st.subheader("Ingredients")

                    for item in details["ingredients"]:
                        st.write(
                            f"- {item['measure']} {item['ingredient']}"
                        )

                    st.subheader("Instructions")
                    st.write(details["instructions"])

            st.divider()
