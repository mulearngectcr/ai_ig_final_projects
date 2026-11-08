from fastapi import APIRouter, HTTPException
from backend.app.services.themealdb import search_recipes
from backend.app.services.themealdb import (
    search_recipes,
    get_recipe_details,
    format_recipe_details
)
from backend.app.schemas.recipe import RecipeSearchResponse
router = APIRouter()


@router.get("/search", response_model=RecipeSearchResponse)
def get_recipes(name: str):
    if not name.strip():
        raise HTTPException(status_code=400, detail="Recipe name is required")

    try:
        recipes = search_recipes(name)

        return {
            "search": name,
            "total": len(recipes),
            "recipes": recipes
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{recipe_id}")
def recipe_details(recipe_id: str):
    try:
        recipe = get_recipe_details(recipe_id)

        if not recipe:
            raise HTTPException(
                status_code=404,
                detail="Recipe not found"
            )

        return format_recipe_details(recipe)

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))