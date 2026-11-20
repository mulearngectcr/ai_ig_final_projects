import json
import os
from typing import Any, Dict, List, Tuple
import requests

from app import rag


def search_notes(query: str, top_k: int = 4) -> List[Dict[str, Any]]:
    """Search ingested notes for relevant chunks using semantic search."""
    return rag.retrieve(query=query, top_k=top_k)


def list_documents() -> List[str]:
    """List the names of all ingested documents in the knowledge base."""
    return rag.list_documents()


def calculate_score(correct: int, total: int) -> Dict[str, Any]:
    """Calculate percentage score and letter grade from quiz results."""
    if total <= 0:
        return {"correct": correct, "total": total, "percentage": 0.0, "grade": "N/A", "message": "Total must be greater than zero."}
    
    percentage = round((correct / total) * 100.0, 2)
    if percentage >= 90:
        grade = "A (Outstanding)"
    elif percentage >= 80:
        grade = "B (Good)"
    elif percentage >= 70:
        grade = "C (Satisfactory)"
    elif percentage >= 60:
        grade = "D (Pass)"
    else:
        grade = "F (Needs Work)"

    return {
        "correct": correct,
        "total": total,
        "percentage": percentage,
        "grade": grade,
        "summary": f"{correct}/{total} ({percentage}%) - Grade {grade}"
    }


def send_report(summary: str) -> str:
    """Send a study progress report summary to the configured webhook endpoint."""
    webhook_url = os.getenv("WEBHOOK_URL", "").strip()
    if not webhook_url:
        return "webhook not configured"

    try:
        payload = {"content": summary}
        resp = requests.post(webhook_url, json=payload, timeout=10)
        if resp.status_code < 400:
            return f"Report sent successfully (status {resp.status_code})."
        return f"Webhook responded with status {resp.status_code}."
    except Exception as e:
        return f"Webhook delivery encountered an error: {str(e)}"


TOOL_REGISTRY: Dict[str, Dict[str, Any]] = {
    "search_notes": {
        "func": search_notes,
        "description": "Search study notes for concepts, explanations, and placement-prep materials.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query, topic, or question keywords."
                },
                "top_k": {
                    "type": "integer",
                    "description": "Number of chunks to retrieve (default is 4).",
                    "default": 4
                }
            },
            "required": ["query"]
        }
    },
    "list_documents": {
        "func": list_documents,
        "description": "List the filenames of all study materials currently ingested.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    "calculate_score": {
        "func": calculate_score,
        "description": "Compute the percentage score and grade for a student quiz.",
        "parameters": {
            "type": "object",
            "properties": {
                "correct": {
                    "type": "integer",
                    "description": "Number of questions answered correctly."
                },
                "total": {
                    "type": "integer",
                    "description": "Total number of questions in the quiz."
                }
            },
            "required": ["correct", "total"]
        }
    },
    "send_report": {
        "func": send_report,
        "description": "Send a formatted performance or study report via webhook. Call ONLY when student requests a report.",
        "parameters": {
            "type": "object",
            "properties": {
                "summary": {
                    "type": "string",
                    "description": "Detailed text summary of the student's study session, quiz results, or report."
                }
            },
            "required": ["summary"]
        }
    }
}


def get_groq_tools() -> List[Dict[str, Any]]:
    """Build the Groq function calling tools definition array."""
    tools_list = []
    for name, item in TOOL_REGISTRY.items():
        tools_list.append({
            "type": "function",
            "function": {
                "name": name,
                "description": item["description"],
                "parameters": item["parameters"]
            }
        })
    return tools_list


def execute_tool(name: str, arguments: Dict[str, Any]) -> Tuple[Any, str]:
    """
    Execute a registered tool by name with provided arguments.
    Returns (raw_result, preview_string).
    """
    if name not in TOOL_REGISTRY:
        error_msg = f"Unknown tool: {name}"
        return {"error": error_msg}, error_msg

    fn = TOOL_REGISTRY[name]["func"]
    try:
        result = fn(**arguments)
        
        # Build concise preview
        if name == "search_notes":
            chunks = result if isinstance(result, list) else []
            sources = set(c.get("source", "") for c in chunks)
            preview = f"Retrieved {len(chunks)} chunks from: {', '.join(sources) if sources else 'none'}"
        elif name == "list_documents":
            docs = result if isinstance(result, list) else []
            preview = f"Documents ({len(docs)}): {', '.join(docs[:5])}"
        elif name == "calculate_score":
            preview = result.get("summary", json.dumps(result)) if isinstance(result, dict) else str(result)
        elif name == "send_report":
            preview = str(result)
        else:
            preview = str(result)[:100]

        return result, preview
    except Exception as e:
        err = f"Tool execution failed: {str(e)}"
        return {"error": err}, err
