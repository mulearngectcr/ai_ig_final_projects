import os
from dotenv import load_dotenv
from groq import Groq
from backend.app.services.vector_store import search_recipe_text
load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def ask_cooking_assistant(question, history=None):
    pdf_keywords = [
        "uploaded pdf",
        "uploaded document",
        "uploaded recipe",
        "in my pdf",
        "in the document",
        "in the guide",
        "in the cookbook"
    ]

    needs_pdf = any(
        keyword in question.lower()
        for keyword in pdf_keywords
    )

    context = ""
    if needs_pdf:
        try:
            recipe_context = search_recipe_text(question, n_results=2)
            context = "\n\n".join(recipe_context)
        except Exception:
            context = ""
    # Try retrieving information from uploaded PDFs
    if needs_pdf and context:
         source = "Uploaded Recipe Library"
    elif needs_pdf:
        source = "No relevant PDF content found"
    else:
        source = "General AI Knowledge"
    if context:
        system_prompt = f"""
You are RecipePilot, a helpful AI cooking assistant.

UPLOADED RECIPE INFORMATION:
{context}

RULES:

1. For general cooking questions, use your general
   cooking knowledge. Do not require PDF information.

2. If the user explicitly asks about uploaded PDFs,
   answer using only the retrieved PDF information.

3. Never claim a recipe is from an uploaded PDF
   unless it is actually present in the retrieved context.

4. If PDF information is insufficient, clearly say so.

5. Give practical, simple and well-organized answers.

6. If the user asks for multiple recipes, provide
   ingredients and short preparation methods.
"""
    else:
        system_prompt = """
        You are RecipePilot, a helpful AI cooking assistant.

        Answer general cooking questions using your knowledge.
        Give simple and practical cooking advice.
        """

    messages = [
        {
            "role": "system",
            "content": system_prompt
        }
    ]

    # Add previous conversation
    if history:
        messages.extend(history)

    # Add current question
    messages.append({
        "role": "user",
        "content": question
    })

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=messages,
        temperature=0.6,
        reasoning_effort="low",
        max_completion_tokens=2000,
        include_reasoning=False
   )

    return {
    "answer": response.choices[0].message.content,
    "source": source
    }