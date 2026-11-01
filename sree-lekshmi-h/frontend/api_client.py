import requests

BASE_URL = "http://127.0.0.1:8000"


def search_recipes(name):
    response = requests.get(
        f"{BASE_URL}/api/recipes/search",
        params={"name": name}
    )

    response.raise_for_status()
    return response.json()


def get_recipe_details(recipe_id):
    response = requests.get(
        f"{BASE_URL}/api/recipes/{recipe_id}"
    )

    response.raise_for_status()
    return response.json()


def ask_assistant(question, history=None):
    response = requests.post(
        f"{BASE_URL}/api/assistant/ask",
        json={
            "question": question,
            "history": history or []
        },
        timeout=90
    )
    response.raise_for_status()
    return response.json()