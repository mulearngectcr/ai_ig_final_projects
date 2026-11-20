import os
from typing import Any, Dict, List
import requests
import streamlit as st

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000").rstrip("/")

st.set_page_config(page_title="CampusPrep AI", page_icon="🎓", layout="wide")


def fetch_documents() -> List[str]:
    try:
        resp = requests.get(f"{BACKEND_URL}/documents", timeout=10)
        if resp.status_code == 200:
            return resp.json().get("documents", [])
    except Exception:
        pass
    return []


# Sidebar for Document Management
with st.sidebar:
    st.title("📚 Knowledge Base")
    st.caption("Upload placement preparation notes and subject materials.")

    uploaded_files = st.file_uploader(
        "Upload files (.txt, .md, .pdf)",
        type=["txt", "md", "pdf"],
        accept_multiple_files=True,
    )

    if st.button("Ingest Notes", use_container_width=True):
        if not uploaded_files:
            st.warning("Please select at least one file to upload.")
        else:
            with st.spinner("Ingesting documents into knowledge base..."):
                try:
                    files_payload = [
                        ("files", (f.name, f.getvalue(), f.type or "application/octet-stream"))
                        for f in uploaded_files
                    ]
                    resp = requests.post(f"{BACKEND_URL}/upload", files=files_payload, timeout=120)
                    if resp.status_code == 200:
                        data = resp.json()
                        st.success(data.get("message", "Files uploaded successfully!"))
                    elif resp.status_code == 429:
                        st.warning("Rate limit exceeded for uploads (5/minute). Please wait a minute.")
                    elif resp.status_code == 413:
                        st.error("File exceeds maximum allowed size (5 MB).")
                    elif resp.status_code == 400:
                        st.error(resp.json().get("detail", "Invalid file upload request."))
                    else:
                        st.error(f"Upload failed: {resp.status_code} - {resp.text}")
                except requests.exceptions.Timeout:
                    st.error("Upload request timed out (120s limit).")
                except requests.exceptions.ConnectionError:
                    st.error("Could not reach backend. Verify BACKEND_URL is running.")
                except Exception as e:
                    st.error(f"Upload error: {str(e)}")

    st.divider()
    st.subheader("Ingested Documents")
    docs = fetch_documents()
    if docs:
        for d in docs:
            st.markdown(f"- 📄 `{d}`")
    else:
        st.info("No documents found or backend offline.")


# Main Chat Interface
st.title("🎓 CampusPrep AI")
st.caption("Your intelligent study and placement-prep assistant with RAG & tool-calling agent.")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("sources"):
            st.markdown("**Sources referenced:**")
            for s in msg["sources"]:
                score_str = f" (relevance: {s['score']})" if s.get("score") is not None else ""
                pg_str = f", page {s['page']}" if s.get("page") and s["page"] > 1 else ""
                st.markdown(f"- `{s.get('source')}`{pg_str}{score_str}")
        if msg.get("tool_trace"):
            with st.expander("Agent execution trace"):
                for idx, t in enumerate(msg["tool_trace"], start=1):
                    st.markdown(f"**Step {idx} - `{t.get('tool')}`**")
                    if t.get("arguments"):
                        st.json(t["arguments"])
                    st.caption(f"Result preview: {t.get('result_preview')}")


# Chat Input
user_query = st.chat_input("Ask a subject question, say 'quiz me on <topic>', or ask for a study report...")

if user_query:
    # Render user query immediately
    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.markdown(user_query)

    # Prepare conversation history for the backend
    history_turns = []
    for m in st.session_state.messages[:-1]:
        history_turns.append({"role": m["role"], "content": m["content"]})

    payload = {
        "message": user_query,
        "history": history_turns[-10:]
    }

    with st.chat_message("assistant"):
        with st.spinner("CampusPrep AI is thinking (note: free backend may take up to 2 mins to wake up)..."):
            try:
                response = requests.post(f"{BACKEND_URL}/agent", json=payload, timeout=120)
                if response.status_code == 200:
                    res_data = response.json()
                    answer_text = res_data.get("answer", "")
                    sources = res_data.get("sources", [])
                    tool_trace = res_data.get("tool_trace", [])

                    st.markdown(answer_text)

                    if sources:
                        st.markdown("**Sources referenced:**")
                        for s in sources:
                            score_str = f" (relevance: {s['score']})" if s.get("score") is not None else ""
                            pg_str = f", page {s['page']}" if s.get("page") and s["page"] > 1 else ""
                            st.markdown(f"- `{s.get('source')}`{pg_str}{score_str}")

                    if tool_trace:
                        with st.expander("Agent execution trace"):
                            for idx, t in enumerate(tool_trace, start=1):
                                st.markdown(f"**Step {idx} - `{t.get('tool')}`**")
                                if t.get("arguments"):
                                    st.json(t["arguments"])
                                st.caption(f"Result preview: {t.get('result_preview')}")

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer_text,
                        "sources": sources,
                        "tool_trace": tool_trace
                    })

                elif response.status_code == 429:
                    err_msg = "⚠️ Rate limit reached (10 requests per minute). Please wait a moment before sending another prompt."
                    st.warning(err_msg)
                    st.session_state.messages.append({"role": "assistant", "content": err_msg})
                else:
                    try:
                        err_detail = response.json().get("detail", response.text)
                    except Exception:
                        err_detail = response.text
                    err_msg = f"Backend error ({response.status_code}): {err_detail}"
                    st.error(err_msg)
                    st.session_state.messages.append({"role": "assistant", "content": err_msg})

            except requests.exceptions.Timeout:
                err_msg = "⏳ Request timed out after 120 seconds. The free backend may be cold-starting; please retry in a moment."
                st.error(err_msg)
                st.session_state.messages.append({"role": "assistant", "content": err_msg})
            except requests.exceptions.ConnectionError:
                err_msg = "🔌 Failed to connect to backend server. Please verify BACKEND_URL and ensure FastAPI is running."
                st.error(err_msg)
                st.session_state.messages.append({"role": "assistant", "content": err_msg})
            except Exception as ex:
                err_msg = f"Unexpected error: {str(ex)}"
                st.error(err_msg)
                st.session_state.messages.append({"role": "assistant", "content": err_msg})
