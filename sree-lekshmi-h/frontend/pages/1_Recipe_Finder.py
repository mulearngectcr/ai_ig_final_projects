import re

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

if "recipes" not in st.session_state:
    st.session_state["recipes"] = []

if "selected_recipe_id" not in st.session_state:
    st.session_state["selected_recipe_id"] = None

if "selected_recipe" not in st.session_state:
    st.session_state["selected_recipe"] = None


# ---- NEW: auto-search when arriving from the Home slideshow ----------------
# Home links here with ?meal_id=<id>&meal=<name>. Runs once per arrival: fills
# the search box, runs the same search as the button, and opens that dish.
# (Must run BEFORE the text box is drawn so the name can be put in it.)
def _search_queries(meal_name):
    """Names to try, best first. Dish names with characters like & or '
    (e.g. "Prawn & noodle salad with crispy shallots") can fail as a search,
    so also try the part before the special character and the first word."""
    queries = [meal_name]
    before_symbol = re.split(r"[^A-Za-z0-9 ]", meal_name)[0].strip()
    first_word = (re.findall(r"[A-Za-z0-9]+", meal_name) or [""])[0]
    for q in (before_symbol, first_word):
        if q and q not in queries:
            queries.append(q)
    return queries


home_meal = st.query_params.get("meal")
home_meal_id = st.query_params.get("meal_id")
home_notice = None

if home_meal:
    arrival = f"{home_meal_id}|{home_meal}"
    if st.session_state.get("home_arrival") != arrival:
        st.session_state["home_arrival"] = arrival
        st.session_state["recipe_name"] = home_meal   # shows the name in the box

        exact = None      # (results, dish) where the dish id matches the slide
        fallback = None   # (results, first result) if no id match anywhere
        last_error = None

        for query in _search_queries(home_meal):
            try:
                found = search_recipes(query)["recipes"] or []
            except Exception as e:
                last_error = e
                continue
            if not found:
                continue
            dish = next(
                (r for r in found if str(r["idMeal"]) == str(home_meal_id)),
                None,
            )
            if dish:
                exact = (found, dish)
                break
            if fallback is None:
                fallback = (found, found[0])

        chosen = exact or fallback
        st.session_state["selected_recipe_id"] = None
        st.session_state["selected_recipe"] = None

        if chosen:
            found, dish = chosen
            st.session_state["recipes"] = found
            try:
                st.session_state["selected_recipe"] = get_recipe_details(dish["idMeal"])
                st.session_state["selected_recipe_id"] = dish["idMeal"]
            except Exception as e:
                home_notice = ("error", f"Error loading recipe: {e}")
        else:
            st.session_state["recipes"] = []
            if last_error:
                home_notice = ("error", f"Unable to connect to backend: {last_error}")
            else:
                home_notice = ("warning", "No recipes found. Try another name.")
# ---- END NEW ----------------------------------------------------------------


name = st.text_input(
    "Enter a recipe name",
    placeholder="e.g. Chicken",
    key="recipe_name"
)

if home_notice:
    getattr(st, home_notice[0])(home_notice[1])


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