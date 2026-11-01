from pydantic import BaseModel
from typing import List


class Recipe(BaseModel):
    idMeal: str
    strMeal: str
    strMealThumb: str


class RecipeSearchResponse(BaseModel):
    search: str
    total: int
    recipes: List[Recipe]