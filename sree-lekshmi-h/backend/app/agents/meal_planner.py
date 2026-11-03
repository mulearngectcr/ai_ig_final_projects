def create_meal_plan(diet, days, meals_per_day, budget, goal):

    prompt = f"""
    Create a practical meal plan with the following requirements:

    Diet preference: {diet}
    Number of days: {days}
    Meals per day: {meals_per_day}
    Budget: {budget}
    Health goal: {goal}

    For each day:
    1. List each meal.
    2. Include the main ingredients.
    3. Give a short description.
    4. Keep the plan within the budget as far as possible.

    Present the result in a clear day-wise format.
    """

    from backend.app.services.groq_service import client

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {
                "role": "system",
                "content": "You are an expert meal planning assistant."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.6,
        reasoning_effort="low",
        max_completion_tokens=2000,
        include_reasoning=False
    )

    return response.choices[0].message.content or ""