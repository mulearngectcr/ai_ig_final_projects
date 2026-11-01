from fastapi import FastAPI
from backend.app.api.routes import recipes
from backend.app.api.routes import assistant,library
app = FastAPI(title="RecipePilot API")

app.include_router(
    recipes.router,
    prefix="/api/recipes",
    tags=["Recipes"]
)

app.include_router(
    library.router,
    prefix="/api/library",
    tags=["Recipe Library"]
)


@app.get("/health")
def health():
    return {"status": "RecipePilot is running"}


app.include_router(
    assistant.router,
    prefix="/api/assistant",
    tags=["AI Assistant"]
)