
import streamlit as st
from api_client import ask_assistant

st.set_page_config(
    page_title="Recipe Assistant",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 AI Cooking Assistant")
st.write("Ask anything about cooking, ingredients and recipes.")

st.divider()

# Initialize conversation history
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

for chat in st.session_state["chat_history"]:
    with st.chat_message(chat["role"]):
        st.write(chat["content"])

question = st.chat_input("Ask your cooking question...")

if question:
    history = st.session_state["chat_history"][-6:]

    with st.chat_message("user"):
        st.write(question)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                result = ask_assistant(question, history)
                answer = result["answer"]
                source = result["source"]
                st.write(answer)
                st.caption(f"Source: {source}")

                st.session_state["chat_history"].append(
                    {"role": "user", "content": question}
                )
                st.session_state["chat_history"].append(
                    {"role": "assistant", "content": answer}
                )

            except Exception as e:
                st.error(f"Unable to get response: {e}")

# Clear conversation
if st.button("Clear Chat"):
    st.session_state["chat_history"] = []
    st.rerun()
