from datetime import datetime, timezone
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional
from dotenv import find_dotenv, load_dotenv
from groq import Groq

from app.schemas import ChatTurn
from app.tools import execute_tool, get_groq_tools

load_dotenv(find_dotenv())

BASE_DIR = Path(__file__).resolve().parent.parent
LOG_FILE = BASE_DIR / "agent_log.jsonl"
DEFAULT_MODEL = "llama-3.3-70b-versatile"

SYSTEM_PROMPT = """You are CampusPrep AI, a knowledgeable, concise study and placement-prep assistant.
Guidelines:
1. Always call the search_notes tool before answering subject questions or technical topics, and explicitly cite the document sources in your answer.
2. For quizzes: search the notes for relevant subject content, then generate 3 clear, testing questions directly from the retrieved notes.
3. When the student answers quiz questions: grade their answers against the retrieved notes, calculate how many are correct out of the total, and call the calculate_score tool to determine their percentage and letter grade.
4. Call send_report ONLY when the student explicitly requests a performance or study session report.
5. Keep explanations direct, professional, and well-structured.
"""

_active_model: Optional[str] = None


def get_groq_client() -> Groq:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY is not set in the environment or .env file.")
    return Groq(api_key=api_key)


def get_model_name(client: Groq) -> str:
    global _active_model
    if _active_model:
        return _active_model

    configured_model = os.getenv("GROQ_MODEL", DEFAULT_MODEL).strip()
    try:
        available_models = [m.id for m in client.models.list().data]
        if configured_model in available_models:
            _active_model = configured_model
            return _active_model

        # Fallback to supported chat/tool models if configured model is not permitted on this API key
        for candidate in ["llama-3.3-70b-versatile", "openai/gpt-oss-120b", "qwen/qwen3.8-27b", "openai/gpt-oss-20b"]:
            if candidate in available_models:
                _active_model = candidate
                return _active_model
    except Exception:
        pass

    _active_model = configured_model
    return _active_model


def append_to_agent_log(message: str, tool_trace: List[Dict[str, Any]], answer: str) -> None:
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "message": message,
        "tool_trace": tool_trace,
        "answer": answer
    }
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception as e:
        print(f"Warning: Failed to append to agent log: {e}")


def get_recent_logs(limit: int = 20) -> List[Dict[str, Any]]:
    if not LOG_FILE.exists():
        return []
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]
        recent = lines[-limit:]
        logs = []
        for line in recent:
            try:
                logs.append(json.loads(line))
            except Exception:
                pass
        return logs
    except Exception:
        return []


def run_agent(message: str, history: Optional[List[ChatTurn]] = None) -> Dict[str, Any]:
    client = get_groq_client()
    model = get_model_name(client)
    tools = get_groq_tools()

    messages: List[Dict[str, Any]] = [{"role": "system", "content": SYSTEM_PROMPT}]

    if history:
        for turn in history[-10:]:
            messages.append({"role": turn.role, "content": turn.content})

    messages.append({"role": "user", "content": message})

    tool_trace: List[Dict[str, Any]] = []
    collected_sources: Dict[str, Dict[str, Any]] = {}
    final_answer = ""
    max_rounds = 5

    for _ in range(max_rounds):
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            tools=tools,
            tool_choice="auto",
            temperature=0.2
        )

        choice = response.choices[0]
        assistant_msg = choice.message

        if assistant_msg.tool_calls:
            messages.append(assistant_msg)

            for tool_call in assistant_msg.tool_calls:
                func_name = tool_call.function.name
                try:
                    args = json.loads(tool_call.function.arguments or "{}")
                except Exception:
                    args = {}

                result_data, result_preview = execute_tool(func_name, args)

                tool_trace.append({
                    "tool": func_name,
                    "arguments": args,
                    "result_preview": result_preview
                })

                if func_name == "search_notes" and isinstance(result_data, list):
                    for item in result_data:
                        src = item.get("source", "unknown")
                        pg = item.get("page", 1)
                        key = f"{src}#p{pg}"
                        if key not in collected_sources:
                            collected_sources[key] = {
                                "source": src,
                                "page": pg,
                                "score": item.get("score"),
                                "text": item.get("text")
                            }

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": func_name,
                    "content": json.dumps(result_data, ensure_ascii=False)
                })
        else:
            final_answer = assistant_msg.content or ""
            break

    if not final_answer:
        final_call = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.2
        )
        final_answer = final_call.choices[0].message.content or ""

    append_to_agent_log(message, tool_trace, final_answer)

    return {
        "answer": final_answer,
        "sources": list(collected_sources.values()),
        "tool_trace": tool_trace
    }
