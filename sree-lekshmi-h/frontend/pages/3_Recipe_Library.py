import streamlit as st
import requests
from urllib.parse import quote
from api_client import BASE_URL

st.set_page_config(
    page_title="Recipe Library",
    page_icon="📚",
    layout="wide"
)

st.title("📚 Recipe Library")
st.write(
    "Upload your recipe PDF cookbooks and build your personal recipe knowledge base."
)

st.divider()

# ---------------------------------------
# UPLOAD RECIPE PDF
# ---------------------------------------

st.subheader("Upload Recipe PDF")

uploaded_file = st.file_uploader(
    "Choose a recipe PDF",
    type=["pdf"]
)

if uploaded_file is not None:

    st.write(f"Selected file: **{uploaded_file.name}**")

    if st.button("Upload and Process PDF"):

        with st.spinner("Extracting text and storing recipes..."):

            try:
                files = {
                    "file": (
                        uploaded_file.name,
                        uploaded_file.getvalue(),
                        "application/pdf"
                    )
                }

                response = requests.post(
                    f"{BASE_URL}/api/library/upload",
                    files=files,
                    timeout=120
                )

                response.raise_for_status()

                result = response.json()

                st.success(result["message"])

                st.write("**Filename:**", result["filename"])
                st.write("**Chunks stored:**", result["chunks_stored"])

                with st.expander("View extracted text"):
                    st.text(result["text"])

            except requests.exceptions.RequestException as e:
                st.error(f"Upload failed: {e}")


st.divider()

# ---------------------------------------
# DISPLAY UPLOADED COOKBOOKS
# ---------------------------------------

st.subheader("📚 Uploaded Cookbooks")

try:
    response = requests.get(
        f"{BASE_URL}/api/library/files",
        timeout=15
    )

    response.raise_for_status()

    result = response.json()

    if result["files"]:

        st.write(f"Total cookbooks: {result['total']}")

        for filename in result["files"]:

            col1, col2 = st.columns([4, 1])

            with col1:
                st.write(f"📄 {filename}")

            with col2:

                if st.button("Delete", key=f"delete_{filename}"):

                    try:
                        delete_response = requests.delete(
                            f"{BASE_URL}/api/library/files/{quote(filename, safe='')}",
                            timeout=15
                        )

                        delete_response.raise_for_status()

                        st.success(
                            f"{filename} deleted successfully!"
                        )

                        st.rerun()

                    except requests.exceptions.RequestException as e:
                        st.error(f"Delete failed: {e}")

    else:
        st.info("No cookbooks uploaded yet.")

except requests.exceptions.RequestException as e:
    st.error(f"Could not load uploaded PDFs: {e}")

if result["files"]:
    st.success("Your recipe PDF library is ready!")

    st.info(
        "🤖 Your recipes have been added to the library. "
        "You can now ask questions about their contents in the Recipe Assistant."
    )

    st.page_link(
        "pages/2_Recipe_Assistant.py",
        label="🤖 Ask Questions in Recipe Assistant",
        icon="🤖"
    )
st.divider()

# ---------------------------------------
# HOW IT WORKS
# ---------------------------------------

st.subheader("How it works")

st.write("""
1. Upload a text-based recipe PDF.
2. RecipePilot extracts its text.
3. The extracted text is split into chunks.
4. ChromaDB stores the chunks as embeddings.
5. Ask questions about your uploaded recipes in the AI Recipe Assistant.
""")