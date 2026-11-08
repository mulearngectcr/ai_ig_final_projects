import httpx

BASE_URL="https://www.themealdb.com/api/json/v1/1"\


def search_recipes(name):
    url = f"{BASE_URL}/search.php"

    params = {
        "s": name
    }

    response = httpx.get(url, params=params, timeout=15)
    response.raise_for_status()

    data = response.json()

    return data.get("meals") or []

def get_recipe_details(recipe_id):
    url = f"{BASE_URL}/lookup.php"

    params = {
        "i": recipe_id
    }

    response = httpx.get(url, params=params, timeout=15)
    response.raise_for_status()

    data = response.json()

    meals = data.get("meals")

    if not meals:
        return None

    return meals[0]


def format_recipe_details(recipe):
    ingredients = []

    for i in range(1, 21):
        ingredient = recipe.get(f"strIngredient{i}")
        measure = recipe.get(f"strMeasure{i}")

        if ingredient and ingredient.strip():
            ingredients.append({
                "ingredient": ingredient.strip(),
                "measure": measure.strip() if measure else ""
            })

    return {
        "id": recipe.get("idMeal"),
        "name": recipe.get("strMeal"),
        "image": recipe.get("strMealThumb"),
        "category": recipe.get("strCategory"),
        "area": recipe.get("strArea"),
        "instructions": recipe.get("strInstructions"),
        "ingredients": ingredients
    }