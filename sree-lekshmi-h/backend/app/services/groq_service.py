
import os
import json

from dotenv import load_dotenv
from groq import Groq
from backend.app.agents.meal_planner import create_meal_plan
from backend.app.services.vector_store import search_recipe_text
from backend.app.services.themealdb import search_recipes


# Load environment variables
load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


# Available agent tools
RECIPE_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_recipes",
            "description": "Search TheMealDB for recipes by recipe name.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Recipe name to search for."
                    }
                },
                "required": ["name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_recipe_library",
            "description": "Search uploaded recipe PDFs for ingredients, recipes, and cooking instructions.",
            "parameters": {
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "Question to search in the uploaded recipe library."
                    }
                },
                "required": ["question"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_meal_plan",
            "description": "Create a personalized meal plan based on diet, duration, meals per day, budget, and health goal.",
            "parameters": {
                "type": "object",
                "properties": {
                    "diet": {
                        "type": "string",
                        "description": "Diet preference, such as vegetarian or non-vegetarian."
                    },
                    "days": {
                        "type": "integer",
                        "description": "Number of days."
                    },
                    "meals_per_day": {
                        "type": "integer",
                        "description": "Number of meals per day."
                    },
                    "budget": {
                        "type": "string",
                        "description": "Meal plan budget."
                    },
                    "goal": {
                        "type": "string",
                        "description": "User's meal planning goal."
                    }
                },
                "required": [
                    "diet",
                    "days",
                    "meals_per_day",
                    "budget",
                    "goal"
                ]
            }
        }
    }
]


# Execute the selected tool
def execute_tool(tool_name, arguments):

    print("AGENT TOOL CALLED:", tool_name, arguments)

    if tool_name == "search_recipes":

        recipes = search_recipes(arguments["name"])

        return [
            {
                "id": recipe.get("idMeal"),
                "name": recipe.get("strMeal"),
                "image": recipe.get("strMealThumb")
            }
            for recipe in recipes
        ]

    elif tool_name == "search_recipe_library":

        return search_recipe_text(
            arguments["question"],
            n_results=2
        )
    elif tool_name == "create_meal_plan":

        return create_meal_plan(
            diet=arguments["diet"],
            days=arguments["days"],
            meals_per_day=arguments["meals_per_day"],
            budget=arguments["budget"],
            goal=arguments["goal"]
        )
    return {"error": "Unknown tool"}


# Main AI cooking assistant
def ask_cooking_assistant(question, history=None):

    system_prompt = """
You are RecipePilot, an intelligent AI cooking assistant.

You have access to three tools:

1. search_recipes:
   Search TheMealDB for recipes by name.

2. search_recipe_library:
   Search the user's uploaded recipe PDFs.
3. create_meal_plan:
   Create personalized meal plans using the user's
   diet, number of days, meals per day, budget, and goal.

If the user requests a meal plan, you MUST use
create_meal_plan.

RULES:

1. Decide independently when to use each available tool based on the user's actual request.

2. If the user asks about uploaded PDFs or their contents, you MUST use search_recipe_library.

3. For recipe searches or requests to discover recipes, use search_recipes.

4. When answering questions about uploaded PDFs, use only the retrieved PDF information.

5. Never invent information from uploaded documents.

6. If PDF search returns no relevant information, clearly say that no relevant information was found.

7. For general cooking questions, use your own knowledge.

8. Give practical, clear, and well-organized answers.

9. Do not invent ingredients, quantities, or instructions that are not present in retrieved PDF information.

10. If the user explicitly requests a meal plan, you MUST use create_meal_plan.

11. You are exclusively a cooking and recipe assistant.

12. Answer only questions related to cooking, recipes, ingredients,
    meal planning, nutrition, and food preparation.

13. If a question is unrelated to cooking or food, politely respond:
    "I'm RecipePilot, your AI cooking assistant. I can help with
    recipes, ingredients, cooking techniques, and meal planning.
    Please ask me something related to cooking!"

14. Do not use tools for unrelated questions.

15. UNDERSTAND USER INTENT:
    - Understand what the user actually wants before calling a tool.
    - Do not assume that sharing information means requesting an action.
    - Respond naturally to statements and simple messages.

16. DIETARY PREFERENCES:
    - If the user says "I am vegan", "I am vegetarian",
      or mentions a dietary preference, acknowledge it.
    - Use these preferences when answering relevant future
      questions in the current conversation.
    - Do not automatically generate a meal plan.
    - Do not assume dietary preferences unless the user mentions them.

17. MEAL PLANNER:
    - Call create_meal_plan ONLY when the user explicitly
      requests a meal plan.
    - Do not call it just because the user mentions a diet,
      budget, health goal, or food preference.
    - Never invent budget, duration, meals per day, or health goals.
    - If required details are missing, ask the user for them
      before generating the meal plan.

18. CONVERSATION CONTEXT:
    - Use previous messages to understand follow-up questions.
    - Remember preferences mentioned earlier in the current conversation.
    - Do not claim the user has shared information that they have not provided.

19. RECIPE SEARCH:
    - Do not search recipes for every general cooking question.
    - Use your own knowledge for general cooking advice.
    - Use search_recipes when the user wants to discover recipes.

20. RESPONSE QUALITY:
    - Answer the user's actual question directly.
    - Do not perform additional tasks that the user did not request.
    - Ask a follow-up question when essential information is missing.
    - Keep answers relevant, helpful, and easy to understand.
21. RECIPE SUGGESTIONS AND FALLBACK:
    - When the user asks for a recipe based on a flavour,
      cuisine, ingredient, or dietary preference, understand
      the request and suggest a suitable recipe.
    - Do not require an exact recipe name to suggest a recipe.
    - Use search_recipes when searching TheMealDB is useful.
    - If the recipe search returns no results, do not stop
      or simply tell the user that no recipes were found.
    - Instead, generate a suitable recipe using your own
      cooking knowledge.
    - Always respect dietary preferences mentioned earlier
      in the conversation.
    - Never suggest meat, fish, eggs, or dairy to a user
      who has stated they are vegan.
"""

    source = "General AI Knowledge"

    messages = [
        {
            "role": "system",
            "content": system_prompt
        }
    ]

    if history:
        messages.extend(history)

    messages.append({
        "role": "user",
        "content": question
    })

    # Agent tool-calling loop
    for _ in range(5):

        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=messages,
            tools=RECIPE_TOOLS,
            tool_choice="auto",
            temperature=0.6,
            reasoning_effort="low",
            max_completion_tokens=2000,
            include_reasoning=False
        )

        assistant_message = response.choices[0].message

        # Return final answer
        if not assistant_message.tool_calls:

            return {
                "answer": assistant_message.content or "",
                "source": source
            }

        # Add assistant tool request
        messages.append(
            assistant_message.model_dump(exclude_none=True)
        )

        # Execute requested tools
        for tool_call in assistant_message.tool_calls:

            tool_name = tool_call.function.name

            arguments = json.loads(
                tool_call.function.arguments
            )

            result = execute_tool(
                tool_name,
                arguments
            )

            # Track answer source
            if tool_name == "search_recipe_library":

                if result:
                    source = "Uploaded Recipe Library"
                else:
                    source = "No relevant PDF content found"

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(result)
            })

    return {
        "answer": "I couldn't complete the request. Please try again.",
        "source": source
    }
